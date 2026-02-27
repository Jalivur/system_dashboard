"""
Ventana de resumen general del sistema.
Muestra todas las métricas críticas en un solo vistazo.
Pensada para usarse como pantalla de reposo en la DSI.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
)
from ui.styles import make_window_header, make_futuristic_button
from utils.logger import get_logger

logger = get_logger(__name__)

# Intervalo de refresco en ms
_REFRESH_MS = 2000


class OverviewWindow(ctk.CTkToplevel):
    """Ventana de resumen — métricas críticas en un vistazo."""

    def __init__(self, parent, system_monitor, service_monitor,
                 pihole_monitor, network_monitor, disk_monitor):
        super().__init__(parent)
        self.system_monitor  = system_monitor
        self.service_monitor = service_monitor
        self.pihole_monitor  = pihole_monitor
        self.network_monitor = network_monitor
        self.disk_monitor    = disk_monitor

        self.title("Resumen del Sistema")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._widgets = {}   # clave -> CTkLabel de valor
        self._running = True

        self._create_ui()
        self._update()
        logger.info("[OverviewWindow] Ventana abierta")

    def destroy(self):
        self._running = False
        super().destroy()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="RESUMEN DEL SISTEMA", on_close=self.destroy)

        # Grid 2x3 de tarjetas
        grid = ctk.CTkFrame(main, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=5, pady=5)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        cards = [
            ("cpu",      "🔥 CPU",         "row=0,col=0"),
            ("ram",      "💾 RAM",         "row=0,col=1"),
            ("temp",     "🌡️ Temperatura", "row=1,col=0"),
            ("disk",     "💿 Disco",       "row=1,col=1"),
            ("net",      "🌐 Red",         "row=2,col=0"),
            ("services", "⚙️ Servicios",   "row=2,col=1"),
        ]

        for key, title, pos in cards:
            # Parsear posición
            parts = {p.split("=")[0]: int(p.split("=")[1]) for p in pos.split(",")}
            row, col = parts["row"], parts["col"]

            card = ctk.CTkFrame(
                grid,
                fg_color=COLORS['bg_dark'],
                corner_radius=8,
            )
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            grid.rowconfigure(row, weight=1)

            ctk.CTkLabel(
                card,
                text=title,
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
                anchor="w",
            ).pack(fill="x", padx=12, pady=(10, 2))

            val_label = ctk.CTkLabel(
                card,
                text="--",
                font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold"),
                text_color=COLORS['primary'],
                anchor="center",
            )
            val_label.pack(expand=True)
            self._widgets[key] = val_label

        # Fila extra: Pi-hole (ancho completo)
        pihole_card = ctk.CTkFrame(
            grid,
            fg_color=COLORS['bg_dark'],
            corner_radius=8,
        )
        pihole_card.grid(row=3, column=0, columnspan=2, padx=6, pady=6, sticky="nsew")
        grid.rowconfigure(3, weight=1)

        ctk.CTkLabel(
            pihole_card,
            text="🕳️ Pi-hole",
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
                col_frame,
                text=sub_label,
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
            ).pack()

            lbl = ctk.CTkLabel(
                col_frame,
                text="--",
                font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
                text_color=COLORS['primary'],
            )
            lbl.pack()
            self._widgets[sub_key] = lbl

    # ── Actualización ─────────────────────────────────────────────────────────

    def _update(self):
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
        """Devuelve el color según umbrales."""
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS.get('warning', '#ffaa00')
        return COLORS['primary']

    def _refresh_system(self):
        stats = self.system_monitor.get_current_stats()

        cpu  = stats.get('cpu', 0)
        ram  = stats.get('ram', 0)
        temp = stats.get('temp', 0)
        disk = stats.get('disk_usage', 0)

        self._widgets['cpu'].configure(
            text=f"{cpu:.0f}%",
            text_color=self._color_for(cpu, 75, 90)
        )
        self._widgets['ram'].configure(
            text=f"{ram:.0f}%",
            text_color=self._color_for(ram, 75, 90)
        )
        self._widgets['temp'].configure(
            text=f"{temp:.0f}°C",
            text_color=self._color_for(temp, 60, 70)
        )
        self._widgets['disk'].configure(
            text=f"{disk:.0f}%",
            text_color=self._color_for(disk, 80, 90)
        )

    def _refresh_services(self):
        stats  = self.service_monitor.get_stats()
        failed = stats.get('failed', 0)
        total  = stats.get('total', 0)
        color  = COLORS['danger'] if failed > 0 else COLORS['primary']
        text   = f"{failed} caídos" if failed > 0 else f"{total} OK"
        self._widgets['services'].configure(text=text, text_color=color)

    def _refresh_net(self):
        try:
            stats = self.network_monitor.get_current_stats()
            dl = stats.get('download_mb', 0)
            ul = stats.get('upload_mb', 0)
            iface = stats.get('interface', '')
            self._widgets['net'].configure(
                text=f"↓{dl:.1f} ↑{ul:.1f}",
                text_color=COLORS['primary']
            )
        except Exception:
            self._widgets['net'].configure(text="--")

    def _refresh_pihole(self):
        try:
            stats = self.pihole_monitor.get_stats()
            if not stats:
                raise ValueError("sin datos")
            blocked = stats.get('blocked_today', 0)
            total   = stats.get('queries_today', 0)
            pct     = stats.get('percent_blocked', 0)
            status  = stats.get('status', 'desconocido').capitalize()
            self._widgets['pihole_blocked'].configure(text=f"{blocked:,}")
            self._widgets['pihole_pct'].configure(text=f"{pct:.1f}%")
            self._widgets['pihole_total'].configure(text=f"{total:,}")
            self._widgets['pihole_status'].configure(text=f"{status}")
        except Exception:
            for k in ('pihole_blocked', 'pihole_pct', 'pihole_total', 'pihole_status'):
                self._widgets[k].configure(text="--", text_color=COLORS['text_dim'])