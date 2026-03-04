"""
Ventana de gestión de visibilidad de botones del menú principal.
Permite activar/desactivar qué botones aparecen en el dashboard.
Los cambios son inmediatos en la UI y se persisten con "Guardar predeterminado".
"""
import customtkinter as ctk
import config.button_labels as BL
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger

logger = get_logger(__name__)

# Fuente única de verdad: clave JSON → constante BL.*
# El orden determina cómo aparecen en la lista.
_BTN_LABELS = {
    "hardware_info":    BL.HARDWARE_INFO,
    "fan_control":      BL.FAN_CONTROL,
    "led_window":       BL.LED_RGB,
    "monitor_window":   BL.MONITOR_PLACA,
    "network_window":   BL.MONITOR_RED,
    "usb_window":       BL.MONITOR_USB,
    "disk_window":      BL.MONITOR_DISCO,
    "launchers":        BL.LANZADORES,
    "process_window":   BL.PROCESOS,
    "service_window":   BL.SERVICIOS,
    "services_manager": BL.SERVICIOS_DASH,
    "crontab_window":   BL.CRONTAB,
    "history_window":   BL.HISTORICO,
    "update_window":    BL.ACTUALIZACIONES,
    "homebridge":       BL.HOMEBRIDGE,
    "log_viewer":       BL.VISOR_LOGS,
    "network_local":    BL.RED_LOCAL,
    "pihole":           BL.PIHOLE,
    "vpn_window":       BL.VPN,
    "ssh_window":       BL.SSH,
    "wifi_window":      BL.WIFI,
    "alert_history":    BL.HISTORIAL_ALERTAS,
    "display_window":   BL.BRILLO,
    "overview":         BL.RESUMEN,
    "camera_window":    BL.CAMARA,
    "theme_selector":   BL.TEMA,
}


class ButtonManagerWindow(ctk.CTkToplevel):
    """Ventana para gestionar la visibilidad de botones del menú principal."""

    def __init__(self, parent, registry, window_manager):
        """
        Args:
            parent:         ventana padre (root)
            registry:       ServiceRegistry (para leer/guardar config ui)
            window_manager: WindowManager activo en MainWindow
        """
        super().__init__(parent)
        self.registry       = registry
        self.window_manager = window_manager

        self.title("Gestor de Botones")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._switches: dict = {}

        self._create_ui()
        logger.info("[ButtonManagerWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="GESTOR DE BOTONES", on_close=self.destroy)

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

        ctk.CTkLabel(
            inner,
            text="Activa o desactiva qué botones aparecen en el menú principal.\n"
                 "Los cambios son inmediatos. Usa 'Guardar predeterminado' para que\n"
                 "persistan al reiniciar el dashboard.",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            justify="left",
        ).pack(anchor="w", padx=14, pady=(6, 10))

        for key, label in _BTN_LABELS.items():
            enabled = self.registry.ui_enabled(key)
            self._create_row(inner, key, label, enabled)

        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", padx=10, pady=(0, 8))

        make_futuristic_button(
            bottom,
            text="💾 Guardar predeterminado",
            command=self._save,
            width=28, height=8, font_size=15,
        ).pack(side="left", padx=5)

        make_futuristic_button(
            bottom,
            text="✓ Activar todos",
            command=self._enable_all,
            width=18, height=8, font_size=15,
        ).pack(side="left", padx=5)

        make_futuristic_button(
            bottom,
            text="✕ Desactivar todos",
            command=self._disable_all,
            width=18, height=8, font_size=15,
        ).pack(side="left", padx=5)

    def _create_row(self, parent, key: str, label: str, enabled: bool):
        """Crea una fila con el nombre del botón y su switch ON/OFF."""
        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=6)
        row.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(
            row,
            text=label,
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text'],
            anchor="w",
        ).pack(side="left", padx=14, pady=10, expand=True, fill="x")

        switch = ctk.CTkSwitch(
            row,
            text="",
            command=lambda k=key: self._on_toggle(k),
            width=56, height=28,
            switch_width=56, switch_height=28,
            progress_color=COLORS['primary'],
        )
        switch.pack(side="right", padx=14, pady=10)

        if enabled:
            switch.select()
        else:
            switch.deselect()

        self._switches[key] = switch

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_toggle(self, key: str):
        """Aplica el cambio inmediatamente en la UI del menú principal."""
        enabled = bool(self._switches[key].get())
        if enabled:
            self.window_manager.show(key)
        else:
            self.window_manager.hide(key)
        logger.debug("[ButtonManagerWindow] %s → %s", key, "visible" if enabled else "oculto")

    def _enable_all(self):
        """Activa todos los switches y aplica los cambios."""
        for key, switch in self._switches.items():
            switch.select()
            self.window_manager.show(key)

    def _disable_all(self):
        """Desactiva todos los switches y aplica los cambios."""
        for key, switch in self._switches.items():
            switch.deselect()
            self.window_manager.hide(key)

    def _save(self):
        """Persiste el estado actual al JSON via registry.save_config()."""
        self.registry.save_config()
        logger.info("[ButtonManagerWindow] Configuración de botones guardada")
