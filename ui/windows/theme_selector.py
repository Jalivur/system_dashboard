"""
Ventana de selección de temas
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from config.themes import get_available_themes, get_theme, save_selected_theme, load_selected_theme
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox, confirm_dialog
import sys
import os
from utils.logger import get_logger

logger = get_logger(__name__)


class ThemeSelector(ctk.CTkToplevel):
    """Ventana de selección de temas"""
    
    def __init__(self, parent):
        """Inicializa la ventana selector de temas del dashboard.

        Args:
            parent: Widget padre CTkToplevel del dashboard.
        """
        super().__init__(parent)
        
        # Configurar ventana
        self.title("Selector de Temas")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        # Tema actualmente seleccionado
        self.current_theme = load_selected_theme()
        self.selected_theme_var = ctk.StringVar(master=self, value=self.current_theme)
        
        # Crear interfaz
        self._create_ui()
        logger.info("[ThemeSelector] Ventana Abierta")

    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="SELECTOR DE TEMAS",
            on_close=self.destroy,
            status_text="Elige un tema y reinicia el dashboard para aplicarlo",
        )
        
        # Área de scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas y scrollbar
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
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Crear tarjetas de temas
        self._create_theme_cards(inner)
        
        # Botones inferiores
        self._create_bottom_buttons(main)
    
    def _create_theme_cards(self, parent):
        """Crea las tarjetas de cada tema"""
        themes = get_available_themes()
        
        for theme_id, theme_name in themes:
            theme_data = get_theme(theme_id)
            colors = theme_data["colors"]
            
            # Frame de la tarjeta
            is_current = (theme_id == self.current_theme)
            border_color = COLORS['success'] if is_current else COLORS['primary']
            border_width = 3 if is_current else 2
            
            card = ctk.CTkFrame(
                parent,
                fg_color=COLORS['bg_dark'],
                border_width=border_width,
                border_color=border_color
            )
            card.pack(fill="x", pady=8, padx=10)
            
            # Radiobutton para seleccionar
            radio = ctk.CTkRadioButton(
                card,
                text=theme_name,
                variable=self.selected_theme_var,
                value=theme_id,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
                command=lambda: self._on_theme_change()
            )
            radio.pack(anchor="w", padx=15, pady=(10, 5))
            StyleManager.style_radiobutton_ctk(radio)
            
            # Indicador de tema actual
            if is_current:
                current_label = ctk.CTkLabel(
                    card,
                    text="" + Icons.CHECK_MARK + " TEMA ACTUAL",
                    text_color=COLORS['success'],
                    font=(FONT_FAMILY, 10, "bold")
                )
                current_label.pack(anchor="w", padx=15, pady=(0, 5))
            
            # Frame de preview de colores
            preview_frame = ctk.CTkFrame(card, fg_color=COLORS['bg_medium'])
            preview_frame.pack(fill="x", padx=15, pady=(5, 10))
            
            # Mostrar colores principales
            color_samples = [
                ("Principal", colors['primary']),
                ("Secundario", colors['secondary']),
                ("Éxito", colors['success']),
                ("Advertencia", colors['warning']),
                ("Peligro", colors['danger']),
                ("Fondo oscuro", colors['bg_dark']),
                ("Fondo medio", colors['bg_medium']),
                ("Fondo claro", colors['bg_light']),
                ("Texto", colors['text']),
                ("Bordes", colors['border'])
            ]
            
            for i, (label, color) in enumerate(color_samples):
                color_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
                color_frame.grid(row=0, column=i, padx=5, pady=5)
                
                # Cuadrado de color
                color_box = ctk.CTkFrame(
                    color_frame,
                    width=40,
                    height=40,
                    fg_color=color,
                    border_width=1,
                    border_color=COLORS['text']
                )
                color_box.pack()
                color_box.pack_propagate(False)
                
                # Label
                color_label = ctk.CTkLabel(
                    color_frame,
                    text=label,
                    text_color=COLORS['text'],
                    font=(FONT_FAMILY, 9)
                )
                color_label.pack(pady=(2, 0))
    
    def _create_bottom_buttons(self, parent):
        """Crea los botones inferiores"""
        bottom = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)
        
        # Botón aplicar
        apply_btn = make_futuristic_button(
            bottom,
            text="Aplicar y Reiniciar",
            command=self._apply_theme,
            width=20,
            height=6
        )
        apply_btn.pack(side="right", padx=5)
    
    def _on_theme_change(self):
        """Callback cuando se selecciona un tema"""
        # Simplemente actualiza la variable, no aplica aún
        pass
    
    def _apply_theme(self):
        """Aplica el tema seleccionado y reinicia la aplicación"""
        selected = self.selected_theme_var.get()
        
        if selected == self.current_theme:
            custom_msgbox(
                self,
                "Este tema ya está activo.\nNo es necesario reiniciar.",
                "Tema Actual"
            )
            return
        
        # Guardar tema seleccionado
        save_selected_theme(selected)
        
        # Mostrar confirmación y reiniciar
        theme_name = get_theme(selected)["name"]
        

        
        def do_restart():
            """Reinicia la aplicación"""
            
            
            # Cerrar ventana de temas
            self.destroy()
            
            # Obtener el script principal
            python = sys.executable
            script = os.path.abspath(sys.argv[0])
            
            # Cerrar aplicación actual
            self.master.quit()
            self.master.destroy()
            
            # Reiniciar con os.execv (reemplaza el proceso actual)
            os.execv(python, [python, script] + sys.argv[1:])
        
        # Confirmar antes de reiniciar
        confirm_dialog(
            parent=self,
            text=f"Tema '{theme_name}' guardado.\n\n¿Reiniciar ahora para aplicar los cambios?",
            title= f"{Icons.REFRESH} Aplicar Tema",
            on_confirm=do_restart,
            on_cancel=self.destroy
        )
