# `ui.windows.gpio_window`

> **Ruta**: `ui/windows/gpio_window.py`

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

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_monitor` | `gpio_monitor` |
| `_op_job` | `None` |

### Métodos públicos

#### `destroy(self)`

Destruye la ventana limpiamente, logueando el cierre.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, gpio_monitor)`

Inicializa la ventana principal de monitorización y control de pines GPIO.

Args:
    parent: Widget padre (CTkToplevel).
    gpio_monitor: Instancia del monitor GPIO para interactuar con el hardware.

Configura la geometría para pantalla DSI, crea la interfaz de usuario completa,
inicializa componentes internos y lanza el bucle de actualización automática.

#### `_create_ui(self)`

Crea todos los widgets y estructura de la interfaz de usuario.

Construye header, barra de modo de operación, área scrollable con canvas,
filas de pines dinámicas, footer con estado y botón de configuración.

#### `_toggle_op_mode(self)`

Alterna el modo de operación entre LIBRE y CONTROLANDO.

Lanza el cambio en thread daemon para no bloquear la UI y programa
actualización de la barra en 200ms.

#### `_on_op_mode_changed(self)`

Callback ejecutado tras cambio de modo de operación.

Actualiza la barra de operación y reconstruye las filas si la ventana existe.

#### `_update_op_bar(self)`

Actualiza visualmente la barra de modo de operación.

Reconfigura labels y botón según el estado actual del monitor.

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

Construye o reconstruye todas las filas de pines en el canvas interno.

Limpia widgets existentes, crea filas nuevas basadas en el estado actual del monitor.
Maneja casos especiales como ausencia de pines o modo LIBRE con mensajes informativos.

#### `_create_pin_row(self, pin: int, data: dict, is_libre: bool)`

Crea una fila completa para un pin específico en el canvas.

Args:
    pin (int): Número del pin GPIO.
    data (dict): Estado actual del pin del monitor.
    is_libre (bool): Si el modo de operación es LIBRE.

Crea indicador visual, etiqueta, badge de modo y controles contextuales (toggle, slider).

#### `_update(self)`

Bucle principal de actualización de estado en tiempo real.

Se ejecuta cada _REFRESH_MS. Verifica servicio, reconstruye si cambios estructurales,
actualiza indicadores, estados y controles sin recrear widgets.

#### `_toggle_output(self, pin: int)`

Alterna el estado HIGH/LOW de un pin en modo OUTPUT.

Args:
    pin (int): Número del pin.

Lanza el comando en thread daemon, actualiza UI reactivamente.

#### `_on_pwm_slide(self, pin: int, val: float)`

Manejador de slider PWM: aplica duty cycle.

Args:
    pin (int): Número del pin PWM.
    val (float): Valor del slider (0-100).

Actualiza label duty inmediato y lanza comando en thread.

#### `_status_text(self, state: dict) -> str`

Genera texto resumido del estado para el footer.

Args:
    state (dict): Diccionario de estado de todos los pines.

Returns:
    str: Resumen como 'CTRL · 4 pines · 2 IN · 1 OUT · 1 PWM'.

#### `_open_config(self)`

Abre el diálogo de configuración de pines.

#### `_on_config_closed(self)`

Callback ejecutado al cerrar el diálogo de configuración.

Reconstruye las filas de pines para reflejar cambios.

</details>

## Clase `_GPIOConfigDialog(ctk.CTkToplevel)`

Panel para añadir, eliminar y reconfigurar pines GPIO.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_monitor` | `gpio_monitor` |
| `_on_close` | `on_close` |

### Métodos públicos

#### `destroy(self) -> None`

Cierra el diálogo y ejecuta callback si existe.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, gpio_monitor, on_close = None)`

Inicializa el diálogo de configuración de pines.

Args:
    parent: Ventana padre.
    gpio_monitor: Instancia del monitor.
    on_close (callable, optional): Callback al cerrar.

#### `_create_ui(self)`

Crea la interfaz del diálogo de configuración.

#### `_build_list(self)`

Reconstruye la lista de pines configurados en el diálogo.

#### `_create_list_row(self, pin: int, data: dict)`

Crea fila editable para un pin en la lista de configuración.

Args:
    pin (int): Pin.
    data (dict): Datos del pin.

#### `_add_pin(self)`

Añade un nuevo pin con modo y etiqueta especificados.

#### `_remove_pin(self, pin: int)`

Elimina un pin de la configuración.

Args:
    pin (int): Pin a eliminar.

#### `_change_mode(self, pin: int, mode: str, feedback_label: ctk.CTkLabel)`

Cambia el modo de un pin y muestra feedback visual.

Args:
    pin (int): Pin.
    mode (str): Nuevo modo.
    feedback_label: Label para mostrar OK/ERR.

#### `_save_label(self, pin: int, entry: ctk.CTkEntry, feedback_label: ctk.CTkLabel)`

Guarda nueva etiqueta para un pin con feedback.

Args:
    pin (int): Pin.
    entry: Entry con nueva etiqueta.
    feedback_label: Label para feedback.

</details>
