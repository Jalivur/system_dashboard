# `core.hardware_monitor`

> **Ruta**: `core/hardware_monitor.py`

Monitor de hardware del GPIO Board (Freenove FNK0100K).
Lee hardware_state.json que escribe fase1.py cada 5s.
Expone: temperatura del chasis, duty% real de cada fan.

## Imports

```python
import json
import threading
import time
from pathlib import Path
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `HardwareMonitor`

Lee hardware_state.json en background cada 6s.
El fichero lo escribe fase1.py cada 5s.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_lock` | `threading.Lock()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_thread` | `None` |
| `_data` | `{'chassis_temp': None, 'fan0_pct': None, 'fan1_pct': None, 'available': False}` |

### Métodos públicos

#### `start(self)`

Inicia thread daemon de polling hardware_state.json cada 6s.

#### `stop(self)`

Detiene el thread de polling, limpia cache.

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo.

#### `get_stats(self) -> dict`

Retorna estado hardware actual (temp chassis, % fans).

Returns:
    dict: {'chassis_temp': float, 'fan0_pct': int, ... 'available': bool}

#### `is_available(self) -> bool`

True si hardware_state.json existe y actualizado <30s (fase1 corriendo).

Returns:
    bool: Datos válidos.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa monitor hardware (GPIO board Freenove).

Cache interno thread-safe para chassis_temp, fans %.

#### `_loop(self)`

Bucle thread daemon: poll cada 6s hasta stop().

#### `_poll(self)`

Lee hardware_state.json escrito por fase1.py, valida antigüedad <30s, actualiza cache thread-safe si válido.

</details>
