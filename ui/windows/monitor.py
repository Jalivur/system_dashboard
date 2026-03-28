"""
Ventana de monitoreo del sistema
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS,
                             CPU_WARN, CPU_CRIT, TEMP_WARN, TEMP_CRIT,
                             RAM_WARN, RAM_CRIT, Icons)
from ui.styles import StyleManager, make_window_header
from ui.widgets import GraphWidget
from core.system_monitor import SystemMonitor
from utils.logger import get_logger

logger = get_logger(__name__)

_COL_W       = (DSI_WIDTH - 70) // 2
_GRAPH_H_TOP = 90


class MonitorWindow(ctk.CTkToplevel):
    """
    Ventana de monitoreo del sistema con información de métricas y estado.

    Args:
        parent: Ventana padre (CTkToplevel).
        system_monitor: Instancia de SystemMonitor para métricas CPU/RAM/TEMP.
        hardware_monitor: Instancia opcional de monitor hardware FNK0100K (fase1).

    Returns:
        None

    Raises:
        None
    """

    def __init__(self, parent, system_monitor: SystemMonitor, hardware_monitor=None):
        """
        Inicializa la ventana de monitoreo del sistema.

        Configura la ventana toplevel con geometría fija para DSI, título, colores y
        comportamientos. Registra monitores de sistema/hardware y crea la interfaz de usuario.

        Args:
            parent: Ventana padre.
            system_monitor: Instancia de SystemMonitor para métricas CPU/RAM/TEMP.
            hardware_monitor: Instancia opcional de monitor hardware.

        """

        super().__init__(parent)
        self._system_monitor   = system_monitor
        self._hardware_monitor = hardware_monitor
        self._widgets = {}
        self._graphs  = {}

        self.title("Monitor del Sistema")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        self._create_ui()
        self._update()
        logger.info("[MonitorWindow] Ventana Abierta")


    def _create_ui(self):
        """
        Crea la interfaz de usuario completa de la ventana de monitoreo.

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
            main, title="MONITOR DEL SISTEMA", on_close=self.destroy)

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
        self._content_frame = inner

        grid = ctk.CTkFrame(inner, fg_color=COLORS['bg_medium'])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self._create_cell(grid, 0, 0, "CPU %",   "cpu",  "%",  _GRAPH_H_TOP)
        self._create_cell(grid, 0, 1, "RAM %",   "ram",  "%",  _GRAPH_H_TOP)
        self._create_cell(grid, 1, 0, "TEMP °C", "temp", "°C", _GRAPH_H_TOP)

        # ── Tarjeta hardware FNK0100K (temperatura chasis + fan duty real) ───
        # Solo se crea si se pasó _hardware_monitor (fase1 activo)
        if self._hardware_monitor:
            chassis_card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
            chassis_card.pack(fill="x", padx=5, pady=(0, 5))

            ctk.CTkLabel(
                chassis_card,
                text="" + Icons.THERMOMETER + "️ Hardware FNK0100K " + Icons.FAN_CONTROL + " (via fase1.py)"  ,
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                text_color=COLORS['primary'],
                anchor="w",
            ).pack(anchor="w", padx=8, pady=(6, 4))

            hw_row = ctk.CTkFrame(chassis_card, fg_color="transparent")
            hw_row.pack(fill="x", padx=8, pady=(0, 10))
            hw_row.grid_columnconfigure(0, weight=1)
            hw_row.grid_columnconfigure(1, weight=1)
            hw_row.grid_columnconfigure(2, weight=1)

            for col_idx, (key, title, unit) in enumerate([
                ("chassis_temp", "Temp. chasis", "°C"),
                ("fan0_pct",     "Fan 1 (real)", "%"),
                ("fan1_pct",     "Fan 2 (real)", "%"),
            ]):
                col_frame = ctk.CTkFrame(hw_row, fg_color="transparent")
                col_frame.grid(row=0, column=col_idx, padx=4, sticky="nsew")

                ctk.CTkLabel(
                    col_frame, text=title,
                    font=(FONT_FAMILY, FONT_SIZES['small']),
                    text_color=COLORS['text_dim'],
                    anchor="center",
                ).pack()

                lbl = ctk.CTkLabel(
                    col_frame,
                    text=f"-- {unit}",
                    font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
                    text_color=COLORS['primary'],
                    anchor="center",
                )
                lbl.pack()
                self._widgets[f"hw_{key}_value"] = (lbl, unit)

    def _create_cell(self, parent, row, col, title, key, unit, graph_h):
        """
        Crea una celda individual para mostrar y graficar una métrica del sistema.

        Args:
            parent: Frame contenedor (grid).
            row, col: Posición en grid.
            title: Título de la métrica (ej: 'CPU %').
            key: Identificador interno ('cpu', 'ram', etc.).
            unit: Unidad de medida ('%', '°C').
            graph_h: Altura del gráfico en píxeles.

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

        val = ctk.CTkLabel(cell, text=f"0.0 {unit}", text_color=COLORS['primary'],
                           font=(FONT_FAMILY, FONT_SIZES['large'], "bold"), anchor="e")
        val.pack(anchor="e", padx=8, pady=(0, 2))

        graph = GraphWidget(cell, width=_COL_W - 16, height=graph_h)
        graph.pack(padx=4, pady=(0, 6))

        self._widgets[f"{key}_label"] = lbl
        self._widgets[f"{key}_value"] = val
        self._graphs[key] = {'widget': graph, 'max_val': 100 if unit in ('%', '°C') else 50}

    def _update(self):
        """
        Actualiza todas las métricas del monitoreo en ciclo recursivo.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """

        if not self.winfo_exists():
            return

        if not self._system_monitor.is_running():
            StyleManager.show_service_stopped_banner(self._content_frame, "System Monitor")
            self.after(UPDATE_MS, self._update)
            return

        stats   = self._system_monitor.get_current_stats()
        self._system_monitor.update_history(stats)
        history = self._system_monitor.get_history()

        self._update_metric('cpu',  stats['cpu'],  history['cpu'],  "%",  CPU_WARN,  CPU_CRIT)
        self._update_metric('ram',  stats['ram'],  history['ram'],  "%",  RAM_WARN,  RAM_CRIT)
        self._update_metric('temp', stats['temp'], history['temp'], "°C", TEMP_WARN, TEMP_CRIT)

        self._header.status_label.configure(
            text=f"CPU {stats['cpu']:.0f}%  ·  RAM {stats['ram']:.0f}%  ·  {stats['temp']:.0f}°C")

        # ── Hardware FNK0100K ──────────────────────────────────────────────────
        if self._hardware_monitor:
            if self._hardware_monitor.is_available():
                hw = self._hardware_monitor.get_stats()
                for key, warn, crit in [
                    ("chassis_temp", 35, 45),
                    ("fan0_pct",     80, 95),
                    ("fan1_pct",     80, 95),
                ]:
                    entry = self._widgets.get(f"hw_{key}_value")
                    if entry is None:
                        continue
                    lbl, unit = entry
                    val = hw.get(key)
                    if val is None:
                        lbl.configure(text=f"-- {unit}", text_color=COLORS['text_dim'])
                    else:
                        color = self._system_monitor.level_color(val, warn, crit)
                        lbl.configure(text=f"{val:.0f} {unit}", text_color=color)
            else:
                for key in ("chassis_temp", "fan0_pct", "fan1_pct"):
                    entry = self._widgets.get(f"hw_{key}_value")
                    if entry:
                        entry[0].configure(text="fase1 inactivo", text_color=COLORS['text_dim'])

        self.after(UPDATE_MS, self._update)

    def _update_metric(self, key, value, history, unit, warn, crit):
        """
        Actualiza visualmente una métrica específica según su valor actual.

        Determina color según umbrales de advertencia y crítico. Actualiza label de valor/unidad 
        y título con el color, y refresca el gráfico con historia y máximo configurado.

        Args:
            key (str): Identificador de métrica.
            value (float): Valor numérico actual.
            history (list): Lista histórica de valores para el gráfico.
            unit (str): Unidad de medida.
            warn (float): Umbral de advertencia.
            crit (float): Umbral crítico.

        Returns:
            None

        Raises:
            None
        """

        color = self._system_monitor.level_color(value, warn, crit)
        self._widgets[f"{key}_value"].configure(text=f"{value:.1f} {unit}", text_color=color)
        self._widgets[f"{key}_label"].configure(text_color=color)
        g = self._graphs[key]
        g['widget'].update(history, g['max_val'], color)
