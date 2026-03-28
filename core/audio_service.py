"""
Servicio de AudioService para control volumen/mute via amixer y play_test con aplay.
Operaciones síncronas, sin threads. Compatible Raspberry Pi OS.
"""
# ── Imports ───────────────────────────────────────────────────────────────────
import subprocess

from utils.logger import get_logger

logger = get_logger(__name__)

"""
Servicio de AudioService para control volumen/mute via amixer y play_test con aplay.
Operaciones síncronas, sin threads. Compatible Raspberry Pi OS.
"""
# ── AudioService ──────────────────────────────────────────────────────────────

class AudioService:

    """
    Servicio de control de audio que interactúa con amixer y aplay para gestionar el volumen del sistema.

        Args:
            control (str): Control de audio a utilizar, por defecto es "Master".

        Returns:
            int: Volumen actual como porcentaje (0-100) o -1 en caso de error.

        Raises:
            subprocess.TimeoutExpired: Si la operación tarda más de 3 segundos.
            subprocess.CalledProcessError: Si el comando amixer falla.
    """

    def __init__(self):
        """
        Inicializa el servicio de audio.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """

        
    DEFAULT_CONTROL = "Master"


    # ── API pública ───────────────────────────────────────────────────────────

    def get_volume(self, control: str = DEFAULT_CONTROL) -> int:
        """
        Devuelve el volumen actual como porcentaje.

        Args:
            control (str): Control de volumen a utilizar, por defecto es DEFAULT_CONTROL.

        Returns:
            int: Volumen actual como porcentaje (0-100) o -1 en caso de error.

        Raises:
            Exception: Si ocurre un error al obtener el volumen.
        """
        try:
            out = subprocess.check_output(
                ["amixer", "sget", control],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=3
            )
            for line in out.splitlines():
                if "%" in line:
                    start = line.index("[") + 1
                    end   = line.index("%")
                    return int(line[start:end])
        except Exception as e:
            logger.warning("[AudioService] get_volume error: %s", e)
        return -1

    def set_volume(self, value: int, control: str = DEFAULT_CONTROL) -> bool:
        """
        Establece el volumen de audio en un valor específico entre 0 y 100.

        Args:
            value (int): El valor de volumen a establecer.
            control (str): El control de volumen a utilizar (por defecto DEFAULT_CONTROL).

        Returns:
            bool: True si el volumen se estableció correctamente, False en caso de error.

        Raises:
            Exception: Si ocurre un error al intentar establecer el volumen.
        """
        value = max(0, min(100, value))
        try:
            subprocess.run(
                ["amixer", "sset", control, f"{value}%"],
                check=True, capture_output=True,
            )
            return True
        except Exception as e:
            logger.warning("[AudioService] set_volume error: %s", e)
            return False

    def is_muted(self, control: str = DEFAULT_CONTROL) -> bool:
        """
        Determina si el canal de audio especificado está muteado.

        Args:
            control (str): Nombre del control de audio a verificar, por defecto es el control predeterminado.

        Returns:
            bool: True si el canal está muteado, False en caso contrario.

        Raises:
            Exception: Si ocurre un error al intentar obtener el estado del volumen.
        """
        try:
            out = subprocess.check_output(
                ["amixer", "sget", control],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=3
            )
            for line in out.splitlines():
                if "[off]" in line:
                    return True
        except Exception as e:
            logger.warning("[AudioService] is_muted error: %s", e)
        return False

    def set_mute(self, muted: bool, control: str = DEFAULT_CONTROL) -> bool:
        """
        Establece el estado de silencio del canal de audio.

        Args:
            muted (bool): Indica si el canal debe ser muteado o no.
            control (str): Control del canal de audio (por defecto DEFAULT_CONTROL).

        Returns:
            bool: True si la operación es exitosa, False en caso de error.

        Raises:
            Exception: Si ocurre un error durante la ejecución de la operación.
        """
        state = "mute" if muted else "unmute"
        try:
            subprocess.run(
                ["amixer", "sset", control, state],
                check=True, capture_output=True,
            )
            return True
        except Exception as e:
            logger.warning("[AudioService] set_mute error: %s", e)
            return False

    def toggle_mute(self, control: str = DEFAULT_CONTROL) -> bool:
        """
        Invierte el estado de mute del control de audio especificado.

        Args:
            control (str): Control de audio a modificar, por defecto es DEFAULT_CONTROL.

        Returns:
            bool: El nuevo estado de mute, True si está muteado, False en caso contrario.

        Raises:
            None
        """
        muted = self.is_muted(control)
        self.set_mute(not muted, control)
        return not muted

    def play_test(self, wav_path: str | None = None) -> None:
        """
        Reproduce un archivo de audio de prueba en segundo plano.

        Args:
            wav_path (str | None): Ruta del archivo de audio, si es None se utiliza el archivo Front_Center.wav por defecto.

        Returns:
            None

        Raises:
            Exception: Si ocurre un error durante la reproducción del archivo de audio.
        """
        path = wav_path or "/usr/share/sounds/alsa/Front_Center.wav"
        try:
            subprocess.Popen(
                ["aplay", "-q", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            logger.warning("[AudioService] play_test error: %s", e)

    def get_controls(self) -> list[str]:
        """
        Recupera una lista de controles amixer disponibles.

        Args:
            No aplica, método sin parámetros.

        Returns:
            Una lista de strings con los controles disponibles.

        Raises:
            Excepción general en caso de error, retornando un control predeterminado.
        """
        try:
            out = subprocess.check_output(
                ["amixer", "scontrols"],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=3
            )
            controls = [l.split("'")[1] for l in out.splitlines() if "'" in l]
            return controls if controls else [self.DEFAULT_CONTROL]
        except Exception as e:
            logger.warning("[AudioService] get_controls error: %s", e)
            return [self.DEFAULT_CONTROL]