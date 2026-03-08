"""
Monitor de conexión WiFi.
Recopila SSID, señal, bitrate y tráfico de la interfaz inalámbrica.
Corre en thread daemon con refresco cada 5 segundos.
"""
import re
import subprocess
import threading
from collections import deque
from typing import Optional
from config.settings import HISTORY
from utils.logger import get_logger

logger = get_logger(__name__)

_POLL_INTERVAL = 5    # segundos
_IFACE_DEFAULT = "wlan0"

# Umbrales de señal (dBm)
WIFI_SIGNAL_GOOD = -60
WIFI_SIGNAL_WARN = -75


def _run(cmd: list) -> str:
    """Ejecuta un comando y devuelve stdout o string vacío si falla."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception as e:
        logger.warning(f"[WiFiMonitor] Error ejecutando {cmd}: {e}")
        return ""


def _parse_iwconfig(raw: str) -> dict:
    """
    Parsea la salida de `iwconfig <iface>` y extrae los campos relevantes.

    Devuelve dict con claves:
        ssid, signal_dbm, link_quality, link_quality_max, bitrate, noise_dbm
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
    Parsea la salida de `iw dev <iface> link` como fuente alternativa/complementaria.

    Devuelve dict con claves: ssid, signal_dbm, bitrate
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
    """Servicio de monitoreo de conexión WiFi."""

    def __init__(self, interface: Optional[str] = None):
        self._iface    = interface or _IFACE_DEFAULT
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
        self.signal_hist = deque(maxlen=HISTORY)
        self.rx_hist     = deque(maxlen=HISTORY)
        self.tx_hist     = deque(maxlen=HISTORY)

        self._last_update: str = ""

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self):
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="WiFiMonitor"
        )
        self._thread.start()
        logger.info(f"[WiFiMonitor] Servicio iniciado — interfaz: {self._iface}")

    def stop(self):
        self._running = False
        self._stop_evt.set()
        logger.info("[WiFiMonitor] Servicio detenido")

    # ── Loop interno ──────────────────────────────────────────────────────────

    def _loop(self):
        self._poll()   # primera lectura inmediata
        while not self._stop_evt.wait(_POLL_INTERVAL):
            self._poll()

    def _poll(self):
        try:
            from datetime import datetime

            # ── Señal via iwconfig ─────────────────────────────────────────────
            iwconfig_raw = _run(["iwconfig", self._iface])
            iw_data      = _parse_iwconfig(iwconfig_raw)

            # Fallback a `iw dev link` si iwconfig no devuelve SSID
            if not iw_data["ssid"]:
                iw_link_raw = _run(["iw", "dev", self._iface, "link"])
                iw_link     = _parse_iw_link(iw_link_raw)
                if iw_link["ssid"]:
                    iw_data["ssid"] = iw_link["ssid"]
                if iw_data["signal_dbm"] is None:
                    iw_data["signal_dbm"] = iw_link["signal_dbm"]
                if not iw_data["bitrate"]:
                    iw_data["bitrate"] = iw_link["bitrate"]

            connected = bool(iw_data["ssid"])

            # ── Tráfico via /proc/net/dev ──────────────────────────────────────
            rx_bytes, tx_bytes = self._read_proc_net_dev()
            rx_mbps, tx_mbps  = self._calc_speed(rx_bytes, tx_bytes)

            ts = datetime.now().strftime("%H:%M:%S")

            with self._lock:
                self._info = {**iw_data, "connected": connected}
                self._rx_mbps = rx_mbps
                self._tx_mbps = tx_mbps
                self._last_update = ts

                if iw_data["signal_dbm"] is not None:
                    self.signal_hist.append(iw_data["signal_dbm"])
                self.rx_hist.append(rx_mbps)
                self.tx_hist.append(tx_mbps)

            """logger.debug(
                f"[WiFiMonitor] Poll: ssid={iw_data['ssid']} "
                f"signal={iw_data['signal_dbm']}dBm "
                f"rx={rx_mbps:.3f} tx={tx_mbps:.3f} MB/s"
            )"""

        except Exception as e:
            logger.error(f"[WiFiMonitor] Error en poll: {e}")

    def _read_proc_net_dev(self) -> tuple:
        """Lee rx_bytes y tx_bytes de /proc/net/dev para la interfaz."""
        try:
            with open("/proc/net/dev", "r") as f:
                for line in f:
                    if self._iface in line:
                        parts = line.split()
                        # Columnas: iface rx_bytes rx_pkts ... tx_bytes ...
                        # rx_bytes = col 1, tx_bytes = col 9
                        return int(parts[1]), int(parts[9])
        except Exception as e:
            logger.warning(f"[WiFiMonitor] Error leyendo /proc/net/dev: {e}")
        return 0, 0

    def _calc_speed(self, rx: int, tx: int) -> tuple:
        """Calcula velocidad MB/s respecto a la medición anterior."""
        rx_mbps = 0.0
        tx_mbps = 0.0

        if self._prev_rx is not None and self._prev_tx is not None:
            delta_rx = max(0, rx - self._prev_rx)
            delta_tx = max(0, tx - self._prev_tx)
            # Convertir bytes/intervalo → MB/s
            rx_mbps = (delta_rx / _POLL_INTERVAL) / 1_048_576
            tx_mbps = (delta_tx / _POLL_INTERVAL) / 1_048_576

        self._prev_rx = rx
        self._prev_tx = tx
        return rx_mbps, tx_mbps

    # ── Acceso a datos ────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Lectura no bloqueante — si el lock está cogido devuelve snapshot vacío."""
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
                "signal_hist": list(self.signal_hist),
                "rx_hist":     list(self.rx_hist),
                "tx_hist":     list(self.tx_hist),
                "last_update": self._last_update,
            }
        finally:
            self._lock.release()

    @property
    def interface(self) -> str:
        return self._iface

    @staticmethod
    def signal_color(dbm: Optional[int], colors: dict) -> str:
        """Devuelve color según nivel de señal dBm."""
        if dbm is None:
            return colors['text_dim']
        if dbm >= WIFI_SIGNAL_GOOD:
            return colors['success']
        if dbm >= WIFI_SIGNAL_WARN:
            return colors['warning']
        return colors['danger']

    @staticmethod
    def signal_quality_pct(dbm: Optional[int]) -> int:
        """Convierte dBm a porcentaje de calidad (0-100)."""
        if dbm is None:
            return 0
        # Rango típico: -30 dBm (excelente) a -90 dBm (sin señal)
        pct = 2 * (dbm + 100)
        return max(0, min(100, pct))
