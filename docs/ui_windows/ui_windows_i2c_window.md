# `ui.windows.i2c_window`

> **Ruta**: `ui/windows/i2c_window.py`

> **Cobertura de documentación**: 🟢 100% (12/12)

ui/windows/i2c_window.py

Ventana de escaneo I2C — muestra dispositivos detectados en cada bus.
Solo lectura. Refresco manual o automático cada 30s.

---

## Tabla de contenidos

**Clase [`I2CWindow`](#clase-i2cwindow)**
  - [`destroy()`](#destroyself-none)

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `utils.logger`

## Imports

```python
import tkinter as tk
import time
import threading
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `I2CWindow(ctk.CTkToplevel)`

Ventana emergente para visualizar información de escaneo I2C.

Args:
    parent: Ventana padre (CTkToplevel).
    i2c_monitor: Instancia del monitor I2C para obtener estadísticas.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_mon` | `i2c_monitor` |
| `_after_id` | `None` |
| `_scanning` | `False` |

### Métodos públicos

#### `destroy(self) -> None`

Destruye la ventana limpiando el temporizador de actualización.

Args:
    None

Returns:
    None

Raises:
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, i2c_monitor)`

Inicializa la ventana de escaneo I2C.

Configura la ventana principal, crea la interfaz de usuario, inicia el bucle
de actualización automática y registra el evento de apertura en el logger.

Args:
    parent: Ventana padre (CTkToplevel).
    i2c_monitor: Instancia del monitor I2C para obtener estadísticas.

#### `_create_ui(self)`

Crea todos los elementos de la interfaz de usuario de la ventana I2C.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update(self) -> None`

Actualiza la interfaz de la ventana I2C periódicamente.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_render(self, stats: dict) -> None`

Renderiza las estadísticas I2C en la interfaz.

Limpia el área de renderizado, maneja errores o datos vacíos, muestra el total de dispositivos 
y renderiza tarjetas por bus con sus dispositivos.

Args:
    stats (dict): Diccionario con 'buses', 'total', 'error'.

Returns:
    None

Raises:
    None

#### `_render_bus(self, bus_info: dict) -> None`

Renderiza la card de un bus I2C específico.

Crea la card con cabecera (label y count), línea divisoria, lista de dispositivos 
o mensaje vacío, y spacer inferior.

Args:
    bus_info (dict): Info del bus con 'label', 'count', 'devices'.

Returns:
    None

Raises:
    Ninguna excepción específica.

#### `_render_device(self, parent, dev: dict) -> None`

Renderiza una fila individual de dispositivo I2C con información proporcionada.

Args:
    parent: Frame contenedor de la fila.
    dev (dict): Info del dispositivo con 'addr_hex', 'name', 'addr'.

Returns:
    None

#### `_show_placeholder(self, text: str, color: str = None) -> None`

Muestra un mensaje placeholder centrado en el área principal.

Útil para estados de carga, errores o sin datos.

Args:
    text (str): Texto a mostrar.
    color (str, opcional): Color del texto. Defaults to None.

Returns:
    None

Raises:
    Ninguna excepción.

#### `_on_scan(self) -> None`

Inicia un escaneo manual I2C en un hilo separado.

Args:
    None

Returns:
    None

Raises:
    None

#### `_on_scan_done(self) -> None`

Callback ejecutado tras completar el escaneo manual.

Re-habilita el botón, limpia status y refresca la visualización.

Args:
    None

Returns:
    None

Raises:
    None

</details>
