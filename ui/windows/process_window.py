"""
Ventana de monitor de procesos
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.process_monitor import ProcessMonitor


class ProcessWindow(ctk.CTkToplevel):
    """Ventana de monitor de procesos"""
    
    def __init__(self, parent, process_monitor: ProcessMonitor):
        super().__init__(parent)
        
        # Referencias
        self.process_monitor = process_monitor
        
        # Estado
        self.search_var = ctk.StringVar()
        self.filter_var = ctk.StringVar(value="all")
        self.process_labels = []  # Lista de labels de procesos
        self.update_paused = False  # Flag para pausar actualización
        self.update_job = None  # ID del trabajo de actualización
        
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
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="MONITOR DE PROCESOS",
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
        
        # Área de scroll para procesos (con altura limitada)
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Limitar altura del canvas para que el botón cerrar sea visible
        max_height = DSI_HEIGHT - 300  # Dejar espacio para header, controles y botón
        
        # Canvas y scrollbar
        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=max_height  # Altura máxima
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
        
        # Frame interno para procesos
        self.process_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self.process_frame, anchor="nw", width=DSI_WIDTH-50)
        self.process_frame.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._content = self.process_frame
        # Botón cerrar
        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=5, padx=10)
        
    
    
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
        
        for filter_type, label in [("all", "Todos"), ("user", "Usuario"), ("system", "Sistema")]:
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
            from ui.styles import StyleManager
            StyleManager.style_radiobutton_ctk(rb)
    
    def _create_column_headers(self, parent):
        """Crea encabezados de columnas ordenables"""
        headers = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'])
        headers.pack(fill="x", padx=10, pady=(5, 0))
        
        # Configurar grid
        headers.grid_columnconfigure(0, weight=1, minsize=20)   # PID
        headers.grid_columnconfigure(1, weight=4, minsize=200)  # Nombre
        headers.grid_columnconfigure(2, weight=2, minsize=100)  # Usuario
        headers.grid_columnconfigure(3, weight=1, minsize=80)   # CPU
        headers.grid_columnconfigure(4, weight=1, minsize=80)   # RAM
        headers.grid_columnconfigure(5, weight=1, minsize=100)  # Acción
        
        # Crear headers
        columns = [
            ("PID", "pid"),
            ("Proceso", "name"),
            ("Usuario", "username"),
            ("CPU%", "cpu"),
            ("RAM%", "memory"),
            ("Acción", None)
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
    
    def _on_sort_change(self, column: str):
        """Cambia el orden de procesos"""
        # Pausar actualización automática temporalmente
        self.update_paused = True
        
        # Si ya estaba ordenado por esta columna, invertir
        if self.process_monitor.sort_by == column:
            self.process_monitor.sort_reverse = not self.process_monitor.sort_reverse
        else:
            self.process_monitor.set_sort(column, reverse=True)
        
        # Actualizar inmediatamente
        self._update_now()
        
        # Reanudar actualización después de 2 segundos
        self.after(2000, self._resume_updates)
    
    def _on_filter_change(self):
        """Cambia el filtro de procesos"""
        # Pausar actualización automática temporalmente
        self.update_paused = True
        
        self.process_monitor.set_filter(self.filter_var.get())
        
        # Actualizar inmediatamente
        self._update_now()
        
        # Reanudar actualización después de 2 segundos
        self.after(2000, self._resume_updates)
    
    def _update_now(self):
        """Actualiza inmediatamente sin programar siguiente"""
        if not self.winfo_exists():
            return
        
        # Cancelar actualización programada si existe
        if self.update_job:
            self.after_cancel(self.update_job)
            self.update_job = None
        
        # Actualizar estadísticas del sistema
        stats = self.process_monitor.get_system_stats()
        self.stats_label.configure(
            text=f"Procesos: {stats['total_processes']} | "
                 f"CPU: {stats['cpu_percent']:.1f}% | "
                 f"RAM: {stats['mem_used_gb']:.1f}/{stats['mem_total_gb']:.1f} GB ({stats['mem_percent']:.1f}%) | "
                 f"Uptime: {stats['uptime']}"
        )
        
        # Limpiar procesos anteriores
        for widget in self.process_frame.winfo_children():
            widget.destroy()
        self.process_labels = []
        
        # Obtener procesos
        search_query = self.search_var.get()
        if search_query:
            processes = self.process_monitor.search_processes(search_query)
        else:
            processes = self.process_monitor.get_processes(limit=20)
        
        # Mostrar procesos
        for i, proc in enumerate(processes):
            self._create_process_row(proc, i)
    
    def _resume_updates(self):
        """Reanuda las actualizaciones automáticas"""
        self.update_paused = False
    
    def _on_search_change(self):
        """Callback cuando cambia la búsqueda"""
        # Pausar actualización automática temporalmente
        self.update_paused = True
        
        # Cancelar timer anterior si existe
        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)
        
        # Actualizar después de 500ms (debounce)
        self._search_timer = self.after(500, self._do_search)
    
    def _do_search(self):
        """Ejecuta la búsqueda"""
        self._update_now()
        # Reanudar actualización después de 3 segundos
        self.after(3000, self._resume_updates)
    
    def _update(self):
        """Actualiza la lista de procesos"""
        
        if not self.winfo_exists():
            return
        if not self.process_monitor._running:
            StyleManager.show_service_stopped_banner(self._content, "Process Monitor")
            self.after(UPDATE_MS, self._update)
            return
        # Si está pausada, reprogramar y salir
        if self.update_paused:
            self.update_job = self.after(UPDATE_MS * 2, self._update)
            return
        
        # Actualizar estadísticas del sistema
        stats = self.process_monitor.get_system_stats()
        self.stats_label.configure(
            text=f"Procesos: {stats['total_processes']} | "
                 f"CPU: {stats['cpu_percent']:.1f}% | "
                 f"RAM: {stats['mem_used_gb']:.1f}/{stats['mem_total_gb']:.1f} GB ({stats['mem_percent']:.1f}%) | "
                 f"Uptime: {stats['uptime']}"
        )
        
        # Limpiar procesos anteriores
        for widget in self.process_frame.winfo_children():
            widget.destroy()
        self.process_labels = []
        
        # Obtener procesos
        search_query = self.search_var.get()
        if search_query:
            processes = self.process_monitor.search_processes(search_query)
        else:
            processes = self.process_monitor.get_processes(limit=20)
        
        # Mostrar procesos
        for i, proc in enumerate(processes):
            self._create_process_row(proc, i)
        
        # Programar siguiente actualización
        self.update_job = self.after(UPDATE_MS * 2, self._update)  # Cada 4 segundos
    
    def _create_process_row(self, proc: dict, row: int):
        """Crea una fila para un proceso"""
        # Frame de la fila (sin altura fija, se adapta al contenido)
        bg_color = COLORS['bg_dark'] if row % 2 == 0 else COLORS['bg_medium']
        row_frame = ctk.CTkFrame(self.process_frame, fg_color=bg_color)
        row_frame.pack(fill="x", pady=2, padx=10)  # Más padding vertical
        
        # Configurar grid igual que headers
        row_frame.grid_columnconfigure(0, weight=1, minsize=70)
        row_frame.grid_columnconfigure(1, weight=3, minsize=300)
        row_frame.grid_columnconfigure(2, weight=2, minsize=100)
        row_frame.grid_columnconfigure(3, weight=1, minsize=80)
        row_frame.grid_columnconfigure(4, weight=1, minsize=80)
        row_frame.grid_columnconfigure(5, weight=1, minsize=100)
        
        # Colores según uso
        cpu_color = COLORS[self.process_monitor.get_process_color(proc['cpu'])]
        mem_color = COLORS[self.process_monitor.get_process_color(proc['memory'])]
        
        # PID
        ctk.CTkLabel(
            row_frame,
            text=str(proc['pid']),
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="center"
        ).grid(row=0, column=0, sticky="n", padx=5, pady=5)  # nw = arriba izquierda
        
        # Nombre (mostrar display_name que es más descriptivo)
        name_text = proc.get('display_name', proc['name'])
        name_label = ctk.CTkLabel(
            row_frame,
            text=name_text,  # Sin truncar
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=250,  # Ajustar texto en 350px de ancho
            justify="left",
            anchor="center"
        )
        name_label.grid(row=0, column=1, sticky="n", padx=5, pady=5)  # nw = arriba izquierda
        
        # Usuario
        ctk.CTkLabel(
            row_frame,
            text=proc['username'][:15],
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="center"
        ).grid(row=0, column=2, sticky="n", padx=5, pady=5)  # nw = arriba izquierda
        
        # CPU
        ctk.CTkLabel(
            row_frame,
            text=f"{proc['cpu']:.1f}%",
            text_color=cpu_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).grid(row=0, column=3, sticky="n", padx=5, pady=5)  # ne = arriba derecha
        
        # RAM
        ctk.CTkLabel(
            row_frame,
            text=f"{proc['memory']:.1f}%",
            text_color=mem_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).grid(row=0, column=4, sticky="n", padx=5, pady=5)  # ne = arriba derecha
        
        # Botón matar
        kill_btn = ctk.CTkButton(
            row_frame,
            text="Matar",
            command=lambda p=proc: self._kill_process(p),
            fg_color=COLORS['danger'],
            hover_color="#cc0000",
            width=70,
            height=25,
            font=(FONT_FAMILY, 9)
        )
        kill_btn.grid(row=0, column=5, padx=5, pady=5)  # centrado
    
    def _kill_process(self, proc: dict):
        """Mata un proceso con confirmación"""
        def do_kill():
            success, message = self.process_monitor.kill_process(proc['pid'])
            
            if success:
                title = "Proceso Terminado"
            else:
                title = "Error"
            
            custom_msgbox(self, message, title)
            self._update()  # Actualizar lista
        
        # Confirmar
        confirm_dialog(
            parent=self,
            text=f"¿Matar proceso '{proc['name']}'?\n\nPID: {proc['pid']}\nCPU: {proc['cpu']:.1f}%",
            title="⚠️ Confirmar",
            on_confirm=do_kill,
            on_cancel=None
        )
