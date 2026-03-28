"""
Servicio de limpieza automática de archivos exportados y datos antiguos
"""
import os
import glob
import threading
import time
from typing import Optional
from config.settings import DATA_DIR, EXPORTS_CSV_DIR, EXPORTS_LOG_DIR, EXPORTS_SCR_DIR
from utils.logger import get_logger

logger = get_logger(__name__)


class CleanupService:
    """
    Servicio de limpieza que elimina periódicamente archivos exportados y datos antiguos de la base de datos de manera segura en segundo plano.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """

    _instance: Optional['CleanupService'] = None
    _lock = threading.Lock()

    # ── Configuración por defecto ─────────────────────────────────────────────
    DEFAULT_MAX_CSV        = 10
    DEFAULT_MAX_PNG        = 10
    DEFAULT_MAX_LOG        = 10
    DEFAULT_DB_DAYS        = 90
    DEFAULT_INTERVAL_HOURS = 24

    def __new__(cls, *args, **kwargs):
        """
        Crea una instancia única de la clase utilizando el patrón singleton thread-safe.

        Args:
            *args: Argumentos posicionales ignorados.
            **kwargs: Argumentos clave-valor ignorados.

        Returns:
            La instancia única de la clase.

        Raises:
            None
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(
        self,
        data_logger=None,
        max_csv: int = DEFAULT_MAX_CSV,
        max_png: int = DEFAULT_MAX_PNG,
        max_log: int = DEFAULT_MAX_LOG,
        db_days: int = DEFAULT_DB_DAYS,
        interval_hours: float = DEFAULT_INTERVAL_HOURS,
    ):
        """
        Inicializa el servicio de limpieza con los parámetros especificados.

        Args:
            data_logger: Instancia de DataLogger para limpiar la BD.
            max_csv: Número máximo de CSV exportados a conservar.
            max_png: Número máximo de PNG exportados a conservar.
            max_log: Número máximo de logs exportados a conservar.
            db_days: Días de histórico a conservar en la BD.
            interval_hours: Horas entre ejecuciones del ciclo de limpieza.
        """
        if hasattr(self, '_initialized'):
            logger.debug("[CleanupService] Instancia singleton ya inicializada — parámetros ignorados")
            return

        self._data_logger    = data_logger
        self._max_csv        = max_csv
        self._max_png        = max_png
        self._max_log        = max_log
        self._db_days        = db_days
        self._interval_hours = interval_hours

        self._running = False
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._initialized = True

        logger.info(
            "[CleanupService] Configurado — CSV: %d, PNG: %d, LOG: %d, BD: %d Dias, intervalo: %g Horas",
            self._max_csv, self._max_png, self._max_log, self._db_days, self._interval_hours
        )

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self):
        """
        Inicia el servicio de limpieza en segundo plano.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        if self._running:
            logger.info("[CleanupService] Ya está corriendo")
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="CleanupService"
        )
        self._thread.start()
        logger.info("[CleanupService] Servicio iniciado")

    def stop(self):
        """
        Detiene el servicio de limpieza.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        if not self._running:
            return
        self._running = False
        self._stop_evt.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[CleanupService] Servicio detenido")

    def _run(self):
        """
        Ejecuta el ciclo de limpieza inicial y luego cada intervalo de horas configurado.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._cleanup_cycle()
        interval_seconds = self._interval_hours * 3600
        while not self._stop_evt.wait(timeout=interval_seconds):
            if self._running:
                self._cleanup_cycle()
                
    def is_running(self) -> bool:
        """
        Verifica si el servicio de limpieza está en ejecución.

        Args:
            None

        Returns:
            bool: True si el servicio está corriendo, False de lo contrario.

        Raises:
            None
        """
        return self._running

    # ── Lógica de limpieza ────────────────────────────────────────────────────

    def _cleanup_cycle(self):
        """
        Ejecuta un ciclo completo de limpieza.

        Args:
            Ninguno.

        Returns:
            Ninguno.

        Raises:
            Ninguno.
        """
        if not self._running:
            return
        logger.info("[CleanupService] Iniciando ciclo de limpieza")
        self.clean_csv()
        self.clean_png()
        self.clean_log_exports()
        if self._data_logger:
            self.clean_db()
        logger.info("[CleanupService] Ciclo de limpieza completado")

    def clean_csv(self, max_files: int = None) -> int:
        """
        Elimina los archivos CSV de exportación más antiguos que superen el límite especificado.

        Args:
            max_files: Límite de archivos a conservar. Si es None, se utiliza el valor por defecto.

        Returns:
            Número de archivos CSV eliminados.

        Raises:
            None
        """
        if not self._running:
            return 0
        limit   = max_files if max_files is not None else self._max_csv
        pattern = os.path.join(str(EXPORTS_CSV_DIR), "history_*.csv")
        return self._trim_files(pattern, limit, "CSV")

    def clean_png(self, max_files: int = None) -> int:
        """
        Elimina los PNG exportados más antiguos que superen el límite configurado.

        Args:
            max_files (int): Límite de archivos a conservar. Si es None, se utiliza el valor por defecto.

        Returns:
            int: Número de archivos PNG eliminados.

        Raises:
            None
        """
        if not self._running:
            return 0
        limit   = max_files if max_files is not None else self._max_png
        pattern = os.path.join(str(EXPORTS_SCR_DIR), "*.png")
        return self._trim_files(pattern, limit, "PNG")

    def clean_log_exports(self, max_files: int = None) -> int:
        """
        Elimina los archivos de exportación de logs más antiguos que superen el límite.

        Args:
            max_files (int): Límite a aplicar. Si es None, se utiliza el valor predeterminado.

        Returns:
            int: Número de archivos eliminados.

        Raises:
            None
        """
        if not self._running:
            return 0
        limit   = max_files if max_files is not None else self._max_log
        pattern = os.path.join(str(EXPORTS_LOG_DIR), "log_export_*.log")
        return self._trim_files(pattern, limit, "LOG_EXPORT")

    def clean_db(self, days: int = None) -> bool:
        """
        Elimina registros de la base de datos más antiguos que un número determinado de días.

        Args:
            days (int): Número de días. Si es None, se utiliza el valor por defecto configurado.

        Returns:
            bool: True si la limpieza fue exitosa.

        Raises:
            Exception: Si ocurre un error durante la limpieza de la base de datos.
        """
        if not self._running:
            return False
        if not self._data_logger:
            logger.warning("[CleanupService] No hay data_logger configurado")
            return False
        d = days if days is not None else self._db_days
        try:
            self._data_logger.clean_old_data(days=d)
            logger.info("[CleanupService] BD limpiada — registros >%dd eliminados", d)
            return True
        except Exception as e:
            logger.error("[CleanupService] Error limpiando BD: %s", e)
            return False

    def _trim_files(self, pattern: str, max_files: int, label: str) -> int:
        """
        Elimina los archivos más antiguos que superen el número máximo permitido según un patrón.

        Args:
            pattern (str): Patrón glob de los archivos a gestionar.
            max_files (int): Número máximo de archivos a conservar.
            label (str): Etiqueta para el log.

        Returns:
            int: Número de archivos eliminados.

        Raises:
            Exception: Si ocurre un error durante la eliminación de archivos.
        """
        if not self._running:
            return 0
        try:
            files     = sorted(glob.glob(pattern), key=os.path.getmtime)
            to_delete = files[:-max_files] if len(files) > max_files else []
            for f in to_delete:
                try:
                    os.remove(f)
                    logger.info("[CleanupService] %s eliminado: %s", label, os.path.basename(f))
                except Exception as e:
                    logger.warning("[CleanupService] No se pudo eliminar %s: %s", f, e)
            if to_delete:
                logger.info(
                    "[CleanupService] %s: %d eliminados, %d conservados",
                    label, len(to_delete), len(files) - len(to_delete)
                )
            return len(to_delete)
        except Exception as e:
            logger.error("[CleanupService] Error en _trim_files (%s): %s", label, e)
            return 0

    # ── Información y estado ──────────────────────────────────────────────────

    def get_status(self) -> dict:
        """
        Devuelve el estado actual del servicio de limpieza.
        Args: 
            None
        Returns:
            dict: Diccionario con la configuración y el estado del hilo de limpieza.
                Contiene información sobre el estado de ejecución, intervalos y conteo de archivos.
        Raises: 
            None
        """
        csv_files = glob.glob(os.path.join(str(EXPORTS_CSV_DIR), "history_*.csv"))
        png_files = glob.glob(os.path.join(str(EXPORTS_SCR_DIR), "*.png"))
        log_files = glob.glob(os.path.join(str(EXPORTS_LOG_DIR), "log_export_*.log"))
        return {
            'running':        self._running,
            'thread_alive':   self._thread.is_alive() if self._thread else False,
            'interval_hours': self._interval_hours,
            'max_csv':        self._max_csv,
            'max_png':        self._max_png,
            'max_log':        self._max_log,
            'db_days':        self._db_days,
            'csv_count':      len(csv_files),
            'png_count':      len(png_files),
            'log_count':      len(log_files),
        }

    def force_cleanup(self) -> dict:
        """
        Fuerza un ciclo de limpieza inmediato de archivos y base de datos.

        Args: None

        Returns:
            dict: Diccionario con el número de archivos eliminados y resultado de la limpieza de base de datos.

        Raises: None
        """
        logger.info("[CleanupService] Limpieza forzada manualmente")
        deleted_csv = self.clean_csv()
        deleted_png = self.clean_png()
        deleted_log = self.clean_log_exports()
        db_ok       = self.clean_db() if self._data_logger else False
        logger.info(
            "[CleanupService] Limpieza manual completada — CSV: %d, PNG: %d, LOG: %d, BD: %s",
            deleted_csv, deleted_png, deleted_log, db_ok
        )
        return {
            'deleted_csv': deleted_csv,
            'deleted_png': deleted_png,
            'deleted_log': deleted_log,
            'db_ok':       db_ok,
        }

    
