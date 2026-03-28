# `ui.windows.wifi_window`

> **Ruta**: `ui/windows/wifi_window.py`

> **Cobertura de documentación**: 🟢 100% (13/13)

Ventana de monitor de conexión WiFi.
Muestra SSID, señal, bitrate, tráfico TX/RX y sus históricos.
Los widgets se crean una sola vez — solo se actualizan los valores.

---

## Tabla de contenidos

**Clase [`WiFiWindow`](#clase-wifiwindow)**

---

## Dependencias internas

- `config.settings`
- `core`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from core import WiFiMonitor, NetworkMonitor
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import GraphWidget
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `WiFiWindow(ctk.CTkToplevel)`

Ventana emergente para monitorizar la conexión WiFi en tiempo real.

Args:
    parent: Ventana padre que contiene la instancia de esta ventana.
    wifi_monitor (WiFiMonitor): Instancia del monitor WiFi para obtener datos.

Raises:
    Ninguna excepción específica.

Returns:
    Ningún valor de retorno específico.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_wifi_monitor` | `wifi_monitor` |
| `_refresh_job` | `None` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, wifi_monitor)`

Inicializa la ventana de monitor WiFi.

Args:
    parent: Ventana padre (principal del dashboard).
    wifi_monitor (WiFiMonitor): Instancia del monitor WiFi para obtener datos en tiempo real.

Raises:
    None

Returns:
    None

#### `_create_ui(self)`

Crea la interfaz de usuario de la ventana WiFi de forma estática.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_build_iface_selector(self, parent)`

Construye el selector de interfaz WiFi en el header de la ventana.

Args:
    parent: Frame padre donde insertar el selector.

Returns:
    None

Raises:
    None

#### `_on_iface_change(self, iface: str)`

Callback ejecutado al seleccionar nueva interfaz WiFi desde el dropdown.

Args:
    iface (str): Nombre de la nueva interfaz seleccionada (ej: 'wlan0').

Returns:
    None

Raises:
    None

#### `_build_connection_card(self)`

Construye la tarjeta superior de estado de conexión WiFi.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_build_traffic_card(self)`

Construye la tarjeta inferior de tráfico de red (RX/TX).

Estructura:
- Header con título 'TRÁFICO'.
- Grid 1x2 para celdas descarga (RX) y subida (TX).
- Cada celda contiene: label métrica, valor actual y gráfica histórica dedicada.

Args: 
- None

Returns: 
- None

Raises: 
- None

#### `_update(self)`

Actualiza los valores de los widgets de la ventana de WiFi cada _REFRESH_MS.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_refresh_connection(self, info: dict)`

Actualiza los valores de la tarjeta de conexión WiFi.

Args:
    info (dict): Datos de conexión de WiFiMonitor ('ssid', 'signal_dbm', etc.).

Returns:
    None

Raises:
    None

#### `_refresh_traffic(self, stats: dict)`

Actualiza valores de tráfico de red (RX/TX) y gráficas históricas.

Args:
    stats (dict): Estadísticas completas de WiFiMonitor.get_stats()
                  ('rx_mbps', 'tx_mbps', 'rx_hist', 'tx_hist', etc.).

Returns:
    None

Raises:
    None

#### `_signal_bars(pct: int) -> str`

Genera representación visual Unicode de barras de intensidad de señal WiFi.

Args:
    pct (int): Porcentaje de calidad de señal (0-100).

Returns:
    str: Representación visual de barras de intensidad de señal WiFi.

Raises:
    None

Nota: Los valores de retorno son:
    - ▂▄▆█ (≥80%)
    - ▂▄▆░ (≥60%)
    - ▂▄░░ (≥40%)
    - ▂░░░ (≥20%)
    - ░░░░ (<20%)

#### `_force_refresh(self)`

Refresca inmediatamente todos los datos cancelando el trabajo pendiente.

Args:
    None

Returns:
    None

Raises:
    None

#### `_on_close(self)`

Maneja el cierre de la ventana limpiando recursos.

Args:
    None

Returns:
    None

Raises:
    None

</details>
