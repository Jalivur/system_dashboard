# `ui.windows.fan_control`

> **Ruta**: `ui/windows/fan_control.py`

> **Cobertura de documentación**: 🟢 100% (17/17)

Ventana de control de ventiladores

---

## Tabla de contenidos

**Clase [`FanControlWindow`](#clase-fancontrolwindow)**

---

## Dependencias internas

- `config.settings`
- `core.fan_controller`
- `core.system_monitor`
- `ui.styles`
- `ui.widgets`
- `utils.file_manager`
- `utils.logger`

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

Ventana de control de ventiladores y curvas PWM.

Args:
    parent: Ventana padre (root).
    fan_controller: Instancia de FanController para control PWM.
    system_monitor: Instancia de SystemMonitor para lecturas de temperatura.
    fan_service: Servicio opcional de ventiladores (puede ser None).

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

Inicializa la ventana de control de ventiladores con dependencias y configuración.

Args:
    parent: Ventana padre (root).
    fan_controller: Instancia de FanController para control PWM.
    system_monitor: Instancia de SystemMonitor para lecturas de temperatura.
    fan_service: Servicio opcional de ventiladores (puede ser None).

Returns:
    None

Raises:
    None

#### `_load_initial_state(self)`

Carga el estado inicial de la ventana de control del ventilador desde archivo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_ui(self)`

Crea la interfaz de usuario de la ventana de control de ventiladores.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update_service_status(self)`

Actualiza el estado de la notificación de servicio según el estado del servicio de ventilador.

Args:
    None

Returns:
    None

Raises:
    None

#### `_create_mode_section(self, parent)`

Crea la sección de selección de modo en la ventana de control del ventilador.

Args:
    parent: El contenedor padre donde se creará la sección de selección de modo.

Returns:
    None

Raises:
    None

#### `_create_manual_pwm_section(self, parent)`

Crea la sección de PWM manual en la ventana de control del ventilador.

Args:
    parent: El elemento padre en el que se creará la sección.

Returns:
    None

Raises:
    None

#### `_create_curve_section(self, parent)`

Crea la sección de curva temperatura-PWM en la ventana de control del ventilador.

Args:
    parent: El elemento padre en el que se creará la sección.

Returns:
    None

Raises:
    None

#### `_entry_focus_in(self, entry, var, placeholder)`

Maneja el evento de foco entrando en un campo de entrada.

Limpia el placeholder si está presente y ajusta el color del texto.

Args:
    entry: Widget CTkEntry que recibe el foco.
    var: Variable StringVar asociada al campo.
    placeholder: Texto placeholder original.

Returns:
    None

Raises:
    None

#### `_entry_focus_out(self, entry, var, placeholder)`

Restaura el texto placeholder en un campo de entrada cuando pierde el foco y está vacío.

Args:
    entry: Widget CTkEntry que pierde el foco.
    var: Variable StringVar asociada al campo.
    placeholder: Texto placeholder original.

Returns:
    None

Raises:
    None

#### `_add_curve_point_from_entries(self)`

Añade un nuevo punto a la curva temperatura-PWM desde los campos de entrada.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

Nota: Valida rangos (temp 0-100, PWM 0-255), actualiza controlador, refresca UI y muestra confirmación.

#### `_refresh_curve_points(self)`

Refresca la visualización de puntos de la curva en la ventana de control.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_remove_curve_point(self, temp: int)`

Elimina un punto específico de la curva por temperatura.

Args:
    temp (int): Temperatura del punto a eliminar.

Raises:
    Exception: Si el punto no existe en la curva.

Returns:
    None

#### `_create_bottom_buttons(self, parent)`

Crea los botones inferiores de la interfaz de control de ventilador.

Args:
    parent: Frame contenedor para los botones.

Returns:
    None

Raises:
    None

#### `_on_mode_change(self, mode: str)`

Actualiza el control de ventilador al cambiar el modo de operación.

Args:
    mode (str): Nuevo modo seleccionado.

Raises:
    None

#### `_on_pwm_change(self, value)`

Actualiza la interfaz y guarda el estado al cambiar el valor del PWM manual.

Args:
    value (float): Nuevo valor PWM del slider.

Raises:
    Ninguna excepción relevante.

#### `_update_pwm_display(self)`

Actualiza periódicamente el display PWM cada 2 segundos.

Recalcula el valor PWM según el modo y temperatura actuales si no está en modo manual.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

</details>
