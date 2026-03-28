"""
Ventana de histórico de datos
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, DATA_DIR, EXPORTS_CSV_DIR, EXPORTS_SCR_DIR, Icons
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox , confirm_dialog
from core.data_analyzer import DataAnalyzer
from core.data_logger import DataLogger
from core.cleanup_service import CleanupService
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from utils.logger import get_logger
import os

logger = get_logger(__name__)

_DATE_FMT = "%Y-%m-%d %H:%M"


class HistoryWindow(ctk.CTkToplevel):
    """
    Ventana de visualización de histórico de datos del sistema.

    Args:
        parent: Ventana padre CTkToplevel.
        cleanup_service: Instancia de CleanupService para gestión de limpieza.

    Returns:
        None

    Raises:
        None
    """

    def __init__(self, parent, cleanup_service: CleanupService):
        """
        Inicializa la ventana de histórico de datos del sistema.

        Args:
            parent: Ventana padre CTkToplevel.
            cleanup_service: Instancia de CleanupService para gestión de limpieza.

        Returns:
            None

        Raises:
            None
        """
        super().__init__(parent)

        # Referencias
        self._analyzer         = DataAnalyzer()
        self._logger           = DataLogger()
        self._cleanup_service  = cleanup_service

        # Estado de periodo
        self._period_var = ctk.StringVar(master=self, value="24h")
        self._period_start = ctk.StringVar(master=self, value="YYYY-MM-DD HH:MM")
        self._period_end   = ctk.StringVar(master=self, value="YYYY-MM-DD HH:MM")

        # Estado de rango personalizado
        self._using_custom_range = False
        self._custom_start: datetime = None
        self._custom_end:   datetime = None

        # Configurar ventana
        self.title("Histórico de Datos")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        # Crear interfaz
        self._create_ui()

        # Cargar datos iniciales
        self._update_data()
        logger.info("[HistoryWindow] Ventana Abierta")


    # ─────────────────────────────────────────────
    # Construcción de la UI
    # ─────────────────────────────────────────────

    def _create_ui(self):
        """
        Crea la interfaz de usuario completa de la ventana de historial.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        self._main.pack(fill="both", expand=True, padx=5, pady=5) 
        # ── Header unificado ──────────────────────────────────────────────────
        self._header = make_window_header(
            self._main,
            title="HISTÓRICO DE DATOS",
            on_close=self.destroy,
        )
        # Barra de herramientas en línea propia debajo del header
        self._toolbar_container = ctk.CTkFrame(self._main, fg_color=COLORS["bg_dark"])
        self._toolbar_container.pack(fill="x", padx=5, pady=(0, 4))
        self._toolbar_container.pack_configure(anchor="center")
        self._create_period_controls(self._main)
        self._create_range_panel(self._main)   # fila oculta de OptionMenus

        scroll_container = ctk.CTkFrame(self._main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas_tk = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=DSI_HEIGHT - 300
        )
        canvas_tk.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas_tk.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")

        StyleManager.style_scrollbar_ctk(scrollbar)

        canvas_tk.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas_tk, fg_color=COLORS['bg_medium'])
        canvas_tk.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>",
                   lambda e: canvas_tk.configure(scrollregion=canvas_tk.bbox("all")))

        self._create_graphs_area(inner)
        self._create_stats_area(inner)
        self._create_buttons(self._main)


    def _create_period_controls(self, parent):
        """
        Crea los controles de periodo en la ventana de historial.

        Args:
            parent: El elemento padre donde se crearán los controles.

        Returns:
            None

        Raises:
            None
        """
        self._controls_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        self._controls_frame.pack(fill="x", padx=10, pady=(5, 0))

        ctk.CTkLabel(
            self._controls_frame,
            text="Periodo:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        ).pack(side="left", padx=10)

        for period, label in [("24h", "24 horas"), ("7d", "7 días"), ("30d", "30 días")]:
            rb = ctk.CTkRadioButton(
                self._controls_frame,
                text=label,
                variable=self._period_var,
                value=period,
                command=self._on_period_radio,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=10)
            StyleManager.style_radiobutton_ctk(rb)

        # Botón toggle del panel de rango
        self._toggle_btn = make_futuristic_button(
            self._controls_frame,
            text=f"{Icons.CALENDAR_RANGE}  Rango",
            command=self._toggle_range_panel,
            height=6,
            width=13
        )
        self._toggle_btn.pack(side="right", padx=10)

    def _create_range_panel(self, parent):
        """
        Crea un panel para seleccionar un rango de fechas con campos para inicio y fin.

        Args:
            parent: El padre del panel.

        Returns:
            None

        Raises:
            None
        """
        self._range_panel = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        # No se hace pack aquí → empieza oculto
        ctk.CTkLabel(
            self._range_panel,
            text="desde:",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(10, 2))

        self._date_start = ctk.CTkEntry(
            self._range_panel,
            textvariable=self._period_start,
            text_color=COLORS['text_dim'],
            width=300,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        # Limpiar al hacer foco si tiene el texto de ejemplo
        self._date_start.bind("<FocusIn>",  lambda e: self._entry_focus_in(self._date_start, self._period_start))
        self._date_start.bind("<FocusOut>", lambda e: self._entry_focus_out(self._date_start, self._period_start))
        self._date_start.pack(side="left", padx=(0, 4))
                # Entradas de fecha en la fila de controles (derecha)
        ctk.CTkLabel(
            self._range_panel,
            text="hasta:",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 2))

        self._date_end = ctk.CTkEntry(
            self._range_panel,
            textvariable=self._period_end,
            text_color=COLORS['text_dim'],
            width=300,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self._date_end.bind("<FocusIn>",  lambda e: self._entry_focus_in(self._date_end, self._period_end))
        self._date_end.bind("<FocusOut>", lambda e: self._entry_focus_out(self._date_end, self._period_end))
        self._date_end.pack(side="left", padx=(0, 4))


        # ── BOTÓN APLICAR ─────────────────────────────────────────
        self._apply_btn = make_futuristic_button(
            self._controls_frame,
            text="" + Icons.CHECK_MARK + "Aplicar",
            command=self._apply_custom_range,
            height=6,
            width=12,
            state="disabled"  # solo se habilita al abrir el panel, para evitar confusión
        )
        self._apply_btn.pack(side="right", padx=(10, 5))

    def _create_graphs_area(self, parent):
        """
        Crea el área de gráficas utilizando matplotlib integrado en Tkinter con canvas y toolbar.

        Args:
            parent: El widget padre donde se creará el área de gráficas.

        Returns:
            None

        Raises:
            None
        """
        graphs_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        graphs_frame.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))

        self._fig = Figure(figsize=(9, 20), facecolor=COLORS['bg_medium'])
        self._fig.set_tight_layout(True)

        self._canvas = FigureCanvasTkAgg(self._fig, master=graphs_frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill="both", expand=True, pady=0)

        # _toolbar invisible — sus métodos se invocan desde botones propios
        self._toolbar = NavigationToolbar2Tk(self._canvas, self)
        self._toolbar.pack_forget()

        # Sub-frame centrado dentro de la barra de herramientas
        _btn_row = ctk.CTkFrame(self._toolbar_container, fg_color="transparent")
        _btn_row.pack(expand=True)

        for text, cmd, w in [
            ("" + Icons.HOME + " Inicio",  self._toolbar.home,          12),
            ("" + Icons.SEARCH + " Zoom",    self._toolbar.zoom,           12),
            ("" + Icons.HAND + "️ Mover",  self._toolbar.pan,            12),
            ("" + Icons.SAVE + " Guardar",  self._export_figure_image,   12),
        ]:
            make_futuristic_button(
                _btn_row, text=text, command=cmd, height=6, width=w
            ).pack(side="left", padx=5, pady=4)

        self._canvas.mpl_connect('button_press_event',   self._on_click)
        self._canvas.mpl_connect('button_release_event', self._on_release)
        self._canvas.mpl_connect('motion_notify_event',  self._on_motion)

    def _create_stats_area(self, parent):
        """
        Crea el área de estadísticas en la ventana de historial.

        Args:
            parent: El padre del frame de estadísticas.

        Returns:
            None

        Raises:
            None
        """
        stats_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        stats_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            stats_frame,
            text="Estadísticas:",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(pady=(10, 5))

        self._stats_label = ctk.CTkLabel(
            stats_frame,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            justify="left"
        )
        self._stats_label.pack(pady=(0, 10), padx=20)

    def _create_buttons(self, parent):
        """
        Crea los botones de acción en la ventana de historial.

        Args:
            parent: El elemento padre donde se crearán los botones.

        Returns:
            None

        Raises:
            None
        """
        buttons = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        buttons.pack(fill="x", pady=10, padx=10)

        for text, cmd, side, w in [
            ("Actualizar",       self._update_data,    "left",  18),
            ("Exportar CSV",     self._export_csv,     "left",  18),
            ("Limpiar Antiguos", self._clean_old_data, "left",  18),
        ]:
            make_futuristic_button(
                buttons, text=text, command=cmd, width=w, height=6
            ).pack(side=side, padx=5)

    # ─────────────────────────────────────────────
    # Control del panel de rango
    # ─────────────────────────────────────────────

    def _toggle_range_panel(self):
        """
        Muestra u oculta la fila de OptionMenus de rango personalizado.

        Args: Ninguno

        Returns: Ninguno

        Raises: Ninguno
        """
        if self._range_panel.winfo_ismapped():
            self._range_panel.pack_forget()
            self._toggle_btn.configure(text=f"{Icons.CALENDAR_RANGE}  Rango")
            self._apply_btn.configure(state="disabled")
        else:
            # Insertar después del frame de controles de periodo
            self._range_panel.pack(
                fill="x", padx=10, pady=(10, 5),
                after=self._controls_frame
            )
            self._toggle_btn.configure(text="" + Icons.CLOSE_X + " Cerrar")
            self._apply_btn.configure(state="normal")


    # ─────────────────────────────────────────────
    # Lógica de actualización
    # ─────────────────────────────────────────────

    _PLACEHOLDER = "YYYY-MM-DD HH:MM"

    def _entry_focus_in(self, entry: ctk.CTkEntry, var: ctk.StringVar):
        """
        Establece el comportamiento al enfocar un campo de entrada de texto.

        Args:
            entry (ctk.CTkEntry): El campo de entrada de texto que ha obtenido el foco.
            var (ctk.StringVar): La variable asociada al campo de entrada de texto.

        """
        if var.get() == self._PLACEHOLDER:
            var.set("")
            entry.configure(text_color=COLORS['text'])

    def _entry_focus_out(self, entry: ctk.CTkEntry, var: ctk.StringVar):
        """
        Restaura el texto de ejemplo en gris cuando un campo de entrada pierde el foco y queda vacío.

        Args:
            entry (ctk.CTkEntry): El campo de entrada que perdió el foco.
            var (ctk.StringVar): La variable asociada al campo de entrada.

        Returns:
            None

        Raises:
            None
        """
        if var.get().strip() == "":
            var.set(self._PLACEHOLDER)
            entry.configure(text_color=COLORS['text_dim'])

    def _on_period_radio(self):
        """
        Desactiva el modo de rango personalizado y actualiza la ventana de historial al seleccionar un período fijo.

        Args: Ninguno

        Returns: Ninguno

        Raises: Ninguno
        """
        self._using_custom_range = False
        self._update_data()

    def _apply_custom_range(self):
        """
        Aplica un rango de fechas personalizado sin necesidad de interacción con el teclado.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        _PH = self._PLACEHOLDER
        start_dt_text = self._period_start.get().strip()
        end_dt_text   = self._period_end.get().strip()
        if start_dt_text == _PH: start_dt_text = ""
        if end_dt_text   == _PH: end_dt_text   = ""
        try:
            start_dt = datetime.strptime(start_dt_text, _DATE_FMT)
        except ValueError as e:
            custom_msgbox(self, f"Fecha de inicio inválida:\n{e}\n{Icons.ERROR} Error")
            return

        try:
            end_dt = datetime.strptime(end_dt_text, _DATE_FMT)
        except ValueError as e:
            custom_msgbox(self, f"Fecha de fin inválida:\n{e}\n{Icons.ERROR} Error")
            return

        if end_dt <= start_dt:
            custom_msgbox(self, "La fecha de fin debe ser\nposterior a la de inicio.", "" + Icons.WARNING + "️ Rango inválido")
            return

        if (end_dt - start_dt).days > 90:
            custom_msgbox(self, "El rango no puede superar 90 días.", "" + Icons.WARNING + "️ Rango demasiado amplio")
            return

        self._using_custom_range = True
        self._custom_start = start_dt
        self._custom_end   = end_dt

        logger.info(
            "[HistoryWindow] Rango aplicado: %s → %s",
            start_dt.strftime('%Y-%m-%d %H:%M'),
            end_dt.strftime('%Y-%m-%d %H:%M')
        )
        self._update_data()

    def _update_data(self):
        """
        Actualiza estadísticas y gráficas según el modo activo.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if self._using_custom_range:
            start = self._custom_start
            end   = self._custom_end
            stats = self._analyzer.get_stats_between(start, end)
            rango_label = f"{start.strftime('%Y-%m-%d %H:%M')} → {end.strftime('%Y-%m-%d %H:%M')}"
            hours = None  # no se usa en modo custom
        else:
            period = self._period_var.get()
            hours  = {"24h": 24, "7d": 24 * 7, "30d": 24 * 30}[period]
            stats  = self._analyzer.get_stats(hours)
            rango_label = period

        total_records = self._logger.get_metrics_count()
        db_size       = self._logger.get_db_size_mb()

        stats_text = (
            f"• CPU promedio: {stats.get('cpu_avg', 0):.1f}%  "
            f"(min: {stats.get('cpu_min', 0):.1f}%, max: {stats.get('cpu_max', 0):.1f}%)\n"
            f"• RAM promedio: {stats.get('ram_avg', 0):.1f}%  "
            f"(min: {stats.get('ram_min', 0):.1f}%, max: {stats.get('ram_max', 0):.1f}%)\n"
            f"• Temp promedio: {stats.get('temp_avg', 0):.1f}°C  "
            f"(min: {stats.get('temp_min', 0):.1f}°C, max: {stats.get('temp_max', 0):.1f}°C)\n"
            f"• Red Down: {stats.get('down_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('down_min', 0):.2f}, max: {stats.get('down_max', 0):.2f})\n"
            f"• Red Up: {stats.get('up_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('up_min', 0):.2f}, max: {stats.get('up_max', 0):.2f})\n"
            f"• Disk Read: {stats.get('disk_read_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('disk_read_min', 0):.2f}, max: {stats.get('disk_read_max', 0):.2f})\n"
            f"• Disk Write: {stats.get('disk_write_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('disk_write_min', 0):.2f}, max: {stats.get('disk_write_max', 0):.2f})\n"
            f"• PWM promedio: {stats.get('pwm_avg', 0):.0f}  "
            f"(min: {stats.get('pwm_min', 0):.0f}, max: {stats.get('pwm_max', 0):.0f})\n"
            f"• Actualizaciones disponibles promedio: {stats.get('updates_available_avg', 0):.2f}\n"
            f"• Actualizaciones disponibles (min: {stats.get('updates_available_min', 0)})\n"
            f"• Actualizaciones disponibles (max: {stats.get('updates_available_max', 0)})\n"
            f"• Uptime promedio: {stats.get('uptime_avg')}\n"
            f"• Uptime maximo: {stats.get('uptime_max')}\n"
            f"• Uptime minimo: {stats.get('uptime_min')}\n"
            f"• Muestras: {stats.get('total_samples', 0)} en {rango_label}\n"
            f"• Total registros: {total_records}  |  DB: {db_size:.2f} MB"
        )
        self._stats_label.configure(text=stats_text)

        if self._using_custom_range:
            self._update_graphs_between(self._custom_start, self._custom_end)
        else:
            self._update_graphs(hours)

    # ─────────────────────────────────────────────
    # Gráficas
    # ─────────────────────────────────────────────

    _METRICS = [
        ('cpu_percent',     'CPU %',           'primary'),
        ('ram_percent',     'RAM %',           'secondary'),
        ('temperature',     'Temp °C',         'danger'),
        ('net_download_mb', 'Red Down MB/s',   'primary'),
        ('net_upload_mb',   'Red Up MB/s',     'secondary'),
        ('disk_read_mb',    'Disk Read MB/s',  'primary'),
        ('disk_write_mb',   'Disk Write MB/s', 'secondary'),
        ('fan_pwm',         'PWM',             'warning'),
    ]

    def _update_graphs(self, hours: int):
        """
        Actualiza todas las gráficas de métricas para un período fijo en horas.

        Args:
            hours (int): Período en horas para el cual se actualizarán las gráficas.

        Returns:
            None

        Raises:
            None
        """
        self._fig.clear()
        axes = [self._fig.add_subplot(8, 1, i) for i in range(1, 9)]
        for (metric, ylabel, color_key), ax in zip(self._METRICS, axes):
            ts, vals = self._analyzer.get_graph_data(metric, hours)
            self._draw_metric(ax, ts, vals, ylabel, COLORS[color_key])
        self._fig.tight_layout()
        self._canvas.draw()

    def _update_graphs_between(self, start: datetime, end: datetime):
        """
        Actualiza todas las gráficas de métricas para un rango de fechas personalizado.

        Args:
            start (datetime): Fecha de inicio del rango.
            end (datetime): Fecha de fin del rango.

        Returns:
            None

        Raises:
            None
        """
        self._fig.clear()
        axes = [self._fig.add_subplot(8, 1, i) for i in range(1, 9)]
        for (metric, ylabel, color_key), ax in zip(self._METRICS, axes):
            ts, vals = self._analyzer.get_graph_data_between(metric, start, end)
            self._draw_metric(ax, ts, vals, ylabel, COLORS[color_key])
        self._fig.tight_layout()
        self._canvas.draw()

    def _draw_metric(self, ax, timestamps, values, ylabel: str, color: str):
        """
        Dibuja una métrica específica en su eje subplot con estilo configurado.

        Args:
            ax: Eje subplot donde se dibujará la métrica.
            timestamps: Fechas o timestamps de los datos a plotear.
            values: Valores de la métrica a plotear.
            ylabel: Etiqueta del eje Y.
            color: Color de la línea de la métrica.

        Returns:
            None

        Raises:
            Ninguna excepción relevante.
        """
        ax.set_facecolor(COLORS['bg_dark'])
        ax.tick_params(colors=COLORS['text'])
        ax.set_ylabel(ylabel, color=COLORS['text'])
        ax.set_xlabel('Tiempo', color=COLORS['text'])
        ax.grid(True, alpha=0.2)
        if timestamps:
            ax.plot(timestamps, values, color=color, linewidth=1.5)

    # ─────────────────────────────────────────────
    # Exportación
    # ─────────────────────────────────────────────

    def _export_csv(self):
        """
        Exporta los datos del período actual a archivo CSV en el directorio de exports.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Exception: Si ocurre un error durante la exportación.
        """
        if self._using_custom_range:
            start = self._custom_start
            end   = self._custom_end
            label = f"custom_{start.strftime('%Y%m%d%H%M')}_{end.strftime('%Y%m%d%H%M')}"
            path  = str(EXPORTS_CSV_DIR / f"history_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            try:
                self._analyzer.export_to_csv_between(path, start, end)
                custom_msgbox(self, f"Datos exportados a:\n{path}\n{Icons.OK} Exportado")
                try:
                    CleanupService().clean_csv()
                except Exception as ce:
                    logger.warning("[HistoryWindow] No se pudo limpiar CSV: %s", ce)
            except Exception as e:
                custom_msgbox(self, f"Error al exportar:\n{e}\n{Icons.ERROR} Error")
        else:
            period = self._period_var.get()
            hours  = {"24h": 24, "7d": 24 * 7, "30d": 24 * 30}[period]
            path   = str(EXPORTS_CSV_DIR / f"history_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            try:
                self._analyzer.export_to_csv(path, hours)
                custom_msgbox(self, f"Datos exportados a:\n{path}\n{Icons.OK} Exportado")
                try:
                    CleanupService().clean_csv()
                except Exception as ce:
                    logger.warning("[HistoryWindow] No se pudo limpiar CSV: %s", ce)
            except Exception as e:
                custom_msgbox(self, f"Error al exportar:\n{e}\n{Icons.ERROR} Error")

    def _clean_old_data(self):
        """
        Fuerza un ciclo de limpieza completo de datos antiguos a través del servicio de limpieza.

        Args: Ninguno

        Returns: Ninguno

        Raises: Exception si ocurre un error durante la limpieza.
        """
        status = self._cleanup_service.get_status()

        def do_clean():
            """Ejecuta la limpieza forzada y muestra resultados en mensaje."""
            try:
                result = self._cleanup_service.force_cleanup()
                msg = (
                    f"Limpieza completada:\n\n"
                    f"• CSV eliminados: {result['deleted_csv']}\n"
                    f"• PNG eliminados: {result['deleted_png']}\n"
                    f"• BD limpiada: {'Sí' if result['db_ok'] else 'No'}"
                )
                custom_msgbox(self, msg, "" + Icons.OK + " Limpiado")
                logger.info("[HistoryWindow] Limpieza manual completada: %s", result)
                self._update_data()
            except Exception as e:
                logger.error("[HistoryWindow] Error en limpieza manual: %s", e)
                custom_msgbox(self, f"Error al limpiar:\n{e}\n{Icons.ERROR} Error")

        confirm_dialog(
            parent=self,
            text=(
                f"¿Forzar limpieza ahora?\n\n"
                f"• CSV actuales: {status['csv_count']} (límite: {status['max_csv']})\n"
                f"• PNG actuales: {status['png_count']} (límite: {status['max_png']})\n"
                f"• BD: registros >'{status['db_days']}' días\n\n"
                f"Esto liberará espacio en disco."
            ),
            title="" + Icons.WARNING + "️ Confirmar Limpieza",
            on_confirm=do_clean,
            on_cancel=None
        )

    def _export_figure_image(self):
        """
        Exporta la figura actual de gráficas como imagen PNG al directorio de screenshots.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Exception: Si ocurre un error al guardar la imagen.
        """
        
        try:
            save_dir = str(EXPORTS_SCR_DIR)
            os.makedirs(save_dir, exist_ok=True)
            filepath = os.path.join(
                save_dir,
                f"graficas_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.png"
            )
            self._fig.savefig(
                filepath, dpi=150,
                facecolor=self._fig.get_facecolor(),
                bbox_inches='tight'
            )
            logger.info("[HistoryWindow] Figura guardada: %s", filepath)
            custom_msgbox(self, f"Imagen guardada en:\n{filepath}\n{Icons.OK} Captura Guardada")
            try:
                CleanupService().clean_png()
            except Exception as ce:
                logger.warning("[HistoryWindow] No se pudo limpiar PNG: %s", ce)
        except Exception as e:
            logger.error("[HistoryWindow] Error guardando imagen: %s", e)
            custom_msgbox(self, f"Error al guardar la imagen: {e}\n{Icons.ERROR} Error")

    # ─────────────────────────────────────────────
    # Eventos matplotlib
    # ─────────────────────────────────────────────

    def _on_click(self, event):
        """
        Maneja el evento de clic del mouse en el canvas de las gráficas.

        Args:
            event: Evento de clic del mouse.

        Raises:
            None

        Returns:
            None
        """
        if event.inaxes:
            logger.debug("Click en gráfica: x=%s, y=%s", event.xdata, event.ydata)

    def _on_release(self, event):
        """
        Maneja el evento de liberación del botón del mouse en el canvas.

        Args:
            event: El evento de liberación del botón del mouse.

        Returns:
            None

        Raises:
            None
        """
        pass

    def _on_motion(self, event):
        """
        Maneja el evento de movimiento del mouse sobre el canvas de gráficas.

        Args:
            event: Evento de movimiento del mouse.

        Returns:
            None

        Raises:
            None
        """
        pass
