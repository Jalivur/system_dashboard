"""
Servicio en segundo plano para modo AUTO de ventiladores
"""
import threading
import time
from typing import Optional
from core.fan_controller import FanController
from core.system_monitor import SystemMonitor
from utils import FileManager
from utils.logger import get_logger

logger = get_logger(__name__)


class FanAutoService:
    """
    Servicio que actualiza automáticamente el PWM en modo AUTO.

    Args:
        fan_controller (FanController): Controlador del ventilador.
        system_monitor (SystemMonitor): Monitor del sistema.

    Returns:
        None

    Raises:
        None
    """

    _instance: Optional['FanAutoService'] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """
        Crea una instancia única del servicio de forma thread-safe.

        Args:
            *args: Argumentos posicionales.
            **kwargs: Argumentos clave-valor.

        Returns:
            La instancia única del servicio.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self, fan_controller: FanController, system_monitor: SystemMonitor):
        """
        Inicializa el servicio de control de ventilador de forma automática.

        Args:
            fan_controller (FanController): Controlador para calcular PWM.
            system_monitor (SystemMonitor): Monitor del sistema para obtener temperatura CPU.
        """
        if hasattr(self, '_initialized'):
            return

        self._fan_controller  = fan_controller
        self._system_monitor  = system_monitor
        self._file_manager    = FileManager()

        self._running          = False
        self._thread: Optional[threading.Thread] = None
        self._stop_evt = threading.Event()
        self._update_interval  = 2.0
        self._initialized      = True


    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self):
        """
        Inicia el servicio en segundo plano.

        Args:
            Ninguno, utiliza atributos de instancia para la configuración.

        Returns:
            Ninguno.

        Raises:
            Ninguno.
        """
        """Inicia el servicio en segundo plano."""
        if self._running:
            logger.info("[FanAutoService] ya está corriendo")
            return
        self._running = True
        self._stop_evt.clear()
        self._thread  = threading.Thread(
            target=self._run, daemon=True, name="FanAutoService"
        )
        self._thread.start()
        logger.info("[FanAutoService] Servicio iniciado")


    def stop(self):
        """
        Detiene el servicio de ajuste automático del ventilador.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        if not self._running:
            logger.debug("[FanAutoService] stop() ignorado — ya estaba parado")
            return
        self._running = False
        self._stop_evt.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[FanAutoService] Servicio detenido")

    def is_running(self) -> bool:
        """
        Indica si el servicio de ventilador automático está en ejecución.

        Args:
            None

        Returns:
            bool: True si el servicio está corriendo, False de lo contrario.

        Raises:
            None
        """
        return self._running
    # ── Bucle ─────────────────────────────────────────────────────────────────

    def _run(self):
        """
        Ejecuta el bucle principal del servicio de ventilador automático.

        Args:
            None

        Returns:
            None

        Raises:
            Exception
        """
        self._update_auto_mode()   # primera ejecución inmediata
        while not self._stop_evt.wait(timeout=self._update_interval):
            if not self._running:
                break
            try:
                self._update_auto_mode()
            except Exception as e:
                logger.error("[FanAutoService] Error en actualización automática: %s", e)

    def _update_auto_mode(self):
        """
        Actualiza el modo automático del ventilador si está activado.

        Args:
            None

        Returns:
            None

        Raises:
            Exception: Si ocurre un error al cargar o guardar el estado o al obtener estadísticas del sistema.
        """
        try:
            state = self._file_manager.load_state()
        except Exception as e:
            logger.error("[FanAutoService] Error cargando estado: %s", e)
            return

        if state.get("mode") != "auto":
            return

        try:
            stats      = self._system_monitor.get_current_stats()
            temp       = stats.get('temp', 50)
            target_pwm = self._fan_controller.get_pwm_for_mode(mode="auto", temp=temp)

            if target_pwm != state.get("target_pwm"):
                self._file_manager.write_state({"mode": "auto", "target_pwm": target_pwm})
        except Exception as e:
            logger.error("[FanAutoService] Error calculando o guardando PWM: %s", e)

    # ── Info ──────────────────────────────────────────────────────────────────

    def set_update_interval(self, seconds: float):
        """
        Establece el intervalo de tiempo entre actualizaciones de polling auto-PWM.

        Args:
            seconds (float): Intervalo en segundos entre actualizaciones.

        Returns:
            None

        Raises:
            None
        """
        """Cambia el intervalo de actualización (mínimo 1.0s)."""
        self._update_interval = max(1.0, seconds)



    def get_status(self) -> dict:
        """
        Retorna el estado actual del servicio de ventilador.

        Args:
            None

        Returns:
            dict: Diccionario con el estado del servicio, incluyendo si está en ejecución, 
                  el intervalo de actualización y el estado del hilo.

        Raises:
            None
        """
        return {
            'running':      self._running,
            'interval':     self._update_interval,
            'thread_alive': self._thread.is_alive() if self._thread else False,
        }

