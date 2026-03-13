"""
Ventana de control de ventiladores
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons)
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox
from core.fan_controller import FanController
from core.system_monitor import SystemMonitor
from utils.file_manager import FileManager


class FanControlWindow(ctk.CTkToplevel):
    """Ventana de control de ventiladores y curvas PWM"""

    def __init__(self, parent, fan_controller: FanController,
                 system_monitor: SystemMonitor, fan_service=None):
        super().__init__(parent)

        # Referencias
        self._fan_controller = fan_controller
        self._system_monitor = system_monitor
        self._fan_service    = fan_service  # puede ser None si no está disponible
        self._file_manager   = FileManager()

        # Variables de estado
        self._mode_var       = tk.StringVar(master=self)
        self._manual_pwm_var = tk.IntVar(master=self, value=128)
        self._curve_vars     = []

        # Variables para entries de nuevo punto (con placeholder)
        self._PLACEHOLDER_TEMP = "0-100"
        self._PLACEHOLDER_PWM  = "0-255"
        self._new_temp_var = tk.StringVar(master=self, value=self._PLACEHOLDER_TEMP)
        self._new_pwm_var  = tk.StringVar(master=self, value=self._PLACEHOLDER_PWM)

        # Cargar estado inicial
        self._load_initial_state()

        # Configurar ventana
        self.title("Control de Ventiladores")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.after(150, self.focus_set)
        self.lift()

        # Crear interfaz
        self._create_ui()

        # Iniciar bucles
        self._update_pwm_display()
        self._update_service_status()

    def _load_initial_state(self):
        """Carga el estado inicial desde archivo"""
        state = self._file_manager.load_state()
        self._mode_var.set(state.get("mode", "auto"))
        target = state.get("target_pwm")
        if target is not None:
            self._manual_pwm_var.set(target)

    def _create_ui(self):
        """Crea la interfaz de usuario"""
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main,
            title="CONTROL DE VENTILADORES",
            on_close=self.destroy,
        )

        # Área de scroll
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
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Aviso de servicio automático parado — se muestra/oculta dinámicamente
        self._service_warning = ctk.CTkLabel(
            inner,
            text="" + Icons.WARNING + "️  Servicio automático parado — modo Auto no actúa  |  Control manual disponible",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS.get('warning', '#ffaa00'),
            fg_color=COLORS['bg_dark'],
            corner_radius=6,
        )
        self._service_warning.pack(fill="x", padx=10, pady=(4, 0))
        self._service_warning.pack_forget()  # oculto por defecto

        # Secciones
        self._create_mode_section(inner)
        self._create_manual_pwm_section(inner)
        self._create_curve_section(inner)
        self._create_bottom_buttons(main)

    # ── Aviso dinámico de servicio ────────────────────────────────────────────

    def _update_service_status(self):
        """Muestra u oculta el aviso según si _fan_service está corriendo."""
        if not self.winfo_exists():
            return
        if self._fan_service is not None and not self._fan_service.is_running():
            self._service_warning.pack(fill="x", padx=10, pady=(4, 0))
        else:
            self._service_warning.pack_forget()
        self.after(UPDATE_MS, self._update_service_status)

    # ── Secciones de la UI ────────────────────────────────────────────────────

    def _create_mode_section(self, parent):
        """Crea la sección de selección de modo"""
        mode_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        mode_frame.pack(fill="x", pady=5, padx=10)

        ctk.CTkLabel(
            mode_frame,
            text="MODO DE OPERACIÓN",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(anchor="w", pady=(0, 5))

        modes_container = ctk.CTkFrame(mode_frame, fg_color=COLORS['bg_medium'])
        modes_container.pack(fill="x", pady=5)

        modes = [
            ("Auto",        "auto"),
            ("Silent",      "silent"),
            ("Normal",      "normal"),
            ("Performance", "performance"),
            ("Manual",      "manual")
        ]

        for text, value in modes:
            rb = ctk.CTkRadioButton(
                modes_container,
                text=text,
                variable=self._mode_var,
                value=value,
                command=lambda v=value: self._on_mode_change(v),
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=8)
            StyleManager.style_radiobutton_ctk(rb)

    def _create_manual_pwm_section(self, parent):
        """Crea la sección de PWM manual"""
        manual_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        manual_frame.pack(fill="x", pady=5, padx=10)

        ctk.CTkLabel(
            manual_frame,
            text="PWM MANUAL (0-255)",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(anchor="w", pady=(0, 5))

        self._pwm_value_label = ctk.CTkLabel(
            manual_frame,
            text=f"Valor: {self._manual_pwm_var.get()} ({int(self._manual_pwm_var.get()/255*100)}%)",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        self._pwm_value_label.pack(anchor="w", pady=(0, 10))

        slider = ctk.CTkSlider(
            manual_frame,
            from_=0,
            to=255,
            variable=self._manual_pwm_var,
            command=self._on_pwm_change,
            width=DSI_WIDTH - 100
        )
        slider.pack(fill="x", pady=5)
        StyleManager.style_slider_ctk(slider)

    def _create_curve_section(self, parent):
        """Crea la sección de curva temperatura-PWM"""
        curve_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        curve_frame.pack(fill="x", pady=5, padx=10)

        ctk.CTkLabel(
            curve_frame,
            text="CURVA TEMPERATURA-PWM",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(anchor="w", pady=(0, 5))

        self._points_frame = ctk.CTkFrame(curve_frame, fg_color=COLORS['bg_dark'])
        self._points_frame.pack(fill="x", pady=5, padx=5)
        self._refresh_curve_points()

        add_section = ctk.CTkFrame(curve_frame, fg_color=COLORS['bg_dark'])
        add_section.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(
            add_section,
            text="AÑADIR NUEVO PUNTO",
            text_color=COLORS['success'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).pack(anchor="w", padx=5, pady=5)

        entries_row = ctk.CTkFrame(add_section, fg_color=COLORS['bg_dark'])
        entries_row.pack(fill="x", padx=5, pady=5)

        # — Temperatura —
        temp_col = ctk.CTkFrame(entries_row, fg_color=COLORS['bg_dark'])
        temp_col.pack(side="top", padx=(0, 20))

        ctk.CTkLabel(
            temp_col,
            text="Temperatura (°C)",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(anchor="n")

        self._entry_temp = ctk.CTkEntry(
            temp_col,
            textvariable=self._new_temp_var,
            width=120, height=36,
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text_dim'],
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['primary']
        )
        self._entry_temp.pack(pady=4)
        self._entry_temp.bind("<FocusIn>",  lambda e: self._entry_focus_in(self._entry_temp, self._new_temp_var, self._PLACEHOLDER_TEMP))
        self._entry_temp.bind("<FocusOut>", lambda e: self._entry_focus_out(self._entry_temp, self._new_temp_var, self._PLACEHOLDER_TEMP))

        # — PWM —
        pwm_col = ctk.CTkFrame(entries_row, fg_color=COLORS['bg_dark'])
        pwm_col.pack(side="top", padx=(0, 20))

        ctk.CTkLabel(
            pwm_col,
            text="PWM (0-255)",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(anchor="n")

        self._entry_pwm = ctk.CTkEntry(
            pwm_col,
            textvariable=self._new_pwm_var,
            width=120, height=36,
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text_dim'],
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['primary']
        )
        self._entry_pwm.pack(pady=4)
        self._entry_pwm.bind("<FocusIn>",  lambda e: self._entry_focus_in(self._entry_pwm, self._new_pwm_var, self._PLACEHOLDER_PWM))
        self._entry_pwm.bind("<FocusOut>", lambda e: self._entry_focus_out(self._entry_pwm, self._new_pwm_var, self._PLACEHOLDER_PWM))

        make_futuristic_button(
            add_section,
            text="" + Icons.CHECK_MARK + " Añadir Punto a la Curva",
            command=self._add_curve_point_from_entries,
            width=25, height=6, font_size=16
        ).pack(pady=10)

    # ── Helpers de placeholder ────────────────────────────────────────────────

    def _entry_focus_in(self, entry, var, placeholder):
        if var.get() == placeholder:
            var.set("")
            entry.configure(text_color=COLORS['text'])

    def _entry_focus_out(self, entry, var, placeholder):
        if var.get().strip() == "":
            var.set(placeholder)
            entry.configure(text_color=COLORS['text_dim'])

    # ── Lógica de añadir punto ────────────────────────────────────────────────

    def _add_curve_point_from_entries(self):
        temp_raw = self._new_temp_var.get().strip()
        pwm_raw  = self._new_pwm_var.get().strip()

        if temp_raw in ("", self._PLACEHOLDER_TEMP) or pwm_raw in ("", self._PLACEHOLDER_PWM):
            custom_msgbox(self, "Introduce un valor en ambos campos.", "Error")
            return

        try:
            temp = int(temp_raw)
            pwm  = int(pwm_raw)
        except ValueError:
            custom_msgbox(self, "Los valores deben ser números enteros.", "Error")
            return

        if not (0 <= temp <= 100):
            custom_msgbox(self, "La temperatura debe estar entre 0 y 100 °C.", "Error")
            return
        if not (0 <= pwm <= 255):
            custom_msgbox(self, "El PWM debe estar entre 0 y 255.", "Error")
            return

        self._fan_controller.add_curve_point(temp, pwm)
        self._new_temp_var.set(self._PLACEHOLDER_TEMP)
        self._new_pwm_var.set(self._PLACEHOLDER_PWM)
        self._entry_temp.configure(text_color=COLORS['text_dim'])
        self._entry_pwm.configure(text_color=COLORS['text_dim'])
        self._refresh_curve_points()
        custom_msgbox(self, f"{Icons.CHECK_MARK} Punto añadido:\n{temp}°C → PWM {pwm}", "Éxito")

    # ── Curva ─────────────────────────────────────────────────────────────────

    def _refresh_curve_points(self):
        for widget in self._points_frame.winfo_children():
            widget.destroy()

        curve = self._file_manager.load_curve()

        if not curve:
            ctk.CTkLabel(
                self._points_frame,
                text="No hay puntos en la curva",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            ).pack(pady=10)
            return

        for point in curve:
            temp = point['temp']
            pwm  = point['pwm']

            point_frame = ctk.CTkFrame(self._points_frame, fg_color=COLORS['bg_medium'])
            point_frame.pack(fill="x", pady=2, padx=5)

            ctk.CTkLabel(
                point_frame,
                text=f"{temp}°C → PWM {pwm}",
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            ).pack(side="left", padx=10)

            make_futuristic_button(
                point_frame,
                text="Eliminar",
                command=lambda t=temp: self._remove_curve_point(t),
                width=10, height=3, font_size=12
            ).pack(side="right", padx=5)

    def _remove_curve_point(self, temp: int):
        self._fan_controller.remove_curve_point(temp)
        self._refresh_curve_points()

    # ── Botones inferiores ────────────────────────────────────────────────────

    def _create_bottom_buttons(self, parent):
        bottom = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)

        make_futuristic_button(
            bottom,
            text="Refrescar Curva",
            command=self._refresh_curve_points,
            width=15, height=6
        ).pack(side="left", padx=5)

    # ── Callbacks modo / PWM ──────────────────────────────────────────────────

    def _on_mode_change(self, mode: str):
        temp = self._system_monitor.get_current_stats()['temp']
        target_pwm = self._fan_controller.get_pwm_for_mode(
            mode=mode, temp=temp, manual_pwm=self._manual_pwm_var.get())
        percent = int(target_pwm / 255 * 100)
        self._manual_pwm_var.set(target_pwm)
        self._pwm_value_label.configure(text=f"Valor: {target_pwm} ({percent}%)")
        self._file_manager.write_state({"mode": mode, "target_pwm": target_pwm})

    def _on_pwm_change(self, value):
        pwm = int(float(value))
        percent = int(pwm / 255 * 100)
        self._pwm_value_label.configure(text=f"Valor: {pwm} ({percent}%)")
        if self._mode_var.get() == "manual":
            self._file_manager.write_state({"mode": "manual", "target_pwm": pwm})

    def _update_pwm_display(self):
        if not self.winfo_exists():
            return
        mode = self._mode_var.get()
        if mode != "manual":
            temp = self._system_monitor.get_current_stats()['temp']
            target_pwm = self._fan_controller.get_pwm_for_mode(
                mode=mode, temp=temp, manual_pwm=self._manual_pwm_var.get())
            percent = int(target_pwm / 255 * 100)
            self._manual_pwm_var.set(target_pwm)
            self._pwm_value_label.configure(text=f"Valor: {target_pwm} ({percent}%)")
        self.after(2000, self._update_pwm_display)
