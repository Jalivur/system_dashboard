"""
Ventana de cámara del FNK0100K.
Usa libcamera-still para capturar fotos.
El módulo de cámara está en CAM/DISP 1 de la RPi 5.
"""
import customtkinter as ctk
import subprocess
import threading
import os
from datetime import datetime
from pathlib import Path
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from ui.styles import make_window_header, make_futuristic_button
from utils.logger import get_logger

logger = get_logger(__name__)

_PHOTO_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "photos"
_MAX_PHOTOS = 20   # limpieza automática


class CameraWindow(ctk.CTkToplevel):
    """Ventana de captura de fotos con la cámara del FNK0100K."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Cámara")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        _PHOTO_DIR.mkdir(parents=True, exist_ok=True)

        self._capturing = False
        self._photos    = []

        self._create_ui()
        self._refresh_list()
        logger.info("[CameraWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="CÁMARA", on_close=self.destroy)

        # ── Controles de captura ──
        ctrl_card = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=8)
        ctrl_card.pack(fill="x", padx=10, pady=(6, 4))

        ctrl_row = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        ctrl_row.pack(pady=12)

        self._capture_btn = make_futuristic_button(
            ctrl_row, text="📷 Capturar foto",
            command=self._capture,
            width=20, height=10, font_size=18
        )
        self._capture_btn.pack(side="left", padx=10)

        # Resolución
        ctk.CTkLabel(ctrl_row, text="Resolución:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(20, 4))

        self._res_var = ctk.StringVar(value="1280x720")
        res_menu = ctk.CTkOptionMenu(
            ctrl_row,
            variable=self._res_var,
            values=["640x480", "1280x720", "1920x1080", "2592x1944"],
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            dropdown_font=(FONT_FAMILY, FONT_SIZES['xlarge']),
            fg_color=COLORS['bg_dark'],
            button_color=COLORS['primary'],
            width=130,
        )
        res_menu.pack(side="left")

        # Estado
        self._status_label = ctk.CTkLabel(
            ctrl_card, text="Listo",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim']
        )
        self._status_label.pack(pady=(0, 8))

        # ── Lista de fotos ──
        list_card = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=8)
        list_card.pack(fill="both", expand=True, padx=10, pady=4)

        list_header = ctk.CTkFrame(list_card, fg_color="transparent")
        list_header.pack(fill="x", padx=14, pady=(8, 4))

        ctk.CTkLabel(list_header, text=f"Fotos guardadas (máx. {_MAX_PHOTOS})",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left")

        make_futuristic_button(
            list_header, text="🗑 Borrar todas",
            command=self._delete_all,
            width=12, height=6, font_size=12
        ).pack(side="right")

        # ScrollFrame para la lista
        scroll_frame = ctk.CTkScrollableFrame(
            list_card, fg_color="transparent", height=180
        )
        scroll_frame.pack(fill="both", expand=True, padx=6, pady=(0, 8))
        self._list_frame = scroll_frame

    # ── Captura ───────────────────────────────────────────────────────────────

    def _capture(self):
        if self._capturing:
            return
        self._capturing = True
        self._capture_btn.configure(state="disabled")
        self._status_label.configure(text="⏳ Capturando...", text_color=COLORS['text'])
        threading.Thread(target=self._do_capture, daemon=True).start()

    def _do_capture(self):
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = _PHOTO_DIR / f"foto_{ts}.jpg"
        res      = self._res_var.get()
        w, h     = res.split("x")

        cmd = [
            "rpicam-still",
            "-o", str(filename),
            "--width",  w,
            "--height", h,
            "--timeout", "2000",
            "--nopreview",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=15)
            if result.returncode == 0 and filename.exists():
                msg = f"✅ Guardada: {filename.name}"
                logger.info("[CameraWindow] Foto capturada: %s", filename)
                self._cleanup_old_photos()
            else:
                err = result.stderr.decode().strip()[:80]
                msg = f"❌ Error: {err or 'rpicam-still falló'}"
                logger.error("[CameraWindow] Error capturando: %s", err)
        except FileNotFoundError:
            msg = "❌ rpicam-still no encontrado. Instalar: sudo apt install rpicam-apps"
        except subprocess.TimeoutExpired:
            msg = "❌ Timeout — ¿cámara conectada?"
        except Exception as e:
            msg = f"❌ {e}"

        self.after(0, self._capture_done, msg)

    def _capture_done(self, msg: str):
        self._capturing = False
        self._capture_btn.configure(state="normal")
        color = COLORS['primary'] if msg.startswith("✅") else COLORS['danger']
        self._status_label.configure(text=msg, text_color=color)
        self._refresh_list()

    # ── Lista de fotos ────────────────────────────────────────────────────────

    def _refresh_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        photos = sorted(_PHOTO_DIR.glob("*.jpg"), reverse=True)
        if not photos:
            ctk.CTkLabel(self._list_frame, text="No hay fotos guardadas",
                         text_color=COLORS['text_dim']).pack(pady=10)
            return

        for photo in photos:
            row = ctk.CTkFrame(self._list_frame, fg_color=COLORS['bg_medium'], corner_radius=6)
            row.pack(fill="x", pady=2)

            size_kb = photo.stat().st_size // 1024
            ctk.CTkLabel(row, text=f"📷 {photo.name}  ({size_kb} KB)",
                         font=(FONT_FAMILY, FONT_SIZES['small']),
                         text_color=COLORS['text'], anchor="w").pack(
                side="left", padx=10, pady=6, expand=True, fill="x"
            )

            make_futuristic_button(
                row, text="🗑",
                command=lambda p=photo: self._delete_one(p),
                width=4, height=5, font_size=14
            ).pack(side="right", padx=6, pady=4)

    def _delete_one(self, photo: Path):
        try:
            photo.unlink()
        except Exception:
            pass
        self._refresh_list()

    def _delete_all(self):
        for p in _PHOTO_DIR.glob("*.jpg"):
            try:
                p.unlink()
            except Exception:
                pass
        self._refresh_list()
        self._status_label.configure(text="Fotos eliminadas", text_color=COLORS['text_dim'])

    def _cleanup_old_photos(self):
        """Mantiene solo las últimas _MAX_PHOTOS fotos."""
        photos = sorted(_PHOTO_DIR.glob("*.jpg"))
        while len(photos) > _MAX_PHOTOS:
            photos[0].unlink(missing_ok=True)
            photos = photos[1:]