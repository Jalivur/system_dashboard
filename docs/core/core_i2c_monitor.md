# `core.i2c_monitor`

> **Ruta**: `core/i2c_monitor.py`

core/i2c_monitor.py

Escaner I2C de solo lectura usando smbus2.
Detecta dispositivos en todos los buses /dev/i2c-* disponibles.

Arquitectura:
  - Thread daemon que escanea cada INTERVAL_SECONDS
  - get_stats() devuelve cache — nunca bloquea la UI
  - SOLO LECTURA: usa read_byte() para detectar ACK, nunca escribe
  - smbus2 es opcional — si no está instalado devuelve error descriptivo

## Imports

```python
import threading
import os
from utils.logger import get_logger
import smbus2
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `INTERVAL_SECONDS` | `30` |

## Clase `I2CMonitor`

Escanea buses I2C periódicamente y cachea los resultados.
Solo lectura — nunca escribe en el bus.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_lock` | `threading.Lock()` |
| `_stats` | `{}` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_thread` | `None` |

### Métodos públicos

#### `start(self) -> None`

Inicia thread daemon de escaneo periódico cada INTERVAL_SECONDS.

#### `stop(self) -> None`

Detiene thread, limpia cache _stats.

#### `is_running(self) -> bool`

Estado del monitor (thread activo).

Returns:
    bool: True si escaneando.

#### `get_stats(self) -> dict`

Retorna stats thread-safe del último escaneo.

Returns:
    dict: {'error':str, 'buses':list[dict], 'total':int}

#### `scan_now(self) -> None`

Fuerza escaneo inmediato en thread daemon separado.
Útil desde UI para refresh manual.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa monitor I2C con locks y estado vacío.

#### `_loop(self) -> None`

Bucle thread daemon: escaneo inicial + INTERVAL_SECONDS loop.
Sale limpiamente en stop().

#### `_scan(self) -> None`

Escaneo interno: importa smbus2, detecta buses /dev/i2c-*, read_byte() en rango 0x03-0x77, cachea thread-safe.
Maneja errores graceful (no instalado, buses vacíos).

</details>
