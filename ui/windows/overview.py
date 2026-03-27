"""
Ventana de resumen general del sistema.
Muestra todas las métricas críticas en un solo vistazo.
Pensada para usarse como pantalla de reposo en la DSI.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y,
    CPU_WARN,  CPU_CRIT,
    RAM_WARN,  RAM_CRIT,
    TEMP_WARN, TEMP_CRIT, Icons)
from ui.styles import StyleManager, make_window_header
from utils.logger import get_logger

logger = get_logger(__name__)

_REFRESH_MS = 2000


class OverviewWindow(ctk.CTkToplevel):
    """Ventana de resumen — métricas críticas en un vistazo."""

    def __init__(self, parent, system_monitor, service_monitor,
                 pihole_monitor, network_monitor, disk_monitor):
        """Inicializador principal de OverviewWindow.

        Configura ventana DSI sin bordes en posición fija, almacena referencias
        a 5 monitores, inicializa widgets/running, crea UI y lanza update loop.

        Args:
            parent: Ventana padre.
            system_monitor: Monitor sistema (CPU/RAM/temp).
            service_monitor: Monitor servicios.
            pihole_monitor: Monitor Pi-hole.
            network_monitor: Monitor red.
            disk_monitor: Monitor disco.
        """
        super().__init__(parent)
        self._system_monitor  = system_monitor
        self._service_monitor = service_monitor
        self._pihole_monitor  = pihole_monitor
        self._network_monitor = network_monitor
        self._disk_monitor    = disk_monitor

        self.title("Resumen del Sistema")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._widgets = {}
        self._running = True

        self._create_ui()
        self._update()
        logger.info("[OverviewWindow] Ventana abierta")

    def destroy(self):
        """Destructor seguro: detiene loop _update y llama super().destroy()."""
        self._running = False
        super().destroy()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        """Construye la interfaz completa del dashboard de resumen.

        Estructura:
        - Frame principal con header draggable.
        - Canvas con scrollbar para contenido.
        - Grid 2 columnas x 3 filas para tarjetas (CPU, RAM, Temp, Disco, Red, Servicios).
        - Fila completa para Pi-hole con 4 sub-métricas.
        - Registra todos los labels de valores en self._widgets para actualizaciones.
        """
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="RESUMEN DEL SISTEMA", on_close=self.destroy)

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

        grid = ctk.CTkFrame(self._inner, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=5, pady=5)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        cards = [
            ("cpu",      "" + Icons.FIRE + " CPU"),
            ("ram",      f"{Icons.RAM} RAM"),
            ("temp",     "" + Icons.THERMOMETER + "️ Temperatura"),
            ("disk",     "" + Icons.MONITOR_DISCO + " Disco"),
            ("net",      "" + Icons.TAB_RED + " Red"),
            ("services", "" + Icons.TAB_SERVICIOS + "️ Servicios"),
        ]

        for idx, (key, title) in enumerate(cards):
            row, col = divmod(idx, 2)
            card = ctk.CTkFrame(grid, fg_color=COLORS['bg_dark'], corner_radius=8)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            grid.rowconfigure(row, weight=1)

            ctk.CTkLabel(
                card, text=title,
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
                anchor="w",
            ).pack(fill="x", padx=12, pady=(10, 2))

            val_label = ctk.CTkLabel(
                card, text="--",
                font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold"),
                text_color=COLORS['primary'],
                anchor="center",
            )
            val_label.pack(expand=True)
            self._widgets[key] = val_label

        # Fila Pi-hole (ancho completo)
        pihole_card = ctk.CTkFrame(grid, fg_color=COLORS['bg_dark'], corner_radius=8)
        pihole_card.grid(row=3, column=0, columnspan=2, padx=6, pady=6, sticky="nsew")
        grid.rowconfigure(3, weight=1)

        ctk.CTkLabel(
            pihole_card, text="" + Icons.PIHOLE + "️ Pi-hole",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 2))

        pihole_inner = ctk.CTkFrame(pihole_card, fg_color="transparent")
        pihole_inner.pack(fill="x", padx=12, pady=(0, 10))

        for sub_key, sub_label in [
            ("pihole_blocked", "Bloqueadas"),
            ("pihole_pct",     "% Bloqueo"),
            ("pihole_total",   "Total"),
            ("pihole_status",  "Estado"),
        ]:
            col_frame = ctk.CTkFrame(pihole_inner, fg_color="transparent")
            col_frame.pack(side="left", expand=True)

            ctk.CTkLabel(
                col_frame, text=sub_label,
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
            ).pack()

            lbl = ctk.CTkLabel(
                col_frame, text="--",
                font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
                text_color=COLORS['primary'],
            )
            lbl.pack()
            self._widgets[sub_key] = lbl

    # ── Actualización ─────────────────────────────────────────────────────────

    def _update(self):
        """Loop principal de actualización automática de todo el dashboard.

        Llama refresh de cada sección cada 2000ms. Maneja errores silenciosamente
        registrando en logger. Se auto-programa recursivamente con after().
        """
        if not self.winfo_exists():
            return
        if not self._running:
            return
        try:
            self._refresh_system()
            self._refresh_services()
            self._refresh_net()
            self._refresh_pihole()
        except Exception as e:
            logger.error("[OverviewWindow] Error en _update: %s", e)
        self.after(_REFRESH_MS, self._update)

    def _color_for(self, value, warn, crit):
        """Sistema de colores semáforo para métricas basado en umbrales.

        Args:
            value (float): Valor numérico de la métrica.
            warn (float): Límite naranja (advertencia).
            crit (float): Límite rojo (crítico).

        Returns:
            str: Clave de color ('danger', 'warning' o 'primary') de COLORS.
        """
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS.get('warning', '#ffaa00')
        return COLORS['primary']

    def _refresh_system(self):
        """Actualiza tarjetas de sistema desde monitores respectivos.

        CPU/RAM/Temp: De SystemMonitor con color por umbrales config.
        Disco: De DiskMonitor (umbral hardcode 80/90%).
        Muestra '-- (parado)' si monitor detenido.
        """
        if self._system_monitor.is_running():
            sys_stats = self._system_monitor.get_current_stats()
            cpu  = sys_stats.get('cpu', 0)
            ram  = sys_stats.get('ram', 0)
            temp = sys_stats.get('temp', 0)
            self._widgets['cpu'].configure(text=f"{cpu:.0f}%",   text_color=self._color_for(cpu,  CPU_WARN,  CPU_CRIT))
            self._widgets['ram'].configure(text=f"{ram:.0f}%",   text_color=self._color_for(ram,  RAM_WARN,  RAM_CRIT))
            self._widgets['temp'].configure(text=f"{temp:.0f}°C", text_color=self._color_for(temp, TEMP_WARN, TEMP_CRIT))
        else:
            for key in ('cpu', 'ram', 'temp'):
                self._widgets[key].configure(text="-- (parado)", text_color=COLORS['text_dim'])

        if self._disk_monitor.is_running():
            disk_stats = self._disk_monitor.get_current_stats()
            disk = disk_stats.get('disk_usage', 0)
            self._widgets['disk'].configure(text=f"{disk:.0f}%", text_color=self._color_for(disk, 80, 90))
        else:
            self._widgets['disk'].configure(text="-- (parado)", text_color=COLORS['text_dim'])

    def _refresh_services(self):
        """Actualiza tarjeta servicios: fallidos vs total, con color rojo si hay fallos.

        Formato: 'X caídos' (rojo) o 'N OK' (verde).
        """
        if not self._service_monitor.is_running():
            self._widgets['services'].configure(text="-- (parado)", text_color=COLORS['text_dim'])
            return

        stats  = self._service_monitor.get_stats()
        failed = stats.get('failed', 0)
        total  = stats.get('total', 0)
        color  = COLORS['danger'] if failed > 0 else COLORS['primary']
        text   = f"{failed} caídos" if failed > 0 else f"{total} OK"
        self._widgets['services'].configure(text=text, text_color=color)

    def _refresh_net(self):
        """Actualiza velocidades red ↓MB/s ↑MB/s desde NetworkMonitor.

        Formato: ↓X.X ↑Y.Y (azul primary).
        Maneja excepciones mostrando '--'.
        """
        if not self._network_monitor.is_running():
            self._widgets['net'].configure(text="-- (parado)", text_color=COLORS['text_dim'])
            return

        try:
            stats = self._network_monitor.get_current_stats()
            dl    = stats.get('download_mb', 0)
            ul    = stats.get('upload_mb', 0)
            self._widgets['net'].configure(
                text=f"↓{dl:.1f} ↑{ul:.1f}",
                text_color=COLORS['primary']
            )
        except Exception:
            self._widgets['net'].configure(text="--")

    def _refresh_pihole(self):
        """Actualiza 4 métricas Pi-hole: bloqueadas hoy, % bloqueo, total queries, estado.

        Formato con separadores miles. Maneja sin datos o errores.
        """
        if not self._pihole_monitor.is_running():
            for k in ('pihole_blocked', 'pihole_pct', 'pihole_total', 'pihole_status'):
                self._widgets[k].configure(text="-- (parado)", text_color=COLORS['text_dim'])
            return

        try:
            stats = self._pihole_monitor.get_stats()
            if not stats:
                raise ValueError("sin datos")

            blocked = stats.get('blocked_today', 0)
            total   = stats.get('queries_today', 0)
            pct     = stats.get('percent_blocked', 0)
            status  = stats.get('status', 'desconocido').capitalize()

            self._widgets['pihole_blocked'].configure(text=f"{blocked:,}")
            self._widgets['pihole_pct'].configure(text=f"{pct:.1f}%")
            self._widgets['pihole_total'].configure(text=f"{total:,}")
            self._widgets['pihole_status'].configure(text=status)
        except Exception:
            for k in ('pihole_blocked', 'pihole_pct', 'pihole_total', 'pihole_status'):
                self._widgets[k].configure(text="--", text_color=COLORS['text_dim'])
