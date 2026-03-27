"""
Ventana de estadísticas de Pi-hole.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
, Icons)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from core.pihole_monitor import PiholeMonitor
from utils.logger import get_logger
import threading

logger = get_logger(__name__)

UPDATE_MS = 5000   # refresco visual de la ventana


class PiholeWindow(ctk.CTkToplevel):
    """Ventana de estadísticas de Pi-hole."""

    def __init__(self, parent, pihole_monitor: PiholeMonitor):
        """
        Inicializa la ventana de estadísticas de Pi-hole.
        
        Configura el título, geometría, posición y propiedades de la ventana Toplevel.
        Crea la interfaz de usuario, programa la primera actualización automática
        y registra la apertura en el logger.
        
        Args:
            parent: Ventana padre (generalmente la ventana principal del dashboard).
            pihole_monitor (PiholeMonitor): Instancia del monitor para obtener estadísticas.
        """
        super().__init__(parent)
        self._pihole = pihole_monitor
        self._update_job = None

        self.title("Pi-hole")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._create_ui()
        self._schedule_update()
        logger.info("[PiholeWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        """
        Crea toda la interfaz gráfica de usuario (UI) de la ventana.
        
        Construye el frame principal, el header con título y estado, el contenedor
        con scroll, el canvas, el grid de 6 tarjetas métricas (queries, bloqueadas,
        % bloqueado, dominios, clientes, estado), y el botón de actualización manual.
        Inicializa labels para valores dinámicos.
        """
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._header = make_window_header(
            main, title="PI-HOLE",
            on_close=self._on_close,
            status_text="Cargando...",
        )
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS["bg_medium"])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        self._inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window(
            (0, 0), window=self._inner,
            anchor="nw", width=DSI_WIDTH - 50)
        self._inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        # Grid 2×2 de tarjetas métricas
        grid = ctk.CTkFrame(self._inner, fg_color=COLORS['bg_medium'])
        grid.pack(fill="both", expand=True, padx=5, pady=5)
        grid.grid_columnconfigure(0, weight=1, uniform="col")
        grid.grid_columnconfigure(1, weight=1, uniform="col")
        self._grid_frame = grid

        # Tarjetas: (título, clave_interna, unidad, color)
        cards_config = [
            ("QUERIES HOY",       "queries_today",   "",   COLORS['primary']),
            ("BLOQUEADAS HOY",    "blocked_today",   "",   COLORS['danger']),
            ("% BLOQUEADO",       "percent_blocked", "%",  COLORS['warning']),
            ("DOMINIOS EN LISTA", "domains_blocked", "",   COLORS['success']),
            ("CLIENTES ÚNICOS",   "unique_clients",  "",   COLORS['secondary']),
            ("ESTADO",            "status",          "",   COLORS['primary']),
        ]

        self._value_labels = {}

        for i, (title, key, unit, color) in enumerate(cards_config):
            row, col = divmod(i, 2)
            card = ctk.CTkFrame(grid, fg_color=COLORS['bg_dark'], corner_radius=8)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            ctk.CTkLabel(
                card, text=title,
                text_color=COLORS['text_dim'],
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                anchor="w",
            ).pack(anchor="w", padx=10, pady=(8, 2))

            val_lbl = ctk.CTkLabel(
                card, text="—",
                text_color=color,
                font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold"),
                anchor="w",
            )
            val_lbl.pack(anchor="w", padx=10, pady=(0, 10))
            self._value_labels[key] = (val_lbl, unit, color)

        # Botón forzar refresco
        bottom = ctk.CTkFrame(self._inner, fg_color="transparent")
        bottom.pack(fill="x", pady=6, padx=10)
        make_futuristic_button(
            bottom, text="⟳  Actualizar",
            command=self._force_refresh,
            width=13, height=5,
        ).pack(side="left")

    # ── Actualización ─────────────────────────────────────────────────────────

    def _schedule_update(self):
        """
        Programa la primera actualización/renderizado de la interfaz.
        
        Utiliza self.after(100ms) para llamar a _render inicialmente, iniciando
        el ciclo de actualizaciones automáticas.
        """
        self._update_job = self.after(100, self._render)

    def _force_refresh(self):        
        """        
        Fuerza actualización manual de estadísticas Pi-hole en background.        
        
        1. Verifica monitor activo       
        2. Lanza thread daemon -> self._pihole.fetch_now()        
        3. Status -> "Actualizando..."        
        4. self._render() @2000ms        
        
        Non-blocking UI.        
        """        
        if not self._pihole.is_running():            
            return

        threading.Thread(
            target=self._pihole.fetch_now(),
            daemon=True, name="PiholeForceRefresh"
        ).start()
        self._header.status_label.configure(text="Actualizando...")
        # Releer tras 2s para dar tiempo al fetch
        self.after(2000, self._render)

    def _render(self):
        """Actualiza los valores en pantalla con la caché del monitor."""
        if not self.winfo_exists():
            return
        if not self._pihole.is_running():
            StyleManager.show_service_stopped_banner(self._grid_frame, "Pi-hole Monitor")
            self._update_job = self.after(UPDATE_MS, self._render)
            return
        
        stats = self._pihole.get_stats()

        if not stats.get("reachable", False):
            self._header.status_label.configure(text="" + Icons.WARNING + " Sin conexión")
        else:
            status_str = "" + Icons.OK + " Activo" if stats.get("status") == "enabled" else "" + Icons.PAUSE + " Pausado"
            pct = stats.get("percent_blocked", 0.0)
            self._header.status_label.configure(
                text=f"{status_str}  ·  {pct:.1f}% bloqueado")

        for key, (lbl, unit, color) in self._value_labels.items():
            value = stats.get(key, "—")
            if key == "status":
                if not stats.get("reachable"):
                    text       = "Sin conexión"
                    text_color = COLORS['danger']
                elif value == "enabled":
                    text       = "" + Icons.OK + " Activo"
                    text_color = COLORS['success']
                else:
                    text       = "" + Icons.PAUSE + " Pausado"
                    text_color = COLORS['warning']
                lbl.configure(text=text, text_color=text_color)
            elif key == "percent_blocked":
                lbl.configure(text=f"{value:.1f}{unit}")
            else:
                lbl.configure(
                    text=f"{value:,}{unit}".replace(",", ".") if isinstance(value, int) else str(value)
                )

        self._update_job = self.after(UPDATE_MS, self._render)

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _on_close(self):
        """
        Maneja el cierre ordenado de la ventana de Pi-hole.
        
        Realiza cleanup:
        - Cancela el job de actualización pendiente
        - Registra el cierre en logs
        - Destruye la ventana
        """
        if self._update_job:
            self.after_cancel(self._update_job)
        logger.info("[PiholeWindow] Ventana cerrada")
        self.destroy()
