# `ui.windows.button_manager_window`

> **Ruta**: `ui/windows/button_manager_window.py`

Ventana de gestión de visibilidad de botones del menú principal.
Permite activar/desactivar qué botones aparecen en el dashboard.
Los cambios son inmediatos en la UI y se persisten con "Guardar predeterminado".

## Imports

```python
import customtkinter as ctk
import config.button_labels as BL
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import custom_msgbox
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `ButtonManagerWindow(ctk.CTkToplevel)`

Ventana para gestionar la visibilidad de botones del menú principal.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_registry` | `registry` |
| `_window_manager` | `window_manager` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, registry, window_manager)`

Args:
    parent:         ventana padre (root)
    registry:       ServiceRegistry (para leer/guardar config ui)
    window_manager: WindowManager activo en MainWindow

#### `_create_ui(self)`

Crea la interfaz completa de la ventana:
- Frame principal con header de ventana
- Contenedor desplazable con canvas y scrollbar
- Lista de filas con etiquetas y switches para cada botón del menú
- Panel inferior con botones de acción (Guardar predeterminado, Activar/Desactivar todos)

#### `_create_row(self, parent, key: str, label: str, enabled: bool)`

Crea una fila con el nombre del botón y su switch ON/OFF.

#### `_on_toggle(self, key: str)`

Aplica el cambio inmediatamente en la UI del menú principal.

#### `_enable_all(self)`

Activa todos los switches y aplica los cambios.

#### `_disable_all(self)`

Desactiva todos los switches y aplica los cambios.

#### `_save(self)`

Persiste el estado actual al JSON via _registry.save_config().

</details>
