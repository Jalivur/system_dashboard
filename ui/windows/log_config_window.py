"""
Ventana de configuración del sistema de logging en runtime.
Permite cambiar niveles de fichero y consola, controlar módulos
individualmente y forzar la rotación del log.

Diseño ligero para Wayland/labwc:
  - Handlers globales: dos CTkOptionMenu (uno por handler)
  - Módulos: tk.Listbox nativo (un solo widget X11) + CTkScrollbar + un CTkOptionMenu compartido

Ubicación: ui/windows/log_config_window.py
"""
import logging
import tkinter as tk
import customtkinter as ctk

from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets.dialogs import custom_msgbox
from utils.logger import get_logger, get_dashboard_logger

logger = get_logger(__name__)

# ── Constantes ────────────────────────────────────────────────────────────────

_LEVELS    = ["DEBUG", "INFO", "WARNING", "ERROR"]
_LEVEL_MAP = {
    "DEBUG":   logging.DEBUG,
    "INFO":    logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR":   logging.ERROR,
}
_LEVEL_NAME = {v: k for k, v in _LEVEL_MAP.items()}
_HEREDAR    = "HEREDAR"

_LEVEL_COLORS = {
    "DEBUG":   "#888888",
    "INFO":    "#00BFFF",
    "WARNING": "#FFA500",
    "ERROR":   "#FF4444",
    _HEREDAR:  "#aaaaaa",
}


def _level_name(level: int) -> str:
    """
    Convierte un nivel numérico de logging en su nombre legible.

    Args:
        level (int): Nivel numérico de logging.

    Returns:
        str: Nombre del nivel o el nombre por defecto si no está mapeado.
    """
    return _LEVEL_NAME.get(level, logging.getLevelName(level))


# ── Ventana ───────────────────────────────────────────────────────────────────

class LogConfigWindow(ctk.CTkToplevel):
    """
    Ventana de control de niveles de logging en runtime.

    Args:
        parent: Ventana padre (CTkToplevel).

    Returns:
        None

    Raises:
        None
    """

    def __init__(self, parent):
        """
        Inicializa la ventana de configuración de logging.

        Configura posición y estado de handlers/módulos.

        Args:
            parent: Ventana padre (CTkToplevel).

        Raises:
            None
        """
        super().__init__(parent)
        self.title("Configuración de Logging")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.lift()
        self.after(150, self.focus_set)

        self._dl = get_dashboard_logger()

        status = self._dl.get_status()
        self._file_level_var    = ctk.StringVar(master=self, value=_level_name(status["file_level"]))
        self._console_level_var = ctk.StringVar(master=self, value=_level_name(status["console_level"]))
        self._console_exact_var = ctk.BooleanVar(master=self, value=status["console_exact"])
        self._console_active    = status["console_active"]

        self._module_level_var  = ctk.StringVar(master=self, value=_HEREDAR)
        self._modules: list     = []
        self._selected_mod: str = ""

        self._create_ui()
        logger.info("[LogConfigWindow] Ventana abierta")

    # ── UI principal ──────────────────────────────────────────────────────────

    def _create_ui(self):
        """
        Crea la estructura principal de la UI para la configuración de logging.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="CONFIGURACIÓN DE LOGGING", on_close=self._on_close)

        body = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        body.pack(fill="both", expand=True, padx=4, pady=4)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(body, fg_color=COLORS['bg_medium'])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        right = ctk.CTkFrame(body, fg_color=COLORS['bg_medium'])
        right.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        self._build_left(left)
        self._build_right(right)

    # ── Columna izquierda: handlers + acciones ────────────────────────────────

    def _build_left(self, parent):
        """
        Construye la columna izquierda de la ventana de configuración de logs.

        Args:
            parent: El padre de la columna izquierda.

        Returns:
            None

        Raises:
            None
        """
        hdr = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        hdr.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            hdr,
            text=f"{Icons.DOCUMENT}  Handlers",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(anchor="w", padx=10, pady=(8, 4))

        ctk.CTkFrame(hdr, fg_color=COLORS['border'], height=1,
                     corner_radius=0).pack(fill="x", padx=6, pady=(0, 6))

        self._build_handler_row(
            hdr,
            label="Fichero:",
            var=self._file_level_var,
            active=True,
            command=self._on_file_level_change,
        )
        self._build_handler_row(
            hdr,
            label="Consola:" if self._console_active else "Consola (sin TTY):",
            var=self._console_level_var,
            active=self._console_active,
            command=self._on_console_level_change,
        )

        ctk.CTkCheckBox(
            hdr,
            text="Consola: solo nivel exacto",
            variable=self._console_exact_var,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            fg_color=COLORS['primary'],
            hover_color=COLORS['secondary'],
            checkmark_color=COLORS['bg_dark'],
            command=self._on_console_level_change,
            state="normal" if self._console_active else "disabled",
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # Acciones
        act = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        act.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            act,
            text=f"{Icons.CONFIG}  Acciones",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(anchor="w", padx=10, pady=(8, 4))

        ctk.CTkFrame(act, fg_color=COLORS['border'], height=1,
                     corner_radius=0).pack(fill="x", padx=6, pady=(0, 8))

        make_futuristic_button(
            act,
            text=f"{Icons.REFRESH} Rotar log ahora",
            command=self._force_rollover,
            width=20, height=8, font_size=13,
        ).pack(fill="x", padx=10, pady=(0, 6))

        make_futuristic_button(
            act,
            text=f"{Icons.REFRESH} Reset módulos",
            command=self._reset_all_modules,
            width=20, height=8, font_size=13,
        ).pack(fill="x", padx=10, pady=(0, 10))

        status = self._dl.get_status()
        ctk.CTkLabel(
            parent,
            text=status['log_file'],
            font=(FONT_FAMILY, 11),
            text_color=COLORS['text_dim'],
            anchor="w",
            wraplength=340,
        ).pack(anchor="w", padx=4, pady=(0, 4))

    def _build_handler_row(self, parent, label: str, var, active: bool, command):
        """
        Crea una fila horizontal reusable para selector de nivel de handler.

        Args:
            parent: Frame contenedor.
            label (str): Etiqueta a mostrar (ej: "Fichero:").
            var: StringVar con nivel actual.
            active (bool): Indica si el handler está habilitado.
            command: Callback a ejecutar al cambiar el nivel.

        Returns:
            None

        Raises:
            None
        """
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 6))

        ctk.CTkLabel(
            row,
            text=label,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text'] if active else COLORS['text_dim'],
            width=100, anchor="w",
        ).pack(side="left")

        ctk.CTkOptionMenu(
            row,
            variable=var,
            values=_LEVELS,
            width=110,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            button_color=COLORS['primary'] if active else COLORS['border'],
            command=command,
            state="normal" if active else "disabled",
        ).pack(side="left")

    def _on_file_level_change(self, value: str):
        """
        Actualiza el nivel de logging del handler de fichero según el valor seleccionado.

        Args:
            value (str): Nuevo nivel de logging.

        Returns:
            None

        Raises:
            None
        """
        self._dl.set_file_level(_LEVEL_MAP[value])
        logger.info("[LogConfigWindow] Nivel fichero -> %s", value)

    def _on_console_level_change(self, value: str = None):
        """
        Establece el nivel de precisión del registro en la consola según el valor seleccionado.

        Args:
            value (str): El nuevo nivel de precisión. Si no se proporciona, se usa el valor actual.

        Returns:
            None

        Raises:
            None
        """
        if value is None:
            value = self._console_level_var.get()
        self._dl.set_console_level(_LEVEL_MAP[value], exact=self._console_exact_var.get())
        logger.info("[LogConfigWindow] Nivel consola -> %s", value)

    # ── Columna derecha: módulos con tk.Listbox + CTkScrollbar ───────────────

    def _build_right(self, parent):
        """
        Construye la columna derecha de la ventana de configuración de logs.

        Args:
            parent: El elemento padre donde se construirá la columna derecha.

        """
        hdr_row = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        hdr_row.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            hdr_row,
            text=f"{Icons.SEARCH}  Módulos",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(side="left", padx=10, pady=8)

        make_futuristic_button(
            hdr_row,
            text=f"{Icons.REFRESH}",
            command=self._reload_modules,
            width=6, height=6, font_size=14,
        ).pack(side="right", padx=8, pady=6)

        # Contenedor listbox + CTkScrollbar
        list_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        list_frame.pack(fill="both", expand=True, pady=(0, 6))

        # CTkScrollbar conectado al tk.Listbox
        sb = ctk.CTkScrollbar(list_frame, orientation="vertical", width=22)
        sb.pack(side="right", fill="y", padx=(0, 4), pady=6)
        StyleManager.style_scrollbar_ctk(sb)

        self._listbox = tk.Listbox(
            list_frame,
            bg=COLORS['bg_dark'],
            fg=COLORS['text'],
            selectbackground=COLORS['primary'],
            selectforeground=COLORS['bg_dark'],
            activestyle="none",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            yscrollcommand=sb.set,
        )
        self._listbox.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        self._listbox.bind("<<ListboxSelect>>", self._on_listbox_select)

        # Conectar scrollbar → listbox después de crear ambos
        sb.configure(command=self._listbox.yview)

        # Selector de nivel compartido
        sel_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        sel_frame.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            sel_frame,
            text="Nivel:",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            width=50, anchor="w",
        ).pack(side="left", padx=(10, 4), pady=8)

        self._mod_menu = ctk.CTkOptionMenu(
            sel_frame,
            variable=self._module_level_var,
            values=[_HEREDAR] + _LEVELS,
            width=110,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            button_color=COLORS['border'],
            state="disabled",
        )
        self._mod_menu.pack(side="left", padx=(0, 8), pady=8)

        make_futuristic_button(
            sel_frame,
            text="Aplicar",
            command=self._apply_module_level,
            width=10, height=6, font_size=13,
        ).pack(side="left", pady=8)

        self._mod_status = ctk.CTkLabel(
            sel_frame,
            text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        )
        self._mod_status.pack(side="left", padx=8, pady=8)

        self._reload_modules()

    def _reload_modules(self):
        """
        Recarga la lista de módulos activos desde dashboard_logger y actualiza la lista visualizada.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._listbox.delete(0, tk.END)
        explicit = self._dl.get_status()["modules"]
        self._modules = [
            (mod, explicit.get(mod, logging.NOTSET))
            for mod in self._dl.get_active_modules()
        ]
        for mod, level_int in self._modules:
            lvl = _level_name(level_int) if level_int != logging.NOTSET else _HEREDAR
            self._listbox.insert(tk.END, f"  {mod}  [{lvl}]")

        self._selected_mod = ""
        self._module_level_var.set(_HEREDAR)
        self._mod_menu.configure(state="disabled", button_color=COLORS['border'])
        self._mod_status.configure(text="")
        logger.debug("[LogConfigWindow] %d modulos cargados", len(self._modules))

    def _on_listbox_select(self, _event):
        """
        Actualiza el selector y el estado del módulo según la selección realizada en el listbox.

        Args:
            _event: Evento de selección en el listbox.

        Returns:
            None

        Raises:
            None
        """
        sel = self._listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(self._modules):
            return
        mod, level_int = self._modules[idx]
        self._selected_mod = mod
        current = _level_name(level_int) if level_int != logging.NOTSET else _HEREDAR
        self._module_level_var.set(current)
        self._mod_menu.configure(state="normal", button_color=COLORS['primary'])
        self._mod_status.configure(
            text=mod,
            text_color=_LEVEL_COLORS.get(current, COLORS['text_dim']),
        )

    def _apply_module_level(self):
        """
        Aplica el nivel de log seleccionado al módulo actualmente elegido y actualiza la lista y el estado.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if not self._selected_mod:
            return
        value = self._module_level_var.get()
        level = logging.NOTSET if value == _HEREDAR else _LEVEL_MAP[value]
        self._dl.set_module_level(self._selected_mod, level)

        for i, (mod, _) in enumerate(self._modules):
            if mod == self._selected_mod:
                self._modules[i] = (mod, level)
                self._listbox.delete(i)
                self._listbox.insert(i, f"  {mod}  [{value}]")
                self._listbox.selection_set(i)
                break

        self._mod_status.configure(
            text=f"{self._selected_mod} → {value}",
            text_color=_LEVEL_COLORS.get(value, COLORS['text_dim']),
        )
        logger.info("[LogConfigWindow] Modulo '%s' -> %s", self._selected_mod, value)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _force_rollover(self):
        """
        Fuerza la rotación manual del archivo de log y muestra una confirmación.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._dl.force_rollover()
        custom_msgbox(self, "Rotación completada.\nFichero anterior guardado como .log.1", "Rotación")
        logger.info("[LogConfigWindow] Rotacion manual ejecutada")

    def _reset_all_modules(self):
        """
        Restablece todos los módulos a nivel HEREDAR y recarga listbox.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        for mod in self._dl.get_active_modules():
            self._dl.set_module_level(mod, logging.NOTSET)
        self._reload_modules()
        logger.info("[LogConfigWindow] Todos los modulos restablecidos a HEREDAR")

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _on_close(self):
        """
        Maneja el evento de cierre de la ventana de configuración de registro.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.master.focus_force()
        self.destroy()

