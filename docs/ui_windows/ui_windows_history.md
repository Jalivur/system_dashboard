# `ui.windows.history`

> **Ruta**: `ui/windows/history.py`

Ventana de histórico de datos

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

Ventana de visualización de histórico

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

#### `_create_ui(self)`

Crea la interfaz de usuario completa de la ventana, incluyendo frames, canvas y widgets principales.

#### `_create_period_controls(self, parent)`

Fila 1: radio buttons 24h/7d/30d + botón para abrir/cerrar el panel de rango.

#### `_create_range_panel(self, parent)`

Fila 2 (oculta por defecto): selectores día/mes/año/hora/min
para inicio y fin del rango. Sin teclado — todo por OptionMenu.

#### `_create_graphs_area(self, parent)`

Crea el área de gráficas utilizando matplotlib integrado en Tkinter con canvas y toolbar.

#### `_create_stats_area(self, parent)`

Crea el frame y label para mostrar las estadísticas calculadas de los datos.

#### `_create_buttons(self, parent)`

Crea los botones de acción: actualizar datos, exportar CSV y limpiar archivos antiguos.

#### `_toggle_range_panel(self)`

Muestra u oculta la fila de OptionMenus de rango personalizado.

#### `_entry_focus_in(self, entry: ctk.CTkEntry, var: ctk.StringVar)`

Al enfocar: si tiene el texto de ejemplo, lo borra y pone color normal.

#### `_entry_focus_out(self, entry: ctk.CTkEntry, var: ctk.StringVar)`

Al perder foco: si quedó vacío, restaura el texto de ejemplo en gris.

#### `_on_period_radio(self)`

Al pulsar radio button fijo: desactiva modo custom y actualiza.

#### `_apply_custom_range(self)`

Lee los OptionMenus y aplica el rango sin necesidad de teclado.

#### `_update_data(self)`

Actualiza estadísticas y gráficas según el modo activo.

#### `_update_graphs(self, hours: int)`

Actualiza todas las gráficas de métricas para un período fijo en horas.

#### `_update_graphs_between(self, start: datetime, end: datetime)`

Actualiza todas las gráficas de métricas para un rango de fechas personalizado.

#### `_draw_metric(self, ax, timestamps, values, ylabel: str, color: str)`

Dibuja una métrica específica en su eje subplot: configura estilo, grid y plotea datos.

#### `_export_csv(self)`

Exporta los datos del período actual (fijo o custom) a archivo CSV en el directorio de exports.

#### `_clean_old_data(self)`

Fuerza un ciclo de limpieza completo a través de CleanupService.

#### `_export_figure_image(self)`

Exporta la figura actual de gráficas como imagen PNG al directorio de screenshots.

#### `_on_click(self, event)`

Maneja el evento de clic del mouse en el canvas de las gráficas.

#### `_on_release(self, event)`

Maneja el evento de liberación del botón del mouse en el canvas.

#### `_on_motion(self, event)`

Maneja el evento de movimiento del mouse sobre el canvas de gráficas.

</details>
