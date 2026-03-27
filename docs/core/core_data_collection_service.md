# `core.data_collection_service`

> **Ruta**: `core/data_collection_service.py`

Servicio de recolección automática de datos

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

Servicio que recolecta métricas cada X minutos

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

Inicia el servicio de recolección

#### `stop(self)`

Detiene el servicio limpiamente.

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo

#### `force_collection(self)`

Fuerza una recolección inmediata

<details>
<summary>Métodos privados</summary>

#### `__new__(cls, *args, **kwargs)`

Implementa patrón singleton thread-safe.

#### `__init__(self, system_monitor, fan_controller, network_monitor, disk_monitor, update_monitor, interval_minutes: int = 5)`

Inicializa singleton DataCollectionService.

Args:
    system_monitor, fan_controller, network_monitor, disk_monitor, update_monitor: Fuentes métricas.
    interval_minutes (int): Minutos entre recolecciones (default 5).

#### `_collection_loop(self)`

Bucle principal de recolección

#### `_collect_and_save(self)`

Recolecta métricas y las guarda

</details>
