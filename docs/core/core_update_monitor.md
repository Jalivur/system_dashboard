# `core.update_monitor`

> **Ruta**: `core/update_monitor.py`

Monitor de actualizaciones del sistema.
Verifica paquetes pendientes via 'apt list --upgradable' con caché de 12h y lock thread-safe.
Ejecuta 'sudo apt update' solo cuando necesario (force o timeout caché).

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

Monitor profesional de actualizaciones APT con sistema de caché inteligente.

Características:
* Caché de 12 horas (_check_interval) para evitar consultas frecuentes.
* Thread-safe con lock para acceso concurrente.
* Ejecución real de 'sudo apt update' solo si force=True o caché expirada.
* Conteo preciso de paquetes upgradable ignorando headers.
* Manejo completo de errores (timeout, apt no encontrado, parse, etc.).
* Estados: Ready/Updated/Error/Stopped con mensajes descriptivos.

Uso: monitor.check_updates(force=False) → dict{pending, status, message}

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

Inicia el servicio (setea running=True).

Logging de inicio. Idempotente.

#### `stop(self) -> None`

Detiene el servicio.

Setea running=False, resetea caché a 'Servicio parado'. Logging.

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo.

#### `check_updates(self, force = False) -> Dict`

Verifica actualizaciones pendientes con sistema de caché.

Args:
    force (bool): Si True, ignora caché e intervalos — ejecuta apt update inmediatamente.

Returns:
    Dict: {
        "pending": int (número de paquetes upgradable),
        "status": str ("Ready", "Updated", "Error", "Stopped"),
        "message": str (descriptivo)
    }

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor de actualizaciones.

Configura estado corriendo, lock, caché inicial 'Unknown', timestamp actual,
intervalo de 12h. No inicia threads automáticos — llamar start().

</details>
