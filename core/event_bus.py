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
    Proporciona un mecanismo de publicación y suscripción de eventos de forma thread-safe.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """
        Crea y devuelve la instancia única de la clase EventBus.

        Args:
            None

        Returns:
            La instancia única de la clase EventBus.

        Raises:
            None
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    
    def __init__(self):
        """
        Inicializa el EventBus singleton la primera vez que se instancia.

        Args:
            None

        Returns:
            None

        Raises:
            None
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
        Suscribirse a un evento para recibir notificaciones cuando ocurra.

        Args:
            event_name (str): Nombre del evento.
            callback (Callable): Función que se ejecutará al ocurrir el evento.

        Returns:
            None

        Raises:
            None
        """
        with self._lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            self._subscribers[event_name].append(callback)
            logger.debug("[EventBus] Suscriptor añadido: %s", event_name)
    
    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """
        Elimina una función de callback previamente registrada para un evento específico.

        Args:
            event_name (str): Nombre del evento del que desuscribirse.
            callback (Callable): Función de callback a eliminar.

        Returns:
            None

        Raises:
            None
        """
        with self._lock:
            if event_name in self._subscribers:
                try:
                    self._subscribers[event_name].remove(callback)
                except ValueError:
                    pass
    
    def publish(self, event_name: str, data: Any = None) -> None:
        """
        Publica un evento de forma segura entre threads.

        Args:
            event_name (str): Nombre del evento a publicar.
            data (Any, opcional): Datos asociados al evento. Por defecto es None.

        Returns:
            None

        Raises:
            None
        """
        self._event_queue.put((event_name, data))
    
    def process_events(self) -> None:
        """
        Procesa eventos pendientes en la cola de eventos.

        Args:
            None

        Returns:
            None

        Raises:
            Exception: Si ocurre un error durante el procesamiento de eventos.
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
        """
        Ejecuta callbacks registrados para un evento específico con los datos proporcionados.

        Args:
            event_name (str): Nombre del evento a dispatchar.
            data (Any): Datos asociados al evento.

        Returns:
            None

        Raises:
            Exception: Si un callback lanza una excepción durante su ejecución.
        """
        with self._lock:
            callbacks = self._subscribers.get(event_name, [])
            callbacks_copy = callbacks.copy()  # Copiar para evitar problemas durante iteración
        
        for callback in callbacks_copy:
            try:
                callback(data)
            except Exception as e:
                logger.error("[EventBus] Error en callback para '%s': %s", event_name, e)
    
    def clear(self) -> None:
        """
        Elimina todos los suscriptores y eventos pendientes de procesamiento.

        Args:
            Ninguno.

        Returns:
            None

        Raises:
            Ninguna excepción.
        """
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
    """
    Obtiene la instancia global del event bus.

    Returns:
        La instancia global del event bus.
    """
    return _event_bus
