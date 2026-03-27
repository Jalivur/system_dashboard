# `ui.main_update_loop`

> **Ruta**: `ui/main_update_loop.py`

Loop de actualizacion del menu principal.

Gestiona tres ciclos independientes:
  - Reloj / uptime: cada 1 segundo via root.after
  - Badges del menu: cada update_interval ms via root.after
  - Eventos del bus: procesa eventos publicados desde threads secundarios

Ambos ciclos leen exclusivamente caches de los monitores — nunca bloquean la UI.

Uso en MainWindow:
    self._update_loop = UpdateLoop(
        root=self.root,
        badge_mgr=self._badge_mgr,
        monitors={...},
        update_interval=2000,
        clock_label=self._clock_label,
        uptime_label=self._uptime_label,
    )
    self._update_loop.start()

    # Al salir, antes de root.destroy():
    self._update_loop.stop()

## Imports

```python
from datetime import datetime
from config.settings import COLORS
from core.event_bus import get_event_bus
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `UpdateLoop`

Encapsula los dos loops de actualizacion del dashboard:
reloj/uptime y badges del menu principal.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_root` | `root` |
| `_badge_mgr` | `badge_mgr` |
| `_monitors` | `monitors` |
| `_update_interval` | `update_interval` |
| `_clock_label` | `clock_label` |
| `_uptime_label` | `uptime_label` |
| `_weather_service` | `weather_service` |
| `_uptime_tick` | `0` |
| `_running` | `False` |
| `_clock_after_id` | `None` |
| `_badges_after_id` | `None` |

### Métodos públicos

#### `start(self) -> None`

Arranca ambos loops. Llamar una sola vez tras construir la UI.

#### `stop(self) -> None`

Detiene ambos loops cancelando los after() pendientes.
Llamar antes de root.destroy() para evitar callbacks sobre
widgets ya destruidos.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, root, badge_mgr, monitors: dict, update_interval: int, clock_label, uptime_label, weather_service = None)`

Args:
    root:            widget Tk raiz
    badge_mgr:       instancia de BadgeManager
    monitors:        dict con los monitores necesarios:
                     system_monitor, update_monitor, homebridge_monitor,
                     pihole_monitor, vpn_monitor, service_monitor
    update_interval: intervalo en ms para el loop de badges
    clock_label:     CTkLabel del reloj en el header
    uptime_label:    CTkLabel del uptime en el header
    weather_service: WeatherService opcional para badge de lluvia

#### `_tick_clock(self) -> None`

Actualiza reloj cada segundo y uptime cada minuto

#### `_update_badges(self) -> None`

Actualiza todos los badges del menu. Solo lee caches — nunca bloquea la UI.

#### `_update_misc_badges(self) -> None`

Actualiza badges misceláneos: updates, homebridge, pihole, vpn

#### `_update_service_badge(self) -> None`

Actualiza badge de servicios fallidos desde service_monitor

#### `_update_weather_badge(self) -> None`

Muestra badge en el botón de clima si hay lluvia probable en las próximas 3h.

#### `_update_watchdog_badge(self) -> None`

Actualiza badge de reinicios del service_watchdog

Muestra contados de reinicios del día si hay alguno.

#### `_update_system_badges(self) -> None`

Actualiza badges de sistema (temp, cpu, ram, disk) desde system_monitor cache

</details>
