# `core.pihole_monitor`

> **Ruta**: `core/pihole_monitor.py`

Monitor de Pi-hole v6.
Sondea la API REST de Pi-hole v6 cada POLL_INTERVAL_S segundos.
Credenciales leídas desde .env: PIHOLE_HOST, PIHOLE_PORT, PIHOLE_PASSWORD.

Sin dependencias nuevas — usa urllib de la stdlib.

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

Busca el archivo .env en el directorio padre del módulo actual.
Intenta usar python-dotenv si está disponible; si no, realiza
el parsing manual del archivo línea por línea.

</details>

## Clase `PiholeMonitor`

Monitor de Pi-hole v6 con sondeo en background.
Autenticación por sesión (sid) con renovación automática antes de expirar.

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

No hace nada si ya está corriendo o si PIHOLE_HOST no está configurado.

#### `stop(self) -> None`

Detiene el monitor de Pi-hole de forma ordenada.

Señaliza la parada al thread de sondeo, espera a que termine,
cierra la sesión en Pi-hole y limpia las estadísticas en caché.

#### `is_running(self) -> bool`

Estado del monitor de Pi-hole.

Returns:
    bool: True si el thread de sondeo está activo.

#### `fetch_now(self) -> None`

Fuerza sondeo inmediato de Pi-hole en thread separado (non-blocking).

No bloquea el caller.

#### `get_stats(self) -> Dict`

Devuelve las estadísticas de Pi-hole almacenadas en caché.

No realiza ninguna petición HTTP, solo devuelve los datos
del último sondeo realizado por el thread de fondo.

Returns:
    Dict: Diccionario con estadísticas de consultas, bloqueos,
          dominios bloqueados, clientes únicos y estado de conexión.
          Devuelve estadísticas vacías si el monitor está parado.

#### `is_reachable(self) -> bool`

Indica si Pi-hole está alcanzable en la red.

Returns:
    bool: True si la última conexión con Pi-hole fue exitosa.

#### `is_enabled(self) -> bool`

Verifica si el bloqueo de Pi-hole está activado.

Returns:
    bool: True si el estado de Pi-hole es 'enabled'.

#### `get_offline_count(self) -> int`

Para badge: 1 si Pi-hole no responde, 0 si ok.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor de Pi-hole con sus configuraciones y locks.

Configura las estadísticas iniciales, los locks para thread-safety,
y verifica si PIHOLE_HOST está configurado en las variables de entorno.
Si no está configurado, el monitor permanece desactivado.

#### `_poll_loop(self) -> None`

Bucle principal del thread daemon de sondeo periódico.

#### `_authenticate(self) -> bool`

Obtiene un sid de sesión. Devuelve True si tiene éxito.

#### `_sid_valid(self) -> bool`

Verifica si el token de sesión (sid) sigue siendo válido.

Returns:
    bool: True si el sid existe y no ha expirado (con margen de 60s).

#### `_get_sid(self) -> Optional[str]`

Devuelve el sid válido, autenticando si es necesario.

#### `_logout(self) -> None`

Cierra la sesión en Pi-hole al parar el monitor.

Envía una petición DELETE a la API de autenticación para
invalidar el token de sesión actual (sid).

#### `_fetch(self) -> None`

Llama a la API v6 de Pi-hole y actualiza la caché.

</details>
