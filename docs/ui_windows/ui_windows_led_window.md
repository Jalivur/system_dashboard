# `ui.windows.led_window`

> **Ruta**: `ui/windows/led_window.py`

Ventana de Control de LEDs RGB

Proporciona una interfaz gráfica intuitiva para controlar 4 LEDs RGB en el GPIO Board
(Freenove FNK0100K, direccion I2C 0x21), gestionados por el servicio LED (fase1.py).

Características:
- Selección de modos: auto, rainbow, static, secuencial, respiración, off.
- Control preciso RGB vía sliders (0-255).
- Preview en tiempo real del color.
- Presets de colores rápidos.
- Estado en vivo sincronizado con el servicio.
- UI responsiva con scroll y banner de servicio.

Dependencias: customtkinter, led_service, StyleManager.
Autor: Sistema Dashboard Develop.

## Imports

```python
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from core.led_service import LED_MODES, LED_MODE_LABELS
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `LedWindow(ctk.CTkToplevel)`

Ventana de control de LEDs RGB.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_led_service` | `led_service` |
| `_r` | `ctk.IntVar(master=self, value=0)` |
| `_g` | `ctk.IntVar(master=self, value=255)` |
| `_b` | `ctk.IntVar(master=self, value=0)` |
| `_mode_var` | `ctk.StringVar(master=self, value='auto')` |
| `_banner_shown` | `False` |
| `_inner` | `None` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, led_service)`

Inicializa la ventana de control LED como Toplevel flotante.

Configura geometría, variables RGB/modo, crea UI y inicia loops de update.

Args:
    parent: Ventana principal (CTk).
    led_service: Instancia del servicio LED para control y estado.

#### `_create_ui(self)`

Crea la interfaz de usuario principal de la ventana LED, incluyendo frame principal, header, canvas con scrollbar y frame interno para contenido.

#### `_build_content(self, inner)`

Construye todos los widgets del contenido: selector de modo, sliders RGB, preview de color, botones de colores rápidos y label de estado.

Args:
    inner (ctk.CTkFrame): Frame contenedor para los widgets.

#### `_update(self)`

Loop principal de actualización periódica (cada UPDATE_MS ms). Monitorea estado del servicio LED:
- Muestra banner si servicio parado.
- Reconstruye UI si servicio reanuda.
Programa la siguiente actualización.

#### `_set_mode(self, mode: str)`

Cambia el modo de operación de los LEDs y aplica el color RGB actual.

Args:
    mode (str): Modo LED (e.g., 'static', 'auto', 'rainbow'). Ver LED_MODES.

#### `_on_color_change(self)`

Callback invocado al cambiar valores de sliders RGB. Actualiza el preview del color en tiempo real.

#### `_apply_color(self)`

Aplica el color RGB actual del preview al servicio LED, ajustando modo a 'static' si necesario. Actualiza UI y estado.

#### `_quick_color(self, r: int, g: int, b: int)`

Establece un color RGB predefinido en los sliders, actualiza el preview y aplica inmediatamente al servicio LED.

Args:
    r (int): Valor rojo (0-255).
    g (int): Valor verde (0-255).
    b (int): Valor azul (0-255).

#### `_update_preview(self)`

Actualiza el canvas de preview con el color RGB actual de los sliders y refresca las etiquetas numéricas de valores R/G/B.

#### `_highlight_mode_btn(self, active_mode: str)`

Resalta visualmente el botón del modo LED activo y desactiva los demás.

Args:
    active_mode (str): Modo actualmente seleccionado.

#### `_update_status(self)`

Actualiza el label de estado con el modo LED actual y valores RGB si aplica (obtenidos del servicio).

#### `_load_current_state(self)`

Carga el estado actual del servicio LED (modo y RGB), lo refleja en sliders/botones/UI y actualiza preview/estado.

</details>
