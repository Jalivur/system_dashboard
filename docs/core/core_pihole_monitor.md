# `core.pihole_monitor`

> **Ruta**: `core/pihole_monitor.py`

> **Cobertura de documentación**: 🟢 100% (17/17)

Monitor de Pi-hole v6.
Sondea la API REST de Pi-hole v6 cada POLL_INTERVAL_S segundos.
Credenciales leídas desde .env: PIHOLE_HOST, PIHOLE_PORT, PIHOLE_PASSWORD.

Sin dependencias nuevas — usa urllib de la stdlib.

---

## Tabla de contenidos

**Clase [`PiholeMonitor`](#clase-piholemonitor)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`fetch_now()`](#fetch_nowself-none)
  - [`get_stats()`](#get_statsself-dict)
  - [`is_reachable()`](#is_reachableself-bool)
  - [`is_enabled()`](#is_enabledself-bool)
  - [`get_offline_count()`](#get_offline_countself-int)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import json
import os
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Optional
from utils.logger import get_logger
from dotenv import load_dotenv
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `PIHOLE_HOST` | `os.environ.get('PIHOLE_HOST', '')` |
| `PIHOLE_PORT` | `int(os.environ.get('PIHOLE_PORT', '80'))` |
| `PIHOLE_PASSWORD` | `os.environ.get('PIHOLE_PASSWORD', '')` |
| `POLL_INTERVAL_S` | `60` |
| `REQUEST_TIMEOUT` | `5` |
| `SESSION_VALIDITY` | `1800` |

<details>
<summary>Funciones privadas</summary>

### `_load_env()`

Carga las variables de entorno desde el archivo .env del proyecto.

Args: 
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>

## Clase `PiholeMonitor`

Inicializa el monitor de Pi-hole con sus configuraciones y locks.

Configura las estadísticas iniciales, los locks para thread-safety,
y verifica si PIHOLE_HOST está configurado en las variables de entorno.
Si no está configurado, el monitor permanece desactivado.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_stats_lock` | `threading.Lock()` |
| `_sid_lock` | `threading.Lock()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |

### Métodos públicos

#### `start(self) -> None`

Inicia el monitor de Pi-hole en un thread daemon.

Args:
    None

Returns:
    None

Raises:
    None

#### `stop(self) -> None`

Detiene el monitor de Pi-hole de forma ordenada.

Args:
    None

Returns:
    None

Raises:
    None

#### `is_running(self) -> bool`

Indica si el monitor de Pi-hole está en ejecución.

Args:
    Ninguno

Returns:
    bool: True si el monitor está activo, False en caso contrario.

#### `fetch_now(self) -> None`

Fuerza un sondeo inmediato de Pi-hole en un hilo separado sin bloquear la llamada.

Args: Ninguno

Returns: None

Raises: Ninguna excepción

Nota: Si el monitor no está en ejecución, esta llamada no tiene efecto.

#### `get_stats(self) -> Dict`

Devuelve las estadísticas de Pi-hole almacenadas en caché.

Args:
    None

Returns:
    Dict: Diccionario con estadísticas de consultas, bloqueos,
          dominios bloqueados, clientes únicos y estado de conexión.
          Devuelve estadísticas vacías si el monitor está parado.

Raises:
    None

#### `is_reachable(self) -> bool`

Indica si Pi-hole está alcanzable en la red.

Args:
    None

Returns:
    bool: True si Pi-hole está alcanzable.

Raises:
    None

#### `is_enabled(self) -> bool`

Verifica si el bloqueo de Pi-hole está activado.

Args:
    Ninguno

Returns:
    bool: True si el estado de Pi-hole es 'enabled'.

Raises:
    Ninguna excepción relevante.

#### `get_offline_count(self) -> int`

Obtiene el número de instancias de Pi-hole que se encuentran fuera de línea.

Args:
    Ninguno

Returns:
    int: 1 si Pi-hole no responde, 0 si está en línea.

Raises:
    Ninguno

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor de Pi-hole con sus configuraciones y locks.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_poll_loop(self) -> None`

Ejecuta el bucle principal del hilo daemon de sondeo periódico.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_authenticate(self) -> bool`

Establece una sesión autenticada con el servidor Pi-hole obteniendo un sid.

Args: 
    Ninguno

Returns:
    bool: True si la autenticación es exitosa, False en caso contrario.

Raises:
    Ninguna excepción específica, pero registra errores en el logger.

#### `_sid_valid(self) -> bool`

Verifica si el token de sesión sigue siendo válido.

Args: 
    Ninguno

Returns:
    bool: True si el sid existe y no ha expirado con margen de 60 segundos.

Raises:
    Ninguno

#### `_get_sid(self) -> Optional[str]`

Obtiene un sid válido, realizando autenticación si es necesario.

Args: Ninguno

Returns: El sid válido o None si no se pudo obtener.

Raises: Ninguna excepción específica

#### `_logout(self) -> None`

Cierra la sesión en Pi-hole invalidando el token de sesión actual.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_fetch(self) -> None`

Llama a la API v6 de Pi-hole y actualiza la caché de estadísticas.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Excepciones relacionadas con urllib.request y json.loads si la solicitud o el parseo falla.

</details>
