# `core.disk_monitor`

> **Ruta**: `core/disk_monitor.py`

Monitor de disco

## Imports

```python
import subprocess
import json
import threading
from collections import deque
from typing import Dict
from config.settings import HISTORY, UPDATE_MS, COLORS
from utils.system_utils import SystemUtils, get_logger
import psutil
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `DiskMonitor`

Monitor de disco con historial

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_utils` | `SystemUtils()` |
| `_usage_hist` | `deque(maxlen=HISTORY)` |
| `_read_hist` | `deque(maxlen=HISTORY)` |
| `_write_hist` | `deque(maxlen=HISTORY)` |
| `_nvme_temp_hist` | `deque(maxlen=HISTORY)` |
| `_cache_lock` | `threading.Lock()` |
| `_last_disk_io` | `psutil.disk_io_counters()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_thread` | `None` |
| `_interval_s` | `max(UPDATE_MS / 1000.0, 1.0)` |

### Métodos públicos

#### `start(self)`

Inicia thread daemon polling cada _interval_s.

#### `stop(self)`

Detiene polling, limpia cache, join thread (timeout 5s).

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo.

#### `get_current_stats(self) -> Dict`

Retorna stats cache actuales disk_usage%/read/write MB/s/nvme_temp.
Thread-safe, 0s si stopped.

#### `update_history(self, stats: Dict) -> None`

Actualiza historiales con estadísticas actuales.

Args:
    stats: Diccionario con estadísticas

#### `get_history(self) -> Dict`

Obtiene todos los historiales.

Returns:
    Diccionario con historiales

#### `get_nvme_smart(self) -> dict`

Devuelve métricas SMART extendidas del NVMe via smartctl.

Requiere en sudoers:
    usuario ALL=(ALL) NOPASSWD: /usr/bin/smartctl

Campos devueltos:
    power_on_hours    — horas de uso total
    power_cycles      — veces encendido
    unsafe_shutdowns  — apagados sin guardar
    data_written_tb   — TB escritos en vida
    data_read_tb      — TB leídos en vida
    percentage_used   — % de vida útil consumida (0=nuevo, 100=al límite)
    available         — False si smartctl falla o no hay NVMe

#### `level_color(value: float, warn: float, crit: float) -> str`

Determina color según nivel.

Args:
    value: Valor actual
    warn:  Umbral de advertencia
    crit:  Umbral crítico

Returns:
    Color en formato hex

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa monitor disco, histories deque(HISTORY), cache thread-safe, deltas IO.

#### `_poll_loop(self) -> None`

Bucle daemon principal: _do_poll() cada self._interval_s segs.

#### `_do_poll(self)`

Sondeo disk_usage% / delta IO MB/s / nvme_temp, update cache/history.

</details>
