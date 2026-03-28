# `ui.windows.update`

> **Ruta**: `ui/windows/update.py`

> **Cobertura de documentación**: 🟢 100% (9/9)

Módulo para la ventana de control y gestión de actualizaciones del sistema en el dashboard.

Contiene:
- Clase UpdatesWindow: Interfaz gráfica para monitorear y ejecutar actualizaciones.
- Integración con monitor de actualizaciones y scripts del sistema.

---

## Tabla de contenidos

**Clase [`UpdatesWindow`](#clase-updateswindow)**

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `ui.widgets.dialogs`
- `utils`
- `utils.logger`

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

Ventana emergente para gestionar y visualizar actualizaciones del sistema.

Args:
    parent: Widget padre que crea esta ventana.
    update_monitor: Monitor de actualizaciones para obtener el estado.

Raises:
    Ninguna excepción específica.

Returns:
    Ningún valor de retorno.

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

Returns:
    None

Raises:
    None

#### `_create_ui(self)`

Crea la interfaz de usuario principal de la ventana de actualizaciones.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_build_content(self, parent)`

Construye el contenido normal de la ventana de actualizaciones.

Args:
    parent: El elemento padre donde se construirá el contenido.

Returns:
    None

Raises:
    None

#### `_update(self)`

Actualiza periódicamente el estado de la ventana según el monitor de actualizaciones.

Muestra un banner si el monitor no está corriendo o reconstruye el contenido si está activo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_refresh_status(self, force = False)`

Actualiza el estado de la ventana de actualizaciones consultando el estado de actualizaciones.

Args:
    force (bool): Fuerza la comprobación de actualizaciones aunque no haya cambios.

Returns:
    None

Raises:
    None

#### `_poll_until_ready(self)`

Reintenta refrescar el estado de actualización cada 2 segundos mientras el resultado sea desconocido.

Args: Ninguno

Returns: Ninguno

Raises: Ninguna excepción específica

#### `_execute_update_script(self)`

Ejecuta el script de actualización en la terminal y refresca la interfaz al finalizar.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

</details>
