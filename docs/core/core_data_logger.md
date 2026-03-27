# `core.data_logger`

> **Ruta**: `core/data_logger.py`

Sistema de logging de datos históricos

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

Registra datos del sistema en base de datos SQLite

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_db_path` | `db_path` |
| `_dashboard_logger` | `DashboardLogger()` |

### Métodos públicos

#### `log_metrics(self, metrics: Dict)`

Guarda un conjunto de métricas.
La timestamp se genera con datetime.now() para usar la hora local del sistema,
evitando el desfase UTC que produce DEFAULT CURRENT_TIMESTAMP de SQLite.

#### `log_event(self, event_type: str, severity: str, message: str, data: Dict = None)`

Registra evento (alerta/log) en tabla events.

Args:
    event_type (str): e.g. 'service_restart'
    severity (str): 'info', 'warning', 'error'
    message (str): Descripción
    data (Dict, optional): Datos extra JSON.

Timestamp local automática.

#### `get_metrics_count(self) -> int`

Cuenta total registros en tabla metrics.

Returns:
    int: Número de entradas históricas.

#### `get_db_size_mb(self) -> float`

Retorna tamaño archivo history.db en MB.

Returns:
    float: Tamaño MB o 0 si no existe.

#### `clean_old_data(self, days: int = 30)`

Borra métricas/events > days antiguos + VACUUM optimizar.

Args:
    days (int): Retener últimos N días (default 30).

#### `check_and_rotate_db(self, max_mb: float = 5.0)`

Chequea tamaño DB > max_mb y auto-limpia si necesario.

Args:
    max_mb (float): Límite tamaño MB (default 5).

<details>
<summary>Métodos privados</summary>

#### `__init__(self, db_path: str = 'data/history.db')`

Inicializa DataLogger con BD SQLite.

Args:
    db_path (str): Ruta BD (default data/history.db).

Crea tablas, chequea rotación automática.

#### `_init_database(self)`

Crea tablas metrics/events si no existen + índice timestamp.

Tabla metrics: Histórico sistema cada UPDATE_MS.
Tabla events: Alertas/log eventos.

</details>
