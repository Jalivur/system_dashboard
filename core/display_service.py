"""
Servicio de control de brillo de la pantalla.
Detecta automáticamente el método disponible:
  - 'sysfs'     : /sys/class/backlight/ (driver kernel estándar)
  - 'wlr-randr' : Wayland (Raspberry Pi OS Bookworm por defecto)
  - 'xrandr'    : X11
  - 'none'      : no disponible (ventana muestra aviso)

Hardware: Freenove FNK0100K (4.3" IPS DSI) — Raspberry Pi 5.
"""
import subprocess
import threading
import json
from pathlib import Path
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Configuración ──────────────────────────────────────────────────────────────

# Rutas posibles de backlight sysfs — se comprueba por orden
_BACKLIGHT_CANDIDATES = [
    Path("/sys/class/backlight/11-0045"),
    Path("/sys/class/backlight/rpi_backlight"),
    Path("/sys/class/backlight/backlight"),
]

# Nombre de la salida DSI en wlr-randr / xrandr
# Verificar con: wlr-randr  o  xrandr | grep connected
# Valores habituales en RPi 5: "DSI-1", "DSI-2"
DSI_OUTPUT = "DSI-2"

BRIGHTNESS_MIN = 10    # % mínimo (no apagar con slider)
BRIGHTNESS_MAX = 100   # % máximo
BRIGHTNESS_OFF = 0     # apagado completo

# Timeouts de inactividad
DIM_TIMEOUT_S = 120        # segundos hasta dim (20%)
OFF_TIMEOUT_S = 2400000    # segundos hasta apagado completo

_STATE_FILE = Path(__file__).resolve().parent.parent / "data" / "display_state.json"

# ── Detección automática ───────────────────────────────────────────────────────

def _find_backlight() -> Optional[Path]:
    for p in _BACKLIGHT_CANDIDATES:
        if (p / "brightness").exists():
            return p
    return None


def _detect_method() -> str:
    """Detecta el método disponible para controlar el brillo."""
    if _find_backlight():
        return 'sysfs'
    try:
        r = subprocess.run(['wlr-randr'], capture_output=True, timeout=3)
        if r.returncode == 0:
            return 'wlr-randr'
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    try:
        r = subprocess.run(['xrandr', '--version'], capture_output=True, timeout=3)
        if r.returncode == 0:
            return 'xrandr'
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return 'none'


# ── Servicio ───────────────────────────────────────────────────────────────────

class DisplayService:
    """
    Servicio de control de brillo.
    No tiene thread permanente — el dim/off usa threading.Timer igual que
    otros servicios ligeros del proyecto.
    """

    def __init__(self):
        self._method    = _detect_method()
        self._backlight = _find_backlight() if self._method == 'sysfs' else None
        self._lock      = threading.Lock()
        self._brightness: int = BRIGHTNESS_MAX
        self._dimmed    = False
        self._dim_timer: Optional[threading.Timer] = None
        self._running   = True

        logger.info("[DisplayService] Método detectado: %s", self._method)
        if self._method == 'none':
            logger.warning(
                "[DisplayService] No hay método de brillo disponible. "
                "Ejecuta el Paso 0 de GUIA_BRILLO_DSI.md para diagnosticar."
            )

        self._load_state()

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        self._running = True
        logger.info("[DisplayService] Iniciado")

    def stop(self) -> None:
        """Desactiva el servicio y cancela timers de dim."""
        self._running = False
        self._cancel_dim_timer()
        logger.info("[DisplayService] Detenido")

    # ── API pública ───────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """True si hay algún método de control de brillo disponible."""
        return self._method != 'none'

    def get_method(self) -> str:
        """Devuelve el método activo: 'sysfs', 'wlr-randr', 'xrandr' o 'none'."""
        return self._method

    def get_brightness(self) -> int:
        """Devuelve el brillo actual en porcentaje (0-100)."""
        return self._brightness

    def set_brightness(self, pct: int) -> bool:
        """
        Establece el brillo. pct en rango 0-100.
        Devuelve True si tuvo éxito.
        """
        if not self._running:
            logger.warning("[DisplayService] set_brightness() ignorado — servicio parado")
            return False
        pct = max(BRIGHTNESS_OFF, min(BRIGHTNESS_MAX, int(pct)))
        if not self.is_available():
            return False

        if self._method == 'sysfs':
            ok = self._set_sysfs(pct)
        elif self._method == 'wlr-randr':
            ok = self._set_wlr(pct)
        else:
            ok = self._set_xrandr(pct)

        if ok:
            with self._lock:
                self._brightness = pct
                self._dimmed = (pct < BRIGHTNESS_MIN)
            self._save_state()

        return ok

    def screen_off(self) -> bool:
        """Apaga la pantalla (brillo = 0)."""
        return self.set_brightness(BRIGHTNESS_OFF)

    def screen_on(self) -> bool:
        """Enciende la pantalla al último nivel guardado."""
        target = self._brightness if self._brightness >= BRIGHTNESS_MIN else BRIGHTNESS_MAX
        return self.set_brightness(target)

    # ── Backends de control ───────────────────────────────────────────────────

    def _set_sysfs(self, pct: int) -> bool:
        try:
            max_b = int((self._backlight / "max_brightness").read_text().strip())
            value = int(pct / 100 * max_b)
            (self._backlight / "brightness").write_text(str(value))
            logger.debug("[DisplayService] sysfs → %d%% (%d/%d)", pct, value, max_b)
            return True
        except PermissionError:
            logger.error(
                "[DisplayService] Sin permisos en sysfs. Configura udev:\n"
                "  echo 'SUBSYSTEM==\"backlight\", ACTION==\"add\", "
                "RUN+=\"/bin/chmod a+w /sys%%p/brightness\"'"
                " | sudo tee /etc/udev/rules.d/99-backlight.rules\n"
                "  sudo udevadm control --reload-rules && sudo udevadm trigger"
            )
            return False
        except Exception as e:
            logger.error("[DisplayService] Error sysfs: %s", e)
            return False

    def _set_wlr(self, pct: int) -> bool:
        try:
            value = round(pct / 100, 2)
            r = subprocess.run(
                ['wlr-randr', '--output', DSI_OUTPUT, '--brightness', str(value)],
                capture_output=True, timeout=5
            )
            if r.returncode == 0:
                logger.debug("[DisplayService] wlr-randr → %d%%", pct)
                return True
            logger.error("[DisplayService] wlr-randr error: %s", r.stderr.decode().strip())
            return False
        except Exception as e:
            logger.error("[DisplayService] Error wlr-randr: %s", e)
            return False

    def _set_xrandr(self, pct: int) -> bool:
        try:
            value = round(pct / 100, 2)
            r = subprocess.run(
                ['xrandr', '--output', DSI_OUTPUT, '--brightness', str(value)],
                capture_output=True, timeout=5
            )
            if r.returncode == 0:
                logger.debug("[DisplayService] xrandr → %d%%", pct)
                return True
            logger.error("[DisplayService] xrandr error: %s", r.stderr.decode().strip())
            return False
        except Exception as e:
            logger.error("[DisplayService] Error xrandr: %s", e)
            return False

    # ── Modo ahorro (dim por inactividad) ─────────────────────────────────────

    def notify_activity(self):
        """
        Llamar desde la UI en cada interacción del usuario.
        Cancela el timer, restaura brillo si estaba en dim, reinicia el timer.
        """
        if not self._running:
            return
        self._cancel_dim_timer()
        if self._dimmed:
            self.screen_on()
            with self._lock:
                self._dimmed = False
        self._start_dim_timer()

    def enable_dim_on_idle(self):
        """Activa el timer de dim. Llamar al arrancar."""
        if not self._running:
            return
        self._start_dim_timer()
        logger.info("[DisplayService] Dim automático activado (%ds→dim, %ds→off)",
                    DIM_TIMEOUT_S, OFF_TIMEOUT_S)

    def disable_dim_on_idle(self):
        """Desactiva el timer de dim."""
        self._cancel_dim_timer()

    def _start_dim_timer(self):
        self._cancel_dim_timer()
        t = threading.Timer(DIM_TIMEOUT_S, self._on_dim)
        t.daemon = True
        t.start()
        self._dim_timer = t

    def _cancel_dim_timer(self):
        if self._dim_timer and self._dim_timer.is_alive():
            self._dim_timer.cancel()
        self._dim_timer = None

    def _on_dim(self):
        """Baja el brillo al 20% y programa el apagado completo."""
        if not self._dimmed and self._running:
            logger.debug("[DisplayService] Dim por inactividad")
            with self._lock:
                self._dimmed = True
            self.set_brightness(20)
        if self._running:
            t = threading.Timer(OFF_TIMEOUT_S - DIM_TIMEOUT_S, self._on_off)
            t.daemon = True
            t.start()
            self._dim_timer = t

    def _on_off(self):
        if self._running:
            logger.debug("[DisplayService] Apagado por inactividad")
            self.screen_off()

    # ── Persistencia ──────────────────────────────────────────────────────────

    def _save_state(self):
        try:
            _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            _STATE_FILE.write_text(json.dumps({"brightness": self._brightness}))
        except Exception as e:
            logger.warning("[DisplayService] No se pudo guardar estado: %s", e)

    def _load_state(self):
        try:
            if _STATE_FILE.exists():
                data = json.loads(_STATE_FILE.read_text())
                saved = int(data.get("brightness", BRIGHTNESS_MAX))
                if saved > 0:
                    with self._lock:
                        self._brightness = saved
                    if self.is_available():
                        self.set_brightness(saved)
        except Exception as e:
            logger.warning("[DisplayService] No se pudo cargar estado: %s", e)
