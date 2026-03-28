# `ui.windows.config_editor_window`

> **Ruta**: `ui/windows/config_editor_window.py`

> **Cobertura de documentación**: 🟢 100% (21/21)

Ventana de edición de configuración local.
Lee los valores actuales en memoria y permite modificarlos.
Al guardar escribe config/local_settings.py con solo los valores
que difieran de los defaults — nunca toca settings.py.
Incluye botón "Guardar y reiniciar" para aplicar cambios.

Iconos: se leen automáticamente desde Icons.__dict__ — no requiere
mantenimiento manual al añadir iconos nuevos a settings.py.

Carga diferida: las filas de iconos se construyen en lotes con after()
para no bloquear el hilo principal al abrir la ventana.

---

## Tabla de contenidos

**Clase [`ConfigEditorWindow`](#clase-configeditorwindow)**

---

## Dependencias internas

- `config.local_settings_io`
- `config.settings`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

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

Recupera la lista de iconos editables en tiempo de ejecución.

Args: Ninguno

Returns:
    list: Tuplas ordenadas con nombres y valores de iconos.

Raises: Ninguno

### `_surrogate_to_cp(high: int, low: int) -> int`

Convierte un par de surrogates UTF-16 a un codepoint Unicode escalar.

Args:
    high: El primer surrogate (0xD800-0xDBFF).
    low: El segundo surrogate (0xDC00-0xDFFF).

Returns:
    El codepoint entero correspondiente (U+10000 a U+10FFFF).

### `_parse_codepoint(raw: str)`

Parsea una representación de un codepoint Unicode en formato hexadecimal.

Args:
    raw (str): Cadena que representa el codepoint Unicode.

Returns:
    tuple: Un par (int, str) con el codepoint como entero y su representación como escape Unicode.

Raises:
    ValueError: Si la entrada es vacía, el valor hexadecimal no es válido o el formato no es reconocido.

### `_load_local_settings() -> tuple`

Carga la configuración local del sistema.

Args:
    Ninguno

Returns:
    tuple: La configuración local cargada.

Raises:
    Ninguna excepción específica.

### `_write_local_settings(param_overrides: dict, icon_overrides: dict)`

Escribe las configuraciones locales sobrescritas en el archivo de settings.

Args:
    param_overrides (dict): Diccionario con parámetros sobrescritos.
    icon_overrides (dict): Diccionario con iconos sobrescritos.

Returns:
    None

Raises:
    None

</details>

## Clase `ConfigEditorWindow(ctk.CTkToplevel)`

Ventana emergente para editar la configuración local del dashboard.

Args:
    parent: Ventana principal (CTk) para modalidad transient.

Raises:
    None

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

Returns:
    None

Raises:
    None

#### `_create_ui(self)`

Crea y configura la interfaz de usuario de la ventana de edición de configuración.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_build_section(self, parent, section: dict)`

Construye una sección de parámetros con su tarjeta visual y filas de entrada.

Args:
    parent: Contenedor padre para la sección.
    section (dict): Diccionario con 'title', 'color' y lista de 'params'.

Returns:
    None

Raises:
    None

#### `_build_param_row(self, parent, key, label, typ, vmin, vmax, step, desc)`

Crea una fila editable para un parámetro numérico con botones +/- y descripción.

Args:
    parent: Frame contenedor de la fila.
    key: Clave del parámetro en settings.
    label: Etiqueta visible.
    typ: Tipo de parámetro, 'int' o 'float'.
    vmin, vmax, step: Límites y paso del parámetro.
    desc: Descripción tooltip del parámetro.

Returns:
    None

Raises:
    None

#### `_build_icons_header(self, parent)`

Construye la cabecera de la sección de iconos con instrucciones y loader.

Args:
    parent: Contenedor padre.

Returns:
    Tuple (card_frame, loading_label).

#### `_build_icon_batch(self)`

Construye lotes de filas de iconos de forma asíncrona para evitar bloqueo UI.

Args:
    None

Returns:
    None

Raises:
    None

#### `_build_icon_row(self, parent, attr: str, current_char: str)`

Crea una fila editable para un icono específico con preview y entry codepoint.

Args:
    parent: Frame contenedor.
    attr (str): Nombre del atributo Icons (ej. 'HOME').
    current_char (str): Carácter Unicode actual.

Returns:
    None

Raises:
    None

#### `_step_value(self, key, typ, delta, vmin, vmax)`

Ajusta el valor de un parámetro numérico con botones +/-, respetando límites.

Args:
    key (str): Clave del parámetro.
    typ (str): Tipo del parámetro, 'int' o 'float'.
    delta (int o float): Incremento/decremento del valor.
    vmin (int o float, opcional): Límite mínimo del valor. 
    vmax (int o float, opcional): Límite máximo del valor.

Raises:
    ValueError: Si el valor actual no se puede convertir a número.

#### `_update_icon_preview(self, attr: str, var: ctk.StringVar, preview: ctk.CTkLabel)`

Actualiza la previsualización del icono en tiempo real al editar el codepoint.

Args:
    attr (str): Nombre del icono.
    var (ctk.StringVar): StringVar con el input raw.
    preview (ctk.CTkLabel): Label para mostrar el carácter.

Returns:
    None

Raises:
    ValueError: Si el codepoint ingresado no es válido.

#### `_collect(self)`

Recopila y valida los valores editados en la ventana de configuración.

Args:
    Ninguno

Returns:
    Tupla conteniendo: 
        - param_overrides (dict): Diccionario con parámetros sobrescritos.
        - icon_overrides (dict): Diccionario vacío (icono no utilizado).
        - errors (list): Lista de errores de validación.

Raises:
    Ninguno

#### `_save(self)`

Guarda los cambios validados en local_settings.py y muestra confirmación sin reiniciar la aplicación.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Exception: Si ocurre un error al guardar los cambios.

#### `_save_and_restart(self)`

Guarda cambios de configuración y reinicia el dashboard completo después de confirmación del usuario.

Args: Ninguno

Returns: Ninguno

Raises: Excepciones internas durante el proceso de guardado y reinicio.

#### `_restore_defaults(self)`

Restaura todos los campos a valores predeterminados y elimina el archivo local_settings.py.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

</details>
