# `ui.main_window`

> **Ruta**: `ui/main_window.py`

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

Ventana principal del dashboard

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

Inicializa MainWindow principal dashboard.

Args:
    root (CTk): Ventana root DSI fullscreen.
    registry (ServiceRegistry): Todos monitors/servicios.
    update_interval (int): ms badges/UI update (default 2000).

Inyecta self.services, build UI, managers, pestañas inicial overview.

#### `_create_ui(self)`

Construye layout completo: header (hostname/clock), pestañas scroll H/V, área botones, footer (gestor/reiniciar/salir).
Inicializa managers (Badge, WindowLifecycle, WindowManager, UpdateLoop).

#### `_register_windows(self)`

Registra ~35 ventanas hijas en WindowLifecycleManager con label/badge_keys.
Lambdas inyectan self.services donde needed.

#### `_build_buttons_meta(self)`

Mapea button_labels.BL → (lambda abrir ventana, list badge keys).

Usado en _switch_tab para render botones pestañas dinámicamente.

Returns:
    dict: label → (command, [badges]).

#### `_switch_tab(self, key: str) -> None`

Cambia pestaña activa, destruye botones viejos, renderiza nuevos basados en pestaña/UI config.

Args:
    key (str): ID pestaña (e.g., 'overview', 'services').

#### `_btn_active(self, text_key: str) -> None`

Resalta botón activo (llamado por WindowLifecycleManager).

Args:
    text_key (str): Label botón desde button_labels.py.

#### `_btn_idle(self, text_key: str) -> None`

Restaura estilo idle botón (llamado por WindowLifecycleManager).

Args:
    text_key (str): Label botón desde button_labels.py.

</details>
