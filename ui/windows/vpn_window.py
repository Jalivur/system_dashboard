"""
Ventana de gestión de conexiones VPN dual (OpenVPN + WireGuard).

Muestra el estado en tiempo real de ambas VPNs y permite conectar/desconectar
usando los scripts del usuario. Al conectar pregunta con cuál VPN; al
desconectar, si hay más de una activa también pregunta.
"""
import os
import customtkinter as ctk

from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR,
    Icons, UPDATE_MS,
)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets.dialogs import terminal_dialog, custom_msgbox
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Scripts por VPN ───────────────────────────────────────────────────────────
_SCRIPTS = {
    "openvpn": {
        "connect":    str(SCRIPTS_DIR / "conectar_openvpn.sh"),
        "disconnect": str(SCRIPTS_DIR / "desconectar_openvpn.sh"),
        "label":      "OpenVPN",
        "iface":      "tun0",
    },
    "wireguard": {
        "connect":    str(SCRIPTS_DIR / "conectar_wireguard.sh"),
        "disconnect": str(SCRIPTS_DIR / "desconectar_wireguard.sh"),
        "label":      "WireGuard",
        "iface":      "wg0",
    },
}


class VpnWindow(ctk.CTkToplevel):
    """
    Ventana de gestión de VPN dual.

    Muestra una tarjeta de estado por cada VPN y permite conectar/desconectar
    con selección de proveedor cuando es necesario.

    Args:
        parent: Ventana padre CTkToplevel de la aplicación principal.
        vpn_monitor: Instancia de VpnMonitor ya iniciada.
    """

    def __init__(self, parent, vpn_monitor):
        """
        Inicializa la ventana de gestión de VPN.

        Args:
            parent: Ventana padre.
            vpn_monitor: Instancia de VpnMonitor ya iniciada.
        """
        super().__init__(parent)
        self._vpn_monitor = vpn_monitor

        self.configure(fg_color=COLORS["bg_medium"])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        # Widgets actualizables por VPN — clave = "openvpn" | "wireguard"
        self._cards: dict[str, dict] = {}
        
        self._btn_connect = None

        self._create_ui()
        self._update()
        logger.info("[VpnWindow] Ventana abierta")

    def destroy(self):
        """
        Destruye la ventana de forma controlada.

        Returns:
            None
        """
        logger.info("[VpnWindow] Ventana cerrada")
        super().destroy()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self) -> None:
        """
        Construye el layout: header + scroll con tarjetas de estado + botones.

        Returns:
            None
        """
        main = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title=f"{Icons.VPN}  GESTOR VPN", on_close=self.destroy)

        scroll_container = ctk.CTkFrame(main, fg_color=COLORS["bg_medium"])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS["bg_medium"], highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30,
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        self._inner = ctk.CTkFrame(canvas, fg_color=COLORS["bg_medium"])
        canvas.create_window((0, 0), window=self._inner, anchor="nw", width=DSI_WIDTH - 50)
        self._inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        # ── Tarjetas de estado (una por VPN) ──────────────────────────────────
        for key, cfg in _SCRIPTS.items():
            self._cards[key] = self._build_vpn_card(self._inner, cfg["label"], cfg["iface"])

        # ── Botones de acción globales ─────────────────────────────────────────
        action_card = ctk.CTkFrame(self._inner, fg_color=COLORS["bg_dark"], corner_radius=8)
        action_card.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            action_card,
            text="Acciones",
            font=(FONT_FAMILY, FONT_SIZES["small"]),
            text_color=COLORS["text_dim"],
            anchor="w",
        ).pack(fill="x", padx=14, pady=(10, 6))

        btn_row = ctk.CTkFrame(action_card, fg_color="transparent")
        btn_row.pack(pady=(0, 12))

        self._btn_connect = make_futuristic_button(
            btn_row,
            text=f"{Icons.VPN}  Conectar",
            command=self._on_connect,
            width=18, height=10, font_size=18,
        )
        self._btn_connect.pack(side="left", padx=12)

        make_futuristic_button(
            btn_row,
            text=f"{Icons.UNLOCK}  Desconectar",
            command=self._on_disconnect,
            width=18, height=10, font_size=18,
        ).pack(side="left", padx=12)

        # ── Nota sobre scripts ─────────────────────────────────────────────────
        note_frame = ctk.CTkFrame(self._inner, fg_color="transparent")
        note_frame.pack(fill="x", padx=14, pady=(4, 8))

        ctk.CTkLabel(
            note_frame,
            text=f"Conectar: conectar_openvpn.sh · conectar_wireguard.sh\n Desconectar: desconectar_openvpn.sh · desconectar_wireguard.sh",
            font=(FONT_FAMILY, FONT_SIZES["small"]),
            text_color=COLORS["text_dim"],
            anchor="w",
        ).pack(fill="x")

    def _build_vpn_card(self, parent, label: str, iface: str) -> dict:
        """
        Construye una tarjeta de estado para una VPN concreta.

        Args:
            parent: Widget padre donde insertar la tarjeta.
            label (str): Nombre visible de la VPN (ej. "OpenVPN").
            iface (str): Nombre de la interfaz (ej. "tun0").

        Returns:
            dict: Referencias a los widgets actualizables de la tarjeta.
        """
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_dark"], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(8, 4))

        # Cabecera de tarjeta
        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            header_row,
            text=label,
            font=(FONT_FAMILY, FONT_SIZES["small"], "bold"),
            text_color=COLORS["primary"],
            anchor="w",
        ).pack(side="left")

        iface_lbl = ctk.CTkLabel(
            header_row,
            text=f"({iface})",
            font=(FONT_FAMILY, FONT_SIZES["small"]),
            text_color=COLORS["text_dim"],
            anchor="e",
        )
        iface_lbl.pack(side="right")

        # Indicador de estado
        indicator_row = ctk.CTkFrame(card, fg_color="transparent")
        indicator_row.pack(fill="x", padx=14, pady=(0, 10))

        dot = ctk.CTkLabel(
            indicator_row,
            text="●",
            font=(FONT_FAMILY, 30, "bold"),
            text_color=COLORS["text_dim"],
        )
        dot.pack(side="left", padx=(0, 10))

        text_col = ctk.CTkFrame(indicator_row, fg_color="transparent")
        text_col.pack(side="left", fill="x", expand=True)

        status_text = ctk.CTkLabel(
            text_col,
            text="Comprobando...",
            font=(FONT_FAMILY, FONT_SIZES["large"], "bold"),
            text_color=COLORS["text"],
            anchor="w",
        )
        status_text.pack(fill="x")

        ip_lbl = ctk.CTkLabel(
            text_col,
            text="",
            font=(FONT_FAMILY, FONT_SIZES["small"]),
            text_color=COLORS["text_dim"],
            anchor="w",
        )
        ip_lbl.pack(fill="x")

        return {
            "dot":         dot,
            "status_text": status_text,
            "ip_lbl":      ip_lbl,
        }

    # ── Actualización ─────────────────────────────────────────────────────────

    def _update(self) -> None:
        """
        Actualiza el estado visual de todas las tarjetas VPN.

        Returns:
            None
        """
        if not self.winfo_exists():
            return

        if not self._vpn_monitor.is_running():
            StyleManager.show_service_stopped_banner(self._inner, "VPN Monitor")
            self.after(UPDATE_MS, self._update)
            return

        try:
            status = self._vpn_monitor.get_status()
            for key, card in self._cards.items():
                vpn = status.get(key, {})
                connected = vpn.get("connected", False)
                ip        = vpn.get("ip", "")

                if connected:
                    card["dot"].configure(text_color="#00CC66")
                    card["status_text"].configure(text="CONECTADA", text_color="#00CC66")
                    card["ip_lbl"].configure(text=f"IP: {ip}" if ip else "IP: --")
                else:
                    card["dot"].configure(text_color=COLORS["danger"])
                    card["status_text"].configure(text="DESCONECTADA", text_color=COLORS["danger"])
                    card["ip_lbl"].configure(text="Sin conexión")
            # Deshabilitar Conectar si alguna VPN ya está activa
            any_connected = any(v.get("connected") for v in status.values())
            if self._btn_connect:
                self._btn_connect.configure(
                    state="disabled" if any_connected else "normal"
                )

        except Exception as e:
            logger.error("[VpnWindow] Error en _update: %s", e)

        self.after(UPDATE_MS, self._update)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _on_connect(self) -> None:
        """
        Gestiona el botón Conectar.

        Si ninguna VPN está activa, abre el selector de VPN.
        Si ya hay una activa, informa al usuario.

        Returns:
            None
        """
        if not self._vpn_monitor.is_running():
            return

        status = self._vpn_monitor.get_status()
        connected_keys = [k for k, v in status.items() if v["connected"]]

        if len(connected_keys) == len(_SCRIPTS):
            custom_msgbox(self, "Ambas VPNs ya están conectadas.", "VPN")
            return

        # Filtrar solo las que están desconectadas para ofrecer como opción
        available = [k for k in _SCRIPTS if k not in connected_keys]
        self._open_vpn_selector(
            title=f"{Icons.VPN}  Selecciona VPN a conectar",
            keys=available,
            action="connect",
        )

    def _on_disconnect(self) -> None:
        """
        Gestiona el botón Desconectar.

        Si solo hay una activa la desconecta directamente.
        Si hay más de una activa abre el selector.
        Si ninguna está activa informa al usuario.

        Returns:
            None
        """
        if not self._vpn_monitor.is_running():
            return

        status = self._vpn_monitor.get_status()
        connected_keys = [k for k, v in status.items() if v["connected"]]

        if not connected_keys:
            custom_msgbox(self, "No hay ninguna VPN conectada.", "VPN")
            return

        if len(connected_keys) == 1:
            # Solo una activa — desconectar directamente sin preguntar
            self._run_vpn_action(connected_keys[0], "disconnect")
            return

        # Más de una activa — preguntar cuál parar
        self._open_vpn_selector(
            title=f"{Icons.UNLOCK}  Selecciona VPN a desconectar",
            keys=connected_keys,
            action="disconnect",
        )

    def _open_vpn_selector(self, title: str, keys: list, action: str) -> None:
        """
        Abre un diálogo modal con un botón por VPN disponible.

        Args:
            title (str): Título del diálogo.
            keys (list): Claves de VPN a mostrar como opciones ("openvpn", "wireguard").
            action (str): Acción a ejecutar ("connect" | "disconnect").

        Returns:
            None
        """
        popup = ctk.CTkToplevel(self)
        popup.transient(self)
        popup.overrideredirect(True)
        popup.configure(fg_color=COLORS["bg_dark"])

        w, h = 420, 200
        x = self.winfo_x() + (self.winfo_width() // 2) - (w // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")

        frame = ctk.CTkFrame(
            popup,
            fg_color=COLORS["bg_dark"],
            border_width=2,
            border_color=COLORS["primary"],
        )
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(
            frame,
            text=title,
            font=(FONT_FAMILY, FONT_SIZES["small"], "bold"),
            text_color=COLORS["secondary"],
        ).pack(pady=(14, 10))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(pady=8)

        def _make_handler(key):
            def _handler():
                popup.destroy()
                self._run_vpn_action(key, action)
            return _handler

        for key in keys:
            make_futuristic_button(
                btn_row,
                text=_SCRIPTS[key]["label"],
                command=_make_handler(key),
                width=16, height=10, font_size=16,
            ).pack(side="left", padx=10)

        make_futuristic_button(
            frame,
            text="Cancelar",
            command=popup.destroy,
            width=12, height=8, font_size=14,
        ).pack(pady=(4, 12))

        popup.after(150, popup.focus_set)

    def _run_vpn_action(self, key: str, action: str) -> None:
        """
        Ejecuta el script de conexión o desconexión para la VPN indicada.

        Args:
            key (str): Clave de VPN ("openvpn" | "wireguard").
            action (str): Acción ("connect" | "disconnect").

        Returns:
            None
        """
        cfg    = _SCRIPTS[key]
        script = cfg[action]
        label  = cfg["label"]

        if not os.path.exists(script):
            custom_msgbox(
                self,
                f"Script no encontrado:\n{script}\n\nCrea el script en la carpeta scripts/",
                "Error",
            )
            return

        if action == "connect":
            title = f"{Icons.VPN}  CONECTANDO {label.upper()}..."
        else:
            title = f"{Icons.UNLOCK}  DESCONECTANDO {label.upper()}..."

        terminal_dialog(
            parent=self,
            script_path=script,
            title=title,
            on_close=self._on_action_done,
        )

    def _on_action_done(self) -> None:
        """
        Callback ejecutado al cerrar el terminal dialog.

        Fuerza un sondeo inmediato para reflejar el nuevo estado en la UI.

        Returns:
            None
        """
        self._vpn_monitor.force_poll()
        self.after(2000, self._update)
