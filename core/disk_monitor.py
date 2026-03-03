"""
Monitor de disco
"""
import subprocess
import json
import threading
from collections import deque
from typing import Dict
from config.settings import HISTORY, UPDATE_MS, COLORS
from utils.system_utils import SystemUtils, get_logger
import psutil

logger = get_logger(__name__)


class DiskMonitor:
    """Monitor de disco con historial"""

    def __init__(self):
        self.system_utils = SystemUtils()

        self.usage_hist    = deque(maxlen=HISTORY)
        self.read_hist     = deque(maxlen=HISTORY)
        self.write_hist    = deque(maxlen=HISTORY)
        self.nvme_temp_hist = deque(maxlen=HISTORY)

        self._cache_lock = threading.Lock()
        self._cache: Dict = {
            'disk_usage':   0.0,
            'disk_read_mb': 0.0,
            'disk_write_mb': 0.0,
            'nvme_temp':    0.0,
        }

        self.last_disk_io = psutil.disk_io_counters()
        self._running   = False
        self._stop_evt  = threading.Event()
        self._thread    = None
        self._interval_s = max(UPDATE_MS / 1000.0, 1.0)

        self.start()

    def start(self):
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="DiskMonitorPoll"
        )
        self._thread.start()
        logger.info("[DiskMonitor] sondeo iniciado (cada %.1fs)", self._interval_s)

    def stop(self):
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        with self._cache_lock:
            self._cache = {
                'disk_usage':   0.0,
                'disk_read_mb': 0.0,
                'disk_write_mb': 0.0,
                'nvme_temp':    0.0,
            }
        logger.info("[DiskMonitor] Detenido")

    def _poll_loop(self) -> None:
        self._do_poll()
        while self._running:
            self._stop_evt.wait(timeout=self._interval_s)
            if self._stop_evt.is_set():
                break
            self._do_poll()

    def _do_poll(self):
        try:
            disk_usage = psutil.disk_usage('/').percent

            disk_io     = psutil.disk_io_counters()
            read_bytes  = max(0, disk_io.read_bytes  - self.last_disk_io.read_bytes)
            write_bytes = max(0, disk_io.write_bytes - self.last_disk_io.write_bytes)
            self.last_disk_io = disk_io

            read_mb  = (read_bytes  / (1024 * 1024)) / self._interval_s
            write_mb = (write_bytes / (1024 * 1024)) / self._interval_s

            nvme_temp = self.system_utils.get_nvme_temp()
            stats = {
                'disk_usage':   disk_usage,
                'disk_read_mb': read_mb,
                'disk_write_mb': write_mb,
                'nvme_temp':    nvme_temp,
            }

            with self._cache_lock:
                self._cache = stats
            self.update_history(stats)

        except Exception as e:
            logger.error("[DiskMonitor] Error en _do_poll: %s", e)

    def get_current_stats(self) -> Dict:
        if not self._running:
            return {
                'disk_usage':   0.0,
                'nvme_temp':    0.0,
                'disk_write_mb': 0.0,
                'disk_read_mb': 0.0,
            }
        with self._cache_lock:
            return dict(self._cache)

    get_cached_stats = get_current_stats

    def update_history(self, stats: Dict) -> None:
        """
        Actualiza historiales con estadísticas actuales.

        Args:
            stats: Diccionario con estadísticas
        """
        self.usage_hist.append(stats['disk_usage'])
        self.read_hist.append(stats['disk_read_mb'])
        self.write_hist.append(stats['disk_write_mb'])
        self.nvme_temp_hist.append(stats['nvme_temp'])

    def get_history(self) -> Dict:
        """
        Obtiene todos los historiales.

        Returns:
            Diccionario con historiales
        """
        return {
            'disk_usage': list(self.usage_hist),
            'disk_read':  list(self.read_hist),
            'disk_write': list(self.write_hist),
            'nvme_temp':  list(self.nvme_temp_hist),
        }

    def get_nvme_smart(self) -> dict:
        """
        Devuelve métricas SMART extendidas del NVMe via smartctl.

        Requiere en sudoers:
            usuario ALL=(ALL) NOPASSWD: /usr/bin/smartctl

        Campos devueltos:
            power_on_hours    — horas de uso total
            power_cycles      — veces encendido
            unsafe_shutdowns  — apagados sin guardar
            data_written_tb   — TB escritos en vida
            data_read_tb      — TB leídos en vida
            percentage_used   — % de vida útil consumida (0=nuevo, 100=al límite)
            available         — False si smartctl falla o no hay NVMe
        """
        if not self._running:
            return {'available': False}

        result = {
            "power_on_hours":   None,
            "power_cycles":     None,
            "unsafe_shutdowns": None,
            "data_written_tb":  None,
            "data_read_tb":     None,
            "percentage_used":  None,
            "available":        False,
        }
        try:
            r = subprocess.run(
                ["sudo", "smartctl", "-A", "--json", "/dev/nvme0"],
                capture_output=True, text=True, timeout=10
            )
            # smartctl devuelve 0 o bitmask de warnings no fatales (2, 4, 6...)
            # Solo falla si el bit 0 o bit 1 está activo (error real)
            if r.returncode & 0b00000011:
                return result

            data  = json.loads(r.stdout)
            attrs = data.get("nvme_smart_health_information_log", {})

            result["power_on_hours"]   = attrs.get("power_on_hours")
            result["power_cycles"]     = attrs.get("power_cycles")
            result["unsafe_shutdowns"] = attrs.get("unsafe_shutdowns")
            result["percentage_used"]  = attrs.get("percentage_used")

            # data_units_written/read vienen en unidades de 512.000 bytes
            dw = attrs.get("data_units_written")
            dr = attrs.get("data_units_read")
            if dw is not None:
                result["data_written_tb"] = round(dw * 512_000 / (1024 ** 4), 2)
            if dr is not None:
                result["data_read_tb"]    = round(dr * 512_000 / (1024 ** 4), 2)

            result["available"] = True

        except FileNotFoundError:
            pass   # smartctl no instalado
        except subprocess.TimeoutExpired:
            pass   # NVMe no responde
        except Exception as e:
            logger.debug("[DiskMonitor] get_nvme_smart error: %s", e)

        return result

    @staticmethod
    def level_color(value: float, warn: float, crit: float) -> str:
        """
        Determina color según nivel.

        Args:
            value: Valor actual
            warn:  Umbral de advertencia
            crit:  Umbral crítico

        Returns:
            Color en formato hex
        """
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS['warning']
        return COLORS['primary']
