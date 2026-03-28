"""
Ventana de monitoreo de red
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, NET_INTERFACE, Icons)
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import GraphWidget
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)

_COL_W   = (DSI_WIDTH - 70) // 2
_GRAPH_H = 110


class NetworkWindow(ctk.CTkToplevel):
    """
    Ventana emergente para monitorear el estado de la red.

    Args:
        parent: Widget padre que crea esta ventana.
        network_monitor: Instancia del monitor de red para obtener estadísticas.

    Raises:
        Ninguna excepción específica.

    Returns:
        Ningún valor de retorno.
    """

    def __init__(self, parent, network_monitor):
        """
        Inicializa la ventana de monitoreo de red.

        Args:
            parent: Widget padre (CTkToplevel).
            network_monitor: Instancia del monitor de red para obtener estadísticas.

        Returns:
            None

        Raises:
            None
        """
        super().__init__(parent)
        self._network_monitor = network_monitor
        self._widgets  = {}
        self._graphs   = {}
        self._interface_update_counter = 0
        self._banner_shown = False

        self.title("Monitor de Red")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        self._create_ui()
        self._update()
        logger.info("[NetworkWindow] Ventana Abierta")


    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        """
        Crea la estructura principal de la interfaz de usuario de la ventana de red.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main, title=f"{Icons.MONITOR_RED} MONITOR DE RED", on_close=self.destroy,
            status_text="Detectando interfaz...")

        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
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
        canvas.create_window((0, 0), window=self._inner, anchor="nw", width=DSI_WIDTH - 50)
        self._inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self._build_content(self._inner)

    def _build_content(self, inner):
        """
        Construye el contenido scrollable de la ventana de red.

        Args:
            inner: El contenedor interno donde se construirá el contenido.

        Returns:
            None

        Raises:
            None
        """
        grid = ctk.CTkFrame(inner, fg_color=COLORS['bg_medium'])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self._create_traffic_cell(grid, 0, 0, f"{Icons.DOWN} DESCARGA", "download")
        self._create_traffic_cell(grid, 0, 1, f"{Icons.UP} SUBIDA",   "upload")
        self._create_interfaces_cell(grid, 1, 0)
        self._create_speedtest_cell(grid,  1, 1)

    # ── Celdas ───────────────────────────────────────────────────────────────

    def _create_traffic_cell(self, parent, row, col, title, key):
        """
        Crea una celda de tráfico de red con gráfica para mostrar datos de descarga o subida.

        Args:
            parent: Frame contenedor de la celda.
            row: Número de fila en el grid.
            col: Número de columna en el grid.
            title: Título de la celda.
            key: Identificador de la celda ('download' o 'upload').

        Returns:
            None

        Raises:
            None
        """
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        lbl = ctk.CTkLabel(cell, text=title, text_color=COLORS['primary'],
                           font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), anchor="w")
        lbl.pack(anchor="w", padx=8, pady=(6, 0))

        val = ctk.CTkLabel(cell, text="0.00 MB/s", text_color=COLORS['primary'],
                           font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"), anchor="e")
        val.pack(anchor="e", padx=8, pady=(0, 2))

        graph = GraphWidget(cell, width=_COL_W - 16, height=_GRAPH_H)
        graph.pack(padx=4, pady=(0, 6))

        self._widgets[f"{key}_label"] = lbl
        self._widgets[f"{key}_value"] = val
        self._graphs[key] = graph

    def _create_interfaces_cell(self, parent, row, col):
        """
        Crea la celda que muestra interfaces de red activas e IPs.

        Args:
            parent: El padre de la celda.
            row (int): La fila de la celda.
            col (int): La columna de la celda.

        Returns:
            None

        Raises:
            None
        """
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        ctk.CTkLabel(cell, text="INTERFACES", text_color=COLORS['success'],
                     font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), anchor="w"
                     ).pack(anchor="w", padx=8, pady=(6, 4))

        self._interfaces_container = ctk.CTkFrame(cell, fg_color="transparent")
        self._interfaces_container.pack(fill="both", expand=True, padx=4, pady=(0, 6))
        self._update_interfaces()

    def _create_speedtest_cell(self, parent, row, col):
        """
        Crea la celda para ejecutar y mostrar resultados de speedtest.

        Args:
            parent: El padre de la celda.
            row: La fila donde se ubicará la celda.
            col: La columna donde se ubicará la celda.

        Returns:
            None

        Raises:
            None
        """
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        ctk.CTkLabel(cell, text="SPEEDTEST", text_color=COLORS['primary'],
                     font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), anchor="w"
                     ).pack(anchor="w", padx=8, pady=(6, 4))

        self._speedtest_result = ctk.CTkLabel(
            cell, text=f"{Icons.TAP} Pulsa {Icons.PLAY} para\ncomenzar",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            justify="left", wraplength=_COL_W - 20)
        self._speedtest_result.pack(anchor="w", padx=8, pady=(0, 4))

        self._speedtest_btn = make_futuristic_button(
            cell, text=f"{Icons.PLAY} Ejecutar Test", command=self._run_speedtest, width=15, height=5)
        self._speedtest_btn.pack(pady=(0, 8))

    # ── Interfaces ───────────────────────────────────────────────────────────

    def _update_interfaces(self):
        """
        Actualiza la lista de interfaces de red con sus direcciones IP.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        for w in self._interfaces_container.winfo_children():
            w.destroy()

        interfaces = SystemUtils.get_interfaces_ips()
        if not interfaces:
            ctk.CTkLabel(self._interfaces_container, text="Sin interfaces",
                         text_color=COLORS['warning'],
                         font=(FONT_FAMILY, FONT_SIZES['small'])).pack(pady=5)
            return

        for iface, ip in sorted(interfaces.items()):
            if iface.startswith('tun'):
                color, icon = COLORS['success'], Icons.VPN
            elif iface.startswith(('eth', 'enp')):
                color, icon = COLORS['primary'], Icons.ETHERNET
            elif iface.startswith(('wlan', 'wlp')):
                color, icon = COLORS['warning'], Icons.WIFI
            else:
                color, icon = COLORS['text'], "•"

            ctk.CTkLabel(self._interfaces_container,
                         text=f"{icon} {iface}: {ip}",
                         text_color=color,
                         font=(FONT_FAMILY, FONT_SIZES['small']),
                         anchor="w", wraplength=_COL_W - 20
                         ).pack(anchor="w", pady=1, padx=4)

    # ── Speedtest ─────────────────────────────────────────────────────────────

    def _run_speedtest(self):
        """
        Inicia la ejecución de un test de velocidad de red.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        result = self._network_monitor.get_speedtest_result()
        if result['status'] == 'running':
            return
        self._network_monitor.reset_speedtest()
        self._network_monitor.run_speedtest()
        self._speedtest_btn.configure(state="disabled")
        self._speedtest_result.configure(text="Ejecutando...", text_color=COLORS['warning'])

    def _update_speedtest(self):
        """
        Actualiza la visualización del resultado del speedtest según su estado.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        result = self._network_monitor.get_speedtest_result()
        status = result['status']
        if status == 'idle':
            self._speedtest_result.configure(
                text=f"{Icons.TAP} Pulsa {Icons.PLAY} para\ncomenzar", text_color=COLORS['text'])
            self._speedtest_btn.configure(state="normal")
        elif status == 'running':
            self._speedtest_result.configure(text="Ejecutando...", text_color=COLORS['warning'])
            self._speedtest_btn.configure(state="disabled")
        elif status == 'done':
            self._speedtest_result.configure(
                text=f"Ping: {result['ping']} ms\n↓ {result['download']:.1f} MB/s\n↑ {result['upload']:.1f} MB/s",
                text_color=COLORS['success'])
            self._speedtest_btn.configure(state="normal")
        elif status == 'timeout':
            self._speedtest_result.configure(text="Timeout", text_color=COLORS['danger'])
            self._speedtest_btn.configure(state="normal")
        elif status == 'error':
            self._speedtest_result.configure(
                text="Error al ejecutar\nel test", text_color=COLORS['danger'])
            self._speedtest_btn.configure(state="normal")

    # ── Update loop ───────────────────────────────────────────────────────────

    def _update(self):
        """
        Actualiza la interfaz de usuario de la ventana de red con datos del monitor de red.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if not self.winfo_exists():
            return

        if not self._network_monitor.is_running():
            if not self._banner_shown:
                StyleManager.show_service_stopped_banner(self._inner, f"{Icons.MONITOR_RED} Monitor de Red")
                self._banner_shown = True
            self.after(UPDATE_MS, self._update)
            return

        if self._banner_shown:
            self._banner_shown = False
            self._widgets.clear()
            self._graphs.clear()
            for w in self._inner.winfo_children():
                w.destroy()
            self._build_content(self._inner)

        stats = self._network_monitor.get_current_stats(NET_INTERFACE)
        self._network_monitor.update_history(stats)
        self._network_monitor.update_dynamic_scale()
        history = self._network_monitor.get_history()

        self._header.status_label.configure(
            text=f"{stats['interface']}  · {Icons.DOWN} {stats['download_mb']:.2f} {Icons.UP} {stats['upload_mb']:.2f} MB/s")

        dl_color = self._network_monitor.net_color(stats['download_mb'])
        self._widgets['download_label'].configure(text_color=dl_color)
        self._widgets['download_value'].configure(
            text=f"{stats['download_mb']:.2f} MB/s", text_color=dl_color)
        self._graphs['download'].update(history['download'], history['dynamic_max'], dl_color)

        ul_color = self._network_monitor.net_color(stats['upload_mb'])
        self._widgets['upload_label'].configure(text_color=ul_color)
        self._widgets['upload_value'].configure(
            text=f"{stats['upload_mb']:.2f} MB/s", text_color=ul_color)
        self._graphs['upload'].update(history['upload'], history['dynamic_max'], ul_color)

        self._update_speedtest()

        self._interface_update_counter += 1
        if self._interface_update_counter >= 5:
            self._update_interfaces()
            self._interface_update_counter = 0

        self.after(UPDATE_MS, self._update)
