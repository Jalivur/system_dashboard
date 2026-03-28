# `ui.windows.camera_window`

> **Ruta**: `ui/windows/camera_window.py`

> **Cobertura de documentación**: 🟢 100% (24/24)

Ventana de cámara del FNK0100K con OCR integrado.
- Captura fotos con rpicam-still (OV5647, Bookworm)
- OCR con Tesseract (local, sin internet)
- Guarda resultado en .txt y .md

Requisitos:
    sudo apt install tesseract-ocr tesseract-ocr-spa rpicam-apps
    pip install pytesseract pillow --break-system-packages

---

## Tabla de contenidos

**Clase [`CameraWindow`](#clase-camerawindow)**

---

## Dependencias internas

- `config.settings`
- `core`
- `ui.styles`
- `utils.logger`

## Imports

```python
import threading
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from core import camera_service as cam
from utils.logger import get_logger
from pathlib import Path
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `CameraWindow(ctk.CTkToplevel)`

Ventana emergente para interactuar con la cámara y realizar capturas de fotos y escaneo OCR.

Args:
    parent: Ventana padre (CTkToplevel) que crea esta instancia.

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_busy` | `False` |
| `_active_tab` | `'photo'` |
| `_canvases` | `{}` |
| `_inners` | `{}` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent)`

Inicializa la ventana de cámara principal.

Args:
    parent: Ventana padre (CTkToplevel).

Returns:
    None.

Raises:
    Ninguna excepción específica.

#### `_create_ui(self)`

Crea la interfaz de usuario principal con tabs y controles.

Args:
    Ninguno.

Returns:
    Ninguno.

Raises:
    Ninguno.

#### `_build_scrollable_tab(self, parent) -> ctk.CTkFrame`

Crea un frame con canvas scrollable para tabs.

Args:
    parent: Contenedor padre.

Returns:
    Frame scrollable (CTkFrame).

#### `_switch_tab(self, tab: str)`

Cambia entre tabs de foto y escáner, actualizando la interfaz de usuario.

Args:
    tab (str): Nombre del tab ('photo' o 'scan').

Returns:
    None.

Raises:
    Ninguna excepción relevante.

#### `_build_photo_content(self, inner: ctk.CTkFrame)`

Construye controles y lista para el contenido de fotos.

Args:
    inner (ctk.CTkFrame): Frame interno donde se ubicarán los controles.

Returns:
    None

Raises:
    Ninguna excepción específica.

#### `_build_scan_content(self, inner: ctk.CTkFrame)`

Construye controles, textbox y lista para tab de escáner.

Args:
    inner (ctk.CTkFrame): Frame interno del tab.

Returns:
    None

Raises:
    None

#### `_build_inner_scroll(self, parent: ctk.CTkFrame, height: int) -> ctk.CTkFrame`

Crea un frame interno scrollable dentro de un contenedor padre.

Args:
    parent: El frame padre donde se ubicará el frame interno.
    height: La altura fija del contenedor interno.

Returns:
    Un frame interno scrollable (CTkFrame).

Raises:
    Ninguna excepción específica.

#### `_capture_photo(self)`

Captura una foto usando el servicio de cámara en un hilo separado.

Args:
    None

Returns:
    None

Raises:
    None

#### `_capture_done(self, ok: bool, msg: str, _path)`

Finaliza la captura de una foto, actualizando el estado y la lista de fotos.

Args:
    ok (bool): Indica si la captura de la foto fue exitosa.
    msg (str): El mensaje de estado resultante de la captura.
    _path: Ruta de la foto capturada (no utilizada).

Returns:
    None

Raises:
    None

#### `_scan_document(self)`

Inicia el escaneo OCR en un hilo en segundo plano.

Args:
    Ninguno.

Returns:
    None.

Raises:
    Ninguna excepción.

Nota: Desactiva el botón de escaneo y actualiza el estado de la ventana.

#### `_scan_done(self, text, msg: str)`

Finaliza el escaneo OCR, actualizando el cuadro de texto y la lista de escaneos.

Args:
    text: El texto extraído del escaneo.
    msg: El mensaje de estado del escaneo.

Returns:
    None

Raises:
    None

#### `_set_textbox(self, text: str)`

Establece el texto en el textbox y lo habilita para copia.

Args:
    text (str): Texto OCR a mostrar.

Returns:
    None

#### `_clear_textbox(self)`

Limpia el contenido del cuadro de texto y deshabilita el botón de copia.

Args:
    Ninguno.

Returns:
    None.

Raises:
    Ninguno.

#### `_copy_text(self)`

Copia el texto seleccionado en el cuadro de texto al portapapeles.

Args:
    Ninguno.

Returns:
    None.

Raises:
    Ninguno.

#### `_refresh_photo_list(self)`

Actualiza la lista de fotos guardadas en el tab.

Args:
    Ninguno.

Returns:
    None.

Raises:
    Ninguno.

#### `_refresh_scan_list(self)`

Actualiza la lista de escaneos guardados en el tab.

Args:
    Ninguno.

Returns:
    None.

Raises:
    Ninguno.

#### `_list_row(self, parent, label: str, size_kb: int, on_delete)`

Crea una fila de interfaz de usuario para representar una foto en una lista.

Args:
    parent: El frame padre que contendrá la fila.
    label (str): La etiqueta o nombre de la foto.
    size_kb (int): El tamaño de la foto en kilobytes.
    on_delete: La función de llamada de vuelta para eliminar la foto.

Returns:
    None

#### `_scan_row(self, parent, txt, md)`

Crea una fila de interfaz de usuario para un escaneo compuesto por archivos .txt y .md.

Args:
    parent: El frame padre que contendrá la fila.
    txt (Path): Ruta al archivo .txt.
    md (Path): Ruta al archivo .md.

Returns:
    None

Raises:
    None

#### `_load_scan(self, txt_path)`

Carga texto de escaneo en textbox y cambia a tab scan.

Args:
    txt_path (str): Path al archivo .txt.

Returns:
    None

Raises:
    None

#### `_delete_one_scan(self, txt, md)`

Elimina un escaneo específico y actualiza la lista de escaneos.

Args:
    txt (str): Ruta del archivo .txt del escaneo.
    md (str): Ruta del archivo .md del escaneo.

Returns:
    None

Raises:
    None

#### `_delete_one_photo(self, p)`

Elimina una foto específica y actualiza la lista de fotos.

Args:
    p: Objeto Path de la foto a eliminar.

Returns:
    None

Raises:
    None

#### `_delete_all_photos(self)`

Elimina todas las fotos de la cámara y actualiza la lista de fotos.

Args:
    Ninguno.

Returns:
    None.

Raises:
    Ninguna excepción.

#### `_delete_all_scans(self)`

Elimina todos los escaneos existentes y actualiza la lista y el área de texto.

Args:
    Ninguno.

Returns:
    Ninguno.

Raises:
    Ninguno.

</details>
