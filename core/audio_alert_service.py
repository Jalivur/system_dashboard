"""
Servicio de alertas sonoras via los altavoces del FNK0100K.

Comportamiento:
  - {metric}_warn.wav : cada WARN_REPEAT_S (5 min) mientras siga en aviso
  - {metric}_crit.wav : cada CRIT_REPEAT_S (30 s)  mientras siga crítico
  - {metric}_ok.wav   : una sola vez al recuperarse

Archivos generados por: scripts/generate_sounds.py
"""
import subprocess
import threading
import time
import os
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Umbrales ──────────────────────────────────────────────────────────────────
_THRESHOLDS = {
    "temp":     {"crit": 70, "warn": 60,   "unit": "°C"},
    "cpu":      {"crit": 90, "warn": 75,   "unit": "%"},
    "ram":      {"crit": 90, "warn": 75,   "unit": "%"},
    "services": {"crit": 1,  "warn": None, "unit": "caídos"},  # sin warn — solo 0 o caído
}

# ── Intervalos de repetición ──────────────────────────────────────────────────
WARN_REPEAT_S = 45 # cada 45 segundos mientras siga en aviso
CRIT_REPEAT_S = 30       # cada 30 segundos mientras siga crítico

# ── Sonidos ───────────────────────────────────────────────────────────────────
_SOUNDS_DIR = Path(__file__).resolve().parent.parent / "scripts" / "sounds"

def _sound(metric: str, level: str) -> str:
    """Devuelve la ruta del audio para una métrica y nivel dados."""
    return str(_SOUNDS_DIR / f"{metric}_{level}.wav")


class _MetricState:
    """
    Estado interno por métrica: zone ('ok'/'warn'/'crit'), last_played ts.
    """
    __slots__ = ("zone", "last_played")

    def __init__(self):
        """
        Inicializa zone 'ok', last_played 0.
        """
        self.zone        = "ok"
        self.last_played = 0.0



class AudioAlertService:
    """
    Servicio de alertas sonoras via los altavoces del FNK0100K.
    Reproduce archivos WAV cuando CPU, RAM, temperatura o servicios
    superan los umbrales configurados en _THRESHOLDS.
    Corre en thread daemon con patrón _stop_evt estándar.
    """
    
    def __init__(self, system_monitor, service_monitor=None):
        """
        Inicializa AudioAlertService.

        Args:
            system_monitor: Fuente de métricas CPU/RAM/TEMP.
            service_monitor (optional): Fuente servicios caídos.
        """
        self._system_monitor = system_monitor
        self._service_monitor = service_monitor

        self._lock      = threading.Lock()
        self._running   = False
        self._stop_evt      = threading.Event()
        self._thread    = None
        self._enabled   = True
        self._play_lock = threading.Lock()

        self._states: dict[str, _MetricState] = {
            key: _MetricState() for key in _THRESHOLDS
        }


    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self):
        """
        Inicia thread daemon _loop para polling alertas sonoras.
        """
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="AudioAlertService"
        )
        self._thread.start()
        logger.info("[AudioAlertService] Iniciado")


    def stop(self):
        """
        Detiene thread limpiamente (join 5s timeout).
        """
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("[AudioAlertService] Detenido")

    
    def is_running(self) -> bool:
        """
        Estado activo del servicio.
        Returns:
            bool
        """
        return self._running


    def set_enabled(self, enabled: bool):
        """
        Activa/desactiva alertas sonoras (thread-safe).

        Args:
            enabled (bool): True para habilitar sonidos.
        """
        with self._lock:
            self._enabled = enabled
        logger.info("[AudioAlertService] %s", "Activado" if enabled else "Desactivado")


    def is_enabled(self) -> bool:
        """
        Estado habilitado sonidos (thread-safe).
        Returns:
            bool
        """
        with self._lock:
            return self._enabled


    def play_test(self):
        """
        Test: Reproduce temp_crit.wav async thread.
        """
        threading.Thread(
            target=self._play, args=(_sound("temp", "crit"),), daemon=True, name="AudioAlert-PlayWav"
        ).start()


    # ── Bucle ─────────────────────────────────────────────────────────────────

    def _loop(self):
        """
        Bucle polling thread daemon: _check cada min(CRIT_REPEAT_S,10)s.
        """
        loop_interval = min(CRIT_REPEAT_S, 10)
        while self._running:
            try:
                self._check()
            except Exception as e:
                logger.error("[AudioAlertService] Error: %s", e)
            self._stop_evt.wait(timeout=loop_interval)
            if self._stop_evt.is_set():
                break


    # ── Lógica principal ──────────────────────────────────────────────────────

    def _check(self):
        """
        Evalúa métricas vs THRESHOLDS: crit/warn/ok zones, play WAV según repeat/edge.
        """
        with self._lock:

            if not self._enabled:
                return

        now = time.time()

        try:
            stats = self._system_monitor.get_current_stats()
        except Exception:
            return

        values = {
            "temp": stats.get("temp", 0),
            "cpu":  stats.get("cpu",  0),
            "ram":  stats.get("ram",  0),
        }
        if self._service_monitor:
            try:
                values["services"] = self._service_monitor.get_stats().get("failed", 0)
            except Exception:
                values["services"] = 0
        else:
            values["services"] = 0

        for key, val in values.items():
            thresh    = _THRESHOLDS[key]
            state     = self._states[key]
            prev_zone = state.zone

            # Zona actual
            if val >= thresh["crit"]:
                new_zone = "crit"
            elif thresh["warn"] is not None and val >= thresh["warn"]:
                new_zone = "warn"
            else:
                new_zone = "ok"

            state.zone = new_zone

            # ── CRÍTICO: {metric}_crit.wav cada CRIT_REPEAT_S ────────────────
            if new_zone == "crit":
                if now - state.last_played >= CRIT_REPEAT_S:
                    logger.warning("[AudioAlertService] CRÍTICO %s=%.1f%s",
                                   key, val, thresh["unit"])
                    state.last_played = now
                    threading.Thread(
                        target=self._play, args=(_sound(key, "crit"),), daemon=True,
                        name="AudioAlert-PlayWav"
                    ).start()

            # ── WARN: {metric}_warn.wav cada WARN_REPEAT_S ───────────────────
            elif new_zone == "warn":
                if now - state.last_played >= WARN_REPEAT_S:
                    logger.info("[AudioAlertService] AVISO %s=%.1f%s",
                                key, val, thresh["unit"])
                    state.last_played = now
                    threading.Thread(
                        target=self._play, args=(_sound(key, "warn"),), daemon=True,
                        name="AudioAlert-PlayWav"
                    ).start()

            # ── OK: {metric}_ok.wav una vez al recuperarse ───────────────────
            elif new_zone == "ok" and prev_zone in ("warn", "crit"):
                logger.info("[AudioAlertService] RECUPERADO %s=%.1f%s",
                            key, val, thresh["unit"])
                state.last_played = now
                threading.Thread(
                    target=self._play, args=(_sound(key, "ok"),), daemon=True,
                    name="AudioAlert-PlayWav"
                ).start()

    # ── Reproducción ─────────────────────────────────────────────────────────

    def _play(self, sound_file: str):
        """
        Reproduce WAV serial (lock), try aplay/paplay, timeout 15s.
        """

        with self._play_lock:
            if not os.path.exists(sound_file):
                logger.warning("[AudioAlertService] Archivo no encontrado: %s", sound_file)
                return
            for cmd in [["aplay", "-q", sound_file], ["paplay", sound_file]]:
                try:
                    r = subprocess.run(cmd, capture_output=True, timeout=15)
                    if r.returncode == 0:
                        return
                except FileNotFoundError:
                    continue
                except subprocess.TimeoutExpired:
                    return
            logger.error("[AudioAlertService] No se pudo reproducir: %s", sound_file)
