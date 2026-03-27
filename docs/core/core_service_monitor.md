# `core.service_monitor`

> **Ruta**: `core/service_monitor.py`

Monitor de servicios systemd

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

Monitor de servicios systemd con caché en background.

El método get_services() en versiones anteriores lanzaba systemctl
en el hilo de UI cada 2s, bloqueando Tkinter. Ahora:
- Un thread de background sondea systemctl cada 10s.
- get_services() y get_stats() devuelven el caché sin bloquear.
- La ventana ServiceWindow puede forzar un refresco con refresh_now().

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

Arranca el sondeo en background (llamado automáticamente en __init__).

#### `stop(self) -> None`

Detiene el sondeo limpiamente.

#### `is_running(self) -> bool`

Verifica si el monitor de servicios está corriendo activamente.

Returns:
    bool: True si el sondeo está activo

#### `toggle_sort(self, column: str) -> None`

Alterna el criterio de ordenación o invierte el orden actual.

Args:
    column: Columna para ordenar ('name', 'state')

#### `refresh_now(self) -> None`

Fuerza un refresco inmediato de la lista de servicios en background.
Útil para actualizar datos sin esperar al intervalo de sondeo.

#### `get_services(self) -> List[Dict]`

Devuelve la lista del caché aplicando filtro. No bloquea el hilo de UI.

#### `get_stats(self) -> Dict`

Devuelve las estadísticas del caché. No bloquea el hilo de UI.

#### `search_services(self, query: str) -> List[Dict]`

Busca servicios por nombre o descripción (en el caché).

#### `start_service(self, name: str) -> tuple`

Inicia un servicio systemd.

Args:
    name: Nombre del servicio (sin .service)

Returns:
    tuple: (éxito, mensaje)

#### `stop_service(self, name: str) -> tuple`

Detiene un servicio systemd.

Args:
    name: Nombre del servicio (sin .service)

Returns:
    tuple: (éxito, mensaje)

#### `restart_service(self, name: str) -> tuple`

Reinicia un servicio systemd.

Args:
    name: Nombre del servicio (sin .service)

Returns:
    tuple: (éxito, mensaje)

#### `enable_service(self, name: str) -> tuple`

Habilita un servicio systemd para inicio automático.

Args:
    name: Nombre del servicio (sin .service)

Returns:
    tuple: (éxito, mensaje)

#### `disable_service(self, name: str) -> tuple`

Deshabilita un servicio systemd para evitar inicio automático.

Args:
    name: Nombre del servicio (sin .service)

Returns:
    tuple: (éxito, mensaje)

#### `get_logs(self, name: str, lines: int = 50) -> str`

Obtiene logs de un servicio vía journalctl.

#### `set_sort(self, column: str, reverse: bool = False) -> None`

Establece el criterio de ordenación de la lista de servicios.

Args:
    column: Columna para ordenar ('name', 'state')
    reverse: Si ordenar de forma descendente (por defecto False)

#### `set_filter(self, filter_type: str) -> None`

Establece el filtro de visualización de servicios.

Args:
    filter_type: Tipo de filtro ('all', 'active', 'inactive', 'failed')

#### `get_state_color(state: str) -> str`

Obtiene el color CSS según el estado del servicio.

Args:
    state: Estado del servicio ('active', 'inactive', 'failed', etc.)

Returns:
    Clave de color ('success', 'danger', 'text_dim')

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor de servicios con configuración por defecto.

Configuración inicial:
- sort_by: 'name' (name | state)
- sort_reverse: False
- filter_type: 'all' (all | active | inactive | failed)

#### `_poll_loop(self) -> None`

Bucle principal de sondeo en background (método privado).
Se ejecuta cada SERVICES_POLL_INTERVAL segundos.

#### `_do_poll(self) -> None`

Realiza un sondeo único de servicios y actualiza los cachés (método privado).

#### `_fetch_services(self) -> List[Dict]`

Obtiene la lista de servicios con una sola llamada a systemctl
y enriquece con el estado enabled en una segunda llamada batch.

#### `_fetch_enabled_batch(self, units: List[str]) -> set`

Obtiene el estado enabled dividiendo en chunks para evitar
timeout en sistemas lentos (Pi 3B+) con muchos servicios.

#### `_compute_stats(self, services: List[Dict]) -> Dict`

Calcula estadísticas resumidas a partir de la lista de servicios (método privado).

Args:
    services: Lista de diccionarios de servicios

Returns:
    Dict con conteos: total, active, inactive, failed, enabled

#### `_run_systemctl(self, action: str, name: str, sudo: bool = True) -> tuple`

Ejecuta un comando systemctl y devuelve resultado (método privado).

Args:
    action: Acción ('start', 'stop', 'restart', 'enable', 'disable')
    name: Nombre del servicio (sin .service)
    sudo: Si usar sudo (por defecto True, False para enable/disable)

Returns:
    tuple: (éxito, mensaje descriptivo)

</details>
