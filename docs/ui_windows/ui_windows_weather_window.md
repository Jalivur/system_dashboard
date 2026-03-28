# `ui.windows.weather_window`

> **Ruta**: `ui/windows/weather_window.py`

> **Cobertura de documentación**: 🟢 100% (31/31)

Ventana de Widget de Clima.

Muestra datos meteorológicos actuales y previsión de las próximas 12 horas
via Open-Meteo (gratuito, sin clave API).

Arquitectura:
  - Todos los datos vienen de WeatherService.get_stats() — caché, no bloquea UI
  - Refresco solo al abrir la ventana y con el botón Actualizar
  - Ciudad editable desde la propia ventana
  - Favoritos: guardar ciudad activa, seleccionar desde desplegable, eliminar
  - Máximo de favoritos editable y persistido en config/local_settings.py
  - Scroll vertical para todo el contenido
  - Scroll horizontal para la previsión por horas
  - StringVar siempre con master= explícito

---

## Tabla de contenidos

**Clase [`WeatherWindow`](#clase-weatherwindow)**
  - [`destroy()`](#destroyself)

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `utils.logger`

## Imports

```python
import tkinter as tk
import customtkinter as ctk
import threading, time
from datetime import datetime
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `WeatherWindow(ctk.CTkToplevel)`

Representa una ventana emergente que muestra información meteorológica con funcionalidades de favoritos.

Args:
    parent (CTk): Ventana padre que contiene la ventana de clima.
    weather_service: Servicio que proporciona datos meteorológicos.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_svc` | `weather_service` |
| `_city_var` | `ctk.StringVar(master=self, value=self._svc.get_city())` |
| `_current_sunrise` | `'--'` |
| `_current_sunset` | `'--'` |
| `_drilldown_active` | `False` |
| `_fav_var` | `ctk.StringVar(master=self, value='')` |
| `_max_fav_var` | `ctk.StringVar(master=self, value=str(self._svc.get_max_favorites()))` |
| `_after_id` | `None` |

### Métodos públicos

#### `destroy(self)`

Cierra la ventana de manera segura, limpiando temporizadores y recursos.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, weather_service)`

Inicializa la ventana de clima configurando geometría, variables de estado y construyendo la UI completa.

Args:
    parent (object): Ventana padre.
    weather_service (object): Servicio de clima.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno.

#### `_create_ui(self)`

Crea la interfaz de usuario completa para la ventana de clima.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_forecast_inner_configure(self, event) -> None`

Ajusta automáticamente el canvas de previsión a la altura real del contenido interno.

Args:
    event: El evento que contiene la altura del contenido interno.

Returns:
    None

Raises:
    None

#### `_on_detail_configure(self, event) -> None`

Ajusta automáticamente el canvas de detalles meteorológicos a la altura real del contenido.

Args:
    event: Evento que contiene la altura disponible para el canvas.

Returns:
    None

Raises:
    None

#### `_aqi_color(aqi) -> str`

Obtiene el color según el índice AQI europeo (0–500+).

Args:
    aqi (int): Índice AQI.

Returns:
    str: Código de color en formato hexadecimal.

Raises:
    None

#### `_wmo_bg_color(code) -> str`

Determina el color de fondo según el código WMO proporcionado.

Args:
    code (str): Código WMO que define el estado del tiempo.

Returns:
    str: Código de color en formato hexadecimal.

Raises:
    None

#### `_temp_color(temp) -> str`

Devuelve un color hex interpolado según la temperatura.

Args:
    temp (float): Temperatura en grados Celsius.

Returns:
    str: Color hex interpolado en formato #RRGGBB.

Raises:
    None

#### `_redraw_day_progress(self) -> None`

Redibuja la barra de progreso del día, mostrando el avance desde la salida hasta la puesta de sol.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_make_detail(self, parent, emoji, label, value)`

Crea un widget compacto de detalle meteorológico que incluye un emoji, una etiqueta y un valor destacado.

Args:
    parent: El padre del widget.
    emoji (str): El emoji a mostrar.
    label (str): La etiqueta a mostrar.
    value (str): El valor destacado a mostrar.

Returns:
    ctk.CTkLabel: La etiqueta que muestra el valor destacado.

Raises:
    Ninguna excepción específica.

#### `_update(self)`

Actualiza la interfaz de la ventana meteorológica con datos frescos del servicio.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_update_forecast(self, forecast, max_items: int = 12)`

Actualiza la previsión meteorológica en el área de scroll horizontal.

Args:
    forecast (list): Lista de items de previsión meteorológica.
    max_items (int): Número máximo de items a mostrar (por defecto, 12).

Returns:
    None

Raises:
    None

#### `_set_view_mode(self, mode: str) -> None`

Establece el modo de vista de la previsión del tiempo.

Args:
    mode (str): El modo de vista a establecer, puede ser 'hours' para 12 horas o 'days' para 14 días.

Returns:
    None

Raises:
    None

#### `_on_search(self)`

Gestiona el evento de búsqueda de ciudad, validando la entrada, 
iniciando una búsqueda asíncrona y actualizando la interfaz de usuario.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_on_search_done(self, result)`

Reactiva la interfaz de usuario y maneja el resultado de una búsqueda asíncrona.

Args:
    result (dict): Resultado de la búsqueda con claves 'ok', 'city' y 'error'.

Returns:
    None

Raises:
    None

#### `_on_refresh(self)`

Inicia la actualización asíncrona de los datos meteorológicos actuales.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_refresh_done(self)`

Finaliza el proceso de refresco de la ventana de clima.

Args:
    None

Returns:
    None

Raises:
    None

#### `_update_forecast_daily(self, forecast: list) -> None`

Actualiza la previsión meteorológica diaria con los datos proporcionados.

Args:
    forecast (list): Lista de objetos con información meteorológica diaria.

Returns:
    None

Raises:
    Ninguna excepción relevante.

Nota: Destruye y vuelve a crear los elementos de la interfaz gráfica de usuario.

#### `_iter_all_children(widget)`

Itera recursivamente todos los widgets hijos de un widget dado para binding de eventos drill-down.

Args:
    widget: El widget cuyos hijos se iterarán.

Yields:
    Los widgets hijos del widget dado.

Raises:
    Ninguna excepción específica.

#### `_drilldown_day(self, date_key: str, label: str) -> None`

Activa el modo drill-down para mostrar la previsión horaria específica de un día seleccionado.

Args:
    date_key (str): Clave de fecha para obtener los datos horarios.
    label (str): Etiqueta a mostrar durante el drill-down.

Returns:
    None

Raises:
    None

#### `_drilldown_back(self) -> None`

Regresa del drill-down de horas a la vista general de 14 días.

Args:
    None

Returns:
    None

Raises:
    None

#### `_on_save_favorite(self)`

Guarda la ciudad actualmente activa en la lista de favoritos del servicio.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_on_delete_favorite(self)`

Elimina el favorito seleccionado del dropdown de la lista del servicio y refresca la UI.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_on_favorite_selected(self, city)`

Carga automáticamente la ciudad seleccionada desde favoritos y ejecuta búsqueda.

Args:
    city (str): La ciudad seleccionada desde favoritos.

Returns:
    None

Raises:
    None

#### `_on_max_changed(self)`

Actualiza el máximo de favoritos al cambiar el valor correspondiente.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_refresh_favorites_dropdown(self)`

Recarga dinámicamente la lista de favoritos en el OptionMenu desde el servicio.

Args:
    None

Returns:
    None

Raises:
    None

#### `_set_fav_status(self, msg, ok = True)`

Establece el estado de favoritos en la UI con un mensaje temporal.

Args:
    msg (str): El mensaje a mostrar en la UI de favoritos.
    ok (bool): Indica si la operación fue exitosa (verde) o no (rojo). Por defecto es True.

Returns:
    None

Raises:
    None

#### `_wind_dir_arrow(degrees)`

Convierte la dirección del viento en grados a símbolo de flecha unicode.

Args:
    degrees (float): Dirección del viento en grados.

Returns:
    str: Símbolo de flecha unicode que representa la dirección del viento.

Raises:
    None

</details>
