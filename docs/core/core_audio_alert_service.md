# `core.audio_alert_service`

> **Ruta**: `core/audio_alert_service.py`

Servicio de alertas sonoras via los altavoces del FNK0100K.

Comportamiento:
  - {metric}_warn.wav : cada WARN_REPEAT_S (5 min) mientras siga en aviso
  - {metric}_crit.wav : cada CRIT_REPEAT_S (30 s)  mientras siga crítico
  - {metric}_ok.wav   : una sola vez al recuperarse

Archivos generados por: scripts/generate_sounds.py

## Imports

```python
import subprocess
import threading
import time
import os
from pathlib import Path
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `WARN_REPEAT_S` | `45` |
| `CRIT_REPEAT_S` | `30` |

<details>
<summary>Funciones privadas</summary>

### `_sound(metric: str, level: str) -> str`

Devuelve la ruta del audio para una métrica y nivel dados.

</details>

## Clase `_MetricState`

Estado interno por métrica: zone ('ok'/'warn'/'crit'), last_played ts.

### Atributos públicos

| Atributo | Valor inicial |
|----------|---------------|
| `zone` | `'ok'` |
| `last_played` | `0.0` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa zone 'ok', last_played 0.

</details>

## Clase `AudioAlertService`

Servicio de alertas sonoras via los altavoces del FNK0100K.
Reproduce archivos WAV cuando CPU, RAM, temperatura o servicios
superan los umbrales configurados en _THRESHOLDS.
Corre en thread daemon con patrón _stop_evt estándar.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_monitor` | `system_monitor` |
| `_service_monitor` | `service_monitor` |
| `_lock` | `threading.Lock()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_thread` | `None` |
| `_enabled` | `True` |
| `_play_lock` | `threading.Lock()` |

### Métodos públicos

#### `start(self)`

Inicia thread daemon _loop para polling alertas sonoras.

#### `stop(self)`

Detiene thread limpiamente (join 5s timeout).

#### `is_running(self) -> bool`

Estado activo del servicio.
Returns:
    bool

#### `set_enabled(self, enabled: bool)`

Activa/desactiva alertas sonoras (thread-safe).

Args:
    enabled (bool): True para habilitar sonidos.

#### `is_enabled(self) -> bool`

Estado habilitado sonidos (thread-safe).
Returns:
    bool

#### `play_test(self)`

Test: Reproduce temp_crit.wav async thread.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, system_monitor, service_monitor = None)`

Inicializa AudioAlertService.

Args:
    system_monitor: Fuente de métricas CPU/RAM/TEMP.
    service_monitor (optional): Fuente servicios caídos.

#### `_loop(self)`

Bucle polling thread daemon: _check cada min(CRIT_REPEAT_S,10)s.

#### `_check(self)`

Evalúa métricas vs THRESHOLDS: crit/warn/ok zones, play WAV según repeat/edge.

#### `_play(self, sound_file: str)`

Reproduce WAV serial (lock), try aplay/paplay, timeout 15s.

</details>
