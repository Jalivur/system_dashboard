# `core.service_watchdog`

> **Ruta**: `core/service_watchdog.py`

Service Watchdog v4.2 — Auto-restart servicios críticos del sistema (FIXED: maneja inactive).

Monitoriza servicios críticos definidos en local_settings.py.
Cada SERVICE_WATCHDOG_INTERVAL segs (default 60s), chequea si NO active consecutivas >= THRESHOLD (default 3).
Si sí, auto-restart via service_monitor + log/alert + reset counter.

Uso:
  wd = ServiceWatchdog(service_monitor)
  wd.start()
  registry.register('service_watchdog', wd)

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

Watchdog profesional para monitoreo y auto-reinicio de servicios críticos systemd.

Características principales:
* Verificación periódica del estado 'active' cada INTERVAL segundos (predeterminado: 60s).
* Reinicio automático al superar THRESHOLD fallos consecutivos (predeterminado: 3).
* Persistencia de contadores de reinicios diarios en data/service_watchdog_state.json.
* Configuración dinámica mediante parámetros en local_settings.py:
  - watchdog_critical_services: Lista de servicios críticos.
  - watchdog_threshold: Umbral de fallos.
  - watchdog_interval: Intervalo de polling.
* Logging detallado con niveles INFO/WARNING y estadísticas exportables para UI/dashboard.
* Ejecución en thread daemon no bloqueante con métodos start/stop limpios (join con timeout 5s).
* Manejo robusto de errores: servicios no encontrados, JSON corrupto, etc.
* Reset automático de contadores al cambiar de día.

Uso recomendado:
    wd = ServiceWatchdog(service_monitor)
    wd.start()
    # Opcional: registry.register('service_watchdog', wd)

Dependencias: ServiceMonitor para operaciones de servicio, utils.logger, config.local_settings_io.
Compatible con systemd servicios.

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

Inicia el hilo de monitoreo del watchdog en background (daemon).

Pollea cada self._interval segs los servicios críticos.

#### `stop(self)`

Detiene el watchdog limpiamente y persiste estado.

Espera hasta 5s al thread, guarda restarts del día.

#### `is_running(self) -> bool`

Verifica si el watchdog está activo.

Returns:
    bool: True si el thread está corriendo.

#### `set_critical_services(self, services: List[str])`

Actualiza la lista de servicios críticos a monitorear.

Args:
    services (List[str]): Nuevos nombres de servicios críticos.

#### `set_threshold(self, thresh: int)`

Cambia el umbral de fallos consecutivos para auto-restart.

Args:
    thresh (int): Número de fallos seguidos (default 3).

#### `set_interval(self, interval: int)`

Cambia el intervalo de polling en segundos.

Args:
    interval (int): Segundos entre chequeos (default 60).

#### `add_critical_service(self, name: str) -> bool`

Añade un servicio crítico si no existe ya.

Args:
    name (str): Nombre del servicio systemd.

Returns:
    bool: True si añadido, False si ya estaba.

#### `get_stats(self) -> Dict`

Obtiene estadísticas del watchdog para UI.

Returns:
    Dict: Counters restarts, servicios, estado, etc.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, service_monitor: ServiceMonitor)`

Inicializa el ServiceWatchdog.

Args:
    service_monitor (ServiceMonitor): Instancia para restart servicios.

Inicializa counters de restarts/fallos, carga estado persistido.

#### `_watch_loop(self)`

Bucle principal privado del watchdog (thread daemon).
Espera self._interval y chequea servicios.

#### `_check_services(self)`

Chequea estado de servicios críticos, incrementa counters fallos.
Si >= threshold, trigger auto_restart().

#### `_auto_restart(self, name: str)`

Reinicia servicio crítico via service_monitor y actualiza counters.

#### `_persist_state(self)`

Guarda counters restarts en data/service_watchdog_state.json (diario).

#### `_load_state(self)`

Carga counters del día desde JSON persistido.
Reset automático si nuevo día.

</details>
