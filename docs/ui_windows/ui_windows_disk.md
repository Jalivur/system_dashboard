# `ui.windows.disk`

> **Ruta**: `ui/windows/disk.py`

> **Cobertura de documentación**: 🟢 100% (13/13)

Ventana de monitoreo de disco

---

## Tabla de contenidos

**Clase [`DiskWindow`](#clase-diskwindow)**

---

## Dependencias internas

- `config.settings`
- `core.disk_monitor`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

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

Ventana emergente para monitorear el estado del disco.

Args:
    parent: Widget padre que crea esta ventana.
    disk_monitor: Instancia de DiskMonitor para obtener estadísticas de disco.

Raises:
    Ninguna excepción específica.

Returns:
    Ningún valor de retorno.

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

Crea la interfaz gráfica completa de la ventana del disco.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_cell(self, parent, row, col, title, key, unit, graph_h)`

Crea una celda con gráfica en la ventana de disco.

Args:
    parent: El widget padre donde se creará la celda.
    row: La fila donde se posicionará la celda en la cuadrícula.
    col: La columna donde se posicionará la celda en la cuadrícula.
    title: El título de la celda.
    key: La clave única para identificar la celda.
    unit: La unidad de medida para el valor de la celda.
    graph_h: La altura de la gráfica en la celda.

Returns:
    None

Raises:
    None

#### `_create_smart_col(self, parent, col_idx: int, key: str, title: str)`

Crea una columna para mostrar información de un campo SMART sin gráfica.

Args:
    parent: El widget padre donde se creará la columna.
    col_idx (int): El índice de la columna.
    key (str): La clave para guardar la referencia del widget.
    title (str): El título de la columna.

Returns:
    None

Raises:
    None

#### `_update(self)`

Actualiza la interfaz de DiskWindow con datos actuales e históricos del DiskMonitor.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_refresh_smart(self)`

Actualiza las etiquetas SMART del disco duro mediante la información obtenida de get_nvme_smart().

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_set_smart(self, key: str, text: str, warn)`

Actualiza una etiqueta SMART con color según warn.

Args:
    key (str): Clave de la etiqueta SMART.
    text (str): Texto a mostrar en la etiqueta.
    warn: Indica el color a utilizar en la etiqueta.

Returns:
    None

Raises:
    None

#### `_fmt_hours(hours) -> str`

Convierte horas totales de uso en formato legible 'Dd Hh'.

Args:
    hours (float | None): Horas totales.

Returns:
    str: Formato 'Dd Hh' o '--' si hours es None.

#### `_fmt_int(val) -> str`

Formatea un valor entero o None como cadena.

Args:
    val (int | None): Valor a formatear.

Returns:
    str: Representación en cadena del valor o '--' si es None.

#### `_fmt_tb(val) -> str`

Formatea terabytes en TB o GB según magnitud.

Args:
    val (float | None): TB a formatear.

Returns:
    str: Representación formateada del valor en TB o GB, o '--' si el valor es None.

#### `_update_metric(self, key, value, history, unit, warn, crit)`

Actualiza la etiqueta, el color y el gráfico de una métrica con umbrales.

Args:
    key (str): Identificador de la métrica.
    value (float): Valor actual de la métrica.
    history (list): Historial de valores para el gráfico.
    unit (str): Unidad de medida de la métrica ('%', '°C').
    warn (float): Umbral de advertencia.
    crit (float): Umbral crítico.

Returns:
    None

Raises:
    None

#### `_update_io(self, key, value, history)`

Actualiza label, color y gráfico para métricas de I/O (lectura/escritura).

Usa umbrales fijos: warn=10, crit=50 MB/s.

Args:
    key (str): 'disk_read' o 'disk_write'.
    value (float): MB/s actual.
    history (list): Historial.

Returns:
    None

Raises:
    None

</details>
