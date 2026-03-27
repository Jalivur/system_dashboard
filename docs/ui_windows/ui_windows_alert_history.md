# `ui.windows.alert_history`

> **Ruta**: `ui/windows/alert_history.py`

Ventana de historial de alertas disparadas por AlertService.
Lee data/alert_history.json y muestra las entradas con colores por nivel.

## Imports

```python
import customtkinter as ctk
from datetime import datetime
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import make_window_header, make_futuristic_button, StyleManager
from ui.widgets import confirm_dialog
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `LEVEL_COLORS` | `{'warn': '#FFA500', 'crit': '#FF4444'}` |
| `KEY_LABELS` | `{'temp_warn': f'{Icons.THERMOMETER} Temperatura — aviso', 'temp_crit': f'{Icons....` |

## Clase `AlertHistoryWindow(ctk.CTkToplevel)`

Ventana de historial de alertas.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_alert_service` | `alert_service` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, alert_service)`

Inicializa la ventana de historial de alertas.

#### `_create_ui(self)`

Crea todos los elementos de la interfaz de usuario.

#### `_load(self)`

Lee el historial y redibuja la lista.

#### `_create_entry_card(self, entry: dict)`

Crea una tarjeta para una entrada del historial.

#### `_confirm_clear(self)`

Muestra diálogo de confirmación para borrar el historial.

#### `_clear(self)`

Borra el historial de alertas y recarga la vista.

</details>
