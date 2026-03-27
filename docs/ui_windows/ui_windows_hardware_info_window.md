# `ui.windows.hardware_info_window`

> **Ruta**: `ui/windows/hardware_info_window.py`

Ventana de información estática del hardware.
Muestra datos del sistema que no cambian en runtime:
modelo de CPU, núcleos, RAM total, kernel, arquitectura,
hostname y uptime (este último se refresca cada 60s).

No requiere core service propio — los datos estáticos se leen
una sola vez al abrir la ventana via psutil/platform/subprocess.
El uptime se lee del caché de SystemMonitor.

## Imports

```python
import platform
import subprocess
import psutil
import threading
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

<details>
<summary>Funciones privadas</summary>

### `_read_cpu_model() -> str`

Lee el modelo de CPU desde /proc/cpuinfo.

### `_read_pi_model() -> str`

Lee el modelo de Raspberry Pi desde /proc/device-tree/model.

### `_read_os() -> str`

Devuelve el nombre del SO.

### `_gather_static_info() -> dict`

Recopila toda la información estática del hardware.

</details>

## Clase `HardwareInfoWindow(ctk.CTkToplevel)`

Ventana de información del hardware — datos estáticos + uptime dinámico.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_monitor` | `system_monitor` |
| `_uptime_tick` | `0` |
| `_uptime_label` | `None` |
| `_info` | `{}` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, system_monitor)`

Inicializa la ventana de información del hardware.

Args:
    parent: Ventana padre (CTkToplevel).
    system_monitor: Instancia para obtener uptime dinámico.

#### `_load_info(self) -> None`

Carga info estática en background y rellena la UI.

#### `_populate_info(self, info: dict) -> None`

Rellena la UI con los datos ya cargados (main thread).

#### `_create_ui(self)`

Crea la estructura de la interfaz de usuario principal con scroll y placeholder de carga.

#### `_show_loading(self, parent) -> None`

Muestra texto de carga mientras _gather_static_info trabaja.

#### `_build_content(self, inner)`

Construye secciones de contenido con datos reales del hardware (Sistema, CPU, RAM, Uptime).

Args:
    inner: Frame contenedor para los widgets de secciones.

#### `_section(self, parent, title: str, rows: list)`

Crea una tarjeta de sección con filas etiqueta-valor.

#### `_tick_uptime(self)`

Refresca el uptime cada _UPTIME_EVERY segundos.

</details>
