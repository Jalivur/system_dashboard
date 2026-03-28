# `ui.windows.audio_window`

> **Ruta**: `ui/windows/audio_window.py`

> **Cobertura de documentación**: 🟢 100% (23/23)

Ventana de control de audio del dashboard de sistema.
Caracteristicas:

VU meter animado con zonas verde/amarillo/rojo
Control de volumen por canal (Master, PCM, etc.) con slider y botones rapidos
Mute/unmute con test de sonido
Interfaz responsive para DSI

---

## Tabla de contenidos

**Clase [`AudioWindow`](#clase-audiowindow)**

---

## Dependencias internas

- `config.settings`
- `core`
- `ui.styles`
- `utils.logger`

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

Ventana emergente para controlar el audio, incluyendo volumen, muteo, medidor de nivel de audio (VU meter) y accesos rápidos.

Args:
    parent (CTk): Ventana padre que crea esta ventana emergente.
    audio_service (AudioService): Servicio de audio asociado a esta ventana.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno.

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

Args:
    parent: La ventana padre que contiene esta ventana de control de audio.
    audio_service (AudioService): El servicio de audio asociado a esta ventana.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno

#### `_create_ui(self)`

Crea todos los elementos de la interfaz de usuario para el control de audio.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_build_vu_segments(self)`

Crea los segmentos iniciales del medidor VU, todos apagados.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_vu_tick(self)`

Actualiza la animación del medidor de volumen (VU meter) suavizando y dibujando el nivel actual.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_draw_vu(self, level: float)`

Actualiza la visualización del medidor de nivel de audio (VU meter) según el nivel de audio proporcionado.

Args:
    level (float): Nivel de audio actual, utilizado para determinar el color y cantidad de segmentos a iluminar.

Raises:
    Ninguna excepción es lanzada explícitamente en este método.

#### `_set_vu_from_vol(self, vol: int)`

Establece el objetivo del medidor de volumen (VU) en función del volumen dado.

Args:
    vol (int): El volumen en el rango 0-100.

Returns:
    None

Raises:
    None

#### `_run_async(self, fn, *args, on_done = None)`

Ejecuta una función de manera asíncrona en un hilo daemon.

Args:
    fn: La función a ejecutar de manera asíncrona.
    *args: Los argumentos a pasar a la función.

Raises:
    None

Returns:
    None

#### `_load_state(self)`

Carga asincrónicamente el estado actual del volumen y mute.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_apply_state(self, vol: int, muted: bool)`

Aplica el estado de volumen y mute a la interfaz de usuario.

Args:
    vol (int): El volumen a aplicar, en porcentaje.
    muted (bool): Indica si el audio está muteado.

Returns:
    None

Raises:
    None

#### `_on_slider(self, value)`

Actualiza el estado de la ventana de audio en respuesta a un cambio en el slider de volumen.

Args:
    value (int): El nuevo valor del slider de volumen.

Returns:
    None

Raises:
    None

#### `_set_quick(self, pct: int)`

Establece el volumen con botones rápidos.

Args:
    pct (int): Porcentaje de volumen.

Raises:
    Ninguna excepción relevante.

Returns:
    Ninguno

#### `_unlock(self)`

Desbloquea la interfaz de usuario después de una operación rápida.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_control_change(self, _value)`

Recarga el estado interno al detectar un cambio en el canal de control.

Args:
    _value: Nuevo valor del canal de control.

#### `_toggle_mute(self)`

Alterna el estado de mute del audio.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_apply_mute(self, muted: bool)`

Aplica el estado mute a la interfaz de usuario.

Args:
    muted (bool): Indica si el audio debe estar muteado o no.

Returns:
    None

Raises:
    None

#### `_play_test(self)`

Inicia una reproducción de prueba de audio en un hilo independiente.

La reproducción busca el archivo de prueba en varias rutas conocidas.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update_mute_ui(self)`

Actualiza la interfaz de usuario según el estado de silencio del audio.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_close(self)`

Maneja el cierre de la ventana de audio.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
