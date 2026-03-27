# `core.network_monitor`

> **Ruta**: `core/network_monitor.py`

Monitor de red

## Imports

```python
import json
import threading
import subprocess
from collections import deque
from typing import Dict, Optional
from config.settings import HISTORY, NET_MIN_SCALE, NET_MAX_SCALE, NET_IDLE_THRESHOLD, NET_IDLE_RESET_TIME, NET_MAX_MB, COLORS, NET_WARN, NET_CRIT
from utils.system_utils import SystemUtils
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `NetworkMonitor`

Monitor de red con gestión de estadísticas y speedtest

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_utils` | `SystemUtils()` |
| `_running` | `True` |
| `_download_hist` | `deque(maxlen=HISTORY)` |
| `_upload_hist` | `deque(maxlen=HISTORY)` |
| `_last_net_io` | `{}` |
| `_last_used_iface` | `None` |
| `_dynamic_max` | `NET_MAX_MB` |
| `_idle_counter` | `0` |
| `_speedtest_result` | `{'status': 'idle', 'ping': 0, 'download': 0.0, 'upload': 0.0}` |

### Métodos públicos

#### `start(self) -> None`

Activa monitor de red.

#### `stop(self) -> None`

Limpia historiales y speedtest cache.

#### `is_running(self) -> bool`

Estado del monitor.

Returns:
    bool: True si activo.

#### `get_current_stats(self, interface: Optional[str] = None) -> Dict`

Obtiene estadísticas actuales de red.

Args:
    interface: Interfaz específica o None para auto-detección

Returns:
    Diccionario con estadísticas de red

#### `update_history(self, stats: Dict) -> None`

Append velocidades a deques HISTORY para gráficos.

Args:
    stats (Dict): {'download_mb':float, 'upload_mb':float}

#### `adaptive_scale(self, current_max: float, recent_data: list) -> float`

Ajusta escala gráfica auto (zoom basado peaks recientes/idle).

Args:
    current_max (float): Máximo actual escala.
    recent_data (list): Datos velocidades MB/s últimos HISTORY.

Returns:
    float: Nueva escala NET_MIN_SCALE..NET_MAX_SCALE.

#### `update_dynamic_scale(self) -> None`

Recalcula _dynamic_max desde historial DL/UL combinado.

#### `get_history(self) -> Dict`

Obtiene historiales de red.

#### `run_speedtest(self) -> None`

Ejecuta speedtest (CLI oficial Ookla) en un thread separado.

#### `get_speedtest_result(self) -> Dict`

Obtiene el resultado del speedtest.

#### `reset_speedtest(self) -> None`

Resetea el estado del speedtest.

#### `net_color(value: float) -> str`

Determina el color según el tráfico de red.

Args:
    value: Velocidad en MB/s

Returns:
    Color en formato hex

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa historiales, caches speedtest, dynamic scale.

</details>
