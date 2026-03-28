# `ui.windows.service`

> **Ruta**: `ui/windows/service.py`

> **Cobertura de documentación**: 🟢 100% (25/25)

Ventana de monitor de servicios systemd

---

## Tabla de contenidos

**Clase [`ServiceWindow`](#clase-servicewindow)**

---

## Dependencias internas

- `config.settings`
- `core.service_monitor`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.service_monitor import ServiceMonitor
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `ServiceWindow(ctk.CTkToplevel)`

Ventana emergente para monitorizar servicios del sistema.

Args:
    parent: Widget padre que contiene la ventana.
    service_monitor (ServiceMonitor): Instancia del monitor de servicios.

Configura la ventana y crea la interfaz de usuario para mostrar información de servicios.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_service_monitor` | `service_monitor` |
| `_search_var` | `ctk.StringVar(master=self)` |
| `_filter_var` | `ctk.StringVar(master=self, value='all')` |
| `_update_paused` | `False` |
| `_update_job` | `None` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, service_monitor: ServiceMonitor)`

Inicializa la ventana principal del monitor de servicios systemd.

Args:
    parent: Widget padre (ventana principal).
    service_monitor (ServiceMonitor): Instancia del monitor de servicios para obtener datos y ejecutar acciones.

Returns:
    None

Raises:
    None

#### `_create_ui(self)`

Crea todos los componentes de la interfaz de usuario de la ventana.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_controls(self, parent)`

Crea los controles de búsqueda y filtrado en la parte superior.

Args:
    parent: Frame contenedor para los controles.

Returns:
    None

Raises:
    None

#### `_create_column_headers(self, parent)`

Crea la fila de encabezados de columnas de la tabla de servicios.

Args:
    parent: Frame contenedor para los headers.

Returns:
    None

Raises:
    None

#### `_on_sort_change(self, column: str)`

Maneja el cambio de ordenación por columna.

Args:
    column (str): Columna por la que ordenar ('name' o 'state').

Raises:
    None

Returns:
    None

#### `_on_filter_change(self)`

Aplica el nuevo filtro de estado seleccionado y refresca la vista filtrada.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_search_change(self)`

Maneja los cambios en la entrada de búsqueda del usuario.

Args: None

Returns: None

Raises: None

#### `_do_search(self)`

Ejecuta la búsqueda real tras el período de debounce.

Refresca la UI con resultados filtrados y reanuda actualizaciones en 3s.

Args:
    None

Returns:
    None

Raises:
    None

#### `_resume_updates(self)`

Reanuda las actualizaciones automáticas periódicas.

Se llama automáticamente tras pausas por sort/filter/search.

Args:
    None

Returns:
    None

Raises:
    None

#### `_force_update(self)`

Forza una actualización inmediata de todos los datos y la interfaz de usuario.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_update(self)`

Actualiza el estado de la ventana de servicio en intervalos regulares.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update_now(self)`

Refresco inmediato y completo de la interfaz con datos actuales.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_service_row(self, service: dict, row: int)`

Crea una fila completa en la tabla para un servicio específico.

Args:
    service (dict): Datos del servicio {name, active, enabled}.
    row (int): Índice de fila para alternar colores de fondo.

Returns:
    None

Raises:
    None

#### `_start_service(self, service: dict)`

Inicia un servicio inactivo solicitando confirmación al usuario.

Args:
    service (dict): Información del servicio a iniciar.

Raises:
    Ninguna excepción específica.

Returns:
    Ningún valor de retorno específico.

#### `_stop_service(self, service: dict)`

Detiene un servicio activo después de confirmar con el usuario.

Args:
    service (dict): Información del servicio a detener, incluyendo su nombre.

Raises:
    None

Returns:
    None

#### `_restart_service(self, service: dict)`

Reinicia un servicio con confirmación previa.

Args:
    service (dict): Información del servicio a reiniciar.

Raises:
    None

Returns:
    None

#### `_view_logs(self, service: dict)`

Abre una ventana modal con los últimos 30 logs del servicio.

Args:
    service (dict): Información del servicio cuyos logs mostrar.

Returns:
    None

Raises:
    None

#### `_enable_service(self, service: dict)`

Habilita el autostart del servicio al boot con confirmación detallada.

Args:
    service (dict): Información del servicio a habilitar.

Raises:
    None

Returns:
    None

#### `_disable_service(self, service: dict)`

Deshabilita el autostart de un servicio al boot con confirmación previa.

Args:
    service (dict): Información del servicio a deshabilitar.

Raises:
    None

Returns:
    None

</details>
