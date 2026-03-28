# `ui.windows.monitor`

> **Ruta**: `ui/windows/monitor.py`

> **Cobertura de documentación**: 🟢 100% (6/6)

Ventana de monitoreo del sistema

---

## Tabla de contenidos

**Clase [`MonitorWindow`](#clase-monitorwindow)**

---

## Dependencias internas

- `config.settings`
- `core.system_monitor`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, CPU_WARN, CPU_CRIT, TEMP_WARN, TEMP_CRIT, RAM_WARN, RAM_CRIT, Icons
from ui.styles import StyleManager, make_window_header
from ui.widgets import GraphWidget
from core.system_monitor import SystemMonitor
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `MonitorWindow(ctk.CTkToplevel)`

Ventana de monitoreo del sistema con información de métricas y estado.

Args:
    parent: Ventana padre (CTkToplevel).
    system_monitor: Instancia de SystemMonitor para métricas CPU/RAM/TEMP.
    hardware_monitor: Instancia opcional de monitor hardware FNK0100K (fase1).

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_monitor` | `system_monitor` |
| `_hardware_monitor` | `hardware_monitor` |
| `_widgets` | `{}` |
| `_graphs` | `{}` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, system_monitor: SystemMonitor, hardware_monitor = None)`

Inicializa la ventana de monitoreo del sistema.

Configura la ventana toplevel con geometría fija para DSI, título, colores y
comportamientos. Registra monitores de sistema/hardware y crea la interfaz de usuario.

Args:
    parent: Ventana padre.
    system_monitor: Instancia de SystemMonitor para métricas CPU/RAM/TEMP.
    hardware_monitor: Instancia opcional de monitor hardware.

#### `_create_ui(self)`

Crea la interfaz de usuario completa de la ventana de monitoreo.

    Args: 
        Ninguno

    Returns: 
        Ninguno

    Raises: 
        Ninguno

#### `_create_cell(self, parent, row, col, title, key, unit, graph_h)`

Crea una celda individual para mostrar y graficar una métrica del sistema.

Args:
    parent: Frame contenedor (grid).
    row, col: Posición en grid.
    title: Título de la métrica (ej: 'CPU %').
    key: Identificador interno ('cpu', 'ram', etc.).
    unit: Unidad de medida ('%', '°C').
    graph_h: Altura del gráfico en píxeles.

Returns:
    None

Raises:
    None

#### `_update(self)`

Actualiza todas las métricas del monitoreo en ciclo recursivo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update_metric(self, key, value, history, unit, warn, crit)`

Actualiza visualmente una métrica específica según su valor actual.

Determina color según umbrales de advertencia y crítico. Actualiza label de valor/unidad 
y título con el color, y refresca el gráfico con historia y máximo configurado.

Args:
    key (str): Identificador de métrica.
    value (float): Valor numérico actual.
    history (list): Lista histórica de valores para el gráfico.
    unit (str): Unidad de medida.
    warn (float): Umbral de advertencia.
    crit (float): Umbral crítico.

Returns:
    None

Raises:
    None

</details>
