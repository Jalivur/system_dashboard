"""
Servicio de alertas sonoras via los altavoces del FNK0100K.

Comportamiento:
  - warn.wav : suena cada WARN_REPEAT_S (5 min) MIENTRAS siga en zona de aviso
  - crit.wav : suena cada CRIT_REPEAT_S (30 s)  MIENTRAS siga en zona crítica
  - ok.wav   : suena UNA VEZ al recuperarse (salir de warn o de crit)
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
    "temp":     {"crit": 70, "warn": 60, "unit": "°C"},
    "cpu":      {"crit": 90, "warn": 75, "unit": "%"},
    "ram":      {"crit": 90, "warn": 75, "unit": "%"},
    "services": {"crit": 1,  "warn": 0,  "unit": "caídos"},
}

# ── Intervalos de repetición ──────────────────────────────────────────────────
WARN_REPEAT_S = 45   # warn.wav cada 5 minutos mientras siga en aviso
CRIT_REPEAT_S = 30       # crit.wav cada 30 segundos mientras siga crítico

# ── Sonidos ───────────────────────────────────────────────────────────────────
_SOUNDS_DIR = Path(__file__).resolve().parent.parent / "scripts" / "sounds"
_SOUND_WARN = str(_SOUNDS_DIR / "warn.wav")
_SOUND_CRIT = str(_SOUNDS_DIR / "crit.wav")
_SOUND_OK   = str(_SOUNDS_DIR / "ok.wav")


class _MetricState:
    """Estado de una métrica: en qué zona está y cuándo sonó por última vez."""
    __slots__ = ("zone", "last_played")

    def __init__(self):
        self.zone        = "ok"   # "ok" | "warn" | "crit"
        self.last_played = 0.0


class AudioAlertService:

    def __init__(self, system_monitor, service_monitor=None):
        self.system_monitor  = system_monitor
        self.service_monitor = service_monitor

        self._lock      = threading.Lock()
        self._running   = False
        self._stop      = threading.Event()
        self._thread    = None
        self._enabled   = True
        self._play_lock = threading.Lock()   # un solo aplay a la vez

        self._states: dict[str, _MetricState] = {
            key: _MetricState() for key in _THRESHOLDS
        }

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self):
        if self._running:
            return
        self._running = True
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="AudioAlertService"
        )
        self._thread.start()
        logger.info("[AudioAlertService] Iniciado")

    def stop(self):
        self._running = False
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("[AudioAlertService] Detenido")

    def set_enabled(self, enabled: bool):
        with self._lock:
            self._enabled = enabled
        logger.info("[AudioAlertService] %s", "Activado" if enabled else "Desactivado")

    def is_enabled(self) -> bool:
        with self._lock:
            return self._enabled

    def play_test(self):
        threading.Thread(target=self._play, args=(_SOUND_CRIT,), daemon=True).start()

    # ── Bucle ─────────────────────────────────────────────────────────────────

    def _loop(self):
        # Iterar más rápido que el intervalo más corto para no perder repeticiones
        loop_interval = min(CRIT_REPEAT_S, 10)
        while self._running:
            try:
                self._check()
            except Exception as e:
                logger.error("[AudioAlertService] Error: %s", e)
            self._stop.wait(timeout=loop_interval)
            if self._stop.is_set():
                break

    # ── Lógica principal ──────────────────────────────────────────────────────

    def _check(self):
        with self._lock:
            if not self._enabled:
                return

        now = time.time()

        try:
            stats = self.system_monitor.get_current_stats()
        except Exception:
            return

        values = {
            "temp": stats.get("temp", 0),
            "cpu":  stats.get("cpu",  0),
            "ram":  stats.get("ram",  0),
        }
        if self.service_monitor:
            try:
                values["services"] = self.service_monitor.get_stats().get("failed", 0)
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
            elif val >= thresh["warn"]:
                new_zone = "warn"
            else:
                new_zone = "ok"

            state.zone = new_zone

            # ── CRÍTICO: crit.wav cada CRIT_REPEAT_S mientras siga crítico ──
            if new_zone == "crit":
                if now - state.last_played >= CRIT_REPEAT_S:
                    logger.warning("[AudioAlertService] CRÍTICO %s=%.1f%s",
                                   key, val, thresh["unit"])
                    state.last_played = now
                    threading.Thread(
                        target=self._play, args=(_SOUND_CRIT,), daemon=True
                    ).start()

            # ── WARN: warn.wav cada WARN_REPEAT_S mientras siga en aviso ────
            elif new_zone == "warn":
                if now - state.last_played >= WARN_REPEAT_S:
                    logger.info("[AudioAlertService] AVISO %s=%.1f%s",
                                key, val, thresh["unit"])
                    state.last_played = now
                    threading.Thread(
                        target=self._play, args=(_SOUND_WARN,), daemon=True
                    ).start()

            # ── OK: ok.wav una sola vez al recuperarse ───────────────────────
            elif new_zone == "ok" and prev_zone in ("warn", "crit"):
                logger.info("[AudioAlertService] RECUPERADO %s=%.1f%s",
                            key, val, thresh["unit"])
                state.last_played = now
                threading.Thread(
                    target=self._play, args=(_SOUND_OK,), daemon=True
                ).start()

    # ── Reproducción ─────────────────────────────────────────────────────────

    def _play(self, sound_file: str):
        """Un solo aplay activo a la vez gracias a _play_lock."""
        with self._play_lock:
            if not os.path.exists(sound_file):
                logger.warning("[AudioAlertService] Archivo no encontrado: %s", sound_file)
                return
            for cmd in [["aplay", "-q", sound_file], ["paplay", sound_file]]:
                try:
                    r = subprocess.run(cmd, capture_output=True, timeout=10)
                    if r.returncode == 0:
                        return
                except FileNotFoundError:
                    continue
                except subprocess.TimeoutExpired:
                    return
            logger.error("[AudioAlertService] No se pudo reproducir: %s", sound_file)
