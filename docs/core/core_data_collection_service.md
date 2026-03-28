# `core.data_collection_service`

> **Ruta**: `core/data_collection_service.py`

> **Cobertura de documentación**: 🟢 100% (9/9)

Servicio de recolección automática de datos

---

## Tabla de contenidos

**Clase [`DataCollectionService`](#clase-datacollectionservice)**
  - [`start()`](#startself)
  - [`stop()`](#stopself)
  - [`is_running()`](#is_runningself-bool)
  - [`force_collection()`](#force_collectionself)

---

## Dependencias internas

- `core`
- `utils.file_manager`
- `utils.logger`

## Imports

```python
import threading
import time
from datetime import datetime
from core import DataLogger
from utils.file_manager import FileManager
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `DataCollectionService`

Servicio que recolecta métricas de forma periódica.

Args:
    system_monitor: Fuente de métricas del sistema.
    fan_controller: Controlador de ventiladores.
    network_monitor: Monitor de red.
    disk_monitor: Monitor de disco.
    update_monitor: Monitor de actualizaciones.
    interval_minutes (int): Minutos entre recolecciones (por defecto, 5).

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_monitor` | `system_monitor` |
| `_fan_file` | `FileManager()` |
| `_network_monitor` | `network_monitor` |
| `_disk_monitor` | `disk_monitor` |
| `_update_monitor` | `update_monitor` |
| `_interval_minutes` | `interval_minutes` |
| `_data_logger` | `DataLogger()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_thread` | `None` |
| `_initialized` | `True` |

### Métodos públicos

#### `start(self)`

Inicia el servicio de recolección de datos en segundo plano.

Args:
    None

Returns:
    None

Raises:
    None

#### `stop(self)`

Detiene el servicio de recolección de datos de manera segura.

Args:
    None

Returns:
    None

Raises:
    None

#### `is_running(self) -> bool`

Indica si el servicio de recolección de datos está en ejecución.

Args:
    None

Returns:
    bool: True si el servicio está corriendo, False de lo contrario.

Raises:
    None

#### `force_collection(self)`

Fuerza una recolección inmediata de datos.

Args:
    Ninguno.

Returns:
    Ninguno.

Raises:
    Ninguna excepción explícita.

<details>
<summary>Métodos privados</summary>

#### `__new__(cls, *args, **kwargs)`

Crea una instancia única de la clase utilizando el patrón singleton thread-safe.

Args:
    *args: Argumentos posicionales ignorados.
    **kwargs: Argumentos clave-valor ignorados.

Returns:
    La instancia única de la clase.

Raises:
    None

#### `__init__(self, system_monitor, fan_controller, network_monitor, disk_monitor, update_monitor, interval_minutes: int = 5)`

Inicializa el servicio de recolección de datos con fuentes métricas y un intervalo de actualización.

Args:
    system_monitor: Fuente de monitorización del sistema.
    fan_controller: Controlador de ventiladores.
    network_monitor: Fuente de monitorización de la red.
    disk_monitor: Fuente de monitorización del disco.
    update_monitor: Fuente de monitorización de actualizaciones.
    interval_minutes (int): Intervalo en minutos entre recolecciones de datos (por defecto, 5).

Raises: 
    None
Returns: 
    None

#### `_collection_loop(self)`

Ejecuta el bucle principal de recolección de datos en intervalos definidos.

Args:
    None

Returns:
    None

Raises:
    Exception: Si ocurre un error durante la recolección de datos.

#### `_collect_and_save(self)`

Recolecta y guarda métricas del sistema, red, disco y ventilador.

Args: None

Returns: None

Raises: None

</details>
