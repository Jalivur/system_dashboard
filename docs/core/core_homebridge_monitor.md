# `core.homebridge_monitor`

> **Ruta**: `core/homebridge_monitor.py`

> **Cobertura de documentación**: 🟢 100% (19/19)

Monitor de Homebridge
Integración con la API REST de homebridge-config-ui-x
Credenciales cargadas desde .env (nunca hardcodeadas)

Incluye sondeo ligero en background cada 30s para mantener
los badges del menú actualizados sin necesidad de abrir la ventana.

---

## Tabla de contenidos

**Clase [`HomebridgeMonitor`](#clase-homebridgemonitor)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`get_accessories()`](#get_accessoriesself-listdict)
  - [`get_accessories_cached()`](#get_accessories_cachedself-listdict)
  - [`toggle()`](#toggleself-unique_id-str-turn_on-bool-bool)
  - [`is_reachable()`](#is_reachableself-bool)
  - [`get_offline_count()`](#get_offline_countself-int)
  - [`get_on_count()`](#get_on_countself-int)
  - [`get_fault_count()`](#get_fault_countself-int)
  - [`set_brightness()`](#set_brightnessself-unique_id-str-brightness-int-bool)
  - [`set_target_temp()`](#set_target_tempself-unique_id-str-temp-float-bool)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import json
import os
import threading
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import get_logger
from dotenv import load_dotenv
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `HOMEBRIDGE_HOST` | `os.environ.get('HOMEBRIDGE_HOST', '')` |
| `HOMEBRIDGE_PORT` | `int(os.environ.get('HOMEBRIDGE_PORT', '8581'))` |
| `HOMEBRIDGE_USER` | `os.environ.get('HOMEBRIDGE_USER', '')` |
| `HOMEBRIDGE_PASS` | `os.environ.get('HOMEBRIDGE_PASS', '')` |
| `HOMEBRIDGE_URL` | `f'http://{HOMEBRIDGE_HOST}:{HOMEBRIDGE_PORT}'` |
| `REQUEST_TIMEOUT` | `5` |
| `POLL_INTERVAL_S` | `30` |

<details>
<summary>Funciones privadas</summary>

### `_load_env()`

Carga variables de entorno desde un archivo .env sin utilizar dependencias externas.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

</details>

## Clase `HomebridgeMonitor`

Inicializa y gestiona un monitor para dispositivos Homebridge, 
realizando sondeos periódicos y actualizaciones de estado.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_token_lock` | `threading.Lock()` |
| `_accessories_lock` | `threading.Lock()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |

### Métodos públicos

#### `start(self) -> None`

Inicia el sondeo de Homebridge en segundo plano.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `stop(self) -> None`

Detiene el sondeo limpiamente.

Args:
    None

Returns:
    None

Raises:
    None

#### `is_running(self) -> bool`

Indica si el servicio de monitorización de Homebridge está en ejecución.

Args:
    Ninguno

Returns:
    bool: True si el servicio está corriendo, False en caso contrario.

Raises:
    Ninguno

#### `get_accessories(self) -> List[Dict]`

Recupera la lista de accesorios disponibles en Homebridge.

Args: 
    Ninguno

Returns:
    List[Dict]: Lista de diccionarios con información de los accesorios.

Raises:
    Ninguna excepción específica.

Nota: Si el monitor no está en ejecución o no se puede conectar a Homebridge, 
      se devuelve una lista vacía y se actualiza el estado de alcanzabilidad.

#### `get_accessories_cached(self) -> List[Dict]`

Devuelve la lista de accesorios en memoria sin realizar peticiones HTTP adicionales.

Args: 
    Ninguno

Returns:
    List[Dict]: La lista de accesorios en memoria.

Raises:
    Ninguno

#### `toggle(self, unique_id: str, turn_on: bool) -> bool`

Cambia el estado On/Off de un accesorio identificado por su ID único.

Args:
    unique_id (str): Identificador único del accesorio.
    turn_on (bool): Nuevo estado del accesorio (True para encender, False para apagar).

Returns:
    bool: True si el comando se envió correctamente, False en caso contrario.

Raises:
    Ninguna excepción específica.

#### `is_reachable(self) -> bool`

Indica si el dispositivo está alcanzable según la última consulta.

Args:
    None

Returns:
    bool: True si el dispositivo está alcanzable, False en caso contrario.

Raises:
    None

#### `get_offline_count(self) -> int`

Obtiene el número de servicios de Homebridge que se encuentran desconectados.

Args:
    None

Returns:
    int: 1 si Homebridge no respondió en la última consulta, 0 en caso contrario.

Raises:
    None

#### `get_on_count(self) -> int`

Obtiene el número de enchufes encendidos.

Args:
    None

Returns:
    int: Número de enchufes encendidos.

Raises:
    None

#### `get_fault_count(self) -> int`

Obtiene el número de dispositivos con estado de falla.

Args:
    Ninguno

Returns:
    int: Número de dispositivos con estado de falla.

Raises:
    Ninguno

#### `set_brightness(self, unique_id: str, brightness: int) -> bool`

Establece el brillo de una luz Homebridge.

Args:
    unique_id (str): ID único del accesorio.
    brightness (int): Brillo en porcentaje (0-100).

Returns:
    bool: True si el comando se envió correctamente.

Raises:
    None

#### `set_target_temp(self, unique_id: str, temp: float) -> bool`

Establece la temperatura objetivo de un termostato.

Args:
    unique_id (str): Identificador único del termostato.
    temp (float): Temperatura objetivo en grados Celsius.

Returns:
    bool: True si la operación fue exitosa, False en caso contrario.

Raises:
    Ninguna excepción explícita, pero puede fallar debido a errores de red o servicio detenido.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor de Homebridge.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_poll_loop(self) -> None`

Ejecuta un bucle de sondeo en segundo plano para obtener información de los accesorios de Homebridge.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

Nota: El bucle se ejecuta hasta que se detenga explícitamente.

#### `_authenticate(self) -> bool`

Autentica con el servidor Homebridge para obtener un token JWT.

Args: 
    Ninguno

Returns:
    bool: True si la autenticación es exitosa, False en caso contrario.

Raises:
    Ninguna excepción específica, pero registra errores en el logger.

#### `_get_token(self) -> Optional[str]`

Obtiene el token de autenticación actual, intentando autenticar si no existe.

Args:
    Ninguno

Returns:
    str: El token de autenticación actual, o None si la autenticación falla.

Raises:
    Ninguno

#### `_request(self, method: str, path: str, body: Optional[Dict] = None) -> Optional[Dict]`

Realiza una petición autenticada a la API de Homebridge, renovando el token de acceso si caduca.

Args:
    method (str): Método HTTP de la petición (p. ej. GET, POST, PUT, DELETE).
    path (str): Ruta de la petición.
    body (Optional[Dict]): Datos de la petición en formato JSON.

Returns:
    Optional[Dict]: Respuesta de la petición en formato JSON, o None si falla.

Raises:
    Exception: Si la petición falla después de renovar el token.

</details>
