# `ui.windows.overview`

> **Ruta**: `ui/windows/overview.py`

> **Cobertura de documentación**: 🟢 100% (10/10)

Ventana de resumen general del sistema.
Muestra todas las métricas críticas en un solo vistazo.
Pensada para usarse como pantalla de reposo en la DSI.

---

## Tabla de contenidos

**Clase [`OverviewWindow`](#clase-overviewwindow)**
  - [`destroy()`](#destroyself)

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `utils.logger`

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, CPU_WARN, CPU_CRIT, RAM_WARN, RAM_CRIT, TEMP_WARN, TEMP_CRIT, Icons
from ui.styles import StyleManager, make_window_header
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `OverviewWindow(ctk.CTkToplevel)`

Ventana de resumen que muestra métricas críticas del sistema en un vistazo.

Args:
    parent: Ventana padre.
    system_monitor: Monitor del sistema (CPU/RAM/temperatura).
    service_monitor: Monitor de servicios.
    pihole_monitor: Monitor de Pi-hole.
    network_monitor: Monitor de red.
    disk_monitor: Monitor de disco.

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_monitor` | `system_monitor` |
| `_service_monitor` | `service_monitor` |
| `_pihole_monitor` | `pihole_monitor` |
| `_network_monitor` | `network_monitor` |
| `_disk_monitor` | `disk_monitor` |
| `_widgets` | `{}` |
| `_running` | `True` |

### Métodos públicos

#### `destroy(self)`

Detiene de forma segura la ventana de descripción general.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, system_monitor, service_monitor, pihole_monitor, network_monitor, disk_monitor)`

Inicializa la ventana de resumen del sistema.

Configura la ventana sin bordes en posición fija, almacena referencias 
a los monitores del sistema y crea la interfaz de usuario.

Args:
    parent: Ventana padre.
    system_monitor: Monitor del sistema (CPU/RAM/temperatura).
    service_monitor: Monitor de servicios.
    pihole_monitor: Monitor de Pi-hole.
    network_monitor: Monitor de red.
    disk_monitor: Monitor de disco.

#### `_create_ui(self)`

Construye la interfaz completa del dashboard de resumen.

Estructura la ventana con un frame principal, un canvas con scrollbar y un grid para tarjetas.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_update(self)`

Actualiza automáticamente todas las secciones del dashboard a intervalos regulares.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_color_for(self, value, warn, crit)`

Asigna un color basado en umbrales configurables para representar estados de una métrica.

Args:
    value (float): Valor numérico de la métrica a evaluar.
    warn (float): Umbral de advertencia que determina el color naranja.
    crit (float): Umbral crítico que determina el color rojo.

Returns:
    str: Clave de color correspondiente ('danger', 'warning' o 'primary').

Raises:
    None

#### `_refresh_system(self)`

Actualiza las tarjetas de sistema con datos de los monitores correspondientes.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_refresh_services(self)`

Actualiza la tarjeta de servicios con el estado actual de servicios fallidos y totales.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_refresh_net(self)`

Actualiza la información de velocidad de red en la ventana de resumen.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Exception: Si ocurre un error al obtener las estadísticas de red.

Nota: Actualiza el texto con formato ↓X.X ↑Y.Y en azul primary si el monitor de red está activo, '--' si no, o '-- (parado)' si el monitor está detenido.

#### `_refresh_pihole(self)`

Actualiza las métricas de Pi-hole: bloqueadas hoy, porcentaje de bloqueo, total de consultas y estado.

Args: Ninguno

Returns: Ninguno

Raises: Exception si ocurre un error al obtener las estadísticas de Pi-hole.

Nota: Actualiza los widgets correspondientes con formato de separadores de miles y maneja casos sin datos o errores.

</details>
