# `utils.system_utils`

> **Ruta**: `utils/system_utils.py`

Utilidades para obtener información del sistema

## Imports

```python
import re
import socket
import psutil
import subprocess
import glob
from typing import Tuple, Dict, Optional, Any
from collections import namedtuple
from config.settings import UPDATE_MS
import json
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `SystemUtils`

Utilidades para interactuar con el sistema

### Métodos públicos

#### `get_cpu_temp() -> float`

Obtiene la temperatura de la CPU

Returns:
    Temperatura en grados Celsius

#### `get_hostname() -> str`

Obtiene el nombre del host

Returns:
    Nombre del host o "unknown"

#### `get_net_io(interface: Optional[str] = None) -> Tuple[str, Any]`

Obtiene estadísticas de red con auto-detección de interfaz activa

Args:
    interface: Nombre de la interfaz o None para auto-detección

Returns:
    Tupla (nombre_interfaz, estadísticas)

#### `safe_net_speed(current: Any, previous: Optional[Any]) -> Tuple[float, float]`

Calcula velocidad de red de forma segura

Args:
    current: Estadísticas actuales
    previous: Estadísticas anteriores

Returns:
    Tupla (download_mb, upload_mb)

#### `list_usb_storage_devices() -> list`

Lista dispositivos USB de almacenamiento (discos)

Returns:
    Lista de diccionarios con información de almacenamiento USB

#### `list_usb_other_devices() -> list`

Lista otros dispositivos USB (no almacenamiento)

Returns:
    Lista de strings con información de dispositivos USB

#### `list_usb_devices() -> list`

Lista TODOS los dispositivos USB (mantener para compatibilidad)

Returns:
    Lista de strings con lsusb

#### `eject_usb_device(device: dict) -> Tuple[bool, str]`

Expulsa un dispositivo USB de forma segura

Args:
    device: Diccionario con información del dispositivo
           (debe tener 'children' con particiones)

Returns:
    Tupla (success: bool, message: str)

#### `run_script(script_path: str) -> Tuple[bool, str]`

Ejecuta un script de sistema

Args:
    script_path: Ruta al script

Returns:
    Tupla (éxito, mensaje)

#### `get_interfaces_ips() -> Dict[str, str]`

Obtiene las IPs de todas las interfaces de red

Returns:
    Diccionario {interfaz: IP}

#### `get_nvme_temp() -> float`

Obtiene la temperatura del disco NVMe.
Solo lee sensores asociados a dispositivos NVMe reales.

Returns:
    Temperatura en °C o 0.0 si no hay NVMe o no se puede leer
