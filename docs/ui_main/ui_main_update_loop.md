# `ui.main_update_loop`

> **Ruta**: `ui/main_update_loop.py`

> **Cobertura de documentación**: 🟢 100% (11/11)

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

---

## Tabla de contenidos

**Clase [`UpdateLoop`](#clase-updateloop)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)

---

## Dependencias internas

- `config.settings`
- `core.event_bus`
- `utils.logger`

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

Encapsula los dos loops de actualización del dashboard: reloj/uptime y badges del menú principal.

Args:
    root:            widget Tk raíz
    badge_mgr:       instancia de BadgeManager
    monitors:        diccionario con monitores necesarios
    update_interval: intervalo en milisegundos para el loop de badges
    clock_label:     etiqueta del reloj en el encabezado
    uptime_label:    etiqueta del uptime en el encabezado
    weather_service: servicio meteorológico opcional para el badge de lluvia

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

Inicia el ciclo de actualización. 

Args: 
    None

Returns: 
    None

Raises: 
    None

#### `stop(self) -> None`

Detiene el bucle de actualización cancelando los callbacks pendientes.

Args:
    None

Returns:
    None

Raises:
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self, root, badge_mgr, monitors: dict, update_interval: int, clock_label, uptime_label, weather_service = None)`

Inicializa el bucle de actualización de la aplicación.

Args:
    root:            widget Tk raíz de la aplicación.
    badge_mgr:       instancia de BadgeManager para gestionar las insignitas.
    monitors:        diccionario con monitores necesarios (system, update, homebridge, pihole, vpn, service).
    update_interval: intervalo en milisegundos para el bucle de actualización de insignitas.
    clock_label:     etiqueta CTkLabel del reloj en el encabezado.
    uptime_label:    etiqueta CTkLabel del tiempo de actividad en el encabezado.
    weather_service: servicio WeatherService opcional para la insignita de lluvia.

#### `_tick_clock(self) -> None`

Actualiza el reloj y el tiempo de actividad del sistema.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_update_badges(self) -> None`

Actualiza todos los badges del menú.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_update_misc_badges(self) -> None`

Actualiza los badges misceláneos de actualizaciones, Homebridge, Pi-hole y VPN.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Exception: Si ocurre un error al actualizar algún badge.

#### `_update_service_badge(self) -> None`

Actualiza el distintivo de servicios fallidos desde el monitor de servicios.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Excepción genérica en caso de error durante la actualización del distintivo.

#### `_update_weather_badge(self) -> None`

Actualiza el distintivo del botón de clima para indicar probabilidad de lluvia en las próximas 3 horas.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Exception: Si ocurre un error al actualizar el distintivo, se registra un mensaje de advertencia.

#### `_update_watchdog_badge(self) -> None`

Actualiza el badge de reinicios del service watchdog con el contador de reinicios del día.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Excepción genérica en caso de error durante la actualización del badge.

#### `_update_system_badges(self) -> None`

Actualiza los badges de sistema relacionados con temperatura, CPU, RAM y disco duro.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

</details>
