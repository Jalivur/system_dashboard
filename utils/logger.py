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
    """Deja pasar únicamente registros cuyo nivel sea exactamente el indicado."""

    def __init__(self, level: int):
        super().__init__()
        self._level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self._level


# ── Logger central ────────────────────────────────────────────────────────────

class DashboardLogger:
    """Logger centralizado para el dashboard."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        """Configura el logger con rutas absolutas y rotación automática."""

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
        Lee log_file_level, log_console_level, log_console_exact y
        log_module_levels desde local_settings.py sin importar el módulo
        local_settings_io para evitar dependencias circulares en el arranque.
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
        """Cambia el nivel del handler de fichero y persiste."""
        self._file_handler.setLevel(level)
        self._persist()
        self.logger.info("[Logger] Nivel fichero -> %s", logging.getLevelName(level))

    def set_console_level(self, level: int, exact: bool = False) -> None:
        """Cambia el nivel del handler de consola y persiste."""
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
        Fija el nivel de un sub-logger concreto y persiste.
        level=NOTSET restablece la herencia del padre.
        """
        name = f"Dashboard.{module}" if module else "Dashboard"
        logging.getLogger(name).setLevel(level)
        self._persist()
        self.logger.debug(
            "[Logger] Modulo '%s' nivel -> %s", name, logging.getLevelName(level)
        )

    def force_rollover(self) -> None:
        """Fuerza la rotación del fichero de log inmediatamente."""
        self._file_handler.doRollover()
        self.logger.info("[Logger] Rotacion manual forzada")

    def get_status(self) -> dict:
        """
        Devuelve el estado actual de los handlers y módulos con nivel explícito.
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
        """Lista de nombres cortos de todos los sub-loggers instanciados."""
        prefix = "Dashboard."
        result = []
        for name, lgr in logging.Logger.manager.loggerDict.items():
            if not isinstance(lgr, logging.Logger):
                continue
            if name.startswith(prefix):
                result.append(name[len(prefix):])
        return sorted(result)

    def get_logger(self, name: str) -> logging.Logger:
        return logging.getLogger(f'Dashboard.{name}')

    # ── Persistencia ──────────────────────────────────────────────────────────

    def _persist(self) -> None:
        """
        Guarda la configuración de logging en local_settings.py via
        local_settings_io.update_params(). Importación local para evitar
        dependencia circular en el arranque del logger.
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
    Obtiene logger para un módulo.

    Uso:
        from utils.logger import get_logger
        logger = get_logger(__name__)
    """
    global _dashboard_logger
    if _dashboard_logger is None:
        _dashboard_logger = DashboardLogger()
    return _dashboard_logger.get_logger(name)


def get_dashboard_logger() -> DashboardLogger:
    """Devuelve la instancia singleton de DashboardLogger para control en runtime."""
    global _dashboard_logger
    if _dashboard_logger is None:
        _dashboard_logger = DashboardLogger()
    return _dashboard_logger


def log_startup_info():
    """Log información de inicio del sistema."""
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
