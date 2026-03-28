# `ui.windows.process_window`

> **Ruta**: `ui/windows/process_window.py`

> **Cobertura de documentación**: 🟢 100% (16/16)

Ventana de monitor de procesos

---

## Tabla de contenidos

**Clase [`ProcessWindow`](#clase-processwindow)**

---

## Dependencias internas

- `config.settings`
- `core.process_monitor`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

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

Ventana emergente para monitorizar procesos en tiempo real.

Args:
    parent: Ventana padre (CTkToplevel).
    process_monitor (ProcessMonitor): Instancia del monitor de procesos.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno.

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

Returns:
    None

Raises:
    None

#### `_create_ui(self)`

Crea la interfaz de usuario de la ventana de proceso.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_controls(self, parent)`

Crea los controles de búsqueda y filtros en la ventana.

Args:
    parent: El elemento padre donde se crearán los controles.

Returns:
    None

Raises:
    None

#### `_create_column_headers(self, parent)`

Crea los encabezados de columnas ordenables para la ventana de procesos.

Args:
    parent: El elemento padre donde se crearán los encabezados.

Returns:
    None

Raises:
    None

#### `_on_sort_change(self, column: str)`

Reordenar los procesos en la ventana según la columna especificada.

Args:
    column (str): La columna por la que ordenar los procesos.

#### `_on_filter_change(self)`

Actualiza el filtro de procesos cuando éste cambia.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_search_change(self)`

Establece un retardo para actualizar la búsqueda cuando el usuario ha dejado de escribir.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_do_search(self)`

Ejecuta la búsqueda y pausa temporalmente las actualizaciones.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_resume_updates(self)`

Reanuda las actualizaciones automáticas de la ventana de proceso.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_render_processes(self)`

Actualiza estadísticas y renderiza la lista de procesos.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update_now(self)`

Actualiza inmediatamente la ventana de procesos sin programar la siguiente actualización.

Args:
    None

Returns:
    None

Raises:
    None

#### `_update(self)`

Actualiza automáticamente la ventana de proceso.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_process_row(self, proc: dict, row: int)`

Crea una fila para mostrar información de un proceso en la ventana.

Args:
    proc (dict): Diccionario con información del proceso.
    row (int): Número de fila para aplicar estilo alternado.

Returns:
    None

Raises:
    None

#### `_kill_process(self, proc: dict)`

Mata un proceso después de confirmar con el usuario.

Args:
    proc (dict): Diccionario con información del proceso a matar, incluyendo 'pid', 'name' y 'cpu'.

Raises:
    None

Returns:
    None

</details>
