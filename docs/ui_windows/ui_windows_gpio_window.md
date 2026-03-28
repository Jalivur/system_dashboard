# `ui.windows.gpio_window`

> **Ruta**: `ui/windows/gpio_window.py`

> **Cobertura de documentación**: 🟢 100% (28/28)

Ventana de control y monitorización de pines GPIO.

Modos de operación (toggle en barra superior):
  LIBRE       — dashboard libera todos los pines. Los scripts externos
                pueden usarlos sin conflictos.
  CONTROLANDO — dashboard reclama los pines con gpiozero.
                INPUT: lectura en tiempo real.
                OUTPUT: botón toggle HIGH/LOW.
                PWM: slider 0–100% duty cycle.

Panel de configuración:
  - Añadir/eliminar pines
  - Cambiar modo de pin en caliente
  - Editar etiqueta descriptiva
  - Feedback visual inmediato en cada acción
  - Al cerrar el diálogo reconstruye las filas de la ventana principal

Arquitectura:
  - Widgets creados una sola vez en _build_rows(); recreados solo si
    cambia la lista de pines o el modo de operación.
  - Actualizaciones de estado vía .configure() — nunca recrear en el loop.
  - Comandos OUTPUT/PWM lanzados en threads para no bloquear la UI.
  - Toda la lógica de hardware delegada a GPIOMonitor.

---

## Tabla de contenidos

**Clase [`GPIOWindow`](#clase-gpiowindow)**
  - [`destroy()`](#destroyself)

**Clase [`_GPIOConfigDialog`](#clase-_gpioconfigdialog)**
  - [`destroy()`](#destroyself-none)

---

## Dependencias internas

- `config.settings`
- `core.gpio_monitor`
- `ui.styles`
- `utils.logger`

## Imports

```python
import threading
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger
from core.gpio_monitor import MODE_INPUT, MODE_OUTPUT, MODE_PWM, VALID_MODES, OP_CONTROLANDO, OP_LIBRE
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `GPIOWindow(ctk.CTkToplevel)`

Ventana de control y monitorización GPIO.

Args:
    parent: Widget padre (CTkToplevel).
    gpio_monitor: Instancia del monitor GPIO para interactuar con el hardware.

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_monitor` | `gpio_monitor` |
| `_op_job` | `None` |

### Métodos públicos

#### `destroy(self)`

Destruye la ventana limpiamente y registra el evento de cierre.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, gpio_monitor)`

Inicializa la ventana principal de monitorización y control de pines GPIO.

Args:
    parent: Widget padre (CTkToplevel).
    gpio_monitor: Instancia del monitor GPIO para interactuar con el hardware.

Configura la geometría para pantalla DSI y crea la interfaz de usuario completa.

#### `_create_ui(self)`

Crea la estructura y widgets de la interfaz de usuario.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_toggle_op_mode(self)`

Alterna el modo de operación entre LIBRE y CONTROLANDO.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_op_mode_changed(self)`

Callback ejecutado tras cambio de modo de operación.

Actualiza la barra de operación y reconstruye las filas si la ventana existe.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update_op_bar(self)`

Actualiza visualmente la barra de modo de operación.

Reconfigura labels y botón según el estado actual del monitor.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_op_text(self) -> str`

Genera el texto descriptivo del modo de operación actual.

Returns:
    str: Texto con icono y descripción del estado (LIBRE o CONTROLANDO).

#### `_op_color(self) -> str`

Determina el color del texto según el modo de operación.

Returns:
    str: Color hexadecimal (_C_LIBRE o _C_CONTROLANDO).

#### `_op_btn_text(self) -> str`

Genera el texto para el botón de toggle de modo de operación.

Returns:
    str: Texto con icono apropiado ('Tomar control' o 'Liberar GPIO').

#### `_build_rows(self)`

Reconstruye todas las filas de pines en el canvas interno según el estado actual del monitor.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_create_pin_row(self, pin: int, data: dict, is_libre: bool)`

Crea una fila completa para un pin específico en el canvas.

Args:
    pin (int): Número del pin GPIO.
    data (dict): Estado actual del pin del monitor.
    is_libre (bool): Si el modo de operación es LIBRE.

Returns:
    None

Raises:
    None

#### `_update(self)`

Actualiza el estado de la ventana en tiempo real.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_toggle_output(self, pin: int)`

Alterna el estado HIGH/LOW de un pin en modo OUTPUT.

Args:
    pin (int): Número del pin.

Raises:
    None

Returns:
    None

Nota: Lanza el comando en thread daemon, actualiza UI reactivamente.

#### `_on_pwm_slide(self, pin: int, val: float)`

Manejador de evento para actualizar el ciclo de trabajo de un pin PWM mediante un deslizador.

Args:
    pin (int): Número del pin PWM que se está actualizando.
    val (float): Valor porcentual del deslizador (0-100).

Returns:
    None

Raises:
    None

#### `_status_text(self, state: dict) -> str`

Genera texto resumido del estado para el footer.

Args:
    state (dict): Diccionario de estado de todos los pines.

Returns:
    str: Resumen del estado de los pines.

Raises:
    None

#### `_open_config(self)`

Abre el diálogo de configuración de pines.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_config_closed(self)`

Callback ejecutado al cerrar el diálogo de configuración.

Reconstruye las filas de pines para reflejar cambios.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>

## Clase `_GPIOConfigDialog(ctk.CTkToplevel)`

Diálogo de configuración para pines GPIO.

Args:
    parent: Ventana padre del diálogo.
    gpio_monitor: Instancia del monitor de pines GPIO.
    on_close (callable, optional): Función a llamar al cerrar el diálogo.

Raises:
    None

Returns:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_monitor` | `gpio_monitor` |
| `_on_close` | `on_close` |

### Métodos públicos

#### `destroy(self) -> None`

Cierra el diálogo de configuración GPIO y ejecuta el callback de cierre si existe.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, gpio_monitor, on_close = None)`

Inicializa el diálogo de configuración de pines.

Args:
    parent: Ventana padre.
    gpio_monitor: Instancia del monitor de pines GPIO.
    on_close (callable, optional): Función de llamada de vuelta al cerrar el diálogo.

#### `_create_ui(self)`

Crea la interfaz del diálogo de configuración de pines GPIO.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_build_list(self)`

Reconstruye la lista de pines configurados en el diálogo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_list_row(self, pin: int, data: dict)`

Crea una fila editable para un pin específico en la lista de configuración.

Args:
    pin (int): Número del pin.
    data (dict): Diccionario con los datos del pin.

Returns:
    None

Raises:
    None

#### `_add_pin(self)`

Añade un nuevo pin con modo y etiqueta especificados.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_remove_pin(self, pin: int)`

Elimina un pin de la configuración del diálogo.

Args:
    pin (int): El pin a eliminar de la configuración.

Returns:
    None

Raises:
    None

#### `_change_mode(self, pin: int, mode: str, feedback_label: ctk.CTkLabel)`

Cambia el modo de un pin y muestra feedback visual.

Args:
    pin (int): Número del pin a modificar.
    mode (str): Nuevo modo del pin.
    feedback_label (ctk.CTkLabel): Etiqueta para mostrar el resultado de la operación.

Returns:
    None

Raises:
    None

#### `_save_label(self, pin: int, entry: ctk.CTkEntry, feedback_label: ctk.CTkLabel)`

Guarda una nueva etiqueta para un pin específico y proporciona retroalimentación visual.

Args:
    pin (int): Número del pin.
    entry (ctk.CTkEntry): Campo de entrada con la nueva etiqueta.
    feedback_label (ctk.CTkLabel): Etiqueta para mostrar retroalimentación.

Returns:
    None

Raises:
    None

</details>
