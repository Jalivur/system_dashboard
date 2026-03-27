# `ui.windows.service`

> **Ruta**: `ui/windows/service.py`

Ventana de monitor de servicios systemd

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

Ventana de monitor de servicios

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

Configura la ventana, variables de estado y lanza la creación de la interfaz.

#### `_create_ui(self)`

Crea todos los componentes de la interfaz de usuario de la ventana.

Incluye: header, barra de estadísticas, controles, encabezados de columnas,
contenedor con scroll y frame inferior con botón de refresco manual.

#### `_create_controls(self, parent)`

Crea los controles de búsqueda y filtrado en la parte superior.

Args:
    parent: Frame contenedor para los controles.

Incluye entrada de búsqueda con debounce y botones radio para filtrar por estado (todos, activos, inactivos, fallidos).

#### `_create_column_headers(self, parent)`

Crea la fila de encabezados de columnas de la tabla de servicios.

Args:
    parent: Frame contenedor para los headers.

Columnas: Servicio (ordenable), Estado, Autostart, Acciones.

#### `_on_sort_change(self, column: str)`

Maneja el cambio de ordenación por columna.

Args:
    column (str): Columna por la que ordenar ('name' o 'state').

Pausa actualizaciones automáticas temporalmente, alterna orden en el monitor y refresca la UI.

#### `_on_filter_change(self)`

Aplica el nuevo filtro de estado seleccionado (todos, activos, inactivos, fallidos).

Pausa actualizaciones temporales y refresca la vista filtrada.

#### `_on_search_change(self)`

Maneja los cambios en la entrada de búsqueda del usuario.

Implementa debounce: cancela timers previos y programa _do_search en 500ms.
Pausa actualizaciones automáticas durante la búsqueda.

#### `_do_search(self)`

Ejecuta la búsqueda real tras el período de debounce.

Refresca la UI con resultados filtrados y reanuda actualizaciones en 3s.

#### `_resume_updates(self)`

Reanuda las actualizaciones automáticas periódicas.

Se llama automáticamente tras pausas por sort/filter/search.

#### `_force_update(self)`

Realiza un refresco manual inmediato de todos los datos y UI.

Desactiva pausa de updates y llama a _update_now.

#### `_update(self)`

Bucle de actualización — winfo_exists siempre primero.

#### `_update_now(self)`

Refresco inmediato y completo de la interfaz con datos actuales.

Actualiza stats, aplica search/filter, crea filas de servicios (máx 30).

#### `_create_service_row(self, service: dict, row: int)`

Crea una fila completa en la tabla para un servicio específico.

Args:
    service (dict): Datos del servicio {name, active, enabled}.
    row (int): Índice de fila para alternar colores de fondo.

Incluye iconos de estado, botones de acción contextuales según estado.

#### `_start_service(self, service: dict)`

Inicia un servicio inactivo con diálogo de confirmación.

Args:
    service (dict): Información del servicio a iniciar.

Llama ServiceMonitor.start_service y refresca UI si éxito.

#### `_stop_service(self, service: dict)`

Detiene un servicio activo con advertencia de confirmación.

Args:
    service (dict): Información del servicio a detener.

Llama ServiceMonitor.stop_service y refresca UI si éxito.

#### `_restart_service(self, service: dict)`

Reinicia un servicio (activo o inactivo) con confirmación.

Args:
    service (dict): Información del servicio a reiniciar.

Llama ServiceMonitor.restart_service y refresca UI si éxito.

#### `_view_logs(self, service: dict)`

Abre una ventana modal con los últimos 30 logs del servicio.

Args:
    service (dict): Información del servicio cuyos logs mostrar.

Crea ventana con textbox de solo lectura y botón cerrar.

#### `_enable_service(self, service: dict)`

Habilita el autostart del servicio al boot con confirmación detallada.

Args:
    service (dict): Información del servicio a habilitar.

Llama ServiceMonitor.enable_service y refresca UI si éxito.

#### `_disable_service(self, service: dict)`

Deshabilita el autostart del servicio al boot con confirmación.

Args:
    service (dict): Información del servicio a deshabilitar.

Llama ServiceMonitor.disable_service y refresca UI si éxito.

</details>
