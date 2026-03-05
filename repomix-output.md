This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: ui/windows/button_manager_window.py
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)
</notes>

</file_summary>

<directory_structure>
ui/
  windows/
    button_manager_window.py
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path="ui/windows/button_manager_window.py">
"""
Ventana de gestión de visibilidad de botones del menú principal.
Permite activar/desactivar qué botones aparecen en el dashboard.
Los cambios son inmediatos en la UI y se persisten con "Guardar predeterminado".
"""
import customtkinter as ctk
import config.button_labels as BL
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import custom_msgbox
from utils.logger import get_logger

logger = get_logger(__name__)

# Fuente única de verdad: clave JSON → constante BL.*
# El orden determina cómo aparecen en la lista.
_BTN_LABELS = {
    "hardware_info":        BL.HARDWARE_INFO,
    "fan_control":          BL.FAN_CONTROL,
    "led_window":           BL.LED_RGB,
    "monitor_window":       BL.MONITOR_PLACA,
    "network_window":       BL.MONITOR_RED,
    "usb_window":           BL.MONITOR_USB,
    "disk_window":          BL.MONITOR_DISCO,
    "launchers":            BL.LANZADORES,
    "process_window":       BL.PROCESOS,
    "service_window":       BL.SERVICIOS,
    "services_manager":     BL.SERVICIOS_DASH,
    "crontab_window":       BL.CRONTAB,
    "history_window":       BL.HISTORICO,
    "update_window":        BL.ACTUALIZACIONES,
    "homebridge":           BL.HOMEBRIDGE,
    "log_viewer":           BL.VISOR_LOGS,
    "network_local":        BL.RED_LOCAL,
    "pihole":               BL.PIHOLE,
    "vpn_window":           BL.VPN,
    "ssh_window":           BL.SSH,
    "wifi_window":          BL.WIFI,
    "alert_history":        BL.HISTORIAL_ALERTAS,
    "display_window":       BL.BRILLO,
    "overview":             BL.RESUMEN,
    "camera_window":        BL.CAMARA,
    "theme_selector":       BL.TEMA,
    "config_editor_window": BL.CONFIG,
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
            text=f"{Icons.SAVE} Guardar predeterminado",
            command=self._save,
            width=28, height=8, font_size=15,
        ).pack(side="left", padx=5)

        make_futuristic_button(
            bottom,
            text=f"{Icons.CHECK} Activar todos",
            command=self._enable_all,
            width=18, height=8, font_size=15,
        ).pack(side="left", padx=5)

        make_futuristic_button(
            bottom,
            text=f"{Icons.CROSS} Desactivar todos",
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
        custom_msgbox(
            parent=self,
            text=f"{Icons.SAVE}  Configuración guardada\n\n"
                 f"{Icons.CHECK}  Los botones activos se aplicarán\n"
                 f"     al reiniciar el dashboard.",
            title="Guardado",
        )
</file>

</files>
