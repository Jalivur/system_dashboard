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
    Servicio que actualiza automáticamente el PWM en modo AUTO
    Se ejecuta en segundo plano independiente de la UI
    
    Características:
    - Singleton: Solo una instancia en toda la aplicación
    - Thread-safe: Seguro para concurrencia
    - Daemon: Se cierra automáticamente con el programa
    - Independiente de UI: Funciona con o sin ventanas abiertas
    """
    
    _instance: Optional['FanAutoService'] = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton: solo una instancia"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, fan_controller: FanController, 
                 system_monitor: SystemMonitor):
        """
        Inicializa el servicio (solo la primera vez)
        
        Args:
            fan_controller: Instancia del controlador de ventiladores
            system_monitor: Instancia del monitor del sistema
        """
        # Solo inicializar una vez (patrón singleton)
        if hasattr(self, '_initialized'):
            return
        
        self.fan_controller = fan_controller
        self.system_monitor = system_monitor
        self.file_manager = FileManager()
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._update_interval = 2.0  # segundos
        self._initialized = True
        self.start_cycle = True
    def start(self):
        """Inicia el servicio en segundo plano"""
        if self._running:
            logger.info("[FanAutoService] ya está corriendo")
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,  # Se cierra con el programa
            name="FanAutoService"
        )
        self._thread.start()
        logger.info("[FanAutoService] Servicio iniciado")
    
    def stop(self):
        """Detiene el servicio"""
        if not self._running:
            logger.warning("[FanAutoService] no está corriendo")
            return
        
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[FanAutoService] Servicio detenido")

    
    def _run(self):
        """Bucle principal del servicio (ejecuta en thread separado)"""
        while self._running:
            try:
                self._update_auto_mode()
            except Exception as e:
                logger.error(f"[FanAutoService] Error en actualización automática: {e}")
            
            # Dormir en intervalos pequeños para poder detener rápido
            for _ in range(int(self._update_interval * 10)):
                if not self._running:
                    break
                time.sleep(0.1)
    
    def _update_auto_mode(self):
        """Actualiza el PWM si está en modo auto"""
        
        try:
            state = self.file_manager.load_state()
        except Exception as e:
            logger.error(f"[FanAutoService] Error cargando estado: {e}")
            return
        
        # Solo actuar si está en modo auto
        if state.get("mode") != "auto":
            
            if self.start_cycle:
                logger.info("[FanAutoService] Modo no es auto, esperando para iniciar actualizaciones automáticas...")
                self.start_cycle = False
            return
        
        try:
            # Obtener temperatura actual
            stats = self.system_monitor.get_current_stats()
            temp = stats.get('temp', 50)
            
            # Calcular PWM según curva
            target_pwm = self.fan_controller.get_pwm_for_mode(
                mode="auto",
                temp=temp,
                manual_pwm=128  # No importa en auto
            )
            
            # Solo guardar si cambió (evitar writes innecesarios)
            current_pwm = state.get("target_pwm")
            if target_pwm != current_pwm:
                self.file_manager.write_state({
                    "mode": "auto",
                    "target_pwm": target_pwm
                })
        
        except Exception as e:
            logger.error(f"[FanAutoService] Error calculando o guardando PWM: {e}")
    
    def set_update_interval(self, seconds: float):
        """
        Cambia el intervalo de actualización
        
        Args:
            seconds: Segundos entre actualizaciones (mínimo 1.0)
        """
        self._update_interval = max(1.0, seconds)
    
    def is_running(self) -> bool:
        """
        Verifica si el servicio está corriendo
        
        Returns:
            True si está activo, False si no
        """
        return self._running
    
    def get_status(self) -> dict:
        """
        Obtiene el estado del servicio
        
        Returns:
            Diccionario con información del servicio
        """
        return {
            'running': self._running,
            'interval': self._update_interval,
            'thread_alive': self._thread.is_alive() if self._thread else False
        }
