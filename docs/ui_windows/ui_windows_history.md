# `ui.windows.history`

> **Ruta**: `ui/windows/history.py`

> **Cobertura de documentación**: 🟢 100% (24/24)

Ventana de histórico de datos

---

## Tabla de contenidos

**Clase [`HistoryWindow`](#clase-historywindow)**

---

## Dependencias internas

- `config.settings`
- `core.cleanup_service`
- `core.data_analyzer`
- `core.data_logger`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

## Imports

```python
import customtkinter as ctk
from datetime import datetime, timedelta
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, DATA_DIR, EXPORTS_CSV_DIR, EXPORTS_SCR_DIR, Icons
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox, confirm_dialog
from core.data_analyzer import DataAnalyzer
from core.data_logger import DataLogger
from core.cleanup_service import CleanupService
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from utils.logger import get_logger
import os
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `HistoryWindow(ctk.CTkToplevel)`

Ventana de visualización de histórico de datos del sistema.

Args:
    parent: Ventana padre CTkToplevel.
    cleanup_service: Instancia de CleanupService para gestión de limpieza.

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_analyzer` | `DataAnalyzer()` |
| `_logger` | `DataLogger()` |
| `_cleanup_service` | `cleanup_service` |
| `_period_var` | `ctk.StringVar(master=self, value='24h')` |
| `_period_start` | `ctk.StringVar(master=self, value='YYYY-MM-DD HH:MM')` |
| `_period_end` | `ctk.StringVar(master=self, value='YYYY-MM-DD HH:MM')` |
| `_using_custom_range` | `False` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, cleanup_service: CleanupService)`

Inicializa la ventana de histórico de datos del sistema.

Args:
    parent: Ventana padre CTkToplevel.
    cleanup_service: Instancia de CleanupService para gestión de limpieza.

Returns:
    None

Raises:
    None

#### `_create_ui(self)`

Crea la interfaz de usuario completa de la ventana de historial.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_period_controls(self, parent)`

Crea los controles de periodo en la ventana de historial.

Args:
    parent: El elemento padre donde se crearán los controles.

Returns:
    None

Raises:
    None

#### `_create_range_panel(self, parent)`

Crea un panel para seleccionar un rango de fechas con campos para inicio y fin.

Args:
    parent: El padre del panel.

Returns:
    None

Raises:
    None

#### `_create_graphs_area(self, parent)`

Crea el área de gráficas utilizando matplotlib integrado en Tkinter con canvas y toolbar.

Args:
    parent: El widget padre donde se creará el área de gráficas.

Returns:
    None

Raises:
    None

#### `_create_stats_area(self, parent)`

Crea el área de estadísticas en la ventana de historial.

Args:
    parent: El padre del frame de estadísticas.

Returns:
    None

Raises:
    None

#### `_create_buttons(self, parent)`

Crea los botones de acción en la ventana de historial.

Args:
    parent: El elemento padre donde se crearán los botones.

Returns:
    None

Raises:
    None

#### `_toggle_range_panel(self)`

Muestra u oculta la fila de OptionMenus de rango personalizado.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_entry_focus_in(self, entry: ctk.CTkEntry, var: ctk.StringVar)`

Establece el comportamiento al enfocar un campo de entrada de texto.

Args:
    entry (ctk.CTkEntry): El campo de entrada de texto que ha obtenido el foco.
    var (ctk.StringVar): La variable asociada al campo de entrada de texto.

#### `_entry_focus_out(self, entry: ctk.CTkEntry, var: ctk.StringVar)`

Restaura el texto de ejemplo en gris cuando un campo de entrada pierde el foco y queda vacío.

Args:
    entry (ctk.CTkEntry): El campo de entrada que perdió el foco.
    var (ctk.StringVar): La variable asociada al campo de entrada.

Returns:
    None

Raises:
    None

#### `_on_period_radio(self)`

Desactiva el modo de rango personalizado y actualiza la ventana de historial al seleccionar un período fijo.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `_apply_custom_range(self)`

Aplica un rango de fechas personalizado sin necesidad de interacción con el teclado.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update_data(self)`

Actualiza estadísticas y gráficas según el modo activo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_update_graphs(self, hours: int)`

Actualiza todas las gráficas de métricas para un período fijo en horas.

Args:
    hours (int): Período en horas para el cual se actualizarán las gráficas.

Returns:
    None

Raises:
    None

#### `_update_graphs_between(self, start: datetime, end: datetime)`

Actualiza todas las gráficas de métricas para un rango de fechas personalizado.

Args:
    start (datetime): Fecha de inicio del rango.
    end (datetime): Fecha de fin del rango.

Returns:
    None

Raises:
    None

#### `_draw_metric(self, ax, timestamps, values, ylabel: str, color: str)`

Dibuja una métrica específica en su eje subplot con estilo configurado.

Args:
    ax: Eje subplot donde se dibujará la métrica.
    timestamps: Fechas o timestamps de los datos a plotear.
    values: Valores de la métrica a plotear.
    ylabel: Etiqueta del eje Y.
    color: Color de la línea de la métrica.

Returns:
    None

Raises:
    Ninguna excepción relevante.

#### `_export_csv(self)`

Exporta los datos del período actual a archivo CSV en el directorio de exports.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Exception: Si ocurre un error durante la exportación.

#### `_clean_old_data(self)`

Fuerza un ciclo de limpieza completo de datos antiguos a través del servicio de limpieza.

Args: Ninguno

Returns: Ninguno

Raises: Exception si ocurre un error durante la limpieza.

#### `_export_figure_image(self)`

Exporta la figura actual de gráficas como imagen PNG al directorio de screenshots.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Exception: Si ocurre un error al guardar la imagen.

#### `_on_click(self, event)`

Maneja el evento de clic del mouse en el canvas de las gráficas.

Args:
    event: Evento de clic del mouse.

Raises:
    None

Returns:
    None

#### `_on_release(self, event)`

Maneja el evento de liberación del botón del mouse en el canvas.

Args:
    event: El evento de liberación del botón del mouse.

Returns:
    None

Raises:
    None

#### `_on_motion(self, event)`

Maneja el evento de movimiento del mouse sobre el canvas de gráficas.

Args:
    event: Evento de movimiento del mouse.

Returns:
    None

Raises:
    None

</details>
