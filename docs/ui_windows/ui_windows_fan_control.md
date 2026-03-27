# `ui.windows.fan_control`

> **Ruta**: `ui/windows/fan_control.py`

Ventana de control de ventiladores

## Imports

```python
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox
from core.fan_controller import FanController
from core.system_monitor import SystemMonitor
from utils.file_manager import FileManager
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `FanControlWindow(ctk.CTkToplevel)`

Ventana de control de ventiladores y curvas PWM

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_fan_controller` | `fan_controller` |
| `_system_monitor` | `system_monitor` |
| `_fan_service` | `fan_service` |
| `_file_manager` | `FileManager()` |
| `_mode_var` | `tk.StringVar(master=self)` |
| `_manual_pwm_var` | `tk.IntVar(master=self, value=128)` |
| `_curve_vars` | `[]` |
| `_PLACEHOLDER_TEMP` | `'0-100'` |
| `_PLACEHOLDER_PWM` | `'0-255'` |
| `_new_temp_var` | `tk.StringVar(master=self, value=self._PLACEHOLDER_TEMP)` |
| `_new_pwm_var` | `tk.StringVar(master=self, value=self._PLACEHOLDER_PWM)` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, fan_controller: FanController, system_monitor: SystemMonitor, fan_service = None)`

Constructor de la ventana de control de ventiladores.

Inicializa dependencias, variables de estado, carga configuración previa,
configura geometría de ventana DSI y crea la UI completa.

Args:
    parent: Ventana padre (root).
    fan_controller: Instancia de FanController para control PWM.
    system_monitor: Instancia de SystemMonitor para lecturas temp.
    fan_service: Servicio opcional de ventiladores (puede ser None).

#### `_load_initial_state(self)`

Carga el estado inicial desde archivo

#### `_create_ui(self)`

Crea la interfaz de usuario

#### `_update_service_status(self)`

Muestra u oculta el aviso según si _fan_service está corriendo.

#### `_create_mode_section(self, parent)`

Crea la sección de selección de modo

#### `_create_manual_pwm_section(self, parent)`

Crea la sección de PWM manual

#### `_create_curve_section(self, parent)`

Crea la sección de curva temperatura-PWM

#### `_entry_focus_in(self, entry, var, placeholder)`

Maneja el evento de foco entrando en un campo de entrada.

Limpia el placeholder si está presente y ajusta el color del texto.

Args:
    entry: Widget CTkEntry que recibe el foco.
    var: Variable StringVar asociada al campo.
    placeholder: Texto placeholder original.

#### `_entry_focus_out(self, entry, var, placeholder)`

Maneja el evento de foco saliendo de un campo de entrada.

Restaura el placeholder si el campo está vacío.

Args:
    entry: Widget CTkEntry que pierde el foco.
    var: Variable StringVar asociada al campo.
    placeholder: Texto placeholder original.

#### `_add_curve_point_from_entries(self)`

Añade un nuevo punto a la curva temperatura-PWM desde los campos de entrada.

Valida rangos (temp 0-100, PWM 0-255), actualiza controlador, refresca UI
y muestra confirmación.

#### `_refresh_curve_points(self)`

Refresca la visualización de puntos de la curva.

Limpia frame actual, carga curva desde archivo y recrea labels/botones
para cada punto. Muestra mensaje si no hay puntos.

#### `_remove_curve_point(self, temp: int)`

Elimina un punto específico de la curva por temperatura.

Args:
    temp: Temperatura del punto a eliminar (int).

#### `_create_bottom_buttons(self, parent)`

Crea los botones inferiores de la interfaz.

Args:
    parent: Frame contenedor para los botones.

#### `_on_mode_change(self, mode: str)`

Callback al cambiar el modo de operación (Auto, Silent, etc.).

Calcula PWM objetivo basado en modo/temperatura actual, actualiza UI
y guarda estado.

Args:
    mode: Nuevo modo seleccionado ('auto', 'silent', etc.).

#### `_on_pwm_change(self, value)`

Callback al cambiar el valor del slider PWM manual.

Actualiza label de visualización y guarda estado si modo es 'manual'.

Args:
    value: Nuevo valor PWM del slider (float).

#### `_update_pwm_display(self)`

Actualización periódica (cada 2s) del display PWM.

Recalcula PWM basado en modo/temperatura actual si no es manual,
y programación recursiva.

</details>
