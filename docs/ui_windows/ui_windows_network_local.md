# `ui.windows.network_local`

> **Ruta**: `ui/windows/network_local.py`

Ventana de panel de red local.
Muestra los dispositivos encontrados por arp-scan con IP, MAC, fabricante y hostname.

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import make_window_header, make_futuristic_button, StyleManager
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `AUTO_REFRESH_S` | `60` |

## Clase `NetworkLocalWindow(ctk.CTkToplevel)`

Panel de dispositivos en la red local.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_scanner` | `network_scanner` |
| `_auto_job` | `None` |
| `_poll_job` | `None` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, network_scanner)`

Inicializa y configura la ventana emergente del panel de red local.

Esta ventana muestra dispositivos detectados en la red mediante arp-scan,
mostrando IP, MAC, fabricante y hostname. Configura geometría, UI y escaneo inicial.

Args:
    parent: Ventana principal (CTkToplevel) padre de esta ventana.
    network_scanner: Instancia del escáner de red externa para obtener dispositivos.

#### `_create_ui(self)`

Construye toda la interfaz de usuario de la ventana.

Crea:
    - Header con título y controles de ventana
    - Canvas scrollable para lista de dispositivos
    - Frame inferior con contador y botón de escaneo manual

#### `_start_scan(self)`

Lanza el escaneo y activa el polling de resultado.

#### `_poll_result(self)`

Comprueba cada 500ms si el escaneo terminó.

#### `_render(self)`

Redibuja la lista con los dispositivos encontrados.

#### `_create_device_row(self, device: dict)`

Fila de un dispositivo: IP | hostname | MAC | fabricante.

#### `_on_close(self)`

Gestiona el cierre ordenado de la ventana.

Cancela:
    - Tareas de refresco automático (_auto_job)
    - Polling de resultados de escaneo (_poll_job)
Registra cierre en logs y destruye la ventana.

</details>
