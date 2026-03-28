# `ui.styles`

> **Ruta**: `ui/styles.py`

> **Cobertura de documentación**: 🟢 100% (17/17)

Estilos y temas para la interfaz

---

## Tabla de contenidos

**Funciones**
- [`make_futuristic_button()`](#funcion-make_futuristic_button)
- [`make_window_header()`](#funcion-make_window_header)
- [`make_homebridge_switch()`](#funcion-make_homebridge_switch)

**Clase [`StyleManager`](#clase-stylemanager)**
  - [`style_radiobutton_tk()`](#style_radiobutton_tkrb-tkradiobutton-fg-str-none-bg-str-none-hover_fg-str-none-none)
  - [`style_radiobutton_ctk()`](#style_radiobutton_ctkrb-ctkctkradiobutton-radiobutton_width-int-25-radiobutton_height-int-25-none)
  - [`style_slider()`](#style_sliderslider-tkscale-color-str-none-none)
  - [`style_slider_ctk()`](#style_slider_ctkslider-ctkctkslider-color-str-none-height-30-none)
  - [`style_scrollbar()`](#style_scrollbarsb-tkscrollbar-color-str-none-none)
  - [`style_scrollbar_ctk()`](#style_scrollbar_ctksb-ctkctkscrollbar-color-str-none-none)
  - [`style_ctk_scrollbar()`](#style_ctk_scrollbarscrollable_frame-ctkctkscrollableframe-color-str-none-none)
  - [`show_service_stopped_banner()`](#show_service_stopped_bannerparent_frame-service_name-str-none)

---

## Dependencias internas

- `config.settings`

## Imports

```python
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, Icons
```

## Funciones

### `make_futuristic_button(parent, text: str, command = None, width: int = None, height: int = None, font_size: int = None, state: str = 'normal') -> ctk.CTkButton`

Crea un botón con estilo futurista.

Args:
    parent: Widget padre.
    text (str): Texto del botón.
    command: Función a ejecutar al hacer clic.
    width (int): Ancho en unidades. Por defecto None.
    height (int): Alto en unidades. Por defecto None.
    font_size (int): Tamaño de fuente. Por defecto None.
    state (str): Estado del botón. Por defecto 'normal'.

Returns:
    ctk.CTkButton: Widget CTkButton configurado.

Raises:
    Ninguna excepción específica.

### `make_window_header(parent, title: str, on_close, status_text: str = None) -> ctk.CTkFrame`

Crea una barra de cabecera unificada para ventanas de monitoreo.

    Args:
        parent:      Widget padre (normalmente el frame main de la ventana).
        title:       Texto del título en mayúsculas.
        on_close:    Callable ejecutado al pulsar el botón de cierre.
        status_text: Texto informativo opcional a la derecha del título.

    Returns:
        CTkFrame de cabecera ya empaquetado con pack(fill="x").

    Raises:
        Ninguno.

### `make_homebridge_switch(parent, text: str, command = None, is_on: bool = False, disabled: bool = False) -> ctk.CTkSwitch`

Crea un CTkSwitch estilado para el control de accesorios Homebridge.

Args:
    parent:   Widget padre (normalmente la tarjeta CTkFrame).
    text:     Etiqueta del switch (nombre del dispositivo).
    command:  Callable ejecutado al cambiar el estado.
              Recibe el nuevo valor como booleano (True=ON, False=OFF).
    is_on:    Estado inicial del switch.
    disabled: Si True, el switch se muestra bloqueado en rojo (fallo/inactivo).

Returns:
    CTkSwitch configurado y listo para empaquetar.

## Clase `StyleManager`

Establece el estilo para un radiobutton de tkinter.

Args:
    rb (tk.Radiobutton): Widget radiobutton a estilizar.
    fg (str, opcional): Color de texto. Por defecto, COLORS['primary'].
    bg (str, opcional): Color de fondo. Por defecto, COLORS['bg_dark'].
    hover_fg (str, opcional): Color de texto al pasar el mouse. Por defecto, COLORS['success'].

Returns:
    None

### Métodos públicos

#### `style_radiobutton_tk(rb: tk.Radiobutton, fg: str = None, bg: str = None, hover_fg: str = None) -> None`

Aplica estilo personalizado a un widget Radiobutton de tkinter.

Args:
    rb (tk.Radiobutton): El widget Radiobutton a estilizar.
    fg (str, opcional): Color del texto. Por defecto, None.
    bg (str, opcional): Color de fondo. Por defecto, None.
    hover_fg (str, opcional): Color del texto al pasar el mouse. Por defecto, None.

Returns:
    None

Raises:
    None

#### `style_radiobutton_ctk(rb: ctk.CTkRadioButton, radiobutton_width: int = 25, radiobutton_height: int = 25) -> None`

Aplica estilo personalizado a un widget CTkRadioButton de customtkinter.

Args:
    rb (ctk.CTkRadioButton): El widget radiobutton a estilizar.
    radiobutton_width (int): Ancho del radiobutton. Por defecto 25.
    radiobutton_height (int): Alto del radiobutton. Por defecto 25.

Returns:
    None

#### `style_slider(slider: tk.Scale, color: str = None) -> None`

Aplica estilo personalizado a un widget slider de tkinter.

Args:
    slider (tk.Scale): El widget slider a estilizar.
    color (str, opcional): Color personalizado para el slider. Por defecto es None.

Returns:
    None

Raises:
    None

#### `style_slider_ctk(slider: ctk.CTkSlider, color: str = None, height = 30) -> None`

Aplica estilo personalizado a un widget CTkSlider de customtkinter.

Args:
    slider (ctk.CTkSlider): El widget slider a personalizar.
    color (str, opcional): Color personalizado para el slider. Por defecto, None.
    height (int, opcional): Altura del slider. Por defecto, 30.

Returns:
    None

Raises:
    Ninguna excepción específica.

#### `style_scrollbar(sb: tk.Scrollbar, color: str = None) -> None`

Aplica estilo personalizado a un widget Scrollbar de tkinter.

Args:
    sb (tk.Scrollbar): El widget Scrollbar a estilizar.
    color (str, opcional): Color personalizado para el scrollbar. Por defecto, None.

Returns:
    None

Raises:
    Ninguna excepción específica.

#### `style_scrollbar_ctk(sb: ctk.CTkScrollbar, color: str = None) -> None`

Aplica estilo personalizado a un scrollbar de customtkinter.

Args:
    sb (ctk.CTkScrollbar): Widget scrollbar a personalizar.
    color (str, opcional): Color personalizado para el scrollbar. Por defecto, usa el color primario del tema.

Returns:
    None

Raises:
    Ninguna excepción específica.

#### `style_ctk_scrollbar(scrollable_frame: ctk.CTkScrollableFrame, color: str = None) -> None`

Aplica estilo personalizado al scrollbar de un CTkScrollableFrame de customtkinter.

Args:
    scrollable_frame (ctk.CTkScrollableFrame): El widget CTkScrollableFrame a estilizar.
    color (str, opcional): Color personalizado para los botones del scrollbar. Por defecto, None.

Returns:
    None

Raises:
    Ninguna excepción específica.

#### `show_service_stopped_banner(parent_frame, service_name: str) -> None`

Muestra un banner indicando que un servicio ha detenido su ejecución.

Args:
    parent_frame: La ventana padre donde se mostrará el banner.
    service_name (str): El nombre del servicio que ha detenido su ejecución.

Returns:
    None

Raises:
    None
