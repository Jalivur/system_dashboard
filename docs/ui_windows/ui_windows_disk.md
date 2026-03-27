# `ui.windows.disk`

> **Ruta**: `ui/windows/disk.py`

Ventana de monitoreo de disco

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_window_header
from ui.widgets import GraphWidget
from core.disk_monitor import DiskMonitor
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `DiskWindow(ctk.CTkToplevel)`

Ventana de monitoreo de disco

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_disk_monitor` | `disk_monitor` |
| `_widgets` | `{}` |
| `_graphs` | `{}` |
| `_smart_tick` | `0` |
| `_smart_cache` | `{}` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, disk_monitor: DiskMonitor)`

Inicializa la ventana de monitoreo de disco con el monitor de disco proporcionado.

Configura título, geometría, colores y lanza creación de UI + bucle de actualizaciones.

Args:
    parent: Widget padre (ctk.CTkToplevel).
    disk_monitor: Instancia de DiskMonitor para obtener estadísticas de disco.

#### `_create_ui(self)`

Construye toda la interfaz gráfica de la ventana:

- Header con título y botón de cierre.
- Contenedor scrollable con canvas.
- Grid 2x2 de celdas con labels, valores numéricos y widgets GraphWidget.
- Tarjeta inferior para métricas SMART NVMe (2 filas x 3 columnas).

#### `_create_cell(self, parent, row, col, title, key, unit, graph_h)`

Celda original con gráfica — sin cambios.

#### `_create_smart_col(self, parent, col_idx: int, key: str, title: str)`

Columna de un campo SMART — sin gráfica.

#### `_update(self)`

Actualiza la interfaz con datos actuales e históricos del DiskMonitor.

- Refresca labels, colores y gráficos de métricas (% uso, temp, I/O).
- Actualiza header status.
- SMART cada _SMART_EVERY ciclos (lento).
- Llama recursivamente cada UPDATE_MS ms.
- Maneja si monitor no corre (muestra banner stopped).

#### `_refresh_smart(self)`

Llama a get_nvme_smart() y actualiza las etiquetas SMART.

#### `_set_smart(self, key: str, text: str, warn)`

Actualiza una etiqueta SMART con color según warn.

#### `_fmt_hours(hours) -> str`

Convierte horas totales de uso en formato legible 'Dd Hh'.

Args:
    hours (float | None): Horas totales.

Returns:
    str: Formato '125d 3h' o '--'.

#### `_fmt_int(val) -> str`

Formatea valor entero o None como string.

Args:
    val (int | None): Valor a formatear.

Returns:
    str: str(val) o '--'.

#### `_fmt_tb(val) -> str`

Formatea terabytes en TB o GB según magnitud.

Args:
    val (float | None): TB a formatear.

Returns:
    str: '1.23 TB', '456 GB' o '--'.

#### `_update_metric(self, key, value, history, unit, warn, crit)`

Actualiza label, color y gráfico de una métrica con umbral.

Args:
    key (str): ID métrica.
    value (float): Valor actual.
    history (list): Historial para gráfico.
    unit (str): Unidad ('%', '°C').
    warn (float): Umbral warning.
    crit (float): Umbral crítico.

#### `_update_io(self, key, value, history)`

Actualiza label, color y gráfico para métricas de I/O (lectura/escritura).

Usa umbrales fijos: warn=10, crit=50 MB/s.

Args:
    key (str): 'disk_read' o 'disk_write'.
    value (float): MB/s actual.
    history (list): Historial.

</details>
