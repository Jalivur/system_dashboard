"""
Estilos y temas para la interfaz
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES


class StyleManager:
    """Gestor centralizado de estilos"""
    
    @staticmethod
    def style_radiobutton_tk(rb: tk.Radiobutton, 
                            fg: str = None, 
                            bg: str = None, 
                            hover_fg: str = None) -> None:
        """
        Aplica estilo a radiobutton de tkinter
        
        Args:
            rb: Widget radiobutton
            fg: Color de texto
            bg: Color de fondo
            hover_fg: Color al pasar el mouse
        """
        fg = fg or COLORS['primary']
        bg = bg or COLORS['bg_dark']
        hover_fg = hover_fg or COLORS['success']
        
        rb.config(
            fg=fg, 
            bg=bg, 
            selectcolor=bg, 
            activeforeground=fg, 
            activebackground=bg,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), 
            indicatoron=True
        )
        
        def on_enter(e): 
            rb.config(fg=hover_fg)
        
        def on_leave(e): 
            rb.config(fg=fg)
        
        rb.bind("<Enter>", on_enter)
        rb.bind("<Leave>", on_leave)
    
    @staticmethod
    def style_radiobutton_ctk(rb: ctk.CTkRadioButton) -> None:
        """
        Aplica estilo a radiobutton de customtkinter
        
        Args:
            rb: Widget radiobutton
        """
        rb.configure(
            radiobutton_width=25,
            radiobutton_height=25,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            fg_color=COLORS['primary'],
        )
    
    @staticmethod
    def style_slider(slider: tk.Scale, color: str = None) -> None:
        """
        Aplica estilo a slider de tkinter
        
        Args:
            slider: Widget slider
            color: Color personalizado
        """
        color = color or COLORS['primary']
        slider.config(
            troughcolor=COLORS['secondary'], 
            sliderrelief="flat", 
            bd=0,
            highlightthickness=0, 
            fg=color, 
            bg=COLORS['bg_dark'], 
            activebackground=color
        )
    
    @staticmethod
    def style_slider_ctk(slider: ctk.CTkSlider, color: str = None) -> None:
        """
        Aplica estilo a slider de customtkinter
        
        Args:
            slider: Widget slider
            color: Color personalizado
        """
        color = color or COLORS['primary']  # ✓ Usar tema
        slider.configure(
            fg_color=COLORS['bg_light'],
            progress_color=color,
            button_color=color,
            button_hover_color=COLORS['secondary'],
            height=30
        )
    
    @staticmethod
    def style_scrollbar(sb: tk.Scrollbar, color: str = None) -> None:
        """
        Aplica estilo a scrollbar de tkinter
        
        Args:
            sb: Widget scrollbar
            color: Color personalizado
        """
        color = color or COLORS['bg_dark']
        sb.config(
            troughcolor=COLORS['secondary'], 
            bg=color, 
            activebackground=color,
            highlightthickness=0, 
            relief="flat"
        )
    
    @staticmethod
    def style_scrollbar_ctk(sb: ctk.CTkScrollbar, color: str = None) -> None:
        """
        Aplica estilo a scrollbar de customtkinter
        
        Args:
            sb: Widget scrollbar
            color: Color personalizado
        """
        color = color or COLORS['primary']  # ✓ Usar tema
        sb.configure(
            bg_color=COLORS['bg_medium'],
            button_color=color,
            button_hover_color=COLORS['secondary']
        )
    
    @staticmethod
    def style_ctk_scrollbar(scrollable_frame: ctk.CTkScrollableFrame, 
                           color: str = None) -> None:
        """
        Aplica estilo a scrollable frame de customtkinter
        
        Args:
            scrollable_frame: Widget scrollable frame
            color: Color personalizado
        """
        color = color or COLORS['primary']  # ✓ Usar tema
        scrollable_frame.configure(
            scrollbar_fg_color=COLORS['bg_medium'],
            scrollbar_button_color=color,
            scrollbar_button_hover_color=COLORS['secondary']
        )


def make_futuristic_button(parent, text: str, command=None, 
                          width: int = None, height: int = None, 
                          font_size: int = None, state: str = "normal") -> ctk.CTkButton:
    """
    Crea un botón con estilo futurista
    
    Args:
        parent: Widget padre
        text: Texto del botón
        command: Función a ejecutar al hacer clic
        width: Ancho en unidades
        height: Alto en unidades
        font_size: Tamaño de fuente
        
    Returns:
        Widget CTkButton configurado
    """
    width = width or 20
    height = height or 10
    font_size = font_size or FONT_SIZES['large']
    
    btn = ctk.CTkButton(
        parent, 
        text=text, 
        command=command,
        fg_color=COLORS['bg_dark'], 
        hover_color=COLORS['bg_light'],
        border_width=3, 
        border_color=COLORS['border'],
        width=width * 8, 
        height=height * 8,
        font=(FONT_FAMILY, font_size, "bold"), 
        corner_radius=10,
        state=state
    )
    
    def on_enter(e): 
        btn.configure(fg_color=COLORS['bg_light'])
    
    def on_leave(e): 
        btn.configure(fg_color=COLORS['bg_dark'])
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn


def make_window_header(parent, title: str, on_close, status_text: str = None) -> ctk.CTkFrame:
    """
    Crea una barra de cabecera unificada para ventanas de monitoreo.

    Layout (altura fija 48px):
    ┌─────────────────────────────────────────────────────────┐
    │  ● TÍTULO DE VENTANA      status_text opcional   [✕]   │
    └─────────────────────────────────────────────────────────┘

    El indicador ● usa COLORS['secondary'] para identificar
    visualmente que es una ventana hija del dashboard.

    Args:
        parent:      Widget padre (normalmente el frame main de la ventana).
        title:       Texto del título en mayúsculas (ej. "MONITOR DEL SISTEMA").
        on_close:    Callable ejecutado al pulsar el botón ✕.
        status_text: Texto informativo opcional a la derecha del título
                     (ej. "CPU 12% · RAM 45% · 52°C"). Si es None no se muestra.

    Returns:
        CTkFrame de cabecera ya empaquetado con pack(fill="x").
        Guarda referencia al label de estado en frame.status_label
        para que la ventana pueda actualizarlo dinámicamente.
    """
    # ── Contenedor ───────────────────────────────────────────────────────────
    header = ctk.CTkFrame(
        parent,
        fg_color=COLORS['bg_dark'],
        height=56,
        corner_radius=8,
    )
    header.pack(fill="x", padx=5, pady=(5, 0))
    header.pack_propagate(False)  # Altura fija

    # Separador inferior (línea decorativa)
    separator = ctk.CTkFrame(
        parent,
        fg_color=COLORS['border'],
        height=1,
        corner_radius=0,
    )
    separator.pack(fill="x", padx=5, pady=(0, 4))

    # ── Indicador de color (pastilla izquierda) ───────────────────────────
    dot = ctk.CTkLabel(
        header,
        text="●",
        text_color=COLORS['secondary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
        width=28,
    )
    dot.pack(side="left", padx=(10, 2))

    # ── Título ────────────────────────────────────────────────────────────
    title_lbl = ctk.CTkLabel(
        header,
        text=title,
        text_color=COLORS['secondary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
        anchor="w",
    )
    title_lbl.pack(side="left", padx=(0, 10))

    # ── Botón cerrar (derecha) ────────────────────────────────────────────
    close_btn = ctk.CTkButton(
        header,
        text="✕",
        command=on_close,
        width=52,
        height=42,
        fg_color=COLORS['bg_medium'],
        hover_color=COLORS['danger'],
        border_width=3,
        border_color=COLORS['border'],
        font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
        corner_radius=6,
    )
    close_btn.pack(side="right", padx=(0, 8))

    # ── Status label (derecha del título, izquierda del botón) ───────────
    status_lbl = ctk.CTkLabel(
        header,
        text=status_text or "",
        text_color=COLORS['text_dim'],
        font=(FONT_FAMILY, FONT_SIZES['small']),
        anchor="e",
    )
    status_lbl.pack(side="right", padx=(0, 12), expand=True, fill="x")

    # Referencia pública para actualizaciones dinámicas
    header.status_label = status_lbl

    return header
