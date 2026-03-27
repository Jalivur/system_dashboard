# `ui.windows.homebridge`

> **Ruta**: `ui/windows/homebridge.py`

Ventana de control de dispositivos Homebridge
Muestra enchufes e interruptores y permite encenderlos / apagarlos

## Imports

```python
import threading
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header, make_homebridge_switch
from ui.widgets import custom_msgbox
from core.homebridge_monitor import HomebridgeMonitor
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `HB_UPDATE_MS` | `5000` |

## Clase `HomebridgeWindow(ctk.CTkToplevel)`

Ventana de control de dispositivos Homebridge.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_hb` | `homebridge_monitor` |
| `_accessories` | `[]` |
| `_update_job` | `None` |
| `_busy` | `False` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, homebridge_monitor: HomebridgeMonitor)`

Inicializa la ventana de Homebridge con monitor, estado inicial y configuración básica.

#### `_create_ui(self)`

Crea todos los elementos de la interfaz de usuario de la ventana.

#### `_schedule_update(self)`

Programa la actualización periódica de los dispositivos.

#### `_force_refresh(self)`

Fuerza una actualización inmediata de los dispositivos Homebridge.

#### `_fetch_and_render(self)`

Obtiene los accesorios de Homebridge y los renderiza en la UI de forma asíncrona.

#### `_render(self, accessories)`

Renderiza la lista de accesorios en tarjetas de dispositivos en la interfaz.

#### `_create_device_card(self, acc: dict, grid_row: int, grid_col: int)`

Crea y posiciona una tarjeta para un dispositivo Homebridge específico.

#### `_card_switch(self, card, acc, disabled)`

Switch ON/OFF (enchufe, interruptor, luz básica).

#### `_card_thermostat(self, card, acc, disabled)`

Crea la interfaz de un termostato con temperatura actual y controles de objetivo.

#### `_card_sensor(self, card, acc)`

Crea la interfaz de un sensor de temperatura/humedad (solo lectura).

#### `_card_blind(self, card, acc, disabled)`

Crea la interfaz de una persiana/estor con barra de progreso de posición.

#### `_toggle(self, unique_id: str, turn_on: bool)`

Envía comando ON/OFF a un dispositivo en segundo plano de forma asíncrona.

#### `_set_status(self, text: str)`

Actualiza el texto de estado en la barra inferior de la ventana.

#### `_on_close(self)`

Maneja el cierre de la ventana, cancelando jobs y limpiando recursos.

</details>
