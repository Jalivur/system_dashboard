# `core.gpio_monitor`

> **Ruta**: `core/gpio_monitor.py`

Controlador de pines GPIO via gpiozero.

Soporta tres modos por pin:
  INPUT  — lectura de estado (Button sin pull interno)
  OUTPUT — escritura HIGH/LOW (LED de gpiozero)
  PWM    — señal PWM con duty cycle 0.0–1.0 (PWMLED de gpiozero)

Modos de operación globales:
  CONTROLANDO — dashboard reclama los pines con gpiozero.
                INPUT/OUTPUT/PWM operativos.
  LIBRE       — dashboard libera todos los pines (gpiozero cerrado).
                Los scripts externos pueden usar los pines sin conflictos.
                No se lee ningún estado de hardware.

Persistencia:
  La configuración de pines se guarda en local_settings.py via
  local_settings_io bajo la clave "gpio_pins_config".
  Formato: {bcm_pin_str: {"mode": str, "label": str}}
  Si no existe la clave se usa _DEFAULT_CONFIG.

Pines reservados por fase1.py — nunca tocar:
  I²C : GPIO 2 (SDA), 3 (SCL)
  PWM : GPIO 12, 13, 18, 19 (hardware PWM ventiladores)
  UART: GPIO 14, 15

## Imports

```python
import threading
import gpiozero
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
from config.local_settings_io import update_params, read
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `MODE_INPUT` | `'INPUT'` |
| `MODE_OUTPUT` | `'OUTPUT'` |
| `MODE_PWM` | `'PWM'` |
| `VALID_MODES` | `(MODE_INPUT, MODE_OUTPUT, MODE_PWM)` |
| `OP_CONTROLANDO` | `'CONTROLANDO'` |
| `OP_LIBRE` | `'LIBRE'` |

<details>
<summary>Funciones privadas</summary>

### `_load_config() -> dict[int, dict]`

Carga la configuración de pines desde local_settings_io.
Si no existe la clave devuelve _DEFAULT_CONFIG.
Las claves se almacenan como strings — se convierten a int.

### `_save_config(pins_cfg: dict[int, dict]) -> None`

Persiste la configuración en local_settings.py via update_params.
Merge seguro — no machaca otras claves del fichero.

</details>

## Clase `GPIOMonitor`

Gestiona pines GPIO con soporte INPUT, OUTPUT y PWM.

Estado por pin:
  {
    "mode":  str        — INPUT | OUTPUT | PWM
    "label": str        — etiqueta descriptiva
    "value": bool|None  — estado leído/escrito; None si LIBRE
    "duty":  float      — PWM duty cycle 0.0–1.0; 0.0 en otros modos
    "error": str|None   — mensaje de error o None
  }

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_lock` | `threading.Lock()` |
| `_stop_evt` | `threading.Event()` |
| `_running` | `False` |
| `_op_mode` | `op_mode` |
| `_gpio_available` | `False` |
| `_gz` | `None` |

### Métodos públicos

#### `start(self)`

Inicia thread daemon de polling GPIO (1s intervalo).

Setup devices si OP_CONTROLANDO.

#### `stop(self)`

Detiene thread, libera dispositivos gpiozero, cierra factory LGPIO.

Espera 5s join max, _running=False.

#### `is_running(self) -> bool`

Retorna estado del monitor (thread activo).

Returns:
    bool: True si corriendo.

#### `get_op_mode(self) -> str`

Retorna modo de operación actual.

Returns:
    str: OP_CONTROLANDO o OP_LIBRE.

#### `set_op_mode(self, mode: str) -> None`

Cambia modo operación. LIBRE libera dispositivos, CONTROLANDO los reclama.

Args:
    mode (str): OP_CONTROLANDO o OP_LIBRE.

#### `get_state(self) -> dict[int, dict]`

Snapshot thread-safe del estado de todos los pines GPIO configurados.

Returns:
    dict[int, dict]: Estado por BCM pin.

#### `is_gpio_available(self) -> bool`

Indica si gpiozero está disponible e importado.

Returns:
    bool: True si Pi5+lgpio OK.

#### `get_pins(self) -> list[int]`

Lista de todos los pines BCM configurados (excluye reservados).

Returns:
    list[int]: Pines BCM ordenados.

#### `reserved_pins() -> set[int]`

Pines BCM reservados por fase1.py (I2C/PWM/UART).

Returns:
    set[int]: {2,3,12,13,14,15,18,19}

#### `set_output(self, pin: int, high: bool) -> bool`

Establece salida OUTPUT HIGH/LOW en pin BCM.

Args:
    pin (int): BCM pin en modo OUTPUT.
    high (bool): True=ON/HIGH, False=OFF/LOW.

Returns:
    bool: True si cambiado correctamente.

#### `set_pwm(self, pin: int, duty: float) -> bool`

Establece duty cycle PWM (0.0-1.0) en pin BCM PWMLED.

Args:
    pin (int): BCM pin en modo PWM.
    duty (float): 0.0=off, 1.0=full, clamped.

Returns:
    bool: True si seteado correctamente.

#### `set_label(self, pin: int, label: str) -> bool`

Cambia etiqueta descriptiva del pin (persiste).

Args:
    pin (int): BCM pin.
    label (str): Nueva etiqueta.

Returns:
    bool: True si actualizado.

#### `set_mode(self, pin: int, mode: str) -> bool`

Cambia modo del pin (INPUT/OUTPUT/PWM), persiste, recrea device si controlando.

Args:
    pin (int): BCM pin.
    mode (str): MODE_INPUT/OUTPUT/PWM.

Returns:
    bool: True si cambiado.

#### `add_pin(self, pin: int, mode: str = MODE_INPUT, label: str = '') -> bool`

Añade nuevo pin BCM a configuración y state (persiste).

Args:
    pin (int): BCM pin no reservado.
    mode (str): Inicial MODE_INPUT/OUTPUT/PWM.
    label (str): Etiqueta o "GPIO N".

Returns:
    bool: True si añadido (no existía).

#### `remove_pin(self, pin: int) -> bool`

Elimina pin de configuración, cierra device, persiste.

Args:
    pin (int): BCM pin a remover.

Returns:
    bool: True si eliminado (existía).

<details>
<summary>Métodos privados</summary>

#### `__init__(self, config: dict | None = None, op_mode: str = OP_LIBRE)`

Inicializa monitor GPIO.

Args:
    config (dict, optional): Config pines. Defaults _load_config().
    op_mode (str): OP_LIBRE o OP_CONTROLANDO.

Configura locks, state, carga pins desde local_settings.

#### `_init_state(self)`

Inicializa dict _state thread-safe con modos/labels desde _pins_cfg.

#### `_run(self)`

Bucle principal thread daemon.

Setup devices si controlando, poll inputs 1s, maneja stop_evt.

#### `_import_gpiozero(self) -> bool`

Importa gpiozero module, set _gz y _gpio_available.
Error: set state error todos pins.

Returns:
    bool: True si disponible.

#### `_setup_devices(self)`

Crea/abre gpiozero devices (Button/LED/PWMLED) para todos pines en state.
Recrear LGPIOFactory si cerrado.

#### `_open_device(self, pin: int, mode: str, duty: float = 0.0)`

Crea gpiozero device según mode:
INPUT: Button(pull_up=None)
OUTPUT: LED(off)
PWM: PWMLED(value=duty clamped 0-1)

Catch exceptions → state error.

#### `_close_device(self, pin: int)`

Cierra gpiozero device (call dev.close()), remove de _devices.
Silencioso exceptions.

#### `_release_devices(self)`

Cleanup total: close devices + LGPIOFactory.close() + None states.

#### `_poll_inputs(self)`

Lee is_active Button INPUT pins → state['value'] thread-safe snapshot.

#### `_persist(self) -> None`

Persiste _pins_cfg snapshot en local_settings thread-safe.

</details>
