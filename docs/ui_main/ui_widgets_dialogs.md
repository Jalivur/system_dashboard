# `ui.widgets.dialogs`

> **Ruta**: `ui/widgets/dialogs.py`

> **Cobertura de documentación**: 🟢 100% (11/11)

Diálogos y ventanas modales personalizadas

---

## Tabla de contenidos

**Funciones**
- [`custom_msgbox()`](#funcion-custom_msgbox)
- [`confirm_dialog()`](#funcion-confirm_dialog)
- [`terminal_dialog()`](#funcion-terminal_dialog)

---

## Dependencias internas

- `config.settings`
- `core.event_bus`
- `ui.styles`

## Imports

```python
import customtkinter as ctk
from ui.styles import make_futuristic_button
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES
import subprocess
import threading
from core.event_bus import get_event_bus
```

## Funciones

### `custom_msgbox(parent, text: str, title: str = 'Info') -> None`

Muestra un cuadro de mensaje personalizado con título y texto.

Args:
    parent: Ventana padre del diálogo.
    text (str): Texto del mensaje a mostrar.
    title (str): Título del diálogo. Por defecto es 'Info'.

Returns:
    None

Raises:
    Ninguna excepción específica.

### `confirm_dialog(parent, text: str, title: str = 'Confirmar', on_confirm = None, on_cancel = None) -> None`

Muestra un diálogo de confirmación con un mensaje y botones para confirmar o cancelar.

Args:
    parent: Ventana padre del diálogo.
    text (str): Texto del mensaje a mostrar.
    title (str): Título del diálogo. Por defecto, 'Confirmar'.
    on_confirm: Función a llamar al confirmar. Por defecto, None.
    on_cancel: Función a llamar al cancelar. Por defecto, None.

Returns:
    None

Raises:
    None

### `terminal_dialog(parent, script_path, title = 'Consola de Sistema', on_close = None)`

Muestra un diálogo de terminal/consola para ejecutar scripts del sistema.

Args:
    parent: Ventana padre del diálogo.
    script_path: Ruta al script bash a ejecutar en la terminal.
    title: Título del diálogo de terminal (por defecto, 'Consola de Sistema').
    on_close: Función de llamada opcional cuando el diálogo se cierra.

Returns:
    None

Raises:
    Ninguna excepción específica.
