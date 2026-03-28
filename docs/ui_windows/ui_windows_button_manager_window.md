# `ui.windows.button_manager_window`

> **Ruta**: `ui/windows/button_manager_window.py`

> **Cobertura de documentación**: 🟢 100% (8/8)

Ventana de gestión de visibilidad de botones del menú principal.
Permite activar/desactivar qué botones aparecen en el dashboard.
Los cambios son inmediatos en la UI y se persisten con "Guardar predeterminado".

---

## Tabla de contenidos

**Clase [`ButtonManagerWindow`](#clase-buttonmanagerwindow)**

---

## Dependencias internas

- `config.button_labels`
- `config.settings`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

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

Ventana emergente para gestionar la visibilidad de botones del menú principal.

Args:
    parent:         Ventana padre (root) de la aplicación.
    registry:       Registro de servicios para leer y guardar configuración de la interfaz de usuario.
    window_manager: Gestor de ventanas activo en la ventana principal.

Raises:
    Ninguna excepción específica.

Returns:
    Ningún valor de retorno.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_registry` | `registry` |
| `_window_manager` | `window_manager` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, registry, window_manager)`

Inicializa la ventana de gestión de botones.

Args:
    parent:         Ventana padre (root) que contiene esta ventana.
    registry:       Registro de servicios para leer y guardar configuración de la interfaz de usuario.
    window_manager: Gestor de ventanas activo en la ventana principal.

Raises:
    Ninguna excepción específica.

#### `_create_ui(self)`

Crea la interfaz completa de la ventana del gestor de botones.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_row(self, parent, key: str, label: str, enabled: bool)`

Crea una fila con el nombre del botón y su switch ON/OFF.

Args:
    parent: El elemento padre donde se creará la fila.
    key (str): La clave única para el botón.
    label (str): El texto que se mostrará como nombre del botón.
    enabled (bool): El estado inicial del switch.

Returns:
    None

Raises:
    None

#### `_on_toggle(self, key: str)`

Aplica el cambio de visibilidad inmediatamente en la UI del menú principal.

Args:
    key (str): La clave del elemento que se va a mostrar u ocultar.

Raises:
    None
Returns:
    None

#### `_enable_all(self)`

Activa todos los switches y aplica los cambios.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_disable_all(self)`

Desactiva todos los switches y oculta los elementos asociados en la ventana.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_save(self)`

Guarda el estado actual de la configuración de botones en un archivo JSON.

Args:
    None

Returns:
    None

Raises:
    None

</details>
