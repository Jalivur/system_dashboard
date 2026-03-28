"""
Estilos y temas para la interfaz
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, Icons


class StyleManager:
    """
    Establece el estilo para un radiobutton de tkinter.

    Args:
        rb (tk.Radiobutton): Widget radiobutton a estilizar.
        fg (str, opcional): Color de texto. Por defecto, COLORS['primary'].
        bg (str, opcional): Color de fondo. Por defecto, COLORS['bg_dark'].
        hover_fg (str, opcional): Color de texto al pasar el mouse. Por defecto, COLORS['success'].

    Returns:
        None
    """
    
    @staticmethod
    def style_radiobutton_tk(rb: tk.Radiobutton, 
                            fg: str = None, 
                            bg: str = None, 
                            hover_fg: str = None) -> None:
        """
        Aplica estilo personalizado a un widget Radiobutton de tkinter.

        Args:
            rb (tk.Radiobutton): El widget Radiobutton a estilizar.
            fg (str, opcional): Color del texto. Por defecto, None.
            bg (str, opcional): Color de fondo. Por defecto, None.
            hover_fg (str, opcional): Color del texto al pasar el mouse. Por defecto, None.

        Returns:
            None

        Raises:
            None
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
            """
            Efecto hover: cambia color de texto al entrar el mouse
            """
            rb.config(fg=hover_fg)
        
        def on_leave(e): 
            """
            Restaura color original al salir el mouse
            """
            rb.config(fg=fg)
        
        rb.bind("<Enter>", on_enter)
        rb.bind("<Leave>", on_leave)
    
    @staticmethod
    def style_radiobutton_ctk(rb: ctk.CTkRadioButton, radiobutton_width: int = 25, radiobutton_height: int = 25) -> None:
        """
        Aplica estilo personalizado a un widget CTkRadioButton de customtkinter.

        Args:
            rb (ctk.CTkRadioButton): El widget radiobutton a estilizar.
            radiobutton_width (int): Ancho del radiobutton. Por defecto 25.
            radiobutton_height (int): Alto del radiobutton. Por defecto 25.

        Returns:
            None
        """
        rb.configure(
            radiobutton_width=radiobutton_width,
            radiobutton_height=radiobutton_height,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            fg_color=COLORS['primary'],
        )
    
    @staticmethod
    def style_slider(slider: tk.Scale, color: str = None) -> None:
        """
        Aplica estilo personalizado a un widget slider de tkinter.

        Args:
            slider (tk.Scale): El widget slider a estilizar.
            color (str, opcional): Color personalizado para el slider. Por defecto es None.

        Returns:
            None

        Raises:
            None
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
    def style_slider_ctk(slider: ctk.CTkSlider, color: str = None, height=30) -> None:
        """
        Aplica estilo personalizado a un widget CTkSlider de customtkinter.

        Args:
            slider (ctk.CTkSlider): El widget slider a personalizar.
            color (str, opcional): Color personalizado para el slider. Por defecto, None.
            height (int, opcional): Altura del slider. Por defecto, 30.

        Returns:
            None

        Raises:
            Ninguna excepción específica.
        """
        color = color or COLORS['primary']  # " + Icons.CHECK_MARK + " Usar tema
        slider.configure(
            fg_color=COLORS['bg_light'],
            progress_color=color,
            button_color=color,
            button_hover_color=COLORS['secondary'],
            height=height
        )
    
    @staticmethod
    def style_scrollbar(sb: tk.Scrollbar, color: str = None) -> None:
        """
        Aplica estilo personalizado a un widget Scrollbar de tkinter.

        Args:
            sb (tk.Scrollbar): El widget Scrollbar a estilizar.
            color (str, opcional): Color personalizado para el scrollbar. Por defecto, None.

        Returns:
            None

        Raises:
            Ninguna excepción específica.
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
        Aplica estilo personalizado a un scrollbar de customtkinter.

        Args:
            sb (ctk.CTkScrollbar): Widget scrollbar a personalizar.
            color (str, opcional): Color personalizado para el scrollbar. Por defecto, usa el color primario del tema.

        Returns:
            None

        Raises:
            Ninguna excepción específica.
        """
        color = color or COLORS['primary']  # " + Icons.CHECK_MARK + " Usar tema
        sb.configure(
            bg_color=COLORS['bg_medium'],
            button_color=color,
            button_hover_color=COLORS['secondary']
        )
    
    @staticmethod
    def style_ctk_scrollbar(scrollable_frame: ctk.CTkScrollableFrame, 
                           color: str = None) -> None:
        """
        Aplica estilo personalizado al scrollbar de un CTkScrollableFrame de customtkinter.

        Args:
            scrollable_frame (ctk.CTkScrollableFrame): El widget CTkScrollableFrame a estilizar.
            color (str, opcional): Color personalizado para los botones del scrollbar. Por defecto, None.

        Returns:
            None

        Raises:
            Ninguna excepción específica.
        """
        color = color or COLORS['primary']  # " + Icons.CHECK_MARK + " Usar tema
        scrollable_frame.configure(
            scrollbar_fg_color=COLORS['bg_medium'],
            scrollbar_button_color=color,
            scrollbar_button_hover_color=COLORS['secondary']
        )
    @staticmethod
    def show_service_stopped_banner(parent_frame, service_name: str) -> None:
        """
        Muestra un banner indicando que un servicio ha detenido su ejecución.

        Args:
            parent_frame: La ventana padre donde se mostrará el banner.
            service_name (str): El nombre del servicio que ha detenido su ejecución.

        Returns:
            None

        Raises:
            None
        """
        for w in parent_frame.winfo_children():
            w.destroy()

        banner = ctk.CTkFrame(parent_frame, fg_color=COLORS['bg_dark'], corner_radius=10)
        banner.pack(expand=True, padx=40, pady=60)

        ctk.CTkLabel(
            banner,
            text= Icons.NO_ENTRY,
            font=(FONT_FAMILY, 48),
            text_color=COLORS['danger'],
        ).pack(pady=(30, 8))

        ctk.CTkLabel(
            banner,
            text=f"{service_name} detenido",
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
            text_color=COLORS['danger'],
        ).pack()

        ctk.CTkLabel(
            banner,
            text="Inícialo desde\nGestor de Servicios",
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text_dim'],
            justify="center",
        ).pack(pady=(6, 30))


def make_futuristic_button(parent, text: str, command=None, 
                          width: int = None, height: int = None, 
                          font_size: int = None, state: str = "normal") -> ctk.CTkButton:
    """
    Crea un botón con estilo futurista.

    Args:
        parent: Widget padre.
        text (str): Texto del botón.
        command: Función a ejecutar al hacer clic.
        width (int): Ancho en unidades. Por defecto None.
        height (int): Alto en unidades. Por defecto None.
        font_size (int): Tamaño de fuente. Por defecto None.
        state (str): Estado del botón. Por defecto 'normal'.

    Returns:
        ctk.CTkButton: Widget CTkButton configurado.

    Raises:
        Ninguna excepción específica.
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
        """
        Efecto hover: cambia color de fondo al entrar el mouse
        """
        btn.configure(fg_color=COLORS['bg_light'])
    
    def on_leave(e): 
        """
        Restaura color original al salir el mouse
        """
        btn.configure(fg_color=COLORS['bg_dark'])
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn


def make_window_header(parent, title: str, on_close, status_text: str = None) -> ctk.CTkFrame:
    """
    Crea una barra de cabecera unificada para ventanas de monitoreo.

        Args:
            parent:      Widget padre (normalmente el frame main de la ventana).
            title:       Texto del título en mayúsculas.
            on_close:    Callable ejecutado al pulsar el botón de cierre.
            status_text: Texto informativo opcional a la derecha del título.

        Returns:
            CTkFrame de cabecera ya empaquetado con pack(fill="x").

        Raises:
            Ninguno.
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
        text=Icons.GREEN_CIRCLE,
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
        text= Icons.CLOSE_X,
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


def make_homebridge_switch(
    parent,
    text: str,
    command=None,
    is_on: bool = False,
    disabled: bool = False,
) -> ctk.CTkSwitch:
    """
    Crea un CTkSwitch estilado para el control de accesorios Homebridge.

    Args:
        parent:   Widget padre (normalmente la tarjeta CTkFrame).
        text:     Etiqueta del switch (nombre del dispositivo).
        command:  Callable ejecutado al cambiar el estado.
                  Recibe el nuevo valor como booleano (True=ON, False=OFF).
        is_on:    Estado inicial del switch.
        disabled: Si True, el switch se muestra bloqueado en rojo (fallo/inactivo).

    Returns:
        CTkSwitch configurado y listo para empaquetar.
    """
    color_on   = COLORS.get('success', '#00ff88')
    color_off  = COLORS.get('bg_light', '#333333')
    color_fault = COLORS.get('danger', '#ff4444')

    if disabled:
        # Fallo o inactivo: switch bloqueado, color de aviso
        sw = ctk.CTkSwitch(
            parent,
            text=text,
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
            text_color=COLORS.get('text_dim', '#888888'),
            progress_color=color_fault,
            button_color=color_fault,
            button_hover_color=color_fault,
            fg_color=color_off,
            switch_width=90,
            switch_height=46,
            state="disabled",
        )
        # Fijar visualmente en OFF aunque haya fallo
        sw.deselect()
    else:
        def _on_toggle():
            """
            Callback ejecutado al cambiar el switch.
            Llama al command del usuario con el nuevo estado (bool).
            """
            # El switch ya cambió internamente; leemos su valor
            if command:
                command(bool(sw.get()))

        sw = ctk.CTkSwitch(
            parent,
            text=text,
            command=_on_toggle,
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
            text_color=COLORS['text'],
            progress_color=color_on,
            button_color=COLORS['secondary'],
            button_hover_color=COLORS['primary'],
            fg_color=color_off,
            switch_width=90,
            switch_height=46,
        )
        # Establecer estado inicial
        if is_on:
            sw.select()
        else:
            sw.deselect()

    return sw
