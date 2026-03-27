# `ui.windows.update`

> **Ruta**: `ui/windows/update.py`

Módulo para la ventana de control y gestión de actualizaciones del sistema en el dashboard.

Contiene:
- Clase UpdatesWindow: Interfaz gráfica para monitorear y ejecutar actualizaciones.
- Integración con monitor de actualizaciones y scripts del sistema.

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR, UPDATE_MS, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets.dialogs import terminal_dialog
from utils import SystemUtils
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `UpdatesWindow(ctk.CTkToplevel)`

Ventana de control de actualizaciones del sistema

### Atributos públicos

| Atributo | Valor inicial |
|----------|---------------|
| `system_utils` | `SystemUtils()` |

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_monitor` | `update_monitor` |
| `_polling` | `False` |
| `_banner_shown` | `False` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, update_monitor)`

Inicializa la ventana de actualizaciones del sistema.

Args:
    parent: Widget padre (CTkToplevel).
    update_monitor: Instancia del monitor de actualizaciones para consultar estado.

#### `_create_ui(self)`

Crea la interfaz de usuario principal de la ventana.

#### `_build_content(self, parent)`

Construye el contenido normal de la ventana.

#### `_update(self)`

Actualiza periódicamente el estado de la ventana según el monitor de actualizaciones.

Muestra banner si el monitor no está corriendo, o reconstruye contenido si está activo.

#### `_refresh_status(self, force = False)`

Consulta el estado de actualizaciones

#### `_poll_until_ready(self)`

Reintenta _refresh_status cada 2s mientras el resultado sea Unknown

#### `_execute_update_script(self)`

Lanza el script de terminal y refresca al terminar

</details>
