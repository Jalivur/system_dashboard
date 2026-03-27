"""
Módulo de ventana de lanzadores para System Dashboard.

Proporciona una interfaz gráfica para ejecutar scripts del sistema configurados
en `config.settings.LAUNCHERS`. Cada lanzador muestra confirmación antes de
ejecución y abre terminal integrada para monitoreo en tiempo real.

Dependencias:
- customtkinter
- config.settings
- ui.styles, ui.widgets
- utils.system_utils, utils.logger
"""

import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, LAUNCHERS, Icons
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import confirm_dialog, terminal_dialog
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class LaunchersWindow(ctk.CTkToplevel):
    """Ventana de lanzadores de scripts del sistema"""
    
    def __init__(self, parent):
        """
        Inicializa la ventana de lanzadores.

        Args:
            parent: Widget padre (ventana principal del dashboard).

        Configura geometría, colores, título y crea la UI completa.
        """
        super().__init__(parent)
        
        self.system_utils = SystemUtils()
        
        self.title("Lanzadores")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        self._create_ui()
        logger.info("[LaunchersWindow] Ventana Abierta")

    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="LANZADORES",
            on_close=self.destroy,
        )
        
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
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
        
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        self._create_launcher_buttons(inner)
        
    
    def _create_launcher_buttons(self, parent):
        """Crea los botones de lanzadores en layout grid"""
        if not LAUNCHERS:
            no_launchers = ctk.CTkLabel(
                parent,
                text="No hay lanzadores configurados\n\nEdita config/settings.py para añadir scripts",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                justify="center"
            )
            no_launchers.pack(pady=50)
            return
        
        columns = 2
        
        for i, launcher in enumerate(LAUNCHERS):
            label = launcher.get("label", "Script")
            script_path = launcher.get("script", "")
            
            row = i // columns
            col = i % columns
            
            launcher_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
            launcher_frame.grid(row=row, column=col, sticky="nsew")
            
            btn = make_futuristic_button(
                launcher_frame,
                text=label,
                command=lambda s=script_path, l=label: self._run_script(s, l),
                width=40,
                height=15,
                font_size=FONT_SIZES['large']
            )
            btn.pack(pady=(10, 5), padx=10)
            
            path_label = ctk.CTkLabel(
                launcher_frame,
                text=script_path,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small']),
                wraplength=300
            )
            path_label.pack(pady=(0, 10), padx=10)
        
        for c in range(columns):
            parent.grid_columnconfigure(c, weight=1)
    
    def _run_script(self, script_path: str, label: str):
        """
        Ejecuta un script usando la terminal integrada tras confirmar.

        Args:
            script_path (str): Ruta absoluta al script ejecutable.
            label (str): Nombre descriptivo del lanzador para logging y UI.
        """
        def do_execute():
            """
            Función interna: Ejecuta el script en terminal integrada.

            Registra log de ejecución y abre diálogo de terminal con el script.
            """
            logger.info("[LaunchersWindow] Ejecutando script: '%s' → %s", label, script_path)
            terminal_dialog(
                parent=self,
                script_path=script_path,
                title=f"EJECUTANDO: {label.upper()}"
            )

        confirm_dialog(
            parent=self,
            text=f"¿Deseas iniciar el proceso '{label}'?\n\nArchivo: {script_path}",
            title="" + Icons.WARNING + "️ Lanzador de Sistema",
            on_confirm=do_execute
        )
