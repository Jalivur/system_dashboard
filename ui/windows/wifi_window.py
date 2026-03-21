"""
Ventana de monitor de conexión WiFi.
Muestra SSID, señal, bitrate, tráfico TX/RX y sus históricos.
Los widgets se crean una sola vez — solo se actualizan los valores.
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES,
                             DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y)
from core import WiFiMonitor, NetworkMonitor
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import GraphWidget
from utils.logger import get_logger

logger = get_logger(__name__)

_REFRESH_MS = 5_000
_GRAPH_H    = 90
_COL_W      = (DSI_WIDTH - 70) // 2


class WiFiWindow(ctk.CTkToplevel):
    """Ventana de monitor de conexión WiFi."""

    def __init__(self, parent, wifi_monitor):
        super().__init__(parent)
        self._wifi_monitor = wifi_monitor

        self.title("Monitor WiFi")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._refresh_job = None

        # Referencias a widgets actualizables
        self._lbl_ssid:        ctk.CTkLabel = None
        self._lbl_signal_val:  ctk.CTkLabel = None
        self._lbl_signal_bar:  ctk.CTkLabel = None
        self._lbl_quality:     ctk.CTkLabel = None
        self._lbl_noise:       ctk.CTkLabel = None
        self._lbl_bitrate:     ctk.CTkLabel = None
        self._lbl_iface:       ctk.CTkLabel = None
        self._lbl_rx:          ctk.CTkLabel = None
        self._lbl_tx:          ctk.CTkLabel = None
        self._graph_signal:    GraphWidget  = None
        self._graph_rx:        GraphWidget  = None
        self._graph_tx:        GraphWidget  = None
        self._update_label:    ctk.CTkLabel = None
        self._iface_var:       ctk.StringVar = None

        self._create_ui()
        self.after(100, self._update)
        logger.info("[WiFiWindow] Ventana abierta")

    # ── Construcción UI (una sola vez) ────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main, title="MONITOR WIFI",
            on_close=self._on_close,
            status_text="Conectando...",
        )

        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

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
        self._build_connection_card()
        self._build_traffic_card()

        # ── Barra inferior ────────────────────────────────────────────────────
        bar = ctk.CTkFrame(main, fg_color="transparent")
        bar.pack(fill="x", padx=5, pady=(0, 4))

        self._update_label = ctk.CTkLabel(
            bar, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'])
        self._update_label.pack(side="left", padx=8)

        make_futuristic_button(
            bar, text="↺ Actualizar", command=self._force_refresh,
            width=12, height=5, font_size=14
        ).pack(side="right", padx=4)

        # Selector de interfaz
        self._build_iface_selector(self._header)

    def _build_iface_selector(self, parent):
        """Selector de interfaz WiFi en la barra inferior."""
        interfaces = WiFiMonitor.get_available_interfaces()

        # Si solo hay una interfaz (o ninguna) no mostrar el selector
        if len(interfaces) <= 1:
            return

        self._iface_var = ctk.StringVar(
            master=self, value=self._wifi_monitor.interface)

        ctk.CTkLabel(
            parent,
            text="Interfaz:",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(side="left", padx=(0, 4))

        ctk.CTkOptionMenu(
            parent,
            variable=self._iface_var,
            values=interfaces,
            width=100,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            button_color=COLORS['primary'],
            command=self._on_iface_change,
        ).pack(side="left", padx=(0, 4))

    def _on_iface_change(self, iface: str):
        """Cambia la interfaz monitorizada y actualiza el label del header."""
        self._wifi_monitor.set_interface(iface)
        self._lbl_iface.configure(text=iface)
        # Forzar refresco inmediato para reflejar el cambio
        if self._refresh_job:
            self.after_cancel(self._refresh_job)
        self.after(200, self._update)
        logger.info("[WiFiWindow] Interfaz seleccionada: %s", iface)

    def _build_connection_card(self):
        """Tarjeta superior: SSID, señal, calidad, bitrate."""
        card = ctk.CTkFrame(self._inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(6, 4))

        # ── Header de tarjeta ─────────────────────────────────────────────────
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            hdr,
            text="CONEXIÓN",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(side="left")

        self._lbl_iface = ctk.CTkLabel(
            hdr, text=self._wifi_monitor.interface,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="e")
        self._lbl_iface.pack(side="right", padx=4)

        ctk.CTkFrame(
            card, fg_color=COLORS['border'], height=1, corner_radius=0
        ).pack(fill="x", padx=14, pady=(0, 8))

        # ── SSID ──────────────────────────────────────────────────────────────
        row_ssid = ctk.CTkFrame(card, fg_color="transparent")
        row_ssid.pack(fill="x", padx=14, pady=(0, 6))

        ctk.CTkLabel(
            row_ssid, text="SSID",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w", width=110,
        ).pack(side="left")

        self._lbl_ssid = ctk.CTkLabel(
            row_ssid, text="—",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['text'],
            anchor="w")
        self._lbl_ssid.pack(side="left", padx=(4, 0))

        # ── Grid de métricas ──────────────────────────────────────────────────
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=14, pady=(0, 8))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        # Señal (dBm) — col 0
        cell_signal = ctk.CTkFrame(grid, fg_color=COLORS['bg_medium'], corner_radius=6)
        cell_signal.grid(row=0, column=0, padx=(0, 4), pady=4, sticky="nsew")

        ctk.CTkLabel(
            cell_signal, text="SEÑAL",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(anchor="w", padx=8, pady=(6, 0))

        self._lbl_signal_val = ctk.CTkLabel(
            cell_signal, text="— dBm",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['text'],
            anchor="w")
        self._lbl_signal_val.pack(anchor="w", padx=8, pady=(0, 2))

        self._lbl_signal_bar = ctk.CTkLabel(
            cell_signal, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w")
        self._lbl_signal_bar.pack(anchor="w", padx=8, pady=(0, 6))

        # Calidad — col 1
        cell_quality = ctk.CTkFrame(grid, fg_color=COLORS['bg_medium'], corner_radius=6)
        cell_quality.grid(row=0, column=1, padx=(4, 0), pady=4, sticky="nsew")

        ctk.CTkLabel(
            cell_quality, text="CALIDAD",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(anchor="w", padx=8, pady=(6, 0))

        self._lbl_quality = ctk.CTkLabel(
            cell_quality, text="—",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['text'],
            anchor="w")
        self._lbl_quality.pack(anchor="w", padx=8, pady=(0, 2))

        self._lbl_noise = ctk.CTkLabel(
            cell_quality, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w")
        self._lbl_noise.pack(anchor="w", padx=8, pady=(0, 6))

        # Bitrate — fila completa
        row_bitrate = ctk.CTkFrame(card, fg_color="transparent")
        row_bitrate.pack(fill="x", padx=14, pady=(0, 8))

        ctk.CTkLabel(
            row_bitrate, text="BITRATE",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w", width=110,
        ).pack(side="left")

        self._lbl_bitrate = ctk.CTkLabel(
            row_bitrate, text="—",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['text'],
            anchor="w")
        self._lbl_bitrate.pack(side="left", padx=(4, 0))

        # Gráfica histórica de señal
        ctk.CTkLabel(
            card, text="HISTÓRICO SEÑAL (dBm)",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(anchor="w", padx=14, pady=(0, 2))

        self._graph_signal = GraphWidget(
            card, width=DSI_WIDTH - 90, height=_GRAPH_H)
        self._graph_signal.pack(padx=10, pady=(0, 10))

    def _build_traffic_card(self):
        """Tarjeta inferior: tráfico RX/TX con gráficas."""
        card = ctk.CTkFrame(self._inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(4, 6))

        ctk.CTkLabel(
            card,
            text="TRÁFICO",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkFrame(
            card, fg_color=COLORS['border'], height=1, corner_radius=0
        ).pack(fill="x", padx=14, pady=(0, 8))

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=10, pady=(0, 10))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        # RX
        cell_rx = ctk.CTkFrame(grid, fg_color=COLORS['bg_medium'], corner_radius=6)
        cell_rx.grid(row=0, column=0, padx=(0, 4), pady=4, sticky="nsew")

        ctk.CTkLabel(
            cell_rx, text="DESCARGA",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(anchor="w", padx=8, pady=(6, 0))

        self._lbl_rx = ctk.CTkLabel(
            cell_rx, text="0.000 MB/s",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['primary'],
            anchor="w")
        self._lbl_rx.pack(anchor="w", padx=8, pady=(0, 4))

        self._graph_rx = GraphWidget(cell_rx, width=_COL_W - 16, height=_GRAPH_H)
        self._graph_rx.pack(padx=4, pady=(0, 6))

        # TX
        cell_tx = ctk.CTkFrame(grid, fg_color=COLORS['bg_medium'], corner_radius=6)
        cell_tx.grid(row=0, column=1, padx=(4, 0), pady=4, sticky="nsew")

        ctk.CTkLabel(
            cell_tx, text="SUBIDA",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(anchor="w", padx=8, pady=(6, 0))

        self._lbl_tx = ctk.CTkLabel(
            cell_tx, text="0.000 MB/s",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['primary'],
            anchor="w")
        self._lbl_tx.pack(anchor="w", padx=8, pady=(0, 4))

        self._graph_tx = GraphWidget(cell_tx, width=_COL_W - 16, height=_GRAPH_H)
        self._graph_tx.pack(padx=4, pady=(0, 6))

    # ── Actualización de valores (sin recrear widgets) ────────────────────────

    def _update(self):
        if not self.winfo_exists():
            return
        if not self._wifi_monitor.is_running():
            StyleManager.show_service_stopped_banner(self._inner, "Wifi Monitor")
            return
        stats = self._wifi_monitor.get_stats()
        info  = stats["info"]

        self._refresh_connection(info)
        self._refresh_traffic(stats)

        # Header
        if info.get("connected"):
            dbm_str = f"{info['signal_dbm']} dBm" if info['signal_dbm'] is not None else ""
            self._header.status_label.configure(
                text=f"{info['ssid']}  ·  {dbm_str}")
        else:
            self._header.status_label.configure(
                text=f"Sin conexión — {self._wifi_monitor.interface}",
                text_color=COLORS['warning'])

        ts = stats["last_update"]
        self._update_label.configure(
            text=f"Actualizado: {ts}" if ts else "")

        self._refresh_job = self.after(_REFRESH_MS, self._update)

    def _refresh_connection(self, info: dict):
        """Actualiza widgets de conexión sin recrearlos."""

        # Interfaz (puede haber cambiado)
        self._lbl_iface.configure(text=self._wifi_monitor.interface)

        # SSID
        self._lbl_ssid.configure(
            text=info.get("ssid") or "Sin conexión",
            text_color=COLORS['text'] if info.get("connected") else COLORS['warning'])

        # Señal
        dbm   = info.get("signal_dbm")
        color = WiFiMonitor.signal_color(dbm, COLORS)
        pct   = WiFiMonitor.signal_quality_pct(dbm)

        self._lbl_signal_val.configure(
            text=f"{dbm} dBm" if dbm is not None else "— dBm",
            text_color=color)

        bars = self._signal_bars(pct)
        self._lbl_signal_bar.configure(text=f"{bars}  {pct}%", text_color=color)

        # Calidad link
        lq     = info.get("link_quality")
        lq_max = info.get("link_quality_max")
        if lq is not None and lq_max:
            self._lbl_quality.configure(text=f"{lq}/{lq_max}", text_color=color)
        else:
            self._lbl_quality.configure(text="—", text_color=COLORS['text_dim'])

        # Ruido
        noise = info.get("noise_dbm")
        self._lbl_noise.configure(
            text=f"Ruido: {noise} dBm" if noise is not None else "",
            text_color=COLORS['text_dim'])

        # Bitrate
        self._lbl_bitrate.configure(
            text=info.get("bitrate") or "—",
            text_color=COLORS['text'])

        # Gráfica señal
        signal_hist = self._wifi_monitor.get_signal_history()
        if signal_hist:
            normalized = [max(0.0, min(100.0, 2.0 * (v + 100))) for v in signal_hist]
            self._graph_signal.update(normalized, 100.0, color)

    def _refresh_traffic(self, stats: dict):
        """Actualiza widgets de tráfico sin recrearlos."""
        rx = stats["rx_mbps"]
        tx = stats["tx_mbps"]

        rx_color = NetworkMonitor.net_color(rx)
        tx_color = NetworkMonitor.net_color(tx)

        self._lbl_rx.configure(text=f"{rx:.3f} MB/s", text_color=rx_color)
        self._lbl_tx.configure(text=f"{tx:.3f} MB/s", text_color=tx_color)

        rx_hist = stats["rx_hist"]
        tx_hist = stats["tx_hist"]

        peak  = max(max(rx_hist, default=0.0), max(tx_hist, default=0.0), 0.5)
        scale = peak * 1.2

        self._graph_rx.update(rx_hist, scale, rx_color)
        self._graph_tx.update(tx_hist, scale, tx_color)

    @staticmethod
    def _signal_bars(pct: int) -> str:
        """Devuelve representación visual de barras de señal."""
        if pct >= 80:
            return "▂▄▆█"
        if pct >= 60:
            return "▂▄▆░"
        if pct >= 40:
            return "▂▄░░"
        if pct >= 20:
            return "▂░░░"
        return "░░░░"

    def _force_refresh(self):
        if self._refresh_job:
            self.after_cancel(self._refresh_job)
        self._update()

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _on_close(self):
        if self._refresh_job:
            self.after_cancel(self._refresh_job)
        logger.info("[WiFiWindow] Ventana cerrada")
        self.destroy()
