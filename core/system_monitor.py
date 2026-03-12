"""
Monitor del sistema
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

_BOOT_TIME = psutil.boot_time()  # se lee una sola vez al importar


class SystemMonitor:
    """
    Monitor centralizado de recursos del sistema.

    Las métricas se actualizan en un thread de background cada UPDATE_MS ms.
    La UI siempre lee del caché (get_current_stats / get_cached_stats),
    nunca bloquea el hilo principal de Tkinter.
    """

    def __init__(self):
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
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="SystemMonitorPoll")
        self._thread.start()
        logger.info("[SystemMonitor] Sondeo iniciado (cada %.1fs)", self._interval_s)

    def stop(self) -> None:
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

    def _poll_loop(self) -> None:
        self._do_poll()
        while self._running:
            self._stop_evt.wait(timeout=self._interval_s)
            if self._stop_evt.is_set():
                break
            self._do_poll()

    def _do_poll(self) -> None:
        try:
            cpu  = psutil.cpu_percent()
            vm   = psutil.virtual_memory()
            temp = self._system_utils.get_cpu_temp()

            uptime_s = time.time() - _BOOT_TIME
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
                'uptime_str': uptime_str,
            }

            with self._cache_lock:
                self._cached = stats

            self.update_history(stats)

        except Exception as e:
            logger.error("[SystemMonitor] Error en _do_poll: %s", e)

    def get_current_stats(self) -> Dict:
        if not self._running:
            return {
                'cpu': 0.0, 'ram': 0.0, 'temp': 0.0, 'uptime_str': '--',
            }
        with self._cache_lock:
            return dict(self._cached)

    get_cached_stats = get_current_stats

    def update_history(self, stats: Dict) -> None:
        self._cpu_hist.append(stats['cpu'])
        self._ram_hist.append(stats['ram'])
        self._temp_hist.append(stats['temp'])

    def get_history(self) -> Dict:
        return {
            'cpu':  list(self._cpu_hist),
            'ram':  list(self._ram_hist),
            'temp': list(self._temp_hist),
        }

    @staticmethod
    def level_color(value: float, warn: float, crit: float) -> str:
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS['warning']
        return COLORS['primary']
