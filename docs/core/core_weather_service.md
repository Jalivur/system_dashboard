# `core.weather_service`

> **Ruta**: `core/weather_service.py`

> **Cobertura de documentación**: 🟢 100% (22/22)

Servicio de datos meteorológicos via Open-Meteo (gratuito, sin clave API).

Flujo:
  1. set_city(nombre) → geocoding Open-Meteo → guarda lat/lon en local_settings
  2. Thread daemon hace fetch cada INTERVAL_MINUTES y bajo demanda (fetch_now)
  3. get_stats() devuelve caché — nunca bloquea la UI

Favoritos:
  - add_favorite(city)    → añade ciudad a la lista (respeta max_favorites)
  - remove_favorite(city) → elimina ciudad de la lista
  - get_favorites()       → devuelve lista ciudades guardadas
  - set_max_favorites(n)  → cambia el límite máximo
  - Todo se persiste en config/local_settings.py

Arquitectura:
  - core/ — cero imports tkinter/ctk
  - get_stats() acquire(blocking=False) — nunca bloquea

---

## Tabla de contenidos

**Clase [`WeatherService`](#clase-weatherservice)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`set_city()`](#set_cityself-city-str-dict)
  - [`get_stats()`](#get_statsself-dict)
  - [`get_city()`](#get_cityself-str)
  - [`fetch_now()`](#fetch_nowself-none)
  - [`get_favorites()`](#get_favoritesself-liststr)
  - [`get_max_favorites()`](#get_max_favoritesself-int)
  - [`add_favorite()`](#add_favoriteself-city-str-dict)
  - [`remove_favorite()`](#remove_favoriteself-city-str-none)
  - [`set_max_favorites()`](#set_max_favoritesself-n-int-none)

---

## Dependencias internas

- `config.local_settings_io`
- `utils.logger`

## Imports

```python
import threading
import time
import json
from typing import Optional, List
import urllib.request
import urllib.parse
from datetime import datetime, date
from config.local_settings_io import update_params, read
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `INTERVAL_MINUTES` | `60` |
| `GEOCODING_URL` | `'https://geocoding-api.open-meteo.com/v1/search'` |
| `WEATHER_URL` | `'https://api.open-meteo.com/v1/forecast'` |
| `AIR_QUALITY_URL` | `'https://air-quality-api.open-meteo.com/v1/air-quality'` |
| `DEFAULT_MAX_FAVORITES` | `5` |

<details>
<summary>Funciones privadas</summary>

### `_wmo_label(code: int) -> tuple`

Devuelve la descripción y emoji asociados a un código WMO.

Args:
    code (int): El código WMO.

Returns:
    tuple: Un tupla conteniendo la descripción y el emoji del código WMO. 
           Si el código no se encuentra, devuelve ("Desconocido", "❓").

Raises:
    None

</details>

## Clase `WeatherService`

Servicio meteorológico thread-safe con cache y actualización periódica.

Soporta ciudad activa, favoritos persistidos, previsión horaria/diaria 14 días,
calidad del aire, WMO codes con emojis españoles.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_lock` | `threading.Lock()` |
| `_stop_evt` | `threading.Event()` |
| `_running` | `False` |
| `_city` | `''` |
| `_lat` | `None` |
| `_lon` | `None` |
| `_stats` | `{}` |
| `_error` | `''` |
| `_last_update` | `None` |
| `_max_favorites` | `DEFAULT_MAX_FAVORITES` |

### Métodos públicos

#### `start(self) -> None`

Inicia el servicio de actualización periódica del clima en un hilo daemon.

Args: Ninguno

Returns: None

Raises: Ninguna excepción

Nota: Operación idempotente. Si el servicio ya está iniciado, no se realiza ninguna acción adicional.

#### `stop(self) -> None`

Detiene el servicio de meteorología.

Args: 
    None

Returns: 
    None

Raises: 
    None

#### `is_running(self) -> bool`

Indica si el servicio meteorológico se está ejecutando actualmente.

Args:
    Ninguno

Returns:
    bool: True si el servicio se está ejecutando, False en caso contrario.

Raises:
    Ninguno

#### `set_city(self, city: str) -> dict`

Establece la ciudad activa realizando geocoding y disparando una actualización inmediata de los datos meteorológicos.

Args:
    city (str): Nombre de la ciudad.

Returns:
    dict: {"ok": bool, "city": str|None, "lat": float|None, "lon": float|None, "error": str|None}

Raises:
    None

#### `get_stats(self) -> dict`

Obtiene las estadísticas actuales de clima de forma no bloqueante.

Returns:
    dict: Un diccionario con las métricas actuales, pronóstico horario y diario, y el índice de calidad del aire.

Raises:
    None

#### `get_city(self) -> str`

Obtiene la ciudad activa actual.

Returns:
    str: Nombre de la ciudad o cadena vacía.

#### `fetch_now(self) -> None`

Fuerza la actualización inmediata de la información meteorológica en un hilo en segundo plano.

No bloquea la ejecución del llamador.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `get_favorites(self) -> List[str]`

Devuelve una copia de la lista de ciudades favoritas.

Args:
    Ninguno

Returns:
    List[str]: Una lista de ciudades favoritas.

Raises:
    Ninguno

#### `get_max_favorites(self) -> int`

Devuelve el límite máximo de favoritos.

Args:
    None

Returns:
    int: Límite máximo de favoritos.

Raises:
    None

#### `add_favorite(self, city: str) -> dict`

Añade una ciudad a la lista de favoritos si no existe ya y no se ha alcanzado el máximo permitido.

Args:
    city (str): Nombre de la ciudad a añadir.

Returns:
    dict: {"ok": bool, "error": str|None} Indica si la operación fue exitosa y un mensaje de error si procede.

Raises:
    None

#### `remove_favorite(self, city: str) -> None`

Elimina una ciudad de la lista de favoritos y persiste el cambio.

Args:
    city (str): La ciudad a eliminar de favoritos.

Returns:
    None

Raises:
    None

#### `set_max_favorites(self, n: int) -> None`

Establece el límite máximo de favoritos permitidos.

Args:
    n (int): Nuevo límite máximo de favoritos.

Returns:
    None

Raises:
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el servicio meteorológico.

Configura los mecanismos de sincronización, estado inicial y carga datos persistidos.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_loop(self) -> None`

Inicia y mantiene el ciclo de actualización del servicio meteorológico.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_geocode(self, city: str) -> dict`

Busca coordenadas geográficas para una ciudad mediante la API de geocodificación de Open-Meteo.

Args:
    city (str): Nombre de la ciudad a buscar.

Returns:
    dict: Diccionario con claves "ok", "city", "lat", "lon", "country" y valores correspondientes.

Raises:
    Excepciones relacionadas con urllib.request.urlopen si la solicitud falla.

#### `_fetch_weather(self) -> None`

Consulta Open-Meteo forecast y air quality, actualizando caché de manera thread-safe.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_persist_location(self, city: str, lat: float, lon: float) -> None`

Persiste la ciudad activa y sus coordenadas en la configuración local.

Args:
    city (str): Nombre de la ciudad.
    lat (float): Latitud de la ciudad.
    lon (float): Longitud de la ciudad.

Raises:
    Exception: Si ocurre un error al actualizar los parámetros.

#### `_persist_favorites(self, favorites: List[str], max_fav: int) -> None`

Persiste la lista de favoritos y el máximo número de favoritos en la configuración local.

Args:
    favorites (List[str]): La lista de favoritos a persistir.
    max_fav (int): El máximo número de favoritos permitido.

Raises:
    Exception: Si ocurre un error al persistir la configuración.

#### `_load_persisted_location(self) -> None`

Carga la ubicación persistida desde la configuración local.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Excepción genérica en caso de error durante la carga de datos.

</details>
