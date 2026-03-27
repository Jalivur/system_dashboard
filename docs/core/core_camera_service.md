# `core.camera_service`

> **Ruta**: `core/camera_service.py`

Servicio de cámara y OCR.
Encapsula la captura con rpicam-still, el preprocesado PIL y el OCR con Tesseract.
La UI solo llama a capture(), scan() y los métodos de gestión de ficheros.

## Imports

```python
import subprocess
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
from PIL import Image
import shutil
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `PHOTO_DIR` | `_BASE / 'data' / 'photos'` |
| `SCAN_DIR` | `_BASE / 'data' / 'scans'` |
| `MAX_PHOTOS` | `20` |

## Funciones

### `capture(width: str, height: str) -> tuple[bool, str, Path | None]`

Captura una foto con rpicam-still.

Returns:
    (ok, mensaje, path_foto) — path es None si falla.

### `scan(lang: str = 'spa') -> tuple[str | None, str]`

Captura a máxima resolución, preprocesa y ejecuta OCR.

Args:
    lang: idioma Tesseract ("spa", "eng", "spa+eng")

Returns:
    (texto_extraído_o_None, mensaje_de_estado)

### `preprocess_image(src: Path, dst: Path)`

Escala de grises + contraste + nitidez para mejorar el OCR.

### `run_ocr(img_path: Path, lang: str) -> tuple[str | None, str]`

Ejecuta Tesseract sobre la imagen dada.

Returns:
    (texto_o_None, mensaje)

### `save_txt(path: Path, text: str, ts: str)`

Guarda el texto extraído como .txt con cabecera.

### `save_md(path: Path, text: str, ts: str, lang: str = 'spa')`

Guarda el texto extraído como .md con metadata.

### `list_photos() -> list[Path]`

Devuelve fotos ordenadas de más reciente a más antigua.

### `list_scans() -> list[tuple[Path, Path]]`

Devuelve pares (txt, md) de escaneos, ordenados del más reciente al más antiguo.
Solo incluye escaneos que tienen .txt.

### `load_scan_text(txt_path: Path) -> str | None`

Lee el contenido de un escaneo .txt. Devuelve None si falla.

### `delete_photo(path: Path)`

Elimina una foto.

### `delete_scan(txt: Path, md: Path)`

Elimina un par de ficheros de escaneo (.txt y .md).

### `delete_all_photos()`

Elimina todas las fotos.

### `delete_all_scans()`

Elimina todos los ficheros de escaneo.

### `cleanup_old_photos()`

Elimina las fotos más antiguas si se supera MAX_PHOTOS.

<details>
<summary>Funciones privadas</summary>

### `_ensure_dirs()`

Crea directorios PHOTO_DIR y SCAN_DIR si no existen.

### `_rpicam_capture(filename: Path, w: str, h: str) -> tuple[bool, str]`

Llama a rpicam-still y devuelve (ok, mensaje).

</details>
