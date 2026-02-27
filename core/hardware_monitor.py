"""
Monitor de hardware del GPIO Board (Freenove FNK0100K).
Lee hardware_state.json que escribe fase1.py cada 5s.
Expone: temperatura del chasis, duty% real de cada fan.
"""
import json
import threading
import time
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

_HW_FILE = Path(__file__).resolve().parent.parent / "data" / "hardware_state.json"

# Antigüedad máxima del fichero antes de marcar datos como obsoletos (segundos)
_MAX_AGE_S = 30


class HardwareMonitor:
    """
    Lee hardware_state.json en background cada 6s.
    El fichero lo escribe fase1.py cada 5s.
    """

    def __init__(self):
        self._lock    = threading.Lock()
        self._running = False
        self._stop    = threading.Event()
        self._thread  = None
        self._data    = {
            "chassis_temp": None,
            "fan0_pct":     None,
            "fan1_pct":     None,
            "available":    False,   # False si el fichero no existe o está obsoleto
        }

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self):
        if self._running:
            return
        self._running = True
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="HardwareMonitor"
        )
        self._thread.start()
        logger.info("[HardwareMonitor] Iniciado")

    def stop(self):
        self._running = False
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("[HardwareMonitor] Detenido")

    # ── Bucle ─────────────────────────────────────────────────────────────────

    def _loop(self):
        while self._running:
            try:
                self._poll()
            except Exception as e:
                logger.error("[HardwareMonitor] Error: %s", e)
            self._stop.wait(timeout=6)
            if self._stop.is_set():
                break

    def _poll(self):
        if not _HW_FILE.exists():
            with self._lock:
                self._data["available"] = False
            return
        try:
            raw = json.loads(_HW_FILE.read_text())
            age = time.time() - raw.get("ts", 0)
            if age > _MAX_AGE_S:
                with self._lock:
                    self._data["available"] = False
                return
            with self._lock:
                self._data = {
                    "chassis_temp": raw.get("chassis_temp"),
                    "fan0_pct":     raw.get("fan0_pct"),
                    "fan1_pct":     raw.get("fan1_pct"),
                    "available":    True,
                }
        except Exception as e:
            logger.warning("[HardwareMonitor] Error leyendo hardware_state: %s", e)
            with self._lock:
                self._data["available"] = False

    # ── API pública ───────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Devuelve el estado del hardware desde caché."""
        with self._lock:
            return dict(self._data)

    def is_available(self) -> bool:
        """True si fase1.py está corriendo y ha escrito datos recientes."""
        with self._lock:
            return self._data.get("available", False)