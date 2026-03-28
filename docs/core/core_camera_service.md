# `core.camera_service`

> **Ruta**: `core/camera_service.py`

> **Cobertura de documentación**: 🟢 100% (16/16)

Servicio de cámara y OCR.
Encapsula la captura con rpicam-still, el preprocesado PIL y el OCR con Tesseract.
La UI solo llama a capture(), scan() y los métodos de gestión de ficheros.

---

## Tabla de contenidos

**Funciones**
- [`capture()`](#funcion-capture)
- [`scan()`](#funcion-scan)
- [`preprocess_image()`](#funcion-preprocess_image)
- [`run_ocr()`](#funcion-run_ocr)
- [`save_txt()`](#funcion-save_txt)
- [`save_md()`](#funcion-save_md)
- [`list_photos()`](#funcion-list_photos)
- [`list_scans()`](#funcion-list_scans)
- [`load_scan_text()`](#funcion-load_scan_text)
- [`delete_photo()`](#funcion-delete_photo)
- [`delete_scan()`](#funcion-delete_scan)
- [`delete_all_photos()`](#funcion-delete_all_photos)
- [`delete_all_scans()`](#funcion-delete_all_scans)
- [`cleanup_old_photos()`](#funcion-cleanup_old_photos)

---

## Dependencias internas

- `utils.logger`

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

Captura una foto con el comando rpicam-still y devuelve el resultado.

Args:
    width (str): Ancho de la foto en píxeles.
    height (str): Alto de la foto en píxeles.

Returns:
    tuple[bool, str, Path | None]: Tupla con éxito (True/False), mensaje de resultado y ruta del archivo de foto (o None si falla).

Raises:
    No se lanzan excepciones explícitas.

### `scan(lang: str = 'spa') -> tuple[str | None, str]`

Captura a máxima resolución, preprocesa y ejecuta OCR para extraer texto de una imagen.

Args:
    lang: idioma Tesseract, por defecto 'spa' ("spa", "eng", "spa+eng")

Returns:
    (texto_extraído_o_None, mensaje_de_estado)

Raises:
    Exception: si falla la eliminación de archivos temporales.

### `preprocess_image(src: Path, dst: Path)`

Aplica filtros de escala de grises, contraste y nitidez a una imagen para mejorar el reconocimiento óptico de caracteres.

Args:
    src (Path): Ruta de la imagen de origen.
    dst (Path): Ruta de la imagen de destino.

Returns:
    None

Raises:
    Exception: Si el preprocesamiento de la imagen falla, se guarda la imagen original en la ruta de destino.

### `run_ocr(img_path: Path, lang: str) -> tuple[str | None, str]`

Ejecuta Tesseract sobre la imagen dada para extraer texto.

Args:
    img_path (Path): Ruta a la imagen a procesar.
    lang (str): Código de idioma para el OCR.

Returns:
    tuple[str | None, str]: Texto extraído o None si no se detectó texto, y un mensaje de resultado.

Raises:
    ImportError: Si pytesseract no está instalado.
    Exception: Si ocurre un error durante el proceso de OCR.

### `save_txt(path: Path, text: str, ts: str)`

Guarda el texto extraído como archivo .txt con cabecera que incluye el momento del escaneo.

Args:
    path (Path): Ruta donde se guardará el archivo .txt.
    text (str): Texto a guardar en el archivo.
    ts (str): Momento del escaneo en formato de timestamp.

Returns:
    None

Raises:
    Exception: Si ocurre un error al guardar el archivo .txt.

### `save_md(path: Path, text: str, ts: str, lang: str = 'spa')`

Guarda el texto extraído como archivo markdown con metadatos.

Args:
    path (Path): Ruta donde se guardará el archivo.
    text (str): Texto extraído a guardar.
    ts (str): Timestamp en formato "%Y%m%d_%H%M%S".
    lang (str): Idioma del texto (por defecto "spa").

Returns:
    None

Raises:
    Exception: Si ocurre un error al guardar el archivo.

### `list_photos() -> list[Path]`

Devuelve una lista de fotos ordenadas de más reciente a más antigua.

Args:
    None

Returns:
    list[Path]: Una lista de objetos Path que representan las fotos.

Raises:
    None

### `list_scans() -> list[tuple[Path, Path]]`

Devuelve pares de archivos de escaneo en formato txt y md, ordenados del más reciente al más antiguo.

Args:
    None

Returns:
    list[tuple[Path, Path]]: Lista de tuplas con rutas a archivos txt y sus correspondientes archivos md.

Raises:
    None

### `load_scan_text(txt_path: Path) -> str | None`

Lee el contenido de un archivo de texto de escaneo.

Args:
    txt_path: Ruta del archivo de texto a leer.

Returns:
    El contenido del archivo como cadena o None si falla.

Raises:
    Excepciones al leer el archivo, registradas en el log.

### `delete_photo(path: Path)`

Elimina una foto del sistema de archivos.

Args:
    path (Path): Ruta de la foto a eliminar.

Raises:
    Exception: Si ocurre un error al eliminar la foto.

### `delete_scan(txt: Path, md: Path)`

Elimina un par de ficheros de escaneo (.txt y .md).

Args:
    txt (Path): Ruta del fichero .txt.
    md (Path): Ruta del fichero .md.

Returns:
    None

Raises:
    Exception: Si ocurre un error al eliminar los ficheros.

### `delete_all_photos()`

Elimina todas las fotos del directorio de fotos.

Args:
    None

Returns:
    None

Raises:
    None

### `delete_all_scans()`

Elimina todos los ficheros de escaneo.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguna excepción

### `cleanup_old_photos()`

Elimina las fotos más antiguas si se supera el límite de fotos permitidas.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

<details>
<summary>Funciones privadas</summary>

### `_ensure_dirs()`

Crea los directorios necesarios si no existen.

Args: None

Returns: None

Raises: None

### `_rpicam_capture(filename: Path, w: str, h: str) -> tuple[bool, str]`

Captura una imagen utilizando rpicam-still y devuelve el resultado de la operación.

Args:
    filename (Path): Ruta donde se guardará la imagen capturada.
    w (str): Ancho de la imagen en píxeles.
    h (str): Alto de la imagen en píxeles.

Returns:
    tuple[bool, str]: Un par que indica si la captura fue exitosa y un mensaje descriptivo.

Raises:
    Exception: Si ocurre un error durante la captura de la imagen.

</details>
