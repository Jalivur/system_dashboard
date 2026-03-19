import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR, UPDATE_MS, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets.dialogs import terminal_dialog
from utils import SystemUtils


class UpdatesWindow(ctk.CTkToplevel):
    """Ventana de control de actualizaciones del sistema"""

    def __init__(self, parent, update_monitor):
        super().__init__(parent)
        self.system_utils = SystemUtils()
        self._monitor = update_monitor
        self._polling = False
        self._banner_shown = False

        self.title(f"{Icons.ACTUALIZACIONES} Actualizaciones del Sistema")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")

        self._create_ui()
        self._update()

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title=f"{Icons.ACTUALIZACIONES} ACTUALIZACIONES DEL SISTEMA", on_close=self.destroy)

        # Frame de contenido que se puede limpiar para el banner
        self._content = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        self._content.pack(fill="both", expand=True, padx=20, pady=10)

        self._build_content(self._content)

    def _build_content(self, parent):
        """Construye el contenido normal de la ventana."""
        # Icono
        self._status_icon = ctk.CTkLabel(parent, text=Icons.UPDATE_SCRIPT, font=(FONT_FAMILY, 60))
        self._status_icon.pack(pady=(10, 5))

        # Labels
        self._status_label = ctk.CTkLabel(
            parent, text="Verificando...",
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold")
        )
        self._status_label.pack()

        self._info_label = ctk.CTkLabel(
            parent, text="Estado de los paquetes",
            text_color=COLORS['text_dim'], font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        self._info_label.pack(pady=5)

        # Frame para botones
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=(10, 20))

        self._search_btn = make_futuristic_button(
            btn_frame, text=f"{Icons.SEARCH} Buscar",
            command=lambda: self._refresh_status(force=True), width=12
        )
        self._search_btn.pack(side="left", padx=5, expand=True)

        self._update_btn = make_futuristic_button(
            btn_frame, text=f"{Icons.UPDATE_SCRIPT}  Instalar",
            command=self._execute_update_script, width=12
        )
        self._update_btn.pack(side="left", padx=5, expand=True)
        self._update_btn.configure(state="disabled")

        close_btn = make_futuristic_button(
            btn_frame, text=f"{Icons.CROSS} Cerrar",
            command=self.destroy, width=12
        )
        close_btn.pack(side="left", padx=5, expand=True)

        self._refresh_status(force=False)

    # ── Loop de actualización con banner ──────────────────────────────────────

    def _update(self):
        if not self.winfo_exists():
            return

        if not self._monitor.is_running():
            if not self._banner_shown:
                for w in self._content.winfo_children():
                    w.destroy()
                StyleManager.show_service_stopped_banner(self._content, "Update Monitor")
                self._banner_shown = True
        else:
            if self._banner_shown:
                self._banner_shown = False
                for w in self._content.winfo_children():
                    w.destroy()
                self._build_content(self._content)

        self.after(UPDATE_MS, self._update)

    # ── Lógica de actualizaciones ─────────────────────────────────────────────

    def _refresh_status(self, force=False):
        """Consulta el estado de actualizaciones"""
        if not self._monitor.is_running():
            return
        if force:
            self._update_btn.configure(state="disabled")
            self._polling = False
            self._status_label.configure(text=f"{Icons.SEARCH} Buscando...", text_color=COLORS['warning'])
            self.update_idletasks()

        res = self._monitor.check_updates(force=force)

        if res['status'] == "Unknown":
            self._status_label.configure(text="Comprobando...", text_color=COLORS['text_dim'])
            self._info_label.configure(text="Verificación inicial en curso")
            self._status_icon.configure(text_color=COLORS['text_dim'])
            self._update_btn.configure(state="disabled")
            if not self._polling:
                self._polling = True
                self._poll_until_ready()
            return

        self._polling = False
        color = COLORS['success'] if res['pending'] == 0 else COLORS['warning']
        self._status_label.configure(text=res['status'], text_color=color)
        self._info_label.configure(text=res['message'])
        self._status_icon.configure(text_color=color)
        self._update_btn.configure(state="normal" if res['pending'] > 0 else "disabled")

    def _poll_until_ready(self):
        """Reintenta _refresh_status cada 2s mientras el resultado sea Unknown"""
        if not self._polling:
            return
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return
        res = self._monitor.check_updates(force=False)
        if res['status'] != "Unknown":
            self._refresh_status(force=False)
        else:
            self.after(2000, self._poll_until_ready)

    def _execute_update_script(self):
        """Lanza el script de terminal y refresca al terminar"""
        script_path = str(SCRIPTS_DIR / "update.sh")

        def al_terminar_actualizacion():
            self._refresh_status(force=True)

        terminal_dialog(
            self,
            script_path,
            f"{Icons.ACTUALIZACIONES} CONSOLA DE ACTUALIZACIÓN",
            on_close=al_terminar_actualizacion
        )
