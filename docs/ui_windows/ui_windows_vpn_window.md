# `ui.windows.vpn_window`

> **Ruta**: `ui/windows/vpn_window.py`

Ventana de gestión de conexiones VPN.
Muestra el estado en tiempo real y permite conectar/desconectar
usando los scripts del usuario.

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

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_vpn_monitor` | `vpn_monitor` |
| `_widgets` | `{}` |

### Métodos públicos

#### `destroy(self)`

Destruye la ventana de VPN de forma controlada.

Registra el cierre en el logger antes de llamar al método padre,
asegurando trazabilidad de eventos de UI.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, vpn_monitor)`

Inicializa la ventana principal de gestión de conexiones VPN.

Configura la ventana toplevel con dimensiones y posición específicas para DSI,
inicializa widgets y comienza el bucle de actualización automática del estado.

Args:
    parent: Ventana padre CTkToplevel de la aplicación principal.
    vpn_monitor: Instancia del monitor de VPN que proporciona el estado en tiempo real.

Raises:
    Exception: Si hay errores en la configuración inicial de la UI.

#### `_create_ui(self)`

Construye toda la interfaz gráfica de usuario de la ventana VPN.

Crea frames jerárquicos, tarjeta de estado con indicador visual,
botones de acción futuristas, sección de información de interfaz/IP,
y nota sobre scripts requeridos. Configura scroll si es necesario.

Utiliza colores y fuentes del sistema de temas global.

#### `_update(self)`

Actualiza el estado visual de la ventana cada UPDATE_MS milisegundos.

Obtiene datos del vpn_monitor (conectado, IP, interfaz), actualiza
colores/indicadores/textos en consecuencia. Maneja errores y detiene
si monitor no está corriendo o ventana destruida. Programa llamada recursiva.

Args:
    Ninguno (usa self._vpn_monitor y self._widgets internamente).

#### `_connect(self)`

Ejecuta conectar_vpn.sh con terminal en vivo.

#### `_disconnect(self)`

Ejecuta desconectar_vpn.sh con terminal en vivo.

#### `_on_action_done(self)`

Callback ejecutado al finalizar operaciones de conexión/desconexión.

Fuerza sondeo inmediato del monitor VPN y retrasa actualización UI
para permitir estabilización del estado post-script.

Garantiza sincronización UI-monitor tras ejecución de scripts externos.

</details>
