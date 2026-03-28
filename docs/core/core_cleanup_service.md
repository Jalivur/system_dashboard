# `core.cleanup_service`

> **Ruta**: `core/cleanup_service.py`

> **Cobertura de documentación**: 🟢 100% (15/15)

Servicio de limpieza automática de archivos exportados y datos antiguos

---

## Tabla de contenidos

**Clase [`CleanupService`](#clase-cleanupservice)**
  - [`start()`](#startself)
  - [`stop()`](#stopself)
  - [`is_running()`](#is_runningself-bool)
  - [`clean_csv()`](#clean_csvself-max_files-int-none-int)
  - [`clean_png()`](#clean_pngself-max_files-int-none-int)
  - [`clean_log_exports()`](#clean_log_exportsself-max_files-int-none-int)
  - [`clean_db()`](#clean_dbself-days-int-none-bool)
  - [`get_status()`](#get_statusself-dict)
  - [`force_cleanup()`](#force_cleanupself-dict)

---

## Dependencias internas

- `config.settings`
- `utils.logger`

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

Servicio de limpieza que elimina periódicamente archivos exportados y datos antiguos de la base de datos de manera segura en segundo plano.

Args:
    None

Returns:
    None

Raises:
    None

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

Inicia el servicio de limpieza en segundo plano.

Args:
    None

Returns:
    None

Raises:
    None

#### `stop(self)`

Detiene el servicio de limpieza.

Args:
    None

Returns:
    None

Raises:
    None

#### `is_running(self) -> bool`

Verifica si el servicio de limpieza está en ejecución.

Args:
    None

Returns:
    bool: True si el servicio está corriendo, False de lo contrario.

Raises:
    None

#### `clean_csv(self, max_files: int = None) -> int`

Elimina los archivos CSV de exportación más antiguos que superen el límite especificado.

Args:
    max_files: Límite de archivos a conservar. Si es None, se utiliza el valor por defecto.

Returns:
    Número de archivos CSV eliminados.

Raises:
    None

#### `clean_png(self, max_files: int = None) -> int`

Elimina los PNG exportados más antiguos que superen el límite configurado.

Args:
    max_files (int): Límite de archivos a conservar. Si es None, se utiliza el valor por defecto.

Returns:
    int: Número de archivos PNG eliminados.

Raises:
    None

#### `clean_log_exports(self, max_files: int = None) -> int`

Elimina los archivos de exportación de logs más antiguos que superen el límite.

Args:
    max_files (int): Límite a aplicar. Si es None, se utiliza el valor predeterminado.

Returns:
    int: Número de archivos eliminados.

Raises:
    None

#### `clean_db(self, days: int = None) -> bool`

Elimina registros de la base de datos más antiguos que un número determinado de días.

Args:
    days (int): Número de días. Si es None, se utiliza el valor por defecto configurado.

Returns:
    bool: True si la limpieza fue exitosa.

Raises:
    Exception: Si ocurre un error durante la limpieza de la base de datos.

#### `get_status(self) -> dict`

Devuelve el estado actual del servicio de limpieza.
Args: 
    None
Returns:
    dict: Diccionario con la configuración y el estado del hilo de limpieza.
        Contiene información sobre el estado de ejecución, intervalos y conteo de archivos.
Raises: 
    None

#### `force_cleanup(self) -> dict`

Fuerza un ciclo de limpieza inmediato de archivos y base de datos.

Args: None

Returns:
    dict: Diccionario con el número de archivos eliminados y resultado de la limpieza de base de datos.

Raises: None

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

#### `__init__(self, data_logger = None, max_csv: int = DEFAULT_MAX_CSV, max_png: int = DEFAULT_MAX_PNG, max_log: int = DEFAULT_MAX_LOG, db_days: int = DEFAULT_DB_DAYS, interval_hours: float = DEFAULT_INTERVAL_HOURS)`

Inicializa el servicio de limpieza con los parámetros especificados.

Args:
    data_logger: Instancia de DataLogger para limpiar la BD.
    max_csv: Número máximo de CSV exportados a conservar.
    max_png: Número máximo de PNG exportados a conservar.
    max_log: Número máximo de logs exportados a conservar.
    db_days: Días de histórico a conservar en la BD.
    interval_hours: Horas entre ejecuciones del ciclo de limpieza.

#### `_run(self)`

Ejecuta el ciclo de limpieza inicial y luego cada intervalo de horas configurado.

Args:
    None

Returns:
    None

Raises:
    None

#### `_cleanup_cycle(self)`

Ejecuta un ciclo completo de limpieza.

Args:
    Ninguno.

Returns:
    Ninguno.

Raises:
    Ninguno.

#### `_trim_files(self, pattern: str, max_files: int, label: str) -> int`

Elimina los archivos más antiguos que superen el número máximo permitido según un patrón.

Args:
    pattern (str): Patrón glob de los archivos a gestionar.
    max_files (int): Número máximo de archivos a conservar.
    label (str): Etiqueta para el log.

Returns:
    int: Número de archivos eliminados.

Raises:
    Exception: Si ocurre un error durante la eliminación de archivos.

</details>
