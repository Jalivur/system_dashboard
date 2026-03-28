# `core.gpio_monitor`

> **Ruta**: `core/gpio_monitor.py`

> **Cobertura de documentación**: 🟢 100% (28/28)

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

---

## Tabla de contenidos

**Clase [`GPIOMonitor`](#clase-gpiomonitor)**
  - [`start()`](#startself)
  - [`stop()`](#stopself)
  - [`is_running()`](#is_runningself-bool)
  - [`get_op_mode()`](#get_op_modeself-str)
  - [`set_op_mode()`](#set_op_modeself-mode-str-none)
  - [`get_state()`](#get_stateself-dictint-dict)
  - [`is_gpio_available()`](#is_gpio_availableself-bool)
  - [`get_pins()`](#get_pinsself-listint)
  - [`reserved_pins()`](#reserved_pins-setint)
  - [`set_output()`](#set_outputself-pin-int-high-bool-bool)
  - [`set_pwm()`](#set_pwmself-pin-int-duty-float-bool)
  - [`set_label()`](#set_labelself-pin-int-label-str-bool)
  - [`set_mode()`](#set_modeself-pin-int-mode-str-bool)
  - [`add_pin()`](#add_pinself-pin-int-mode-str-mode_input-label-str-bool)
  - [`remove_pin()`](#remove_pinself-pin-int-bool)

---

## Dependencias internas

- `config.local_settings_io`
- `utils.logger`

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

Carga la configuración de pines desde local_settings_io y devuelve un diccionario con pines como claves enteras y configuraciones como valores.

Args: 
    Ninguno

Returns:
    dict[int, dict]: Diccionario con pines como claves enteras y configuraciones como valores.

Raises:
    Ninguna excepción específica, aunque se registran warnings en caso de errores.

### `_save_config(pins_cfg: dict[int, dict]) -> None`

Persiste la configuración de pines en local_settings.py de manera segura.

Args:
    pins_cfg: Diccionario con configuración de pines, donde cada clave es un pin y cada valor es otro diccionario con la configuración.

Returns:
    None

Raises:
    Exception: Si ocurre un error al guardar la configuración.

</details>

## Clase `GPIOMonitor`

Gestiona el estado y configuración de pines GPIO.

La clase proporciona información sobre el estado de cada pin, incluyendo su modo (INPUT, OUTPUT o PWM), 
etiqueta descriptiva, valor actual y ciclo de trabajo en caso de PWM.

Args:
    config (dict, optional): Configuración de pines. Por defecto, carga configuración desde local_settings.
    op_mode (str): Modo de operación, OP_LIBRE o OP_CONTROLANDO.

Returns:
    None

Raises:
    None

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

Inicia el hilo daemon de monitoreo de GPIO con un intervalo de polling de 1 segundo.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `stop(self)`

Detiene el monitor de GPIO, liberando recursos y deteniendo el hilo de ejecución.

Args: None

Returns: None

Raises: None

#### `is_running(self) -> bool`

Indica si el monitor de GPIO está actualmente en ejecución.

Args:
    Ninguno

Returns:
    bool: True si el monitor está corriendo, False en caso contrario.

Raises:
    Ninguno

#### `get_op_mode(self) -> str`

Retorna el modo de operación actual del monitor GPIO.

Args:
    Ninguno

Returns:
    str: El modo de operación actual, OP_CONTROLANDO o OP_LIBRE.

Raises:
    Ninguno

#### `set_op_mode(self, mode: str) -> None`

Establece el modo de operación del monitor GPIO.

Args:
    mode (str): Modo de operación, puede ser OP_CONTROLANDO o OP_LIBRE.

Raises:
    None

Returns:
    None

#### `get_state(self) -> dict[int, dict]`

Obtiene un snapshot thread-safe del estado actual de todos los pines GPIO configurados.

Returns:
    dict[int, dict]: Un diccionario donde cada clave es un número de pin BCM y cada valor es otro diccionario con los detalles del estado del pin.

Raises:
    None

#### `is_gpio_available(self) -> bool`

Indica si gpiozero está disponible e importado.

Returns:
    bool: True si gpiozero está disponible.

Raises:
    None

#### `get_pins(self) -> list[int]`

Obtiene una lista de todos los pines BCM configurados, excluyendo los reservados.

Args:
    Ninguno

Returns:
    list[int]: Una lista de pines BCM ordenados.

Raises:
    Ninguno

#### `reserved_pins() -> set[int]`

Devuelve el conjunto de pines BCM reservados para uso de I2C, PWM y UART.

Returns:
    set[int]: Conjunto de pines BCM reservados.

#### `set_output(self, pin: int, high: bool) -> bool`

Establece el estado de salida de un pin GPIO en modo OUTPUT.

Args:
    pin (int): Número del pin GPIO en modo BCM.
    high (bool): Estado del pin, True para HIGH y False para LOW.

Returns:
    bool: True si el estado del pin se cambió correctamente.

Raises:
    Exception: Si ocurre un error al cambiar el estado del pin.

#### `set_pwm(self, pin: int, duty: float) -> bool`

Establece el ciclo de trabajo PWM en un pin específico.

Args:
    pin (int): Número de pin en modo BCM PWM.
    duty (float): Ciclo de trabajo PWM, entre 0.0 (apagado) y 1.0 (completo).

Returns:
    bool: True si el ciclo de trabajo PWM se estableció correctamente.

Raises:
    Exception: Si ocurre un error al establecer el valor PWM.

#### `set_label(self, pin: int, label: str) -> bool`

Establece una etiqueta descriptiva para un pin GPIO específico y persiste el cambio.

Args:
    pin (int): Número de pin BCM.
    label (str): Nueva etiqueta para el pin.

Returns:
    bool: True si la etiqueta se actualizó correctamente.

Raises:
    None

#### `set_mode(self, pin: int, mode: str) -> bool`

Establece el modo de un pin GPIO específico.

Args:
    pin (int): Número del pin GPIO en formato BCM.
    mode (str): Modo del pin, puede ser INPUT, OUTPUT o PWM.

Returns:
    bool: True si el modo del pin se ha cambiado correctamente.

Raises:
    None

#### `add_pin(self, pin: int, mode: str = MODE_INPUT, label: str = '') -> bool`

Añade un nuevo pin BCM a la configuración y estado persistente.

Args:
    pin (int): Número de pin BCM no reservado.
    mode (str): Modo inicial del pin (MODE_INPUT, MODE_OUTPUT o MODE_PWM).
    label (str): Etiqueta para el pin, por defecto "GPIO N".

Returns:
    bool: True si el pin fue añadido correctamente (no existía previamente).

Raises:
    None

#### `remove_pin(self, pin: int) -> bool`

Elimina un pin de la configuración del monitor GPIO.

Args:
    pin (int): Número del pin BCM a remover.

Returns:
    bool: True si el pin fue eliminado correctamente.

Raises:
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self, config: dict | None = None, op_mode: str = OP_LIBRE)`

Inicializa el monitor de GPIO con la configuración proporcionada.

Args:
    config (dict, optional): Configuración de pines. Por defecto, carga la configuración desde local_settings.
    op_mode (str): Modo de operación, puede ser OP_LIBRE o OP_CONTROLANDO.

Returns:
    None

Raises:
    None

#### `_init_state(self)`

Inicializa el estado de los pines GPIO de manera thread-safe.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_run(self)`

Ejecuta el bucle principal del thread daemon.

Setup dispositivos si se está controlando, sondea entradas cada segundo y maneja el evento de parada.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_import_gpiozero(self) -> bool`

Intenta importar el módulo gpiozero y configura el estado de disponibilidad de GPIO.

Args:
    Ninguno

Returns:
    bool: True si gpiozero se importa correctamente, False en caso contrario.

Raises:
    Ninguna excepción explícita, pero se registra un warning si gpiozero no está disponible.

#### `_setup_devices(self)`

Configura los dispositivos gpiozero (Button/LED/PWMLED) para todos los pines en el estado actual.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Excepciones durante la recreación de LGPIOFactory.

#### `_open_device(self, pin: int, mode: str, duty: float = 0.0)`

Abre un dispositivo GPIO según el modo especificado y lo registra para su uso posterior.

Args:
    pin (int): El número de pin GPIO a abrir.
    mode (str): El modo de funcionamiento del pin (INPUT, OUTPUT o PWM).
    duty (float, opcional): El valor de duty cycle para modo PWM (por defecto 0.0).

Returns:
    None

Raises:
    Exception: Si ocurre un error al abrir el dispositivo, se registra en el estado de error.

#### `_close_device(self, pin: int)`

Cierra el dispositivo GPIO asociado a un pin específico.

Args:
    pin (int): El número de pin GPIO a cerrar.

Returns:
    None

Raises:
    None

#### `_release_devices(self)`

Cierra todos los dispositivos gpiozero y el factory lgpio.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Excepción genérica si falla el cierre del factory lgpio.

#### `_poll_inputs(self)`

Actualiza de forma segura el estado de los pines de entrada de la GPIO.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Excepciones relacionadas con la lectura de los dispositivos GPIO.

#### `_persist(self) -> None`

Persiste una captura de la configuración actual de los pines en local_settings de manera segura para hilos concurrentes.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
