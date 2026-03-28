"""
Servicio de control de LEDs RGB del GPIO Board (Freenove FNK0100K).
El dashboard escribe led_state.json que fase1.py lee y aplica via I2C.
"""
import json
import os
import threading
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

_LED_FILE = Path(__file__).resolve().parent.parent / "data" / "led_state.json"

# Modos disponibles (deben coincidir con apply_led_state en fase1.py)
LED_MODES = ["auto", "off", "static", "follow", "breathing", "rainbow"]

# Descripciones legibles para la UI
LED_MODE_LABELS = {
    "auto":      "Auto (temperatura)",
    "off":       "Apagado",
    "static":    "Color fijo",
    "follow":    "Secuencial",
    "breathing": "Respiración",
    "rainbow":   "Arcoíris",
}

class LedService:
    """
    Servicio para controlar los LEDs mediante archivo de estado.

    Args: Ninguno

    Returns: Ninguno

    Raises: Ninguno
    """

    def __init__(self):
        """
        Inicializa el servicio de LED, cargando el estado desde el archivo led_state.json y configurando el bloqueo de ejecución.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._lock    = threading.Lock()
        self._state   = self._load()
        self._running = True
        logger.info("[LedService] Iniciado. Modo actual: %s", self._state.get("mode", "auto"))

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Inicia el servicio de LED, habilitando el modo y el color.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._running = True
        logger.info("[LedService] Iniciado")

    def stop(self) -> None:
        """
        Detiene el servicio de LEDs, apagándolos y desactivando su funcionamiento.

        Args: 
            None

        Returns: 
            None

        Raises: 
            None
        """
        self._running = False
        self._save({"mode": "off", "r": 0, "g": 0, "b": 0})
        logger.info("[LedService] Detenido — LEDs apagados")
        
    def is_running(self) -> bool:
        """
        Indica si el servicio de LED está actualmente en ejecución.

        Returns:
            bool: True si el servicio está activo, False en caso contrario.
        """
        return self._running

    # ── API pública ───────────────────────────────────────────────────────────

    def get_state(self) -> dict:
        """
        Obtiene el estado actual del LED de manera segura para hilos.

        Args:
            Ninguno

        Returns:
            dict: Un diccionario con el modo y valores de color RGB actuales, en el formato {'mode': str, 'r': int, 'g': int, 'b': int}

        Raises:
            Ninguno
        """
        with self._lock:
            return dict(self._state)

    def set_mode(self, mode: str, r: int = 0, g: int = 255, b: int = 0) -> bool:
        """
        Cambia el modo del LED y los valores RGB, validándolos y guardando el estado en led_state.json de manera atómica.

        Args:
            mode (str): El modo del LED, puede ser 'auto', 'off', 'static', etc. (ver LED_MODES).
            r (int): El valor del rojo, entre 0 y 255. Por defecto es 0.
            g (int): El valor del verde, entre 0 y 255. Por defecto es 255.
            b (int): El valor del azul, entre 0 y 255. Por defecto es 0.

        Returns:
            bool: True si el estado se guardó correctamente.

        Raises:
            None
        """
        if not self._running:
            logger.warning("[LedService] set_mode() ignorado — servicio parado")
            return False
        if mode not in LED_MODES:
            logger.warning("[LedService] Modo desconocido: %s", mode)
            return False
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        new_state = {"mode": mode, "r": r, "g": g, "b": b}
        with self._lock:
            self._state = new_state
        ok = self._save(new_state)
        if ok:
            logger.info("[LedService] Modo → %s  RGB(%d,%d,%d)", mode, r, g, b)
        return ok

    def set_color(self, r: int, g: int, b: int) -> bool:
        """
        Establece el color del LED actualizando solo los componentes RGB.

        Args:
            r (int): Componente rojo del color (0-255).
            g (int): Componente verde del color (0-255).
            b (int): Componente azul del color (0-255).

        Returns:
            bool: True si el color se guardó correctamente.
        """
        if not self._running:
            return False
        with self._lock:
            mode = self._state.get("mode", "static")
        return self.set_mode(mode, r, g, b)

    # ── Persistencia ──────────────────────────────────────────────────────────

    def _save(self, state: dict) -> bool:
        """
        Guarda el estado del LED de manera atómica en un archivo JSON.

        Args:
            state (dict): El estado del LED a ser guardado.

        Returns:
            bool: True si el estado se guardó correctamente, False en caso de error.

        Raises:
            Exception: Si ocurre un error durante el proceso de guardado.
        """
        try:
            _LED_FILE.parent.mkdir(parents=True, exist_ok=True)
            tmp = str(_LED_FILE) + ".tmp"
            with open(tmp, "w") as f:
                json.dump(state, f)
            os.replace(tmp, str(_LED_FILE))
            return True
        except Exception as e:
            logger.error("[LedService] Error guardando led_state: %s", e)
            return False

    def _load(self) -> dict:
        """
        Carga el estado de la configuración de LED desde un archivo o retorna un estado por defecto.

        Args:
            Ninguno

        Returns:
            dict: Estado parseado del LED o un diccionario con valores por defecto {'mode':'auto','r':0,'g':255,'b':0}

        Raises:
            Ninguno
        """
        try:
            if _LED_FILE.exists():
                with open(_LED_FILE) as f:
                    return json.load(f)
        except Exception:
            pass
        return {"mode": "auto", "r": 0, "g": 255, "b": 0}
