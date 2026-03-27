# `ui.windows.log_viewer`

> **Ruta**: `ui/windows/log_viewer.py`

Ventana de visualización del log del dashboard.
Permite filtrar por nivel, módulo, texto libre e intervalo de tiempo
y exportar el resultado filtrado a un archivo .log

## Imports

```python
import re
import threading
from datetime import datetime, timedelta
from pathlib import Path
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, DATA_DIR, EXPORTS_LOG_DIR
from ui.styles import make_window_header, make_futuristic_button, StyleManager
from ui.widgets.dialogs import custom_msgbox
from utils.logger import get_logger
from core.cleanup_service import CleanupService
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `LOG_FILE` | `DATA_DIR / 'logs' / 'dashboard.log'` |
| `LOG_LEVELS` | `['TODOS', 'DEBUG', 'INFO', 'WARNING', 'ERROR']` |
| `LEVEL_COLORS` | `{'DEBUG': '#888888', 'INFO': '#00BFFF', 'WARNING': '#FFA500', 'ERROR': '#FF4444'...` |
| `LOG_PATTERN` | `re.compile('^(\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})\\s+\\[(\\w+)\\]\\s+Dash...` |

## Clase `LogViewerWindow(ctk.CTkToplevel)`

Ventana principal para visualización y filtrado de logs del dashboard.

Proporciona interfaz gráfica con filtros avanzados por nivel de log, módulo,
texto de búsqueda e intervalo de tiempo. Soporta recarga automática, resaltado
por colores según severidad y exportación de resultados filtrados a archivo .log.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_cleanup_service` | `CleanupService()` |
| `_loading` | `False` |
| `_level_var` | `ctk.StringVar(master=self, value='TODOS')` |
| `_module_var` | `ctk.StringVar(master=self, value=_PH_MODULE)` |
| `_search_var` | `ctk.StringVar(master=self, value=_PH_SEARCH)` |
| `_quick_var` | `ctk.StringVar(master=self, value='1h')` |
| `_date_from` | `ctk.StringVar(master=self, value=_PH_DATE)` |
| `_time_from` | `ctk.StringVar(master=self, value=_PH_TIME)` |
| `_date_to` | `ctk.StringVar(master=self, value=_PH_DATE)` |
| `_time_to` | `ctk.StringVar(master=self, value=_PH_TIME)` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent)`

Inicializa la ventana del visor de logs.

Configura geometría, variables de estado/filtros, UI y carga inicial de logs.
Registra la apertura en el logger.

#### `_entry_focus_in(self, entry, var, placeholder)`

Maneja el evento de entrada de foco en campo de texto.

Limpia el placeholder si está presente y ajusta el color del texto.

Args:
    entry: Widget CTkEntry.
    var: Variable StringVar asociada.
    placeholder: Texto placeholder a limpiar.

#### `_entry_focus_out(self, entry, var, placeholder)`

Maneja el evento de salida de foco en campo de texto.

Restaura placeholder si el campo está vacío y ajusta color del texto.

Args:
    entry: Widget CTkEntry.
    var: Variable StringVar asociada.
    placeholder: Texto placeholder a restaurar.

#### `_entry_value(self, var, placeholder)`

Obtiene el valor real del campo de entrada, ignorando placeholder.

Args:
    var: Variable StringVar del campo.
    placeholder: Texto placeholder de referencia.

Returns:
    str: Valor limpio o cadena vacía si solo tenía placeholder.

#### `_make_entry(self, parent, var, placeholder, width)`

Crea un CTkEntry con manejo automático de placeholders y bindings.

Args:
    parent: Contenedor padre.
    var: Variable StringVar.
    placeholder: Texto placeholder inicial.
    width: Ancho del entry en píxeles.

Returns:
    CTkEntry: Instancia configurada con eventos de foco.

#### `_create_ui(self)`

Construye la interfaz de usuario completa.

Crea frame principal, header, panel de filtros, área de resultados
y barra inferior de controles.

#### `_create_filters(self, parent)`

Crea el panel de filtros avanzados.

Incluye selección de nivel, filtro por módulo, búsqueda libre,
intervalos rápidos/manuales y botón 'Aplicar'.

Args:
    parent: Frame contenedor.

#### `_create_results(self, parent)`

Crea el área de visualización de resultados con textbox coloreado.

Configura tags de color por nivel de log y estilos de scrollbars.

Args:
    parent: Frame contenedor.

#### `_create_bottom_bar(self, parent)`

Crea la barra inferior con controles de contador, exportar y recargar.

Args:
    parent: Frame contenedor.

#### `_load_log(self)`

Inicia la carga asíncrona de logs desde archivo.

Previene cargas concurrentes y muestra mensaje de carga en UI.

#### `_read_log_thread(self)`

Hilo secundario para lectura y parseo de logs.

Lee logs principales y rotados (.1), parsea líneas con regex y
actualiza módulos/lista de líneas en thread-safe manner.

#### `_parse_line(self, raw)`

Parsea una línea de log cruda usando regex.

Extrae timestamp, nivel, módulo y mensaje. Valida fecha.

Args:
    raw: Línea de log como string.

Returns:
    dict o None: Estructura parseada o None si no coincide patrón.

#### `_update_modules(self, modules)`

Actualiza la lista de módulos únicos detectados en logs.

Args:
    modules: Lista ordenada de nombres de módulos.

#### `_on_quick_interval(self, value)`

Configura intervalos de tiempo rápidos automáticamente.

Actualiza campos fecha/hora basados en selección (15min,1h,etc.)
y aplica filtros inmediatamente.

Args:
    value: Opción seleccionada (ej: '1h').

#### `_apply_filters(self)`

Aplica todos los filtros activos y actualiza la visualización.

Filtra por nivel, módulo, búsqueda y rango temporal. Actualiza
contador de entradas y renderiza resultados coloreados.

#### `_parse_datetime(self, date_str, time_str, is_end)`

Convierte strings de fecha/hora a objeto datetime.

Aplica defaults (00:00 inicio, 23:59 fin) si faltan hora.

Args:
    date_str: Fecha en formato YYYY-MM-DD.
    time_str: Hora en formato HH:MM.
    is_end: True para usar 23:59 si falta hora.

Returns:
    datetime o None: Objeto parseado o None si inválido.

#### `_set_text(self, loading_msg, lines)`

Renderiza logs filtrados o mensaje de carga en textbox.

Aplica tags de color por nivel y posiciona scroll al final.

Args:
    loading_msg: Mensaje de carga (str) o None.
    lines: Lista de dicts parseados de logs.

#### `_export(self)`

Exporta logs filtrados a archivo .log con timestamp único.

Aplica filtros actuales, genera ruta en EXPORTS_LOG_DIR y ejecuta
limpieza automática de exports antiguos via CleanupService.

</details>
