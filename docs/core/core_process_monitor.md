# `core.process_monitor`

> **Ruta**: `core/process_monitor.py`

> **Cobertura de documentación**: 🟢 100% (17/17)

Monitor de procesos del sistema

---

## Tabla de contenidos

**Clase [`ProcessMonitor`](#clase-processmonitor)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`toggle_sort()`](#toggle_sortself-column-str-none)
  - [`refresh_now()`](#refresh_nowself-none)
  - [`get_processes()`](#get_processesself-limit-int-20-listdict)
  - [`search_processes()`](#search_processesself-query-str-listdict)
  - [`kill_process()`](#kill_processself-pid-int-tuple)
  - [`get_system_stats()`](#get_system_statsself-dict)
  - [`set_sort()`](#set_sortself-column-str-reverse-bool-true)
  - [`set_filter()`](#set_filterself-filter_type-str)
  - [`get_process_color()`](#get_process_colorvalue-float-str)

---

## Dependencias internas

- `utils.logger`

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

Monitoriza procesos en tiempo real con configuración personalizable.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

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

Inicia el sondeo de procesos en segundo plano.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `stop(self) -> None`

Detiene el sondeo de procesos limpiamente.

Args:
    None

Returns:
    None

Raises:
    None

#### `is_running(self) -> bool`

Verifica si el monitor de procesos está corriendo activamente.

Returns:
    bool: True si el monitor está activo.

#### `toggle_sort(self, column: str) -> None`

Alterna el criterio de ordenación o invierte el orden actual de la columna especificada.

Args:
    column (str): Columna para ordenar ('cpu', 'memory', 'name', 'pid')

Returns:
    None

Raises:
    None

#### `refresh_now(self) -> None`

Fuerza un refresco inmediato de la lista de procesos en background.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `get_processes(self, limit: int = 20) -> List[Dict]`

Obtiene una lista de procesos con su información, aplicando filtros según el tipo configurado.

Args:
    limit (int): Número máximo de procesos a retornar. Por defecto, 20.

Returns:
    List[Dict]: Lista de diccionarios con información de procesos.

#### `search_processes(self, query: str) -> List[Dict]`

Busca procesos por nombre o descripción que coincidan con la consulta dada.

Args:
    query (str): Texto a buscar en nombres y descripciones de procesos.

Returns:
    List[Dict]: Lista de procesos que coinciden con la consulta.

Raises:
    None

#### `kill_process(self, pid: int) -> tuple`

Mata un proceso por su ID de proceso (PID).

Args:
    pid: ID del proceso a terminar

Returns:
    Tupla (éxito, mensaje) indicando si se terminó el proceso y un mensaje descriptivo

Raises:
    psutil.NoSuchProcess: Si el proceso con el PID dado no existe
    psutil.AccessDenied: Si no hay permisos para terminar el proceso

#### `get_system_stats(self) -> Dict`

Obtiene estadísticas generales del sistema.

Returns:
    Dict: Diccionario con estadísticas del sistema, incluyendo uso de CPU, memoria utilizada y total, porcentaje de memoria usada, número total de procesos y tiempo de actividad.

Raises:
    Ninguna excepción específica.

Args:
    Ninguno.

#### `set_sort(self, column: str, reverse: bool = True)`

Establece el criterio de ordenación de la lista de procesos.

Args:
    column (str): Columna para ordenar ('cpu', 'memory', 'name', 'pid')
    reverse (bool): Si ordenar de forma descendente (por defecto True)

Returns:
    None

Raises:
    None

#### `set_filter(self, filter_type: str)`

Establece el tipo de filtro para la visualización de procesos.

Args:
    filter_type (str): Tipo de filtro a aplicar. Puede ser 'all', 'user' o 'system'.

Raises:
    ValueError: Si el tipo de filtro no es válido.

#### `get_process_color(value: float) -> str`

Obtiene la clave de color según el porcentaje de uso del proceso.

Args:
    value (float): Porcentaje de uso del proceso (0-100)

Returns:
    str: Clave de color ("danger", "warning" o "success")

Raises:
    Ninguna excepción explícita.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor de procesos con configuración por defecto.

Args:
    None

Returns:
    None

Raises:
    None

#### `_poll_loop(self) -> None`

Ejecuta el bucle principal de sondeo en segundo plano.

Args: 
    None

Returns: 
    None

Raises: 
    None

#### `_do_poll(self) -> None`

Realiza un sondeo único de procesos y actualiza el caché interno.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Exception: Si ocurre un error durante el sondeo de procesos.

#### `_format_uptime(seconds: float) -> str`

Formatea el tiempo de actividad (uptime) en un formato legible.

Args:
    seconds (float): Tiempo de actividad en segundos.

Returns:
    str: Cadena con el tiempo de actividad formateado (días, horas, minutos).

</details>
