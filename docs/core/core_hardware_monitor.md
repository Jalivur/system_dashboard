# `core.hardware_monitor`

> **Ruta**: `core/hardware_monitor.py`

> **Cobertura de documentación**: 🟢 100% (9/9)

Monitor de hardware del GPIO Board (Freenove FNK0100K).
Lee hardware_state.json que escribe fase1.py cada 5s.
Expone: temperatura del chasis, duty% real de cada fan.

---

## Tabla de contenidos

**Clase [`HardwareMonitor`](#clase-hardwaremonitor)**
  - [`start()`](#startself)
  - [`stop()`](#stopself)
  - [`is_running()`](#is_runningself-bool)
  - [`get_stats()`](#get_statsself-dict)
  - [`is_available()`](#is_availableself-bool)

---

## Dependencias internas

- `utils.logger`

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

Monitoriza el estado del hardware leyendo periódicamente el archivo hardware_state.json.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

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

Inicia el hilo daemon para sondear el estado del hardware cada 6 segundos.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `stop(self)`

Detiene el monitor de hardware y limpia la caché de datos.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `is_running(self) -> bool`

Indica si el servicio de monitoreo de hardware está en ejecución.

Args:
    None

Returns:
    bool: True si el servicio está corriendo, False en caso contrario.

Raises:
    None

#### `get_stats(self) -> dict`

Retorna el estado actual del hardware, incluyendo temperatura del chasis y porcentajes de ventiladores.

Args:
    Ninguno

Returns:
    dict: Un diccionario con el estado actual del hardware, incluyendo 'chassis_temp', 'fan0_pct' y 'available'.

Raises:
    Ninguno

#### `is_available(self) -> bool`

Indica si el hardware está disponible según el estado actualizado recientemente.

Args:
    Ninguno

Returns:
    bool: True si el hardware está disponible, False en caso contrario.

Raises:
    Ninguno

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor de hardware.

Configura el estado inicial del monitor, incluyendo la creación de un bloqueo interno para asegurar la seguridad en hilos,
y la inicialización de los datos de estado del hardware.

Args:
    None

Returns:
    None

Raises:
    None

#### `_loop(self)`

Ejecuta un bucle en un hilo daemon que sondea cada 6 segundos hasta ser detenido.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_poll(self)`

Actualiza la información de estado del hardware leyendo el archivo hardware_state.json.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

</details>
