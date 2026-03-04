This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: ui/windows/theme_selector.py, ui/windows/display_window.py
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)
</notes>

</file_summary>

<directory_structure>
ui/
  windows/
    display_window.py
    theme_selector.py
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path="ui/windows/theme_selector.py">
"""
Ventana de selección de temas
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from config.themes import get_available_themes, get_theme, save_selected_theme, load_selected_theme
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox, confirm_dialog
import sys
import os

class ThemeSelector(ctk.CTkToplevel):
    """Ventana de selección de temas"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configurar ventana
        self.title("Selector de Temas")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        # Tema actualmente seleccionado
        self.current_theme = load_selected_theme()
        self.selected_theme_var = ctk.StringVar(value=self.current_theme)
        
        # Crear interfaz
        self._create_ui()
    
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
                    text="✓ TEMA ACTUAL",
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
            title="🔄 Aplicar Tema",
            on_confirm=do_restart,
            on_cancel=self.destroy
        )
</file>

<file path="ui/windows/display_window.py">
"""
Ventana de control de brillo de la pantalla.
Hardware: Freenove FNK0100K — Raspberry Pi 5.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger
from core.display_service import BRIGHTNESS_MIN, BRIGHTNESS_MAX

logger = get_logger(__name__)

QUICK_LEVELS = [
    ("🌑 10%",   10),
    ("🌒 30%",   30),
    ("🌓 60%",   60),
    ("🌕 100%", 100),
]


class DisplayWindow(ctk.CTkToplevel):
    """Ventana de control de brillo de pantalla."""

    def __init__(self, parent, display_service):
        super().__init__(parent)
        self.display_service = display_service

        self.title("Control de Pantalla")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._slider_var = ctk.IntVar(value=self.display_service.get_brightness())
        self._banner_shown = False
        self._inner = None

        self._create_ui()
        self._update()
        logger.info("[DisplayWindow] Ventana abierta (método: %s)",
                    self.display_service.get_method())

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main,
            title="CONTROL DE PANTALLA",
            on_close=self.destroy,
        )
        # Area de scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30,
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._inner = inner

        self._build_content(inner)

    def _build_content(self, inner):
        """Construye el contenido real de la ventana."""
        # ── Sin método disponible ──
        if not self.display_service.is_available():
            ctk.CTkLabel(
                inner,
                text=(
                    "⚠️ Brillo no disponible\n\n"
                    "No se encontró /sys/class/backlight/ ni wlr-randr.\n\n"
                    "Consulta GUIA_BRILLO_DSI.md → Paso 0\n"
                    "para diagnosticar tu sistema."
                ),
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                text_color=COLORS.get('warning', '#ffaa00'),
                justify="center",
            ).pack(expand=True)
            return

        # ── Info método activo ──
        method = self.display_service.get_method()
        ctk.CTkLabel(
            inner,
            text=f"Método activo: {method}",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(fill="x", padx=14, pady=(4, 0))

        # ── Tarjeta brillo actual + slider ──
        card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(6, 4))

        ctk.CTkLabel(
            card, text="Brillo",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(pady=(10, 0))

        self._brightness_label = ctk.CTkLabel(
            card, text="--",
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold"),
            text_color=COLORS['primary'],
        )
        self._brightness_label.pack()

        ctk.CTkSlider(
            card,
            from_=BRIGHTNESS_MIN, to=BRIGHTNESS_MAX,
            variable=self._slider_var,
            command=self._on_slider,
            width=680, height=36,
            button_length=40,
            progress_color=COLORS['primary'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['secondary'],
        ).pack(padx=20, pady=(4, 14))

        # ── Niveles rápidos ──
        quick = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        quick.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            quick, text="Niveles rápidos",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(pady=(8, 4))

        row = ctk.CTkFrame(quick, fg_color="transparent")
        row.pack(pady=(0, 10))
        for label, value in QUICK_LEVELS:
            make_futuristic_button(
                row, text=label,
                command=lambda v=value: self._set_quick(v),
                width=14, height=8, font_size=14,
            ).pack(side="left", padx=6)

        # ── ON / OFF ──
        toggle = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        toggle.pack(fill="x", padx=10, pady=4)

        tog_row = ctk.CTkFrame(toggle, fg_color="transparent")
        tog_row.pack(pady=10)

        make_futuristic_button(
            tog_row, text="🌕 Encender",
            command=self._screen_on,
            width=16, height=8, font_size=16,
        ).pack(side="left", padx=10)

        make_futuristic_button(
            tog_row, text="🌑 Apagar",
            command=self._screen_off,
            width=16, height=8, font_size=16,
        ).pack(side="left", padx=10)

        # ── Modo ahorro ──
        dim = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        dim.pack(fill="x", padx=10, pady=4)

        dim_row = ctk.CTkFrame(dim, fg_color="transparent")
        dim_row.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(
            dim_row,
            text="Dim automático  (2 min → 20%  |  4 min → apagado):",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(side="left", padx=(0, 10))

        self._dim_switch = ctk.CTkSwitch(
            dim_row, text="",
            command=self._toggle_dim,
            width=60, height=30,
            switch_width=60, switch_height=30,
            progress_color=COLORS['primary'],
        )
        self._dim_switch.pack(side="left")

        self._refresh()

    # ── Loop de actualización con banner ──────────────────────────────────────

    def _update(self):
        if not self.winfo_exists():
            return

        if not self.display_service._running:
            if not self._banner_shown:
                for w in self._inner.winfo_children():
                    w.destroy()
                StyleManager.show_service_stopped_banner(self._inner, "Display Service")
                self._banner_shown = True
        else:
            if self._banner_shown:
                self._banner_shown = False
                for w in self._inner.winfo_children():
                    w.destroy()
                self._build_content(self._inner)

        self.after(UPDATE_MS, self._update)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_slider(self, value):
        self.display_service.set_brightness(int(value))
        self._refresh()

    def _set_quick(self, value):
        self.display_service.set_brightness(value)
        self._slider_var.set(value)
        self._refresh()

    def _screen_on(self):
        self.display_service.screen_on()
        self._refresh()

    def _screen_off(self):
        self.display_service.screen_off()
        self._refresh()

    def _toggle_dim(self):
        if self._dim_switch.get():
            self.display_service.enable_dim_on_idle()
        else:
            self.display_service.disable_dim_on_idle()

    def _refresh(self):
        if not self.display_service.is_available():
            return
        if not hasattr(self, "_brightness_label"):
            return
        pct = self.display_service.get_brightness()
        self._brightness_label.configure(text=f"{pct}%")
        self._slider_var.set(pct)
</file>

</files>
