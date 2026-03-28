# `ui.windows.led_window`

> **Ruta**: `ui/windows/led_window.py`

> **Cobertura de documentación**: 🟢 100% (13/13)

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

---

## Tabla de contenidos

**Clase [`LedWindow`](#clase-ledwindow)**

---

## Dependencias internas

- `config.settings`
- `core.led_service`
- `ui.styles`
- `utils.logger`

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

Ventana de control de LEDs RGB flotante.

Args:
    parent: Ventana principal (CTk).
    led_service: Instancia del servicio LED para control y estado.

Returns:
    None

Raises:
    None

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

Crea la interfaz de usuario principal de la ventana LED.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_build_content(self, inner)`

Construye el contenido real de la ventana de LEDs.

Args:
    inner (ctk.CTkFrame): Frame contenedor para los widgets del contenido.

Raises:
    Ninguna excepción específica.

#### `_update(self)`

Actualiza periódicamente el estado de la ventana LED, monitoreando el servicio LED.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_set_mode(self, mode: str)`

Cambia el modo de operación de los LEDs y aplica el color RGB actual.

Args:
    mode (str): Modo LED (e.g., 'static', 'auto', 'rainbow'). 

Raises:
    None
Returns:
    None

#### `_on_color_change(self)`

Actualiza el previsualizador de color en tiempo real cuando se modifican los valores de los deslizadores RGB.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_apply_color(self)`

Aplica el color RGB actual del preview al servicio LED, ajustando modo a 'static' si necesario.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_quick_color(self, r: int, g: int, b: int)`

Establece un color RGB predefinido en los sliders, actualiza el preview y aplica inmediatamente al servicio LED.

Args:
    r (int): Valor rojo (0-255).
    g (int): Valor verde (0-255).
    b (int): Valor azul (0-255).

#### `_update_preview(self)`

Actualiza el canvas de preview con el color RGB actual de los sliders y refresca las etiquetas numéricas de valores R/G/B.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_highlight_mode_btn(self, active_mode: str)`

Resalta visualmente el botón del modo LED activo y desactiva los demás.

Args:
    active_mode (str): Modo actualmente seleccionado.

Returns:
    None

Raises:
    None

#### `_update_status(self)`

Actualiza el label de estado con el modo LED actual y valores RGB si aplica.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_load_current_state(self)`

Carga el estado actual del servicio LED y actualiza la interfaz gráfica reflejando el modo y los valores RGB.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

</details>
