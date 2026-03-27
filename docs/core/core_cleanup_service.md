# `core.cleanup_service`

> **Ruta**: `core/cleanup_service.py`

Servicio de limpieza automática de archivos exportados y datos antiguos

## Imports

```python
import os
import glob
import threading
import time
from typing import Optional
from config.settings import DATA_DIR, EXPORTS_CSV_DIR, EXPORTS_LOG_DIR, EXPORTS_SCR_DIR
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `CleanupService`

Servicio background que limpia periódicamente archivos exportados
y datos antiguos de la base de datos.

Características:
- Singleton: Solo una instancia en toda la aplicación
- Thread-safe: Seguro para concurrencia
- Daemon: Se cierra automáticamente con el programa
- Configurable: límites de archivos y antigüedad ajustables

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_data_logger` | `data_logger` |
| `_max_csv` | `max_csv` |
| `_max_png` | `max_png` |
| `_max_log` | `max_log` |
| `_db_days` | `db_days` |
| `_interval_hours` | `interval_hours` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_initialized` | `True` |

### Métodos públicos

#### `start(self)`

Inicia el servicio en segundo plano.

#### `stop(self)`

Detiene el servicio.

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo.

#### `clean_csv(self, max_files: int = None) -> int`

Elimina los CSV exportados más antiguos que superen el límite.

Args:
    max_files: Límite a aplicar. Si es None usa self._max_csv.

Returns:
    Número de archivos eliminados.

#### `clean_png(self, max_files: int = None) -> int`

Elimina los PNG exportados más antiguos que superen el límite.

Args:
    max_files: Límite a aplicar. Si es None usa self._max_png.

Returns:
    Número de archivos eliminados.

#### `clean_log_exports(self, max_files: int = None) -> int`

Elimina los archivos de exportación de logs más antiguos que superen el límite.

Args:
    max_files: Límite a aplicar. Si es None usa self._max_log.

Returns:
    Número de archivos eliminados.

#### `clean_db(self, days: int = None) -> bool`

Elimina registros de la BD más antiguos que 'days' días.

Args:
    days: Antigüedad máxima. Si es None usa self._db_days.

Returns:
    True si la limpieza fue exitosa.

#### `get_status(self) -> dict`

Devuelve el estado actual del servicio.

Returns:
    Diccionario con configuración y estado del hilo.

#### `force_cleanup(self) -> dict`

Fuerza un ciclo de limpieza inmediato desde fuera del hilo.

Returns:
    Diccionario con el número de archivos eliminados y resultado de BD.

<details>
<summary>Métodos privados</summary>

#### `__new__(cls, *args, **kwargs)`

Implementa patrón singleton thread-safe.

#### `__init__(self, data_logger = None, max_csv: int = DEFAULT_MAX_CSV, max_png: int = DEFAULT_MAX_PNG, max_log: int = DEFAULT_MAX_LOG, db_days: int = DEFAULT_DB_DAYS, interval_hours: float = DEFAULT_INTERVAL_HOURS)`

Inicializa el servicio (solo la primera vez).

Args:
    data_logger:     Instancia de DataLogger para limpiar la BD.
                     Si es None, solo se limpian archivos.
    max_csv:         Número máximo de CSV exportados a conservar.
    max_png:         Número máximo de PNG exportados a conservar.
    max_log:         Número máximo de logs exportados a conservar.
    db_days:         Días de histórico a conservar en la BD.
    interval_hours:  Horas entre ejecuciones del ciclo de limpieza.

#### `_run(self)`

Bucle principal: limpia al arrancar y luego cada interval_hours.

#### `_cleanup_cycle(self)`

Ejecuta un ciclo completo de limpieza.

#### `_trim_files(self, pattern: str, max_files: int, label: str) -> int`

Elimina los archivos más antiguos que superen max_files.

Args:
    pattern:   Patrón glob de los archivos a gestionar.
    max_files: Número máximo a conservar.
    label:     Etiqueta para el log.

Returns:
    Número de archivos eliminados.

</details>
