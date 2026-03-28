# `core.service_watchdog`

> **Ruta**: `core/service_watchdog.py`

> **Cobertura de documentación**: 🟢 100% (15/15)

Service Watchdog v4.2 — Auto-restart servicios críticos del sistema (FIXED: maneja inactive).

Monitoriza servicios críticos definidos en local_settings.py.
Cada SERVICE_WATCHDOG_INTERVAL segs (default 60s), chequea si NO active consecutivas >= THRESHOLD (default 3).
Si sí, auto-restart via service_monitor + log/alert + reset counter.

Uso:
  wd = ServiceWatchdog(service_monitor)
  wd.start()
  registry.register('service_watchdog', wd)

---

## Tabla de contenidos

**Clase [`ServiceWatchdog`](#clase-servicewatchdog)**
  - [`start()`](#startself)
  - [`stop()`](#stopself)
  - [`is_running()`](#is_runningself-bool)
  - [`set_critical_services()`](#set_critical_servicesself-services-liststr)
  - [`set_threshold()`](#set_thresholdself-thresh-int)
  - [`set_interval()`](#set_intervalself-interval-int)
  - [`add_critical_service()`](#add_critical_serviceself-name-str-bool)
  - [`get_stats()`](#get_statsself-dict)

---

## Dependencias internas

- `config.local_settings_io`
- `config.settings`
- `core.service_monitor`
- `utils.logger`

## Imports

```python
import threading
import time
from typing import Dict, List
from pathlib import Path
import json
from utils.logger import get_logger
from config.settings import SERVICE_WATCHDOG_INTERVAL, SERVICE_WATCHDOG_THRESHOLD
from config.local_settings_io import get_param, update_params
from core.service_monitor import ServiceMonitor
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `DATA_DIR` | `Path(__file__).parent.parent / 'data'` |
| `WD_STATE_FILE` | `DATA_DIR / 'service_watchdog_state.json'` |

## Clase `ServiceWatchdog`

Inicializa el watchdog para monitoreo y auto-reinicio de servicios críticos.

Args:
    service_monitor (ServiceMonitor): Instancia para operaciones de servicio.

Características:
    * Verificación periódica del estado 'active' cada INTERVAL segundos.
    * Reinicio automático al superar THRESHOLD fallos consecutivos.
    * Persistencia de contadores de reinicios diarios.

Raises:
    Exception: Si la inicialización falla.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_service_monitor` | `service_monitor` |
| `_threshold` | `get_param('watchdog_threshold', SERVICE_WATCHDOG_THRESHOLD)` |
| `_interval` | `get_param('watchdog_interval', SERVICE_WATCHDOG_INTERVAL)` |
| `_running` | `False` |
| `_stop_event` | `threading.Event()` |

### Métodos públicos

#### `start(self)`

Inicia el hilo de monitoreo del watchdog en background.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `stop(self)`

Detiene el watchdog limpiamente y persiste estado.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `is_running(self) -> bool`

Verifica si el watchdog está activo.

Args:
    None

Returns:
    bool: True si el servicio está corriendo.

Raises:
    None

#### `set_critical_services(self, services: List[str])`

Establece la lista de servicios críticos que serán monitoreados por el watchdog.

Args:
    services (List[str]): Lista de nombres de servicios críticos.

Returns:
    None

Raises:
    None

#### `set_threshold(self, thresh: int)`

Establece el umbral de fallos consecutivos para auto-restart.

Args:
    thresh (int): Número de fallos seguidos.

Raises:
    None
Returns:
    None

#### `set_interval(self, interval: int)`

Establece el intervalo de tiempo en segundos entre chequeos del servicio.

Args:
    interval (int): Intervalo en segundos entre chequeos.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno

#### `add_critical_service(self, name: str) -> bool`

Añade un servicio crítico si no existe ya.

Args:
    name (str): Nombre del servicio systemd.

Returns:
    bool: True si el servicio fue añadido, False si ya estaba registrado.

#### `get_stats(self) -> Dict`

Obtiene estadísticas del watchdog para UI.

Returns:
    Dict: Diccionario con contadores de servicios críticos, 
          número de reinicios hoy, lista de servicios, 
          umbral de reinicio, intervalo, estado de ejecución, 
          conteo de reinicios y fallos consecutivos.

Raises:
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self, service_monitor: ServiceMonitor)`

Inicializa el ServiceWatchdog con la instancia de ServiceMonitor proporcionada.

Args:
    service_monitor (ServiceMonitor): Instancia para reiniciar servicios.

Inicializa contadores de reinicios y fallos, carga estado persistido y configura parámetros.

#### `_watch_loop(self)`

Bucle principal privado del watchdog que monitorea servicios a intervalos regulares.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_check_services(self)`

Verifica el estado de los servicios críticos y actualiza los contadores de fallos.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_auto_restart(self, name: str)`

Reinicia automáticamente un servicio crítico mediante el service_monitor y actualiza los contadores de reinicios.

Args:
    name (str): Nombre del servicio a reiniciar.

Raises:
    None

Returns:
    None

#### `_persist_state(self)`

Guarda el estado actual del watchdog en un archivo persistente.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_load_state(self)`

Carga los contadores del día desde el archivo JSON persistido y resetea automáticamente si es un nuevo día.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

</details>
