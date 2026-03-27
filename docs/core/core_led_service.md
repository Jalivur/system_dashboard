# `core.led_service`

> **Ruta**: `core/led_service.py`

Servicio de control de LEDs RGB del GPIO Board (Freenove FNK0100K).
El dashboard escribe led_state.json que fase1.py lee y aplica via I2C.

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

Escribe led_state.json para controlar los LEDs via fase1.py.
No tiene thread permanente — escritura directa al pulsar en la UI.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_lock` | `threading.Lock()` |
| `_state` | `self._load()` |
| `_running` | `True` |

### Métodos públicos

#### `start(self) -> None`

Activa el servicio (habilita set_mode/set_color).

#### `stop(self) -> None`

Apaga los LEDs y desactiva el servicio.

#### `is_running(self) -> bool`

Estado del servicio.

Returns:
    bool: True si activo.

#### `get_state(self) -> dict`

Lee estado actual thread-safe (modo/color).

Returns:
    dict: {'mode': str, 'r': int, 'g': int, 'b': int}

#### `set_mode(self, mode: str, r: int = 0, g: int = 255, b: int = 0) -> bool`

Cambia modo LED y RGB, valida, guarda led_state.json atomically.

Args:
    mode (str): 'auto'|'off'|'static'|... (LED_MODES)
    r, g, b (int): Colores 0-255 clamped.

Returns:
    bool: True si guardado OK.

#### `set_color(self, r: int, g: int, b: int) -> bool`

Actualiza solo RGB manteniendo modo actual.

Args:
    r, g, b (int): Colores 0-255 clamped.

Returns:
    bool: True si guardado OK (via set_mode).

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Constructor: carga estado desde led_state.json, inicializa lock.

#### `_save(self, state: dict) -> bool`

Guarda estado atomically a data/led_state.json (.tmp → replace).

Returns:
    bool: True si escrito OK.

#### `_load(self) -> dict`

Carga led_state.json o retorna default.

Returns:
    dict: Estado parseado o {'mode':'auto','r':0,'g':255,'b':0}

</details>
