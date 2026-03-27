"""
Ventana de control y monitorización de pines GPIO.

Modos de operación (toggle en barra superior):
  LIBRE       — dashboard libera todos los pines. Los scripts externos
                pueden usarlos sin conflictos.
  CONTROLANDO — dashboard reclama los pines con gpiozero.
                INPUT: lectura en tiempo real.
                OUTPUT: botón toggle HIGH/LOW.
                PWM: slider 0–100% duty cycle.

Panel de configuración:
  - Añadir/eliminar pines
  - Cambiar modo de pin en caliente
  - Editar etiqueta descriptiva
  - Feedback visual inmediato en cada acción
  - Al cerrar el diálogo reconstruye las filas de la ventana principal

Arquitectura:
  - Widgets creados una sola vez en _build_rows(); recreados solo si
    cambia la lista de pines o el modo de operación.
  - Actualizaciones de estado vía .configure() — nunca recrear en el loop.
  - Comandos OUTPUT/PWM lanzados en threads para no bloquear la UI.
  - Toda la lógica de hardware delegada a GPIOMonitor.
"""
import threading
import tkinter as tk
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES,
                              DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger
from core.gpio_monitor import (MODE_INPUT, MODE_OUTPUT, MODE_PWM, VALID_MODES,
                                OP_CONTROLANDO, OP_LIBRE)

logger = get_logger(__name__)

_REFRESH_MS = 800

# Colores de estado
_C_HIGH = "#39ff7a"
_C_LOW  = "#4a5568"
_C_ERR  = "#fc4f4f"
_C_NONE = "#888888"
_C_PWM  = "#63b3ed"
_C_OK   = "#39ff7a"   # feedback éxito

# Colores de modo de operación
_C_LIBRE       = "#f6ad55"
_C_CONTROLANDO = "#39ff7a"

_MODE_LABEL = {MODE_INPUT: "INPUT", MODE_OUTPUT: "OUTPUT", MODE_PWM: "PWM"}
_MODE_COLOR = {
    MODE_INPUT:  COLORS.get('text_dim', '#888'),
    MODE_OUTPUT: "#f6ad55",
    MODE_PWM:    _C_PWM,
}


class GPIOWindow(ctk.CTkToplevel):
    """Ventana de control y monitorización GPIO."""

    def __init__(self, parent, gpio_monitor):
        """Inicializa la ventana principal de monitorización y control de pines GPIO.

    Args:
        parent: Widget padre (CTkToplevel).
        gpio_monitor: Instancia del monitor GPIO para interactuar con el hardware.

    Configura la geometría para pantalla DSI, crea la interfaz de usuario completa,
    inicializa componentes internos y lanza el bucle de actualización automática.
        """
        super().__init__(parent)
        self._monitor = gpio_monitor

        self.title("GPIO Monitor")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._rows: dict[int, dict]        = {}
        self._inner: ctk.CTkFrame | None   = None
        self._lbl_status: ctk.CTkLabel | None = None
        self._btn_op: ctk.CTkButton | None    = None
        self._lbl_op: ctk.CTkLabel | None     = None
        self._op_job = None
        self._last_op_mode: str = self._monitor.get_op_mode()

        self._create_ui()
        self._update()
        logger.info("[GPIOWindow] Ventana abierta")

    # ── UI principal ──────────────────────────────────────────────────────────

    def _create_ui(self):
        """Crea todos los widgets y estructura de la interfaz de usuario.

    Construye header, barra de modo de operación, área scrollable con canvas,
    filas de pines dinámicas, footer con estado y botón de configuración.
        """
        self._main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        self._main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(self._main, title="GPIO MONITOR / CONTROL",
                           on_close=self.destroy)

        # ── Barra de modo de operación ────────────────────────────────────────
        op_bar = ctk.CTkFrame(self._main, fg_color=COLORS['bg_dark'],
                              corner_radius=8)
        op_bar.pack(fill="x", padx=8, pady=(4, 2))

        self._lbl_op = ctk.CTkLabel(
            op_bar,
            text=self._op_text(),
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=self._op_color(),
            anchor="w",
        )
        self._lbl_op.pack(side="left", padx=12, pady=8)

        self._btn_op = make_futuristic_button(
            op_bar,
            text=self._op_btn_text(),
            command=self._toggle_op_mode,
            width=24, height=6, font_size=13,
        )
        self._btn_op.pack(side="right", padx=10, pady=6)

        # ── Área scrollable ───────────────────────────────────────────────────
        sc = ctk.CTkFrame(self._main, fg_color=COLORS['bg_medium'])
        sc.pack(fill="both", expand=True, padx=5, pady=4)

        self._canvas = ctk.CTkCanvas(sc, bg=COLORS['bg_medium'],
                                     highlightthickness=0)
        self._canvas.pack(side="left", fill="both", expand=True)

        sb = ctk.CTkScrollbar(sc, orientation="vertical",
                              command=self._canvas.yview, width=30)
        sb.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(sb)
        self._canvas.configure(yscrollcommand=sb.set)

        self._inner = ctk.CTkFrame(self._canvas, fg_color=COLORS['bg_medium'])
        self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw", width=DSI_WIDTH - 50)
        self._inner.bind("<Configure>",
                         lambda e: self._canvas.configure(
                             scrollregion=self._canvas.bbox("all")))

        self._build_rows()

        # ── Footer ────────────────────────────────────────────────────────────
        footer = ctk.CTkFrame(self._main, fg_color=COLORS['bg_medium'])
        footer.pack(fill="x", padx=8, pady=(2, 6))

        self._lbl_status = ctk.CTkLabel(
            footer, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'], anchor="w",
        )
        self._lbl_status.pack(side="left", padx=4)

        self._pin_btn = make_futuristic_button(
            footer, text=f"{Icons.PROCESOS}  Configurar pines",
            command=self._open_config,
            width=22, height=7, font_size=14,
        )
        self._pin_btn.pack(side="right", padx=4)

    # ── Toggle modo de operación ──────────────────────────────────────────────

    def _toggle_op_mode(self):
        """Alterna el modo de operación entre LIBRE y CONTROLANDO.

    Lanza el cambio en thread daemon para no bloquear la UI y programa
    actualización de la barra en 200ms.
        """
        current = self._monitor.get_op_mode()
        new = OP_CONTROLANDO if current == OP_LIBRE else OP_LIBRE
        threading.Thread(
            target=self._monitor.set_op_mode,
            args=(new,),
            daemon=True, name="GPIO-opmode",
        ).start()
        self._op_job = self.after(200, self._on_op_mode_changed)

    def _on_op_mode_changed(self):
        """Callback ejecutado tras cambio de modo de operación.

    Actualiza la barra de operación y reconstruye las filas si la ventana existe.
        """
        if not self.winfo_exists():
            return
        self._update_op_bar()
        self._build_rows()

    def _update_op_bar(self):
        """Actualiza visualmente la barra de modo de operación.

    Reconfigura labels y botón según el estado actual del monitor.
        """
        if self._lbl_op and self._lbl_op.winfo_exists():
            self._lbl_op.configure(
                text=self._op_text(),
                text_color=self._op_color())
        if self._btn_op and self._btn_op.winfo_exists():
            self._btn_op.configure(text=self._op_btn_text())

    def _op_text(self) -> str:
        """Genera el texto descriptivo del modo de operación actual.

    Returns:
        str: Texto con icono y descripción del estado (LIBRE o CONTROLANDO).
        """
        if self._monitor.get_op_mode() == OP_LIBRE:
            return f"{Icons.WARNING}  GPIO LIBRE — pines disponibles para otros procesos"
        return f"{Icons.TAP}  CONTROLANDO — dashboard tiene los pines"

    def _op_color(self) -> str:
        """Determina el color del texto según el modo de operación.

    Returns:
        str: Color hexadecimal (_C_LIBRE o _C_CONTROLANDO).
        """
        return (_C_LIBRE if self._monitor.get_op_mode() == OP_LIBRE
                else _C_CONTROLANDO)

    def _op_btn_text(self) -> str:
        """Genera el texto para el botón de toggle de modo de operación.

    Returns:
        str: Texto con icono apropiado ('Tomar control' o 'Liberar GPIO').
        """
        return (f"{Icons.TAP}  Tomar control"
                if self._monitor.get_op_mode() == OP_LIBRE
                else f"{Icons.WARNING}  Liberar GPIO")

    # ── Construcción de filas ─────────────────────────────────────────────────

    def _build_rows(self):
        """Construye o reconstruye todas las filas de pines en el canvas interno.

    Limpia widgets existentes, crea filas nuevas basadas en el estado actual del monitor.
    Maneja casos especiales como ausencia de pines o modo LIBRE con mensajes informativos.
        """
        if not self.winfo_exists():
            return
        for w in self._inner.winfo_children():
            w.destroy()
        self._rows.clear()

        state    = self._monitor.get_state()
        is_libre = self._monitor.get_op_mode() == OP_LIBRE

        if not state:
            ctk.CTkLabel(
                self._inner,
                text="No hay pines configurados.\nUsa 'Configurar pines' para añadir.",
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
                justify="center",
            ).pack(pady=30)
            return

        if is_libre:
            ctk.CTkLabel(
                self._inner,
                text=f"{Icons.WARNING}  GPIO liberado.\nLos pines están disponibles para scripts externos.",
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=_C_LIBRE,
                justify="center",
            ).pack(pady=16)

        for pin in sorted(state.keys()):
            self._create_pin_row(pin, state[pin], is_libre)

    def _create_pin_row(self, pin: int, data: dict, is_libre: bool):
        """Crea una fila completa para un pin específico en el canvas.

    Args:
        pin (int): Número del pin GPIO.
        data (dict): Estado actual del pin del monitor.
        is_libre (bool): Si el modo de operación es LIBRE.

    Crea indicador visual, etiqueta, badge de modo y controles contextuales (toggle, slider).
    """
        mode = data["mode"]
        row  = ctk.CTkFrame(self._inner, fg_color=COLORS['bg_dark'],
                            corner_radius=8)
        row.pack(fill="x", padx=10, pady=4)
        row.grid_columnconfigure(3, weight=1)

        # ── Indicador ─────────────────────────────────────────────────────────
        DOT   = 14
        dot_c = tk.Canvas(row, width=DOT, height=DOT,
                          bg=COLORS['bg_dark'], highlightthickness=0, bd=0)
        dot_c.grid(row=0, column=0, padx=(10, 6), pady=14)
        oval = dot_c.create_oval(1, 1, DOT - 1, DOT - 1,
                                 fill=_C_NONE, outline="")

        # ── Nombre + etiqueta ─────────────────────────────────────────────────
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=1, padx=(0, 8), pady=8, sticky="w")

        ctk.CTkLabel(
            info, text=f"GPIO {pin:2d}",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['text'] if not is_libre else COLORS['text_dim'],
            anchor="w",
        ).pack(anchor="w")

        lbl_label = ctk.CTkLabel(
            info, text=data.get("label", f"GPIO {pin}"),
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'], anchor="w",
        )
        lbl_label.pack(anchor="w")

        # ── Badge modo ────────────────────────────────────────────────────────
        lbl_mode = ctk.CTkLabel(
            row, text=_MODE_LABEL.get(mode, mode),
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=(_MODE_COLOR.get(mode, COLORS['text_dim'])
                        if not is_libre else COLORS['text_dim']),
            width=60, anchor="center",
        )
        lbl_mode.grid(row=0, column=2, padx=4, pady=8)

        # ── Control contextual ────────────────────────────────────────────────
        ctrl = ctk.CTkFrame(row, fg_color="transparent")
        ctrl.grid(row=0, column=3, padx=(4, 10), pady=8, sticky="ew")

        row_w = {
            "dot": dot_c, "oval": oval,
            "lbl_mode": lbl_mode, "lbl_label": lbl_label, "mode": mode,
            "lbl_state": None, "btn_toggle": None,
            "slider": None, "lbl_duty": None,
        }

        if is_libre:
            ctk.CTkLabel(
                ctrl, text="—",
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                text_color=COLORS['text_dim'], width=80, anchor="center",
            ).pack(side="left", padx=4)

        elif mode == MODE_INPUT:
            lbl_state = ctk.CTkLabel(
                ctrl, text="—",
                font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
                text_color=_C_NONE, width=80, anchor="center",
            )
            lbl_state.pack(side="left", padx=4)
            row_w["lbl_state"] = lbl_state

        elif mode == MODE_OUTPUT:
            lbl_state = ctk.CTkLabel(
                ctrl, text="LOW",
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                text_color=_C_LOW, width=50, anchor="center",
            )
            lbl_state.pack(side="left", padx=(0, 6))
            row_w["lbl_state"] = lbl_state

            btn_toggle = make_futuristic_button(
                ctrl, text="→ HIGH",
                command=lambda p=pin: self._toggle_output(p),
                width=12, height=6, font_size=13,
            )
            btn_toggle.pack(side="left")
            row_w["btn_toggle"] = btn_toggle

        elif mode == MODE_PWM:
            lbl_duty = ctk.CTkLabel(
                ctrl, text="0%",
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                text_color=_C_PWM, width=42, anchor="e",
            )
            lbl_duty.pack(side="left", padx=(0, 4))
            row_w["lbl_duty"] = lbl_duty

            slider = ctk.CTkSlider(
                ctrl, from_=0, to=100, number_of_steps=100, width=200,
                progress_color=_C_PWM, button_color=_C_PWM,
                button_hover_color="#90cdf4",
                command=lambda val, p=pin: self._on_pwm_slide(p, val),
            )
            slider.set(0)
            slider.pack(side="left", padx=4)
            row_w["slider"]  = slider

        self._rows[pin] = row_w

    # ── Loop de refresco ──────────────────────────────────────────────────────

    def _update(self):
        """Bucle principal de actualización de estado en tiempo real.

    Se ejecuta cada _REFRESH_MS. Verifica servicio, reconstruye si cambios estructurales,
    actualiza indicadores, estados y controles sin recrear widgets.
        """
        if not self.winfo_exists():
            return
        if not self._monitor.is_running():
            StyleManager.show_service_stopped_banner(self._inner, "GPIO Monitor")
            self._btn_op.configure(state = "disabled")
            self._pin_btn.configure(state = "disabled")
            return

        state    = self._monitor.get_state()
        is_libre = self._monitor.get_op_mode() == OP_LIBRE

        current_op = self._monitor.get_op_mode()
        if (set(state.keys()) != set(self._rows.keys())
                or current_op != self._last_op_mode):
            self._last_op_mode = current_op
            self._update_op_bar()
            self._build_rows()
            if self._lbl_status and self._lbl_status.winfo_exists():
                self._lbl_status.configure(text=self._status_text(state))
            self.after(_REFRESH_MS, self._update)
            return

        if not is_libre:
            for pin, data in state.items():
                if pin not in self._rows:
                    continue
                rw    = self._rows[pin]
                error = data.get("error")
                mode  = data.get("mode", MODE_INPUT)
                value = data.get("value")
                duty  = data.get("duty", 0.0)

                # Indicador
                if error:
                    dot_color = _C_ERR
                elif mode == MODE_INPUT:
                    dot_color = (_C_HIGH if value is True else
                                 _C_LOW  if value is False else _C_NONE)
                elif mode == MODE_OUTPUT:
                    dot_color = _C_HIGH if value else _C_LOW
                elif mode == MODE_PWM:
                    dot_color = _C_PWM if duty > 0 else _C_LOW
                else:
                    dot_color = _C_NONE
                rw["dot"].itemconfigure(rw["oval"], fill=dot_color)

                rw["lbl_label"].configure(text=data.get("label", f"GPIO {pin}"))

                if mode == MODE_INPUT and rw["lbl_state"]:
                    if error:
                        rw["lbl_state"].configure(text="ERR", text_color=_C_ERR)
                    elif value is None:
                        rw["lbl_state"].configure(text="—", text_color=_C_NONE)
                    elif value:
                        rw["lbl_state"].configure(text="HIGH", text_color=_C_HIGH)
                    else:
                        rw["lbl_state"].configure(text="LOW", text_color=_C_LOW)

                if mode == MODE_OUTPUT and rw["lbl_state"] and rw["btn_toggle"]:
                    if error:
                        rw["lbl_state"].configure(text="ERR", text_color=_C_ERR)
                    else:
                        is_high = bool(value)
                        rw["lbl_state"].configure(
                            text="HIGH" if is_high else "LOW",
                            text_color=_C_HIGH if is_high else _C_LOW)
                        rw["btn_toggle"].configure(
                            text="→ LOW" if is_high else "→ HIGH")

                if mode == MODE_PWM and rw["lbl_duty"]:
                    if error:
                        rw["lbl_duty"].configure(text="ERR", text_color=_C_ERR)
                    else:
                        rw["lbl_duty"].configure(
                            text=f"{int(duty * 100)}%", text_color=_C_PWM)

        if self._lbl_status and self._lbl_status.winfo_exists():
            self._lbl_status.configure(text=self._status_text(state))

        self.after(_REFRESH_MS, self._update)

    # ── Acciones OUTPUT ───────────────────────────────────────────────────────

    def _toggle_output(self, pin: int):
        """Alterna el estado HIGH/LOW de un pin en modo OUTPUT.

    Args:
        pin (int): Número del pin.

    Lanza el comando en thread daemon, actualiza UI reactivamente.
        """
        state   = self._monitor.get_state()
        current = state.get(pin, {}).get("value", False)
        threading.Thread(
            target=self._monitor.set_output,
            args=(pin, not current),
            daemon=True, name=f"GPIO-out-{pin}",
        ).start()

    # ── Acciones PWM ──────────────────────────────────────────────────────────

    def _on_pwm_slide(self, pin: int, val: float):
        """Manejador de slider PWM: aplica duty cycle.

    Args:
        pin (int): Número del pin PWM.
        val (float): Valor del slider (0-100).

    Actualiza label duty inmediato y lanza comando en thread.
        """
        duty = val / 100.0
        if pin in self._rows and self._rows[pin]["lbl_duty"]:
            self._rows[pin]["lbl_duty"].configure(text=f"{int(val)}%")
        threading.Thread(
            target=self._monitor.set_pwm,
            args=(pin, duty),
            daemon=True, name=f"GPIO-pwm-{pin}",
        ).start()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _status_text(self, state: dict) -> str:
        """Genera texto resumido del estado para el footer.

    Args:
        state (dict): Diccionario de estado de todos los pines.

    Returns:
        str: Resumen como 'CTRL · 4 pines · 2 IN · 1 OUT · 1 PWM'.
        """
        total   = len(state)
        inputs  = sum(1 for d in state.values() if d["mode"] == MODE_INPUT)
        outputs = sum(1 for d in state.values() if d["mode"] == MODE_OUTPUT)
        pwms    = sum(1 for d in state.values() if d["mode"] == MODE_PWM)
        errors  = sum(1 for d in state.values() if d.get("error"))
        op      = "LIBRE" if self._monitor.get_op_mode() == OP_LIBRE else "CTRL"
        parts   = [op, f"{total} pines", f"{inputs} IN",
                   f"{outputs} OUT", f"{pwms} PWM"]
        if errors:
            parts.append(f"{errors} err")
        return "  ·  ".join(parts)

    # ── Config ────────────────────────────────────────────────────────────────

    def _open_config(self):
        """Abre el diálogo de configuración de pines.
        """
        _GPIOConfigDialog(self, self._monitor,
                          on_close=self._on_config_closed)

    def _on_config_closed(self):
        """Callback ejecutado al cerrar el diálogo de configuración.

    Reconstruye las filas de pines para reflejar cambios.
        """
        if self.winfo_exists():
            self._build_rows()

    def destroy(self):
        """Destruye la ventana limpiamente, logueando el cierre.
        """
        logger.info("[GPIOWindow] Ventana cerrada")
        super().destroy()


# ── Diálogo de configuración de pines ────────────────────────────────────────

class _GPIOConfigDialog(ctk.CTkToplevel):
    """Panel para añadir, eliminar y reconfigurar pines GPIO."""

    _ALL_PINS = [p for p in range(1, 28)
                 if p not in {2, 3, 12, 13, 14, 15, 18, 19}]

    def __init__(self, parent, gpio_monitor, on_close=None):
        """Inicializa el diálogo de configuración de pines.

    Args:
        parent: Ventana padre.
        gpio_monitor: Instancia del monitor.
        on_close (callable, optional): Callback al cerrar.
        """
        super().__init__(parent)
        self._monitor  = gpio_monitor
        self._on_close = on_close   # callback hacia GPIOWindow

        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(100, self.focus_set)

        self._row_widgets: dict[int, dict] = {}
        self._create_ui()

    def _create_ui(self):
        """Crea la interfaz del diálogo de configuración.
        """
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="CONFIGURAR PINES GPIO",
                           on_close=self.destroy)

        # ── Añadir pin ────────────────────────────────────────────────────────
        add_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=8)
        add_bar.pack(fill="x", padx=8, pady=(4, 2))

        ctk.CTkLabel(add_bar, text="Añadir pin:",
                     font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                     text_color=COLORS['text'],
                     ).pack(side="left", padx=10, pady=8)

        self._new_pin_var = ctk.StringVar(master=self, value="4")
        ctk.CTkOptionMenu(
            add_bar,
            values=[str(p) for p in self._ALL_PINS],
            variable=self._new_pin_var,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'], width=80,
        ).pack(side="left", padx=6, pady=8)

        self._new_mode_var = ctk.StringVar(master=self, value=MODE_INPUT)
        ctk.CTkOptionMenu(
            add_bar,
            values=list(VALID_MODES),
            variable=self._new_mode_var,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'], width=100,
        ).pack(side="left", padx=6, pady=8)

        self._new_label_entry = ctk.CTkEntry(
            add_bar,
            placeholder_text="Etiqueta (opcional)",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            text_color=COLORS['text'], width=180,
        )
        self._new_label_entry.pack(side="left", padx=6, pady=8)

        make_futuristic_button(
            add_bar, text=f"{Icons.PLUS}  Añadir",
            command=self._add_pin,
            width=10, height=6, font_size=13,
        ).pack(side="left", padx=6, pady=8)

        # ── Lista de pines ────────────────────────────────────────────────────
        sc = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        sc.pack(fill="both", expand=True, padx=5, pady=4)

        canvas = ctk.CTkCanvas(sc, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        sb = ctk.CTkScrollbar(sc, orientation="vertical",
                              command=canvas.yview, width=30)
        sb.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(sb)
        canvas.configure(yscrollcommand=sb.set)

        self._list_inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self._list_inner,
                             anchor="nw", width=DSI_WIDTH - 50)
        self._list_inner.bind("<Configure>",
                              lambda e: canvas.configure(
                                  scrollregion=canvas.bbox("all")))

        self._build_list()

        # ── Footer ────────────────────────────────────────────────────────────
        footer = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        footer.pack(fill="x", padx=8, pady=(2, 6))

        ctk.CTkLabel(
            footer,
            text=f"{Icons.WARNING}  Pines reservados (2,3,12,13,14,15,18,19) no disponibles.",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(side="left", padx=4)

        make_futuristic_button(
            footer, text=f"{Icons.CHECK}  Cerrar",
            command=self.destroy,
            width=10, height=6, font_size=13,
        ).pack(side="right", padx=4)

    def _build_list(self):
        """Reconstruye la lista de pines configurados en el diálogo.
        """
        for w in self._list_inner.winfo_children():
            w.destroy()
        self._row_widgets.clear()

        state = self._monitor.get_state()
        if not state:
            ctk.CTkLabel(
                self._list_inner,
                text="Sin pines configurados.",
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
            ).pack(pady=20)
            return

        for pin in sorted(state.keys()):
            self._create_list_row(pin, state[pin])

    def _create_list_row(self, pin: int, data: dict):
        """Crea fila editable para un pin en la lista de configuración.

    Args:
        pin (int): Pin.
        data (dict): Datos del pin.
        """
        row = ctk.CTkFrame(self._list_inner, fg_color=COLORS['bg_dark'],
                           corner_radius=8)
        row.pack(fill="x", padx=8, pady=3)

        ctk.CTkLabel(row, text=f"GPIO {pin:2d}",
                     font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
                     text_color=COLORS['text'], width=80, anchor="w",
                     ).pack(side="left", padx=10, pady=8)

        # ── Modo ──────────────────────────────────────────────────────────────
        mode_var = ctk.StringVar(master=self, value=data["mode"])

        # Label de feedback para cambio de modo
        lbl_mode_fb = ctk.CTkLabel(
            row, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=_C_OK, width=60, anchor="w",
        )

        ctk.CTkOptionMenu(
            row,
            values=list(VALID_MODES),
            variable=mode_var,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'], width=100,
            command=lambda m, p=pin, fb=lbl_mode_fb: self._change_mode(p, m, fb),
        ).pack(side="left", padx=6, pady=8)

        lbl_mode_fb.pack(side="left", padx=(0, 4))

        # ── Etiqueta ──────────────────────────────────────────────────────────
        lbl_entry = ctk.CTkEntry(
            row,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            text_color=COLORS['text'], width=180,
        )
        lbl_entry.insert(0, data.get("label", f"GPIO {pin}"))
        lbl_entry.pack(side="left", padx=6, pady=8)

        # Label de feedback para guardar etiqueta
        lbl_save_fb = ctk.CTkLabel(
            row, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=_C_OK, width=40, anchor="w",
        )
        lbl_save_fb.pack(side="left", padx=(0, 2))

        make_futuristic_button(
            row, text=f"{Icons.SAVE}",
            command=lambda p=pin, e=lbl_entry, fb=lbl_save_fb: self._save_label(p, e, fb),
            width=6, height=6, font_size=13,
        ).pack(side="left", padx=2, pady=8)

        make_futuristic_button(
            row, text=f"{Icons.TRASH}",
            command=lambda p=pin: self._remove_pin(p),
            width=6, height=6, font_size=13,
        ).pack(side="right", padx=(2, 10), pady=8)

        self._row_widgets[pin] = {"mode_var": mode_var, "lbl_entry": lbl_entry}

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _add_pin(self):
        """Añade un nuevo pin con modo y etiqueta especificados.
        """
        try:
            pin = int(self._new_pin_var.get())
        except ValueError:
            return
        mode  = self._new_mode_var.get()
        label = self._new_label_entry.get().strip()
        if self._monitor.add_pin(pin, mode, label):
            self._new_label_entry.delete(0, "end")
            self._build_list()

    def _remove_pin(self, pin: int):
        """Elimina un pin de la configuración.

    Args:
        pin (int): Pin a eliminar.
        """
        self._monitor.remove_pin(pin)
        self._build_list()

    def _change_mode(self, pin: int, mode: str, feedback_label: ctk.CTkLabel):
        """Cambia el modo de un pin y muestra feedback visual.

    Args:
        pin (int): Pin.
        mode (str): Nuevo modo.
        feedback_label: Label para mostrar OK/ERR.
        """
        ok = self._monitor.set_mode(pin, mode)
        if ok:
            feedback_label.configure(text=f"{Icons.CHECK}", text_color=_C_OK)
            self.after(1500, lambda: (feedback_label.winfo_exists() and
                                      feedback_label.configure(text="")))
        else:
            feedback_label.configure(text="ERR", text_color=_C_ERR)
            self.after(1500, lambda: (feedback_label.winfo_exists() and
                                      feedback_label.configure(text="")))

    def _save_label(self, pin: int, entry: ctk.CTkEntry,
                    feedback_label: ctk.CTkLabel):
        """Guarda nueva etiqueta para un pin con feedback.

    Args:
        pin (int): Pin.
        entry: Entry con nueva etiqueta.
        feedback_label: Label para feedback.
        """
        label = entry.get().strip()
        if not label:
            return
        ok = self._monitor.set_label(pin, label)
        if ok:
            feedback_label.configure(text=f"{Icons.CHECK}", text_color=_C_OK)
            self.after(1500, lambda: (feedback_label.winfo_exists() and
                                      feedback_label.configure(text="")))
        else:
            feedback_label.configure(text="ERR", text_color=_C_ERR)
            self.after(1500, lambda: (feedback_label.winfo_exists() and
                                      feedback_label.configure(text="")))

    def destroy(self) -> None:
        """Cierra el diálogo y ejecuta callback si existe.
        """
        logger.info('[GPIOConfigDialog] Diálogo cerrado')
        super().destroy()
        if callable(self._on_close):
            self._on_close()
