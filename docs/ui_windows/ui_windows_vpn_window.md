# `ui.windows.vpn_window`

> **Ruta**: `ui/windows/vpn_window.py`

> **Cobertura de documentación**: 🟢 100% (8/8)

Ventana de gestión de conexiones VPN.
Muestra el estado en tiempo real y permite conectar/desconectar
usando los scripts del usuario.

---

## Tabla de contenidos

**Clase [`VpnWindow`](#clase-vpnwindow)**
  - [`destroy()`](#destroyself)

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `ui.widgets.dialogs`
- `utils.logger`

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR, Icons, UPDATE_MS
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets.dialogs import terminal_dialog
from utils.logger import get_logger
import os
from ui.widgets.dialogs import custom_msgbox
from ui.widgets.dialogs import custom_msgbox
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `VpnWindow(ctk.CTkToplevel)`

Ventana de gestión de VPN.

Args:
    parent: Ventana padre CTkToplevel de la aplicación principal.
    vpn_monitor: Instancia del monitor de VPN que proporciona el estado en tiempo real.

Raises:
    Exception: Si hay errores en la configuración inicial de la UI.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_vpn_monitor` | `vpn_monitor` |
| `_widgets` | `{}` |

### Métodos públicos

#### `destroy(self)`

Destruye la ventana de VPN de forma controlada.

    Args:
        None

    Returns:
        None

    Raises:
        None

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, vpn_monitor)`

Inicializa la ventana principal de gestión de conexiones VPN.

Configura la ventana toplevel con dimensiones y posición específicas.

Args:
    parent: Ventana padre CTkToplevel de la aplicación principal.
    vpn_monitor: Instancia del monitor de VPN que proporciona el estado en tiempo real.

Raises:
    Exception: Si hay errores en la configuración inicial de la UI.

#### `_create_ui(self)`

Construye la interfaz gráfica de usuario de la ventana VPN.

Crea frames jerárquicos y componentes visuales.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update(self)`

Actualiza el estado visual de la ventana según el estado del monitor de VPN.

Args: 
    Ninguno (usa atributos de instancia internamente).

Returns: 
    Ninguno.

Raises: 
    Ninguno.

#### `_connect(self)`

Inicia la conexión VPN ejecutando el script conectar_vpn.sh en una terminal en vivo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_disconnect(self)`

Desconecta la VPN ejecutando el script de desconexión en una terminal en vivo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_action_done(self)`

Callback ejecutado al finalizar operaciones de conexión/desconexión.

Garantiza sincronización UI-monitor tras ejecución de scripts externos.

Args:
    None

Returns:
    None

Raises:
    None

</details>
