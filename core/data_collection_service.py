"""
Servicio de recolección automática de datos
"""
import threading
import time
from datetime import datetime
from core import DataLogger
from utils.file_manager import FileManager
from utils.logger import get_logger
 
logger = get_logger(__name__)
 
 
class DataCollectionService:
    """Servicio que recolecta métricas cada X minutos"""
 
    _instance = None
    _lock = threading.Lock()
 
    def __new__(cls, *args, **kwargs):
        """
        Implementa patrón singleton thread-safe.
        """
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

 
    def __init__(self, system_monitor, fan_controller, network_monitor,
                 disk_monitor, update_monitor, interval_minutes: int = 5):
        """
        Inicializa singleton DataCollectionService.

        Args:
            system_monitor, fan_controller, network_monitor, disk_monitor, update_monitor: Fuentes métricas.
            interval_minutes (int): Minutos entre recolecciones (default 5).
        """
        if hasattr(self, '_initialized'):
            return
 
        self._system_monitor   = system_monitor
        self._fan_file         = FileManager()   # lee fan_state.json para el PWM
        self._network_monitor  = network_monitor
        self._disk_monitor     = disk_monitor
        self._update_monitor   = update_monitor
        self._interval_minutes = interval_minutes
 
        self._data_logger = DataLogger()
        self._running     = False
        self._stop_evt    = threading.Event()
        self._thread      = None
 
        self._initialized = True

 
    # ── Ciclo de vida ─────────────────────────────────────────────────────────
 
    def start(self):
        """Inicia el servicio de recolección"""
        if self._running:
            logger.info("[DataCollection] Servicio ya está corriendo")
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._collection_loop, daemon=True, name="DataCollection"
        )
        self._thread.start()
        logger.info("[DataCollection] Servicio iniciado (cada %d min)", self._interval_minutes)
 
    def stop(self):
        """Detiene el servicio limpiamente."""
        if not self._running:
            return
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=6)
        logger.info("[DataCollection] Servicio detenido")
 
    def is_running(self) -> bool:
        """Verifica si el servicio está corriendo"""
        return self._running
 
    # ── Bucle principal ───────────────────────────────────────────────────────
 
    def _collection_loop(self):
        """Bucle principal de recolección"""
        self._collect_and_save()
        while not self._stop_evt.wait(timeout=self._interval_minutes * 60):
            try:
                self._collect_and_save()
            except Exception as e:
                logger.error("[DataCollection] Error en recolección: %s", e)
 
    def _collect_and_save(self):
        """Recolecta métricas y las guarda"""
        system_stats  = self._system_monitor.get_current_stats()
        network_stats = self._network_monitor.get_current_stats()
        disk_stats    = self._disk_monitor.get_current_stats()
        update_stats  = self._update_monitor.check_updates()
        fan_state     = self._fan_file.load_state()
 
        metrics = {
            'cpu_percent':       system_stats.get('cpu', 0),
            'ram_percent':       system_stats.get('ram', 0),
            'ram_used_gb':       "{:.2f}".format(system_stats.get('ram_used', 0) / (1024 ** 3)),
            'temperature':       system_stats.get('temp', 0),
            'disk_used_percent': disk_stats.get('disk_usage', 0),
            'disk_read_mb':      "{:.2f}".format(disk_stats.get('disk_read_mb', 0)),
            'disk_write_mb':     "{:.2f}".format(disk_stats.get('disk_write_mb', 0)),
            'net_download_mb':   "{:.2f}".format(network_stats.get('download_mb', 0)),
            'net_upload_mb':     "{:.2f}".format(network_stats.get('upload_mb', 0)),
            'fan_pwm':           fan_state.get('target_pwm', 0),
            'fan_mode':          fan_state.get('mode', 'unknown'),
            'updates_available': update_stats.get('pending', 0),
            'uptime_s':          system_stats.get('uptime_s', 0),
        }
 
        self._data_logger.log_metrics(metrics)
 
        if metrics['temperature'] > 80:
            self._data_logger.log_event(
                'temp_high', 'critical',
                "Temperatura alta detectada: %.1f\u00b0C" % metrics['temperature'],
                {'temperature': metrics['temperature']}
            )
 
        if metrics['cpu_percent'] > 90:
            self._data_logger.log_event(
                'cpu_high', 'warning',
                "CPU alta detectada: %.1f%%" % metrics['cpu_percent'],
                {'cpu': metrics['cpu_percent']}
            )
 
        logger.info(
            "[DataCollection] Métricas guardadas: %s",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
 
    def force_collection(self):
        """Fuerza una recolección inmediata"""
        self._collect_and_save()