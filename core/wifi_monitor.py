"""
Monitor de conexión WiFi profesional.
Recopila SSID, señal (dBm), calidad link, bitrate, ruido, tráfico RX/TX Mbps.
Thread daemon cada 5s, históricos, cambio interfaz en caliente, persistencia.
Fallback ip/iwconfig/ifconfig.
"""
import re
import subprocess
import threading
from collections import deque
from typing import Optional
from config.settings import HISTORY
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

_POLL_INTERVAL = 5    # segundos
_IFACE_DEFAULT = "wlan0"

# Umbrales de señal (dBm)
WIFI_SIGNAL_GOOD = -60
WIFI_SIGNAL_WARN = -75


def _run(cmd: list) -> str:
    """
    Ejecuta comando shell y retorna stdout limpio o vacío en fallo.

    Timeout 5s. Log warning en exceptions.
    """
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        logger.warning("[WiFiMonitor] Error ejecutando %s: %s", cmd, e)
        return ""


def _parse_iwconfig(raw: str) -> dict:
    """
    Parsea salida `iwconfig <iface>` → métricas WiFi.

    Returns:
        dict: {"ssid": str, "signal_dbm": int|None, "link_quality": int|None, 
               "link_quality_max": int|None, "bitrate": str, "noise_dbm": int|None}
    """
    data = {
        "ssid":              "",
        "signal_dbm":        None,
        "link_quality":      None,
        "link_quality_max":  None,
        "bitrate":           "",
        "noise_dbm":         None,
    }

    m = re.search(r'ESSID:"([^"]*)"', raw)
    if m:
        data["ssid"] = m.group(1)

    m = re.search(r'Link Quality=(\d+)/(\d+)', raw)
    if m:
        data["link_quality"]     = int(m.group(1))
        data["link_quality_max"] = int(m.group(2))

    m = re.search(r'Signal level=(-?\d+)', raw)
    if m:
        data["signal_dbm"] = int(m.group(1))

    m = re.search(r'Noise level=(-?\d+)', raw)
    if m:
        data["noise_dbm"] = int(m.group(1))

    m = re.search(r'Bit Rate=([^\s]+\s+[^\s]+)', raw)
    if m:
        data["bitrate"] = m.group(1)

    return data


def _parse_iw_link(raw: str) -> dict:
    """
    Parsea salida `iw dev <iface> link` como fallback.

    Returns:
        dict: {"ssid": str, "signal_dbm": int|None, "bitrate": str}
    """
    data = {"ssid": "", "signal_dbm": None, "bitrate": ""}

    m = re.search(r'SSID:\s*(.+)', raw)
    if m:
        data["ssid"] = m.group(1).strip()

    m = re.search(r'signal:\s*(-?\d+)', raw)
    if m:
        data["signal_dbm"] = int(m.group(1))

    m = re.search(r'tx bitrate:\s*([^\n]+)', raw)
    if m:
        data["bitrate"] = m.group(1).strip()

    return data


class WiFiMonitor:
    """
    Monitor completo de WiFi con históricos, tráfico realtime, cambio interfaz dinámica.

    Thread-safe, persistencia interfaz, umbrales dBm, métricas iwconfig/iw fallback.
    """

    def __init__(self, interface: Optional[str] = None):
        """
        Inicializa monitor.

        Args:
            interface (str, optional): wlan0/wlan1. Prioridad: arg → settings → wlan0.
        """
        # Prioridad: argumento explícito → local_settings → constante por defecto
        self._iface    = interface or self._load_saved_interface() or _IFACE_DEFAULT
        self._running  = False
        self._stop_evt = threading.Event()
        self._lock     = threading.Lock()
        self._thread   = None

        # Estado actual
        self._info: dict = {
            "ssid":              "",
            "signal_dbm":        None,
            "link_quality":      None,
            "link_quality_max":  None,
            "bitrate":           "",
            "noise_dbm":         None,
            "connected":         False,
        }

        # Tráfico
        self._prev_rx: Optional[int] = None
        self._prev_tx: Optional[int] = None
        self._rx_mbps: float = 0.0
        self._tx_mbps: float = 0.0

        # Históricos
        self._signal_hist = deque(maxlen=HISTORY)
        self._rx_hist     = deque(maxlen=HISTORY)
        self._tx_hist     = deque(maxlen=HISTORY)

        self._last_update: str = ""

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self):
        """
        Inicia thread daemon de polling cada 5s.

        Idempotente, log interfaz.
        """
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="WiFiMonitor"
        )
        self._thread.start()
        logger.info("[WiFiMonitor] Servicio iniciado — interfaz: %s", self._iface)

    def stop(self):
        """
        Detiene servicio.

        Join 6s, resetea estado. Log.
        """
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=6)
        with self._lock:
            self._info = {}
        logger.info("[WiFiMonitor] Servicio detenido")

    def is_running(self) -> bool:
        """
        Estado running.

        Returns:
            bool
        """
        return self._running

    def get_signal_history(self) -> list:
        """
        Histórico señal dBm (últimos HISTORY puntos).

        Returns:
            list[int]
        """
        with self._lock:
            return list(self._signal_hist)

    # ── Cambio de interfaz en caliente ────────────────────────────────────────

    def set_interface(self, iface: str) -> None:
        """
        Cambia interfaz en runtime.

        Resetea históricos/tráfico. Persiste. Próximo poll usa nueva iface.
        """
        with self._lock:
            self._iface    = iface
            self._prev_rx  = None
            self._prev_tx  = None
            self._rx_mbps  = 0.0
            self._tx_mbps  = 0.0
            self._signal_hist.clear()
            self._rx_hist.clear()
            self._tx_hist.clear()
            self._info = {
                "ssid":             "",
                "signal_dbm":       None,
                "link_quality":     None,
                "link_quality_max": None,
                "bitrate":          "",
                "noise_dbm":        None,
                "connected":        False,
            }
            self._last_update = ""

        self._persist_interface(iface)
        logger.info("[WiFiMonitor] Interfaz cambiada a: %s", iface)

    # ── Interfaces disponibles ────────────────────────────────────────────────

    @staticmethod
    def get_available_interfaces() -> list:
        """
        Lista wlan* interfaces desde /proc/net/dev.

        Returns:
            list[str]: sorted wlan0, wlan1...
        """
        interfaces = []
        try:
            with open("/proc/net/dev", "r") as f:
                for line in f:
                    line = line.strip()
                    if ":" in line:
                        iface = line.split(":")[0].strip()
                        if iface.startswith("wlan"):
                            interfaces.append(iface)
        except Exception as e:
            logger.warning("[WiFiMonitor] Error leyendo interfaces: %s", e)
        return sorted(interfaces)

    # ── Persistencia de interfaz ──────────────────────────────────────────────

    @staticmethod
    def _load_saved_interface() -> Optional[str]:
        """
        Carga interfaz desde local_settings.py.

        Returns:
            str or None
        """
        try:
            from config.local_settings_io import get_param
            return get_param("wifi_interface", None)
        except Exception:
            return None

    @staticmethod
    def _persist_interface(iface: str) -> None:
        """
        Persiste iface en local_settings.py.
        """
        try:
            from config.local_settings_io import update_params
            update_params({"wifi_interface": iface})
        except Exception as e:
            logger.warning("[WiFiMonitor] No se pudo persistir interfaz: %s", e)

    # ── Loop interno ──────────────────────────────────────────────────────────

    def _loop(self):
        """
        Thread loop: poll inicial + repeat cada _POLL_INTERVAL.
        """
        self._poll()
        while not self._stop_evt.wait(_POLL_INTERVAL):
            self._poll()

    def _poll(self):
        """
        Ciclo de polling: iwconfig/iw + proc/net/dev → update info/hist/tráfico.
        """
        try:
            # Capturar interfaz actual bajo lock para evitar race con set_interface
            with self._lock:
                iface = self._iface

            # ── Señal via iwconfig ─────────────────────────────────────────────
            iwconfig_raw = _run(["iwconfig", iface])
            iw_data      = _parse_iwconfig(iwconfig_raw)

            # Fallback a `iw dev link` si iwconfig no devuelve SSID
            if not iw_data["ssid"]:
                iw_link_raw = _run(["iw", "dev", iface, "link"])
                iw_link     = _parse_iw_link(iw_link_raw)
                if iw_link["ssid"]:
                    iw_data["ssid"] = iw_link["ssid"]
                if iw_data["signal_dbm"] is None:
                    iw_data["signal_dbm"] = iw_link["signal_dbm"]
                if not iw_data["bitrate"]:
                    iw_data["bitrate"] = iw_link["bitrate"]

            connected = bool(iw_data["ssid"])

            # ── Tráfico via /proc/net/dev ──────────────────────────────────────
            rx_bytes, tx_bytes = self._read_proc_net_dev(iface)
            rx_mbps, tx_mbps  = self._calc_speed(rx_bytes, tx_bytes)

            ts = datetime.now().strftime("%H:%M:%S")

            with self._lock:
                # Verificar que la interfaz no cambió durante el poll
                if self._iface != iface:
                    return
                self._info = {**iw_data, "connected": connected}
                self._rx_mbps = rx_mbps
                self._tx_mbps = tx_mbps
                self._last_update = ts

                if iw_data["signal_dbm"] is not None:
                    self._signal_hist.append(iw_data["signal_dbm"])
                self._rx_hist.append(rx_mbps)
                self._tx_hist.append(tx_mbps)

            logger.debug(
                "[WiFiMonitor] Poll: ssid=%s signal=%s dBm rx=%.2f tx=%.2f Mb/s",
                iw_data['ssid'], iw_data['signal_dbm'], rx_mbps, tx_mbps,
            )

        except Exception as e:
            logger.error("[WiFiMonitor] Error en poll: %s", e)

    def _read_proc_net_dev(self, iface: str) -> tuple:
        """
        Lee bytes RX/TX desde /proc/net/dev para iface.

        Returns:
            tuple[int, int]: (rx_bytes, tx_bytes)
        """
        try:
            with open("/proc/net/dev", "r") as f:
                for line in f:
                    if iface in line:
                        parts = line.split()
                        return int(parts[1]), int(parts[9])
        except Exception as e:
            logger.warning("[WiFiMonitor] Error leyendo /proc/net/dev: %s", e)
        return 0, 0

    def _calc_speed(self, rx: int, tx: int) -> tuple:
        """
        Calcula Mbps desde bytes prev/current div _POLL_INTERVAL.

        Actualiza _prev_rx/tx. Wrap around manejo max(0, delta).

        Returns:
            tuple[float, float]: (rx_mbps, tx_mbps)
        """
        rx_mbps = 0.0
        tx_mbps = 0.0

        if self._prev_rx is not None and self._prev_tx is not None:
            delta_rx = max(0, rx - self._prev_rx)
            delta_tx = max(0, tx - self._prev_tx)
            rx_mbps = (delta_rx / _POLL_INTERVAL) / 1_048_576
            tx_mbps = (delta_tx / _POLL_INTERVAL) / 1_048_576

        self._prev_rx = rx
        self._prev_tx = tx
        return rx_mbps, tx_mbps

    # ── Acceso a datos ────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """
        Snapshot completo thread-safe no-bloqueante.

        Returns:
            dict: info, velocidades, históricos, timestamp.
        """
        acquired = self._lock.acquire(blocking=False)
        if not acquired:
            return {
                "info":        dict(self._info),
                "rx_mbps":     0.0,
                "tx_mbps":     0.0,
                "signal_hist": [],
                "rx_hist":     [],
                "tx_hist":     [],
                "last_update": "",
            }
        try:
            return {
                "info":        dict(self._info),
                "rx_mbps":     self._rx_mbps,
                "tx_mbps":     self._tx_mbps,
                "signal_hist": list(self._signal_hist),
                "rx_hist":     list(self._rx_hist),
                "tx_hist":     list(self._tx_hist),
                "last_update": self._last_update,
            }
        finally:
            self._lock.release()

    @property
    def interface(self) -> str:
        """
        Interfaz actual (read-only).

        Returns:
            str: e.g. "wlan0"
        """
        return self._iface

    @staticmethod
    def signal_color(dbm: Optional[int], colors: dict) -> str:
        """
        Color semáforo por dBm.

        Args:
            dbm (int|None): Nivel señal.
            colors (dict): {'success', 'warning', 'danger', 'text_dim'}

        Returns:
            str: Clave color.
        """
        if dbm is None:
            return colors['text_dim']
        if dbm >= WIFI_SIGNAL_GOOD:
            return colors['success']
        if dbm >= WIFI_SIGNAL_WARN:
            return colors['warning']
        return colors['danger']

    @staticmethod
    def signal_quality_pct(dbm: Optional[int]) -> int:
        """
        Convierte dBm → % calidad (0-100, no lineal).

        Returns:
            int: 0 (pésimo) - 100 (excelente)
        """
        if dbm is None:
            return 0
        pct = 2 * (dbm + 100)
        return max(0, min(100, pct))

