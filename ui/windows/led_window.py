"""
Ventana de control de LEDs RGB del GPIO Board.
Hardware: Freenove FNK0100K — 4 LEDs RGB (I2C 0x21, gestionados por fase1.py).
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from core.led_service import LED_MODES, LED_MODE_LABELS
from utils.logger import get_logger

logger = get_logger(__name__)


class LedWindow(ctk.CTkToplevel):
    """Ventana de control de LEDs RGB."""

    def __init__(self, parent, led_service):
        super().__init__(parent)
        self.led_service = led_service

        self.title("Control LEDs")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._r = ctk.IntVar(value=0)
        self._g = ctk.IntVar(value=255)
        self._b = ctk.IntVar(value=0)
        self._mode_var = ctk.StringVar(value="auto")

        self._banner_shown = False
        self._inner = None   # referencia al frame de contenido

        self._create_ui()
        self._update()
        logger.info("[LedWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="CONTROL LEDs RGB", on_close=self.destroy)

        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        sb = ctk.CTkScrollbar(scroll_container, orientation="vertical", command=canvas.yview, width=30)
        sb.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(sb)
        canvas.configure(yscrollcommand=sb.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._inner = inner

        self._build_content(inner)

    def _build_content(self, inner):
        """Construye el contenido real de la ventana."""
        # ── Selector de modo ──
        mode_card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        mode_card.pack(fill="x", padx=10, pady=(6, 4))

        ctk.CTkLabel(mode_card, text="Modo de los LEDs",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(anchor="w", padx=14, pady=(10, 6))

        btn_row = ctk.CTkFrame(mode_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(0, 10))

        self._mode_btns = {}
        for i, mode in enumerate(LED_MODES):
            label = LED_MODE_LABELS[mode]
            btn = make_futuristic_button(
                btn_row, text=label,
                command=lambda m=mode: self._set_mode(m),
                width=14, height=8, font_size=13
            )
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=4, sticky="nsew")
            self._mode_btns[mode] = btn
        for c in range(3):
            btn_row.grid_columnconfigure(c, weight=1)

        # ── Color RGB ──
        color_card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        color_card.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(color_card, text="Color (para modos: fijo, secuencial, respiración)",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(anchor="w", padx=14, pady=(10, 4))

        for label, var, color_accent in [
            ("R", self._r, "#FF4444"),
            ("G", self._g, "#44FF44"),
            ("B", self._b, "#4488FF"),
        ]:
            row = ctk.CTkFrame(color_card, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=2)

            ctk.CTkLabel(row, text=label, width=20,
                         font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
                         text_color=color_accent).pack(side="left")

            ctk.CTkSlider(
                row, from_=0, to=255, variable=var,
                command=lambda v, lbl=label: self._on_color_change(),
                width=500, height=28,
                progress_color=color_accent,
                button_color=color_accent,
                button_hover_color=COLORS['secondary'],
            ).pack(side="left", padx=8)

            val_lbl = ctk.CTkLabel(row, text="---", width=40,
                                   font=(FONT_FAMILY, FONT_SIZES['small']),
                                   text_color=COLORS['text'])
            val_lbl.pack(side="left")
            setattr(self, f"_{label.lower()}_lbl", val_lbl)

        # ── Preview color ──
        preview_row = ctk.CTkFrame(color_card, fg_color="transparent")
        preview_row.pack(pady=(6, 10))

        ctk.CTkLabel(preview_row, text="Preview:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 10))

        import tkinter as tk
        self._preview_canvas = tk.Canvas(preview_row, width=60, height=30,
                                         bg="#000000", highlightthickness=1,
                                         highlightbackground=COLORS['border'])
        self._preview_canvas.pack(side="left")
        self._preview_rect = self._preview_canvas.create_rectangle(0, 0, 60, 30, fill="#00ff00")

        make_futuristic_button(
            preview_row, text="✓ Aplicar color",
            command=self._apply_color,
            width=16, height=8, font_size=14
        ).pack(side="left", padx=10)

        # ── Colores rápidos ──
        quick_card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        quick_card.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(quick_card, text="Colores rápidos",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(anchor="w", padx=14, pady=(10, 6))

        presets = [
            ("🔴 Rojo",     255, 0,   0),
            ("🟢 Verde",    0,   255, 0),
            ("🔵 Azul",     0,   0,   255),
            ("🟡 Amarillo", 255, 200, 0),
            ("🟣 Violeta",  180, 0,   255),
            ("⚪ Blanco",   255, 255, 255),
        ]
        qrow = ctk.CTkFrame(quick_card, fg_color="transparent")
        qrow.pack(fill="x", padx=10, pady=(0, 10))
        for i, (lbl, r, g, b) in enumerate(presets):
            make_futuristic_button(
                qrow, text=lbl,
                command=lambda r=r, g=g, b=b: self._quick_color(r, g, b),
                width=12, height=7, font_size=12
            ).grid(row=i // 3, column=i % 3, padx=5, pady=3, sticky="nsew")
        for c in range(3):
            qrow.grid_columnconfigure(c, weight=1)

        # ── Estado actual ──
        self._status_label = ctk.CTkLabel(inner, text="",
                                          font=(FONT_FAMILY, FONT_SIZES['small']),
                                          text_color=COLORS['text_dim'])
        self._status_label.pack(pady=6)

        self._load_current_state()
        self._update_preview()

    # ── Loop de actualización con banner ──────────────────────────────────────

    def _update(self):
        if not self.winfo_exists():
            return

        if not self.led_service._running:
            # Mostrar banner si no estaba ya
            if not self._banner_shown:
                for w in self._inner.winfo_children():
                    w.destroy()
                StyleManager.show_service_stopped_banner(self._inner, "LED Service")
                self._banner_shown = True
        else:
            # Reconstruir contenido si veníamos de banner
            if self._banner_shown:
                self._banner_shown = False
                for w in self._inner.winfo_children():
                    w.destroy()
                self._build_content(self._inner)

        self.after(UPDATE_MS, self._update)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _set_mode(self, mode: str):
        r, g, b = self._r.get(), self._g.get(), self._b.get()
        self.led_service.set_mode(mode, r, g, b)
        self._mode_var.set(mode)
        self._highlight_mode_btn(mode)
        self._update_status()

    def _on_color_change(self):
        self._update_preview()

    def _apply_color(self):
        r, g, b = self._r.get(), self._g.get(), self._b.get()
        mode = self._mode_var.get()
        if mode in ("auto", "rainbow", "off"):
            mode = "static"
            self._mode_var.set(mode)
        self.led_service.set_mode(mode, r, g, b)
        self._highlight_mode_btn(mode)
        self._update_status()

    def _quick_color(self, r: int, g: int, b: int):
        self._r.set(r)
        self._g.set(g)
        self._b.set(b)
        self._update_preview()
        self._apply_color()

    def _update_preview(self):
        if not hasattr(self, "_preview_canvas"):
            return
        r, g, b = self._r.get(), self._g.get(), self._b.get()
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        self._preview_canvas.itemconfigure(self._preview_rect, fill=hex_color)
        if hasattr(self, "_r_lbl"):
            self._r_lbl.configure(text=str(r))
            self._g_lbl.configure(text=str(g))
            self._b_lbl.configure(text=str(b))

    def _highlight_mode_btn(self, active_mode: str):
        if not hasattr(self, "_mode_btns"):
            return
        for mode, btn in self._mode_btns.items():
            if mode == active_mode:
                btn.configure(fg_color=COLORS['primary'], border_width=2,
                              border_color=COLORS['secondary'])
            else:
                btn.configure(fg_color=COLORS['bg_dark'], border_width=1,
                              border_color=COLORS['border'])

    def _update_status(self):
        if not hasattr(self, "_status_label"):
            return
        state = self.led_service.get_state()
        mode  = state.get("mode", "auto")
        label = LED_MODE_LABELS.get(mode, mode)
        r, g, b = state.get("r", 0), state.get("g", 255), state.get("b", 0)
        if mode in ("auto", "rainbow", "off"):
            self._status_label.configure(text=f"Modo activo: {label}")
        else:
            self._status_label.configure(
                text=f"Modo activo: {label}  •  RGB({r},{g},{b})"
            )

    def _load_current_state(self):
        state = self.led_service.get_state()
        mode  = state.get("mode", "auto")
        self._mode_var.set(mode)
        self._r.set(state.get("r", 0))
        self._g.set(state.get("g", 255))
        self._b.set(state.get("b", 0))
        self._highlight_mode_btn(mode)
        self._update_status()
        self._update_preview()
