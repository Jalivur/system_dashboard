# `ui.widgets.dialogs`

> **Ruta**: `ui/widgets/dialogs.py`

Diálogos y ventanas modales personalizadas

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

Muestra un cuadro de mensaje personalizado

Args:
    parent: Ventana padre
    text: Texto del mensaje
    title: Título del diálogo

### `confirm_dialog(parent, text: str, title: str = 'Confirmar', on_confirm = None, on_cancel = None) -> None`

Muestra un diálogo de confirmación

Args:
    parent: Ventana padre
    text: Texto del mensaje
    title: Título del diálogo
    on_confirm: Callback al confirmar
    on_cancel: Callback al cancelar

### `terminal_dialog(parent, script_path, title = 'Consola de Sistema', on_close = None)`

Muestra un diálogo de terminal/consola para ejecutar scripts del sistema

Args:
    parent: Ventana padre
    script_path: Ruta al script bash a ejecutar
    title: Título del diálogo
    on_close: Callback opcional al cerrar
