# `ui.windows.theme_selector`

> **Ruta**: `ui/windows/theme_selector.py`

Ventana de selección de temas

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from config.themes import get_available_themes, get_theme, save_selected_theme, load_selected_theme
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox, confirm_dialog
import sys
import os
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `ThemeSelector(ctk.CTkToplevel)`

Ventana de selección de temas

### Atributos públicos

| Atributo | Valor inicial |
|----------|---------------|
| `current_theme` | `load_selected_theme()` |
| `selected_theme_var` | `ctk.StringVar(master=self, value=self.current_theme)` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent)`

Inicializa la ventana selector de temas del dashboard.

Args:
    parent: Widget padre CTkToplevel del dashboard.

#### `_create_ui(self)`

Crea la interfaz de usuario

#### `_create_theme_cards(self, parent)`

Crea las tarjetas de cada tema

#### `_create_bottom_buttons(self, parent)`

Crea los botones inferiores

#### `_on_theme_change(self)`

Callback cuando se selecciona un tema

#### `_apply_theme(self)`

Aplica el tema seleccionado y reinicia la aplicación

</details>
