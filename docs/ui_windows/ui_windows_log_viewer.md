# `ui.windows.log_viewer`

> **Ruta**: `ui/windows/log_viewer.py`

> **Cobertura de documentación**: 🟢 100% (19/19)

Ventana de visualización del log del dashboard.
Permite filtrar por nivel, módulo, texto libre e intervalo de tiempo
y exportar el resultado filtrado a un archivo .log

---

## Tabla de contenidos

**Clase [`LogViewerWindow`](#clase-logviewerwindow)**

---

## Dependencias internas

- `config.settings`
- `core.cleanup_service`
- `ui.styles`
- `ui.widgets.dialogs`
- `utils.logger`

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

Args:
    parent: Ventana padre de la aplicación.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno.

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

Configura la geometría, variables de estado y filtros, UI, y carga inicial de logs.

Args:
    parent: La ventana padre.

Raises:
    Ninguna excepción específica.

Returns:
    Ninguno

#### `_entry_focus_in(self, entry, var, placeholder)`

Limpia el texto placeholder de un campo de texto cuando recibe el foco.

    Args:
        entry: Widget CTkEntry que recibió el foco.
        var: Variable StringVar asociada al campo de texto.
        placeholder: Texto placeholder a limpiar.

    Returns:
        None

#### `_entry_focus_out(self, entry, var, placeholder)`

Restaura el texto placeholder en un campo de texto cuando pierde el foco.

Args:
    entry: Widget CTkEntry que ha perdido el foco.
    var: Variable StringVar asociada al campo de texto.
    placeholder: Texto placeholder a restaurar cuando el campo está vacío.

Returns:
    None

Raises:
    None

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

Construye la interfaz de usuario completa del visor de logs.

Crea el frame principal, header, panel de filtros, área de resultados 
y barra inferior de controles.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_filters(self, parent)`

Crea el panel de filtros avanzados para la ventana de visualización de registros.

Args:
    parent: Frame contenedor donde se ubicará el panel de filtros.

#### `_create_results(self, parent)`

Crea el área de visualización de resultados con textbox coloreado.

Configura tags de color por nivel de log y estilos de scrollbars.

Args:
    parent: Frame contenedor.

Raises:
    None

#### `_create_bottom_bar(self, parent)`

Crea la barra inferior con controles de contador, exportar y recargar.

Args:
    parent: Frame contenedor.

Returns:
    None

Raises:
    None

#### `_load_log(self)`

Inicia la carga asíncrona de logs desde archivo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_read_log_thread(self)`

Hilo secundario para lectura y parseo de logs.

Lee logs principales y rotados, parsea líneas con regex y actualiza 
módulos/lista de líneas en un entorno thread-safe.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Exception: Si ocurre un error al leer o parsear el log.

#### `_parse_line(self, raw)`

Parsea una línea de log cruda usando regex, extrayendo timestamp, nivel, módulo y mensaje, y validando la fecha.

Args:
    raw (str): Línea de log como string.

Returns:
    dict o None: Estructura parseada con ts, ts_str, level, module, message y raw, o None si no coincide patrón.

Raises:
    None

#### `_update_modules(self, modules)`

Actualiza la lista de módulos únicos detectados en logs.

Args:
    modules: Lista ordenada de nombres de módulos.

Returns:
    None

Raises:
    None

#### `_on_quick_interval(self, value)`

Configura intervalos de tiempo rápidos automáticamente.

Actualiza campos fecha/hora basados en selección y aplica filtros inmediatamente.

Args:
    value (str): Opción seleccionada (ej: '15min', '1h', '6h', '24h', 'Todo').

Raises:
    Ninguna excepción específica.

#### `_apply_filters(self)`

Aplica todos los filtros activos y actualiza la visualización.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_parse_datetime(self, date_str, time_str, is_end)`

Convierte strings de fecha/hora a objeto datetime.

Aplica defaults (00:00 inicio, 23:59 fin) si faltan hora.

Args:
    date_str (str): Fecha en formato YYYY-MM-DD.
    time_str (str): Hora en formato HH:MM.
    is_end (bool): True para usar 23:59 si falta hora.

Returns:
    datetime o None: Objeto parseado o None si inválido.

#### `_set_text(self, loading_msg, lines)`

Renderiza logs filtrados o mensaje de carga en textbox.

Aplica tags de color por nivel y posiciona scroll al final.

Args:
    loading_msg (str o None): Mensaje de carga o None.
    lines (lista de dicts): Lista de dicts parseados de logs.

Returns:
    None

Raises:
    Ninguna excepción.

#### `_export(self)`

Exporta logs filtrados a archivo .log con timestamp único.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
