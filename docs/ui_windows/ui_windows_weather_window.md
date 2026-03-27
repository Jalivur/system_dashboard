# `ui.windows.weather_window`

> **Ruta**: `ui/windows/weather_window.py`

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

Ventana de datos meteorológicos con favoritos.

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

Limpia temporizadores y recursos al cerrar la ventana de manera segura.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, weather_service)`

Inicializa la ventana de clima: configura geometría, variables de estado y construye UI completa.

#### `_create_ui(self)`

Construye toda la interfaz de usuario: header, búsqueda, favoritos, datos actuales y área de previsión.

#### `_on_forecast_inner_configure(self, event) -> None`

Ajusta automáticamente el canvas de previsión a la altura real del contenido interno.

#### `_on_detail_configure(self, event) -> None`

Ajusta automáticamente el canvas de detalles meteorológicos a la altura real del contenido.

#### `_aqi_color(aqi) -> str`

Color según índice AQI europeo (0–500+).

#### `_wmo_bg_color(code) -> str`

Color de fondo del panel actual según código WMO.

#### `_temp_color(temp) -> str`

Devuelve un color hex interpolado según la temperatura.

#### `_redraw_day_progress(self) -> None`

Dibuja la barra de progreso del día (desde salida hasta puesta de sol) con marcador actual y etiquetas.

#### `_make_detail(self, parent, emoji, label, value)`

Crea un widget compacto de detalle meteorológico (icono + etiqueta + valor destacado).

#### `_update(self)`

Actualiza toda la interfaz con datos frescos del servicio: condiciones actuales, detalles y previsión.

#### `_update_forecast(self, forecast, max_items: int = 12)`

Renderiza las celdas de previsión por horas en el área de scroll horizontal (máx. 12 items).

#### `_set_view_mode(self, mode: str) -> None`

Cambia el modo de vista de previsión entre 'hours' (12h) y 'days' (14 días), actualizando contenido.

#### `_on_search(self)`

Callback del botón/Enter de búsqueda: valida ciudad, inicia thread asíncrono y actualiza UI.

#### `_on_search_done(self, result)`

Callback post-búsqueda desde thread: re-activa UI, maneja éxito/error y refresca datos.

#### `_on_refresh(self)`

Inicia actualización asíncrona de datos meteorológicos actuales, deshabilitando botón durante proceso.

#### `_on_refresh_done(self)`

Finaliza refresh: re-habilita botón, limpia mensajes y actualiza toda la UI.

#### `_update_forecast_daily(self, forecast: list) -> None`

Renderiza previsión extendida de 14 días con celdas clickeables para drill-down a horas específicas.

#### `_iter_all_children(widget)`

Generador recursivo que itera todos los widgets hijos para binding de eventos drill-down.

#### `_drilldown_day(self, date_key: str, label: str) -> None`

Activa modo drill-down: muestra previsión horaria específica del día seleccionado, ocultando selectores.

#### `_drilldown_back(self) -> None`

Regresa del drill-down de horas a la vista general de 14 días.

#### `_on_save_favorite(self)`

Guarda la ciudad actualmente activa en la lista de favoritos del servicio.

#### `_on_delete_favorite(self)`

Elimina el favorito seleccionado del dropdown de la lista del servicio y refresca UI.

#### `_on_favorite_selected(self, city)`

Carga automáticamente la ciudad seleccionada desde favoritos y ejecuta búsqueda.

#### `_on_max_changed(self)`

Valida y persiste el nuevo máximo de favoritos desde el campo de entrada.

#### `_refresh_favorites_dropdown(self)`

Recarga dinámicamente la lista de favoritos en el OptionMenu desde el servicio.

#### `_set_fav_status(self, msg, ok = True)`

Muestra mensaje de estado temporal (3s) en la UI de favoritos con color según éxito/error.

#### `_wind_dir_arrow(degrees)`

Convierte la dirección del viento en grados a símbolo de flecha unicode (8 direcciones).

</details>
