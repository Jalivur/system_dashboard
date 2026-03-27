# `core.vpn_monitor`

> **Ruta**: `core/vpn_monitor.py`

Monitor de estado de VPN.
Detecta si la interfaz VPN está activa leyendo /proc/net/if_inet6 o ip link.
Sin dependencias nuevas — usa subprocess con comandos estándar.

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

Servicio background profesional que monitoriza el estado de la VPN.

Características:
* Sondeo cada 10s de estado de interfaz tun0/wg0 via 'ip addr' o fallback 'ifconfig'.
* Extracción automática de IP IPv4 asignada si interfaz UP.
* Thread daemon con lock para acceso thread-safe.
* API pública: get_status(), is_connected(), get_offline_count() para UI badge.
* force_poll() para comprobación inmediata.

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

Inicia el sondeo background (thread daemon).

Idempotente, log con intervalo e interfaz.

#### `stop(self) -> None`

Detiene el servicio limpiamente.

Join timeout 5s, resetea caché. Log de detención.

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo.

#### `get_status(self) -> dict`

Devuelve el estado actual de la VPN desde caché (thread-safe).

Returns:
    dict: {"connected": bool, "ip": str, "interface": str}

#### `is_connected(self) -> bool`

Estado rápido de conexión VPN (thread-safe).

Returns:
    bool: True si interfaz tiene IP IPv4 asignada.

#### `get_offline_count(self) -> int`

Para badge UI: 1 si desconectada, 0 si conectada (thread-safe).

Returns:
    int: 1 (offline) o 0 (online).

#### `force_poll(self) -> None`

Fuerza comprobación inmediata en thread separado.

Útil tras eventos connect/disconnect manual.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, interface: str = VPN_INTERFACE)`

Inicializa el monitor VPN.

Args:
    interface (str): Nombre de interfaz VPN (default "tun0").

Configura lock, estado inicial desconectado, event stop.

#### `_loop(self) -> None`

Bucle principal del thread de sondeo (privado).

Llama _poll() + wait(CHECK_INTERVAL), maneja exceptions.

#### `_poll(self) -> None`

Actualiza estado de VPN (privado).

Llama _check_interface(), actualiza caché protegida por lock.

#### `_check_interface(self, iface: str)`

Comprueba si la interfaz está activa y obtiene su IP.
Devuelve (connected: bool, ip: str).

#### `_check_interface_ifconfig(self, iface: str)`

Fallback usando ifconfig si 'ip' no está disponible (privado).

Returns:
    tuple[bool, str]: (connected, ip)

</details>
