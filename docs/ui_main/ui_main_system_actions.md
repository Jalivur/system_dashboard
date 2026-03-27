# `ui.main_system_actions`

> **Ruta**: `ui/main_system_actions.py`

Acciones de sistema del dashboard: salir y reiniciar.

Separado de MainWindow para mantener main_window.py enfocado en UI.
Las funciones reciben el root y los dialogos necesarios como parametros
— sin acoplamiento a MainWindow mas alla de lo imprescindible.

Uso en MainWindow:
    from ui.main_system_actions import exit_application, restart_application

    # En _create_ui footer:
    make_futuristic_button(..., command=lambda: exit_application(self.root, self._update_loop))
    make_futuristic_button(..., command=lambda: restart_application(self.root, self._update_loop))

## Imports

```python
import sys
import os
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_X, DSI_Y, SCRIPTS_DIR, Icons
from ui.styles import StyleManager, make_futuristic_button
from ui.widgets import confirm_dialog, terminal_dialog
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Funciones

### `exit_application(root, update_loop = None) -> None`

Muestra el dialogo de opciones de salida (salir / apagar sistema).

Args:
    root:        ventana Tk raiz del dashboard
    update_loop: instancia de UpdateLoop (se detiene antes de destroy)

### `restart_application(root, update_loop = None) -> None`

Muestra confirmacion y reinicia el proceso del dashboard via os.execv.

Args:
    root:        ventana Tk raiz del dashboard
    update_loop: instancia de UpdateLoop (se detiene antes de destroy)
