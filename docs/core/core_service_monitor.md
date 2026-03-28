# `core.service_monitor`

> **Ruta**: `core/service_monitor.py`

> **Cobertura de documentación**: 🟢 100% (25/25)

Monitor de servicios systemd

---

## Tabla de contenidos

**Clase [`ServiceMonitor`](#clase-servicemonitor)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`toggle_sort()`](#toggle_sortself-column-str-none)
  - [`refresh_now()`](#refresh_nowself-none)
  - [`get_services()`](#get_servicesself-listdict)
  - [`get_stats()`](#get_statsself-dict)
  - [`search_services()`](#search_servicesself-query-str-listdict)
  - [`start_service()`](#start_serviceself-name-str-tuple)
  - [`stop_service()`](#stop_serviceself-name-str-tuple)
  - [`restart_service()`](#restart_serviceself-name-str-tuple)
  - [`enable_service()`](#enable_serviceself-name-str-tuple)
  - [`disable_service()`](#disable_serviceself-name-str-tuple)
  - [`get_logs()`](#get_logsself-name-str-lines-int-50-str)
  - [`set_sort()`](#set_sortself-column-str-reverse-bool-false-none)
  - [`set_filter()`](#set_filterself-filter_type-str-none)
  - [`get_state_color()`](#get_state_colorstate-str-str)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import subprocess
import threading
from typing import List, Dict, Optional
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `SERVICES_POLL_INTERVAL` | `10` |

## Clase `ServiceMonitor`

Monitoriza servicios systemd con caché en segundo plano.

Args:
    Ninguno

Returns:
    Ninguno

Nota: Configuración inicial: 
    - sort_by: 'name' (name | state)
    - sort_reverse: False
    - filter_type: 'all' (all | active | inactive | failed)

### Atributos públicos

| Atributo | Valor inicial |
|----------|---------------|
| `sort_by` | `'name'` |
| `sort_reverse` | `False` |
| `filter_type` | `'all'` |

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |

### Métodos públicos

#### `start(self) -> None`

Inicia el servicio de monitorización en segundo plano.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `stop(self) -> None`

Detiene el sondeo de servicios limpiamente.

Args:
    None

Returns:
    None

Raises:
    None

#### `is_running(self) -> bool`

Verifica si el monitor de servicios está corriendo activamente.

Returns:
    bool: True si el monitor está activo

#### `toggle_sort(self, column: str) -> None`

Alterna el criterio de ordenación o invierte el orden actual de la columna especificada.

Args:
    column (str): Columna para ordenar, ya sea 'name' o 'state'.

Returns:
    None

Raises:
    None

#### `refresh_now(self) -> None`

Fuerza un refresco inmediato de la lista de servicios en background.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `get_services(self) -> List[Dict]`

Recupera la lista de servicios filtrados del caché.

Args:
    Ninguno

Returns:
    List[Dict]: Lista de servicios filtrados.

Raises:
    Ninguno

#### `get_stats(self) -> Dict`

Devuelve las estadísticas actuales del servicio de monitorización.

Args:
    Ninguno

Returns:
    Dict: Un diccionario con las estadísticas del servicio, incluyendo 'total', 'active', 'inactive', 'failed' y 'enabled'.

Raises:
    Ninguno

#### `search_services(self, query: str) -> List[Dict]`

Busca servicios por nombre o descripción en el caché.

Args:
    query (str): Cadena de búsqueda.

Returns:
    List[Dict]: Lista de servicios que coinciden con la búsqueda.

Raises:
    None

#### `start_service(self, name: str) -> tuple`

Inicia un servicio systemd y actualiza el estado del monitor si es exitoso.

Args:
    name: Nombre del servicio (sin extensión .service)

Returns:
    tuple: Un tupla con un booleano que indica si la operación fue exitosa y un mensaje de resultado.

Raises:
    None

#### `stop_service(self, name: str) -> tuple`

Detiene un servicio systemd y actualiza el estado del monitor si es exitoso.

Args:
    name: Nombre del servicio (sin .service)

Returns:
    tuple: (éxito, mensaje)

Raises:
    None

#### `restart_service(self, name: str) -> tuple`

Reinicia un servicio systemd y actualiza el estado del monitor si es exitoso.

Args:
    name: Nombre del servicio (sin extensión .service)

Returns:
    tuple: (éxito, mensaje) donde éxito es un booleano y mensaje es una cadena de texto.

Raises:
    None

#### `enable_service(self, name: str) -> tuple`

Habilita un servicio systemd para inicio automático.

Args:
    name: Nombre del servicio (sin .service)

Returns:
    tuple: (éxito, mensaje)

#### `disable_service(self, name: str) -> tuple`

Deshabilita un servicio systemd para evitar su inicio automático.

Args:
    name (str): Nombre del servicio (sin extensión .service)

Returns:
    tuple: Un tupla con dos elementos: éxito (bool) y mensaje (str)

Raises:
    None

#### `get_logs(self, name: str, lines: int = 50) -> str`

Obtiene los logs de un servicio específico vía journalctl.

Args:
    name (str): Nombre del servicio.
    lines (int): Número de líneas de logs a obtener (por defecto, 50).

Returns:
    str: Los logs del servicio o un mensaje de error.

Raises:
    Exception: Si ocurre un error durante la ejecución de journalctl.

#### `set_sort(self, column: str, reverse: bool = False) -> None`

Establece el criterio de ordenación de la lista de servicios.

Args:
    column (str): Columna para ordenar ('name', 'state')
    reverse (bool): Si ordenar de forma descendente (por defecto False)

Returns:
    None

Raises:
    None

#### `set_filter(self, filter_type: str) -> None`

Establece el filtro de visualización de servicios.

Args:
    filter_type (str): Tipo de filtro ('all', 'active', 'inactive', 'failed')

Returns:
    None

Raises:
    Ninguna excepción específica.

#### `get_state_color(state: str) -> str`

Obtiene el color CSS según el estado del servicio.

Args:
    state (str): Estado del servicio.

Returns:
    str: Clave de color.

Raises:
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor de servicios con configuración por defecto.

Args:
    Ninguno

Returns:
    Ninguno

Nota: Configuración inicial: 
    - sort_by: 'name' (name | state)
    - sort_reverse: False
    - filter_type: 'all' (all | active | inactive | failed)

#### `_poll_loop(self) -> None`

Ejecuta el bucle principal de sondeo en segundo plano.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_do_poll(self) -> None`

Realiza un sondeo único de servicios y actualiza los cachés internos.

Args: 
    Ninguno

Returns: 
    None

Raises: 
    Exception: Si ocurre un error durante el sondeo o el cálculo de estadísticas.

#### `_fetch_services(self) -> List[Dict]`

Obtiene la lista de servicios del sistema mediante una llamada a systemctl.

Args: 
    Ninguno

Returns:
    List[Dict]: Lista de servicios, donde cada servicio es un diccionario.

Raises:
    Ninguna excepción relevante.

#### `_fetch_enabled_batch(self, units: List[str]) -> set`

Obtiene el conjunto de servicios habilitados a partir de una lista de unidades.

Args:
    units: Lista de nombres de unidades de servicio.

Returns:
    Un conjunto de nombres de unidades de servicio que están habilitados.

Raises:
    Exception: Si ocurre un error al ejecutar el comando systemctl.

#### `_compute_stats(self, services: List[Dict]) -> Dict`

Calcula estadísticas resumidas a partir de la lista de servicios.

Args:
    services (List[Dict]): Lista de diccionarios de servicios

Returns:
    Dict: Conteo de servicios total, activos, inactivos, fallidos y habilitados.

Raises:
    Ninguna excepción explícita.

#### `_run_systemctl(self, action: str, name: str, sudo: bool = True) -> tuple`

Ejecuta un comando systemctl y devuelve el resultado.

Args:
    action (str): Acción a realizar ('start', 'stop', 'restart', 'enable', 'disable').
    name (str): Nombre del servicio (sin extensión .service).
    sudo (bool): Indica si se debe utilizar sudo (por defecto True).

Returns:
    tuple: Un tupla con dos elementos: éxito (bool) y mensaje descriptivo (str).

Raises:
    Exception: Si ocurre un error durante la ejecución del comando.

</details>
