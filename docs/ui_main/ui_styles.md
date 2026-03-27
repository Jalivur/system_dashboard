# `ui.styles`

> **Ruta**: `ui/styles.py`

Estilos y temas para la interfaz

## Imports

```python
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, Icons
```

## Funciones

### `make_futuristic_button(parent, text: str, command = None, width: int = None, height: int = None, font_size: int = None, state: str = 'normal') -> ctk.CTkButton`

Crea un botón con estilo futurista

Args:
    parent: Widget padre
    text: Texto del botón
    command: Función a ejecutar al hacer clic
    width: Ancho en unidades
    height: Alto en unidades
    font_size: Tamaño de fuente

Returns:
    Widget CTkButton configurado

### `make_window_header(parent, title: str, on_close, status_text: str = None) -> ctk.CTkFrame`

Crea una barra de cabecera unificada para ventanas de monitoreo.

Layout (altura fija 48px):
┌─────────────────────────────────────────────────────────┐
│  ● TÍTULO DE VENTANA      status_text opcional   [" + Icons.CLOSE_X + "]   │
└─────────────────────────────────────────────────────────┘

El indicador ● usa COLORS['secondary'] para identificar
visualmente que es una ventana hija del dashboard.

Args:
    parent:      Widget padre (normalmente el frame main de la ventana).
    title:       Texto del título en mayúsculas (ej. "MONITOR DEL SISTEMA").
    on_close:    Callable ejecutado al pulsar el botón " + Icons.CLOSE_X + ".
    status_text: Texto informativo opcional a la derecha del título
                 (ej. "CPU 12% · RAM 45% · 52°C"). Si es None no se muestra.

Returns:
    CTkFrame de cabecera ya empaquetado con pack(fill="x").
    Guarda referencia al label de estado en frame.status_label
    para que la ventana pueda actualizarlo dinámicamente.

### `make_homebridge_switch(parent, text: str, command = None, is_on: bool = False, disabled: bool = False) -> ctk.CTkSwitch`

Crea un CTkSwitch estilado para el control de accesorios Homebridge.

Layout dentro de la tarjeta de dispositivo:
┌─────────────────────────────────────────┐
│   NOMBRE DEL DISPOSITIVO   [══ ●]       │
└─────────────────────────────────────────┘

El switch usa los colores del tema activo:
- ON  → COLORS['success']  (verde por defecto)
- OFF → COLORS['bg_light'] (gris oscuro)
- Deshabilitado (fallo/inactivo) → COLORS['danger'] fijo, no interactivo

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

Gestor centralizado de estilos para todos los widgets

### Métodos públicos

#### `style_radiobutton_tk(rb: tk.Radiobutton, fg: str = None, bg: str = None, hover_fg: str = None) -> None`

Aplica estilo a radiobutton de tkinter

Args:
    rb: Widget radiobutton
    fg: Color de texto
    bg: Color de fondo
    hover_fg: Color al pasar el mouse

#### `style_radiobutton_ctk(rb: ctk.CTkRadioButton, radiobutton_width: int = 25, radiobutton_height: int = 25) -> None`

Aplica estilo a radiobutton de customtkinter

Args:
    rb: Widget radiobutton

#### `style_slider(slider: tk.Scale, color: str = None) -> None`

Aplica estilo a slider de tkinter

Args:
    slider: Widget slider
    color: Color personalizado

#### `style_slider_ctk(slider: ctk.CTkSlider, color: str = None, height = 30) -> None`

Aplica estilo a slider de customtkinter

Args:
    slider: Widget slider
    color: Color personalizado

#### `style_scrollbar(sb: tk.Scrollbar, color: str = None) -> None`

Aplica estilo a scrollbar de tkinter

Args:
    sb: Widget scrollbar
    color: Color personalizado

#### `style_scrollbar_ctk(sb: ctk.CTkScrollbar, color: str = None) -> None`

Aplica estilo a scrollbar de customtkinter

Args:
    sb: Widget scrollbar
    color: Color personalizado

#### `style_ctk_scrollbar(scrollable_frame: ctk.CTkScrollableFrame, color: str = None) -> None`

Aplica estilo a scrollable frame de customtkinter

Args:
    scrollable_frame: Widget scrollable frame
    color: Color personalizado

#### `show_service_stopped_banner(parent_frame, service_name: str) -> None`

Limpia parent_frame y pinta un banner de 'servicio detenido'.
Llamar cuando el monitor asociado a la ventana está parado.
