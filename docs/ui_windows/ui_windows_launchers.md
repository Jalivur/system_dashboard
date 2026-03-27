# `ui.windows.launchers`

> **Ruta**: `ui/windows/launchers.py`

Módulo de ventana de lanzadores para System Dashboard.

Proporciona una interfaz gráfica para ejecutar scripts del sistema configurados
en `config.settings.LAUNCHERS`. Cada lanzador muestra confirmación antes de
ejecución y abre terminal integrada para monitoreo en tiempo real.

Dependencias:
- customtkinter
- config.settings
- ui.styles, ui.widgets
- utils.system_utils, utils.logger

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, LAUNCHERS, Icons
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import confirm_dialog, terminal_dialog
from utils.system_utils import SystemUtils
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `LaunchersWindow(ctk.CTkToplevel)`

Ventana de lanzadores de scripts del sistema

### Atributos públicos

| Atributo | Valor inicial |
|----------|---------------|
| `system_utils` | `SystemUtils()` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent)`

Inicializa la ventana de lanzadores.

Args:
    parent: Widget padre (ventana principal del dashboard).

Configura geometría, colores, título y crea la UI completa.

#### `_create_ui(self)`

Crea la interfaz de usuario

#### `_create_launcher_buttons(self, parent)`

Crea los botones de lanzadores en layout grid

#### `_run_script(self, script_path: str, label: str)`

Ejecuta un script usando la terminal integrada tras confirmar.

Args:
    script_path (str): Ruta absoluta al script ejecutable.
    label (str): Nombre descriptivo del lanzador para logging y UI.

</details>
