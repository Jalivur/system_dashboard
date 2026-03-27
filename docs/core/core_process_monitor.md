# `core.process_monitor`

> **Ruta**: `core/process_monitor.py`

Monitor de procesos del sistema

## Imports

```python
import threading
import psutil
from typing import List, Dict, Optional
from datetime import datetime
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `PROCESS_POLL_INTERVAL` | `10` |

## Clase `ProcessMonitor`

Monitor de procesos en tiempo real

### Atributos públicos

| Atributo | Valor inicial |
|----------|---------------|
| `sort_by` | `'cpu'` |
| `sort_reverse` | `True` |
| `filter_type` | `'all'` |

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |

### Métodos públicos

#### `start(self) -> None`

Arranca el sondeo en background (llamado automáticamente en __init__).

#### `stop(self) -> None`

Detiene el sondeo limpiamente.

#### `is_running(self) -> bool`

Verifica si el monitor de procesos está corriendo activamente.

Returns:
    bool: True si el sondeo está activo

#### `toggle_sort(self, column: str) -> None`

Alterna el criterio de ordenación o invierte el orden actual.

Args:
    column: Columna para ordenar ('cpu', 'memory', 'name', 'pid')

#### `refresh_now(self) -> None`

Fuerza un refresco inmediato de la lista de procesos en background.
Útil para actualizar datos sin esperar al intervalo de sondeo.

#### `get_processes(self, limit: int = 20) -> List[Dict]`

Obtiene lista de procesos con su información.

Args:
    limit: Número máximo de procesos a retornar

Returns:
    Lista de diccionarios con información de procesos

#### `search_processes(self, query: str) -> List[Dict]`

Busca procesos por nombre o descripción.

Args:
    query: Texto a buscar

Returns:
    Lista de procesos que coinciden

#### `kill_process(self, pid: int) -> tuple`

Mata un proceso por su PID.

Args:
    pid: ID del proceso

Returns:
    Tupla (éxito, mensaje)

#### `get_system_stats(self) -> Dict`

Obtiene estadísticas generales del sistema.

Returns:
    Diccionario con estadísticas

#### `set_sort(self, column: str, reverse: bool = True)`

Establece el criterio de ordenación de la lista de procesos.

Args:
    column: Columna para ordenar ('cpu', 'memory', 'name', 'pid')
    reverse: Si ordenar de forma descendente (por defecto True)

#### `set_filter(self, filter_type: str)`

Establece el filtro de visualización de procesos.

Args:
    filter_type: Tipo de filtro ('all', 'user', 'system')

#### `get_process_color(value: float) -> str`

Obtiene color según porcentaje de uso.

Args:
    value: Porcentaje (0-100)

Returns:
    Clave de color en COLORS

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor de procesos con configuración por defecto.

Configuración inicial:
- sort_by: 'cpu' (cpu | memory | name | pid)
- sort_reverse: True
- filter_type: 'all' (all | user | system)

#### `_poll_loop(self) -> None`

Bucle principal de sondeo en background (método privado).
Se ejecuta cada PROCESS_POLL_INTERVAL segundos.

#### `_do_poll(self) -> None`

Realiza un sondeo único de procesos y actualiza el caché (método privado).

#### `_format_uptime(seconds: float) -> str`

Formatea uptime en formato legible.

</details>
