# `ui.windows.network`

> **Ruta**: `ui/windows/network.py`

Ventana de monitoreo de red

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, NET_INTERFACE, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import GraphWidget
from utils.system_utils import SystemUtils
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `NetworkWindow(ctk.CTkToplevel)`

Ventana de monitoreo de red

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_network_monitor` | `network_monitor` |
| `_widgets` | `{}` |
| `_graphs` | `{}` |
| `_interface_update_counter` | `0` |
| `_banner_shown` | `False` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, network_monitor)`

Inicializa la ventana de monitoreo de red.

Args:
    parent: Widget padre (CTkToplevel).
    network_monitor: Instancia del monitor de red para obtener estadísticas.

#### `_create_ui(self)`

Crea la estructura principal de la interfaz de usuario de la ventana de red.

Esta método configura:
 - Frame principal con colores del tema.
 - Header con título 'MONITOR DE RED', botón cerrar y label de status.
 - Contenedor scrollable con canvas y scrollbar vertical estilizado.
 - Frame interno vinculado para contenido dinámico.

Llama a _build_content para poblar celdas.

#### `_build_content(self, inner)`

Construye el contenido scrollable (se puede reconstruir al reanudar).

#### `_create_traffic_cell(self, parent, row, col, title, key)`

Crea una celda de tráfico de red (descarga/subida) con gráfica.

Args:
    parent: Frame contenedor.
    row, col: Posición en grid.
    title: Título de la celda.
    key: Identificador ('download' o 'upload').

#### `_create_interfaces_cell(self, parent, row, col)`

Crea la celda que muestra interfaces de red activas e IPs.

#### `_create_speedtest_cell(self, parent, row, col)`

Crea la celda para ejecutar y mostrar resultados de speedtest.

#### `_update_interfaces(self)`

Actualiza la lista de interfaces de red con sus direcciones IP.

#### `_run_speedtest(self)`

Inicia la ejecución de un test de velocidad de red.

#### `_update_speedtest(self)`

Actualiza la visualización del resultado del speedtest según su estado.

#### `_update(self)`

Actualiza la interfaz de usuario periódicamente con datos del monitor de red.

</details>
