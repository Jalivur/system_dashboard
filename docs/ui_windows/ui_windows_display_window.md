# `ui.windows.display_window`

> **Ruta**: `ui/windows/display_window.py`

> **Cobertura de documentación**: 🟢 100% (11/11)

Ventana de control de brillo de la pantalla.
Hardware: Freenove FNK0100K — Raspberry Pi 5.

---

## Tabla de contenidos

**Clase [`DisplayWindow`](#clase-displaywindow)**

---

## Dependencias internas

- `config.settings`
- `core.display_service`
- `ui.styles`
- `utils.logger`

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger
from core.display_service import BRIGHTNESS_MIN, BRIGHTNESS_MAX
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `QUICK_LEVELS` | `[('' + Icons.MOON_NEW + ' 10%', 10), ('' + Icons.MOON_CRESCENT + ' 30%', 30), ('...` |

## Clase `DisplayWindow(ctk.CTkToplevel)`

Ventana emergente para controlar el brillo de la pantalla.

Args:
    parent: Ventana padre que crea esta ventana.
    display_service: Servicio encargado de gestionar el brillo de la pantalla.

Raises:
    Ninguna excepción específica.

Returns:
    Ningún valor de retorno.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_display_service` | `display_service` |
| `_slider_var` | `ctk.IntVar(master=self, value=self._display_service.get_brightness())` |
| `_banner_shown` | `False` |
| `_inner` | `None` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, display_service)`

Inicializa la ventana de control de brillo de pantalla.

Args:
    parent: Ventana padre.
    display_service: Servicio de control de display.

Returns:
    None

Raises:
    None

#### `_create_ui(self)`

Crea la estructura principal de la interfaz de usuario de la ventana.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_build_content(self, inner)`

Construye el contenido real de la ventana de visualización.

Args:
    inner: El contenedor interno donde se construirá el contenido.

Returns:
    None

Raises:
    None

#### `_update(self)`

Actualiza la ventana periódicamente para reflejar el estado del servicio.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_on_slider(self, value)`

Actualiza el brillo de la pantalla según el valor del deslizador.

Args:
    value: El nuevo valor de brillo seleccionado en el deslizador.

Returns:
    None

Raises:
    None

#### `_set_quick(self, value)`

Establece un nivel de brillo rápido predefinido.

Args:
    value (int): Nivel de brillo en un rango de 0 a 100.

Returns:
    None

Raises:
    Ninguna excepción específica.

#### `_screen_on(self)`

Activa la pantalla y la establece al 100% de brillo.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Excepciones relacionadas con DisplayService

#### `_screen_off(self)`

Apaga la pantalla configurando el brillo al 0%.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Excepciones relacionadas con el servicio de pantalla

#### `_toggle_dim(self)`

Activa o desactiva el modo de atenuado automático por inactividad.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_refresh(self)`

Actualiza la etiqueta y slider con el brillo actual.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

</details>
