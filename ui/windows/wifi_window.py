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
        """Inicializa la ventana de monitor WiFi.
        
        Args:
            parent: Ventana padre (principal del dashboard).
            wifi_monitor (WiFiMonitor): Instancia del monitor WiFi para obtener datos en tiempo real.
        
        Configuración inicial:
        - Título, colores, geometría fija para pantalla DSI.
        - No redimensionable, modal sobre padre, foco automático.
        - Inicializa _refresh_job y todas referencias de widgets (None).
        - Crea UI estática con _create_ui().
        - Agenda primer _update() en 100ms.
        - Registra apertura en logger.
        """
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
        """Crea toda la interfaz de usuario de la ventana WiFi de forma estática (una sola vez).
        
        Estructura completa:
        - Frame principal y header personalizable con título y estado dinámico.
        - Contenedor scrollable con canvas para contenido extensible.
        - Tarjetas dedicadas para estado de conexión y tráfico de red.
        - Gráficas históricas (GraphWidget) para evolución de señal, RX y TX.
        - Barra inferior con timestamp de última actualización y botón de refresco manual.
        - Selector de interfaz (dropdown) si hay múltiples adaptadores WiFi disponibles.
        
        Inicializa todas las referencias a widgets actualizables como atributos de instancia
        (_lbl_ssid, _graph_rx, etc.) para su posterior actualización sin recrearlos.
        """
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
        """Construye el selector (dropdown) de interfaz WiFi en el header de la ventana.
        
        Args:
            parent: Frame padre donde insertar el selector (header).
        
        Solo se muestra si hay múltiples interfaces WiFi disponibles (WiFiMonitor.get_available_interfaces()).
        Crea label 'Interfaz:', CTkStringVar para valor actual, y CTkOptionMenu con lista de interfaces.
        Al cambiar selección, llama a self._on_iface_change().
        """
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
        """Callback ejecutado al seleccionar nueva interfaz WiFi desde el dropdown.
        
        Args:
            iface (str): Nombre de la nueva interfaz seleccionada (ej: 'wlan0').
        
        Acciones:
        - Cambia la interfaz activa en self._wifi_monitor.
        - Actualiza el label _lbl_iface con el nuevo nombre.
        - Cancela refresco pendiente y agenda _update() en 200ms para reflejar cambios.
        - Registra cambio en logger.
        """
        self._wifi_monitor.set_interface(iface)
        self._lbl_iface.configure(text=iface)
        # Forzar refresco inmediato para reflejar el cambio
        if self._refresh_job:
            self.after_cancel(self._refresh_job)
        self.after(200, self._update)
        logger.info("[WiFiWindow] Interfaz seleccionada: %s", iface)

    def _build_connection_card(self):
        """Construye la tarjeta superior de estado de conexión WiFi.
        
        Incluye:
        - Header con título 'CONEXIÓN' y label de interfaz actual (_lbl_iface).
        - Fila SSID con label principal.
        - Grid 1x2 para métricas: señal (dBm + barra + %) y calidad link (LQ/max).
        - Fila bitrate con valor actual.
        - Gráfica histórica de señal (_graph_signal, toda el ancho).
        
        Todos los labels métricos (_lbl_signal_val, etc.) referenciados para _update().
        Usa colores dinámicos basados en calidad de señal (WiFiMonitor.signal_color()).
        """
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
        """Construye la tarjeta inferior de tráfico de red (RX/TX).
        
        Estructura:
        - Header con título 'TRÁFICO'.
        - Grid 1x2 para celdas descarga (RX) y subida (TX).
        - Cada celda contiene: label métrica, valor actual (_lbl_rx/_lbl_tx),
          gráfica histórica dedicada (_graph_rx/_graph_tx).
        
        Ancho de gráficas ajustado a _COL_W. Colores dinámicos via NetworkMonitor.net_color().
        Referencias inicializadas para actualización en _refresh_traffic().
        """
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
        """Actualiza todos los valores de widgets cada _REFRESH_MS (5s).
        
        Proceso:
        1. Verifica existencia de ventana.
        2. Si monitor no corre, muestra banner 'stopped'.
        3. Obtiene stats de WiFiMonitor.get_stats().
        4. Actualiza conexión (_refresh_connection), tráfico (_refresh_traffic).
        5. Actualiza header status con SSID + dBm o 'Sin conexión'.
        6. Muestra timestamp última actualización.
        7. Agenda próximo _update().
        
        Centraliza lógica de refresco periódico.
        """
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
        """Actualiza solo los valores de la tarjeta de conexión (SSID, señal, calidad, bitrate, gráfica).
        
        Args:
            info (dict): Datos de conexión de WiFiMonitor ('ssid', 'signal_dbm', etc.).
        
        Actualiza:
        - SSID con color warning si desconectado.
        - Señal: valor dBm, barras visuales (self._signal_bars), % con color dinámico.
        - Calidad link: LQ/max.
        - Ruido dBm.
        - Bitrate.
        - Gráfica señal: normaliza historia [-100..0] -> [0..100], color dinámico.
        """
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
        """Actualiza valores de tráfico de red (RX/TX) y gráficas históricas.
        
        Args:
            stats (dict): Estadísticas completas de WiFiMonitor.get_stats()
                          ('rx_mbps', 'tx_mbps', 'rx_hist', 'tx_hist', etc.).
        
        Actualiza:
        - Velocidades actuales _lbl_rx/_lbl_tx con 3 decimales y colores (NetworkMonitor.net_color).
        - Historia RX/TX: escala a peak*1.2, colores dinámicos.
        """
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
        """Genera representación visual Unicode de barras de intensidad de señal WiFi.
        
        Args:
            pct (int): Porcentaje de calidad de señal (0-100).
        
        Returns:
            str: 4 caracteres Unicode:
                 - ▂▄▆█ (≥80%)
                 - ▂▄▆░ (≥60%)
                 - ▂▄░░ (≥40%)
                 - ▂░░░ (≥20%)
                 - ░░░░ (<20%)
        
        Usado en _lbl_signal_bar para display intuitivo.
        """
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
        """Refresca inmediatamente todos los datos cancelando job pendiente.
        
        Callback del botón '↺ Actualizar' en barra inferior.
        Cancela _refresh_job actual y llama _update() directo.
        """
        if self._refresh_job:
            self.after_cancel(self._refresh_job)
        self._update()

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _on_close(self):
        """Maneja el cierre de la ventana limpiando recursos.
        
        Callback del botón cerrar en header.
        - Cancela job de refresco pendiente.
        - Registra cierre en logger.
        - Destruye ventana.
        """
        if self._refresh_job:
            self.after_cancel(self._refresh_job)
        logger.info("[WiFiWindow] Ventana cerrada")
        self.destroy()
