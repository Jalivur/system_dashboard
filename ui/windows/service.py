"""
Ventana de monitor de servicios systemd
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.service_monitor import ServiceMonitor


class ServiceWindow(ctk.CTkToplevel):
    """Ventana de monitor de servicios"""

    def __init__(self, parent, service_monitor: ServiceMonitor):
        super().__init__(parent)

        self._service_monitor = service_monitor

        self._search_var    = ctk.StringVar(master=self)
        self._filter_var    = ctk.StringVar(master=self, value="all")
        self._update_paused = False
        self._update_job    = None

        self.title("Monitor de Servicios")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        self._create_ui()
        self._update()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(
            main,
            title="MONITOR DE SERVICIOS",
            on_close=self.destroy,
        )

        stats_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'])
        stats_bar.pack(fill="x", padx=5, pady=(0, 4))
        self._stats_label = ctk.CTkLabel(
            stats_bar,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self._stats_label.pack(pady=4, padx=10, anchor="w")

        self._create_controls(main)
        self._create_column_headers(main)

        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        self._content_frame = scroll_container

        max_height = DSI_HEIGHT - 300

        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=max_height
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        self._service_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self._service_frame, anchor="nw", width=DSI_WIDTH - 50)
        self._service_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)

        make_futuristic_button(
            bottom,
            text="Refrescar",
            command=self._force_update,
            width=15,
            height=6
        ).pack(side="left", padx=5)

    # ── Controles ─────────────────────────────────────────────────────────────

    def _create_controls(self, parent):
        controls = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        controls.pack(fill="x", padx=10, pady=5)

        search_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        search_frame.pack(side="left", padx=10, pady=10)

        ctk.CTkLabel(
            search_frame,
            text="Buscar:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self._search_var,
            width=200,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())

        filter_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        filter_frame.pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            filter_frame,
            text="Filtro:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))

        for filter_type, label in [
            ("all",      "Todos"),
            ("active",   "Activos"),
            ("inactive", "Inactivos"),
            ("failed",   "Fallidos"),
        ]:
            rb = ctk.CTkRadioButton(
                filter_frame,
                text=label,
                variable=self._filter_var,
                value=filter_type,
                command=self._on_filter_change,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=5)
            StyleManager.style_radiobutton_ctk(rb)

    def _create_column_headers(self, parent):
        headers = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'])
        headers.pack(fill="x", padx=10, pady=(5, 0))

        headers.grid_columnconfigure(0, weight=2, minsize=150)
        headers.grid_columnconfigure(1, weight=1, minsize=100)
        headers.grid_columnconfigure(2, weight=1, minsize=80)
        headers.grid_columnconfigure(3, weight=3, minsize=300)

        columns = [
            ("Servicio",  "name"),
            ("Estado",    "state"),
            ("Autostart", None),
            ("Acciones",  None),
        ]

        for i, (label, sort_key) in enumerate(columns):
            if sort_key:
                btn = ctk.CTkButton(
                    headers,
                    text=label,
                    command=lambda k=sort_key: self._on_sort_change(k),
                    fg_color=COLORS['bg_medium'],
                    hover_color=COLORS['bg_dark'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                    height=30
                )
            else:
                btn = ctk.CTkLabel(
                    headers,
                    text=label,
                    text_color=COLORS['text'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
                )

            btn.grid(row=0, column=i, sticky="ew", padx=2, pady=5)

    # ── Callbacks de UI ───────────────────────────────────────────────────────

    def _on_sort_change(self, column: str):
        self._update_paused = True
        
        self._service_monitor.toggle_sort(column)

        self._update_now()
        self.after(2000, self._resume_updates)

    def _on_filter_change(self):
        self._update_paused = True
        self._service_monitor.set_filter(self._filter_var.get())
        self._update_now()
        self.after(2000, self._resume_updates)

    def _on_search_change(self):
        self._update_paused = True

        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)

        self._search_timer = self.after(500, self._do_search)

    def _do_search(self):
        self._update_now()
        self.after(3000, self._resume_updates)

    def _resume_updates(self):
        self._update_paused = False

    def _force_update(self):
        self._update_paused = False
        self._update_now()

    # ── Bucle de actualización ────────────────────────────────────────────────

    def _update(self):
        """Bucle de actualización — winfo_exists siempre primero."""
        if not self.winfo_exists():
            return

        if not self._service_monitor.is_running():
            StyleManager.show_service_stopped_banner(self._content_frame, "Service Monitor")
            self._update_job = self.after(UPDATE_MS, self._update)
            return

        if self._update_paused:
            self._update_job = self.after(UPDATE_MS * 5, self._update)
            return

        self._update_now()
        self._update_job = self.after(UPDATE_MS * 5, self._update)

    def _update_now(self):
        if not self.winfo_exists():
            return

        stats = self._service_monitor.get_stats()
        self._stats_label.configure(
            text=(
                f"Total: {stats['total']} | "
                f"Activos: {stats['active']} | "
                f"Inactivos: {stats['inactive']} | "
                f"Fallidos: {stats['failed']} | "
                f"Autostart: {stats['enabled']}"
            )
        )

        for widget in self._service_frame.winfo_children():
            widget.destroy()

        search_query = self._search_var.get()
        services = (
            self._service_monitor.search_services(search_query)
            if search_query
            else self._service_monitor.get_services()
        )

        for i, service in enumerate(services[:30]):
            self._create_service_row(service, i)

    # ── Filas de servicio ─────────────────────────────────────────────────────

    def _create_service_row(self, service: dict, row: int):
        bg_color  = COLORS['bg_dark'] if row % 2 == 0 else COLORS['bg_medium']
        row_frame = ctk.CTkFrame(self._service_frame, fg_color=bg_color)
        row_frame.pack(fill="x", pady=2)

        row_frame.grid_columnconfigure(0, weight=2, minsize=150)
        row_frame.grid_columnconfigure(1, weight=1, minsize=100)
        row_frame.grid_columnconfigure(2, weight=1, minsize=80)
        row_frame.grid_columnconfigure(3, weight=3, minsize=300)

        state_icon  = Icons.GREEN_CIRCLE if service['active'] == 'active' else Icons.RED_CIRCLE
        state_color = COLORS[self._service_monitor.get_state_color(service['active'])]

        ctk.CTkLabel(
            row_frame,
            text=f"{state_icon} {service['name']}",
            text_color=state_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(
            row_frame,
            text=service['active'],
            text_color=state_color,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        autostart_color = COLORS['success'] if service['enabled'] else COLORS['text_dim']
        ctk.CTkLabel(
            row_frame,
            text="" + Icons.CHECK_MARK + "" if service['enabled'] else "" + Icons.CROSS_MARK + "",
            text_color=autostart_color,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).grid(row=0, column=2, sticky="n", padx=5, pady=5)

        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=3, sticky="ew", padx=5, pady=3)

        if service['active'] == 'active':
            ctk.CTkButton(
                actions_frame, text="" + Icons.PAUSE + "",
                command=lambda s=service: self._stop_service(s),
                fg_color=COLORS['warning'], hover_color=COLORS['danger'],
                width=40, height=25, font=(FONT_FAMILY, 14)
            ).pack(side="left", padx=2)
        else:
            ctk.CTkButton(
                actions_frame, text="" + Icons.PLAY + "" ,
                command=lambda s=service: self._start_service(s),
                fg_color=COLORS['success'], hover_color="#00aa00",
                width=40, height=25, font=(FONT_FAMILY, 14)
            ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions_frame, text="" + Icons.REFRESH + "",
            command=lambda s=service: self._restart_service(s),
            fg_color=COLORS['primary'], width=40, height=25,
            font=(FONT_FAMILY, 12)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions_frame, text="" + Icons.EYE + "",
            command=lambda s=service: self._view_logs(s),
            fg_color=COLORS['bg_light'], width=40, height=25,
            font=(FONT_FAMILY, 12)
        ).pack(side="left", padx=2)

        if service['enabled']:
            ctk.CTkButton(
                actions_frame, text="" + Icons.TAB_SERVICIOS + "",
                command=lambda s=service: self._disable_service(s),
                fg_color=COLORS['text_dim'], width=40, height=25,
                font=(FONT_FAMILY, 12)
            ).pack(side="left", padx=2)
        else:
            ctk.CTkButton(
                actions_frame, text="" + Icons.TAB_SERVICIOS + "",
                command=lambda s=service: self._enable_service(s),
                fg_color=COLORS['secondary'], width=40, height=25,
                font=(FONT_FAMILY, 12)
            ).pack(side="left", padx=2)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _start_service(self, service: dict):
        def do_start():
            success, message = self._service_monitor.start_service(service['name'])
            custom_msgbox(self, message, "Iniciar Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Iniciar servicio '{service['name']}'?",
            title="" + Icons.WARNING + "️ Confirmar",
            on_confirm=do_start,
            on_cancel=None
        )

    def _stop_service(self, service: dict):
        def do_stop():
            success, message = self._service_monitor.stop_service(service['name'])
            custom_msgbox(self, message, "Detener Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Detener servicio '{service['name']}'?\n\nEl servicio dejará de funcionar.",
            title="" + Icons.WARNING + "️ Confirmar",
            on_confirm=do_stop,
            on_cancel=None
        )

    def _restart_service(self, service: dict):
        def do_restart():
            success, message = self._service_monitor.restart_service(service['name'])
            custom_msgbox(self, message, "Reiniciar Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Reiniciar servicio '{service['name']}'?",
            title="" + Icons.WARNING + "️ Confirmar",
            on_confirm=do_restart,
            on_cancel=None
        )

    def _view_logs(self, service: dict):
        logs = self._service_monitor.get_logs(service['name'], lines=30)

        logs_window = ctk.CTkToplevel(self)
        logs_window.title(f"Logs: {service['name']}")
        logs_window.geometry("700x500")

        textbox = ctk.CTkTextbox(
            logs_window,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wrap="word"
        )
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("1.0", logs)
        textbox.configure(state="disabled")

        make_futuristic_button(
            logs_window, text="Cerrar",
            command=logs_window.destroy,
            width=15, height=6
        ).pack(pady=10)

    def _enable_service(self, service: dict):
        def do_enable():
            success, message = self._service_monitor.enable_service(service['name'])
            custom_msgbox(self, message, "Habilitar Autostart")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Habilitar autostart para '{service['name']}'?\n\n"
                 f"El servicio se iniciará automáticamente al arrancar.",
            title="" + Icons.WARNING + "️ Confirmar",
            on_confirm=do_enable,
            on_cancel=None
        )

    def _disable_service(self, service: dict):
        def do_disable():
            success, message = self._service_monitor.disable_service(service['name'])
            custom_msgbox(self, message, "Deshabilitar Autostart")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Deshabilitar autostart para '{service['name']}'?\n\n"
                 f"El servicio NO se iniciará automáticamente al arrancar.",
            title="" + Icons.WARNING + "️ Confirmar",
            on_confirm=do_disable,
            on_cancel=None
        )
