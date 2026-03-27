"""
Ventana de cámara del FNK0100K con OCR integrado.
- Captura fotos con rpicam-still (OV5647, Bookworm)
- OCR con Tesseract (local, sin internet)
- Guarda resultado en .txt y .md

Requisitos:
    sudo apt install tesseract-ocr tesseract-ocr-spa rpicam-apps
    pip install pytesseract pillow --break-system-packages
"""
import threading
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES,
                              DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from core import camera_service as cam
from utils.logger import get_logger

logger = get_logger(__name__)

_INNER_W = DSI_WIDTH - 50


class CameraWindow(ctk.CTkToplevel):
    """Ventana de cámara con captura de fotos y escáner OCR."""

    def __init__(self, parent):
        """Inicializa la ventana de cámara principal.

        Args:
            parent: Ventana padre (CTkToplevel).

        Returns:
            None.
        """
        super().__init__(parent)
        self.title("Cámara / Escáner")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._busy       = False
        self._active_tab = "photo"

        self._canvases = {}
        self._inners   = {}

        self._create_ui()
        self._refresh_photo_list()
        self._refresh_scan_list()
        logger.info("[CameraWindow] Ventana Abierta")

    # ── Estructura principal ──────────────────────────────────────────────────

    def _create_ui(self):
        """Crea la interfaz de usuario principal con tabs y controles.

        Returns:
            None.
        """
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="CÁMARA / ESCÁNER OCR", on_close=self.destroy)

        # ── Selector de tab (botones) ──
        tab_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=8)
        tab_bar.pack(fill="x", padx=5, pady=(0, 4))

        self._tab_photo_btn = make_futuristic_button(
            tab_bar, text="" + Icons.CAMARA + " Foto",
            command=lambda: self._switch_tab("photo"),
            width=14, height=7, font_size=14,
        )
        self._tab_photo_btn.pack(side="left", padx=8, pady=6)

        self._tab_scan_btn = make_futuristic_button(
            tab_bar, text="" + Icons.SEARCH + " Escáner OCR",
            command=lambda: self._switch_tab("scan"),
            width=18, height=7, font_size=14,
        )
        self._tab_scan_btn.pack(side="left", padx=4, pady=6)

        # ── Contenedor de tabs ──
        self._tab_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        self._tab_container.pack(fill="both", expand=True)

        self._photo_frame = self._build_scrollable_tab(self._tab_container)
        self._scan_frame  = self._build_scrollable_tab(self._tab_container)

        self._build_photo_content(self._inners["photo"])
        self._build_scan_content(self._inners["scan"])

        self._switch_tab("photo")

    def _build_scrollable_tab(self, parent) -> ctk.CTkFrame:
        """Construye un frame con canvas scrollable para tabs.

        Args:
            parent: Contenedor padre.

        Returns:
            Frame scrollable (CTkFrame).
        """
        tab_name = "photo" if "photo" not in self._canvases else "scan"
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])

        scroll_container = ctk.CTkFrame(frame, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=_INNER_W)
        inner.bind("<Configure>",
                   lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))

        self._canvases[tab_name] = canvas
        self._inners[tab_name]   = inner
        return frame

    def _switch_tab(self, tab: str):
        """Cambia entre tabs de foto y escáner, actualizando UI.

        Args:
            tab: Nombre del tab ('photo' o 'scan').

        Returns:
            None.
        """
        self._active_tab = tab
        if tab == "photo":
            self._scan_frame.pack_forget()
            self._photo_frame.pack(fill="both", expand=True)
            self._tab_photo_btn.configure(
                fg_color=COLORS['primary'], border_width=2,
                border_color=COLORS['secondary'])
            self._tab_scan_btn.configure(
                fg_color=COLORS['bg_dark'], border_width=1,
                border_color=COLORS['border'])
        else:
            self._photo_frame.pack_forget()
            self._scan_frame.pack(fill="both", expand=True)
            self._tab_scan_btn.configure(
                fg_color=COLORS['primary'], border_width=2,
                border_color=COLORS['secondary'])
            self._tab_photo_btn.configure(
                fg_color=COLORS['bg_dark'], border_width=1,
                border_color=COLORS['border'])

    # ── Contenido tab FOTO ────────────────────────────────────────────────────

    def _build_photo_content(self, inner: ctk.CTkFrame):
        """Construye controles y lista para tab de fotos.

        Args:
            inner: Frame interno del tab.

        Returns:
            None.
        """
        ctrl = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        ctrl.pack(fill="x", padx=10, pady=(6, 4))

        row = ctk.CTkFrame(ctrl, fg_color="transparent")
        row.pack(pady=10)

        self._photo_btn = make_futuristic_button(
            row, text="" + Icons.CAMARA + " Capturar",
            command=self._capture_photo,
            width=16, height=9, font_size=16,
        )
        self._photo_btn.pack(side="left", padx=10)

        ctk.CTkLabel(row, text="Resolución:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(16, 4))

        self._res_var = ctk.StringVar(master=self, value="1920x1080")
        ctk.CTkOptionMenu(
            row, variable=self._res_var,
            values=["640x480", "1296x972", "1920x1080", "2592x1944"],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            button_color=COLORS['primary'],
            width=140,
        ).pack(side="left")

        self._photo_status = ctk.CTkLabel(
            ctrl, text="Listo",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        )
        self._photo_status.pack(pady=(0, 8))

        list_hdr = ctk.CTkFrame(inner, fg_color="transparent")
        list_hdr.pack(fill="x", padx=10, pady=(4, 2))

        ctk.CTkLabel(list_hdr,
                     text=f"Fotos guardadas (máx. {cam.MAX_PHOTOS})",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left")

        make_futuristic_button(
            list_hdr, text="" + Icons.TRASH + " Borrar todas",
            command=self._delete_all_photos,
            width=12, height=6, font_size=11,
        ).pack(side="right")

        self._photo_list_frame = self._build_inner_scroll(inner, height=300)

    # ── Contenido tab ESCÁNER ─────────────────────────────────────────────────

    def _build_scan_content(self, inner: ctk.CTkFrame):
        """Construye controles, textbox y lista para tab de escáner.

        Args:
            inner: Frame interno del tab.

        Returns:
            None.
        """
        ctrl = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        ctrl.pack(fill="x", padx=10, pady=(6, 4))

        row = ctk.CTkFrame(ctrl, fg_color="transparent")
        row.pack(pady=8)

        self._scan_btn = make_futuristic_button(
            row, text="" + Icons.SEARCH + " Escanear documento",
            command=self._scan_document,
            width=22, height=9, font_size=16,
        )
        self._scan_btn.pack(side="left", padx=10)

        ctk.CTkLabel(row, text="Idioma:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(16, 4))

        self._lang_var = ctk.StringVar(master=self, value="spa")
        ctk.CTkOptionMenu(
            row, variable=self._lang_var,
            values=["spa", "eng", "spa+eng"],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            button_color=COLORS['primary'],
            width=110,
        ).pack(side="left")

        self._scan_status = ctk.CTkLabel(
            ctrl, text="Coloca el documento y pulsa Escanear",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        )
        self._scan_status.pack(pady=(0, 8))

        txt_hdr = ctk.CTkFrame(inner, fg_color="transparent")
        txt_hdr.pack(fill="x", padx=10, pady=(4, 2))

        ctk.CTkLabel(txt_hdr, text="Texto extraído:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left")

        self._copy_btn = make_futuristic_button(
            txt_hdr, text="" + Icons.CLIPBOARD + " Copiar",
            command=self._copy_text,
            width=10, height=5, font_size=11,
        )
        self._copy_btn.pack(side="right")
        self._copy_btn.configure(state="disabled")

        self._text_box = ctk.CTkTextbox(
            inner,
            fg_color=COLORS['bg_dark'],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            height=160, wrap="word",
        )
        self._text_box.pack(fill="x", padx=10, pady=4)
        self._text_box.configure(state="disabled")

        scan_hdr = ctk.CTkFrame(inner, fg_color="transparent")
        scan_hdr.pack(fill="x", padx=10, pady=(6, 2))

        ctk.CTkLabel(scan_hdr, text="Escaneos guardados:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left")

        make_futuristic_button(
            scan_hdr, text="" + Icons.TRASH + " Borrar todos",
            command=self._delete_all_scans,
            width=12, height=6, font_size=11,
        ).pack(side="right")

        self._scan_list_frame = self._build_inner_scroll(inner, height=200)

    # ── Scroll interno para listas ────────────────────────────────────────────

    def _build_inner_scroll(self, parent: ctk.CTkFrame, height: int) -> ctk.CTkFrame:
        """Crea scroll interno para listas de elementos.

        Args:
            parent: Frame padre.
            height: Altura fija del container.

        Returns:
            Frame interno scrollable (CTkFrame).
        """
        container = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'],
                                 corner_radius=6, height=height)
        container.pack(fill="x", padx=10, pady=(0, 6))
        container.pack_propagate(False)

        canvas = ctk.CTkCanvas(container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            container, orientation="vertical",
            command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=_INNER_W - 40)
        inner.bind("<Configure>",
                   lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
        return inner

    # ── Captura de foto ───────────────────────────────────────────────────────

    def _capture_photo(self):
        """Captura una foto usando el servicio de cámara en threading.

        Returns:
            None.
        """
        if self._busy:
            return
        self._busy = True
        self._photo_btn.configure(state="disabled")
        self._photo_status.configure(text="" + Icons.WAITING + " Capturando...", text_color=COLORS['text'])
        w, h = self._res_var.get().split("x")
        threading.Thread(
            target=lambda: self.after(0, self._capture_done, *cam.capture(w, h)),
            daemon=True,
        ).start()

    def _capture_done(self, ok: bool, msg: str, _path):
        """Finaliza captura de foto, actualiza status y lista.

        Args:
            ok: Si la captura fue exitosa.
            msg: Mensaje de estado.
            _path: Ruta de la foto (no usada).

        Returns:
            None.
        """
        self._busy = False
        self._photo_btn.configure(state="normal")
        color = COLORS['primary'] if ok else COLORS['danger']
        self._photo_status.configure(text=msg, text_color=color)
        self._refresh_photo_list()

    # ── Escáner OCR ───────────────────────────────────────────────────────────

    def _scan_document(self):
        """Inicia escaneo OCR en background thread.

        Returns:
            None.
        """
        if self._busy:
            return
        self._busy = True
        self._scan_btn.configure(state="disabled")
        self._scan_status.configure(text="" + Icons.WAITING + " Procesando...", text_color=COLORS['text'])
        self._clear_textbox()
        lang = self._lang_var.get()
        threading.Thread(
            target=lambda: self.after(0, self._scan_done, *cam.scan(lang)),
            daemon=True,
        ).start()

    def _scan_done(self, text, msg: str):
        """Finaliza escaneo OCR, actualiza textbox y lista.

        Args:
            text: Texto extraído.
            msg: Mensaje de estado.

        Returns:
            None.
        """
        self._busy = False
        self._scan_btn.configure(state="normal")
        color = COLORS['primary'] if text else COLORS['danger']
        self._scan_status.configure(text=msg, text_color=color)
        if text:
            self._set_textbox(text)
            self._copy_btn.configure(state="normal")
        self._refresh_scan_list()

    # ── TextBox helpers ───────────────────────────────────────────────────────

    def _set_textbox(self, text: str):
        """Establece el texto en el textbox, habilita copia.

        Args:
            text: Texto OCR a mostrar.

        Returns:
            None.
        """
        self._text_box.configure(state="normal")
        self._text_box.delete("1.0", "end")
        self._text_box.insert("1.0", text)
        self._text_box.configure(state="disabled")

    def _clear_textbox(self):
        """Limpia el textbox y deshabilita botón de copia.

        Returns:
            None.
        """
        self._text_box.configure(state="normal")
        self._text_box.delete("1.0", "end")
        self._text_box.configure(state="disabled")
        self._copy_btn.configure(state="disabled")

    def _copy_text(self):
        """Copia texto del textbox al portapapeles.

        Returns:
            None.
        """
        self._text_box.configure(state="normal")
        text = self._text_box.get("1.0", "end").strip()
        self._text_box.configure(state="disabled")
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self._copy_btn.configure(text="" + Icons.OK + " Copiado")
            self.after(2000, lambda: self._copy_btn.configure(text="" + Icons.CLIPBOARD + " Copiar"))

    # ── Listas ────────────────────────────────────────────────────────────────

    def _refresh_photo_list(self):
        """Actualiza la lista de fotos guardadas en el tab.

        Returns:
            None.
        """
        for w in self._photo_list_frame.winfo_children():
            w.destroy()
        photos = cam.list_photos()
        if not photos:
            ctk.CTkLabel(self._photo_list_frame, text="No hay fotos guardadas",
                         text_color=COLORS['text_dim']).pack(pady=10)
            return
        for p in photos:
            self._list_row(
                self._photo_list_frame,
                f"{Icons.CAMARA} {p.name}", p.stat().st_size // 1024,
                on_delete=lambda ph=p: self._delete_one_photo(ph),
            )

    def _refresh_scan_list(self):
        """Actualiza la lista de escaneos guardados en el tab.

        Returns:
            None.
        """
        for w in self._scan_list_frame.winfo_children():
            w.destroy()
        scans = cam.list_scans()
        if not scans:
            ctk.CTkLabel(self._scan_list_frame, text="No hay escaneos guardados",
                         text_color=COLORS['text_dim']).pack(pady=10)
            return
        for txt, md in scans:
            self._scan_row(self._scan_list_frame, txt, md)

    def _list_row(self, parent, label: str, size_kb: int, on_delete):
        """Crea fila UI para una foto en la lista.

        Args:
            parent: Frame padre.
            label: Etiqueta con nombre/icono.
            size_kb: Tamaño en KB.
            on_delete: Callback para borrar.

        Returns:
            None.
        """
        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=6)
        row.pack(fill="x", pady=2, padx=4)
        ctk.CTkLabel(row, text=f"{label}  ({size_kb} KB)",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text'], anchor="w",
                     ).pack(side="left", padx=10, pady=6, expand=True, fill="x")
        make_futuristic_button(
            row, text="" + Icons.TRASH + "", command=on_delete,
            width=4, height=5, font_size=13,
        ).pack(side="right", padx=6, pady=4)

    def _scan_row(self, parent, txt, md):
        """Crea fila UI para un escaneo (.txt + .md).

        Args:
            parent: Frame padre.
            txt: Path al archivo .txt.
            md: Path al archivo .md.

        Returns:
            None.
        """
        from pathlib import Path
        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=6)
        row.pack(fill="x", pady=2, padx=4)
        size_kb = txt.stat().st_size // 1024
        ctk.CTkLabel(row, text=f"{Icons.DOCUMENT} {txt.stem}  ({size_kb} KB)  [.txt + .md]",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text'], anchor="w",
                     ).pack(side="left", padx=10, pady=6, expand=True, fill="x")
        make_futuristic_button(
            row, text="" + Icons.TRASH + "",
            command=lambda t=txt, m=md: self._delete_one_scan(t, m),
            width=4, height=5, font_size=13,
        ).pack(side="right", padx=2, pady=4)
        make_futuristic_button(
            row, text="" + Icons.FOLDER_OPEN + "",
            command=lambda t=txt: self._load_scan(t),
            width=4, height=5, font_size=13,
        ).pack(side="right", padx=2, pady=4)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _load_scan(self, txt_path):
        """Carga texto de escaneo en textbox y cambia a tab scan.

        Args:
            txt_path: Path al archivo .txt.

        Returns:
            None.
        """
        text = cam.load_scan_text(txt_path)
        if text:
            self._set_textbox(text)
            self._copy_btn.configure(state="normal")
            self._switch_tab("scan")

    def _delete_one_scan(self, txt, md):
        """Borra un escaneo (.txt + .md) y refresca lista.

        Args:
            txt: Path .txt.
            md: Path .md.

        Returns:
            None.
        """
        cam.delete_scan(txt, md)
        self._refresh_scan_list()

    def _delete_one_photo(self, p):
        """Borra una foto y refresca lista.

        Args:
            p: Objeto Path de la foto.

        Returns:
            None.
        """
        cam.delete_photo(p)
        self._refresh_photo_list()

    def _delete_all_photos(self):
        """Borra todas las fotos y refresca lista.

        Returns:
            None.
        """
        cam.delete_all_photos()
        self._refresh_photo_list()

    def _delete_all_scans(self):
        """Borra todos los escaneos y refresca lista/textbox.

        Returns:
            None.
        """
        cam.delete_all_scans()
        self._refresh_scan_list()
        self._clear_textbox()




