# `core.weather_service`

> **Ruta**: `core/weather_service.py`

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

Devuelve (descripción, emoji) para un código WMO.

</details>

## Clase `WeatherService`

Servicio meteorológico thread-safe con cache y actualización periódica profesional.

Soporta ciudad activa, favoritos persistidos, previsión horaria/diaria 14 días,
calidad del aire, WMO codes con emojis españoles.

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

Arranca el thread daemon de actualización periódica.

Idempotente, log de inicio.

#### `stop(self) -> None`

Detiene el thread daemon.

Join timeout 3s, resetea stats. Log.

#### `is_running(self) -> bool`

Estado del servicio.

Returns:
    bool: True si thread activo.

#### `set_city(self, city: str) -> dict`

Cambia la ciudad activa: hace geocoding y dispara fetch inmediato.

Persiste lat/lon. 

Returns:
    dict: {"ok": bool, "city": str|None, "lat": float|None, "lon": float|None, "error": str|None}

#### `get_stats(self) -> dict`

Devuelve la caché actual de forma no bloqueante.

Returns:
    dict: Métricas actuales + forecast hourly/daily + AQI.

#### `get_city(self) -> str`

Ciudad activa actual.

Returns:
    str: Nombre ciudad o vacío.

#### `fetch_now(self) -> None`

Fuerza fetch inmediato en thread background.

No bloquea caller.

#### `get_favorites(self) -> List[str]`

Devuelve copia de la lista de ciudades favoritas.

#### `get_max_favorites(self) -> int`

Devuelve el límite máximo de favoritos.

#### `add_favorite(self, city: str) -> dict`

Añade la ciudad a favoritos si no existe ya y no se supera el máximo.

Persiste. 

Returns:
    dict: {"ok": bool, "error": str|None}

#### `remove_favorite(self, city: str) -> None`

Elimina una ciudad de favoritos y persiste.

#### `set_max_favorites(self, n: int) -> None`

Cambia el límite máximo de favoritos, trunca lista si necesario, persiste.

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el servicio meteorológico.

Configura lock, event, estado inicial, carga datos persistidos de local_settings.

#### `_loop(self) -> None`

Thread principal: fetch al arrancar y cada INTERVAL_MINUTES.

#### `_geocode(self, city: str) -> dict`

Busca coordenadas para una ciudad via Open-Meteo Geocoding API (privado).

Returns:
    dict: {"ok": bool, "city": str, "lat": float, "lon": float, "country": str}

#### `_fetch_weather(self) -> None`

Consulta Open-Meteo forecast + air quality y actualiza caché (privado).

Incluye current, hourly 12h, daily 14d, AQI. WMO emojis. Thread-safe.

#### `_persist_location(self, city: str, lat: float, lon: float) -> None`

Persiste ciudad activa y coordenadas en local_settings.py (privado).

#### `_persist_favorites(self, favorites: List[str], max_fav: int) -> None`

Persiste lista favoritos y máximo en local_settings.py (privado).

#### `_load_persisted_location(self) -> None`

Carga persistidos desde local_settings: ciudad, coords, favoritos (privado).

</details>
