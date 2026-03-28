# `core.audio_alert_service`

> **Ruta**: `core/audio_alert_service.py`

> **Cobertura de documentación**: 🟢 100% (14/14)

Servicio de alertas sonoras via los altavoces del FNK0100K.

Comportamiento:
  - {metric}_warn.wav : cada WARN_REPEAT_S (5 min) mientras siga en aviso
  - {metric}_crit.wav : cada CRIT_REPEAT_S (30 s)  mientras siga crítico
  - {metric}_ok.wav   : una sola vez al recuperarse

Archivos generados por: scripts/generate_sounds.py

---

## Tabla de contenidos

**Clase [`_MetricState`](#clase-_metricstate)**

**Clase [`AudioAlertService`](#clase-audioalertservice)**
  - [`start()`](#startself)
  - [`stop()`](#stopself)
  - [`is_running()`](#is_runningself-bool)
  - [`set_enabled()`](#set_enabledself-enabled-bool)
  - [`is_enabled()`](#is_enabledself-bool)
  - [`play_test()`](#play_testself)

---

## Dependencias internas

- `utils.logger`

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

Args:
    metric (str): La métrica a considerar.
    level (str): El nivel de la métrica.

Returns:
    str: La ruta del archivo de audio correspondiente.

</details>

## Clase `_MetricState`

Almacena el estado interno de una métrica y la fecha de última reproducción.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

### Atributos públicos

| Atributo | Valor inicial |
|----------|---------------|
| `zone` | `'ok'` |
| `last_played` | `0.0` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el estado de la métrica con valores predeterminados.

Args:
    None

Returns:
    None

Raises:
    None

</details>

## Clase `AudioAlertService`

Servicio de alertas sonoras que reproduce archivos WAV cuando se superan umbrales configurados.

Args:
    system_monitor: Fuente de métricas CPU/RAM/TEMP.
    service_monitor (opcional): Fuente de servicios caídos.

Returns:
    None

Raises:
    None

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

Inicia el servicio de alertas sonoras en segundo plano.

Args:
    None

Returns:
    None

Raises:
    None

#### `stop(self)`

Detiene el servicio de alertas de audio de manera limpia.

Args:
    None

Returns:
    None

Raises:
    None

#### `is_running(self) -> bool`

Indica si el servicio de alertas de audio está activo.

Args:
    None

Returns:
    bool: True si el servicio está en ejecución, False de lo contrario.

#### `set_enabled(self, enabled: bool)`

Activa o desactiva las alertas sonoras de forma segura.

Args:
    enabled (bool): Indica si se deben habilitar o deshabilitar las alertas sonoras.

Returns:
    None

Raises:
    None

#### `is_enabled(self) -> bool`

Indica si el servicio de alertas de audio está habilitado.

Args:
    None

Returns:
    bool: True si el servicio está habilitado, False de lo contrario.

Raises:
    None

#### `play_test(self)`

Reproduce un archivo de audio de prueba de forma asíncrona.

Args: 
    None

Returns: 
    None

Raises: 
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self, system_monitor, service_monitor = None)`

Inicializa el servicio de alertas de audio con monitores del sistema y servicios.

Args:
    system_monitor: Fuente de métricas CPU/RAM/TEMP.
    service_monitor (opcional): Fuente de servicios caídos.

Returns:
    None

Raises:
    None

#### `_loop(self)`

Ejecuta un bucle de polling en segundo plano para verificar alertas de audio.

Args: None

Returns: None

Raises: Exception en caso de error durante la verificación de alertas.

#### `_check(self)`

Evalúa las métricas del sistema y servicios contra los umbrales definidos.

Args: 
    None

Returns: 
    None

Raises: 
    Exception

#### `_play(self, sound_file: str)`

Reproduce un archivo de sonido utilizando aplay o paplay con un timeout de 15 segundos.

Args:
    sound_file (str): Ruta al archivo de sonido a reproducir.

Raises:
    FileNotFoundError: Si el archivo de sonido no existe.
    subprocess.TimeoutExpired: Si la reproducción del sonido supera el timeout.

</details>
