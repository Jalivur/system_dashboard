# `core.audio_service`

> **Ruta**: `core/audio_service.py`

> **Cobertura de documentación**: 🟢 100% (9/9)

Servicio de AudioService para control volumen/mute via amixer y play_test con aplay.
Operaciones síncronas, sin threads. Compatible Raspberry Pi OS.

---

## Tabla de contenidos

**Clase [`AudioService`](#clase-audioservice)**
  - [`get_volume()`](#get_volumeself-control-str-default_control-int)
  - [`set_volume()`](#set_volumeself-value-int-control-str-default_control-bool)
  - [`is_muted()`](#is_mutedself-control-str-default_control-bool)
  - [`set_mute()`](#set_muteself-muted-bool-control-str-default_control-bool)
  - [`toggle_mute()`](#toggle_muteself-control-str-default_control-bool)
  - [`play_test()`](#play_testself-wav_path-str-none-none-none)
  - [`get_controls()`](#get_controlsself-liststr)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import subprocess
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `AudioService`

Servicio de control de audio que interactúa con amixer y aplay para gestionar el volumen del sistema.

    Args:
        control (str): Control de audio a utilizar, por defecto es "Master".

    Returns:
        int: Volumen actual como porcentaje (0-100) o -1 en caso de error.

    Raises:
        subprocess.TimeoutExpired: Si la operación tarda más de 3 segundos.
        subprocess.CalledProcessError: Si el comando amixer falla.

### Métodos públicos

#### `get_volume(self, control: str = DEFAULT_CONTROL) -> int`

Devuelve el volumen actual como porcentaje.

Args:
    control (str): Control de volumen a utilizar, por defecto es DEFAULT_CONTROL.

Returns:
    int: Volumen actual como porcentaje (0-100) o -1 en caso de error.

Raises:
    Exception: Si ocurre un error al obtener el volumen.

#### `set_volume(self, value: int, control: str = DEFAULT_CONTROL) -> bool`

Establece el volumen de audio en un valor específico entre 0 y 100.

Args:
    value (int): El valor de volumen a establecer.
    control (str): El control de volumen a utilizar (por defecto DEFAULT_CONTROL).

Returns:
    bool: True si el volumen se estableció correctamente, False en caso de error.

Raises:
    Exception: Si ocurre un error al intentar establecer el volumen.

#### `is_muted(self, control: str = DEFAULT_CONTROL) -> bool`

Determina si el canal de audio especificado está muteado.

Args:
    control (str): Nombre del control de audio a verificar, por defecto es el control predeterminado.

Returns:
    bool: True si el canal está muteado, False en caso contrario.

Raises:
    Exception: Si ocurre un error al intentar obtener el estado del volumen.

#### `set_mute(self, muted: bool, control: str = DEFAULT_CONTROL) -> bool`

Establece el estado de silencio del canal de audio.

Args:
    muted (bool): Indica si el canal debe ser muteado o no.
    control (str): Control del canal de audio (por defecto DEFAULT_CONTROL).

Returns:
    bool: True si la operación es exitosa, False en caso de error.

Raises:
    Exception: Si ocurre un error durante la ejecución de la operación.

#### `toggle_mute(self, control: str = DEFAULT_CONTROL) -> bool`

Invierte el estado de mute del control de audio especificado.

Args:
    control (str): Control de audio a modificar, por defecto es DEFAULT_CONTROL.

Returns:
    bool: El nuevo estado de mute, True si está muteado, False en caso contrario.

Raises:
    None

#### `play_test(self, wav_path: str | None = None) -> None`

Reproduce un archivo de audio de prueba en segundo plano.

Args:
    wav_path (str | None): Ruta del archivo de audio, si es None se utiliza el archivo Front_Center.wav por defecto.

Returns:
    None

Raises:
    Exception: Si ocurre un error durante la reproducción del archivo de audio.

#### `get_controls(self) -> list[str]`

Recupera una lista de controles amixer disponibles.

Args:
    No aplica, método sin parámetros.

Returns:
    Una lista de strings con los controles disponibles.

Raises:
    Excepción general en caso de error, retornando un control predeterminado.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el servicio de audio.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
