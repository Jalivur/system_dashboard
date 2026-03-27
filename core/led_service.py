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
    Escribe led_state.json para controlar los LEDs via fase1.py.
    No tiene thread permanente — escritura directa al pulsar en la UI.
    """

    def __init__(self):
        """
        Constructor: carga estado desde led_state.json, inicializa lock.
        """
        self._lock    = threading.Lock()
        self._state   = self._load()
        self._running = True
        logger.info("[LedService] Iniciado. Modo actual: %s", self._state.get("mode", "auto"))

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Activa el servicio (habilita set_mode/set_color).
        """
        self._running = True
        logger.info("[LedService] Iniciado")

    def stop(self) -> None:
        """Apaga los LEDs y desactiva el servicio."""
        self._running = False
        self._save({"mode": "off", "r": 0, "g": 0, "b": 0})
        logger.info("[LedService] Detenido — LEDs apagados")
        
    def is_running(self) -> bool:
        """
        Estado del servicio.

        Returns:
            bool: True si activo.
        """
        return self._running

    # ── API pública ───────────────────────────────────────────────────────────

    def get_state(self) -> dict:
        """
        Lee estado actual thread-safe (modo/color).

        Returns:
            dict: {'mode': str, 'r': int, 'g': int, 'b': int}
        """
        with self._lock:
            return dict(self._state)

    def set_mode(self, mode: str, r: int = 0, g: int = 255, b: int = 0) -> bool:
        """
        Cambia modo LED y RGB, valida, guarda led_state.json atomically.

        Args:
            mode (str): 'auto'|'off'|'static'|... (LED_MODES)
            r, g, b (int): Colores 0-255 clamped.

        Returns:
            bool: True si guardado OK.
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
        Actualiza solo RGB manteniendo modo actual.

        Args:
            r, g, b (int): Colores 0-255 clamped.

        Returns:
            bool: True si guardado OK (via set_mode).
        """
        if not self._running:
            return False
        with self._lock:
            mode = self._state.get("mode", "static")
        return self.set_mode(mode, r, g, b)

    # ── Persistencia ──────────────────────────────────────────────────────────

    def _save(self, state: dict) -> bool:
        """
        Guarda estado atomically a data/led_state.json (.tmp → replace).

        Returns:
            bool: True si escrito OK.
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
        Carga led_state.json o retorna default.

        Returns:
            dict: Estado parseado o {'mode':'auto','r':0,'g':255,'b':0}
        """
        try:
            if _LED_FILE.exists():
                with open(_LED_FILE) as f:
                    return json.load(f)
        except Exception:
            pass
        return {"mode": "auto", "r": 0, "g": 255, "b": 0}
