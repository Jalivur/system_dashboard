# `ui.windows.ssh_window`

> **Ruta**: `ui/windows/ssh_window.py`

> **Cobertura de documentación**: 🟢 100% (14/14)

Ventana de monitor de sesiones SSH.
Muestra sesiones activas (who) e historial de conexiones (last).
Se refresca automáticamente cada 30 segundos via SSHMonitor.
Los widgets se crean una sola vez — solo se actualizan los valores.

---

## Tabla de contenidos

**Clase [`SSHWindow`](#clase-sshwindow)**

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `utils.logger`

## Imports

```python
import re
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

<details>
<summary>Funciones privadas</summary>

### `_fmt_tty(raw: str) -> str`

Formatea una cadena de texto que representa un terminal de tty para su visualización.

Args:
    raw (str): La cadena de texto a formatear.

Returns:
    str: La cadena de texto formateada.

Raises:
    None

### `_fmt_ip(raw: str) -> str`

Formatea una dirección IP para su visualización.

Args:
    raw (str): La dirección IP a formatear.

Returns:
    str: La dirección IP formateada con indicador de red local si corresponde.

### `_fmt_time_active(date: str, time: str) -> str`

Formatea la fecha y hora de conexión activa en un formato legible.

Args:
    date (str): Fecha de conexión en formato YYYY-MM-DD.
    time (str): Hora de conexión en formato HH:MM.

Returns:
    str: Cadena formateada con la hora y fecha de conexión, o cadena vacía si no se proporciona la hora.

Raises:
    None

### `_fmt_time_history(raw: str) -> str`

Formatea una cadena de historial de tiempo en un formato legible.

Args:
    raw (str): Cadena de tiempo en formato raw.

Returns:
    str: Cadena formateada con información de tiempo.

Raises:
    Ninguna excepción relevante.

</details>

## Clase `SSHWindow(ctk.CTkToplevel)`

Ventana emergente para monitorizar sesiones SSH en tiempo real.

Args:
    parent: Ventana padre (CTkToplevel) que alberga la ventana de monitor.
    ssh_monitor: Instancia de SSHMonitor para obtener estadísticas en tiempo real.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_ssh_monitor` | `ssh_monitor` |
| `_refresh_job` | `None` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, ssh_monitor)`

Inicializa la ventana de monitor SSH.

Args:
    parent: Ventana padre (CTkToplevel).
    ssh_monitor: Instancia de SSHMonitor para obtener estadísticas en tiempo real.

Raises:
    None

Returns:
    None

#### `_create_ui(self)`

Crea la interfaz de usuario de la ventana de SSH.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_build_sessions_card(self)`

Crea la tarjeta de sesiones activas con filas fijas.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_build_history_card(self)`

Crea la tarjeta de historial con filas fijas para mostrar conexiones.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update(self)`

Actualiza los datos visuales de sesiones activas e historial de conexiones.

Obtiene estadísticas del SSHMonitor, refresca widgets sin recrearlos,
maneja estado parado del monitor, y programa la próxima actualización.

Args: 
    None

Returns: 
    None

Raises: 
    None

#### `_refresh_sessions(self, sessions: list)`

Refresca la visualización de las sesiones SSH activas actuales.

Muestra hasta 10 filas; oculta filas extras y mensaje 'Ninguna' si vacío.
Actualiza badges de conteo y colores de estado.

Args:
    sessions: Lista de dicts con claves 'user', 'tty', 'ip' (opcional),
              'date' (opcional), 'time'.

Returns:
    None

Raises:
    None

#### `_refresh_history(self, history: list)`

Refresca la visualización del historial reciente de conexiones SSH.

    Args:
        history: Lista de diccionarios con claves 'user', 'tty', 'ip' (opcional) y 'time_info'.

    Nota: Muestra hasta 50 entradas con colores alternos y oculta extras si la lista está vacía.

#### `_force_refresh(self)`

Fuerza una actualización inmediata de todos los datos SSH.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_close(self)`

Limpia recursos y cierra la ventana de forma segura.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
