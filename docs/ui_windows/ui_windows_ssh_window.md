# `ui.windows.ssh_window`

> **Ruta**: `ui/windows/ssh_window.py`

Ventana de monitor de sesiones SSH.
Muestra sesiones activas (who) e historial de conexiones (last).
Se refresca automáticamente cada 30 segundos via SSHMonitor.
Los widgets se crean una sola vez — solo se actualizan los valores.

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

pts/0 → Sesión 1 · tty1 → Consola local

### `_fmt_ip(raw: str) -> str`

192.168.x.x → 192.168.x.x (local) · vacío → Consola local

### `_fmt_time_active(date: str, time: str) -> str`

2026-03-04 10:22 → Conectado desde las 10:22

### `_fmt_time_history(raw: str) -> str`

Transforma la cadena de time_info del historial en algo legible.
Ejemplos de entrada:
    'Tue Mar  4 10:22   still logged in'
    'Mon Mar  3 21:10 - 21:45  (00:35)'
    'Mon Mar  3 09:00 - crash'
    'Mon Mar  3 09:00 - down'

</details>

## Clase `SSHWindow(ctk.CTkToplevel)`

Ventana de monitor de sesiones SSH.

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

#### `_create_ui(self)`

Crea toda la interfaz de usuario una sola vez al inicializar la ventana.

Incluye header, scrollable canvas, tarjetas de sesiones e historial,
y barra de controles con botón de actualización manual.

#### `_build_sessions_card(self)`

Crea la tarjeta de sesiones activas con filas fijas (máximo 10).

#### `_build_history_card(self)`

Crea la tarjeta de historial con filas fijas (50 entradas).

#### `_update(self)`

Actualiza los datos visuales de sesiones activas e historial de conexiones.

Obtiene estadísticas del SSHMonitor, refresca widgets sin recrearlos,
maneja estado parado del monitor, y programa la próxima actualización
cada 30 segundos.

Returns:
    None

#### `_refresh_sessions(self, sessions: list)`

Refresca la visualización de las sesiones SSH activas actuales.

Muestra hasta 10 filas; oculta filas extras y mensaje 'Ninguna' si vacío.
Actualiza badges de conteo y colores de estado.

Args:
    sessions: Lista de dicts con claves 'user', 'tty', 'ip' (opcional),
              'date' (opcional), 'time'.

#### `_refresh_history(self, history: list)`

Refresca la visualización del historial reciente de conexiones SSH.

Muestra hasta 50 entradas con colores alternos; oculta extras si vacío.

Args:
    history: Lista de dicts con claves 'user', 'tty', 'ip' (opcional),
             'time_info' (cadena con detalles de tiempo).

#### `_force_refresh(self)`

Fuerza una actualización inmediata de todos los datos SSH.

Cancela el job automático pendiente y llama a _update directamente.

#### `_on_close(self)`

Limpia recursos y cierra la ventana de forma segura.

Cancela jobs de refresco pendientes y registra cierre en logger.

</details>
