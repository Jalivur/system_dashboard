# `ui.windows.wifi_window`

> **Ruta**: `ui/windows/wifi_window.py`

Ventana de monitor de conexión WiFi.
Muestra SSID, señal, bitrate, tráfico TX/RX y sus históricos.
Los widgets se crean una sola vez — solo se actualizan los valores.

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

Ventana de monitor de conexión WiFi.

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

Configuración inicial:
- Título, colores, geometría fija para pantalla DSI.
- No redimensionable, modal sobre padre, foco automático.
- Inicializa _refresh_job y todas referencias de widgets (None).
- Crea UI estática con _create_ui().
- Agenda primer _update() en 100ms.
- Registra apertura en logger.

#### `_create_ui(self)`

Crea toda la interfaz de usuario de la ventana WiFi de forma estática (una sola vez).

Estructura completa:
- Frame principal y header personalizable con título y estado dinámico.
- Contenedor scrollable con canvas para contenido extensible.
- Tarjetas dedicadas para estado de conexión y tráfico de red.
- Gráficas históricas (GraphWidget) para evolución de señal, RX y TX.
- Barra inferior con timestamp de última actualización y botón de refresco manual.
- Selector de interfaz (dropdown) si hay múltiples adaptadores WiFi disponibles.

Inicializa todas las referencias a widgets actualizables como atributos de instancia
(_lbl_ssid, _graph_rx, etc.) para su posterior actualización sin recrearlos.

#### `_build_iface_selector(self, parent)`

Construye el selector (dropdown) de interfaz WiFi en el header de la ventana.

Args:
    parent: Frame padre donde insertar el selector (header).

Solo se muestra si hay múltiples interfaces WiFi disponibles (WiFiMonitor.get_available_interfaces()).
Crea label 'Interfaz:', CTkStringVar para valor actual, y CTkOptionMenu con lista de interfaces.
Al cambiar selección, llama a self._on_iface_change().

#### `_on_iface_change(self, iface: str)`

Callback ejecutado al seleccionar nueva interfaz WiFi desde el dropdown.

Args:
    iface (str): Nombre de la nueva interfaz seleccionada (ej: 'wlan0').

Acciones:
- Cambia la interfaz activa en self._wifi_monitor.
- Actualiza el label _lbl_iface con el nuevo nombre.
- Cancela refresco pendiente y agenda _update() en 200ms para reflejar cambios.
- Registra cambio en logger.

#### `_build_connection_card(self)`

Construye la tarjeta superior de estado de conexión WiFi.

Incluye:
- Header con título 'CONEXIÓN' y label de interfaz actual (_lbl_iface).
- Fila SSID con label principal.
- Grid 1x2 para métricas: señal (dBm + barra + %) y calidad link (LQ/max).
- Fila bitrate con valor actual.
- Gráfica histórica de señal (_graph_signal, toda el ancho).

Todos los labels métricos (_lbl_signal_val, etc.) referenciados para _update().
Usa colores dinámicos basados en calidad de señal (WiFiMonitor.signal_color()).

#### `_build_traffic_card(self)`

Construye la tarjeta inferior de tráfico de red (RX/TX).

Estructura:
- Header con título 'TRÁFICO'.
- Grid 1x2 para celdas descarga (RX) y subida (TX).
- Cada celda contiene: label métrica, valor actual (_lbl_rx/_lbl_tx),
  gráfica histórica dedicada (_graph_rx/_graph_tx).

Ancho de gráficas ajustado a _COL_W. Colores dinámicos via NetworkMonitor.net_color().
Referencias inicializadas para actualización en _refresh_traffic().

#### `_update(self)`

Actualiza todos los valores de widgets cada _REFRESH_MS (5s).

Proceso:
1. Verifica existencia de ventana.
2. Si monitor no corre, muestra banner 'stopped'.
3. Obtiene stats de WiFiMonitor.get_stats().
4. Actualiza conexión (_refresh_connection), tráfico (_refresh_traffic).
5. Actualiza header status con SSID + dBm o 'Sin conexión'.
6. Muestra timestamp última actualización.
7. Agenda próximo _update().

Centraliza lógica de refresco periódico.

#### `_refresh_connection(self, info: dict)`

Actualiza solo los valores de la tarjeta de conexión (SSID, señal, calidad, bitrate, gráfica).

Args:
    info (dict): Datos de conexión de WiFiMonitor ('ssid', 'signal_dbm', etc.).

Actualiza:
- SSID con color warning si desconectado.
- Señal: valor dBm, barras visuales (self._signal_bars), % con color dinámico.
- Calidad link: LQ/max.
- Ruido dBm.
- Bitrate.
- Gráfica señal: normaliza historia [-100..0] -> [0..100], color dinámico.

#### `_refresh_traffic(self, stats: dict)`

Actualiza valores de tráfico de red (RX/TX) y gráficas históricas.

Args:
    stats (dict): Estadísticas completas de WiFiMonitor.get_stats()
                  ('rx_mbps', 'tx_mbps', 'rx_hist', 'tx_hist', etc.).

Actualiza:
- Velocidades actuales _lbl_rx/_lbl_tx con 3 decimales y colores (NetworkMonitor.net_color).
- Historia RX/TX: escala a peak*1.2, colores dinámicos.

#### `_signal_bars(pct: int) -> str`

Genera representación visual Unicode de barras de intensidad de señal WiFi.

Args:
    pct (int): Porcentaje de calidad de señal (0-100).

Returns:
    str: 4 caracteres Unicode:
         - ▂▄▆█ (≥80%)
         - ▂▄▆░ (≥60%)
         - ▂▄░░ (≥40%)
         - ▂░░░ (≥20%)
         - ░░░░ (<20%)

Usado en _lbl_signal_bar para display intuitivo.

#### `_force_refresh(self)`

Refresca inmediatamente todos los datos cancelando job pendiente.

Callback del botón '↺ Actualizar' en barra inferior.
Cancela _refresh_job actual y llama _update() directo.

#### `_on_close(self)`

Maneja el cierre de la ventana limpiando recursos.

Callback del botón cerrar en header.
- Cancela job de refresco pendiente.
- Registra cierre en logger.
- Destruye ventana.

</details>
