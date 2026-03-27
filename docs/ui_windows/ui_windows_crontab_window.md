# `ui.windows.crontab_window`

> **Ruta**: `ui/windows/crontab_window.py`

Ventana de gestión de crontab.
Permite ver, añadir, editar y eliminar entradas del crontab
para el usuario actual (jalivur) o root.

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

Ventana de gestión de crontab — ver, añadir, editar y eliminar.

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

#### `_build_edit_panel(self, parent)`

Construye el panel deslizable de formulario para nueva/edición de entradas.

Args:
    parent: Frame contenedor del panel.

#### `_update_preview(self)`

Actualiza la etiqueta de previsualización de la programación cron en lenguaje natural.

#### `_apply_quick(self, m, h, d, mo, wd)`

Aplica una programación cron de acceso rápido a los campos del formulario.

Args:
    m, h, d, mo, wd: Valores para minuto, hora, día-mes, mes, día-semana (o '@' especial).

#### `_open_new_form(self)`

Abre el panel para crear nueva entrada.

Resetea campos del formulario y muestra/oculta panel.

#### `_open_edit_form(self, index: int)`

Abre el panel para editar entrada existente.

Carga datos del índice en campos.

Args:
    index (int): Índice de entrada a editar.

#### `_close_form(self)`

Cierra el panel de formulario y resetea estado de edición.

#### `_save_entry(self)`

Valida los campos del formulario y guarda la entrada (nueva o edición).

Construye la línea cron, actualiza self._lines y escribe al crontab del usuario.

#### `_delete_entry(self, index: int)`

Inicia proceso de eliminación de entrada con confirmación de diálogo.

Actualiza self._lines y escribe al crontab.

Args:
    index: Índice en self._parsed de la entrada a eliminar.

#### `_load(self)`

Carga las entradas del crontab del usuario actual en self._lines y self._parsed.

Invoca _render_list() para actualizar la vista.

#### `_render_list(self)`

Limpia el frame de lista y renderiza todas las entradas parseadas.

Muestra mensaje si no hay entradas.

#### `_create_entry_row(self, index: int, entry: dict)`

Crea y configura una fila de entrada en la lista.

Args:
    index: Índice de la entrada.
    entry: Diccionario parseado de la entrada cron.

#### `_on_user_change(self)`

Callback invocado al cambiar el usuario seleccionado.

Cierra formulario abierto y recarga la lista para el nuevo usuario.

</details>
