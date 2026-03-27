# `core.network_scanner`

> **Ruta**: `core/network_scanner.py`

Escáner de red local usando arp-scan.
Requiere: sudo arp-scan (disponible en Kali por defecto)

Ejecuta arp-scan en un thread de background para no bloquear la UI.

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

Escáner de red local con arp-scan.

Uso:
    scanner = NetworkScanner()
    scanner.scan()                    # lanza en background
    devices = scanner.get_devices()   # lee caché (no bloquea)
    status  = scanner.get_status()    # 'idle' | 'scanning' | 'done' | 'error'

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_status` | `'idle'` |
| `_error` | `''` |
| `_lock` | `threading.Lock()` |
| `_running` | `True` |

### Métodos públicos

#### `start(self) -> None`

Activa el scanner.

#### `stop(self) -> None`

Limpia cache dispositivos/status.

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo.

#### `scan(self) -> None`

Lanza el escaneo en background. Si ya hay uno en curso, no hace nada.

#### `get_devices(self) -> List[Dict]`

Devuelve la lista de dispositivos del último escaneo (caché).

#### `get_status(self) -> str`

Estado actual: 'idle' | 'scanning' | 'done' | 'error'.

#### `get_error(self) -> str`

Mensaje de error si status == 'error'.

#### `get_last_scan_age(self) -> Optional[float]`

Segundos desde el último escaneo completado. None si nunca se escaneó.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa listas dispositivos, status, locks.

#### `_do_scan(self) -> None`

Ejecuta arp-scan y parsea el resultado.

#### `_parse_output(self, output: str) -> list`

Parsea stdout de arp-scan: IP/MAC/Vendor → lista Dict ordenada.
Filtra headers/stats, resolve hostname por IP.

#### `_resolve_hostname(ip: str) -> str`

Intenta resolver el hostname de una IP. Devuelve '' si falla.

</details>
