"""
Monitor del sistema
Monitor centralizado de métricas CPU, RAM, temperatura y uptime con histórico para UI.
Thread background no-bloqueante, thread-safe con lock.
"""
import time
import threading
import psutil
from collections import deque
from typing import Dict
from config.settings import HISTORY, UPDATE_MS, COLORS
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)



class SystemMonitor:
    """
    Inicializa el monitor del sistema.

    Crea las utilidades del sistema, inicializa los historiales de métricas,
    configura el caché y el bloqueo de acceso. Inicia automáticamente el thread
    de actualización en segundo plano.
    """

    def __init__(self):
        """
        Inicializa el monitor del sistema.

        Args: Ninguno

        Returns: Ninguno

        Raises: Ninguno
        """
        self._system_utils = SystemUtils()

        self._cpu_hist  = deque(maxlen=HISTORY)
        self._ram_hist  = deque(maxlen=HISTORY)
        self._temp_hist = deque(maxlen=HISTORY)

        self._cache_lock = threading.Lock()
        self._cached: Dict = {
            'cpu': 0.0, 'ram': 0.0, 'ram_used': 0,
            'temp': 0.0, 'uptime_str': '--',
        }

        self._running    = False
        self._stop_evt   = threading.Event()
        self._thread     = None
        self._interval_s = max(UPDATE_MS / 1000.0, 1.0)

        self.start()

    def start(self) -> None:
        """
        Inicia el hilo de sondeo en segundo plano para monitorear el sistema.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="SystemMonitorPoll")
        self._thread.start()
        logger.info("[SystemMonitor] Sondeo iniciado (cada %.1fs)", self._interval_s)

    def stop(self) -> None:
        """
        Detiene el monitor del sistema de manera limpia.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        self._cached = {
            'cpu': 0.0, 'ram': 0.0, 'temp': 0.0,
            'disk_usage': 0.0, 'disk_write_mb': 0.0, 'disk_read_mb': 0.0,
            'uptime_str': '--',
        }
        logger.info("[SystemMonitor] Sondeo detenido")
    
    def is_running(self) -> bool:
        """
        Indica si el monitor del sistema está actualmente en ejecución.

        Returns:
            bool: True si el monitor está activo, False en caso contrario.
        """
        return self._running

    def _poll_loop(self) -> None:
        """
        Ejecuta el bucle principal del hilo de sondeo en segundo plano.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._do_poll()
        while self._running:
            self._stop_evt.wait(timeout=self._interval_s)
            if self._stop_evt.is_set():
                break
            self._do_poll()

    def _do_poll(self) -> None:
        """
        Captura rápida de métricas del sistema y actualiza la caché.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno, las excepciones se manejan silenciosamente.
        """
        try:
            cpu  = psutil.cpu_percent()
            vm   = psutil.virtual_memory()
            temp = self._system_utils.get_cpu_temp()

            with open("/proc/uptime") as f:
                uptime_s = float(f.read().split()[0])
            days     = int(uptime_s // 86400)
            hours    = int((uptime_s % 86400) // 3600)
            minutes  = int((uptime_s % 3600) // 60)
            uptime_str = (f"⏱ {days}d {hours}h" if days > 0
                          else f"⏱ {hours}h {minutes}m")

            stats = {
                'cpu':        cpu,
                'ram':        vm.percent,
                'ram_used':   vm.used,
                'temp':       temp,
                'uptime_s':   uptime_s,
                'uptime_str': uptime_str,
            }

            with self._cache_lock:
                self._cached = stats

            self.update_history(stats)

        except Exception as e:
            logger.error("[SystemMonitor] Error en _do_poll: %s", e)

    def get_current_stats(self) -> Dict:
        """
        Obtiene las estadísticas actuales del sistema.

        Args:
            Ninguno

        Returns:
            Dict: Un diccionario con las estadísticas actuales del sistema, 
                  incluyendo 'cpu', 'ram', 'ram_used', 'temp' y 'uptime_str'.

        Raises:
            Ninguno
        """
        if not self._running:
            return {
                'cpu': 0.0, 'ram': 0.0, 'temp': 0.0, 'uptime_str': '--',
            }
        with self._cache_lock:
            return dict(self._cached)

    get_cached_stats = get_current_stats

    def update_history(self, stats: Dict) -> None:
        """
        Actualiza los registros históricos de estadísticas del sistema para su representación gráfica.

        Args:
            stats (Dict): Diccionario con las métricas actuales de CPU, RAM y temperatura.

        Returns:
            None

        Raises:
            None
        """
        self._cpu_hist.append(stats['cpu'])
        self._ram_hist.append(stats['ram'])
        self._temp_hist.append(stats['temp'])

    def get_history(self) -> Dict:
        """
        Retorna un diccionario con listas históricas de uso de recursos del sistema.

        Args:
            Ninguno

        Returns:
            Dict: Un diccionario con claves 'cpu', 'ram', 'temp' y valores correspondientes a listas de históricos.

        Raises:
            Ninguno
        """
        return {
            'cpu':  list(self._cpu_hist),
            'ram':  list(self._ram_hist),
            'temp': list(self._temp_hist),
        }

    @staticmethod
    def level_color(value: float, warn: float, crit: float) -> str:
        """
        Determina el color semáforo según umbrales de warning y crítico.

        Args:
            value (float): Valor de la métrica (CPU%, RAM%, TEMP).
            warn (float): Umbral de warning.
            crit (float): Umbral crítico.

        Returns:
            str: Clase de color correspondiente.

        Raises:
            None
        """
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS['warning']
        return COLORS['primary']

