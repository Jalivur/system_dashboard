# `ui.windows.pihole_window`

> **Ruta**: `ui/windows/pihole_window.py`

> **Cobertura de documentación**: 🟢 100% (7/7)

Ventana de estadísticas de Pi-hole.

---

## Tabla de contenidos

**Clase [`PiholeWindow`](#clase-piholewindow)**

---

## Dependencias internas

- `config.settings`
- `core.pihole_monitor`
- `ui.styles`
- `utils.logger`

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from core.pihole_monitor import PiholeMonitor
from utils.logger import get_logger
import threading
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `UPDATE_MS` | `5000` |

## Clase `PiholeWindow(ctk.CTkToplevel)`

Ventana de estadísticas de Pi-hole.

Args:
    parent: Ventana padre (generalmente la ventana principal del dashboard).
    pihole_monitor (PiholeMonitor): Instancia del monitor para obtener estadísticas.

Raises:
    None

Returns:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_pihole` | `pihole_monitor` |
| `_update_job` | `None` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, pihole_monitor: PiholeMonitor)`

Inicializa la ventana de estadísticas de Pi-hole.

Configura el título, geometría, posición y propiedades de la ventana Toplevel.
Crea la interfaz de usuario, programa la primera actualización automática
y registra la apertura en el logger.

Args:
    parent: Ventana padre (generalmente la ventana principal del dashboard).
    pihole_monitor (PiholeMonitor): Instancia del monitor para obtener estadísticas.

Raises:
    None
Returns:
    None

#### `_create_ui(self)`

Crea la interfaz gráfica de usuario de la ventana.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_schedule_update(self)`

Programa la primera actualización de la interfaz.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_force_refresh(self)`

Fuerza la actualización manual de estadísticas Pi-hole en segundo plano de manera no bloqueante.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

Nota: Verifica si el monitor está activo antes de forzar la actualización.

#### `_render(self)`

Actualiza los valores en pantalla con la caché del monitor.

Args:
    None

Returns:
    None

Raises:
    None

#### `_on_close(self)`

Maneja el cierre ordenado de la ventana de Pi-hole.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
