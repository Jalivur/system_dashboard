# `ui.windows.monitor`

> **Ruta**: `ui/windows/monitor.py`

Ventana de monitoreo del sistema

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

Ventana de monitoreo del sistema

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
comportamientos (no redimensionable, sin barra título). Registra monitores de
sistema/hardware, crea la interfaz de usuario y lanza el ciclo de actualizaciones.

Args:
    parent: Ventana padre (CTkToplevel).
    system_monitor: Instancia de SystemMonitor para métricas CPU/RAM/TEMP.
    hardware_monitor: Instancia opcional de monitor hardware FNK0100K (fase1).

#### `_create_ui(self)`

Crea la interfaz de usuario completa de la ventana de monitoreo.

Construye el frame principal, header de ventana, contenedor scrollable con canvas,
grid de celdas para métricas CPU/RAM/TEMP con labels, valores y gráficos. 
Condicionalmente añade tarjeta de hardware FNK0100K si self._hardware_monitor existe.
Registra todos los widgets y graphs en self._widgets/self._graphs.

#### `_create_cell(self, parent, row, col, title, key, unit, graph_h)`

Crea una celda individual para mostrar y graficar una métrica del sistema.

Construye frame para celda con label de título, label dinámico de valor/unidad,
y GraphWidget. Aplica colores y estilos según StyleManager. Registra los widgets
en self._widgets y el gráfico con max_val en self._graphs.

Args:
    parent: Frame contenedor (grid).
    row, col: Posición en grid.
    title: Título de la métrica (ej: 'CPU %').
    key: Identificador interno ('cpu', 'ram', etc.).
    unit: Unidad de medida ('%', '°C').
    graph_h: Altura del gráfico en píxeles.

#### `_update(self)`

Actualiza todas las métricas del monitoreo en ciclo recursivo.

Verifica existencia de ventana y estado del servicio SystemMonitor. Obtiene
estadísticas actuales/históricas, actualiza celdas métricas (CPU/RAM/TEMP),
header resumen, tarjeta hardware FNK0100K si disponible (con colores por umbrales),
y programa la próxima actualización en UPDATE_MS milisegundos.

#### `_update_metric(self, key, value, history, unit, warn, crit)`

Actualiza visualmente una métrica específica según su valor actual.

Determina color según umbrales de advertencia (warn) y crítico (crit) usando
SystemMonitor.level_color(). Actualiza label de valor/unidad y título con el color,
y refresca el gráfico con historia y máximo configurado.

Args:
    key: Identificador de métrica ('cpu', 'ram', 'temp').
    value: Valor numérico actual.
    history: Lista histórica de valores para el gráfico.
    unit: Unidad ('%', '°C').
    warn: Umbral de advertencia.
    crit: Umbral crítico.

</details>
