# `core.led_service`

> **Ruta**: `core/led_service.py`

> **Cobertura de documentación**: 🟢 100% (10/10)

Servicio de control de LEDs RGB del GPIO Board (Freenove FNK0100K).
El dashboard escribe led_state.json que fase1.py lee y aplica via I2C.

---

## Tabla de contenidos

**Clase [`LedService`](#clase-ledservice)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`get_state()`](#get_stateself-dict)
  - [`set_mode()`](#set_modeself-mode-str-r-int-0-g-int-255-b-int-0-bool)
  - [`set_color()`](#set_colorself-r-int-g-int-b-int-bool)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import json
import os
import threading
from pathlib import Path
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `LED_MODES` | `['auto', 'off', 'static', 'follow', 'breathing', 'rainbow']` |
| `LED_MODE_LABELS` | `{'auto': 'Auto (temperatura)', 'off': 'Apagado', 'static': 'Color fijo', 'follow...` |

## Clase `LedService`

Servicio para controlar los LEDs mediante archivo de estado.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_lock` | `threading.Lock()` |
| `_state` | `self._load()` |
| `_running` | `True` |

### Métodos públicos

#### `start(self) -> None`

Inicia el servicio de LED, habilitando el modo y el color.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `stop(self) -> None`

Detiene el servicio de LEDs, apagándolos y desactivando su funcionamiento.

Args: 
    None

Returns: 
    None

Raises: 
    None

#### `is_running(self) -> bool`

Indica si el servicio de LED está actualmente en ejecución.

Returns:
    bool: True si el servicio está activo, False en caso contrario.

#### `get_state(self) -> dict`

Obtiene el estado actual del LED de manera segura para hilos.

Args:
    Ninguno

Returns:
    dict: Un diccionario con el modo y valores de color RGB actuales, en el formato {'mode': str, 'r': int, 'g': int, 'b': int}

Raises:
    Ninguno

#### `set_mode(self, mode: str, r: int = 0, g: int = 255, b: int = 0) -> bool`

Cambia el modo del LED y los valores RGB, validándolos y guardando el estado en led_state.json de manera atómica.

Args:
    mode (str): El modo del LED, puede ser 'auto', 'off', 'static', etc. (ver LED_MODES).
    r (int): El valor del rojo, entre 0 y 255. Por defecto es 0.
    g (int): El valor del verde, entre 0 y 255. Por defecto es 255.
    b (int): El valor del azul, entre 0 y 255. Por defecto es 0.

Returns:
    bool: True si el estado se guardó correctamente.

Raises:
    None

#### `set_color(self, r: int, g: int, b: int) -> bool`

Establece el color del LED actualizando solo los componentes RGB.

Args:
    r (int): Componente rojo del color (0-255).
    g (int): Componente verde del color (0-255).
    b (int): Componente azul del color (0-255).

Returns:
    bool: True si el color se guardó correctamente.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el servicio de LED, cargando el estado desde el archivo led_state.json y configurando el bloqueo de ejecución.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_save(self, state: dict) -> bool`

Guarda el estado del LED de manera atómica en un archivo JSON.

Args:
    state (dict): El estado del LED a ser guardado.

Returns:
    bool: True si el estado se guardó correctamente, False en caso de error.

Raises:
    Exception: Si ocurre un error durante el proceso de guardado.

#### `_load(self) -> dict`

Carga el estado de la configuración de LED desde un archivo o retorna un estado por defecto.

Args:
    Ninguno

Returns:
    dict: Estado parseado del LED o un diccionario con valores por defecto {'mode':'auto','r':0,'g':255,'b':0}

Raises:
    Ninguno

</details>
