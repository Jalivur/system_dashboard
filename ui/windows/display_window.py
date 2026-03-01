"""
Ventana de control de brillo de la pantalla.
Hardware: Freenove FNK0100K — Raspberry Pi 5.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger
from core.display_service import BRIGHTNESS_MIN, BRIGHTNESS_MAX

logger = get_logger(__name__)

QUICK_LEVELS = [
    ("🌑 10%",   10),
    ("🌒 30%",   30),
    ("🌓 60%",   60),
    ("🌕 100%", 100),
]


class DisplayWindow(ctk.CTkToplevel):
    """Ventana de control de brillo de pantalla."""

    def __init__(self, parent, display_service):
        super().__init__(parent)
        self.display_service = display_service

        self.title("Control de Pantalla")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._slider_var = ctk.IntVar(value=self.display_service.get_brightness())
        self._banner_shown = False
        self._inner = None

        self._create_ui()
        self._update()
        logger.info("[DisplayWindow] Ventana abierta (método: %s)",
                    self.display_service.get_method())

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main,
            title="CONTROL DE PANTALLA",
            on_close=self.destroy,
        )
        # Area de scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30,
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._inner = inner

        self._build_content(inner)

    def _build_content(self, inner):
        """Construye el contenido real de la ventana."""
        # ── Sin método disponible ──
        if not self.display_service.is_available():
            ctk.CTkLabel(
                inner,
                text=(
                    "⚠️ Brillo no disponible\n\n"
                    "No se encontró /sys/class/backlight/ ni wlr-randr.\n\n"
                    "Consulta GUIA_BRILLO_DSI.md → Paso 0\n"
                    "para diagnosticar tu sistema."
                ),
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                text_color=COLORS.get('warning', '#ffaa00'),
                justify="center",
            ).pack(expand=True)
            return

        # ── Info método activo ──
        method = self.display_service.get_method()
        ctk.CTkLabel(
            inner,
            text=f"Método activo: {method}",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(fill="x", padx=14, pady=(4, 0))

        # ── Tarjeta brillo actual + slider ──
        card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(6, 4))

        ctk.CTkLabel(
            card, text="Brillo",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(pady=(10, 0))

        self._brightness_label = ctk.CTkLabel(
            card, text="--",
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold"),
            text_color=COLORS['primary'],
        )
        self._brightness_label.pack()

        ctk.CTkSlider(
            card,
            from_=BRIGHTNESS_MIN, to=BRIGHTNESS_MAX,
            variable=self._slider_var,
            command=self._on_slider,
            width=680, height=36,
            button_length=40,
            progress_color=COLORS['primary'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['secondary'],
        ).pack(padx=20, pady=(4, 14))

        # ── Niveles rápidos ──
        quick = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        quick.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            quick, text="Niveles rápidos",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(pady=(8, 4))

        row = ctk.CTkFrame(quick, fg_color="transparent")
        row.pack(pady=(0, 10))
        for label, value in QUICK_LEVELS:
            make_futuristic_button(
                row, text=label,
                command=lambda v=value: self._set_quick(v),
                width=14, height=8, font_size=14,
            ).pack(side="left", padx=6)

        # ── ON / OFF ──
        toggle = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        toggle.pack(fill="x", padx=10, pady=4)

        tog_row = ctk.CTkFrame(toggle, fg_color="transparent")
        tog_row.pack(pady=10)

        make_futuristic_button(
            tog_row, text="🌕 Encender",
            command=self._screen_on,
            width=16, height=8, font_size=16,
        ).pack(side="left", padx=10)

        make_futuristic_button(
            tog_row, text="🌑 Apagar",
            command=self._screen_off,
            width=16, height=8, font_size=16,
        ).pack(side="left", padx=10)

        # ── Modo ahorro ──
        dim = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        dim.pack(fill="x", padx=10, pady=4)

        dim_row = ctk.CTkFrame(dim, fg_color="transparent")
        dim_row.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(
            dim_row,
            text="Dim automático  (2 min → 20%  |  4 min → apagado):",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(side="left", padx=(0, 10))

        self._dim_switch = ctk.CTkSwitch(
            dim_row, text="",
            command=self._toggle_dim,
            width=60, height=30,
            switch_width=60, switch_height=30,
            progress_color=COLORS['primary'],
        )
        self._dim_switch.pack(side="left")

        self._refresh()

    # ── Loop de actualización con banner ──────────────────────────────────────

    def _update(self):
        if not self.winfo_exists():
            return

        if not self.display_service._running:
            if not self._banner_shown:
                for w in self._inner.winfo_children():
                    w.destroy()
                StyleManager.show_service_stopped_banner(self._inner, "Display Service")
                self._banner_shown = True
        else:
            if self._banner_shown:
                self._banner_shown = False
                for w in self._inner.winfo_children():
                    w.destroy()
                self._build_content(self._inner)

        self.after(UPDATE_MS, self._update)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_slider(self, value):
        self.display_service.set_brightness(int(value))
        self._refresh()

    def _set_quick(self, value):
        self.display_service.set_brightness(value)
        self._slider_var.set(value)
        self._refresh()

    def _screen_on(self):
        self.display_service.screen_on()
        self._refresh()

    def _screen_off(self):
        self.display_service.screen_off()
        self._refresh()

    def _toggle_dim(self):
        if self._dim_switch.get():
            self.display_service.enable_dim_on_idle()
        else:
            self.display_service.disable_dim_on_idle()

    def _refresh(self):
        if not self.display_service.is_available():
            return
        if not hasattr(self, "_brightness_label"):
            return
        pct = self.display_service.get_brightness()
        self._brightness_label.configure(text=f"{pct}%")
        self._slider_var.set(pct)
