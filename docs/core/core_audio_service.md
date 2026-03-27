# `core.audio_service`

> **Ruta**: `core/audio_service.py`

Servicio de AudioService para control volumen/mute via amixer y play_test con aplay.
Operaciones síncronas, sin threads. Compatible Raspberry Pi OS.

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

Servicio de control de audio via amixer/aplay.
No usa thread daemon — las operaciones son síncronas y puntuales.
Cero imports de tkinter/ctk.

### Métodos públicos

#### `get_volume(self, control: str = DEFAULT_CONTROL) -> int`

Devuelve el volumen actual (0-100). -1 si error.

#### `set_volume(self, value: int, control: str = DEFAULT_CONTROL) -> bool`

Establece volumen 0-100. Devuelve True si éxito.

#### `is_muted(self, control: str = DEFAULT_CONTROL) -> bool`

Devuelve True si el canal está muteado.

#### `set_mute(self, muted: bool, control: str = DEFAULT_CONTROL) -> bool`

Mutea o desmutea el canal. Devuelve True si éxito.

#### `toggle_mute(self, control: str = DEFAULT_CONTROL) -> bool`

Invierte el estado mute. Devuelve el nuevo estado (True=muteado).

#### `play_test(self, wav_path: str | None = None) -> None`

Lanza aplay en background. Si wav_path es None usa Front_Center.wav.

#### `get_controls(self) -> list[str]`

Devuelve lista de controles amixer disponibles.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa AudioService (no requiere parámetros).

</details>
