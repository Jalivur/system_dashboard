# `utils.system_utils`

> **Ruta**: `utils/system_utils.py`

> **Cobertura de documentación**: 🟢 100% (12/12)

Utilidades para obtener información del sistema

---

## Tabla de contenidos

**Clase [`SystemUtils`](#clase-systemutils)**
  - [`get_cpu_temp()`](#get_cpu_temp-float)
  - [`get_hostname()`](#get_hostname-str)
  - [`get_net_io()`](#get_net_iointerface-optionalstr-none-tuplestr-any)
  - [`safe_net_speed()`](#safe_net_speedcurrent-any-previous-optionalany-tuplefloat-float)
  - [`list_usb_storage_devices()`](#list_usb_storage_devices-list)
  - [`list_usb_other_devices()`](#list_usb_other_devices-list)
  - [`list_usb_devices()`](#list_usb_devices-list)
  - [`eject_usb_device()`](#eject_usb_devicedevice-dict-tuplebool-str)
  - [`run_script()`](#run_scriptscript_path-str-tuplebool-str)
  - [`get_interfaces_ips()`](#get_interfaces_ips-dictstr-str)
  - [`get_nvme_temp()`](#get_nvme_temp-float)

---

## Dependencias internas

- `config.settings`
- `utils.logger`

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

Proporciona funcionalidades para obtener información del sistema.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

### Métodos públicos

#### `get_cpu_temp() -> float`

Obtiene la temperatura actual de la CPU.

Args:
    Ninguno

Returns:
    float: Temperatura en grados Celsius.

Raises:
    Ninguna excepción específica, aunque puede registrar un warning si el formato de salida de los comandos del sistema es inesperado.

#### `get_hostname() -> str`

Obtiene el nombre del host del sistema.

Returns:
    str: Nombre del host del sistema. Si no se puede obtener, devuelve "unknown".

Raises:
    Exception: Si ocurre un error al obtener el nombre del host, se registra un warning.

#### `get_net_io(interface: Optional[str] = None) -> Tuple[str, Any]`

Obtiene estadísticas de red de una interfaz específica o la más activa si no se especifica.

Args:
    interface: Nombre de la interfaz de red o None para auto-detección de la interfaz más activa.

Returns:
    Tupla que contiene el nombre de la interfaz y sus estadísticas de red.

Raises:
    No se documentan excepciones explícitas.

#### `safe_net_speed(current: Any, previous: Optional[Any]) -> Tuple[float, float]`

Calcula la velocidad de red de forma segura a partir de estadísticas actuales y anteriores.

Args:
    current: Estadísticas actuales de red.
    previous: Estadísticas anteriores de red, puede ser None.

Returns:
    Tupla con velocidades de descarga y subida en megabytes por segundo.

Raises:
    Atrapa AttributeError y TypeError, registrando un mensaje de advertencia y retornando velocidades nulas.

#### `list_usb_storage_devices() -> list`

Recupera una lista de dispositivos de almacenamiento USB conectados al sistema.

Returns:
    list: Lista de diccionarios con información de los dispositivos de almacenamiento USB, 
          incluyendo nombre, tipo, punto de montaje, dispositivo, tamaño.

#### `list_usb_other_devices() -> list`

Recupera una lista de dispositivos USB del sistema, excluyendo dispositivos de almacenamiento.

Returns:
    list: Lista de strings con información de dispositivos USB.

Raises:
    subprocess.TimeoutExpired: Si el comando lsusb excede el tiempo límite.
    FileNotFoundError: Si el comando lsusb no se encuentra en el sistema.

#### `list_usb_devices() -> list`

Recupera una lista de dispositivos USB conectados al sistema.

Returns:
    list: Lista de dispositivos USB en formato de cadena.

Raises:
    None

#### `eject_usb_device(device: dict) -> Tuple[bool, str]`

Expulsa un dispositivo USB de forma segura.

Args:
    device: Diccionario con información del dispositivo (debe tener 'children' con particiones).

Returns:
    Tupla (success: bool, message: str) indicando si la expulsión fue exitosa y un mensaje descriptivo.

Raises:
    No se especifican excepciones explícitas en la implementación.

#### `run_script(script_path: str) -> Tuple[bool, str]`

Ejecuta un script de sistema mediante el comando bash.

Args:
    script_path: Ruta al script que se ejecutará.

Returns:
    Tupla que contiene un booleano que indica si la ejecución fue exitosa y un mensaje con el resultado.

Raises:
    subprocess.TimeoutExpired: Si el script tarda más de 30 segundos en ejecutarse.
    FileNotFoundError: Si el script no se encuentra en la ruta especificada.

#### `get_interfaces_ips() -> Dict[str, str]`

Obtiene las direcciones IP de todas las interfaces de red disponibles.

Returns:
    dict: Diccionario con el nombre de la interfaz como clave y su dirección IP como valor.

Raises:
    Exception: Si ocurre un error al obtener las direcciones IP de las interfaces.

#### `get_nvme_temp() -> float`

Obtiene la temperatura del disco NVMe mediante el comando smartctl.

Args:
    Ninguno

Returns:
    float: Temperatura en °C o 0.0 si no hay NVMe o no se puede leer.

Raises:
    Ninguna excepción relevante, maneja internamente posibles errores.
