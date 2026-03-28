# `core.ssh_monitor`

> **Ruta**: `core/ssh_monitor.py`

> **Cobertura de documentación**: 🟢 100% (14/14)

Monitor de sesiones SSH.
Recopila sesiones activas via `who` e historial via `last`.
Corre en thread daemon con refresco cada 30 segundos.

---

## Tabla de contenidos

**Clase [`SSHMonitor`](#clase-sshmonitor)**
  - [`start()`](#startself)
  - [`stop()`](#stopself)
  - [`is_running()`](#is_runningself-bool)
  - [`get_sessions()`](#get_sessionsself-list)
  - [`get_history()`](#get_historyself-list)
  - [`get_last_update()`](#get_last_updateself-str)
  - [`get_stats()`](#get_statsself-dict)

---

## Dependencias internas

- `utils.logger`

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

Ejecuta un comando y devuelve la salida estándar o una cadena vacía si falla.

Args:
    cmd (list): Lista de comando y argumentos a ejecutar.

Returns:
    str: Salida estándar del comando ejecutado.

Raises:
    Exception: Si ocurre un error durante la ejecución del comando.

### `_parse_who(raw: str) -> list`

Parsea la salida de `who` y devuelve una lista de diccionarios con información de sesión.

Args:
    raw (str): Salida de `who` a parsear.

Returns:
    list: Lista de diccionarios con claves "user", "tty", "date", "time" e "ip".

Raises:
    Ninguna excepción específica.

### `_parse_last(raw: str) -> list`

Parsea la salida de `last -n 50` y devuelve una lista de diccionarios con información de sesión.

Args:
    raw (str): La salida de `last -n 50` como cadena de texto.

Returns:
    list: Lista de diccionarios con claves "user", "tty", "ip" y "time_info".

Raises:
    Ninguna excepción es lanzada explícitamente.

</details>

## Clase `SSHMonitor`

Servicio de monitoreo de sesiones SSH activas e historial.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

Características:
* Inicializa flags de estado, evento de parada, bloqueo de threading y estructuras de datos vacías.
* No inicia el monitoreo automáticamente, requiere llamada explícita a start().

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_lock` | `threading.Lock()` |
| `_thread` | `None` |

### Métodos públicos

#### `start(self)`

Inicia el servicio de monitoreo en segundo plano.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

Nota: Si el servicio ya está ejecutándose, este método no tiene efecto.
El servicio se ejecuta en un hilo daemon y realiza una primera verificación inmediata,
posteriormente ejecuta verificaciones cada intervalo configurado.

#### `stop(self)`

Detiene el servicio de monitoreo SSH de manera limpia.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `is_running(self) -> bool`

Verifica si el servicio de monitoreo SSH está en ejecución.

Args:
    None

Returns:
    bool: True si el servicio está corriendo, False en caso contrario.

Raises:
    None

#### `get_sessions(self) -> list`

Retorna una lista de sesiones SSH activas actuales.

Args:
    Ninguno

Returns:
    list[dict]: Lista de diccionarios con información de sesiones SSH, 
                 cada diccionario contiene: "user", "tty", "date", "time", "ip".

Raises:
    Ninguno

#### `get_history(self) -> list`

Retorna el historial reciente de logins.

Args:
    Ninguno

Returns:
    list[dict]: Lista de diccionarios con información de los últimos logins. 
                 Cada diccionario contiene: "user" (str), "tty" (str), "ip" (str) y "time_info" (str).

Raises:
    Ninguno

#### `get_last_update(self) -> str`

Retorna el timestamp de la última actualización en formato HH:MM:SS.

Args:
    Ninguno

Returns:
    str: Fecha y hora de última actualización en formato "%H:%M:%S" o cadena vacía si no se ha actualizado.

Raises:
    Ninguno

#### `get_stats(self) -> dict`

Obtiene un snapshot completo de las estadísticas actuales del monitor SSH.

Args:
    Ninguno

Returns:
    dict: Un diccionario con las estadísticas, incluyendo "sessions", "history" y "last_update".

Raises:
    Ninguno

Notas: Si el bloqueo interno está ocupado, devuelve un diccionario vacío.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor SSH.

Configura flags de estado, evento de parada, bloqueo de threading y estructuras de datos vacías.
No inicia el monitoreo automáticamente, requiere llamada explícita a start().

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_loop(self)`

Ejecuta el bucle principal del thread de monitoreo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_poll(self)`

Realiza un ciclo de polling completo para obtener información de sesiones activas y historial.

Args: Ninguno

Returns: Ninguno

Raises: Exception - Si ocurre un error durante la ejecución, se registra en el log de errores.

</details>
