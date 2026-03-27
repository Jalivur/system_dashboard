# `ui.windows.config_editor_window`

> **Ruta**: `ui/windows/config_editor_window.py`

Ventana de edición de configuración local.
Lee los valores actuales en memoria y permite modificarlos.
Al guardar escribe config/local_settings.py con solo los valores
que difieran de los defaults — nunca toca settings.py.
Incluye botón "Guardar y reiniciar" para aplicar cambios.

Iconos: se leen automáticamente desde Icons.__dict__ — no requiere
mantenimiento manual al añadir iconos nuevos a settings.py.

Carga diferida: las filas de iconos se construyen en lotes con after()
para no bloquear el hilo principal al abrir la ventana.

## Imports

```python
import os
import sys
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
import config.settings as _settings
from config.local_settings_io import read as _ls_read, write as _ls_write
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import confirm_dialog, custom_msgbox
from utils.logger import get_logger
from config.local_settings_io import _PATH
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

<details>
<summary>Funciones privadas</summary>

### `_get_editable_icons() -> list`

Lee Icons.__dict__ en tiempo de ejecución.
Automático — cualquier icono nuevo en settings.py aparece aquí sin
tocar este fichero.

### `_surrogate_to_cp(high: int, low: int) -> int`

Convierte par de surrogates UTF-16 high/low a codepoint Unicode scalar.

Args:
    high: Primer surrogate (0xD800-0xDBFF).
    low: Segundo surrogate (0xDC00-0xDFFF).

Returns:
    Codepoint int (U+10000 a U+10FFFF).

### `_parse_codepoint(raw: str)`

Acepta: \udb81\udda9 | \U000F06A9 | F06A9 | 0xF06A9
Devuelve (int codepoint, str escape) o raise ValueError.

### `_load_local_settings() -> tuple`

Delega en local_settings_io.read() — fuente única de verdad.

### `_write_local_settings(param_overrides: dict, icon_overrides: dict)`

Delega en local_settings_io.write() — fuente única de verdad.

</details>

## Clase `ConfigEditorWindow(ctk.CTkToplevel)`

Editor de configuración local del dashboard.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_editable_icons` | `_get_editable_icons()` |
| `_icon_build_idx` | `0` |
| `_icon_card` | `None` |
| `_icon_loading_lbl` | `None` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent)`

Inicializa la ventana editor de configuración.

Args:
    parent: Ventana principal (CTk) para modalidad transient.

#### `_create_ui(self)`

Crea y configura toda la interfaz de usuario de la ventana.
Incluye header, secciones de parámetros, iconos y botones de acción.

#### `_build_section(self, parent, section: dict)`

Construye una sección de parámetros con su tarjeta visual y filas de entrada.

Args:
    parent: Contenedor padre para la sección.
    section: Diccionario con 'title', 'color' y lista de 'params'.

#### `_build_param_row(self, parent, key, label, typ, vmin, vmax, step, desc)`

Crea una fila editable para un parámetro numérico con botones +/- y descripción.

Args:
    parent: Frame contenedor de la fila.
    key: Clave del parámetro en settings.
    label: Etiqueta visible.
    typ: 'int' o 'float'.
    vmin, vmax, step: Límites y paso.
    desc: Descripción tooltip.

#### `_build_icons_header(self, parent)`

Construye la cabecera de la sección de iconos con instrucciones y loader.

Args:
    parent: Contenedor padre.

Returns:
    Tuple (card_frame, loading_label).

#### `_build_icon_batch(self)`

Construye lotes de filas de iconos de forma asíncrona (after()) para evitar bloqueo UI.
Llama recursivamente hasta completar todos los iconos editables.

#### `_build_icon_row(self, parent, attr: str, current_char: str)`

Crea una fila editable para un icono específico con preview y entry codepoint.

Args:
    parent: Frame contenedor.
    attr: Nombre del atributo Icons (ej. 'HOME').
    current_char: Carácter Unicode actual.

#### `_step_value(self, key, typ, delta, vmin, vmax)`

Ajusta el valor de un parámetro numérico con botones +/-, respetando límites.

Args:
    key: Clave del parámetro.
    typ: 'int' o 'float'.
    delta: Incremento/decremento.
    vmin, vmax: Límites opcionales.

#### `_update_icon_preview(self, attr: str, var: ctk.StringVar, preview: ctk.CTkLabel)`

Actualiza la previsualización del icono en tiempo real al editar el codepoint.
Muestra verde si válido, rojo con cruz si inválido.

Args:
    attr: Nombre del icono.
    var: StringVar con el input raw.
    preview: Label para mostrar el carácter.

#### `_collect(self)`

Recopila todos los valores editados, valida rangos/formato y filtra solo overrides vs defaults.

Returns:
    Tuple (param_overrides: dict, icon_overrides: dict, errors: list).

#### `_save(self)`

Guarda los cambios validados en local_settings.py y muestra confirmación.
No reinicia la aplicación.

#### `_save_and_restart(self)`

Guarda cambios y reinicia el dashboard completo vía os.execv.
Requiere confirmación del usuario.

#### `_restore_defaults(self)`

Restaura todos los campos a valores default y elimina local_settings.py.
Requiere confirmación y reinicio manual.

</details>
