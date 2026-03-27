# `ui.windows.log_config_window`

> **Ruta**: `ui/windows/log_config_window.py`

Ventana de configuración del sistema de logging en runtime.
Permite cambiar niveles de fichero y consola, controlar módulos
individualmente y forzar la rotación del log.

Diseño ligero para Wayland/labwc:
  - Handlers globales: dos CTkOptionMenu (uno por handler)
  - Módulos: tk.Listbox nativo (un solo widget X11) + CTkScrollbar + un CTkOptionMenu compartido

Ubicación: ui/windows/log_config_window.py

## Imports

```python
import logging
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets.dialogs import custom_msgbox
from utils.logger import get_logger, get_dashboard_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

<details>
<summary>Funciones privadas</summary>

### `_level_name(level: int) -> str`

Convierte un nivel numérico de logging en su nombre legible.

Args:
    level (int): Nivel numérico de logging (ej: logging.DEBUG).

Returns:
    str: Nombre del nivel (ej: "DEBUG") o el nombre por defecto si no está mapeado.

</details>

## Clase `LogConfigWindow(ctk.CTkToplevel)`

Ventana de control de niveles de logging en runtime.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_dl` | `get_dashboard_logger()` |
| `_file_level_var` | `ctk.StringVar(master=self, value=_level_name(status['file_level']))` |
| `_console_level_var` | `ctk.StringVar(master=self, value=_level_name(status['console_level']))` |
| `_console_exact_var` | `ctk.BooleanVar(master=self, value=status['console_exact'])` |
| `_console_active` | `status['console_active']` |
| `_module_level_var` | `ctk.StringVar(master=self, value=_HEREDAR)` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent)`

Inicializa la ventana de configuración de logging.

Configura posición, estado de handlers/módulos desde dashboard_logger,
y construye la interfaz de usuario.

Args:
    parent: Ventana padre (CTkToplevel).

#### `_create_ui(self)`

Crea la estructura principal de la UI con header y dos columnas (izq/der).

#### `_build_left(self, parent)`

Construye columna izquierda: selectores handlers, checkbox consola,
botones acción (rotar/reset) y path del log actual.

#### `_build_handler_row(self, parent, label: str, var, active: bool, command)`

Crea fila horizontal reusable para selector de nivel de handler.

Args:
    parent: Frame contenedor.
    label: Etiqueta (ej: "Fichero:").
    var: StringVar con nivel actual.
    active: Si está habilitado.
    command: Callback al cambiar.

#### `_on_file_level_change(self, value: str)`

Callback: cambia nivel de logging del handler de fichero.

#### `_on_console_level_change(self, value: str = None)`

Callback: cambia nivel/exactitud del handler de consola.

#### `_build_right(self, parent)`

Construye columna derecha: listbox módulos, scrollbar, selector nivel y botón aplicar.

#### `_reload_modules(self)`

Recarga la lista de módulos activos desde dashboard_logger y actualiza listbox.

#### `_on_listbox_select(self, _event)`

Callback selección en listbox: actualiza selector y status del módulo.

#### `_apply_module_level(self)`

Aplica nivel de log al módulo seleccionado y actualiza listbox/status.

#### `_force_rollover(self)`

Fuerza rotación manual del archivo de log y muestra confirmación.

#### `_reset_all_modules(self)`

Restablece todos los módulos a nivel HEREDAR y recarga listbox.

#### `_on_close(self)`

Maneja cierre de ventana: enfoca padre y destruye self.

</details>
