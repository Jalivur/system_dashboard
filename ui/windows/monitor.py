"""
Ventana de monitoreo del sistema
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS,
                             CPU_WARN, CPU_CRIT, TEMP_WARN, TEMP_CRIT,
                             RAM_WARN, RAM_CRIT)
from ui.styles import StyleManager, make_window_header
from ui.widgets import GraphWidget
from core.system_monitor import SystemMonitor

_COL_W       = (DSI_WIDTH - 70) // 2
_GRAPH_H_TOP = 90
_GRAPH_H_BOT = 75


class MonitorWindow(ctk.CTkToplevel):
    """Ventana de monitoreo del sistema"""

    def __init__(self, parent, system_monitor: SystemMonitor):
        super().__init__(parent)
        self.system_monitor = system_monitor
        self.widgets = {}
        self.graphs  = {}

        self.title("Monitor del Sistema")
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
            main, title="MONITOR DEL SISTEMA", on_close=self.destroy)

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

        self._create_cell(grid, 0, 0, "CPU %",    "cpu",        "%",    _GRAPH_H_TOP)
        self._create_cell(grid, 0, 1, "RAM %",    "ram",        "%",    _GRAPH_H_TOP)
        self._create_cell(grid, 1, 0, "TEMP °C",  "temp",       "°C",   _GRAPH_H_TOP)
        self._create_cell(grid, 1, 1, "DISCO %",  "disk",       "%",    _GRAPH_H_TOP)
        self._create_cell(grid, 2, 0, "ESCRITURA","disk_write", "MB/s", _GRAPH_H_BOT)
        self._create_cell(grid, 2, 1, "LECTURA",  "disk_read",  "MB/s", _GRAPH_H_BOT)

    def _create_cell(self, parent, row, col, title, key, unit, graph_h):
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        lbl = ctk.CTkLabel(cell, text=title, text_color=COLORS['primary'],
                           font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), anchor="w")
        lbl.pack(anchor="w", padx=8, pady=(6, 0))

        val = ctk.CTkLabel(cell, text=f"0.0 {unit}", text_color=COLORS['primary'],
                           font=(FONT_FAMILY, FONT_SIZES['large'], "bold"), anchor="e")
        val.pack(anchor="e", padx=8, pady=(0, 2))

        graph = GraphWidget(cell, width=_COL_W - 16, height=graph_h)
        graph.pack(padx=4, pady=(0, 6))

        self.widgets[f"{key}_label"] = lbl
        self.widgets[f"{key}_value"] = val
        self.graphs[key] = {'widget': graph, 'max_val': 100 if unit in ('%', '°C') else 50}

    def _update(self):
        if not self.winfo_exists():
            return

        stats   = self.system_monitor.get_current_stats()
        self.system_monitor.update_history(stats)
        history = self.system_monitor.get_history()

        self._update_metric('cpu',  stats['cpu'],        history['cpu'],   "%",   CPU_WARN,  CPU_CRIT)
        self._update_metric('ram',  stats['ram'],        history['ram'],   "%",   RAM_WARN,  RAM_CRIT)
        self._update_metric('temp', stats['temp'],       history['temp'],  "°C",  TEMP_WARN, TEMP_CRIT)
        self._update_metric('disk', stats['disk_usage'], history['disk'],  "%",   60,        80)
        self._update_io('disk_write', stats['disk_write_mb'], history['disk_write'])
        self._update_io('disk_read',  stats['disk_read_mb'],  history['disk_read'])

        self._header.status_label.configure(
            text=f"CPU {stats['cpu']:.0f}%  ·  RAM {stats['ram']:.0f}%  ·  {stats['temp']:.0f}°C")

        self.after(UPDATE_MS, self._update)

    def _update_metric(self, key, value, history, unit, warn, crit):
        color = self.system_monitor.level_color(value, warn, crit)
        self.widgets[f"{key}_value"].configure(text=f"{value:.1f} {unit}", text_color=color)
        self.widgets[f"{key}_label"].configure(text_color=color)
        g = self.graphs[key]
        g['widget'].update(history, g['max_val'], color)

    def _update_io(self, key, value, history):
        color = self.system_monitor.level_color(value, 10, 50)
        self.widgets[f"{key}_value"].configure(text=f"{value:.1f} MB/s", text_color=color)
        self.widgets[f"{key}_label"].configure(text_color=color)
        g = self.graphs[key]
        g['widget'].update(history, g['max_val'], color)
