# `ui.windows.audio_window`

> **Ruta**: `ui/windows/audio_window.py`

Ventana de control de audio del dashboard de sistema.
Caracteristicas:

VU meter animado con zonas verde/amarillo/rojo
Control de volumen por canal (Master, PCM, etc.) con slider y botones rapidos
Mute/unmute con test de sonido
Interfaz responsive para DSI

## Imports

```python
import threading
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import make_window_header, make_futuristic_button
from core import AudioService
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `AudioWindow(ctk.CTkToplevel)`

Ventana de control de audio — volumen, mute, VU meter y accesos rápidos.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_svc` | `audio_service` |
| `_control` | `ctk.StringVar(master=self, value=AudioService.DEFAULT_CONTROL)` |
| `_vol_var` | `ctk.IntVar(master=self, value=50)` |
| `_muted` | `False` |
| `_busy` | `False` |
| `_vu_target` | `0` |
| `_vu_current` | `0.0` |
| `_vu_job` | `None` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, audio_service: AudioService)`

Inicializa la ventana de control de audio.

#### `_create_ui(self)`

Crea todos los elementos de la interfaz de usuario.

#### `_build_vu_segments(self)`

Dibuja los segmentos iniciales del VU meter (todos apagados).

#### `_vu_tick(self)`

Actualiza la animación del VU meter — suaviza y dibuja.

#### `_draw_vu(self, level: float)`

Dibuja los segmentos del VU meter según el nivel.

#### `_set_vu_from_vol(self, vol: int)`

Convierte volumen 0-100 a segmentos y actualiza el target del VU.

#### `_run_async(self, fn, *args, on_done = None)`

Ejecuta fn(*args) en un thread daemon. on_done se llama en el hilo UI.

#### `_load_state(self)`

Carga el estado actual del volumen y mute.

#### `_apply_state(self, vol: int, muted: bool)`

Aplica el estado de volumen y mute a la UI.

#### `_on_slider(self, value)`

Maneja cambio en el slider de volumen.

#### `_set_quick(self, pct: int)`

Establece volumen con botones rápidos.

#### `_unlock(self)`

Desbloquea la UI después de operación rápida.

#### `_on_control_change(self, _value)`

Recarga estado al cambiar canal de control.

#### `_toggle_mute(self)`

Alterna estado de mute.

#### `_apply_mute(self, muted: bool)`

Aplica estado mute a la UI.

#### `_play_test(self)`

Lanza aplay en thread — busca el wav en varias rutas conocidas.

#### `_update_mute_ui(self)`

Actualiza elementos UI según estado de mute.

#### `_on_close(self)`

Maneja cierre de la ventana.

</details>
