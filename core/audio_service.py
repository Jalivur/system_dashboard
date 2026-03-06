# ── Imports ───────────────────────────────────────────────────────────────────
import subprocess
from utils.logger import get_logger

logger = get_logger(__name__)


# ── AudioService ──────────────────────────────────────────────────────────────

class AudioService:
    """
    Servicio de control de audio via amixer/aplay.
    No usa thread daemon — las operaciones son síncronas y puntuales.
    Cero imports de tkinter/ctk.
    """

    DEFAULT_CONTROL = "Master"

    # ── API pública ───────────────────────────────────────────────────────────

    def get_volume(self, control: str = DEFAULT_CONTROL) -> int:
        """Devuelve el volumen actual (0-100). -1 si error."""
        try:
            out = subprocess.check_output(
                ["amixer", "sget", control],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            for line in out.splitlines():
                if "%" in line:
                    start = line.index("[") + 1
                    end   = line.index("%")
                    return int(line[start:end])
        except Exception as e:
            logger.warning(f"[AudioService] get_volume error: {e}")
        return -1

    def set_volume(self, value: int, control: str = DEFAULT_CONTROL) -> bool:
        """Establece volumen 0-100. Devuelve True si éxito."""
        value = max(0, min(100, value))
        try:
            subprocess.run(
                ["amixer", "sset", control, f"{value}%"],
                check=True, capture_output=True,
            )
            return True
        except Exception as e:
            logger.warning(f"[AudioService] set_volume error: {e}")
            return False

    def is_muted(self, control: str = DEFAULT_CONTROL) -> bool:
        """Devuelve True si el canal está muteado."""
        try:
            out = subprocess.check_output(
                ["amixer", "sget", control],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            for line in out.splitlines():
                if "[off]" in line:
                    return True
        except Exception as e:
            logger.warning(f"[AudioService] is_muted error: {e}")
        return False

    def set_mute(self, muted: bool, control: str = DEFAULT_CONTROL) -> bool:
        """Mutea o desmutea el canal. Devuelve True si éxito."""
        state = "mute" if muted else "unmute"
        try:
            subprocess.run(
                ["amixer", "sset", control, state],
                check=True, capture_output=True,
            )
            return True
        except Exception as e:
            logger.warning(f"[AudioService] set_mute error: {e}")
            return False

    def toggle_mute(self, control: str = DEFAULT_CONTROL) -> bool:
        """Invierte el estado mute. Devuelve el nuevo estado (True=muteado)."""
        muted = self.is_muted(control)
        self.set_mute(not muted, control)
        return not muted

    def play_test(self, wav_path: str | None = None) -> None:
        """Lanza aplay en background. Si wav_path es None usa Front_Center.wav."""
        path = wav_path or "/usr/share/sounds/alsa/Front_Center.wav"
        try:
            subprocess.Popen(
                ["aplay", "-q", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            logger.warning(f"[AudioService] play_test error: {e}")

    def get_controls(self) -> list[str]:
        """Devuelve lista de controles amixer disponibles."""
        try:
            out = subprocess.check_output(
                ["amixer", "scontrols"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            controls = [l.split("'")[1] for l in out.splitlines() if "'" in l]
            return controls if controls else [self.DEFAULT_CONTROL]
        except Exception as e:
            logger.warning(f"[AudioService] get_controls error: {e}")
            return [self.DEFAULT_CONTROL]