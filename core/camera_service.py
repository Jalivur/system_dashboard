"""
Servicio de cámara y OCR.
Encapsula la captura con rpicam-still, el preprocesado PIL y el OCR con Tesseract.
La UI solo llama a capture(), scan() y los métodos de gestión de ficheros.
"""
import subprocess
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

# Rutas de datos (relativas a la raíz del proyecto)
_BASE     = Path(__file__).resolve().parent.parent
PHOTO_DIR = _BASE / "data" / "photos"
SCAN_DIR  = _BASE / "data" / "scans"
MAX_PHOTOS = 20


def _ensure_dirs():
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    SCAN_DIR.mkdir(parents=True, exist_ok=True)


# ── Captura ───────────────────────────────────────────────────────────────────

def capture(width: str, height: str) -> tuple[bool, str, Path | None]:
    """
    Captura una foto con rpicam-still.

    Returns:
        (ok, mensaje, path_foto) — path es None si falla.
    """
    _ensure_dirs()
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = PHOTO_DIR / f"foto_{ts}.jpg"

    ok, msg = _rpicam_capture(filename, width, height)
    if ok:
        cleanup_old_photos()
        return True, msg, filename
    return False, msg, None


def _rpicam_capture(filename: Path, w: str, h: str) -> tuple[bool, str]:
    """Llama a rpicam-still y devuelve (ok, mensaje)."""
    cmd = [
        "rpicam-still", "-o", str(filename),
        "--width", w, "--height", h,
        "--timeout", "2000", "--nopreview",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=20)
        if r.returncode == 0 and filename.exists():
            logger.info("[CameraService] Foto capturada: %s", filename.name)
            return True, f"✅ Capturada: {filename.name}"
        err = r.stderr.decode().strip()[:80]
        return False, f"❌ Error cámara: {err or 'rpicam-still falló'}"
    except FileNotFoundError:
        return False, "❌ rpicam-still no encontrado"
    except subprocess.TimeoutExpired:
        return False, "❌ Timeout — ¿cámara conectada?"
    except Exception as e:
        logger.error("[CameraService] Error en rpicam_capture: %s", e)
        return False, f"❌ {e}"


# ── OCR ───────────────────────────────────────────────────────────────────────

def scan(lang: str = "spa") -> tuple[str | None, str]:
    """
    Captura a máxima resolución, preprocesa y ejecuta OCR.

    Args:
        lang: idioma Tesseract ("spa", "eng", "spa+eng")

    Returns:
        (texto_extraído_o_None, mensaje_de_estado)
    """
    _ensure_dirs()
    ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_path  = PHOTO_DIR / f"scan_src_{ts}.jpg"
    proc_path = PHOTO_DIR / f"scan_proc_{ts}.jpg"

    ok, msg = _rpicam_capture(img_path, "2592", "1944")
    if not ok:
        return None, msg

    preprocess_image(img_path, proc_path)
    text, ocr_msg = run_ocr(proc_path, lang)

    if text:
        txt_path = SCAN_DIR / f"scan_{ts}.txt"
        md_path  = SCAN_DIR / f"scan_{ts}.md"
        save_txt(txt_path, text, ts)
        save_md(md_path, text, ts, lang)

    for p in [img_path, proc_path]:
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass

    return text, ocr_msg


def preprocess_image(src: Path, dst: Path):
    """Escala de grises + contraste + nitidez para mejorar el OCR."""
    try:
        from PIL import Image, ImageFilter, ImageEnhance
        img = Image.open(src).convert("L")
        img = ImageEnhance.Contrast(img).enhance(2.0)
        img = img.filter(ImageFilter.SHARPEN)
        img.save(str(dst), "JPEG", quality=95)
    except Exception as e:
        logger.warning("[CameraService] Preprocesado falló, usando imagen original: %s", e)
        import shutil
        shutil.copy(str(src), str(dst))


def run_ocr(img_path: Path, lang: str) -> tuple[str | None, str]:
    """
    Ejecuta Tesseract sobre la imagen dada.

    Returns:
        (texto_o_None, mensaje)
    """
    try:
        import pytesseract
        from PIL import Image
        img  = Image.open(str(img_path))
        text = pytesseract.image_to_string(
            img, config=f"--oem 3 --psm 6 -l {lang}"
        ).strip()
        if not text:
            return None, "⚠️ No se detectó texto en la imagen"
        words = len(text.split())
        lines = len(text.splitlines())
        logger.info("[CameraService] OCR completado: %d líneas, %d palabras", lines, words)
        return text, f"✅ {lines} líneas / {words} palabras extraídas"
    except ImportError:
        return None, "❌ pytesseract no instalado: pip install pytesseract"
    except Exception as e:
        logger.error("[CameraService] Error OCR: %s", e)
        return None, f"❌ Error OCR: {e}"


# ── Guardado de resultados ────────────────────────────────────────────────────

def save_txt(path: Path, text: str, ts: str):
    """Guarda el texto extraído como .txt con cabecera."""
    try:
        path.write_text(
            f"Escaneo: {ts}\n{'─' * 40}\n\n{text}", encoding="utf-8"
        )
        logger.info("[CameraService] TXT guardado: %s", path.name)
    except Exception as e:
        logger.error("[CameraService] Error guardando TXT: %s", e)


def save_md(path: Path, text: str, ts: str, lang: str = "spa"):
    """Guarda el texto extraído como .md con metadata."""
    try:
        dt    = datetime.strptime(ts, "%Y%m%d_%H%M%S").strftime("%d/%m/%Y %H:%M:%S")
        lines = [
            "# Escaneo OCR", "",
            f"**Fecha:** {dt}  ",
            f"**Idioma:** {lang}  ",
            f"**Palabras:** {len(text.split())}",
            "", "---", "", "## Texto extraído", "",
        ]
        for line in text.splitlines():
            lines.append(line if line.strip() else "")
        path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("[CameraService] MD guardado: %s", path.name)
    except Exception as e:
        logger.error("[CameraService] Error guardando MD: %s", e)


# ── Gestión de ficheros ───────────────────────────────────────────────────────

def list_photos() -> list[Path]:
    """Devuelve fotos ordenadas de más reciente a más antigua."""
    return sorted(PHOTO_DIR.glob("foto_*.jpg"), reverse=True)


def list_scans() -> list[tuple[Path, Path]]:
    """
    Devuelve pares (txt, md) de escaneos, ordenados del más reciente al más antiguo.
    Solo incluye escaneos que tienen .txt.
    """
    txts = sorted(SCAN_DIR.glob("scan_*.txt"), reverse=True)
    return [(txt, txt.with_suffix(".md")) for txt in txts]


def load_scan_text(txt_path: Path) -> str | None:
    """Lee el contenido de un escaneo .txt. Devuelve None si falla."""
    try:
        return txt_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error("[CameraService] Error cargando escaneo: %s", e)
        return None


def delete_photo(path: Path):
    """Elimina una foto."""
    try:
        path.unlink(missing_ok=True)
    except Exception as e:
        logger.error("[CameraService] Error eliminando foto: %s", e)


def delete_scan(txt: Path, md: Path):
    """Elimina un par de ficheros de escaneo (.txt y .md)."""
    for p in [txt, md]:
        try:
            p.unlink(missing_ok=True)
        except Exception as e:
            logger.error("[CameraService] Error eliminando escaneo: %s", e)


def delete_all_photos():
    """Elimina todas las fotos."""
    for p in PHOTO_DIR.glob("foto_*.jpg"):
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass
    logger.info("[CameraService] Todas las fotos eliminadas")


def delete_all_scans():
    """Elimina todos los ficheros de escaneo."""
    for p in SCAN_DIR.glob("scan_*"):
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass
    logger.info("[CameraService] Todos los escaneos eliminados")


def cleanup_old_photos():
    """Elimina las fotos más antiguas si se supera MAX_PHOTOS."""
    photos = sorted(PHOTO_DIR.glob("foto_*.jpg"))
    while len(photos) > MAX_PHOTOS:
        photos[0].unlink(missing_ok=True)
        photos = photos[1:]
