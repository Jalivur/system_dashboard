"""
Ventana de control de audio del dashboard de sistema.
Caracteristicas:

VU meter animado con zonas verde/amarillo/rojo
Control de volumen por canal (Master, PCM, etc.) con slider y botones rapidos
Mute/unmute con test de sonido
Interfaz responsive para DSI
"""
# ── Imports ───────────────────────────────────────────────────────────────────
import threading
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import make_window_header, make_futuristic_button
from core import AudioService
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Constantes ────────────────────────────────────────────────────────────────

_VU_W          = DSI_WIDTH - 80    # Ancho de la barra VU
_VU_H          = 28                # Altura de la barra VU
_VU_REFRESH_MS = 150               # Refresco animación (~7 fps)
_VU_SEGMENTS   = 40                # Número de segmentos del VU meter
_VU_DECAY      = 2                 # Segmentos que cae por tick

# Colores del VU meter por zona
_VU_GREEN  = "#00cc66"
_VU_YELLOW = "#f0c030"
_VU_RED    = "#ff3333"
_VU_OFF    = "#1a1a2e"

# Umbrales de zona (en % de segmentos)
_THRESH_YELLOW = 0.65
_THRESH_RED    = 0.85


# ── AudioWindow ───────────────────────────────────────────────────────────────

class AudioWindow(ctk.CTkToplevel):
    """
    Ventana emergente para controlar el audio, incluyendo volumen, muteo, medidor de nivel de audio (VU meter) y accesos rápidos.

    Args:
        parent (CTk): Ventana padre que crea esta ventana emergente.
        audio_service (AudioService): Servicio de audio asociado a esta ventana.

    Raises:
        Ninguna excepción específica.

    Returns:
        Ninguno.
    """

    def __init__(self, parent, audio_service: AudioService):
        """
        Inicializa la ventana de control de audio.

        Args:
            parent: La ventana padre que contiene esta ventana de control de audio.
            audio_service (AudioService): El servicio de audio asociado a esta ventana.

        Raises:
            Ninguna excepción específica.

        Returns:
            Ninguno
        """
        super().__init__(parent)
        self._svc     = audio_service
        self._control = ctk.StringVar(master=self, value=AudioService.DEFAULT_CONTROL)
        self._vol_var = ctk.IntVar(master=self, value=50)
        self._muted   = False
        self._busy    = False          # bloquea llamadas amixer simultáneas

        # Estado interno del VU meter
        self._vu_target  = 0
        self._vu_current = 0.0
        self._vu_job     = None

        self.title("Control Audio")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._create_ui()
        self._load_state()
        self._vu_tick()
        logger.info("[AudioWindow] Ventana Abierta")

    # ── Construcción UI ───────────────────────────────────────────────────────

    def _create_ui(self):
        """
        Crea todos los elementos de la interfaz de usuario para el control de audio.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._header = make_window_header(
            main, title="CONTROL DE AUDIO", on_close=self._on_close,
        )

        # ── Icono central + porcentaje ────────────────────────────────────────
        icon_row = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=12)
        icon_row.pack(fill="x", padx=10, pady=(8, 4))

        self._main_icon = ctk.CTkLabel(
            icon_row,
            text=Icons.VOLUME_HIGH,
            font=(FONT_FAMILY, 64),
            text_color=COLORS['primary'],
        )
        self._main_icon.pack(side="left", padx=(20, 8), pady=10)

        info_col = ctk.CTkFrame(icon_row, fg_color="transparent")
        info_col.pack(side="left", fill="both", expand=True, pady=10)

        self._pct_label = ctk.CTkLabel(
            info_col,
            text="50%",
            font=(FONT_FAMILY, 42, "bold"),
            text_color=COLORS['text'],
            anchor="w",
        )
        self._pct_label.pack(anchor="w")

        self._state_label = ctk.CTkLabel(
            info_col,
            text="Reproduciendo",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['success'],
            anchor="w",
        )
        self._state_label.pack(anchor="w")

        # Selector de canal (discreto, a la derecha)
        ctrl_col = ctk.CTkFrame(icon_row, fg_color="transparent")
        ctrl_col.pack(side="right", padx=(0, 16), pady=10)

        ctk.CTkLabel(
            ctrl_col,
            text="Canal",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack()

        self._ctrl_menu = ctk.CTkOptionMenu(
            ctrl_col,
            values=self._svc.get_controls(),
            variable=self._control,
            command=self._on_control_change,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            button_color=COLORS['primary'],
            width=120,
            height=28,
        )
        self._ctrl_menu.pack()

        # ── VU meter ──────────────────────────────────────────────────────────
        vu_frame = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=10)
        vu_frame.pack(fill="x", padx=10, pady=(4, 4))

        ctk.CTkLabel(
            vu_frame,
            text="NIVEL",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(anchor="w", padx=14, pady=(8, 2))

        self._vu_canvas = tk.Canvas(
            vu_frame,
            width=_VU_W,
            height=_VU_H,
            bg=COLORS['bg_dark'],
            highlightthickness=0,
            bd=0,
        )
        self._vu_canvas.pack(padx=14, pady=(0, 10))
        self._vu_segments = []
        self._build_vu_segments()

        # ── Slider ───────────────────────────────────────────────────────────
        slider_frame = ctk.CTkFrame(main, fg_color="transparent")
        slider_frame.pack(fill="x", padx=10, pady=(4, 2))

        ctk.CTkLabel(
            slider_frame,
            text=Icons.VOLUME_MUTE,
            font=(FONT_FAMILY, FONT_SIZES['large']),
            text_color=COLORS['text_dim'],
            width=30,
        ).pack(side="left", padx=(4, 4))

        self._slider = ctk.CTkSlider(
            slider_frame,
            from_=0, to=100,
            variable=self._vol_var,
            command=self._on_slider,
            height=36,
            progress_color=COLORS['primary'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['secondary'],
        )
        self._slider.pack(side="left", fill="x", expand=True, padx=(0, 4))

        ctk.CTkLabel(
            slider_frame,
            text=Icons.VOLUME_HIGH,
            font=(FONT_FAMILY, FONT_SIZES['large']),
            text_color=COLORS['text_dim'],
            width=30,
        ).pack(side="left", padx=(4, 8))

        # ── Botones de acceso rápido ──────────────────────────────────────────
        quick_frame = ctk.CTkFrame(main, fg_color="transparent")
        quick_frame.pack(fill="x", padx=10, pady=(4, 4))

        for pct in (0, 25, 50, 75, 100):
            ctk.CTkButton(
                quick_frame,
                text=f"{pct}%",
                command=lambda v=pct: self._set_quick(v),
                width=60, height=60,
                fg_color=COLORS['bg_dark'],
                hover_color=COLORS['bg_light'],
                border_width=2,
                border_color=COLORS['border'],
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                corner_radius=8,
            ).pack(side="left", padx=4, expand=True, fill="x")

        # ── Botones mute / test ───────────────────────────────────────────────
        action_frame = ctk.CTkFrame(main, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(4, 6))

        self._mute_btn = make_futuristic_button(
            action_frame,
            text=f"{Icons.VOLUME_MUTE}  Silenciar",
            command=self._toggle_mute,
            width=16, height=7,
        )
        self._mute_btn.pack(side="left", padx=(0, 8), expand=True, fill="x")

        make_futuristic_button(
            action_frame,
            text=f"{Icons.PLAY}  Test sonido",
            command=self._play_test,
            width=16, height=7,
        ).pack(side="left", expand=True, fill="x")

    def _build_vu_segments(self):
        """
        Crea los segmentos iniciales del medidor VU, todos apagados.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        seg_w = (_VU_W - (_VU_SEGMENTS - 1) * 2) / _VU_SEGMENTS
        for i in range(_VU_SEGMENTS):
            x0 = i * (seg_w + 2)
            x1 = x0 + seg_w
            rect = self._vu_canvas.create_rectangle(
                x0, 0, x1, _VU_H,
                fill=_VU_OFF, outline="", width=0,
            )
            self._vu_segments.append(rect)

    # ── VU meter animado ──────────────────────────────────────────────────────

    def _vu_tick(self):
        """
        Actualiza la animación del medidor de volumen (VU meter) suavizando y dibujando el nivel actual.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if not self.winfo_exists():
            return

        target = 0.0 if self._muted else float(self._vu_target)

        prev = self._vu_current
        if self._vu_current < target:
            self._vu_current = min(target, self._vu_current + _VU_DECAY * 1.5)
        elif self._vu_current > target:
            self._vu_current = max(target, self._vu_current - _VU_DECAY * 1.5)

        # Solo redibujar si el nivel cambió
        if self._vu_current != prev:
            self._draw_vu(self._vu_current)

        self._vu_job = self.after(_VU_REFRESH_MS, self._vu_tick)

    def _draw_vu(self, level: float):
        """
        Actualiza la visualización del medidor de nivel de audio (VU meter) según el nivel de audio proporcionado.

        Args:
            level (float): Nivel de audio actual, utilizado para determinar el color y cantidad de segmentos a iluminar.

        Raises:
            Ninguna excepción es lanzada explícitamente en este método.
        """
        lit = int(level)
        for i, rect in enumerate(self._vu_segments):
            if i < lit:
                ratio = i / _VU_SEGMENTS
                if ratio >= _THRESH_RED:
                    color = _VU_RED
                elif ratio >= _THRESH_YELLOW:
                    color = _VU_YELLOW
                else:
                    color = _VU_GREEN
            else:
                color = _VU_OFF
            self._vu_canvas.itemconfig(rect, fill=color)

    def _set_vu_from_vol(self, vol: int):
        """
        Establece el objetivo del medidor de volumen (VU) en función del volumen dado.

        Args:
            vol (int): El volumen en el rango 0-100.

        Returns:
            None

        Raises:
            None
        """
        self._vu_target = int(vol / 100 * _VU_SEGMENTS)

    # ── Helpers de threading ──────────────────────────────────────────────────

    def _run_async(self, fn, *args, on_done=None):
        """
        Ejecuta una función de manera asíncrona en un hilo daemon.

        Args:
            fn: La función a ejecutar de manera asíncrona.
            *args: Los argumentos a pasar a la función.

        Raises:
            None

        Returns:
            None
        """
        def _worker():
            """Worker para funciones asíncronas."""
            result = fn(*args)
            if on_done and self.winfo_exists():
                self.after(0, lambda: on_done(result))
        threading.Thread(target=_worker, daemon=True, name="AudioCmd").start()

    # ── Lógica ────────────────────────────────────────────────────────────────

    def _load_state(self):
        """
        Carga asincrónicamente el estado actual del volumen y mute.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        def _worker():
            """Worker para funciones asíncronas."""
            control = self._control.get()
            vol     = self._svc.get_volume(control)
            muted   = self._svc.is_muted(control)
            if self.winfo_exists():
                self.after(0, lambda: self._apply_state(vol, muted))
        threading.Thread(target=_worker, daemon=True, name="AudioLoad").start()

    def _apply_state(self, vol: int, muted: bool):
        """
        Aplica el estado de volumen y mute a la interfaz de usuario.

        Args:
            vol (int): El volumen a aplicar, en porcentaje.
            muted (bool): Indica si el audio está muteado.

        Returns:
            None

        Raises:
            None
        """
        if not self.winfo_exists():
            return
        if vol >= 0:
            self._vol_var.set(vol)
            self._pct_label.configure(text=f"{vol}%")
            self._set_vu_from_vol(vol)
        self._muted = muted
        self._update_mute_ui()

    def _on_slider(self, value):
        """
        Actualiza el estado de la ventana de audio en respuesta a un cambio en el slider de volumen.

        Args:
            value (int): El nuevo valor del slider de volumen.

        Returns:
            None

        Raises:
            None
        """
        vol = int(value)
        self._pct_label.configure(text=f"{vol}%")
        self._set_vu_from_vol(vol)
        if self._muted:
            self._muted = False
        self._update_mute_ui()
        self._run_async(self._svc.set_volume, vol, self._control.get())

    def _set_quick(self, pct: int):
        """
        Establece el volumen con botones rápidos.

        Args:
            pct (int): Porcentaje de volumen.

        Raises:
            Ninguna excepción relevante.

        Returns:
            Ninguno
        """
        if self._busy:
            return
        self._busy = True
        self._vol_var.set(pct)
        self._pct_label.configure(text=f"{pct}%")
        self._set_vu_from_vol(pct)
        if self._muted and pct > 0:
            self._muted = False
            self._update_mute_ui()

        def _worker():
            """Worker para funciones asíncronas."""
            self._svc.set_volume(pct, self._control.get())
            if self.winfo_exists():
                self.after(0, self._unlock)
        threading.Thread(target=_worker, daemon=True, name="AudioQuick").start()

    def _unlock(self):
        """
        Desbloquea la interfaz de usuario después de una operación rápida.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._busy = False

    def _on_control_change(self, _value):
        """
        Recarga el estado interno al detectar un cambio en el canal de control.

        Args:
            _value: Nuevo valor del canal de control.

        """
        self._load_state()

    def _toggle_mute(self):
        """
        Alterna el estado de mute del audio.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
        if self._busy:
            return
        self._busy = True

        def _worker():
            """Worker para funciones asíncronas."""
            muted = self._svc.toggle_mute(self._control.get())
            if self.winfo_exists():
                self.after(0, lambda: self._apply_mute(muted))
        threading.Thread(target=_worker, daemon=True, name="AudioMute").start()

    def _apply_mute(self, muted: bool):
        """
        Aplica el estado mute a la interfaz de usuario.

        Args:
            muted (bool): Indica si el audio debe estar muteado o no.

        Returns:
            None

        Raises:
            None
        """
        if not self.winfo_exists():
            return
        self._muted = muted
        self._update_mute_ui()
        self._busy = False

    def _play_test(self):
        """
        Inicia una reproducción de prueba de audio en un hilo independiente.

        La reproducción busca el archivo de prueba en varias rutas conocidas.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        threading.Thread(
            target=self._svc.play_test,
            daemon=True, name='AudioTest'
        ).start()

    def _update_mute_ui(self):
        """
        Actualiza la interfaz de usuario según el estado de silencio del audio.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if not self.winfo_exists():
            return
        if self._muted:
            self._main_icon.configure(text=Icons.VOLUME_MUTE, text_color=COLORS['danger'])
            self._state_label.configure(text="Silenciado", text_color=COLORS['danger'])
            self._mute_btn.configure(text=f"{Icons.VOLUME_HIGH}  Activar audio")
            self._slider.configure(state="disabled", button_color=COLORS['text_dim'])
            self._header.status_label.configure(
                text="SILENCIADO", text_color=COLORS['danger'])
        else:
            vol   = self._vol_var.get()
            icon  = Icons.VOLUME_MUTE if vol == 0 else Icons.VOLUME_HIGH
            color = COLORS['text_dim'] if vol == 0 else COLORS['primary']
            self._main_icon.configure(text=icon, text_color=color)
            self._state_label.configure(text="Reproduciendo", text_color=COLORS['success'])
            self._mute_btn.configure(text=f"{Icons.VOLUME_MUTE}  Silenciar")
            self._slider.configure(state="normal", button_color=COLORS['primary'])
            self._header.status_label.configure(text=f"Vol {vol}%", text_color=COLORS['text_dim'])

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _on_close(self):
        """
        Maneja el cierre de la ventana de audio.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if self._vu_job:
            self.after_cancel(self._vu_job)
        logger.info("[AudioWindow] Ventana cerrada")
        self.destroy()
