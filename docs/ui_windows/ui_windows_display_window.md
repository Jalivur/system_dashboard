# `ui.windows.display_window`

> **Ruta**: `ui/windows/display_window.py`

Ventana de control de brillo de la pantalla.
Hardware: Freenove FNK0100K — Raspberry Pi 5.

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger
from core.display_service import BRIGHTNESS_MIN, BRIGHTNESS_MAX
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `QUICK_LEVELS` | `[('' + Icons.MOON_NEW + ' 10%', 10), ('' + Icons.MOON_CRESCENT + ' 30%', 30), ('...` |

## Clase `DisplayWindow(ctk.CTkToplevel)`

Ventana de control de brillo de pantalla.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_display_service` | `display_service` |
| `_slider_var` | `ctk.IntVar(master=self, value=self._display_service.get_brightness())` |
| `_banner_shown` | `False` |
| `_inner` | `None` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, display_service)`

Inicializa la ventana de control de brillo de pantalla.

Args:
    parent: Ventana padre.
    display_service: Servicio de control de display.

#### `_create_ui(self)`

Crea la estructura principal de la interfaz de usuario de la ventana.

#### `_build_content(self, inner)`

Construye el contenido real de la ventana.

#### `_update(self)`

Actualiza la ventana periódicamente, mostrando banner si el servicio está detenido.

#### `_on_slider(self, value)`

Maneja cambios en el slider de brillo, aplicando el nuevo valor.

#### `_set_quick(self, value)`

Establece un nivel de brillo rápido predefinido.

Args:
    value (int): Nivel de brillo (0-100).

#### `_screen_on(self)`

Enciende la pantalla al 100% de brillo.

#### `_screen_off(self)`

Apaga la pantalla (brillo 0%).

#### `_toggle_dim(self)`

Activa o desactiva el modo de atenuado automático por inactividad.

#### `_refresh(self)`

Actualiza la etiqueta y slider con el brillo actual.

</details>
