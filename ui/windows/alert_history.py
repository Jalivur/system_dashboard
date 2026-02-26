"""
Ventana de historial de alertas disparadas por AlertService.
Lee data/alert_history.json y muestra las entradas con colores por nivel.
"""
import customtkinter as ctk
from datetime import datetime
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from ui.styles import make_window_header, make_futuristic_button, StyleManager
from ui.widgets import confirm_dialog
from utils.logger import get_logger

logger = get_logger(__name__)

# Colores por nivel (misma paleta que LogViewer)
LEVEL_COLORS = {
    "warn": "#FFA500",
    "crit": "#FF4444",
}

# Etiqueta legible por clave
KEY_LABELS = {
    "temp_warn":      "🌡️ Temperatura — aviso",
    "temp_crit":      "🌡️ Temperatura — crítico",
    "cpu_warn":       "🔥 CPU — aviso",
    "cpu_crit":       "🔥 CPU — crítico",
    "ram_warn":       "💾 RAM — aviso",
    "ram_crit":       "💾 RAM — crítico",
    "disk_warn":      "💿 Disco — aviso",
    "disk_crit":      "💿 Disco — crítico",
    "services_failed": "⚠️ Servicios caídos",
}


class AlertHistoryWindow(ctk.CTkToplevel):
    """Ventana de historial de alertas."""

    def __init__(self, parent, alert_service):
        super().__init__(parent)
        self.alert_service = alert_service

        self.title("Historial de Alertas")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._create_ui()
        self._load()
        logger.info("[AlertHistoryWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="HISTORIAL DE ALERTAS", on_close=self.destroy)

        # Área scrollable
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
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

        self._list_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window(
            (0, 0), window=self._list_frame, anchor="nw", width=DSI_WIDTH - 50)
        self._list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Barra inferior
        bar = ctk.CTkFrame(main, fg_color="transparent")
        bar.pack(fill="x", padx=5, pady=(0, 4))

        self._count_label = ctk.CTkLabel(
            bar, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'])
        self._count_label.pack(side="left", padx=8)

        make_futuristic_button(
            bar, text="↺ Actualizar", command=self._load,
            width=11, height=5, font_size=14
        ).pack(side="right", padx=4)

        make_futuristic_button(
            bar, text="🗑 Borrar todo", command=self._confirm_clear,
            width=12, height=5, font_size=14
        ).pack(side="right", padx=4)

    # ── Carga ─────────────────────────────────────────────────────────────────

    def _load(self):
        """Lee el historial y redibuja la lista."""
        for w in self._list_frame.winfo_children():
            w.destroy()

        history = self.alert_service.get_history()

        if not history:
            ctk.CTkLabel(
                self._list_frame,
                text="No hay alertas registradas.",
                text_color=COLORS['text_dim'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
            ).pack(pady=40)
            self._count_label.configure(text="0 alertas")
            return

        # Mostrar en orden inverso (más reciente primero)
        for entry in reversed(history):
            self._create_entry_card(entry)

        total = len(history)
        self._count_label.configure(text=f"{total} alerta{'s' if total != 1 else ''}")

    def _create_entry_card(self, entry: dict):
        """Crea una tarjeta para una entrada del historial."""
        level  = entry.get("level", "warn")
        key    = entry.get("key", "")
        color  = LEVEL_COLORS.get(level, COLORS['text'])
        label  = KEY_LABELS.get(key, key)
        value  = entry.get("value", 0)
        unit   = entry.get("unit", "")
        ts_str = entry.get("ts", "")

        card = ctk.CTkFrame(
            self._list_frame,
            fg_color=COLORS['bg_dark'],
            corner_radius=6,
        )
        card.pack(fill="x", padx=6, pady=3)

        # Franja de color a la izquierda
        ctk.CTkFrame(card, fg_color=color, width=4, corner_radius=0).pack(
            side="left", fill="y", padx=(0, 8))

        # Contenido
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="x", expand=True, pady=6)

        # Fila superior: etiqueta + valor
        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top, text=label,
            text_color=color,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=f"{value}{unit}",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="e",
        ).pack(side="right", padx=12)

        # Fila inferior: timestamp
        ctk.CTkLabel(
            content, text=ts_str,
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="w",
        ).pack(fill="x")

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _confirm_clear(self):
        confirm_dialog(
            parent=self,
            text="¿Borrar todo el historial de alertas?\n\nEsta acción no se puede deshacer.",
            title="🗑 Borrar Historial",
            on_confirm=self._clear,
        )

    def _clear(self):
        self.alert_service.clear_history()
        self._load()