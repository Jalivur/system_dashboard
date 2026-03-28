# `core.vpn_monitor`

> **Ruta**: `core/vpn_monitor.py`

> **Cobertura de documentación**: 🟢 100% (13/13)

Monitor de estado de VPN.
Detecta si la interfaz VPN está activa leyendo /proc/net/if_inet6 o ip link.
Sin dependencias nuevas — usa subprocess con comandos estándar.

---

## Tabla de contenidos

**Clase [`VpnMonitor`](#clase-vpnmonitor)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`get_status()`](#get_statusself-dict)
  - [`is_connected()`](#is_connectedself-bool)
  - [`get_offline_count()`](#get_offline_countself-int)
  - [`force_poll()`](#force_pollself-none)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import subprocess
import threading
import time
from typing import Optional
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `VPN_INTERFACE` | `'tun0'` |
| `CHECK_INTERVAL` | `10` |

## Clase `VpnMonitor`

Servicio background que monitoriza el estado de la VPN.

Args:
    interface (str): Nombre de interfaz VPN (default "tun0").

Características:
* Configura lock para acceso thread-safe.
* Estado inicial: desconectado.

Atributos:
* _interface: Nombre de interfaz VPN.
* _lock: Lock para acceso thread-safe.
* _running: Estado de ejecución.
* _stop_evt: Evento de parada.
* _thread: Hilo de ejecución.
* _connected: Estado de conexión.
* _vpn_ip: Dirección IP asignada.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_interface` | `interface` |
| `_lock` | `threading.Lock()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_connected` | `False` |
| `_vpn_ip` | `''` |
| `_iface` | `interface` |

### Métodos públicos

#### `start(self) -> None`

Inicia el sondeo de VPN en segundo plano.

Args: 
    None

Returns: 
    None

Raises: 
    None

#### `stop(self) -> None`

Detiene el servicio de monitoreo de VPN de manera limpia.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `is_running(self) -> bool`

Indica si el servicio de monitoreo de VPN está actualmente en ejecución.

Args:
    None

Returns:
    bool: True si el servicio está corriendo, False en caso contrario.

Raises:
    None

#### `get_status(self) -> dict`

Obtiene el estado actual de la VPN desde caché de manera segura para hilos.

Args:
    None

Returns:
    dict: Diccionario con el estado de la VPN. 
          {"connected": bool, "ip": str, "interface": str}

Raises:
    None

#### `is_connected(self) -> bool`

Indica si la conexión VPN está actualmente activa.

Args:
    None

Returns:
    bool: True si la interfaz VPN tiene una IP IPv4 asignada.

Raises:
    None

#### `get_offline_count(self) -> int`

Obtiene el estado de conexión de la VPN para mostrar en la interfaz de usuario.

Args:
    Ninguno

Returns:
    int: 1 si la VPN está desconectada, 0 si está conectada.

Raises:
    Ninguno

#### `force_poll(self) -> None`

Fuerza una comprobación inmediata del estado de la VPN en un hilo separado.

Útil después de eventos de conexión o desconexión manual.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

<details>
<summary>Métodos privados</summary>

#### `__init__(self, interface: str = VPN_INTERFACE)`

Inicializa el monitor VPN.

Args:
    interface (str): Nombre de interfaz VPN (por defecto "tun0").

Configura el bloqueo, el estado inicial desconectado y el evento de parada.

#### `_loop(self) -> None`

Ejecuta el bucle principal del thread de sondeo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

Nota: 
    Llama a _poll() y wait(CHECK_INTERVAL) en un ciclo, manejando excepciones.
    Se detiene cuando self._running es False o self._stop_evt está seteado.

#### `_poll(self) -> None`

Actualiza el estado de la conexión VPN.

Actualiza la caché protegida por bloqueo, llamando previamente a `_check_interface()`.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_check_interface(self, iface: str)`

Comprueba si una interfaz de red está activa y obtiene su dirección IP.

Args:
    iface (str): Nombre de la interfaz de red a comprobar.

Returns:
    tuple: Un tupla con dos valores, el primero indica si la interfaz está conectada (bool) y el segundo la dirección IP de la interfaz (str).

Raises:
    Exception: Si ocurre un error durante la comprobación de la interfaz, se registra el error y se devuelve False junto con una cadena vacía.

#### `_check_interface_ifconfig(self, iface: str)`

Verifica el estado de una interfaz de red y su dirección IP mediante ifconfig.

Args:
    iface (str): Nombre de la interfaz de red a verificar.

Returns:
    tuple[bool, str]: Tupla con un booleano que indica si la interfaz está conectada y la dirección IP asignada.

Raises:
    Exception: Si ocurre un error durante la ejecución de ifconfig.

</details>
