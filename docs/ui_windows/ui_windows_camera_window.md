# `ui.windows.camera_window`

> **Ruta**: `ui/windows/camera_window.py`

Ventana de cámara del FNK0100K con OCR integrado.
- Captura fotos con rpicam-still (OV5647, Bookworm)
- OCR con Tesseract (local, sin internet)
- Guarda resultado en .txt y .md

Requisitos:
    sudo apt install tesseract-ocr tesseract-ocr-spa rpicam-apps
    pip install pytesseract pillow --break-system-packages

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

Ventana de cámara con captura de fotos y escáner OCR.

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

#### `_create_ui(self)`

Crea la interfaz de usuario principal con tabs y controles.

Returns:
    None.

#### `_build_scrollable_tab(self, parent) -> ctk.CTkFrame`

Construye un frame con canvas scrollable para tabs.

Args:
    parent: Contenedor padre.

Returns:
    Frame scrollable (CTkFrame).

#### `_switch_tab(self, tab: str)`

Cambia entre tabs de foto y escáner, actualizando UI.

Args:
    tab: Nombre del tab ('photo' o 'scan').

Returns:
    None.

#### `_build_photo_content(self, inner: ctk.CTkFrame)`

Construye controles y lista para tab de fotos.

Args:
    inner: Frame interno del tab.

Returns:
    None.

#### `_build_scan_content(self, inner: ctk.CTkFrame)`

Construye controles, textbox y lista para tab de escáner.

Args:
    inner: Frame interno del tab.

Returns:
    None.

#### `_build_inner_scroll(self, parent: ctk.CTkFrame, height: int) -> ctk.CTkFrame`

Crea scroll interno para listas de elementos.

Args:
    parent: Frame padre.
    height: Altura fija del container.

Returns:
    Frame interno scrollable (CTkFrame).

#### `_capture_photo(self)`

Captura una foto usando el servicio de cámara en threading.

Returns:
    None.

#### `_capture_done(self, ok: bool, msg: str, _path)`

Finaliza captura de foto, actualiza status y lista.

Args:
    ok: Si la captura fue exitosa.
    msg: Mensaje de estado.
    _path: Ruta de la foto (no usada).

Returns:
    None.

#### `_scan_document(self)`

Inicia escaneo OCR en background thread.

Returns:
    None.

#### `_scan_done(self, text, msg: str)`

Finaliza escaneo OCR, actualiza textbox y lista.

Args:
    text: Texto extraído.
    msg: Mensaje de estado.

Returns:
    None.

#### `_set_textbox(self, text: str)`

Establece el texto en el textbox, habilita copia.

Args:
    text: Texto OCR a mostrar.

Returns:
    None.

#### `_clear_textbox(self)`

Limpia el textbox y deshabilita botón de copia.

Returns:
    None.

#### `_copy_text(self)`

Copia texto del textbox al portapapeles.

Returns:
    None.

#### `_refresh_photo_list(self)`

Actualiza la lista de fotos guardadas en el tab.

Returns:
    None.

#### `_refresh_scan_list(self)`

Actualiza la lista de escaneos guardados en el tab.

Returns:
    None.

#### `_list_row(self, parent, label: str, size_kb: int, on_delete)`

Crea fila UI para una foto en la lista.

Args:
    parent: Frame padre.
    label: Etiqueta con nombre/icono.
    size_kb: Tamaño en KB.
    on_delete: Callback para borrar.

Returns:
    None.

#### `_scan_row(self, parent, txt, md)`

Crea fila UI para un escaneo (.txt + .md).

Args:
    parent: Frame padre.
    txt: Path al archivo .txt.
    md: Path al archivo .md.

Returns:
    None.

#### `_load_scan(self, txt_path)`

Carga texto de escaneo en textbox y cambia a tab scan.

Args:
    txt_path: Path al archivo .txt.

Returns:
    None.

#### `_delete_one_scan(self, txt, md)`

Borra un escaneo (.txt + .md) y refresca lista.

Args:
    txt: Path .txt.
    md: Path .md.

Returns:
    None.

#### `_delete_one_photo(self, p)`

Borra una foto y refresca lista.

Args:
    p: Objeto Path de la foto.

Returns:
    None.

#### `_delete_all_photos(self)`

Borra todas las fotos y refresca lista.

Returns:
    None.

#### `_delete_all_scans(self)`

Borra todos los escaneos y refresca lista/textbox.

Returns:
    None.

</details>
