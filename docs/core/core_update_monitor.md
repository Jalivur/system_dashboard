# `core.update_monitor`

> **Ruta**: `core/update_monitor.py`

> **Cobertura de documentación**: 🟢 100% (6/6)

Monitor de actualizaciones del sistema.
Verifica paquetes pendientes via 'apt list --upgradable' con caché de 12h y lock thread-safe.
Ejecuta 'sudo apt update' solo cuando necesario (force o timeout caché).

---

## Tabla de contenidos

**Clase [`UpdateMonitor`](#clase-updatemonitor)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`check_updates()`](#check_updatesself-force-false-dict)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import subprocess
import time
import threading
from typing import Dict
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `UpdateMonitor`

Inicializa el monitor de actualizaciones.

Configura el estado de ejecución, un bloqueo para acceso concurrente, 
una caché inicial con estado desconocido y un intervalo de comprobación 
de 12 horas. No inicia hilos automáticos; requiere llamada explícita a start().

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_running` | `True` |
| `_lock` | `threading.Lock()` |
| `_last_check_time` | `time.time()` |
| `_cached_result` | `{'pending': 0, 'status': 'Unknown', 'message': 'No comprobado'}` |
| `_check_interval` | `43200` |

### Métodos públicos

#### `start(self) -> None`

Inicia el servicio de monitoreo de actualizaciones.

Args: 
    None

Returns: 
    None

Raises: 
    None

#### `stop(self) -> None`

Detiene el servicio de monitoreo de actualizaciones.

Args: 
    None

Returns: 
    None

Raises: 
    None

#### `is_running(self) -> bool`

Indica si el servicio de actualización está actualmente en ejecución.

Args:
    Ninguno

Returns:
    bool: True si el servicio está corriendo, False en caso contrario.

Raises:
    Ninguno

#### `check_updates(self, force = False) -> Dict`

Verifica actualizaciones pendientes del sistema con un mecanismo de caché.

Args:
    force (bool): Si True, ignora la caché y los intervalos de actualización, ejecutando 'apt update' inmediatamente.

Returns:
    Dict: Un diccionario con el número de paquetes actualizables, el estado de la actualización y un mensaje descriptivo.

Raises:
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor de actualizaciones.

Configura el estado de ejecución, bloqueo de acceso, caché inicial de resultado desconocido,
timestamp actual y un intervalo de comprobación de 12 horas. No inicia hilos automáticos,
requiere llamada explícita a start() para comenzar la monitorización.

</details>
