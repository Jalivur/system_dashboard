"""
Sistema central de Event Bus thread-safe para comunicación between servicios y UI.

Previene acceso directo a Tkinter desde threads secundarios.
Los servicios publican eventos, la UI se suscribe y actualiza widgets en el thread principal.
"""
import queue
import threading
from typing import Callable, Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


class EventBus:
    """
    Bus de eventos thread-safe singleton.
    
    Uso:
        bus = EventBus()
        
        # Publicar evento desde thread secundario
        bus.publish("system.cpu_changed", {"cpu": 45.2})
        
        # Suscribirse en thread principal
        bus.subscribe("system.cpu_changed", callback)
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """
        Singleton thread-safe. Crea instancia única si no existe.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    
    def __init__(self):
        """
        Inicializa EventBus singleton (solo primera vez).
        Configura queue, subscribers, RLock.
        """
        if self._initialized:
            return
            
        self._initialized = True
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_queue = queue.Queue()
        self._lock = threading.RLock()
        logger.info("[EventBus] Inicializado")

    
    def subscribe(self, event_name: str, callback: Callable) -> None:
        """
        Suscribirse a un evento.
        
        Args:
            event_name: Nombre del evento (ej: "system.cpu_changed")
            callback: Función que se ejecutará: callback(event_data)
        """
        with self._lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            self._subscribers[event_name].append(callback)
            logger.debug("[EventBus] Suscriptor añadido: %s", event_name)
    
    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """Desuscribirse de un evento."""
        with self._lock:
            if event_name in self._subscribers:
                try:
                    self._subscribers[event_name].remove(callback)
                except ValueError:
                    pass
    
    def publish(self, event_name: str, data: Any = None) -> None:
        """
        Publicar un evento (thread-safe).
        
        Puede llamarse desde cualquier thread, incluidos threads secundarios.
        Los callbacks se ejecutarán mediante root.after() desde el thread principal.
        
        Args:
            event_name: Nombre del evento
            data: Datos del evento (dict recomendado)
        """
        self._event_queue.put((event_name, data))
    
    def process_events(self) -> None:
        """
        Procesar eventos pendientes. LLamar desde main_update_loop o desde root.after().
        
        Esto DEBE ejecutarse en el thread principal de Tkinter.
        """
        try:
            while True:
                try:
                    event_name, data = self._event_queue.get_nowait()
                    self._dispatch_event(event_name, data)
                except queue.Empty:
                    break
        except Exception as e:
            logger.error("[EventBus] Error procesando eventos: %s", e)
    
    def _dispatch_event(self, event_name: str, data: Any) -> None:
        """Ejecutar callbacks para un evento."""
        with self._lock:
            callbacks = self._subscribers.get(event_name, [])
            callbacks_copy = callbacks.copy()  # Copiar para evitar problemas durante iteración
        
        for callback in callbacks_copy:
            try:
                callback(data)
            except Exception as e:
                logger.error("[EventBus] Error en callback para '%s': %s", event_name, e)
    
    def clear(self) -> None:
        """Limpiar todos los suscriptores (útil para tests)."""
        with self._lock:
            self._subscribers.clear()
            while not self._event_queue.empty():
                try:
                    self._event_queue.get_nowait()
                except queue.Empty:
                    break


# Instancia global singleton
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Obtener la instancia global del event bus."""
    return _event_bus
