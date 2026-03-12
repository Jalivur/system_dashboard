"""
Servicio de datos meteorológicos via Open-Meteo (gratuito, sin clave API).

Flujo:
  1. set_city(nombre) → geocoding Open-Meteo → guarda lat/lon en local_settings
  2. Thread daemon hace fetch cada INTERVAL_MINUTES y bajo demanda (fetch_now)
  3. get_stats() devuelve caché — nunca bloquea la UI

Favoritos:
  - add_favorite(city)    → añade ciudad a la lista (respeta max_favorites)
  - remove_favorite(city) → elimina ciudad de la lista
  - get_favorites()       → devuelve lista de ciudades guardadas
  - set_max_favorites(n)  → cambia el límite máximo
  - Todo se persiste en config/local_settings.py

Arquitectura:
  - core/ — cero imports tkinter/ctk
  - get_stats() acquire(blocking=False) — nunca bloquea
"""
import threading
import time
import json
from typing import Optional, List
import urllib.request
import urllib.parse
import urllib.request
from datetime import datetime, date
from config.local_settings_io import update_params, read
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Constantes ────────────────────────────────────────────────────────────────

INTERVAL_MINUTES  = 60
GEOCODING_URL     = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL       = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL   = "https://air-quality-api.open-meteo.com/v1/air-quality"
DEFAULT_MAX_FAVORITES = 5

# Códigos WMO → descripción + icono emoji
_WMO_CODES = {
    0:  ("Despejado",           "☀️"),
    1:  ("Casi despejado",      "🌤️"),
    2:  ("Parcialmente nuboso", "⛅"),
    3:  ("Nublado",             "☁️"),
    45: ("Niebla",              "🌫️"),
    48: ("Niebla con escarcha", "🌫️"),
    51: ("Llovizna ligera",     "🌦️"),
    53: ("Llovizna moderada",   "🌦️"),
    55: ("Llovizna densa",      "🌧️"),
    61: ("Lluvia ligera",       "🌧️"),
    63: ("Lluvia moderada",     "🌧️"),
    65: ("Lluvia intensa",      "🌧️"),
    71: ("Nieve ligera",        "🌨️"),
    73: ("Nieve moderada",      "🌨️"),
    75: ("Nieve intensa",       "❄️"),
    80: ("Chubascos ligeros",   "🌦️"),
    81: ("Chubascos moderados", "🌧️"),
    82: ("Chubascos intensos",  "⛈️"),
    95: ("Tormenta",            "⛈️"),
    96: ("Tormenta con granizo","⛈️"),
    99: ("Tormenta con granizo","⛈️"),
}


def _wmo_label(code: int) -> tuple:
    """Devuelve (descripción, emoji) para un código WMO."""
    return _WMO_CODES.get(code, ("Desconocido", "❓"))


class WeatherService:
    """
    Servicio meteorológico thread-safe con cache y actualización periódica.
    """

    def __init__(self):
        self._lock        = threading.Lock()
        self._stop_evt    = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._running     = False

        # Estado
        self._city        = ""
        self._lat         = None
        self._lon         = None
        self._stats       = {}
        self._error       = ""
        self._last_update = None

        # Favoritos
        self._favorites: List[str] = []
        self._max_favorites        = DEFAULT_MAX_FAVORITES

        # Cargar ciudad y favoritos guardados
        self._load_persisted_location()

    # ── Arranque / parada ─────────────────────────────────────────────────────

    def start(self) -> None:
        """Arranca el thread daemon de actualización periódica."""
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="WeatherService")
        self._thread.start()
        logger.info("[WeatherService] Iniciado")

    def stop(self) -> None:
        """Detiene el thread daemon."""
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        with self._lock:
            self._stats       = {}
        logger.info("[WeatherService] Detenido")

    def is_running(self) -> bool:
        return self._running

    # ── API pública — ciudad activa ───────────────────────────────────────────

    def set_city(self, city: str) -> dict:
        """
        Cambia la ciudad activa: hace geocoding y dispara fetch inmediato.

        Returns:
            {"ok": True, "city": ..., "country": ...}  si éxito
            {"ok": False, "error": ...}                si falla
        """
        city = city.strip()
        if not city:
            return {"ok": False, "error": "Nombre de ciudad vacío"}

        result = self._geocode(city)
        if not result["ok"]:
            return result

        with self._lock:
            self._city  = result["city"]
            self._lat   = result["lat"]
            self._lon   = result["lon"]
            self._error = ""

        self._persist_location(result["city"], result["lat"], result["lon"])
        self._fetch_weather()
        return result

    def get_stats(self) -> dict:
        """
        Devuelve la caché actual. acquire(blocking=False) — nunca bloquea la UI.
        """
        if self._lock.acquire(blocking=False):
            try:
                return dict(self._stats)
            finally:
                self._lock.release()
        return {}

    def get_city(self) -> str:
        return self._city

    def fetch_now(self) -> None:
        """Fuerza una actualización inmediata en background."""
        threading.Thread(
            target=self._fetch_weather, daemon=True, name="WeatherFetch"
        ).start()

    # ── API pública — favoritos ───────────────────────────────────────────────

    def get_favorites(self) -> List[str]:
        """Devuelve copia de la lista de ciudades favoritas."""
        with self._lock:
            return list(self._favorites)

    def get_max_favorites(self) -> int:
        """Devuelve el límite máximo de favoritos."""
        return self._max_favorites

    def add_favorite(self, city: str) -> dict:
        """
        Añade la ciudad a favoritos si no existe ya y no se supera el máximo.

        Returns:
            {"ok": True}                    si éxito
            {"ok": False, "error": ...}     si falla
        """
        city = city.strip()
        if not city:
            return {"ok": False, "error": "Ciudad vacía"}

        with self._lock:
            if city in self._favorites:
                return {"ok": False, "error": f"'{city}' ya está en favoritos"}
            if len(self._favorites) >= self._max_favorites:
                return {"ok": False,
                        "error": f"Máximo de {self._max_favorites} favoritos alcanzado"}
            self._favorites.append(city)
            favorites_copy = list(self._favorites)

        self._persist_favorites(favorites_copy, self._max_favorites)
        logger.info("[WeatherService] Favorito añadido: %s", city)
        return {"ok": True}

    def remove_favorite(self, city: str) -> None:
        """Elimina una ciudad de favoritos."""
        with self._lock:
            if city in self._favorites:
                self._favorites.remove(city)
            favorites_copy = list(self._favorites)

        self._persist_favorites(favorites_copy, self._max_favorites)
        logger.info("[WeatherService] Favorito eliminado: %s", city)

    def set_max_favorites(self, n: int) -> None:
        """Cambia el límite máximo de favoritos y persiste."""
        n = max(1, int(n))
        with self._lock:
            self._max_favorites = n
            # Truncar lista si excede el nuevo máximo
            if len(self._favorites) > n:
                self._favorites = self._favorites[:n]
            favorites_copy = list(self._favorites)

        self._persist_favorites(favorites_copy, n)
        logger.info("[WeatherService] Máximo favoritos: %d", n)

    # ── Loop daemon ───────────────────────────────────────────────────────────

    def _loop(self) -> None:
        """Thread principal: fetch al arrancar y cada INTERVAL_MINUTES."""
        if self._lat is not None:
            self._fetch_weather()

        while not self._stop_evt.wait(timeout=INTERVAL_MINUTES * 60):
            if self._lat is not None:
                self._fetch_weather()

    # ── Geocoding ─────────────────────────────────────────────────────────────

    def _geocode(self, city: str) -> dict:
        """Busca coordenadas para una ciudad via Open-Meteo Geocoding API."""
        try:
            params = urllib.parse.urlencode({
                "name":     city,
                "count":    1,
                "language": "es",
                "format":   "json",
            })
            url = f"{GEOCODING_URL}?{params}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            results = data.get("results")
            if not results:
                return {"ok": False, "error": f"Ciudad '{city}' no encontrada"}

            r = results[0]
            return {
                "ok":      True,
                "city":    f"{r['name']}, {r.get('country', '')}",
                "lat":     r["latitude"],
                "lon":     r["longitude"],
                "country": r.get("country", ""),
            }
        except Exception as e:
            logger.error("[WeatherService] Geocoding error: %s", e)
            return {"ok": False, "error": f"Error de conexión: {e}"}

    # ── Fetch meteorológico ───────────────────────────────────────────────────

    def _fetch_weather(self) -> None:
        """Consulta Open-Meteo y actualiza la caché."""
        with self._lock:
            lat  = self._lat
            lon  = self._lon
            city = self._city

        if lat is None or lon is None:
            return

        try:
            params = urllib.parse.urlencode({
                "latitude":  lat,
                "longitude": lon,
                "current":   ",".join([
                    "temperature_2m",
                    "apparent_temperature",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "precipitation",
                    "weather_code",
                    "uv_index",
                ]),
                "hourly":    ",".join([
                    "temperature_2m",
                    "precipitation_probability",
                    "weather_code",
                ]),
                "daily":     ",".join([
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_probability_max",
                    "sunrise",
                    "sunset",
                ]),
                "forecast_days":   14,
                "timezone":        "auto",
                "wind_speed_unit": "kmh",
            })
            url = f"{WEATHER_URL}?{params}"

            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            cur  = data.get("current", {})
            code = cur.get("weather_code", 0)
            desc, icon = _wmo_label(code)

            # Previsión: próximas 12 horas desde la hora actual
            hourly   = data.get("hourly", {})
            h_times  = hourly.get("time", [])
            h_temps  = hourly.get("temperature_2m", [])
            h_precip = hourly.get("precipitation_probability", [])
            h_codes  = hourly.get("weather_code", [])

            now_str = datetime.now().strftime("%Y-%m-%dT%H:00")
            try:
                start_idx = h_times.index(now_str)
            except ValueError:
                start_idx = 0

            forecast = []
            for i in range(start_idx, min(start_idx + 12, len(h_times))):
                h_code = h_codes[i] if i < len(h_codes) else 0
                _, h_icon = _wmo_label(h_code)
                forecast.append({
                    "hour":         h_times[i][11:16],
                    "temp":         h_temps[i] if i < len(h_temps) else "--",
                    "precip_prob":  h_precip[i] if i < len(h_precip) else 0,
                    "weather_code": h_code,
                    "weather_icon": h_icon,
                })

            # Todas las horas agrupadas por fecha — para drill-down días
            hourly_by_date: dict = {}
            for i, t in enumerate(h_times):
                date_key = t[:10]   # "2024-03-07"
                h_code   = h_codes[i] if i < len(h_codes) else 0
                _, h_icon = _wmo_label(h_code)
                hourly_by_date.setdefault(date_key, []).append({
                    "hour":         t[11:16],
                    "temp":         h_temps[i]  if i < len(h_temps)  else "--",
                    "precip_prob":  h_precip[i] if i < len(h_precip) else 0,
                    "weather_code": h_code,
                    "weather_icon": h_icon,
                })

            # Previsión diaria: 14 días
            daily      = data.get("daily", {})
            d_times    = daily.get("time", [])
            d_codes    = daily.get("weather_code", [])
            d_max      = daily.get("temperature_2m_max", [])
            d_min      = daily.get("temperature_2m_min", [])
            d_precip   = daily.get("precipitation_probability_max", [])
            d_sunrise  = daily.get("sunrise", [])
            d_sunset   = daily.get("sunset", [])

            _DAY_NAMES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
            forecast_daily = []
            for i in range(min(14, len(d_times))):
                d_code = d_codes[i] if i < len(d_codes) else 0
                _, d_icon = _wmo_label(d_code)
                try:
                    d = date.fromisoformat(d_times[i])
                    label = "Hoy" if i == 0 else _DAY_NAMES[d.weekday()]
                    date_str = d.strftime("%d/%m")
                except Exception:
                    label = d_times[i]
                    date_str = ""
                # Sunrise / sunset: vienen como "2024-03-07T07:23" → extraer HH:MM
                def _hhmm(val):
                    try:
                        return val[11:16]
                    except Exception:
                        return "--"

                forecast_daily.append({
                    "label":        label,
                    "date":         date_str,
                    "date_iso":     d_times[i],   # "2024-03-07" — para drill-down
                    "temp_max":     d_max[i]     if i < len(d_max)     else "--",
                    "temp_min":     d_min[i]     if i < len(d_min)     else "--",
                    "precip_prob":  d_precip[i]  if i < len(d_precip)  else 0,
                    "sunrise":      _hhmm(d_sunrise[i]) if i < len(d_sunrise) else "--",
                    "sunset":       _hhmm(d_sunset[i])  if i < len(d_sunset)  else "--",
                    "weather_code": d_code,
                    "weather_icon": d_icon,
                })

            stats = {
                "city":         city,
                "lat":          lat,
                "lon":          lon,
                "error":        "",
                "last_update":  datetime.now().strftime("%H:%M"),
                "temp":         cur.get("temperature_2m", "--"),
                "feels_like":   cur.get("apparent_temperature", "--"),
                "humidity":     cur.get("relative_humidity_2m", "--"),
                "wind_speed":   cur.get("wind_speed_10m", "--"),
                "wind_dir":     cur.get("wind_direction_10m", "--"),
                "precip":       cur.get("precipitation", "--"),
                "weather_code": code,
                "weather_desc": desc,
                "weather_icon": icon,
                "uv_index":     cur.get("uv_index", "--"),
                "sunrise":      _hhmm(d_sunrise[0]) if d_sunrise else "--",
                "sunset":       _hhmm(d_sunset[0])  if d_sunset  else "--",
                "forecast":         forecast,
                "forecast_daily":   forecast_daily,
                "hourly_by_date":   hourly_by_date,
            }

            # ── Calidad del aire (llamada independiente, fallo silencioso) ──────
            try:
                aq_params = urllib.parse.urlencode({
                    "latitude":  lat,
                    "longitude": lon,
                    "current":   "pm2_5,pm10,european_aqi",
                    "timezone":  "auto",
                })
                aq_url = f"{AIR_QUALITY_URL}?{aq_params}"
                with urllib.request.urlopen(aq_url, timeout=8) as aq_resp:
                    aq_data = json.loads(aq_resp.read().decode())
                aq_cur = aq_data.get("current", {})
                stats["aqi"]    = aq_cur.get("european_aqi", "--")
                stats["pm2_5"]  = aq_cur.get("pm2_5",        "--")
                stats["pm10"]   = aq_cur.get("pm10",         "--")
            except Exception as aq_err:
                logger.debug("[WeatherService] AQI no disponible: %s", aq_err)
                stats["aqi"]   = "--"
                stats["pm2_5"] = "--"
                stats["pm10"]  = "--"

            with self._lock:
                self._stats       = stats
                self._last_update = stats["last_update"]
                self._error       = ""

            logger.info("[WeatherService] Actualizado: %s %.1f°C %s",
                        city, stats["temp"], desc)

        except Exception as e:
            logger.error("[WeatherService] Fetch error: %s", e)
            with self._lock:
                self._error          = f"Error de conexión: {e}"
                self._stats["error"] = self._error

    # ── Persistencia ─────────────────────────────────────────────────────────

    def _persist_location(self, city: str, lat: float, lon: float) -> None:
        """Guarda ciudad activa y coordenadas en config/local_settings.py."""
        try:
            update_params({
                "WEATHER_CITY": city,
                "WEATHER_LAT":  lat,
                "WEATHER_LON":  lon,
            })
        except Exception as e:
            logger.error("[WeatherService] Error persistiendo ubicación: %s", e)

    def _persist_favorites(self, favorites: List[str], max_fav: int) -> None:
        """Guarda lista de favoritos y máximo en config/local_settings.py."""
        try:
            update_params({
                "WEATHER_FAVORITES":     favorites,
                "WEATHER_MAX_FAVORITES": max_fav,
            })
        except Exception as e:
            logger.error("[WeatherService] Error persistiendo favoritos: %s", e)

    def _load_persisted_location(self) -> None:
        """Carga ciudad, coordenadas, favoritos y máximo desde local_settings."""
        try:
            params, _ = read()

            city  = params.get("WEATHER_CITY")
            lat   = params.get("WEATHER_LAT")
            lon   = params.get("WEATHER_LON")
            favs  = params.get("WEATHER_FAVORITES", [])
            max_f = params.get("WEATHER_MAX_FAVORITES", DEFAULT_MAX_FAVORITES)

            if city and lat is not None and lon is not None:
                self._city = city
                self._lat  = lat
                self._lon  = lon
                logger.info("[WeatherService] Ubicación cargada: %s", city)

            if isinstance(favs, list):
                self._favorites = favs
            self._max_favorites = max(1, int(max_f))

        except Exception as e:
            logger.error("[WeatherService] Error cargando datos: %s", e)
