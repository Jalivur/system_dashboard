"""
Ventana Service Watchdog - monitor críticos + config inline
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.service_monitor import ServiceMonitor
from core.service_watchdog import ServiceWatchdog
from utils.logger import get_logger

logger = get_logger(__name__)

class ServiceWatchdogWindow(ctk.CTkToplevel):
    """Ventana Service Watchdog systemd"""

    def __init__(self, parent, service_monitor: ServiceMonitor, watchdog: ServiceWatchdog):
        super().__init__(parent)

        self._service_monitor = service_monitor
        self._watchdog = watchdog

        self._search_var = ctk.StringVar(master=self)
        self._filter_var = ctk.StringVar(master=self, value="critical")
        self._critical_entry = ctk.StringVar(master=self)
        self._critical_list_label = None
        self._update_paused = False
        self._update_job = None
        self._umbral_debounce_id = None
        self._interval_debounce_id = None
        _stats = watchdog.get_stats()
        self._umbral_var = ctk.StringVar(master=self, value=str(_stats['threshold']))
        self._interval_var = ctk.StringVar(master=self, value=str(_stats['interval']))

        self.title("Service Watchdog")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        self._create_ui()
        self._update()
        logger.info("[ServiceWatchdogWindow] Ventana Abierta")


    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(
            main,
            title="SERVICE WATCHDOG",
            on_close=self.destroy,
        )

        # STATS BAR
        stats_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'])
        stats_bar.pack(fill="x", padx=5, pady=(0, 4))
        self._stats_label = ctk.CTkLabel(
            stats_bar,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self._stats_label.pack(pady=4, padx=10, anchor="w")
        
        # CONFIG INFERIOR (GPIO STYLE)
        config_frame = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=8)
        config_frame.pack(fill="x", padx=8, pady=(0, 6))

        # Umbral
        ctk.CTkLabel(config_frame, text="Umbral:", font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), 
                    text_color=COLORS['text']).pack(side="left", padx=(10,5), pady=8)
        self._umbral_entry = ctk.CTkEntry(config_frame, textvariable=self._umbral_var, width=50, height=25, justify="center")
        self._umbral_entry.pack(side="left", padx=5, pady=8)
        self._umbral_entry.bind("<KeyRelease>", lambda e: self._debounce_umbral_update())
        self._umbral_val = ctk.CTkLabel(config_frame, text="3", width=40, font=(FONT_FAMILY, 16, "bold"))
        self._umbral_val.pack(side="left", padx=5, pady=8)

        # Intervalo
        ctk.CTkLabel(config_frame, text="Intervalo(s):", font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), 
                    text_color=COLORS['text']).pack(side="left", padx=(20,5), pady=8)
        self._interval_entry = ctk.CTkEntry(config_frame, textvariable=self._interval_var, width=70, height=25, justify="center")
        self._interval_entry.pack(side="left", padx=5, pady=8)
        self._interval_entry.bind("<KeyRelease>", lambda e: self._debounce_interval_update())
        self._interval_val = ctk.CTkLabel(config_frame, text="60", width=50, font=(FONT_FAMILY, 16, "bold"))
        self._interval_val.pack(side="left", padx=5, pady=8)

        # Apply
        make_futuristic_button(config_frame, text="APLIAR", width=8, height=6,
                             command=self._apply_config).pack(side="right", padx=10, pady=8)

        # Refresh
        make_futuristic_button(config_frame, text="🔄 Refrescar", width=8, height=6,
                             command=self._force_update).pack(side="right" ,pady=5)

        # CONTROLS
        self._create_controls(main)
        self._create_column_headers(main)

        # SCROLL TABLE
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        canvas = ctk.CTkCanvas(scroll_container, bg=COLORS['bg_medium'], highlightthickness=0, height=80)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ctk.CTkScrollbar(scroll_container, orientation="vertical", command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        self._table_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self._table_frame, anchor="nw", width=DSI_WIDTH - 50)
        self._table_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        

    def _create_controls(self, parent):
        controls = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        controls.pack(fill="x", padx=10, pady=5)

        # Search
        ctk.CTkLabel(controls, text="Buscar:", font=(FONT_FAMILY, FONT_SIZES['small'])).pack(side="left", padx=(0,5))
        search_entry = ctk.CTkEntry(controls, textvariable=self._search_var, width=200)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self._debounced_search())

        # Filter
        ctk.CTkLabel(controls, text="Filter:", font=(FONT_FAMILY, FONT_SIZES['small'])).pack(side="left", padx=(20,5))
        ctk.CTkRadioButton(controls, text="Críticos", variable=self._filter_var, value="critical",
                          command=self._on_filter).pack(side="left", padx=5)
        ctk.CTkRadioButton(controls, text="Todos", variable=self._filter_var, value="all",
                          command=self._on_filter).pack(side="left", padx=5)
        controls_second = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        controls_second.pack(fill="x", padx=10, pady=5)
        # Add Crítico
        ctk.CTkLabel(controls_second, text="Añadir crítico:", font=(FONT_FAMILY, FONT_SIZES['small'])).pack(side="left", padx=(20,5))
        entry = ctk.CTkEntry(controls_second, textvariable=self._critical_entry, width=150, placeholder_text="ej. nginx")
        entry.pack(side="left", padx=5)
        make_futuristic_button(controls_second, text="AÑADIR", width=8, height=6, command=self._add_critical).pack(side="left", padx=5)
        make_futuristic_button(controls_second, text="Guardar", width=8, height=6, command=self._save_criticals).pack(side="left", padx=5)


    def _create_column_headers(self, parent):
        headers = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'])
        headers.pack(fill="x", padx=10, pady=5)
        headers.grid_columnconfigure((0,1,2), weight=1)
        headers.grid_columnconfigure(3, weight=2)

        ctk.CTkLabel(headers, text="Servicio", font=(FONT_FAMILY, FONT_SIZES['small'], "bold")).grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(headers, text="Estado", font=(FONT_FAMILY, FONT_SIZES['small'], "bold")).grid(row=0, column=1, sticky="w", padx=5)
        ctk.CTkLabel(headers, text="Fallos", font=(FONT_FAMILY, FONT_SIZES['small'], "bold")).grid(row=0, column=2, sticky="w", padx=5)
        ctk.CTkLabel(headers, text="Actions", font=(FONT_FAMILY, FONT_SIZES['small'], "bold")).grid(row=0, column=3, sticky="w", padx=5)

    def _debounce_umbral_update(self):
        if self._umbral_debounce_id:
            self.after_cancel(self._umbral_debounce_id)
        self._umbral_debounce_id = self.after(400, lambda: self._on_umbral_change(self._umbral_var.get()))

    def _on_umbral_change(self, val):
        try:
            v = int(val)
            v = max(1, min(10, v))
            self._umbral_var.set(str(v))
            self._umbral_val.configure(text=str(v))
        except ValueError:
            pass

    def _debounce_interval_update(self):
        if self._interval_debounce_id:
            self.after_cancel(self._interval_debounce_id)
        self._interval_debounce_id = self.after(400, lambda: self._on_interval_change(self._interval_var.get()))

    def _on_interval_change(self, val):
        try:
            v = int(val)
            v = max(30, min(300, v))
            self._interval_var.set(str(v))
            self._interval_val.configure(text=str(v))
        except ValueError:
            pass

    def _apply_config(self):
        try:
            threshold = max(1, min(10, int(self._umbral_var.get())))
            interval = max(30, min(300, int(self._interval_var.get())))
            self._watchdog.set_threshold(threshold)
            self._watchdog.set_interval(interval)
            custom_msgbox(self, f"Umbral: {threshold} | Intervalo: {interval}s")
        except ValueError:
            custom_msgbox(self, "Valores inválidos. Usa enteros (Umbral:1-10, Intervalo:30-300)")

    def _debounced_search(self):
        if hasattr(self, '_search_id'):
            self.after_cancel(self._search_id)
        self._search_id = self.after(400, self._update_now)

    def _on_filter(self):
        self._update_paused = True
        self.after(1500, self._resume_updates)

    def _resume_updates(self):
        self._update_paused = False

    def _force_update(self):
        self._update_paused = False
        self._update_now()

    def _update(self):
        if not self.winfo_exists():
            return
        if self._update_paused:
            self.after(2000, self._update)
            return
        self._update_now()
        self.after(UPDATE_MS * 2, self._update)

    def _update_now(self):
        stats = self._watchdog.get_stats()
        self._stats_label.configure(text=f"Críticos: {stats['critical_count']} | Restarts hoy: {stats['restarts_today']} | Umbral: {stats['threshold']} | Estado: {'🟢' if stats['running'] else '🔴'}")

        for w in self._table_frame.winfo_children():
            w.destroy()

        services = self._service_monitor.get_services()
        critical = [s for s in services if s['name'] in stats['services']]
        filtered = critical if self._filter_var.get() == "critical" else services
        query = self._search_var.get().lower()
        filtered = [s for s in filtered if query in s['name'].lower()]

        for i, service in enumerate(filtered[:25]):
            bg = COLORS['bg_dark'] if i%2==0 else COLORS['bg_medium']
            row = ctk.CTkFrame(self._table_frame, fg_color=bg)
            row.pack(fill="x", pady=2, padx=5)

            # Servicio
            color = COLORS['success'] if service['active'] == 'active' else COLORS['danger']
            icon = Icons.GREEN_CIRCLE if service['active'] == 'active' else Icons.RED_CIRCLE
            ctk.CTkLabel(row, text=f"{icon} {service['name']}", text_color=color, font=(FONT_FAMILY, FONT_SIZES['small'])).pack(side="left", padx=8)

            # Fallos
            fallos = stats['consec_failed'].get(service['name'], 0)
            fcolor = COLORS['danger'] if fallos >= stats['threshold'] else COLORS['warning']
            ctk.CTkLabel(row, text=str(fallos), text_color=fcolor, font=(FONT_FAMILY, FONT_SIZES['small'], 'bold')).pack(side="left", padx=8)

            # Restarts
            restarts = stats['restart_counts'].get(service['name'], 0)
            ctk.CTkLabel(row, text=str(restarts), text_color=COLORS['primary']).pack(side="left", padx=8)

            # Actions 35x22
            ctk.CTkButton(row, text=Icons.REFRESH, width=35, height=22, fg_color=COLORS['primary'],
                         command=lambda n=service['name']: self._do_restart(n)).pack(side="right", padx=2)
            ctk.CTkButton(row, text=Icons.EYE, width=35, height=22, fg_color=COLORS['bg_light'],
                         command=lambda n=service['name']: self._show_logs(n)).pack(side="right", padx=2)

    def _do_restart(self, name):
        def action():
            success, msg = self._service_monitor.restart_service(name)
            custom_msgbox(self, msg)
            self._update_now()
        confirm_dialog(
            self,
            f"¿Reiniciar {name}?",
            title=f"{Icons.WARNING} Confirmar",
            on_confirm=action
        )

    def _show_logs(self, name):
        logs = self._service_monitor.get_logs(name, lines=30)
        custom_msgbox(self, logs[:800] if logs else "Sin logs", title=f"Logs — {name}")
        
    def _add_critical(self):
        name = self._critical_entry.get().strip()
        if not name:
            return custom_msgbox(self, "Nombre vacío")
        if not self._watchdog.add_critical_service(name):
            return custom_msgbox(self, f"{name} ya es crítico")
        self._update_critical_label()
        self._update_now()
        custom_msgbox(self, f"'{name}' añadido a críticos")

    def _save_criticals(self):
        services = self._watchdog.get_stats()['services']
        self._watchdog.set_critical_services(services)
        custom_msgbox(self, "Lista críticos guardada")

    def _update_critical_label(self):
        if self._critical_list_label:
            self._critical_list_label.configure(text=f"Críticos: {', '.join(self._watchdog._critical_services)}")

