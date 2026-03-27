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
    Se ejecuta en segundo plano independiente de la UI.

    Características:
    - Singleton: Solo una instancia en toda la aplicación
    - Thread-safe: Seguro para concurrencia
    - Daemon: Se cierra automáticamente con el programa
    - Independiente de UI: Funciona con o sin ventanas abiertas
    """

    _instance: Optional['FanAutoService'] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """
        Singleton thread-safe para única instancia del servicio.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance


    def __init__(self, fan_controller: FanController, system_monitor: SystemMonitor):
        """
        Inicializa singleton FanAutoService (solo primera vez).

        Args:
            fan_controller (FanController): Para calcular PWM.
            system_monitor (SystemMonitor): Para temperatura CPU.
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
        Inicia thread daemon para bucle auto-PWM.

        Args:
            Ninguno (usa self._fan_controller, self._system_monitor).
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
        """Detiene el servicio."""
        if not self._running:
            logger.debug("[FanAutoService] stop() ignorado — ya estaba parado")
            return
        self._running = False
        self._stop_evt.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[FanAutoService] Servicio detenido")

    def is_running(self) -> bool:
        """Verifica si el servicio está corriendo."""
        return self._running
    # ── Bucle ─────────────────────────────────────────────────────────────────

    def _run(self):
        """Bucle principal del servicio."""
        self._update_auto_mode()   # primera ejecución inmediata
        while not self._stop_evt.wait(timeout=self._update_interval):
            if not self._running:
                break
            try:
                self._update_auto_mode()
            except Exception as e:
                logger.error("[FanAutoService] Error en actualización automática: %s", e)

    def _update_auto_mode(self):
        """Actualiza el PWM si está en modo auto."""
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
        Configura intervalo de polling auto-PWM (mín 1s).

        Args:
            seconds (float): Segundos entre updates.
        """
        """Cambia el intervalo de actualización (mínimo 1.0s)."""
        self._update_interval = max(1.0, seconds)



    def get_status(self) -> dict:
        """
        Retorna estado para UI (running, interval, thread_alive).

        Returns:
            dict: Status dict del servicio.
        """
        return {
            'running':      self._running,
            'interval':     self._update_interval,
            'thread_alive': self._thread.is_alive() if self._thread else False,
        }

