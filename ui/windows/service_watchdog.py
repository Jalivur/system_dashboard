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
    """
    Ventana para monitoreo y configuración del watchdog de servicios systemd.

    Args:
        parent: Ventana padre (CTk).
        service_monitor (ServiceMonitor): Instancia para queries de servicios y logs.
        watchdog (ServiceWatchdog): Instancia para configuración y estadísticas críticas.

    Returns:
        None

    Raises:
        None
    """

    def __init__(self, parent, service_monitor: ServiceMonitor, watchdog: ServiceWatchdog):
        """
        Inicializa la ventana de monitoreo Service Watchdog.

        Configura las dependencias, variables de estado y la interfaz de usuario.

        Args:
            parent: Ventana padre (CTk).
            service_monitor (ServiceMonitor): Instancia para queries de servicios y logs.
            watchdog (ServiceWatchdog): Instancia para configuración y estadísticas críticas.

        Returns:
            None

        Raises:
            None
        """
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
        """
        Crea la interfaz de usuario principal de la ventana Service Watchdog.

            Args:
                Ninguno

            Returns:
                Ninguno

            Raises:
                Ninguno
        """
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
        """
        Crea los controles interactivos superiores para filtrado y gestión de servicios.

        Args:
            parent: Frame contenedor principal donde se crearán los controles.

        """
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
        """
        Crea la fila de encabezados para la tabla scrollable de servicios.

        Args:
            parent: Frame contenedor de headers.

        Returns:
            None

        Raises:
            None
        """
        headers = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'])
        headers.pack(fill="x", padx=10, pady=5)
        headers.grid_columnconfigure((0,1,2), weight=1)
        headers.grid_columnconfigure(3, weight=2)

        ctk.CTkLabel(headers, text="Servicio", font=(FONT_FAMILY, FONT_SIZES['small'], "bold")).grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(headers, text="Estado", font=(FONT_FAMILY, FONT_SIZES['small'], "bold")).grid(row=0, column=1, sticky="w", padx=5)
        ctk.CTkLabel(headers, text="Fallos", font=(FONT_FAMILY, FONT_SIZES['small'], "bold")).grid(row=0, column=2, sticky="w", padx=5)
        ctk.CTkLabel(headers, text="Actions", font=(FONT_FAMILY, FONT_SIZES['small'], "bold")).grid(row=0, column=3, sticky="w", padx=5)

    def _debounce_umbral_update(self):
        """
        Maneja el debounce para cambios en el campo de umbral de fallos críticos.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if self._umbral_debounce_id:
            self.after_cancel(self._umbral_debounce_id)
        self._umbral_debounce_id = self.after(400, lambda: self._on_umbral_change(self._umbral_var.get()))

    def _on_umbral_change(self, val):
        """
        Aplica cambios al umbral de fallos consecutivos críticos a partir de un valor introducido.

        Args:
            val (str): Valor crudo del campo de entrada.

        Raises:
            None
        """
        try:
            v = int(val)
            v = max(1, min(10, v))
            self._umbral_var.set(str(v))
            self._umbral_val.configure(text=str(v))
        except ValueError:
            pass

    def _debounce_interval_update(self):
        """
        Establece un debounce para cambios en el intervalo de monitoreo, 
        programando una actualización diferida después de un período de inactividad.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if self._interval_debounce_id:
            self.after_cancel(self._interval_debounce_id)
        self._interval_debounce_id = self.after(400, lambda: self._on_interval_change(self._interval_var.get()))

    def _on_interval_change(self, val):
        """
        Aplica cambios al intervalo de chequeo periódico del watchdog.

            Args:
                val (str): Valor del entry field.

            Raises:
                None
        """
        try:
            v = int(val)
            v = max(30, min(300, v))
            self._interval_var.set(str(v))
            self._interval_val.configure(text=str(v))
        except ValueError:
            pass

    def _apply_config(self):
        """
        Aplica la configuración actual de umbral e intervalo al ServiceWatchdog.

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: Si los valores de umbral o intervalo no son válidos.

        Nota: Configura el umbral entre 1 y 10, e intervalo entre 30 y 300.
        """
        try:
            threshold = max(1, min(10, int(self._umbral_var.get())))
            interval = max(30, min(300, int(self._interval_var.get())))
            self._watchdog.set_threshold(threshold)
            self._watchdog.set_interval(interval)
            custom_msgbox(self, f"Umbral: {threshold} | Intervalo: {interval}s")
        except ValueError:
            custom_msgbox(self, "Valores inválidos. Usa enteros (Umbral:1-10, Intervalo:30-300)")

    def _debounced_search(self):
        """
        Implementa búsqueda en tiempo real con debounce para nombres de servicios.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if hasattr(self, '_search_id'):
            self.after_cancel(self._search_id)
        self._search_id = self.after(400, self._update_now)

    def _on_filter(self):
        """
        Responde a cambios en el filtro de servicios.

        Pausa las actualizaciones durante 1.5 segundos para evitar flicker durante la transición.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._update_paused = True
        self.after(1500, self._resume_updates)

    def _resume_updates(self):
        """
        Reanuda el ciclo de actualizaciones periódicas tras una pausa temporal.

        Args: None

        Returns: None

        Raises: None
        """
        self._update_paused = False

    def _force_update(self):
        """
        Fuerza la actualización inmediata de datos y la interfaz de usuario.

        Despausa las actualizaciones si estaban detenidas y llama a _update_now directamente.
        Este método es utilizado por el botón Refrescar.

        Args: Ninguno

        Returns: Ninguno

        Raises: Ninguno
        """
        self._update_paused = False
        self._update_now()

    def _update(self):
        """
        Actualiza periódicamente la interfaz de usuario del ServiceWatchdogWindow.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if not self.winfo_exists():
            return
        if self._update_paused:
            self.after(2000, self._update)
            return
        self._update_now()
        self.after(UPDATE_MS * 2, self._update)

    def _update_now(self):
        """
        Actualiza inmediatamente estadísticas y tabla de servicios.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
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
        """
        Inicia el reinicio seguro de un servicio con confirmación del usuario.

        Args:
            name (str): Nombre exacto del servicio systemd.

        Raises:
            None

        Returns:
            None
        """
        def action():
            '''Closure local ejecutada post-confirmación de reinicio de servicio.

            - Ejecuta ServiceMonitor.restart_service(name)
            - Muestra resultado en custom_msgbox 
            - Refresca UI inmediata con _update_now()
            '''

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
        """
        Muestra logs recientes del servicio en una ventana modal.

        Args:
            name (str): Nombre del servicio.

        Returns:
            None

        Raises:
            None
        """
        logs = self._service_monitor.get_logs(name, lines=30)
        custom_msgbox(self, logs[:800] if logs else "Sin logs", title=f"Logs — {name}")
        
    def _add_critical(self):
        """
        Añade un servicio a la lista de monitoreo crítico.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        name = self._critical_entry.get().strip()
        if not name:
            return custom_msgbox(self, "Nombre vacío")
        if not self._watchdog.add_critical_service(name):
            return custom_msgbox(self, f"{name} ya es crítico")
        self._update_critical_label()
        self._update_now()
        custom_msgbox(self, f"'{name}' añadido a críticos")

    def _save_criticals(self):
        """
        Persiste la lista actual de servicios críticos en watchdog.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        services = self._watchdog.get_stats()['services']
        self._watchdog.set_critical_services(services)
        custom_msgbox(self, "Lista críticos guardada")

    def _update_critical_label(self):
        """
        Actualiza la etiqueta textual con la lista actual de servicios críticos.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if self._critical_list_label:
            self._critical_list_label.configure(text=f"Críticos: {', '.join(self._watchdog._critical_services)}")

