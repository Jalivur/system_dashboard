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
    Ejecuta un comando shell y retorna la salida estándar limpia.

    Args:
        cmd (list): Comando a ejecutar.

    Returns:
        str: Salida estándar del comando o cadena vacía en caso de fallo.

    Raises:
        Exception: Si ocurre un error durante la ejecución del comando.
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
    Extrae información WiFi de la salida cruda de iwconfig.

    Args:
        raw (str): Salida cruda de iwconfig.

    Returns:
        dict: Diccionario con métricas WiFi como ssid, signal_dbm, link_quality, link_quality_max, bitrate y noise_dbm.

    Raises:
        None
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
    Extrae información de conexión inalámbrica de la salida del comando `iw dev <iface> link`.

    Args:
        raw (str): Salida cruda del comando `iw dev <iface> link`.

    Returns:
        dict: Diccionario con los campos "ssid", "signal_dbm" y "bitrate".

    Raises:
        None
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
    Monitor de WiFi que proporciona información en tiempo real y históricos de tráfico.

    Args:
        interface (str, optional): Interfaz de red inalámbrica a monitorear.

    Raises:
        Exception: Si no se puede inicializar el monitor.
    """

    def __init__(self, interface: Optional[str] = None):
        """
        Inicializa el monitor de WiFi con una interfaz específica.

        Args:
            interface (str, optional): Interfaz de red inalámbrica, como wlan0 o wlan1.

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
        Inicia el monitoreo de WiFi en segundo plano.

        Args:
            None

        Returns:
            None

        Raises:
            None
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
        Detiene el servicio de monitoreo de WiFi.

        Args:
            None

        Returns:
            None

        Raises:
            None
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
        Indica si el monitor de WiFi está en ejecución.

        Args:
            None

        Returns:
            bool: True si el monitor está en ejecución, False de lo contrario.

        Raises:
            None
        """
        return self._running

    def get_signal_history(self) -> list:
        """
        Obtiene el histórico de señal de WiFi en dBm de los últimos puntos registrados.

        Args:
            No requiere parámetros.

        Returns:
            list: Lista de valores de señal de WiFi en dBm.
        """
        with self._lock:
            return list(self._signal_hist)

    # ── Cambio de interfaz en caliente ────────────────────────────────────────

    def set_interface(self, iface: str) -> None:
        """
        Cambia la interfaz de red en tiempo de ejecución.

        Args:
            iface (str): Nombre de la interfaz de red a utilizar.

        Returns:
            None

        Raises:
            None
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
        Obtiene la lista de interfaces de red inalámbrica disponibles.

        Args: None

        Returns:
            list[str]: Lista ordenada de interfaces inalámbricas disponibles.

        Raises:
            Exception: Si ocurre un error al leer la lista de interfaces.
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
        Carga la interfaz de red WiFi guardada desde la configuración local.

        Args:
            None

        Returns:
            La interfaz de red WiFi guardada o None si no existe.

        Raises:
            Exception: Si ocurre un error al cargar la configuración.
        """
        try:
            from config.local_settings_io import get_param
            return get_param("wifi_interface", None)
        except Exception:
            return None

    @staticmethod
    def _persist_interface(iface: str) -> None:
        """
        Persiste la interfaz de red WiFi en la configuración local.

        Args:
            iface (str): Nombre de la interfaz de red WiFi a persistir.

        Raises:
            Exception: Si ocurre un error al persistir la interfaz.
        """
        try:
            from config.local_settings_io import update_params
            update_params({"wifi_interface": iface})
        except Exception as e:
            logger.warning("[WiFiMonitor] No se pudo persistir interfaz: %s", e)

    # ── Loop interno ──────────────────────────────────────────────────────────

    def _loop(self):
        """
        Ejecuta el bucle de polling del monitor de WiFi.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._poll()
        while not self._stop_evt.wait(_POLL_INTERVAL):
            self._poll()

    def _poll(self):
        """
        Realiza un ciclo de polling para actualizar la información de la interfaz de red inalámbrica.

        Args:
            None

        Returns:
            None

        Raises:
            None
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
        Lee bytes RX/TX desde /proc/net/dev para una interfaz de red específica.

        Args:
            iface (str): Nombre de la interfaz de red.

        Returns:
            tuple[int, int]: Tupla con bytes recibidos y transmitidos.

        Raises:
            Exception: Si ocurre un error al leer el archivo /proc/net/dev.
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
        Calcula la velocidad de transferencia de datos en Mbps.

        Args:
            rx (int): Número de bytes recibidos.
            tx (int): Número de bytes transmitidos.

        Returns:
            tuple[float, float]: Velocidad de recepción y transmisión en Mbps.

        Raises:
            None
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
        Obtiene un snapshot completo de las estadísticas de WiFi de manera thread-safe y no bloqueante.

        Args:
            No aplica.

        Returns:
            dict: Información de WiFi, incluyendo velocidades y registros históricos, junto con un timestamp.

        Raises:
            No aplica.
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
        Obtiene la interfaz de red actual.

        Args:
            Ninguno.

        Returns:
            str: La interfaz de red actual, por ejemplo "wlan0".
        """
        return self._iface

    @staticmethod
    def signal_color(dbm: Optional[int], colors: dict) -> str:
        """
        Determina el color semáforo según el nivel de señal de WiFi en dBm.

        Args:
            dbm (int|None): Nivel de señal de WiFi en dBm.
            colors (dict): Diccionario con claves de color ('success', 'warning', 'danger', 'text_dim').

        Returns:
            str: Clave del color correspondiente al nivel de señal.

        Raises:
            Ninguna excepción relevante.
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
        Convierte un nivel de señal en dBm a porcentaje de calidad de señal de WiFi.

        Args:
            dbm (Optional[int]): Nivel de señal en decibelios con referencia a un miliwatt.

        Returns:
            int: Calidad de señal como porcentaje (0-100).

        Raises:
            Ninguna excepción explícita, devuelve 0 si dbm es None.
        """
        if dbm is None:
            return 0
        pct = 2 * (dbm + 100)
        return max(0, min(100, pct))

