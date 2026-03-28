# `core.network_scanner`

> **Ruta**: `core/network_scanner.py`

> **Cobertura de documentación**: 🟢 100% (13/13)

Escáner de red local usando arp-scan.
Requiere: sudo arp-scan (disponible en Kali por defecto)

Ejecuta arp-scan en un thread de background para no bloquear la UI.

---

## Tabla de contenidos

**Clase [`NetworkScanner`](#clase-networkscanner)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`scan()`](#scanself-none)
  - [`get_devices()`](#get_devicesself-listdict)
  - [`get_status()`](#get_statusself-str)
  - [`get_error()`](#get_errorself-str)
  - [`get_last_scan_age()`](#get_last_scan_ageself-optionalfloat)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import subprocess
import threading
import socket
import re
import time
from typing import List, Dict, Optional
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `ARP_TIMEOUT` | `15` |

## Clase `NetworkScanner`

Activa el escáner de red para iniciar el proceso de detección de dispositivos.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_status` | `'idle'` |
| `_error` | `''` |
| `_lock` | `threading.Lock()` |
| `_running` | `True` |

### Métodos públicos

#### `start(self) -> None`

Inicia el escaneo de red.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `stop(self) -> None`

Detiene el escaneo de red y limpia la caché de dispositivos y estados.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `is_running(self) -> bool`

Indica si el servicio de escaneo de red está actualmente en ejecución.

Args:
    None

Returns:
    bool: True si el servicio está corriendo, False en caso contrario.

Raises:
    None

#### `scan(self) -> None`

Inicia el escaneo de la red en segundo plano si no hay uno en curso.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `get_devices(self) -> List[Dict]`

Devuelve la lista de dispositivos del último escaneo almacenada en caché.

Args:
    Ninguno

Returns:
    List[Dict]: Lista de dispositivos detectados en el último escaneo.

Raises:
    Ninguno

#### `get_status(self) -> str`

Obtiene el estado actual del escaneo de red.

Args:
    Ninguno

Returns:
    str: Estado actual del escaneo, puede ser 'idle', 'scanning', 'done' o 'error'.

Raises:
    Ninguno

#### `get_error(self) -> str`

Obtiene el mensaje de error registrado en el escáner de red.

Args:
    Ninguno

Returns:
    str: El mensaje de error registrado.

Raises:
    Ninguno

#### `get_last_scan_age(self) -> Optional[float]`

Devuelve la edad del último escaneo completado en segundos.

Args:
    None

Returns:
    float: Edad del último escaneo en segundos. 
    None: Si nunca se ha realizado un escaneo.

Raises:
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el NetworkScanner con listas de dispositivos y estado.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_do_scan(self) -> None`

Ejecuta arp-scan para detectar dispositivos en la red local y parsea el resultado.

Args: Ninguno

Returns: Ninguno

Raises: 
- RuntimeError: Si arp-scan devuelve un código de salida distinto de cero.
- subprocess.TimeoutExpired: Si arp-scan excede el tiempo límite establecido.
- FileNotFoundError: Si no se encuentran archivos necesarios para arp-scan.

#### `_parse_output(self, output: str) -> list`

Parsea la salida de arp-scan para extraer información de dispositivos en la red.

Args:
    output (str): La salida de arp-scan a parsear.

Returns:
    list: Una lista de diccionarios ordenados con la información de cada dispositivo, 
          incluyendo IP, MAC, proveedor y nombre de host.

Raises:
    None

#### `_resolve_hostname(ip: str) -> str`

Resuelve el hostname asociado a una dirección IP.

Args:
    ip (str): La dirección IP a resolver.

Returns:
    str: El hostname asociado a la IP, o cadena vacía si falla la resolución.

Raises:
    Exception: Si ocurre un error durante la resolución.

</details>
