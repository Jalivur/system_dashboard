"""
ui/windows/i2c_window.py

Ventana de escaneo I2C — muestra dispositivos detectados en cada bus.
Solo lectura. Refresco manual o automático cada 30s.
"""
import tkinter as tk
import time
import threading
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger

logger = get_logger(__name__)


class I2CWindow(ctk.CTkToplevel):
    """Ventana de escaneo I2C — solo lectura."""

    _REFRESH_MS = 30_000   # refresco automático cada 30s

    def __init__(self, parent, i2c_monitor):
        """Inicializa la ventana de escaneo I2C.

        Configura la ventana principal, crea la interfaz de usuario, inicia el bucle
        de actualización automática y registra el evento de apertura en el logger.

        Args:
            parent: Ventana padre (CTkToplevel).
            i2c_monitor: Instancia del monitor I2C para obtener estadísticas.
        """
        super().__init__(parent)

        self._mon          = i2c_monitor
        self._after_id     = None
        self._scanning     = False

        self.title("Scanner I2C")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._create_ui()
        self._update()
        logger.info("[I2CWindow] Ventana abierta")

    # ── Construcción UI ───────────────────────────────────────────────────────

    def _create_ui(self):
        """Crea todos los elementos de la interfaz de usuario.

        Incluye header, barra de acciones (botón de escaneo, labels de estado),
        y área scrollable con canvas para mostrar los resultados por bus I2C.
        """
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main,
            title="SCANNER I²C",
            on_close=self.destroy,
            status_text="Solo lectura — no escribe en el bus",
        )

        # ── Barra de acciones ─────────────────────────────────────────────────
        action_bar = ctk.CTkFrame(main, fg_color="transparent")
        action_bar.pack(fill="x", padx=8, pady=(4, 0))

        self._scan_btn = make_futuristic_button(
            action_bar,
            text=f"{Icons.REFRESH}  Escanear ahora",
            command=self._on_scan,
            width=18, height=7, font_size=FONT_SIZES['small'],
            state="normal"
        )
        self._scan_btn.pack(side="left", padx=4)

        self._status_lbl = ctk.CTkLabel(
            action_bar, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        )
        self._status_lbl.pack(side="left", padx=12)

        self._total_lbl = ctk.CTkLabel(
            action_bar, text="",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
            anchor="e",
        )
        self._total_lbl.pack(side="right", padx=8)

        # ── Área scrollable ───────────────────────────────────────────────────
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=6)

        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        sb = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        sb.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(sb)
        canvas.configure(yscrollcommand=sb.set)

        self._inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window(
            (0, 0), window=self._inner,
            anchor="nw", width=DSI_WIDTH - 50)
        self._inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # ── Actualización ─────────────────────────────────────────────────────────

    def _update(self) -> None:
        """Actualiza la interfaz periódicamente (cada 30s).

        Verifica si la ventana existe y si el monitor I2C está activo.
        Renderiza estadísticas o muestra banner de servicio detenido. Programa la
        siguiente actualización.
        """
        if not self.winfo_exists():
            return
        if not self._mon.is_running():
            StyleManager.show_service_stopped_banner(self._inner, "I2C Monitor" )
            self._scan_btn.configure(state="disabled")
            return
        self._render(self._mon.get_stats())
        self._after_id = self.after(self._REFRESH_MS, self._update)

    def _render(self, stats: dict) -> None:
        """Renderiza las estadísticas I2C en la interfaz.

        Limpia el área, maneja errores o datos vacíos, muestra total de dispositivos
        y renderiza cards por bus con sus dispositivos.

        Args:
            stats (dict): Diccionario con 'buses', 'total', 'error'.
        """
        # Limpiar área
        for w in self._inner.winfo_children():
            w.destroy()

        if not stats:
            self._show_placeholder("Escaneando buses I²C...")
            self._total_lbl.configure(text="")
            return

        error = stats.get("error", "")
        if error:
            self._show_placeholder(error, color=COLORS['danger'])
            self._total_lbl.configure(text="")
            return

        buses = stats.get("buses", [])
        total = stats.get("total", 0)

        self._total_lbl.configure(
            text=f"{total} dispositivo{'s' if total != 1 else ''} detectado{'s' if total != 1 else ''}")

        if not buses:
            self._show_placeholder("No se encontraron buses I²C")
            return

        for bus_info in buses:
            self._render_bus(bus_info)

    def _render_bus(self, bus_info: dict) -> None:
        """Renderiza la card de un bus I2C específico.

        Crea la card con cabecera (label y count), línea divisoria, lista de dispositivos
        o mensaje vacío, y spacer inferior.

        Args:
            bus_info (dict): Info del bus con 'label', 'count', 'devices'.
        """
        devices = bus_info.get("devices", [])
        count   = bus_info.get("count", 0)

        # Card por bus
        card = ctk.CTkFrame(self._inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(6, 2))

        # Cabecera del bus
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            hdr,
            text=f"{Icons.I2C}  {bus_info.get('label', '--')}",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(side="left")

        color_count = COLORS['success'] if count > 0 else COLORS['text_dim']
        ctk.CTkLabel(
            hdr,
            text=f"{count} dispositivo{'s' if count != 1 else ''}",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=color_count,
            anchor="e",
        ).pack(side="right")

        ctk.CTkFrame(
            card, fg_color=COLORS['border'], height=1, corner_radius=0
        ).pack(fill="x", padx=14, pady=(0, 6))

        if not devices:
            ctk.CTkLabel(
                card,
                text="Sin dispositivos detectados",
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
            ).pack(pady=(4, 10))
        else:
            for dev in devices:
                self._render_device(card, dev)

        ctk.CTkFrame(card, fg_color="transparent", height=4).pack()

    def _render_device(self, parent, dev: dict) -> None:
        """Renderiza una fila individual de dispositivo I2C.

        Crea badge con dirección hex, label con nombre y label con decimal.

        Args:
            parent: Frame contenedor de la fila.
            dev (dict): Info del dispositivo con 'addr_hex', 'name', 'addr'.
        """
        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=6)
        row.pack(fill="x", padx=14, pady=2)

        # Dirección hex — badge estilo
        addr_lbl = ctk.CTkLabel(
            row,
            text=dev.get("addr_hex", "--"),
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['bg_dark'],
            fg_color=COLORS['primary'],
            corner_radius=6,
            width=64, height=32,
        )
        addr_lbl.pack(side="left", padx=(10, 0), pady=6)

        # Nombre del dispositivo
        ctk.CTkLabel(
            row,
            text=dev.get("name", "Desconocido"),
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text'],
            anchor="w",
        ).pack(side="left", padx=14, pady=6)

        # Decimal
        ctk.CTkLabel(
            row,
            text=f"dec {dev.get('addr', '--')}",
            font=(FONT_FAMILY, FONT_SIZES['small'] - 2),
            text_color=COLORS['text_dim'],
            anchor="e",
        ).pack(side="right", padx=14, pady=6)

    def _show_placeholder(self, text: str, color: str = None) -> None:
        """Muestra un mensaje placeholder centrado en el área principal.

        Útil para estados de carga, errores o sin datos.

        Args:
            text (str): Texto a mostrar.
            color (str, opcional): Color del texto. Defaults to COLORS['text_dim'].
        """
        ctk.CTkLabel(
            self._inner,
            text=text,
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=color or COLORS['text_dim'],
        ).pack(pady=40)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_scan(self) -> None:
        """Inicia un escaneo manual I2C en thread separado.

        Deshabilita botón, muestra status 'Escaneando...',
        llama a monitor.scan_now() y agenda _on_scan_done.
        """
        if self._scanning:
            return
        self._scanning = True
        self._scan_btn.configure(state="disabled")
        self._status_lbl.configure(text="Escaneando...", text_color=COLORS['text_dim'])

        def _do():
            """Función interna para escaneo: ejecuta scan_now, espera y agenda callback."""
            self._mon.scan_now()
            time.sleep(2)
            if self.winfo_exists():
                self.after(0, self._on_scan_done)

        threading.Thread(target=_do, daemon=True, name="I2CScanUI").start()

    def _on_scan_done(self) -> None:
        """Callback ejecutado tras completar el escaneo manual.

        Re-habilita el botón, limpia status y refresca la visualización.
        """
        if not self.winfo_exists():
            return
        self._scanning = False
        self._scan_btn.configure(state="normal")
        self._status_lbl.configure(text="")
        self._render(self._mon.get_stats())

    # ── Cierre limpio ─────────────────────────────────────────────────────────

    def destroy(self) -> None:
        """Destruye la ventana limpiando el temporizador de actualización.

        Cancela el after_id si existe y llama al destroy del padre.
        Registra el cierre en logger.
        """
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        super().destroy()
        logger.info("[I2CWindow] Ventana cerrada")

