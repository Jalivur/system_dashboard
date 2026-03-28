# `ui.windows.usb`

> **Ruta**: `ui/windows/usb.py`

> **Cobertura de documentación**: 🟢 100% (11/11)

Ventana de monitoreo de dispositivos USB

---

## Tabla de contenidos

**Clase [`USBWindow`](#clase-usbwindow)**

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `ui.widgets`
- `utils.logger`
- `utils.system_utils`

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox
from utils.system_utils import SystemUtils
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `USBWindow(ctk.CTkToplevel)`

Ventana emergente para monitorear dispositivos USB conectados.

Args:
    parent: Widget padre CTkToplevel del dashboard.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_utils` | `SystemUtils()` |
| `_device_widgets` | `[]` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent)`

Inicializa la ventana de monitoreo de dispositivos USB.

Args:
    parent: Widget padre CTkToplevel del dashboard.

Returns:
    None

Raises:
    None

#### `_create_ui(self)`

Crea la interfaz de usuario para la ventana de dispositivos USB.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_refresh_devices(self)`

Refresca la lista de dispositivos USB conectados y actualiza la interfaz gráfica.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_create_storage_section(self, storage_devices: list)`

Crea la sección de almacenamiento USB en la ventana.

Args:
    storage_devices (list): Lista de dispositivos de almacenamiento USB.

#### `_create_storage_device_widget(self, device: dict, index: int)`

Crea un widget para representar un dispositivo de almacenamiento en la interfaz gráfica.

Args:
    device (dict): Diccionario con información del dispositivo, incluyendo 'name', 'size', 'type' y 'dev'.
    index (int): Índice del dispositivo, no utilizado en la implementación actual.

Returns:
    None

Raises:
    None

#### `_create_partition_widget(self, parent, partition: dict)`

Crea un widget para representar una partición en la interfaz gráfica.

Args:
    parent: El widget padre donde se creará el widget de partición.
    partition (dict): Diccionario con información de la partición, incluyendo 'name', 'mount' y 'size'.

Returns:
    None

Raises:
    None

#### `_create_other_devices_section(self, other_devices: list)`

Crea la sección de otros dispositivos USB en la ventana.

Args:
    other_devices (list): Lista de dispositivos USB adicionales para mostrar.

Returns:
    None

Raises:
    None

#### `_create_other_device_widget(self, device_line: str, index: int)`

Crea un widget para representar un dispositivo USB adicional en la interfaz.

Args:
    device_line (str): Línea de salida del comando lsusb que describe el dispositivo.
    index (int): Índice del dispositivo en la lista.

Returns:
    None

Raises:
    None

#### `_parse_lsusb_line(self, line: str) -> dict`

Extrae información de un dispositivo USB a partir de una línea de salida de lsusb.

Args:
    line (str): Línea de salida de lsusb.

Returns:
    dict: Diccionario con claves 'bus' y 'description' que contienen la información del dispositivo.

Raises:
    None

#### `_eject_device(self, device: dict)`

Expulsa un dispositivo USB de manera segura.

Args:
    device (dict): Información del dispositivo USB a expulsar.

Returns:
    None

Raises:
    None

</details>
