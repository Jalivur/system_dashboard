"""
Servicio de recolección automática de datos
"""
import threading
import time
from datetime import datetime
from core.data_logger import DataLogger
from utils.file_manager import FileManager
from utils.logger import get_logger

logger = get_logger(__name__)


class DataCollectionService:
    """Servicio que recolecta métricas cada X minutos"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, system_monitor, fan_controller, network_monitor,
                 disk_monitor, update_monitor, interval_minutes: int = 5):
        if hasattr(self, '_initialized'):
            return

        self.system_monitor  = system_monitor
        self.fan_file        = FileManager()   # lee fan_state.json para el PWM
        self.network_monitor = network_monitor
        self.disk_monitor    = disk_monitor
        self.update_monitor  = update_monitor
        self.interval_minutes = interval_minutes

        self.logger  = DataLogger()
        self.running = False
        self.thread  = None

        self._initialized = True

    def start(self):
        """Inicia el servicio de recolección"""
        if self.running:
            logger.info("[DataCollection] Servicio ya está corriendo")
            return
        self.running = True
        self.thread  = threading.Thread(
            target=self._collection_loop, daemon=True, name="DataCollection"
        )
        self.thread.start()
        logger.info("[DataCollection] Servicio iniciado (cada %d min)", self.interval_minutes)

    def stop(self):
        """Detiene el servicio"""
        if not self.running:
            return
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("[DataCollection] Servicio detenido")

    def _collection_loop(self):
        """Bucle principal de recolección"""
        while self.running:
            try:
                self._collect_and_save()
            except Exception as e:
                logger.error("[DataCollection] Error en recolección: %s", e)
            time.sleep(self.interval_minutes * 60)

    def _collect_and_save(self):
        """Recolecta métricas y las guarda"""
        system_stats  = self.system_monitor.get_current_stats()
        network_stats = self.network_monitor.get_current_stats()
        disk_stats    = self.disk_monitor.get_current_stats()
        update_stats  = self.update_monitor.check_updates()
        fan_state     = self.fan_file.load_state()

        metrics = {
            'cpu_percent':      system_stats.get('cpu', 0),
            'ram_percent':      system_stats.get('ram', 0),
            'ram_used_gb':      "{:.2f}".format(system_stats.get('ram_used', 0) / (1024 ** 3)),
            'temperature':      system_stats.get('temp', 0),
            'disk_used_percent': disk_stats.get('disk_usage', 0),
            'disk_read_mb':     "{:.2f}".format(disk_stats.get('disk_read_mb', 0)),
            'disk_write_mb':    "{:.2f}".format(disk_stats.get('disk_write_mb', 0)),
            'net_download_mb':  "{:.2f}".format(network_stats.get('download_mb', 0)),
            'net_upload_mb':    "{:.2f}".format(network_stats.get('upload_mb', 0)),
            'fan_pwm':          fan_state.get('target_pwm', 0),
            'fan_mode':         fan_state.get('mode', 'unknown'),
            'updates_available': update_stats.get('pending', 0),
        }

        self.logger.log_metrics(metrics)

        if metrics['temperature'] > 80:
            self.logger.log_event(
                'temp_high', 'critical',
                f"Temperatura alta detectada: {metrics['temperature']:.1f}°C",
                {'temperature': metrics['temperature']}
            )

        if metrics['cpu_percent'] > 90:
            self.logger.log_event(
                'cpu_high', 'warning',
                f"CPU alta detectada: {metrics['cpu_percent']:.1f}%",
                {'cpu': metrics['cpu_percent']}
            )

        logger.info(
            "[DataCollection] Métricas guardadas: %s",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    def force_collection(self):
        """Fuerza una recolección inmediata"""
        self._collect_and_save()

    def is_running(self) -> bool:
        """Verifica si el servicio está corriendo"""
        return self.running
