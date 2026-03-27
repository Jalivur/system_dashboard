# `ui.windows.usb`

> **Ruta**: `ui/windows/usb.py`

Ventana de monitoreo de dispositivos USB

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

Ventana de monitoreo de dispositivos USB

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

#### `_create_ui(self)`

Crea la interfaz de usuario

#### `_refresh_devices(self)`

Refresca la lista de dispositivos USB

#### `_create_storage_section(self, storage_devices: list)`

Crea la sección de almacenamiento USB

#### `_create_storage_device_widget(self, device: dict, index: int)`

Crea widget para un dispositivo de almacenamiento

#### `_create_partition_widget(self, parent, partition: dict)`

Crea widget para una partición

#### `_create_other_devices_section(self, other_devices: list)`

Crea la sección de otros dispositivos USB

#### `_create_other_device_widget(self, device_line: str, index: int)`

Crea widget para otro dispositivo USB

#### `_parse_lsusb_line(self, line: str) -> dict`

Parsea una línea de lsusb

#### `_eject_device(self, device: dict)`

Expulsa un dispositivo USB

</details>
