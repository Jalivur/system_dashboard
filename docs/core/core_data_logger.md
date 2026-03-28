# `core.data_logger`

> **Ruta**: `core/data_logger.py`

> **Cobertura de documentación**: 🟢 100% (9/9)

Sistema de logging de datos históricos

---

## Tabla de contenidos

**Clase [`DataLogger`](#clase-datalogger)**
  - [`log_metrics()`](#log_metricsself-metrics-dict)
  - [`log_event()`](#log_eventself-event_type-str-severity-str-message-str-data-dict-none)
  - [`get_metrics_count()`](#get_metrics_countself-int)
  - [`get_db_size_mb()`](#get_db_size_mbself-float)
  - [`clean_old_data()`](#clean_old_dataself-days-int-30)
  - [`check_and_rotate_db()`](#check_and_rotate_dbself-max_mb-float-50)

---

## Dependencias internas

- `utils`

## Imports

```python
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict
from utils import DashboardLogger
```

## Clase `DataLogger`

Clase para registrar datos del sistema en una base de datos SQLite.

Args:
    db_path (str): Ruta de la base de datos (por defecto "data/history.db").

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_db_path` | `db_path` |
| `_dashboard_logger` | `DashboardLogger()` |

### Métodos públicos

#### `log_metrics(self, metrics: Dict)`

Guarda un conjunto de métricas en la base de datos.

Args:
    metrics (Dict): Diccionario con las métricas a guardar.

Returns:
    None

Raises:
    sqlite3.Error: Si ocurre un error al conectar o ejecutar la consulta en la base de datos.

#### `log_event(self, event_type: str, severity: str, message: str, data: Dict = None)`

Registra un evento en la tabla de eventos.

Args:
    event_type (str): Tipo de evento, por ejemplo 'service_restart'.
    severity (str): Nivel de gravedad, puede ser 'info', 'warning' o 'error'.
    message (str): Descripción del evento.
    data (Dict, optional): Datos adicionales en formato JSON.

Returns:
    None

Raises:
    None

#### `get_metrics_count(self) -> int`

Obtiene el número total de registros en la tabla de métricas.

Args:
    No aplica.

Returns:
    int: Número de entradas históricas.

Raises:
    No aplica.

#### `get_db_size_mb(self) -> float`

Retorna el tamaño del archivo de base de datos en megabytes.

Args:
    No aplica.

Returns:
    float: Tamaño en megabytes o 0 si el archivo no existe.

#### `clean_old_data(self, days: int = 30)`

Elimina datos antiguos y optimiza la base de datos.

Args:
    days (int): Número de días para retener los datos (por defecto 30).

Returns:
    None

Raises:
    sqlite3.Error: Si ocurre un error en la conexión a la base de datos.

#### `check_and_rotate_db(self, max_mb: float = 5.0)`

Verifica si el tamaño de la base de datos supera el límite establecido y la limpia automáticamente si es necesario.

Args:
    max_mb (float): Límite de tamaño en megabytes (por defecto 5.0).

Returns:
    None

Raises:
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self, db_path: str = 'data/history.db')`

Inicializa el registrador de datos con una base de datos SQLite.

Args:
    db_path (str): Ruta de la base de datos (por defecto 'data/history.db').

Returns:
    None

Raises:
    None

#### `_init_database(self)`

Inicializa la base de datos creando las tablas necesarias si no existen.

Args:
    None

Returns:
    None

Raises:
    None

</details>
