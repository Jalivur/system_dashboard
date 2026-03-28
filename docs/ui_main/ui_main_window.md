# `ui.main_window`

> **Ruta**: `ui/main_window.py`

> **Cobertura de documentación**: 🟢 100% (8/8)

Ventana principal del sistema de monitoreo.

Responsabilidades de este fichero:
  - Construir el layout (header, pestanas, area de botones, footer)
  - Gestionar el cambio de pestana y el filtrado de botones por visibilidad
  - Coordinar BadgeManager, UpdateLoop y WindowLifecycleManager

Todo lo demas vive en modulos especializados:
  ui/main_badges.py         — BadgeManager
  ui/main_update_loop.py    — UpdateLoop
  ui/main_system_actions.py — exit_application, restart_application
  ui/window_lifecycle.py    — WindowLifecycleManager
  ui/window_manager.py      — WindowManager (visibilidad JSON)

---

## Tabla de contenidos

**Clase [`MainWindow`](#clase-mainwindow)**

---

## Dependencias internas

- `config.button_labels`
- `config.settings`
- `ui.main_badges`
- `ui.main_system_actions`
- `ui.main_update_loop`
- `ui.styles`
- `ui.window_lifecycle`
- `ui.window_manager`
- `ui.windows`
- `utils.logger`
- `utils.system_utils`

## Imports

```python
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, Icons
import config.button_labels as BL
from config.settings import UI as UICfg
from ui.styles import StyleManager, make_futuristic_button
from ui.windows import FanControlWindow, MonitorWindow, NetworkWindow, USBWindow, ProcessWindow, ServiceWindow, HistoryWindow, LaunchersWindow, ThemeSelector, DiskWindow, UpdatesWindow, HomebridgeWindow, NetworkLocalWindow, PiholeWindow, AlertHistoryWindow, DisplayWindow, VpnWindow, OverviewWindow, LedWindow, CameraWindow, ServicesManagerWindow, LogViewerWindow, ButtonManagerWindow, CrontabWindow, HardwareInfoWindow, SSHWindow, WiFiWindow, ConfigEditorWindow, AudioWindow, WeatherWindow, I2CWindow, GPIOWindow, ServiceWatchdogWindow, LogConfigWindow
from ui.window_manager import WindowManager
from ui.window_lifecycle import WindowLifecycleManager
from ui.main_badges import BadgeManager
from ui.main_update_loop import UpdateLoop
from ui.main_system_actions import exit_application, restart_application
from utils.system_utils import SystemUtils
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `MainWindow`

Inicializa la ventana principal del dashboard.

Args:
    root (CTk): Ventana root DSI fullscreen.
    registry (ServiceRegistry): Registro de todos los monitores y servicios.
    update_interval (int): Intervalo de actualización de badges/UI en milisegundos (por defecto 2000).

Raises:
    None

Returns:
    None

### Atributos públicos

| Atributo | Valor inicial |
|----------|---------------|
| `root` | `root` |
| `registry` | `registry` |
| `update_interval` | `update_interval` |
| `system_utils` | `SystemUtils()` |
| `system_monitor` | `registry.get('system_monitor')` |
| `fan_controller` | `registry.get('fan_controller')` |
| `fan_service` | `registry.get('fan_service')` |
| `data_service` | `registry.get('data_service')` |
| `network_monitor` | `registry.get('network_monitor')` |
| `disk_monitor` | `registry.get('disk_monitor')` |
| `process_monitor` | `registry.get('process_monitor')` |
| `service_monitor` | `registry.get('service_monitor')` |
| `update_monitor` | `registry.get('update_monitor')` |
| `cleanup_service` | `registry.get('cleanup_service')` |
| `homebridge_monitor` | `registry.get('homebridge_monitor')` |
| `network_scanner` | `registry.get('network_scanner')` |
| `pihole_monitor` | `registry.get('pihole_monitor')` |
| `alert_service` | `registry.get('alert_service')` |
| `display_service` | `registry.get('display_service')` |
| `vpn_monitor` | `registry.get('vpn_monitor')` |
| `led_service` | `registry.get('led_service')` |
| `hardware_monitor` | `registry.get('hardware_monitor')` |
| `audio_alert_service` | `registry.get('audio_alert_service')` |
| `ssh_monitor` | `registry.get('ssh_monitor')` |
| `wifi_monitor` | `registry.get('wifi_monitor')` |
| `audio_service` | `registry.get('audio_service')` |
| `weather_service` | `registry.get('weather_service')` |
| `i2c_monitor` | `registry.get('i2c_monitor')` |
| `gpio_monitor` | `registry.get('gpio_monitor')` |
| `service_watchdog` | `registry.get('service_watchdog')` |

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_menu_btns` | `{}` |
| `_active_tab` | `UICfg.MENU_TABS[0][0]` |
| `_tab_buttons` | `{}` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, root, registry, update_interval = 2000)`

Inicializa la ventana principal del dashboard.

Args:
    root (CTk): Ventana root DSI fullscreen.
    registry (ServiceRegistry): Registro de todos los monitores y servicios.
    update_interval (int): Intervalo de actualización de insignias/UI en milisegundos (predeterminado 2000).

Returns:
    None

Raises:
    None

#### `_create_ui(self)`

Crea la interfaz de usuario completa, incluyendo el diseño de la ventana principal 
con header, pestañas, área de botones y footer.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_register_windows(self)`

Registra ventanas hijas en el administrador de ciclo de vida de ventanas.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_build_buttons_meta(self)`

Crea un diccionario que mapeia etiquetas de botones a tuplas con funciones de apertura de ventanas y listas de claves de insignias.

Usado en _switch_tab para renderizar botones de pestañas dinámicamente.

Returns:
    dict: label → (command, [badges]).

#### `_switch_tab(self, key: str) -> None`

Cambia la pestaña activa y actualiza la interfaz de usuario en consecuencia.

Args:
    key (str): La clave de identificación de la pestaña a activar (por ejemplo, 'overview', 'services').

Returns:
    None

Raises:
    None

#### `_btn_active(self, text_key: str) -> None`

Resalta el botón activo en la ventana principal.

Args:
    text_key (str): Clave de texto del botón, según se define en button_labels.py.

Returns:
    None

Raises:
    Exception: Si ocurre un error al configurar el botón.

#### `_btn_idle(self, text_key: str) -> None`

Restaura el estilo idle de un botón.

Args:
    text_key (str): Clave de texto del botón desde button_labels.py.

Returns:
    None

Raises:
    Exception: Si ocurre un error al configurar el botón.

</details>
