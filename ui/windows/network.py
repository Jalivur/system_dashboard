"""
Ventana de monitoreo de red
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, NET_INTERFACE)
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import GraphWidget
from core.network_monitor import NetworkMonitor
from utils.system_utils import SystemUtils

_COL_W   = (DSI_WIDTH - 70) // 2
_GRAPH_H = 110


class NetworkWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de red"""

    def __init__(self, parent, network_monitor: NetworkMonitor):
        super().__init__(parent)
        self.network_monitor = network_monitor
        self.widgets = {}
        self.graphs  = {}
        self._interface_update_counter = 0

        self.title("Monitor de Red")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        self._create_ui()
        self._update()

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main, title="MONITOR DE RED", on_close=self.destroy,
            status_text="Detectando interfaz...")

        # Scroll
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

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Grid 2 columnas dentro del inner scrollable
        grid = ctk.CTkFrame(inner, fg_color=COLORS['bg_medium'])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        # Fila 0: DESCARGA | SUBIDA  (con gráfica)
        self._create_traffic_cell(grid, 0, 0, "DESCARGA", "download")
        self._create_traffic_cell(grid, 0, 1, "SUBIDA",   "upload")

        # Fila 1: INTERFACES | SPEEDTEST  (informativas)
        self._create_interfaces_cell(grid, 1, 0)
        self._create_speedtest_cell(grid,  1, 1)

    # ── Celdas ───────────────────────────────────────────────────────────────

    def _create_traffic_cell(self, parent, row, col, title, key):
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

        self.widgets[f"{key}_label"] = lbl
        self.widgets[f"{key}_value"] = val
        self.graphs[key] = graph

    def _create_interfaces_cell(self, parent, row, col):
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        ctk.CTkLabel(cell, text="INTERFACES", text_color=COLORS['success'],
                     font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), anchor="w"
                     ).pack(anchor="w", padx=8, pady=(6, 4))

        self.interfaces_container = ctk.CTkFrame(cell, fg_color="transparent")
        self.interfaces_container.pack(fill="both", expand=True, padx=4, pady=(0, 6))
        self._update_interfaces()

    def _create_speedtest_cell(self, parent, row, col):
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        ctk.CTkLabel(cell, text="SPEEDTEST", text_color=COLORS['primary'],
                     font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), anchor="w"
                     ).pack(anchor="w", padx=8, pady=(6, 4))

        self.speedtest_result = ctk.CTkLabel(
            cell, text="Pulsa 'Test' para\ncomenzar",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            justify="left", wraplength=_COL_W - 20)
        self.speedtest_result.pack(anchor="w", padx=8, pady=(0, 4))

        self.speedtest_btn = make_futuristic_button(
            cell, text="Ejecutar Test", command=self._run_speedtest, width=15, height=5)
        self.speedtest_btn.pack(pady=(0, 8))

    # ── Interfaces ───────────────────────────────────────────────────────────

    def _update_interfaces(self):
        for w in self.interfaces_container.winfo_children():
            w.destroy()

        interfaces = SystemUtils.get_interfaces_ips()
        if not interfaces:
            ctk.CTkLabel(self.interfaces_container, text="Sin interfaces",
                         text_color=COLORS['warning'],
                         font=(FONT_FAMILY, FONT_SIZES['small'])).pack(pady=5)
            return

        for iface, ip in sorted(interfaces.items()):
            if iface.startswith('tun'):
                color, icon = COLORS['success'], "🔒"
            elif iface.startswith(('eth', 'enp')):
                color, icon = COLORS['primary'], "🌐"
            elif iface.startswith(('wlan', 'wlp')):
                color, icon = COLORS['warning'], "\uf0eb"
            else:
                color, icon = COLORS['text'], "•"

            ctk.CTkLabel(self.interfaces_container,
                         text=f"{icon} {iface}: {ip}",
                         text_color=color,
                         font=(FONT_FAMILY, FONT_SIZES['small']),
                         anchor="w", wraplength=_COL_W - 20
                         ).pack(anchor="w", pady=1, padx=4)

    # ── Speedtest ─────────────────────────────────────────────────────────────

    def _run_speedtest(self):
        result = self.network_monitor.get_speedtest_result()
        if result['status'] == 'running':
            return
        self.network_monitor.reset_speedtest()
        self.network_monitor.run_speedtest()
        self.speedtest_btn.configure(state="disabled")
        self.speedtest_result.configure(text="Ejecutando...", text_color=COLORS['warning'])

    def _update_speedtest(self):
        result = self.network_monitor.get_speedtest_result()
        status = result['status']
        if status == 'idle':
            self.speedtest_result.configure(
                text="Pulsa 'Test' para\ncomenzar", text_color=COLORS['text'])
            self.speedtest_btn.configure(state="normal")
        elif status == 'running':
            self.speedtest_result.configure(text="Ejecutando...", text_color=COLORS['warning'])
            self.speedtest_btn.configure(state="disabled")
        elif status == 'done':
            self.speedtest_result.configure(
                text=f"Ping: {result['ping']} ms\n↓ {result['download']:.1f} MB/s\n↑ {result['upload']:.1f} MB/s",
                text_color=COLORS['success'])
            self.speedtest_btn.configure(state="normal")
        elif status == 'timeout':
            self.speedtest_result.configure(text="Timeout", text_color=COLORS['danger'])
            self.speedtest_btn.configure(state="normal")
        elif status == 'error':
            self.speedtest_result.configure(
                text="Error al ejecutar\nel test", text_color=COLORS['danger'])
            self.speedtest_btn.configure(state="normal")

    # ── Update loop ───────────────────────────────────────────────────────────

    def _update(self):
        if not self.winfo_exists():
            return

        stats = self.network_monitor.get_current_stats(NET_INTERFACE)
        self.network_monitor.update_history(stats)
        self.network_monitor.update_dynamic_scale()
        history = self.network_monitor.get_history()

        self._header.status_label.configure(
            text=f"{stats['interface']}  ·  ↓{stats['download_mb']:.2f}  ↑{stats['upload_mb']:.2f} MB/s")

        dl_color = self.network_monitor.net_color(stats['download_mb'])
        self.widgets['download_label'].configure(text_color=dl_color)
        self.widgets['download_value'].configure(
            text=f"{stats['download_mb']:.2f} MB/s", text_color=dl_color)
        self.graphs['download'].update(history['download'], history['dynamic_max'], dl_color)

        ul_color = self.network_monitor.net_color(stats['upload_mb'])
        self.widgets['upload_label'].configure(text_color=ul_color)
        self.widgets['upload_value'].configure(
            text=f"{stats['upload_mb']:.2f} MB/s", text_color=ul_color)
        self.graphs['upload'].update(history['upload'], history['dynamic_max'], ul_color)

        self._update_speedtest()

        self._interface_update_counter += 1
        if self._interface_update_counter >= 5:
            self._update_interfaces()
            self._interface_update_counter = 0

        self.after(UPDATE_MS, self._update)
