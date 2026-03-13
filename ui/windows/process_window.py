"""
Ventana de monitor de procesos
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.process_monitor import ProcessMonitor


class ProcessWindow(ctk.CTkToplevel):
    """Ventana de monitor de procesos"""

    def __init__(self, parent, process_monitor: ProcessMonitor):
        super().__init__(parent)

        # Referencias
        self._process_monitor = process_monitor

        # Estado
        self._search_var    = ctk.StringVar(master=self)
        self._filter_var    = ctk.StringVar(master=self, value="all")
        self._update_paused = False
        self._update_job    = None

        # Configurar ventana
        self.title("Monitor de Procesos")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        # Crear interfaz
        self._create_ui()

        # Iniciar actualización
        self._update()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        """Crea la interfaz de usuario"""
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(
            main,
            title="MONITOR DE PROCESOS",
            on_close=self.destroy,
        )

        # Stats debajo del header
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

        # Área de scroll para procesos
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

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

        self._process_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self._process_frame, anchor="nw", width=DSI_WIDTH - 50)
        self._process_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._content = self._process_frame

    # ── Controles ─────────────────────────────────────────────────────────────

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
            textvariable=self._search_var,
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

        for filter_type, label in [("all", "Todos"), ("user", "Usuario"), ("system", "Sistema")]:
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
        """Crea encabezados de columnas ordenables"""
        headers = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'])
        headers.pack(fill="x", padx=10, pady=(5, 0))

        headers.grid_columnconfigure(0, weight=1, minsize=20)
        headers.grid_columnconfigure(1, weight=4, minsize=200)
        headers.grid_columnconfigure(2, weight=2, minsize=100)
        headers.grid_columnconfigure(3, weight=1, minsize=80)
        headers.grid_columnconfigure(4, weight=1, minsize=80)
        headers.grid_columnconfigure(5, weight=1, minsize=100)

        columns = [
            ("PID",     "pid"),
            ("Proceso", "name"),
            ("Usuario", "username"),
            ("CPU%",    "cpu"),
            ("RAM%",    "memory"),
            ("Acción",  None),
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
                    width=50,
                    height=30
                )
            else:
                btn = ctk.CTkLabel(
                    headers,
                    text=label,
                    text_color=COLORS['text'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
                )

            btn.grid(row=0, column=i, sticky="n", padx=2, pady=5)

    # ── Callbacks de UI ───────────────────────────────────────────────────────

    def _on_sort_change(self, column: str):
        """Cambia el orden de procesos"""
        self._update_paused = True

        if self._process_monitor.sort_by == column:
            self._process_monitor.sort_reverse = not self._process_monitor.sort_reverse
        else:
            self._process_monitor.set_sort(column, reverse=True)

        self._update_now()
        self.after(2000, self._resume_updates)

    def _on_filter_change(self):
        """Cambia el filtro de procesos"""
        self._update_paused = True
        self._process_monitor.set_filter(self._filter_var.get())
        self._update_now()
        self.after(2000, self._resume_updates)

    def _on_search_change(self):
        """Callback cuando cambia la búsqueda — debounce 500 ms"""
        self._update_paused = True

        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)

        self._search_timer = self.after(500, self._do_search)

    def _do_search(self):
        """Ejecuta la búsqueda"""
        self._update_now()
        self.after(3000, self._resume_updates)

    def _resume_updates(self):
        """Reanuda las actualizaciones automáticas"""
        self._update_paused = False

    # ── Renderizado ───────────────────────────────────────────────────────────

    def _render_processes(self):
        """Actualiza stats y renderiza la lista de procesos (lógica compartida)."""
        stats = self._process_monitor.get_system_stats()
        self._stats_label.configure(
            text=(
                f"Procesos: {stats['total_processes']} | "
                f"CPU: {stats['cpu_percent']:.1f}% | "
                f"RAM: {stats['mem_used_gb']:.1f}/{stats['mem_total_gb']:.1f} GB "
                f"({stats['mem_percent']:.1f}%) | "
                f"Uptime: {stats['uptime']}"
            )
        )

        for widget in self._process_frame.winfo_children():
            widget.destroy()

        search_query = self._search_var.get()
        processes = (
            self._process_monitor.search_processes(search_query)
            if search_query
            else self._process_monitor.get_processes(limit=20)
        )

        for i, proc in enumerate(processes):
            self._create_process_row(proc, i)

    def _update_now(self):
        """Actualiza inmediatamente sin programar siguiente"""
        if not self.winfo_exists():
            return

        if self._update_job:
            self.after_cancel(self._update_job)
            self._update_job = None

        self._render_processes()

    def _update(self):
        """Bucle de actualización automática"""
        if not self.winfo_exists():
            return

        if not self._process_monitor.is_running():
            StyleManager.show_service_stopped_banner(self._content, "Process Monitor")
            self.after(UPDATE_MS, self._update)
            return

        if self._update_paused:
            self._update_job = self.after(UPDATE_MS * 2, self._update)
            return

        self._render_processes()
        self._update_job = self.after(UPDATE_MS * 2, self._update)

    def _create_process_row(self, proc: dict, row: int):
        """Crea una fila para un proceso"""
        bg_color  = COLORS['bg_dark'] if row % 2 == 0 else COLORS['bg_medium']
        row_frame = ctk.CTkFrame(self._process_frame, fg_color=bg_color)
        row_frame.pack(fill="x", pady=2, padx=10)

        row_frame.grid_columnconfigure(0, weight=1, minsize=70)
        row_frame.grid_columnconfigure(1, weight=3, minsize=300)
        row_frame.grid_columnconfigure(2, weight=2, minsize=100)
        row_frame.grid_columnconfigure(3, weight=1, minsize=80)
        row_frame.grid_columnconfigure(4, weight=1, minsize=80)
        row_frame.grid_columnconfigure(5, weight=1, minsize=100)

        cpu_color = COLORS[self._process_monitor.get_process_color(proc['cpu'])]
        mem_color = COLORS[self._process_monitor.get_process_color(proc['memory'])]

        # PID
        ctk.CTkLabel(
            row_frame,
            text=str(proc['pid']),
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="center"
        ).grid(row=0, column=0, sticky="n", padx=5, pady=5)

        # Nombre
        name_text = proc.get('display_name', proc['name'])
        ctk.CTkLabel(
            row_frame,
            text=name_text,
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=250,
            justify="left",
            anchor="center"
        ).grid(row=0, column=1, sticky="n", padx=5, pady=5)

        # Usuario
        ctk.CTkLabel(
            row_frame,
            text=proc['username'][:15],
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="center"
        ).grid(row=0, column=2, sticky="n", padx=5, pady=5)

        # CPU
        ctk.CTkLabel(
            row_frame,
            text=f"{proc['cpu']:.1f}%",
            text_color=cpu_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).grid(row=0, column=3, sticky="n", padx=5, pady=5)

        # RAM
        ctk.CTkLabel(
            row_frame,
            text=f"{proc['memory']:.1f}%",
            text_color=mem_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).grid(row=0, column=4, sticky="n", padx=5, pady=5)

        # Botón matar
        ctk.CTkButton(
            row_frame,
            text="Matar",
            command=lambda p=proc: self._kill_process(p),
            fg_color=COLORS['danger'],
            hover_color="#cc0000",
            width=70,
            height=25,
            font=(FONT_FAMILY, 9)
        ).grid(row=0, column=5, padx=5, pady=5)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _kill_process(self, proc: dict):
        """Mata un proceso con confirmación"""
        def do_kill():
            success, message = self._process_monitor.kill_process(proc['pid'])
            title = "Proceso Terminado" if success else "Error"
            custom_msgbox(self, message, title)
            self._update_now()

        confirm_dialog(
            parent=self,
            text=f"¿Matar proceso '{proc['name']}'?\n\nPID: {proc['pid']}\nCPU: {proc['cpu']:.1f}%",
            title="" + Icons.WARNING + "️ Confirmar",
            on_confirm=do_kill,
            on_cancel=None
        )
