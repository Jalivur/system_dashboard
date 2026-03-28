"""
Sistema de logging robusto para el dashboard
Funciona correctamente tanto desde terminal como desde auto-start

Ubicación: utils/logger.py
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import os


# ── Filtro de nivel exacto ────────────────────────────────────────────────────

class _ExactLevelFilter(logging.Filter):
    """
    Filtra registros de log permitiendo solo aquellos con un nivel de log exacto.

    Args:
        level (int): Nivel de logging exacto (e.g., logging.INFO).

    Returns:
        bool: True si el nivel coincide, False en caso contrario.

    Raises:
        None
    """

    def __init__(self, level: int):
        """
        Inicializa el filtro con el nivel de log exacto especificado.

        Args:
            level (int): Nivel de logging exacto.

        """
        super().__init__()
        self._level = level

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filtra registros de log según su nivel exacto.

        Args:
            record (logging.LogRecord): Registro de log a evaluar.

        Returns:
            bool: True si el nivel coincide, False en caso contrario.
        """
        return record.levelno == self._level


# ── Logger central ────────────────────────────────────────────────────────────

class DashboardLogger:
    """
    Clase que implementa un logger centralizado para el dashboard siguiendo el patrón Singleton.

    Args:
        Ninguno

    Returns:
        DashboardLogger: La instancia única del logger.

    Raises:
        Ninguna excepción explícita.

    Notas:
        La instancia única se crea automáticamente al invocar la clase.
    """

    _instance = None

    def __new__(cls):
        """
        Crea una nueva instancia del logger, aplicando el patrón Singleton para garantizar una única instancia.

        Args:
            cls: La clase DashboardLogger.

        Returns:
            DashboardLogger: La instancia única del logger.

        Raises:
            None
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        """
        Configura el logger con rutas absolutas y rotación automática.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """

        if hasattr(sys, '_MEIPASS'):
            project_root = Path(sys._MEIPASS)
        else:
            project_root = Path(__file__).parent.parent.resolve()

        log_dir = project_root / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = log_dir / "dashboard.log"

        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # ── Leer niveles persistidos antes de crear handlers ──────────────────
        saved = self._load_saved_config(project_root)
        file_level    = saved.get("log_file_level",    logging.DEBUG)
        console_level = saved.get("log_console_level", logging.WARNING)
        console_exact = saved.get("log_console_exact", False)

        # ── File handler ──────────────────────────────────────────────────────
        self._file_handler = RotatingFileHandler(
            self._log_file,
            maxBytes=2 * 1024 * 1024,
            backupCount=1,
            encoding='utf-8',
        )
        self._file_handler.setFormatter(formatter)
        self._file_handler.setLevel(file_level)

        # ── Console handler ───────────────────────────────────────────────────
        self._console_handler = logging.StreamHandler(sys.stdout)
        self._console_handler.setFormatter(formatter)
        self._console_handler.setLevel(console_level)
        self._console_exact = False
        if console_exact:
            self._console_handler.addFilter(_ExactLevelFilter(console_level))
            self._console_exact = True

        # ── Root logger 'Dashboard' ───────────────────────────────────────────
        self.logger = logging.getLogger('Dashboard')
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            self.logger.addHandler(self._file_handler)
            try:
                if sys.stdout and sys.stdout.isatty():
                    self.logger.addHandler(self._console_handler)
            except Exception:
                pass

        # ── Restaurar niveles por módulo ──────────────────────────────────────
        module_levels = saved.get("log_module_levels", {})
        for mod, level in module_levels.items():
            try:
                logging.getLogger(f'Dashboard.{mod}').setLevel(level)
            except Exception:
                pass

        self.logger.info("=" * 60)
        self.logger.info("Logger inicializado - Archivo: %s", self._log_file)
        self.logger.info(
            "Niveles: fichero=%s consola=%s",
            logging.getLevelName(file_level),
            logging.getLevelName(console_level),
        )
        self.logger.info("=" * 60)

    def _load_saved_config(self, project_root: Path) -> dict:
        """
        Carga la configuración guardada de niveles de registro desde el archivo local_settings.py.

        Args:
            project_root: Ruta raíz del proyecto.

        Returns:
            Un diccionario con la configuración guardada de niveles de registro.

        Raises:
            Ninguna excepción es propagada explícitamente, aunque puede ocurrir una excepción genérica durante la ejecución.
        """
        result = {}
        settings_path = project_root / "config" / "local_settings.py"
        if not settings_path.exists():
            return result
        try:
            ns: dict = {}
            exec(settings_path.read_text(encoding="utf-8"), ns)  # noqa: S102
            for key in ("log_file_level", "log_console_level",
                        "log_console_exact", "log_module_levels"):
                if key in ns:
                    result[key] = ns[key]
        except Exception:
            pass
        return result

    # ── API pública de control ────────────────────────────────────────────────

    def set_file_level(self, level: int) -> None:
        """
        Establece el nivel de registro para el handler de fichero y persiste los cambios.

        Args:
            level (int): El nuevo nivel de registro.

        Returns:
            None

        Raises:
            None
        """
        self._file_handler.setLevel(level)
        self._persist()
        self.logger.info("[Logger] Nivel fichero -> %s", logging.getLevelName(level))

    def set_console_level(self, level: int, exact: bool = False) -> None:
        """
        Establece el nivel de registro de la consola y persiste la configuración.

        Args:
            level (int): El nuevo nivel de registro.
            exact (bool): Si True, solo se mostrarán mensajes con el nivel exacto. Por defecto es False.

        Returns:
            None

        Raises:
            None
        """
        self._console_handler.filters = [
            f for f in self._console_handler.filters
            if not isinstance(f, _ExactLevelFilter)
        ]
        self._console_handler.setLevel(level)
        self._console_exact = exact
        if exact:
            self._console_handler.addFilter(_ExactLevelFilter(level))
        self._persist()
        self.logger.info(
            "[Logger] Nivel consola -> %s%s",
            logging.getLevelName(level),
            " (exacto)" if exact else "",
        )

    def set_module_level(self, module: str, level: int) -> None:
        """
        Establece el nivel de registro para un módulo específico en el sistema de registro.

        Args:
            module (str): Nombre del módulo para el que se establece el nivel de registro.
            level (int): Nivel de registro que se asigna al módulo.

        Returns:
            None

        Raises:
            None
        """
        name = f"Dashboard.{module}" if module else "Dashboard"
        logging.getLogger(name).setLevel(level)
        self._persist()
        self.logger.debug(
            "[Logger] Modulo '%s' nivel -> %s", name, logging.getLevelName(level)
        )

    def force_rollover(self) -> None:
        """
        Fuerza la rotación inmediata del fichero de log.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._file_handler.doRollover()
        self.logger.info("[Logger] Rotacion manual forzada")

    def get_status(self) -> dict:
        """
        Devuelve el estado actual de los handlers y módulos con nivel explícito.

        Args:
            Ninguno

        Returns:
            dict: Diccionario con el estado de los handlers y módulos, incluyendo niveles de registro.

        Raises:
            Ninguno
        """
        modules = {}
        prefix = "Dashboard."
        for name, lgr in logging.Logger.manager.loggerDict.items():
            if not isinstance(lgr, logging.Logger):
                continue
            if name == "Dashboard":
                continue
            if name.startswith(prefix):
                short = name[len(prefix):]
                if lgr.level != logging.NOTSET:
                    modules[short] = lgr.level
        return {
            "file_level":     self._file_handler.level,
            "console_level":  self._console_handler.level,
            "console_exact":  self._console_exact,
            "console_active": self._console_handler in self.logger.handlers,
            "log_file":       str(self._log_file),
            "modules":        modules,
        }

    def get_active_modules(self) -> list:
        """
        Obtiene una lista de nombres cortos de todos los sub-loggers activos instanciados en el dashboard.

        Args:
            Ninguno

        Returns:
            list: Lista ordenada de nombres cortos de sub-loggers activos.

        Raises:
            Ninguno
        """
        prefix = "Dashboard."
        result = []
        for name, lgr in logging.Logger.manager.loggerDict.items():
            if not isinstance(lgr, logging.Logger):
                continue
            if name.startswith(prefix):
                result.append(name[len(prefix):])
        return sorted(result)

    def get_logger(self, name: str) -> logging.Logger:
        """
        Obtiene un logger con prefijo 'Dashboard.' para el módulo especificado.

        Args:
            name (str): Nombre del módulo (e.g., 'ui', 'services').

        Returns:
            logging.Logger: Logger configurado para el módulo.
        """
        return logging.getLogger(f'Dashboard.{name}')

    # ── Persistencia ──────────────────────────────────────────────────────────

    def _persist(self) -> None:
        """
        Guarda la configuración actual de logging en el archivo local_settings.py.

        Args: Ninguno

        Returns: None

        Raises: Exception - Si ocurre un error al persistir la configuración, se registra una advertencia.
        """
        try:
            from config.local_settings_io import update_params  # noqa: PLC0415

            # Recoger niveles de módulos con override explícito
            module_levels = {}
            prefix = "Dashboard."
            for name, lgr in logging.Logger.manager.loggerDict.items():
                if not isinstance(lgr, logging.Logger):
                    continue
                if name.startswith(prefix) and lgr.level != logging.NOTSET:
                    module_levels[name[len(prefix):]] = lgr.level

            update_params({
                "log_file_level":    self._file_handler.level,
                "log_console_level": self._console_handler.level,
                "log_console_exact": self._console_exact,
                "log_module_levels": module_levels,
            })
        except Exception as e:
            self.logger.warning("[Logger] No se pudo persistir config: %s", e)


# ── Singleton global ──────────────────────────────────────────────────────────

_dashboard_logger = None


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger para un módulo específico.

    Args:
        name (str): Nombre del módulo que solicita el logger.

    Returns:
        logging.Logger: Instancia de logger configurada para el módulo.

    Raises:
        None
    """
    global _dashboard_logger
    if _dashboard_logger is None:
        _dashboard_logger = DashboardLogger()
    return _dashboard_logger.get_logger(name)


def get_dashboard_logger() -> DashboardLogger:
    """
    Devuelve la instancia singleton de DashboardLogger para control en runtime.

    Args:
        Ninguno

    Returns:
        DashboardLogger: La instancia singleton de DashboardLogger.

    Raises:
        Ninguno
    """
    global _dashboard_logger
    if _dashboard_logger is None:
        _dashboard_logger = DashboardLogger()
    return _dashboard_logger


def log_startup_info():
    """
    Registra información de inicio del sistema en el registro de eventos.

    Args:
        Ninguno

    Returns:
        Ninguno

    Raises:
        Ninguno
    """
    logger = get_logger('startup')
    logger.info("Python: %s", sys.version)
    logger.info("Platform: %s", sys.platform)
    logger.info("CWD: %s", os.getcwd())
    logger.info("User: %s", os.getenv('USER', 'unknown'))
    logger.info("HOME: %s", os.getenv('HOME', 'unknown'))
    display = os.getenv('DISPLAY', 'not set')
    logger.info("DISPLAY: %s", display)
    if display == 'not set':
        logger.warning("DISPLAY no configurado - posible problema de GUI")
