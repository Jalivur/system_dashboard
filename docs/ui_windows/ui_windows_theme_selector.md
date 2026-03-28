# `ui.windows.theme_selector`

> **Ruta**: `ui/windows/theme_selector.py`

> **Cobertura de documentación**: 🟢 100% (8/8)

Ventana de selección de temas

---

## Tabla de contenidos

**Clase [`ThemeSelector`](#clase-themeselector)**

---

## Dependencias internas

- `config.settings`
- `config.themes`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

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

Ventana emergente para seleccionar temas de la aplicación.

Args:
    parent: Widget padre CTkToplevel del dashboard.

Raises:
    None

Returns:
    None

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

Returns:
    None

Raises:
    None

#### `_create_ui(self)`

Crea la interfaz de usuario del selector de temas.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_theme_cards(self, parent)`

Crea las tarjetas de cada tema disponible en la aplicación.

Args:
    parent: El elemento padre donde se crearán las tarjetas de temas.

Returns:
    None

Raises:
    None

#### `_create_bottom_buttons(self, parent)`

Crea los botones inferiores de la interfaz de selección de temas.

Args:
    parent: El elemento padre donde se crearán los botones.

Returns:
    None

Raises:
    None

#### `_on_theme_change(self)`

Actualiza la configuración del tema seleccionado.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_apply_theme(self)`

Aplica el tema seleccionado y reinicia la aplicación si es diferente al actual.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
