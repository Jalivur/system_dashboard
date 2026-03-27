# `ui.windows.i2c_window`

> **Ruta**: `ui/windows/i2c_window.py`

ui/windows/i2c_window.py

Ventana de escaneo I2C — muestra dispositivos detectados en cada bus.
Solo lectura. Refresco manual o automático cada 30s.

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

Ventana de escaneo I2C — solo lectura.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_mon` | `i2c_monitor` |
| `_after_id` | `None` |
| `_scanning` | `False` |

### Métodos públicos

#### `destroy(self) -> None`

Destruye la ventana limpiando el temporizador de actualización.

Cancela el after_id si existe y llama al destroy del padre.
Registra el cierre en logger.

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

Crea todos los elementos de la interfaz de usuario.

Incluye header, barra de acciones (botón de escaneo, labels de estado),
y área scrollable con canvas para mostrar los resultados por bus I2C.

#### `_update(self) -> None`

Actualiza la interfaz periódicamente (cada 30s).

Verifica si la ventana existe y si el monitor I2C está activo.
Renderiza estadísticas o muestra banner de servicio detenido. Programa la
siguiente actualización.

#### `_render(self, stats: dict) -> None`

Renderiza las estadísticas I2C en la interfaz.

Limpia el área, maneja errores o datos vacíos, muestra total de dispositivos
y renderiza cards por bus con sus dispositivos.

Args:
    stats (dict): Diccionario con 'buses', 'total', 'error'.

#### `_render_bus(self, bus_info: dict) -> None`

Renderiza la card de un bus I2C específico.

Crea la card con cabecera (label y count), línea divisoria, lista de dispositivos
o mensaje vacío, y spacer inferior.

Args:
    bus_info (dict): Info del bus con 'label', 'count', 'devices'.

#### `_render_device(self, parent, dev: dict) -> None`

Renderiza una fila individual de dispositivo I2C.

Crea badge con dirección hex, label con nombre y label con decimal.

Args:
    parent: Frame contenedor de la fila.
    dev (dict): Info del dispositivo con 'addr_hex', 'name', 'addr'.

#### `_show_placeholder(self, text: str, color: str = None) -> None`

Muestra un mensaje placeholder centrado en el área principal.

Útil para estados de carga, errores o sin datos.

Args:
    text (str): Texto a mostrar.
    color (str, opcional): Color del texto. Defaults to COLORS['text_dim'].

#### `_on_scan(self) -> None`

Inicia un escaneo manual I2C en thread separado.

Deshabilita botón, muestra status 'Escaneando...',
llama a monitor.scan_now() y agenda _on_scan_done.

#### `_on_scan_done(self) -> None`

Callback ejecutado tras completar el escaneo manual.

Re-habilita el botón, limpia status y refresca la visualización.

</details>
