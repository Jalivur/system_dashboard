# `ui.windows.pihole_window`

> **Ruta**: `ui/windows/pihole_window.py`

Ventana de estadísticas de Pi-hole.

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

#### `_create_ui(self)`

Crea toda la interfaz gráfica de usuario (UI) de la ventana.

Construye el frame principal, el header con título y estado, el contenedor
con scroll, el canvas, el grid de 6 tarjetas métricas (queries, bloqueadas,
% bloqueado, dominios, clientes, estado), y el botón de actualización manual.
Inicializa labels para valores dinámicos.

#### `_schedule_update(self)`

Programa la primera actualización/renderizado de la interfaz.

Utiliza self.after(100ms) para llamar a _render inicialmente, iniciando
el ciclo de actualizaciones automáticas.

#### `_force_refresh(self)`

Fuerza actualización manual de estadísticas Pi-hole en background.        

1. Verifica monitor activo       
2. Lanza thread daemon -> self._pihole.fetch_now()        
3. Status -> "Actualizando..."        
4. self._render() @2000ms        

Non-blocking UI.

#### `_render(self)`

Actualiza los valores en pantalla con la caché del monitor.

#### `_on_close(self)`

Maneja el cierre ordenado de la ventana de Pi-hole.

Realiza cleanup:
- Cancela el job de actualización pendiente
- Registra el cierre en logs
- Destruye la ventana

</details>
