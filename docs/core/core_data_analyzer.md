# `core.data_analyzer`

> **Ruta**: `core/data_analyzer.py`

Análisis de datos históricos

## Imports

```python
import sqlite3
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from config.settings import DATA_DIR
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

<details>
<summary>Funciones privadas</summary>

### `_fmt(dt: datetime) -> str`

Convierte datetime a string sin microsegundos, formato que usa la BD.

</details>

## Clase `DataAnalyzer`

Analiza datos históricos de la base de datos

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_db_path` | `db_path` |

### Métodos públicos

#### `get_data_range(self, hours: int = 24) -> List[Dict]`

Obtiene datos de las últimas X horas

#### `get_stats(self, hours: int = 24) -> Dict`

Obtiene estadísticas de las últimas X horas

#### `get_graph_data(self, metric: str, hours: int = 24) -> Tuple[List, List]`

Obtiene datos para gráficas (últimas X horas)

#### `export_to_csv(self, output_path: str, hours: int = 24)`

Exporta datos a CSV (últimas X horas)

#### `get_data_range_between(self, start: datetime, end: datetime) -> List[Dict]`

Obtiene datos entre dos fechas exactas

#### `get_stats_between(self, start: datetime, end: datetime) -> Dict`

Obtiene estadísticas entre dos fechas exactas

#### `get_graph_data_between(self, metric: str, start: datetime, end: datetime) -> Tuple[List, List]`

Obtiene datos para gráficas entre dos fechas exactas

#### `export_to_csv_between(self, output_path: str, start: datetime, end: datetime)`

Exporta datos a CSV entre dos fechas exactas

#### `detect_anomalies(self, hours: int = 24) -> List[Dict]`

Detecta anomalías en los datos

<details>
<summary>Métodos privados</summary>

#### `__init__(self, db_path: str = f'{DATA_DIR}/history.db')`

Inicializa DataAnalyzer.

Args:
    db_path (str): Ruta a la BD de métricas (default DATA_DIR/history.db).

#### `_get_stats_between(self, start: datetime, end: datetime) -> Dict`

Lógica común de estadísticas para cualquier rango start→end.

#### `_extract_metric(self, data: List[Dict], metric: str) -> Tuple[List, List]`

Extrae timestamps y valores de una métrica.

#### `_write_csv(self, output_path: str, data: List[Dict])`

Escribe una lista de registros a CSV.

#### `_format_uptime(self, seconds: float) -> str`

Convierte segundos brutos (float/int) a formato D:HH:MM.

</details>
