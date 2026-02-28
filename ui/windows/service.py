"""
Ventana de monitor de servicios systemd
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.service_monitor import ServiceMonitor


class ServiceWindow(ctk.CTkToplevel):
    """Ventana de monitor de servicios"""

    def __init__(self, parent, service_monitor: ServiceMonitor):
        super().__init__(parent)

        # Referencias
        self.service_monitor = service_monitor

        # Estado
        self.search_var = ctk.StringVar()
        self.filter_var = ctk.StringVar(value="all")
        self.update_paused = False
        self.update_job = None

        # Configurar ventana
        self.title("Monitor de Servicios")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        # Crear interfaz
        self._create_ui()

        # Iniciar actualización
        self._update()

    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="MONITOR DE SERVICIOS",
            on_close=self.destroy,
        )

        # Stats en línea propia debajo del header
        stats_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'])
        stats_bar.pack(fill="x", padx=5, pady=(0, 4))
        self.stats_label = ctk.CTkLabel(
            stats_bar,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self.stats_label.pack(pady=4, padx=10, anchor="w")

        # Controles (búsqueda y filtros)
        self._create_controls(main)

        # Encabezados de columnas
        self._create_column_headers(main)

        # Área de scroll para servicios
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        self._content_frame = scroll_container
        # Limitar altura
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

        # Frame interno para servicios
        self.service_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self.service_frame, anchor="nw", width=DSI_WIDTH-50)
        self.service_frame.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Botones inferiores
        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)

        refresh_btn = make_futuristic_button(
            bottom,
            text="Refrescar",
            command=self._force_update,
            width=15,
            height=6
        )
        refresh_btn.pack(side="left", padx=5)



    def _create_controls(self, parent):
        """Crea controles de búsqueda y filtros"""
        controls = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        controls.pack(fill="x", padx=10, pady=5)

        # Búsqueda
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
            textvariable=self.search_var,
            width=200,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())

        # Filtros
        filter_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        filter_frame.pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            filter_frame,
            text="Filtro:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))

        for filter_type, label in [("all", "Todos"), ("active", "Activos"), 
                                   ("inactive", "Inactivos"), ("failed", "Fallidos")]:
            rb = ctk.CTkRadioButton(
                filter_frame,
                text=label,
                variable=self.filter_var,
                value=filter_type,
                command=self._on_filter_change,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=5)
            StyleManager.style_radiobutton_ctk(rb)

    def _create_column_headers(self, parent):
        """Crea encabezados de columnas"""
        headers = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'])
        headers.pack(fill="x", padx=10, pady=(5, 0))

        headers.grid_columnconfigure(0, weight=2, minsize=150)  # Servicio
        headers.grid_columnconfigure(1, weight=1, minsize=100)  # Estado
        headers.grid_columnconfigure(2, weight=1, minsize=80)   # Autostart
        headers.grid_columnconfigure(3, weight=3, minsize=300)  # Acciones

        columns = [
            ("Servicio", "name"),
            ("Estado", "state"),
            ("Autostart", None),
            ("Acciones", None)
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

    def _on_sort_change(self, column: str):
        """Cambia el orden"""
        self.update_paused = True

        if self.service_monitor.sort_by == column:
            self.service_monitor.sort_reverse = not self.service_monitor.sort_reverse
        else:
            self.service_monitor.set_sort(column, reverse=False)

        self._update_now()
        self.after(2000, self._resume_updates)

    def _on_filter_change(self):
        """Cambia el filtro"""
        self.update_paused = True
        self.service_monitor.set_filter(self.filter_var.get())
        self._update_now()
        self.after(2000, self._resume_updates)

    def _on_search_change(self):
        """Callback cuando cambia la búsqueda"""
        self.update_paused = True

        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)

        self._search_timer = self.after(500, self._do_search)

    def _do_search(self):
        """Ejecuta la búsqueda"""
        self._update_now()
        self.after(3000, self._resume_updates)

    def _update(self):
        """Actualiza la lista de servicios"""
        if not self.service_monitor._running:
            StyleManager.show_service_stopped_banner(self._content_frame, "Service Monitor")
            self._update_job = self.after(UPDATE_MS, self._update)
            return
        if not self.winfo_exists():
            return

        if self.update_paused:
            self.update_job = self.after(UPDATE_MS * 5, self._update)  # 10 segundos
            return

        self._update_now()
        self.update_job = self.after(UPDATE_MS * 5, self._update)  # 10 segundos

    def _update_now(self):
        """Actualiza inmediatamente"""
        if not self.winfo_exists():
            return

        # Actualizar estadísticas
        stats = self.service_monitor.get_stats()
        self.stats_label.configure(
            text=f"Total: {stats['total']} | "
                 f"Activos: {stats['active']} | "
                 f"Inactivos: {stats['inactive']} | "
                 f"Fallidos: {stats['failed']} | "
                 f"Autostart: {stats['enabled']}"
        )

        # Limpiar servicios anteriores
        for widget in self.service_frame.winfo_children():
            widget.destroy()

        # Obtener servicios
        search_query = self.search_var.get()
        if search_query:
            services = self.service_monitor.search_services(search_query)
        else:
            services = self.service_monitor.get_services()

        # Limitar a top 30
        services = services[:30]

        # Mostrar servicios
        for i, service in enumerate(services):
            self._create_service_row(service, i)

    def _create_service_row(self, service: dict, row: int):
        """Crea una fila para un servicio"""
        bg_color = COLORS['bg_dark'] if row % 2 == 0 else COLORS['bg_medium']
        row_frame = ctk.CTkFrame(self.service_frame, fg_color=bg_color)
        row_frame.pack(fill="x", pady=2)

        row_frame.grid_columnconfigure(0, weight=2, minsize=150)
        row_frame.grid_columnconfigure(1, weight=1, minsize=100)
        row_frame.grid_columnconfigure(2, weight=1, minsize=80)
        row_frame.grid_columnconfigure(3, weight=3, minsize=300)

        # Icono y nombre
        state_icon = "🟢" if service['active'] == 'active' else "🔴"
        state_color = COLORS[self.service_monitor.get_state_color(service['active'])]

        name_label = ctk.CTkLabel(
            row_frame,
            text=f"{state_icon} {service['name']}",
            text_color=state_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        )
        name_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Estado
        ctk.CTkLabel(
            row_frame,
            text=service['active'],
            text_color=state_color,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Autostart
        autostart_text = "✓" if service['enabled'] else "✗"
        autostart_color = COLORS['success'] if service['enabled'] else COLORS['text_dim']
        ctk.CTkLabel(
            row_frame,
            text=autostart_text,
            text_color=autostart_color,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).grid(row=0, column=2, sticky="n", padx=5, pady=5)

        # Botones de acción
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=3, sticky="ew", padx=5, pady=3)

        # Start/Stop
        if service['active'] == 'active':
            stop_btn = ctk.CTkButton(
                actions_frame,
                text="⏸",
                command=lambda s=service: self._stop_service(s),
                fg_color=COLORS['warning'],
                hover_color=COLORS['danger'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 14)
            )
            stop_btn.pack(side="left", padx=2)
        else:
            start_btn = ctk.CTkButton(
                actions_frame,
                text="▶",
                command=lambda s=service: self._start_service(s),
                fg_color=COLORS['success'],
                hover_color="#00aa00",
                width=40,
                height=25,
                font=(FONT_FAMILY, 14)
            )
            start_btn.pack(side="left", padx=2)

        # Restart
        restart_btn = ctk.CTkButton(
            actions_frame,
            text="🔄",
            command=lambda s=service: self._restart_service(s),
            fg_color=COLORS['primary'],
            width=40,
            height=25,
            font=(FONT_FAMILY, 12)
        )
        restart_btn.pack(side="left", padx=2)

        # Logs
        logs_btn = ctk.CTkButton(
            actions_frame,
            text="👁",
            command=lambda s=service: self._view_logs(s),
            fg_color=COLORS['bg_light'],
            width=40,
            height=25,
            font=(FONT_FAMILY, 12)
        )
        logs_btn.pack(side="left", padx=2)

        # Enable/Disable
        if service['enabled']:
            disable_btn = ctk.CTkButton(
                actions_frame,
                text="⚙",
                command=lambda s=service: self._disable_service(s),
                fg_color=COLORS['text_dim'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 12)
            )
            disable_btn.pack(side="left", padx=2)
        else:
            enable_btn = ctk.CTkButton(
                actions_frame,
                text="⚙",
                command=lambda s=service: self._enable_service(s),
                fg_color=COLORS['secondary'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 12)
            )
            enable_btn.pack(side="left", padx=2)

    def _start_service(self, service: dict):
        """Inicia un servicio"""
        def do_start():
            success, message = self.service_monitor.start_service(service['name'])
            custom_msgbox(self, message, "Iniciar Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Iniciar servicio '{service['name']}'?",
            title="⚠️ Confirmar",
            on_confirm=do_start,
            on_cancel=None
        )

    def _stop_service(self, service: dict):
        """Detiene un servicio"""
        def do_stop():
            success, message = self.service_monitor.stop_service(service['name'])
            custom_msgbox(self, message, "Detener Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Detener servicio '{service['name']}'?\n\n"
                 f"El servicio dejará de funcionar.",
            title="⚠️ Confirmar",
            on_confirm=do_stop,
            on_cancel=None
        )

    def _restart_service(self, service: dict):
        """Reinicia un servicio"""
        def do_restart():
            success, message = self.service_monitor.restart_service(service['name'])
            custom_msgbox(self, message, "Reiniciar Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Reiniciar servicio '{service['name']}'?",
            title="⚠️ Confirmar",
            on_confirm=do_restart,
            on_cancel=None
        )

    def _view_logs(self, service: dict):
        """Muestra logs de un servicio"""
        logs = self.service_monitor.get_logs(service['name'], lines=30)

        # Crear ventana de logs
        logs_window = ctk.CTkToplevel(self)
        logs_window.title(f"Logs: {service['name']}")
        logs_window.geometry("700x500")

        # Textbox con logs
        textbox = ctk.CTkTextbox(
            logs_window,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wrap="word"
        )
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("1.0", logs)
        textbox.configure(state="disabled")

        # Botón cerrar
        close_btn = make_futuristic_button(
            logs_window,
            text="Cerrar",
            command=logs_window.destroy,
            width=15,
            height=6
        )
        close_btn.pack(pady=10)

    def _enable_service(self, service: dict):
        """Habilita autostart"""
        def do_enable():
            success, message = self.service_monitor.enable_service(service['name'])
            custom_msgbox(self, message, "Habilitar Autostart")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Habilitar autostart para '{service['name']}'?\n\n"
                 f"El servicio se iniciará automáticamente al arrancar.",
            title="⚠️ Confirmar",
            on_confirm=do_enable,
            on_cancel=None
        )

    def _disable_service(self, service: dict):
        """Deshabilita autostart"""
        def do_disable():
            success, message = self.service_monitor.disable_service(service['name'])
            custom_msgbox(self, message, "Deshabilitar Autostart")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Deshabilitar autostart para '{service['name']}'?\n\n"
                 f"El servicio NO se iniciará automáticamente al arrancar.",
            title="⚠️ Confirmar",
            on_confirm=do_disable,
            on_cancel=None
        )

    def _force_update(self):
        """Fuerza actualización inmediata"""
        self.update_paused = False
        self._update_now()

    def _resume_updates(self):
        """Reanuda actualizaciones"""
        self.update_paused = False
