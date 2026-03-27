# `core.ssh_monitor`

> **Ruta**: `core/ssh_monitor.py`

Monitor de sesiones SSH.
Recopila sesiones activas via `who` e historial via `last`.
Corre en thread daemon con refresco cada 30 segundos.

## Imports

```python
import subprocess
import threading
from datetime import datetime
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

<details>
<summary>Funciones privadas</summary>

### `_run(cmd: list) -> str`

Ejecuta un comando y devuelve stdout o string vacío si falla.

### `_parse_who(raw: str) -> list`

Parsea la salida de `who` y devuelve lista de dicts.
Formato típico:
    jalivur  pts/0        2026-03-04 10:22 (192.168.1.10)

### `_parse_last(raw: str) -> list`

Parsea la salida de `last -n 50` y devuelve lista de dicts.
Formato típico:
    jalivur  pts/0   192.168.1.10  Tue Mar  4 10:22   still logged in
    jalivur  pts/1   192.168.1.10  Mon Mar  3 21:10 - 21:45  (00:35)

</details>

## Clase `SSHMonitor`

Servicio profesional de monitoreo de sesiones SSH activas e historial.

Características:
* Polling cada 30s de `who` (sesiones actuales) y `last -n 50` (historial reciente).
* Parsing robusto de formatos variable con extracción de user/tty/IP/tiempos.
* Thread daemon con lock para acceso concurrente seguro (thread-safe).
* Métodos start/stop/is_running para ciclo de vida.
* Getters optimizados: bloqueante y no-bloqueante (get_stats).
* Logging apropiado para debug/error.

Datos retornados:
- sessions: list[dict{"user", "tty", "date", "time", "ip"}]
- history: list[dict{"user", "tty", "ip", "time_info"}]

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_lock` | `threading.Lock()` |
| `_thread` | `None` |

### Métodos públicos

#### `start(self)`

Inicia el servicio de monitoreo en background (thread daemon).

Primera poll inmediata, luego cada _POLL_INTERVAL segs.
Idempotente: si ya corriendo, no hace nada.

#### `stop(self)`

Detiene el servicio limpiamente.

Setea evento stop, join thread (timeout 6s), limpia datos internos.
Logging de detención.

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo.

#### `get_sessions(self) -> list`

Retorna lista de sesiones SSH activas actuales (copia).

Returns:
    list[dict]: [{"user": str, "tty": str, "date": str, "time": str, "ip": str}, ...]

#### `get_history(self) -> list`

Retorna historial reciente de logins (últimas 50 entradas, copia).

Returns:
    list[dict]: [{"user": str, "tty": str, "ip": str, "time_info": str}, ...]

#### `get_last_update(self) -> str`

Retorna timestamp de última actualización (HH:MM:SS, copia).

Returns:
    str: Formato "%H:%M:%S" o vacío si no actualizado.

#### `get_stats(self) -> dict`

Lectura no bloqueante de snapshot completo — si lock ocupado devuelve datos vacíos.

Returns:
    dict: {"sessions": list, "history": list, "last_update": str}

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor SSH.

Configura flags de estado, event stop, lock threading y estructuras de datos vacías.
No inicia polling automáticamente — llamar start().

#### `_loop(self)`

Bucle principal del thread de monitoreo (privado).

Poll inicial inmediato + wait(POLL_INTERVAL) entre iteraciones.
Sale al detectar _stop_evt.

#### `_poll(self)`

Realiza un ciclo de polling completo (privado).

Ejecuta who/last, parsea, actualiza datos protegidos por lock.
Timestamp de última actualización.
Manejo de excepciones con log error.

</details>
