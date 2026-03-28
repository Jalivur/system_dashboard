# `ui.windows.crontab_window`

> **Ruta**: `ui/windows/crontab_window.py`

> **Cobertura de documentación**: 🟢 100% (16/16)

Ventana de gestión de crontab.
Permite ver, añadir, editar y eliminar entradas del crontab
para el usuario actual (jalivur) o root.

---

## Tabla de contenidos

**Clase [`CrontabWindow`](#clase-crontabwindow)**

---

## Dependencias internas

- `config.settings`
- `core.crontab_service`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import custom_msgbox, confirm_dialog
from core.crontab_service import read_crontab, write_crontab, parse_crontab, build_line, describe_cron, QUICK_SCHEDULES
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `CrontabWindow(ctk.CTkToplevel)`

Ventana de gestión de crontab para visualizar, agregar, editar y eliminar entradas.

Args:
    parent: Widget padre que representa la ventana principal de la aplicación.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_user_var` | `ctk.StringVar(master=self, value=_SYSTEM_USER)` |
| `_lines` | `[]` |
| `_parsed` | `[]` |
| `_edit_index` | `None` |
| `_panel_open` | `False` |
| `_f_minute` | `ctk.StringVar(master=self, value='*')` |
| `_f_hour` | `ctk.StringVar(master=self, value='*')` |
| `_f_day` | `ctk.StringVar(master=self, value='*')` |
| `_f_month` | `ctk.StringVar(master=self, value='*')` |
| `_f_weekday` | `ctk.StringVar(master=self, value='*')` |
| `_f_command` | `ctk.StringVar(master=self, value='')` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent)`

Inicializa la ventana principal de gestión de crontab.

Configura la ventana toplevel, variables de estado, UI y carga las entradas iniciales.

Args:
    parent: Widget padre (ventana principal).

#### `_create_ui(self)`

Crea todos los elementos de la interfaz de usuario de la ventana.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_build_edit_panel(self, parent)`

Construye el panel deslizable de formulario para nueva/edición de entradas.

Args:
    parent: Frame contenedor del panel.

Returns:
    None

Raises:
    None

#### `_update_preview(self)`

Actualiza la etiqueta de previsualización de la programación cron en lenguaje natural.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_apply_quick(self, m, h, d, mo, wd)`

Aplica una programación cron de acceso rápido a los campos del formulario.

Args:
    m (str): Valor para minuto, o '@' para un valor especial.
    h (str): Valor para hora.
    d (str): Valor para día-mes.
    mo (str): Valor para mes.
    wd (str): Valor para día-semana.

Returns:
    None

Raises:
    None

#### `_open_new_form(self)`

Abre el panel para crear una nueva entrada en la Crontab.

Args:
    None

Returns:
    None

Raises:
    None

#### `_open_edit_form(self, index: int)`

Abre el panel para editar una entrada existente en la Crontab.

Carga los datos de la entrada seleccionada en los campos del formulario.

Args:
    index (int): Índice de la entrada a editar.

Raises:
    Ninguna excepción específica.

#### `_close_form(self)`

Cierra el panel de formulario y resetea el estado de edición.

Args:
    None

Returns:
    None

Raises:
    None

#### `_save_entry(self)`

Guarda la entrada de un formulario de Crontab después de validación.

    Args:
        Ninguno

    Returns:
        Ninguno

    Raises:
        Ninguno

#### `_delete_entry(self, index: int)`

Inicia proceso de eliminación de entrada con confirmación de diálogo.

    Args:
        index (int): Índice en self._parsed de la entrada a eliminar.

    Raises:
        None

#### `_load(self)`

Carga las entradas del crontab del usuario actual en la ventana.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_render_list(self)`

Limpia el frame de lista y renderiza todas las entradas parseadas del crontab.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_create_entry_row(self, index: int, entry: dict)`

Crea y configura una fila de entrada en la lista para mostrar información de una tarea programada.

Args:
    index (int): Índice de la entrada.
    entry (dict): Diccionario parseado de la entrada cron.

Returns:
    None

Raises:
    None

#### `_on_user_change(self)`

Callback invocado al cambiar el usuario seleccionado.

Cierra formulario abierto y recarga la lista para el nuevo usuario.

Args:
    None

Returns:
    None

Raises:
    None

</details>
