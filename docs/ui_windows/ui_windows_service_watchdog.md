# `ui.windows.service_watchdog`

> **Ruta**: `ui/windows/service_watchdog.py`

> **Cobertura de documentación**: 🟢 100% (22/22)

Ventana Service Watchdog - monitor críticos + config inline

---

## Tabla de contenidos

**Clase [`ServiceWatchdogWindow`](#clase-servicewatchdogwindow)**

---

## Dependencias internas

- `config.settings`
- `core.service_monitor`
- `core.service_watchdog`
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
from core.service_watchdog import ServiceWatchdog
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `ServiceWatchdogWindow(ctk.CTkToplevel)`

Ventana para monitoreo y configuración del watchdog de servicios systemd.

Args:
    parent: Ventana padre (CTk).
    service_monitor (ServiceMonitor): Instancia para queries de servicios y logs.
    watchdog (ServiceWatchdog): Instancia para configuración y estadísticas críticas.

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_service_monitor` | `service_monitor` |
| `_watchdog` | `watchdog` |
| `_search_var` | `ctk.StringVar(master=self)` |
| `_filter_var` | `ctk.StringVar(master=self, value='critical')` |
| `_critical_entry` | `ctk.StringVar(master=self)` |
| `_critical_list_label` | `None` |
| `_update_paused` | `False` |
| `_update_job` | `None` |
| `_umbral_debounce_id` | `None` |
| `_interval_debounce_id` | `None` |
| `_umbral_var` | `ctk.StringVar(master=self, value=str(_stats['threshold']))` |
| `_interval_var` | `ctk.StringVar(master=self, value=str(_stats['interval']))` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, service_monitor: ServiceMonitor, watchdog: ServiceWatchdog)`

Inicializa la ventana de monitoreo Service Watchdog.

Configura las dependencias, variables de estado y la interfaz de usuario.

Args:
    parent: Ventana padre (CTk).
    service_monitor (ServiceMonitor): Instancia para queries de servicios y logs.
    watchdog (ServiceWatchdog): Instancia para configuración y estadísticas críticas.

Returns:
    None

Raises:
    None

#### `_create_ui(self)`

Crea la interfaz de usuario principal de la ventana Service Watchdog.

    Args:
        Ninguno

    Returns:
        Ninguno

    Raises:
        Ninguno

#### `_create_controls(self, parent)`

Crea los controles interactivos superiores para filtrado y gestión de servicios.

Args:
    parent: Frame contenedor principal donde se crearán los controles.

#### `_create_column_headers(self, parent)`

Crea la fila de encabezados para la tabla scrollable de servicios.

Args:
    parent: Frame contenedor de headers.

Returns:
    None

Raises:
    None

#### `_debounce_umbral_update(self)`

Maneja el debounce para cambios en el campo de umbral de fallos críticos.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_umbral_change(self, val)`

Aplica cambios al umbral de fallos consecutivos críticos a partir de un valor introducido.

Args:
    val (str): Valor crudo del campo de entrada.

Raises:
    None

#### `_debounce_interval_update(self)`

Establece un debounce para cambios en el intervalo de monitoreo, 
programando una actualización diferida después de un período de inactividad.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_interval_change(self, val)`

Aplica cambios al intervalo de chequeo periódico del watchdog.

    Args:
        val (str): Valor del entry field.

    Raises:
        None

#### `_apply_config(self)`

Aplica la configuración actual de umbral e intervalo al ServiceWatchdog.

Args:
    None

Returns:
    None

Raises:
    ValueError: Si los valores de umbral o intervalo no son válidos.

Nota: Configura el umbral entre 1 y 10, e intervalo entre 30 y 300.

#### `_debounced_search(self)`

Implementa búsqueda en tiempo real con debounce para nombres de servicios.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_filter(self)`

Responde a cambios en el filtro de servicios.

Pausa las actualizaciones durante 1.5 segundos para evitar flicker durante la transición.

Args:
    None

Returns:
    None

Raises:
    None

#### `_resume_updates(self)`

Reanuda el ciclo de actualizaciones periódicas tras una pausa temporal.

Args: None

Returns: None

Raises: None

#### `_force_update(self)`

Fuerza la actualización inmediata de datos y la interfaz de usuario.

Despausa las actualizaciones si estaban detenidas y llama a _update_now directamente.
Este método es utilizado por el botón Refrescar.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_update(self)`

Actualiza periódicamente la interfaz de usuario del ServiceWatchdogWindow.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update_now(self)`

Actualiza inmediatamente estadísticas y tabla de servicios.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_do_restart(self, name)`

Inicia el reinicio seguro de un servicio con confirmación del usuario.

Args:
    name (str): Nombre exacto del servicio systemd.

Raises:
    None

Returns:
    None

#### `_show_logs(self, name)`

Muestra logs recientes del servicio en una ventana modal.

Args:
    name (str): Nombre del servicio.

Returns:
    None

Raises:
    None

#### `_add_critical(self)`

Añade un servicio a la lista de monitoreo crítico.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_save_criticals(self)`

Persiste la lista actual de servicios críticos en watchdog.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update_critical_label(self)`

Actualiza la etiqueta textual con la lista actual de servicios críticos.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
