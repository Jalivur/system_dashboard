# `ui.windows.network_local`

> **Ruta**: `ui/windows/network_local.py`

> **Cobertura de documentación**: 🟢 100% (8/8)

Ventana de panel de red local.
Muestra los dispositivos encontrados por arp-scan con IP, MAC, fabricante y hostname.

---

## Tabla de contenidos

**Clase [`NetworkLocalWindow`](#clase-networklocalwindow)**

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `utils.logger`

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

Ventana emergente que muestra dispositivos detectados en la red local.

Args:
    parent: Ventana principal padre de esta ventana.
    network_scanner: Instancia del escáner de red externa para obtener dispositivos.

Raises:
    None

Returns:
    None

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
mostrando IP, MAC, fabricante y hostname.

Args:
    parent: Ventana principal (CTkToplevel) padre de esta ventana.
    network_scanner: Instancia del escáner de red externa para obtener dispositivos.

#### `_create_ui(self)`

Construye toda la interfaz de usuario de la ventana.

Crea los componentes visuales principales, incluyendo el encabezado con título y 
controles de ventana, un área scrollable para la lista de dispositivos y un 
frame inferior con funcionalidades adicionales.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_start_scan(self)`

Inicia el proceso de escaneo de la red y activa la verificación periódica de resultados.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_poll_result(self)`

Verifica periódicamente el estado del escaneo y actualiza la interfaz gráfica accordingly.

Args: 
    None

Returns: 
    None

Raises: 
    None

#### `_render(self)`

Redibuja la lista con los dispositivos encontrados en la red local.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_device_row(self, device: dict)`

Crea una fila que representa un dispositivo en la interfaz gráfica.

Args:
    device (dict): Diccionario que contiene la información del dispositivo, incluyendo 'ip', 'hostname' y 'MAC' (aunque este último no se utiliza en este método).

Returns:
    None

Raises:
    None

#### `_on_close(self)`

Gestiona el cierre ordenado de la ventana.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
