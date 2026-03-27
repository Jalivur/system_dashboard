# `ui.windows.process_window`

> **Ruta**: `ui/windows/process_window.py`

Ventana de monitor de procesos

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.process_monitor import ProcessMonitor
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `ProcessWindow(ctk.CTkToplevel)`

Ventana de monitor de procesos

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_process_monitor` | `process_monitor` |
| `_search_var` | `ctk.StringVar(master=self)` |
| `_filter_var` | `ctk.StringVar(master=self, value='all')` |
| `_update_paused` | `False` |
| `_update_job` | `None` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, process_monitor: ProcessMonitor)`

Inicializa la ventana de monitor de procesos.

Args:
    parent: Ventana padre (CTkToplevel).
    process_monitor (ProcessMonitor): Instancia del monitor de procesos para obtener datos en tiempo real.

#### `_create_ui(self)`

Crea la interfaz de usuario

#### `_create_controls(self, parent)`

Crea controles de búsqueda y filtros

#### `_create_column_headers(self, parent)`

Crea encabezados de columnas ordenables

#### `_on_sort_change(self, column: str)`

Cambia el orden de procesos

#### `_on_filter_change(self)`

Cambia el filtro de procesos

#### `_on_search_change(self)`

Callback cuando cambia la búsqueda — debounce 500 ms

#### `_do_search(self)`

Ejecuta la búsqueda

#### `_resume_updates(self)`

Reanuda las actualizaciones automáticas

#### `_render_processes(self)`

Actualiza stats y renderiza la lista de procesos (lógica compartida).

#### `_update_now(self)`

Actualiza inmediatamente sin programar siguiente

#### `_update(self)`

Bucle de actualización automática

#### `_create_process_row(self, proc: dict, row: int)`

Crea una fila para un proceso

#### `_kill_process(self, proc: dict)`

Mata un proceso con confirmación

</details>
