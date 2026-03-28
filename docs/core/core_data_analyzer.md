# `core.data_analyzer`

> **Ruta**: `core/data_analyzer.py`

> **Cobertura de documentación**: 🟢 100% (16/16)

Análisis de datos históricos

---

## Tabla de contenidos

**Clase [`DataAnalyzer`](#clase-dataanalyzer)**
  - [`get_data_range()`](#get_data_rangeself-hours-int-24-listdict)
  - [`get_stats()`](#get_statsself-hours-int-24-dict)
  - [`get_graph_data()`](#get_graph_dataself-metric-str-hours-int-24-tuplelist-list)
  - [`export_to_csv()`](#export_to_csvself-output_path-str-hours-int-24)
  - [`get_data_range_between()`](#get_data_range_betweenself-start-datetime-end-datetime-listdict)
  - [`get_stats_between()`](#get_stats_betweenself-start-datetime-end-datetime-dict)
  - [`get_graph_data_between()`](#get_graph_data_betweenself-metric-str-start-datetime-end-datetime-tuplelist-list)
  - [`export_to_csv_between()`](#export_to_csv_betweenself-output_path-str-start-datetime-end-datetime)
  - [`detect_anomalies()`](#detect_anomaliesself-hours-int-24-listdict)

---

## Dependencias internas

- `config.settings`
- `utils.logger`

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

Convierte un objeto datetime a una cadena de caracteres sin microsegundos.
Args:
    dt (datetime): Fecha y hora a convertir.
Returns:
    str: Representación en cadena de la fecha y hora en el formato utilizado por la base de datos.

</details>

## Clase `DataAnalyzer`

Analiza datos históricos de la base de datos.

Args:
    db_path (str): Ruta a la BD de métricas.

Returns:
    None

Raises:
    Exception: Si ocurre un error al conectar con la base de datos.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_db_path` | `db_path` |

### Métodos públicos

#### `get_data_range(self, hours: int = 24) -> List[Dict]`

Obtiene datos de las últimas X horas.

Args:
    hours (int): Número de horas a considerar, por defecto 24.

Returns:
    List[Dict]: Lista de diccionarios con los datos obtenidos.

Raises:
    sqlite3.OperationalError: Error en la operación con la base de datos.
    Exception: Error inesperado.

#### `get_stats(self, hours: int = 24) -> Dict`

Obtiene estadísticas de las últimas horas especificadas.

Args:
    hours (int): Número de horas a considerar, por defecto 24.

Returns:
    Dict: Diccionario con las estadísticas calculadas.

#### `get_graph_data(self, metric: str, hours: int = 24) -> Tuple[List, List]`

Obtiene datos para gráficas en un rango de tiempo determinado.

Args:
    metric (str): Métrica a extraer de los datos.
    hours (int): Número de horas a considerar (por defecto 24).

Returns:
    Tuple[List, List]: Datos para la gráfica.

Raises:
    Exception: Si ocurre un error durante la extracción de datos.

#### `export_to_csv(self, output_path: str, hours: int = 24)`

Exporta datos a un archivo CSV para un rango de horas especificado.

Args:
    output_path (str): Ruta del archivo de salida CSV.
    hours (int): Número de horas de datos a exportar (por defecto 24).

Returns:
    None

Raises:
    FileNotFoundError: Si la ruta de salida no es válida.

#### `get_data_range_between(self, start: datetime, end: datetime) -> List[Dict]`

Obtiene datos de métricas entre dos fechas exactas.

Args:
    start (datetime): Fecha de inicio.
    end (datetime): Fecha de fin.

Returns:
    List[Dict]: Lista de diccionarios con los datos obtenidos.

Raises:
    sqlite3.OperationalError: Error de operación en la base de datos.
    Exception: Error inesperado.

#### `get_stats_between(self, start: datetime, end: datetime) -> Dict`

Obtiene estadísticas de los datos analizados dentro de un rango de fechas específico.

Args:
    start (datetime): Fecha de inicio del rango.
    end (datetime): Fecha de fin del rango.

Returns:
    Dict: Diccionario que contiene las estadísticas calculadas.

Raises:
    ValueError: Si la fecha de inicio es posterior a la fecha de fin.

#### `get_graph_data_between(self, metric: str, start: datetime, end: datetime) -> Tuple[List, List]`

Obtiene datos para gráficas de una métrica específica entre dos fechas exactas.

Args:
    metric (str): Métrica a obtener.
    start (datetime): Fecha de inicio.
    end (datetime): Fecha de fin.

Returns:
    Tuple[List, List]: Datos para la gráfica.

Raises:
    Exception: Si ocurre un error al obtener los datos.

#### `export_to_csv_between(self, output_path: str, start: datetime, end: datetime)`

Exporta datos a un archivo CSV dentro de un rango de fechas específico.

Args:
    output_path (str): Ruta de salida del archivo CSV.
    start (datetime): Fecha de inicio del rango de datos.
    end (datetime): Fecha de fin del rango de datos.

Returns:
    None

Raises:
    FileNotFoundError: Si la ruta de salida no es válida.

#### `detect_anomalies(self, hours: int = 24) -> List[Dict]`

Detecta anomalías en los datos de los últimos horas especificadas.

Args:
    hours (int): Número de horas a considerar para la detección de anomalías (por defecto 24).

Returns:
    List[Dict]: Lista de diccionarios que describen las anomalías detectadas.

Raises:
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self, db_path: str = f'{DATA_DIR}/history.db')`

Inicializa el analizador de datos con una ruta a la base de datos.

Args:
    db_path (str): Ruta a la BD de métricas (por defecto, DATA_DIR/history.db).

#### `_get_stats_between(self, start: datetime, end: datetime) -> Dict`

Obtiene estadísticas de métricas entre dos fechas específicas.

Args:
    start (datetime): Fecha de inicio del rango.
    end (datetime): Fecha de fin del rango.

Returns:
    Dict: Diccionario con estadísticas del rango de fechas.

Raises:
    sqlite3.Error: Si ocurre un error en la conexión a la base de datos.

#### `_extract_metric(self, data: List[Dict], metric: str) -> Tuple[List, List]`

Extrae timestamps y valores de una métrica de una lista de datos.

Args:
    data (List[Dict]): Lista de diccionarios con datos.
    metric (str): Nombre de la métrica a extraer.

Returns:
    Tuple[List, List]: Tupla con listas de timestamps y valores.

Raises:
    ValueError: Si el formato de timestamp es inválido.

#### `_write_csv(self, output_path: str, data: List[Dict])`

Escribe una lista de registros a un archivo CSV.

Args:
    output_path (str): Ruta del archivo de salida.
    data (List[Dict]): Lista de registros a escribir.

Returns:
    None

Raises:
    OSError: Si ocurre un error al escribir el archivo.

#### `_format_uptime(self, seconds: float) -> str`

Convierte tiempo en segundos a un formato legible D:HH:MM.

Args:
    seconds (float): Tiempo en segundos.

Returns:
    str: Tiempo formateado como D:HH:MM.

Raises:
    None

</details>
