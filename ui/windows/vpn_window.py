"""
Ventana de gestión de conexiones VPN.
Muestra el estado en tiempo real y permite conectar/desconectar
usando los scripts del usuario.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR
, Icons)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets.dialogs import terminal_dialog
from utils.logger import get_logger
import os

logger = get_logger(__name__)

# Rutas de los scripts (deben coincidir con los de LAUNCHERS en settings.py)
_SCRIPT_CONNECT    = str(SCRIPTS_DIR / "conectar_vpn.sh")
_SCRIPT_DISCONNECT = str(SCRIPTS_DIR / "desconectar_vpn.sh")

# Intervalo de refresco del estado en ms
UPDATE_MS = 3000


class VpnWindow(ctk.CTkToplevel):
    """Ventana de gestión de VPN."""

    def __init__(self, parent, vpn_monitor):
        super().__init__(parent)
        self.vpn_monitor = vpn_monitor

        self.title("Gestor VPN")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._running = True
        self._widgets = {}

        self._create_ui()
        self._update()
        logger.info("[VpnWindow] Ventana abierta")

    def destroy(self):
        self._running = False
        super().destroy()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="GESTOR VPN", on_close=self.destroy)
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS["bg_medium"])
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

        self.inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window(
            (0, 0), window=self.inner,
            anchor="nw", width=DSI_WIDTH - 50)
        self.inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        # ── Tarjeta de estado ──
        status_card = ctk.CTkFrame(self.inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        status_card.pack(fill="x", padx=10, pady=(8, 4))
        self._content_frame = status_card
        ctk.CTkLabel(
            status_card,
            text="Estado de la conexión",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(fill="x", padx=14, pady=(10, 4))

        # Indicador de estado grande
        indicator_row = ctk.CTkFrame(status_card, fg_color="transparent")
        indicator_row.pack(fill="x", padx=14, pady=(0, 6))

        self._widgets['status_dot'] = ctk.CTkLabel(
            indicator_row,
            text="●",
            font=(FONT_FAMILY, 36, "bold"),
            text_color=COLORS['text_dim'],
        )
        self._widgets['status_dot'].pack(side="left", padx=(0, 10))

        status_text_col = ctk.CTkFrame(indicator_row, fg_color="transparent")
        status_text_col.pack(side="left", fill="x", expand=True)

        self._widgets['status_text'] = ctk.CTkLabel(
            status_text_col,
            text="Comprobando...",
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold"),
            text_color=COLORS['text'],
            anchor="w",
        )
        self._widgets['status_text'].pack(fill="x")

        self._widgets['status_detail'] = ctk.CTkLabel(
            status_text_col,
            text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        )
        self._widgets['status_detail'].pack(fill="x")

        # ── Botones de acción ──
        action_card = ctk.CTkFrame(self.inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        action_card.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            action_card,
            text="Acciones",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(fill="x", padx=14, pady=(10, 6))

        btn_row = ctk.CTkFrame(action_card, fg_color="transparent")
        btn_row.pack(pady=(0, 12))

        make_futuristic_button(
            btn_row,
            text="" + Icons.VPN + " Conectar VPN",
            command=self._connect,
            width=18, height=10, font_size=18,
        ).pack(side="left", padx=12)

        make_futuristic_button(
            btn_row,
            text="" + Icons.UNLOCK + " Desconectar",
            command=self._disconnect,
            width=18, height=10, font_size=18,
        ).pack(side="left", padx=12)

        # ── Info de interfaz ──
        info_card = ctk.CTkFrame(self.inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        info_card.pack(fill="x", padx=10, pady=4)

        info_inner = ctk.CTkFrame(info_card, fg_color="transparent")
        info_inner.pack(fill="x", padx=14, pady=10)

        for key, label in [("iface_label", "Interfaz"), ("ip_label", "IP VPN")]:
            col = ctk.CTkFrame(info_inner, fg_color="transparent")
            col.pack(side="left", expand=True)

            ctk.CTkLabel(
                col,
                text=label,
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
            ).pack()

            lbl = ctk.CTkLabel(
                col,
                text="--",
                font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
                text_color=COLORS['primary'],
            )
            lbl.pack()
            self._widgets[key] = lbl

        # ── Nota sobre scripts ──
        note_frame = ctk.CTkFrame(self.inner, fg_color="transparent")
        note_frame.pack(fill="x", padx=14, pady=(4, 0))

        ctk.CTkLabel(
            note_frame,
            text=f"Scripts: conectar_vpn.sh / desconectar_vpn.sh",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(fill="x")

    # ── Actualización ─────────────────────────────────────────────────────────

    def _update(self):
        if not self.winfo_exists():
            return
        
        if not self.vpn_monitor._running:
            StyleManager.show_service_stopped_banner(self._content_frame, "VPN Monitor")
            self.after(UPDATE_MS, self._update)
            return
        
        try:
            status = self.vpn_monitor.get_status()
            connected = status['connected']
            ip        = status['ip']
            iface     = status['interface']

            if connected:
                self._widgets['status_dot'].configure(text_color="#00CC66")
                self._widgets['status_text'].configure(
                    text="CONECTADA", text_color="#00CC66")
                self._widgets['status_detail'].configure(text="VPN activa")
            else:
                self._widgets['status_dot'].configure(text_color=COLORS['danger'])
                self._widgets['status_text'].configure(
                    text="DESCONECTADA", text_color=COLORS['danger'])
                self._widgets['status_detail'].configure(text="Sin conexión VPN")

            self._widgets['iface_label'].configure(
                text=iface if connected else "--",
                text_color=COLORS['primary'] if connected else COLORS['text_dim']
            )
            self._widgets['ip_label'].configure(
                text=ip if ip else "--",
                text_color=COLORS['primary'] if ip else COLORS['text_dim']
            )
        except Exception as e:
            logger.error("[VpnWindow] Error en _update: %s", e)

        self.after(UPDATE_MS, self._update)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _connect(self):
        """Ejecuta conectar_vpn.sh con terminal en vivo."""
        if not self.vpn_monitor._running:
            return

        if not os.path.exists(_SCRIPT_CONNECT):
            from ui.widgets.dialogs import custom_msgbox
            custom_msgbox(
                self,
                f"Script no encontrado:\n{_SCRIPT_CONNECT}\n\n"
                "Crea el script en la carpeta scripts/",
                "Error"
            )
            return
        terminal_dialog(
            parent=self,
            script_path=_SCRIPT_CONNECT,
            title="" + Icons.VPN + " CONECTANDO VPN...",
            on_close=self._on_action_done,
        )

    def _disconnect(self):
        """Ejecuta desconectar_vpn.sh con terminal en vivo."""
        if not self.vpn_monitor._running:
            return
        
        if not os.path.exists(_SCRIPT_DISCONNECT):
            from ui.widgets.dialogs import custom_msgbox
            custom_msgbox(
                self,
                f"Script no encontrado:\n{_SCRIPT_DISCONNECT}\n\n"
                "Crea el script en la carpeta scripts/",
                "Error"
            )
            return
        terminal_dialog(
            parent=self,
            script_path=_SCRIPT_DISCONNECT,
            title="" + Icons.UNLOCK + " DESCONECTANDO VPN...",
            on_close=self._on_action_done,
        )

    def _on_action_done(self):
        """Fuerza sondeo inmediato tras conectar/desconectar."""
        self.vpn_monitor.force_poll()
        # Pequeño delay para que el sondeo tenga tiempo de completarse
        self.after(2000, self._update)
