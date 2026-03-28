# `ui.windows.alert_history`

> **Ruta**: `ui/windows/alert_history.py`

> **Cobertura de documentación**: 🟢 100% (7/7)

Ventana de historial de alertas disparadas por AlertService.
Lee data/alert_history.json y muestra las entradas con colores por nivel.

---

## Tabla de contenidos

**Clase [`AlertHistoryWindow`](#clase-alerthistorywindow)**

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

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

Representa una ventana emergente que muestra el historial de alertas.

Args:
    parent: La ventana padre que crea esta instancia.
    alert_service: El servicio de alertas que proporciona los datos históricos.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_alert_service` | `alert_service` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, alert_service)`

Inicializa la ventana de historial de alertas.

Args:
    parent: La ventana padre.
    alert_service: El servicio de alertas.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno

#### `_create_ui(self)`

Crea todos los elementos de la interfaz de usuario de la ventana de historial de alertas.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_load(self)`

Carga el historial de alertas y actualiza la lista de alertas en la ventana.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_entry_card(self, entry: dict)`

Crea una tarjeta para una entrada del historial de alertas.

Args:
    entry (dict): Diccionario con información de la entrada del historial.

Returns:
    None

Raises:
    None

#### `_confirm_clear(self)`

Muestra un diálogo de confirmación para borrar todo el historial de alertas.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_clear(self)`

Borra el historial de alertas y recarga la vista.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
