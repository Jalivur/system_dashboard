"""
Ventana de control de dispositivos Homebridge
Muestra enchufes e interruptores y permite encenderlos / apagarlos
"""
import threading
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from ui.styles import StyleManager, make_futuristic_button, make_window_header, make_homebridge_switch
from ui.widgets import custom_msgbox
from core.homebridge_monitor import HomebridgeMonitor
from utils.logger import get_logger

logger = get_logger(__name__)

# Intervalo de refresco de la ventana (ms)
HB_UPDATE_MS = 5000


class HomebridgeWindow(ctk.CTkToplevel):
    """Ventana de control de dispositivos Homebridge."""

    def __init__(self, parent, homebridge_monitor: HomebridgeMonitor):
        super().__init__(parent)
        self.hb = homebridge_monitor
        self._accessories = []
        self._update_job = None
        self._busy = False  # evita peticiones simultáneas

        # Configurar ventana
        self.title("Homebridge")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        self._create_ui()
        self._schedule_update()
        logger.info("[HomebridgeWindow] Ventana abierta")

    # ── Interfaz ──────────────────────────────────────────────────────────────

    def _create_ui(self):
        """Construye la interfaz completa."""
        self.main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        self.main.pack(fill="both", expand=True, padx=5, pady=5)

        # ── Header unificado ──────────────────────────────────────────────────
        self._header = make_window_header(
            self.main,
            title="HOMEBRIDGE",
            on_close=self._on_close,
            status_text="Conectando...",
        )

        # ── Barra de estado ───────────────────────────────────────────────────
        status_bar = ctk.CTkFrame(self.main, fg_color=COLORS['bg_dark'])
        status_bar.pack(fill="x", padx=5, pady=(0, 4))
        self._status_label = ctk.CTkLabel(
            status_bar,
            text="",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="w",
        )
        self._status_label.pack(pady=4, padx=10, fill="x")

        # ── Área scrollable de dispositivos ───────────────────────────────────
        scroll_container = ctk.CTkFrame(self.main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        max_height = DSI_HEIGHT - 220
        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=max_height,
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

        self._device_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window(
            (0, 0), window=self._device_frame, anchor="nw", width=DSI_WIDTH - 50
        )
        self._device_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        self._content_frame = self._device_frame
        # ── Botón Refrescar ───────────────────────────────────────────────────
        bottom = ctk.CTkFrame(self.main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=8, padx=10)

        make_futuristic_button(
            bottom,
            text="⟳  Refrescar",
            command=self._force_refresh,
            width=15,
            height=6,
        ).pack(side="left", padx=5)

    # ── Actualización ─────────────────────────────────────────────────────────

    def _schedule_update(self):
        """Programa la siguiente actualización."""
        self._update_job = self.after(100, self._fetch_and_render)

    def _force_refresh(self):
        """Fuerza un refresco inmediato."""
        if self._update_job:
            self.after_cancel(self._update_job)
        self._fetch_and_render()

    def _fetch_and_render(self):
        """Lanza la petición en background y actualiza la UI cuando termina."""
        if not self.hb._running:
            StyleManager.show_service_stopped_banner(self._device_frame, "Homebridge Monitor")
            self._update_job = self.after(HB_UPDATE_MS, self._fetch_and_render)
            return
        if self._busy:
            return
        if self._busy:
            return
        self._busy = True
        self._set_status("Actualizando...")

        def fetch():
            accessories = self.hb.get_accessories()
            self.after(0, lambda: self._render(accessories))

        threading.Thread(target=fetch, daemon=True, name="HB-Fetch").start()

    def _render(self, accessories):
        """Actualiza la lista de dispositivos en el hilo principal."""
        self._accessories = accessories
        self._busy = False

        # ── Header status ──────────────────────────────────────────────────────
        if self.hb.is_reachable():
            on_count = sum(1 for a in accessories if a["on"])
            total = len(accessories)
            header_status = f"{on_count}/{total} encendidos"
            self._set_status(
                f"{total} dispositivo{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}"
            )
        else:
            header_status = "⚠ Sin conexión"
            self._set_status("No se pudo conectar con Homebridge — verifica host y credenciales")

        # Actualizar status del header
        try:
            self._header.status_label.configure(text=header_status)
        except Exception:
            pass

        # ── Redibujar grid 2 columnas ──────────────────────────────────────────
        for widget in self._device_frame.winfo_children():
            widget.destroy()

        if not accessories:
            msg = (
                "Sin conexión con Homebridge" if not self.hb.is_reachable()
                else "No se encontraron enchufes ni interruptores"
            )
            ctk.CTkLabel(
                self._device_frame,
                text=msg,
                text_color=COLORS.get('warning', '#ffaa00'),
                font=(FONT_FAMILY, FONT_SIZES['medium']),
            ).pack(pady=30)
        else:
            self._device_frame.grid_columnconfigure(0, weight=1, uniform="col")
            self._device_frame.grid_columnconfigure(1, weight=1, uniform="col")
            for idx, acc in enumerate(accessories):
                self._create_device_card(acc, idx // 2, idx % 2)

        # Programar siguiente actualización
        self._update_job = self.after(HB_UPDATE_MS, self._fetch_and_render)

    def _create_device_card(self, acc: dict, grid_row: int, grid_col: int):
        """Tarjeta adaptada al tipo de dispositivo."""
        dev_type = acc.get("type", "switch")
        is_fault = acc.get("fault", False)
        disabled = is_fault or acc.get("inactive", False)

        card = ctk.CTkFrame(
            self._device_frame,
            fg_color=COLORS['bg_dark'],
            corner_radius=8,
        )
        card.grid(row=grid_row, column=grid_col, sticky="nsew", padx=4, pady=4)

        if disabled:
            ctk.CTkLabel(
                card, text="⚠  FALLO",
                text_color=COLORS.get('danger', '#ff4444'),
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            ).pack(pady=(10, 0))
        else:
            ctk.CTkFrame(card, fg_color="transparent", height=10).pack()

        if dev_type in ("switch", "light"):
            self._card_switch(card, acc, disabled)
        elif dev_type == "thermostat":
            self._card_thermostat(card, acc, disabled)
        elif dev_type == "sensor":
            self._card_sensor(card, acc)
        elif dev_type == "blind":
            self._card_blind(card, acc, disabled)

    def _card_switch(self, card, acc, disabled):
        """Switch ON/OFF (enchufe, interruptor, luz básica)."""
    # ── Bloquear por nombre ──────────────────────────────
        blocked_names = ["Rpi5"]  # nombres a bloquear
        read_only = acc["displayName"] in blocked_names
        effective_disabled = disabled and not read_only  # mantén fallo/desactivado real

        def on_toggle(new_state, uid=acc["uniqueId"]):
            if read_only:
                # Solo mostrar mensaje o ignorar
                custom_msgbox(
                    parent=self, 
                    title="Aviso", 
                    text=f"El dispositivo '{acc['displayName']}' no puede ser manipulado.",
                )
                return
            self._toggle(uid, new_state)

        sw = make_homebridge_switch(
            card,
            text=acc["displayName"],
            command=on_toggle,
            is_on=acc["on"],
            disabled=disabled,
        )
        sw.pack(padx=16, pady=(8, 18))

    def _card_thermostat(self, card, acc, disabled):
        """Termostato: temperatura actual + botones +/- para objetivo."""
        ctk.CTkLabel(
            card,
            text=acc["displayName"],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
        ).pack(pady=(4, 0))

        ctk.CTkLabel(
            card,
            text=f"Actual: {acc['current_temp']:.1f}°C",
            text_color=COLORS.get('primary', '#00ffff'),
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
        ).pack()

        target_frame = ctk.CTkFrame(card, fg_color="transparent")
        target_frame.pack(pady=(4, 12))

        target_var = ctk.StringVar(value=f"{acc['target_temp']:.1f}°C")

        ctk.CTkLabel(
            target_frame, text="Objetivo:",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
        ).pack(side="left", padx=4)

        target_lbl = ctk.CTkLabel(
            target_frame, textvariable=target_var,
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
        )
        target_lbl.pack(side="left", padx=4)

        uid   = acc["uniqueId"]
        _temp = [acc["target_temp"]]  # mutable closure

        def change(delta):
            if disabled:
                return
            _temp[0] = round(_temp[0] + delta, 1)
            target_var.set(f"{_temp[0]:.1f}°C")
            threading.Thread(
                target=lambda: self.hb.set_target_temp(uid, _temp[0]),
                daemon=True, name="HB-SetTemp"
            ).start()

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=(0, 12))

        for label, delta in [("  −  ", -0.5), ("  +  ", +0.5)]:
            make_futuristic_button(
                btn_frame, text=label,
                command=lambda d=delta: change(d),
                width=8, height=5,
            ).pack(side="left", padx=4)

    def _card_sensor(self, card, acc):
        """Sensor de temperatura / humedad (solo lectura)."""
        ctk.CTkLabel(
            card,
            text=acc["displayName"],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
        ).pack(pady=(4, 0))

        if acc.get("temp") is not None:
            ctk.CTkLabel(
                card,
                text=f"🌡  {acc['temp']:.1f}°C",
                text_color=COLORS.get('primary', '#00ffff'),
                font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold"),
            ).pack(pady=4)

        if acc.get("humidity") is not None:
            ctk.CTkLabel(
                card,
                text=f"💧  {acc['humidity']:.0f}%",
                text_color=COLORS.get('secondary', '#aaaaff'),
                font=(FONT_FAMILY, FONT_SIZES['large']),
            ).pack(pady=(0, 12))

    def _card_blind(self, card, acc, disabled):
        """Persiana / estor con barra de posición."""
        ctk.CTkLabel(
            card,
            text=acc["displayName"],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
        ).pack(pady=(4, 0))

        pos_var = ctk.IntVar(value=acc["position"])

        ctk.CTkLabel(
            card,
            text=f"Posición: {acc['position']}%",
            text_color=COLORS.get('primary', '#00ffff'),
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
        ).pack()

        # Barra visual (solo lectura — las persianas se controlan desde HomeKit)
        ctk.CTkProgressBar(
            card,
            variable=pos_var,
            progress_color=COLORS.get('primary', '#00ffff'),
            fg_color=COLORS['bg_light'],
            width=140, height=12,
        ).pack(pady=(4, 12))
    # ── Acciones ──────────────────────────────────────────────────────────────

    def _toggle(self, unique_id: str, turn_on: bool):
        """Envía el comando ON/OFF al dispositivo en background."""
        if not self.hb._running:
            StyleManager.show_service_stopped_banner(self._device_frame, "Homebridge Monitor")
            self._update_job = self.after(HB_UPDATE_MS, self._fetch_and_render)
            return
        if self._busy:
            return
        def send():
            ok = self.hb.toggle(unique_id, turn_on)
            if ok:
                # Refresca inmediatamente para reflejar el nuevo estado
                self.after(500, self._force_refresh)
            else:
                self.after(
                    0,
                    lambda: custom_msgbox(
                        self, "Error",
                        "No se pudo enviar el comando al dispositivo.\n"
                        "Verifica la conexión con Homebridge.",
                        tipo="error"
                    )
                )

        threading.Thread(target=send, daemon=True, name="HB-Toggle").start()

    def _set_status(self, text: str):
        """Actualiza la barra de estado inferior."""
        try:
            self._status_label.configure(text=text)
        except Exception:
            pass

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _on_close(self):
        """Cancela actualizaciones pendientes y cierra la ventana."""
        if self._update_job:
            self.after_cancel(self._update_job)
        logger.info("[HomebridgeWindow] Ventana cerrada")
        self.destroy()
