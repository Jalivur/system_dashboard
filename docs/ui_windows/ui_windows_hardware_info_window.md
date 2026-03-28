# `ui.windows.hardware_info_window`

> **Ruta**: `ui/windows/hardware_info_window.py`

> **Cobertura de documentación**: 🟢 100% (13/13)

Ventana de información estática del hardware.
Muestra datos del sistema que no cambian en runtime:
modelo de CPU, núcleos, RAM total, kernel, arquitectura,
hostname y uptime (este último se refresca cada 60s).

No requiere core service propio — los datos estáticos se leen
una sola vez al abrir la ventana via psutil/platform/subprocess.
El uptime se lee del caché de SystemMonitor.

---

## Tabla de contenidos

**Clase [`HardwareInfoWindow`](#clase-hardwareinfowindow)**

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `utils.logger`

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

Lee el modelo de CPU desde el sistema.

Args:
    Ninguno

Returns:
    str: El modelo de CPU.

Raises:
    Ninguno

Nota: Si no se puede leer el modelo de CPU desde /proc/cpuinfo, 
      se devuelve el resultado de platform.processor() o "Desconocido".

### `_read_pi_model() -> str`

Lee el modelo de Raspberry Pi desde el archivo /proc/device-tree/model.

Args: 
    Ninguno

Returns:
    str: El modelo de Raspberry Pi como cadena de texto.

Raises:
    Ninguno

### `_read_os() -> str`

Obtiene el nombre del sistema operativo.

Args:
    Ninguno

Returns:
    str: El nombre del sistema operativo.

Raises:
    Ninguna excepción específica, manejo genérico de excepciones.

### `_gather_static_info() -> dict`

Recopila información estática del hardware y sistema operativo.

Args:
    Ninguno

Returns:
    dict: Diccionario con información estática del hardware y sistema operativo.

Raises:
    Ninguno

</details>

## Clase `HardwareInfoWindow(ctk.CTkToplevel)`

Ventana emergente que muestra información estática del hardware y uptime dinámico.

Args:
    parent: Ventana padre (CTkToplevel) que crea esta ventana.
    system_monitor: Instancia para obtener uptime dinámico.

Raises:
    Ninguna excepción específica.

Returns:
    Ningún valor de retorno.

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

Raises:
    None

#### `_load_info(self) -> None`

Carga información estática en segundo plano y actualiza la interfaz de usuario.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_populate_info(self, info: dict) -> None`

Rellena la UI con los datos de hardware proporcionados.

Args:
    info (dict): Diccionario con la información de hardware.

Returns:
    None

Raises:
    None

#### `_create_ui(self)`

Crea la estructura de la interfaz de usuario principal para mostrar información del hardware.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_show_loading(self, parent) -> None`

Muestra un mensaje de carga mientras se recopila información del hardware.

Args:
    parent: El elemento padre donde se mostrará el mensaje de carga.

Returns:
    None

Raises:
    None

#### `_build_content(self, inner)`

Construye secciones de contenido con datos reales del hardware.

Args:
    inner: Frame contenedor para los widgets de secciones.

Returns:
    None

Raises:
    None

#### `_section(self, parent, title: str, rows: list)`

Crea una tarjeta de sección con filas etiqueta-valor en la ventana de información de hardware.

Args:
    parent: El elemento padre donde se creará la tarjeta de sección.
    title (str): El título de la sección.
    rows (list): Una lista de tuplas (etiqueta, valor) que representan las filas de la sección.

Returns:
    None

Raises:
    None

#### `_tick_uptime(self)`

Refresca el tiempo de actividad (uptime) de la ventana cada segundo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
