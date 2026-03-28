# `core.wifi_monitor`

> **Ruta**: `core/wifi_monitor.py`

> **Cobertura de documentación**: 🟢 100% (21/21)

Monitor de conexión WiFi profesional.
Recopila SSID, señal (dBm), calidad link, bitrate, ruido, tráfico RX/TX Mbps.
Thread daemon cada 5s, históricos, cambio interfaz en caliente, persistencia.
Fallback ip/iwconfig/ifconfig.

---

## Tabla de contenidos

**Clase [`WiFiMonitor`](#clase-wifimonitor)**
  - [`start()`](#startself)
  - [`stop()`](#stopself)
  - [`is_running()`](#is_runningself-bool)
  - [`get_signal_history()`](#get_signal_historyself-list)
  - [`set_interface()`](#set_interfaceself-iface-str-none)
  - [`get_available_interfaces()`](#get_available_interfaces-list)
  - [`get_stats()`](#get_statsself-dict)
  - [`interface()`](#interfaceself-str)
  - [`signal_color()`](#signal_colordbm-optionalint-colors-dict-str)
  - [`signal_quality_pct()`](#signal_quality_pctdbm-optionalint-int)

---

## Dependencias internas

- `config.local_settings_io`
- `config.settings`
- `utils.logger`

## Imports

```python
import re
import subprocess
import threading
from collections import deque
from typing import Optional
from config.settings import HISTORY
from datetime import datetime
from utils.logger import get_logger
from config.local_settings_io import get_param
from config.local_settings_io import update_params
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `WIFI_SIGNAL_GOOD` | `-60` |
| `WIFI_SIGNAL_WARN` | `-75` |

<details>
<summary>Funciones privadas</summary>

### `_run(cmd: list) -> str`

Ejecuta un comando shell y retorna la salida estándar limpia.

Args:
    cmd (list): Comando a ejecutar.

Returns:
    str: Salida estándar del comando o cadena vacía en caso de fallo.

Raises:
    Exception: Si ocurre un error durante la ejecución del comando.

### `_parse_iwconfig(raw: str) -> dict`

Extrae información WiFi de la salida cruda de iwconfig.

Args:
    raw (str): Salida cruda de iwconfig.

Returns:
    dict: Diccionario con métricas WiFi como ssid, signal_dbm, link_quality, link_quality_max, bitrate y noise_dbm.

Raises:
    None

### `_parse_iw_link(raw: str) -> dict`

Extrae información de conexión inalámbrica de la salida del comando `iw dev <iface> link`.

Args:
    raw (str): Salida cruda del comando `iw dev <iface> link`.

Returns:
    dict: Diccionario con los campos "ssid", "signal_dbm" y "bitrate".

Raises:
    None

</details>

## Clase `WiFiMonitor`

Monitor de WiFi que proporciona información en tiempo real y históricos de tráfico.

Args:
    interface (str, optional): Interfaz de red inalámbrica a monitorear.

Raises:
    Exception: Si no se puede inicializar el monitor.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_iface` | `interface or self._load_saved_interface() or _IFACE_DEFAULT` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_lock` | `threading.Lock()` |
| `_thread` | `None` |
| `_signal_hist` | `deque(maxlen=HISTORY)` |
| `_rx_hist` | `deque(maxlen=HISTORY)` |
| `_tx_hist` | `deque(maxlen=HISTORY)` |

### Métodos públicos

#### `start(self)`

Inicia el monitoreo de WiFi en segundo plano.

Args:
    None

Returns:
    None

Raises:
    None

#### `stop(self)`

Detiene el servicio de monitoreo de WiFi.

Args:
    None

Returns:
    None

Raises:
    None

#### `is_running(self) -> bool`

Indica si el monitor de WiFi está en ejecución.

Args:
    None

Returns:
    bool: True si el monitor está en ejecución, False de lo contrario.

Raises:
    None

#### `get_signal_history(self) -> list`

Obtiene el histórico de señal de WiFi en dBm de los últimos puntos registrados.

Args:
    No requiere parámetros.

Returns:
    list: Lista de valores de señal de WiFi en dBm.

#### `set_interface(self, iface: str) -> None`

Cambia la interfaz de red en tiempo de ejecución.

Args:
    iface (str): Nombre de la interfaz de red a utilizar.

Returns:
    None

Raises:
    None

#### `get_available_interfaces() -> list`

Obtiene la lista de interfaces de red inalámbrica disponibles.

Args: None

Returns:
    list[str]: Lista ordenada de interfaces inalámbricas disponibles.

Raises:
    Exception: Si ocurre un error al leer la lista de interfaces.

#### `get_stats(self) -> dict`

Obtiene un snapshot completo de las estadísticas de WiFi de manera thread-safe y no bloqueante.

Args:
    No aplica.

Returns:
    dict: Información de WiFi, incluyendo velocidades y registros históricos, junto con un timestamp.

Raises:
    No aplica.

#### `interface(self) -> str`

Obtiene la interfaz de red actual.

Args:
    Ninguno.

Returns:
    str: La interfaz de red actual, por ejemplo "wlan0".

#### `signal_color(dbm: Optional[int], colors: dict) -> str`

Determina el color semáforo según el nivel de señal de WiFi en dBm.

Args:
    dbm (int|None): Nivel de señal de WiFi en dBm.
    colors (dict): Diccionario con claves de color ('success', 'warning', 'danger', 'text_dim').

Returns:
    str: Clave del color correspondiente al nivel de señal.

Raises:
    Ninguna excepción relevante.

#### `signal_quality_pct(dbm: Optional[int]) -> int`

Convierte un nivel de señal en dBm a porcentaje de calidad de señal de WiFi.

Args:
    dbm (Optional[int]): Nivel de señal en decibelios con referencia a un miliwatt.

Returns:
    int: Calidad de señal como porcentaje (0-100).

Raises:
    Ninguna excepción explícita, devuelve 0 si dbm es None.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, interface: Optional[str] = None)`

Inicializa el monitor de WiFi con una interfaz específica.

Args:
    interface (str, optional): Interfaz de red inalámbrica, como wlan0 o wlan1.

#### `_load_saved_interface() -> Optional[str]`

Carga la interfaz de red WiFi guardada desde la configuración local.

Args:
    None

Returns:
    La interfaz de red WiFi guardada o None si no existe.

Raises:
    Exception: Si ocurre un error al cargar la configuración.

#### `_persist_interface(iface: str) -> None`

Persiste la interfaz de red WiFi en la configuración local.

Args:
    iface (str): Nombre de la interfaz de red WiFi a persistir.

Raises:
    Exception: Si ocurre un error al persistir la interfaz.

#### `_loop(self)`

Ejecuta el bucle de polling del monitor de WiFi.

Args:
    None

Returns:
    None

Raises:
    None

#### `_poll(self)`

Realiza un ciclo de polling para actualizar la información de la interfaz de red inalámbrica.

Args:
    None

Returns:
    None

Raises:
    None

#### `_read_proc_net_dev(self, iface: str) -> tuple`

Lee bytes RX/TX desde /proc/net/dev para una interfaz de red específica.

Args:
    iface (str): Nombre de la interfaz de red.

Returns:
    tuple[int, int]: Tupla con bytes recibidos y transmitidos.

Raises:
    Exception: Si ocurre un error al leer el archivo /proc/net/dev.

#### `_calc_speed(self, rx: int, tx: int) -> tuple`

Calcula la velocidad de transferencia de datos en Mbps.

Args:
    rx (int): Número de bytes recibidos.
    tx (int): Número de bytes transmitidos.

Returns:
    tuple[float, float]: Velocidad de recepción y transmisión en Mbps.

Raises:
    None

</details>
