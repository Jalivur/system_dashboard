# `core.display_service`

> **Ruta**: `core/display_service.py`

Servicio de control de brillo de la pantalla.
Detecta automáticamente el método disponible:
  - 'sysfs'     : /sys/class/backlight/ (driver kernel estándar)
  - 'wlr-randr' : Wayland (Raspberry Pi OS Bookworm por defecto)
  - 'xrandr'    : X11
  - 'none'      : no disponible (ventana muestra aviso)

Hardware: Freenove FNK0100K (4.3" IPS DSI) — Raspberry Pi 5.

## Imports

```python
import subprocess
import threading
import json
from pathlib import Path
from typing import Optional
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `DSI_OUTPUT` | `'DSI-2'` |
| `BRIGHTNESS_MIN` | `10` |
| `BRIGHTNESS_MAX` | `100` |
| `BRIGHTNESS_OFF` | `0` |
| `DIM_TIMEOUT_S` | `120` |
| `OFF_TIMEOUT_S` | `2400000` |

<details>
<summary>Funciones privadas</summary>

### `_find_backlight() -> Optional[Path]`

Busca primera ruta válida en _BACKLIGHT_CANDIDATES.

Returns:
    Path o None.

### `_detect_method() -> str`

Detecta el método disponible para controlar el brillo.

</details>

## Clase `DisplayService`

Servicio de control de brillo.
No tiene thread permanente — el dim/off usa threading.Timer igual que
otros servicios ligeros del proyecto.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_method` | `_detect_method()` |
| `_backlight` | `_find_backlight() if self._method == 'sysfs' else None` |
| `_lock` | `threading.Lock()` |
| `_dimmed` | `False` |
| `_running` | `True` |

### Métodos públicos

#### `start(self) -> None`

Activa servicio (set _running=True).

#### `stop(self) -> None`

Detiene servicio, cancela dim timers.

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo.

#### `is_available(self) -> bool`

True si hay algún método de control de brillo disponible.

#### `get_method(self) -> str`

Devuelve el método activo: 'sysfs', 'wlr-randr', 'xrandr' o 'none'.

#### `get_brightness(self) -> int`

Devuelve el brillo actual en porcentaje (0-100).

#### `set_brightness(self, pct: int) -> bool`

Establece el brillo. pct en rango 0-100.
Devuelve True si tuvo éxito.

#### `screen_off(self) -> bool`

Apaga la pantalla (brillo = 0).

#### `screen_on(self) -> bool`

Enciende la pantalla al último nivel guardado.

#### `notify_activity(self)`

Llamar desde la UI en cada interacción del usuario.
Cancela el timer, restaura brillo si estaba en dim, reinicia el timer.

#### `enable_dim_on_idle(self)`

Activa modo dim/off por inactividad. Llamar al iniciar UI.

#### `disable_dim_on_idle(self)`

Desactiva ahorro por inactividad (cancela timers).

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Detecta método (sysfs/wlr-randr/xrandr), carga estado persistido brillo.

#### `_set_sysfs(self, pct: int) -> bool`

Backend sysfs: convierte PCT a valor 0-max_brightness.

#### `_set_wlr(self, pct: int) -> bool`

Backend wlr-randr --output DSI-2 --brightness (PCT→float 0.0-1.0).

#### `_set_xrandr(self, pct: int) -> bool`

Backend xrandr --output DSI-2 --brightness (PCT→float 0.0-1.0).

#### `_start_dim_timer(self)`

Inicia/reinicia Timer para dim por inactividad (DIM_TIMEOUT_S).

#### `_cancel_dim_timer(self)`

Cancela timer activo si existe.

#### `_on_dim(self)`

Callback timer: dim 20%, schedule _on_off (OFF_TIMEOUT_S).

#### `_on_off(self)`

Callback timer: screen_off() total blackout.

#### `_save_state(self)`

Persiste brillo actual data/display_state.json.

#### `_load_state(self)`

Carga brillo persistido, restaura si válido (>0).

</details>
