"""
Ventana de monitoreo de disco
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons)
from ui.styles import StyleManager, make_window_header
from ui.widgets import GraphWidget
from core.disk_monitor import DiskMonitor
from utils.logger import get_logger

logger = get_logger(__name__)

_COL_W   = (DSI_WIDTH - 70) // 2
_GRAPH_H = 95

# Cada cuántos ciclos de _update se refresca el SMART (es lento — smartctl tarda ~1s)
# UPDATE_MS suele ser 1000ms → cada 30 ciclos = cada 30 segundos
_SMART_EVERY = 30


class DiskWindow(ctk.CTkToplevel):
    """
    Ventana emergente para monitorear el estado del disco.

    Args:
        parent: Widget padre que crea esta ventana.
        disk_monitor: Instancia de DiskMonitor para obtener estadísticas de disco.

    Raises:
        Ninguna excepción específica.

    Returns:
        Ningún valor de retorno.
    """


    def __init__(self, parent, disk_monitor: DiskMonitor):
        """
        Inicializa la ventana de monitoreo de disco con el monitor de disco proporcionado.

        Configura título, geometría, colores y lanza creación de UI + bucle de actualizaciones.

        Args:
            parent: Widget padre (ctk.CTkToplevel).
            disk_monitor: Instancia de DiskMonitor para obtener estadísticas de disco.
        """
        super().__init__(parent)
        self._disk_monitor = disk_monitor
        self._widgets = {}
        self._graphs  = {}

        self._smart_tick = 0          # contador de ciclos para el SMART
        self._smart_cache = {}        # último resultado SMART

        self.title("Monitor de Disco")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        self._create_ui()
        self._update()
        logger.info("[DiskWindow] Ventana Abierta")


    def _create_ui(self):
        """
        Crea la interfaz gráfica completa de la ventana del disco.

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
            main, title="MONITOR DE DISCO", on_close=self.destroy)

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
        self._content_inner = inner
        # ── Grid 2 columnas — celdas originales con gráfica ──
        grid = ctk.CTkFrame(inner, fg_color=COLORS['bg_medium'])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self._create_cell(grid, 0, 0, "DISCO %",   "disk",       "%",    _GRAPH_H)
        self._create_cell(grid, 0, 1, "NVMe °C",   "nvme_temp",  "°C",   _GRAPH_H)
        self._create_cell(grid, 1, 0, "ESCRITURA", "disk_write", "MB/s", _GRAPH_H)
        self._create_cell(grid, 1, 1, "LECTURA",   "disk_read",  "MB/s", _GRAPH_H)

        # ── Tarjeta SMART NVMe (ancha, debajo del grid) ──
        smart_card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        smart_card.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkLabel(
            smart_card,
            text=f"{Icons.MONITOR_DISCO} NVMe SMART",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(anchor="w", padx=8, pady=(6, 4))

        # Fila 1: Horas de uso / Ciclos de encendido / Apagados bruscos
        row1 = ctk.CTkFrame(smart_card, fg_color="transparent")
        row1.pack(fill="x", padx=8, pady=(0, 4))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)
        row1.grid_columnconfigure(2, weight=1)

        for col_idx, (key, title) in enumerate([
            ("power_on_hours", "Horas de uso"),
            ("power_cycles",   "Ciclos encendido"),
            ("unsafe_shutdowns", "Apagados bruscos"),
        ]):
            self._create_smart_col(row1, col_idx, key, title)

        # Separador
        ctk.CTkFrame(smart_card, fg_color=COLORS['border'], height=1).pack(
            fill="x", padx=8, pady=2)

        # Fila 2: TBW consumido / TB leídos / Vida útil consumida
        row2 = ctk.CTkFrame(smart_card, fg_color="transparent")
        row2.pack(fill="x", padx=8, pady=(4, 10))
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)
        row2.grid_columnconfigure(2, weight=1)

        for col_idx, (key, title) in enumerate([
            ("data_written_tb", "TB escritos"),
            ("data_read_tb",    "TB leídos"),
            ("percentage_used", "Vida útil usada"),
        ]):
            self._create_smart_col(row2, col_idx, key, title)

    def _create_cell(self, parent, row, col, title, key, unit, graph_h):
        """
        Crea una celda con gráfica en la ventana de disco.

        Args:
            parent: El widget padre donde se creará la celda.
            row: La fila donde se posicionará la celda en la cuadrícula.
            col: La columna donde se posicionará la celda en la cuadrícula.
            title: El título de la celda.
            key: La clave única para identificar la celda.
            unit: La unidad de medida para el valor de la celda.
            graph_h: La altura de la gráfica en la celda.

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

    def _create_smart_col(self, parent, col_idx: int, key: str, title: str):
        """
        Crea una columna para mostrar información de un campo SMART sin gráfica.

        Args:
            parent: El widget padre donde se creará la columna.
            col_idx (int): El índice de la columna.
            key (str): La clave para guardar la referencia del widget.
            title (str): El título de la columna.

        Returns:
            None

        Raises:
            None
        """
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=col_idx, padx=4, sticky="nsew")

        ctk.CTkLabel(
            col, text=title,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="center",
        ).pack()

        lbl = ctk.CTkLabel(
            col, text="--",
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
            text_color=COLORS['primary'],
            anchor="center",
        )
        lbl.pack()

        # Guardar referencia con prefijo smart_
        self._widgets[f"smart_{key}"] = lbl

    # ── Update ────────────────────────────────────────────────────────────────

    def _update(self):
        """
        Actualiza la interfaz de DiskWindow con datos actuales e históricos del DiskMonitor.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if not self.winfo_exists():
            return
        if not self._disk_monitor.is_running():
            StyleManager.show_service_stopped_banner(self._content_inner, "Disk Monitor")
            self.after(UPDATE_MS, self._update)
            return
        stats   = self._disk_monitor.get_current_stats()
        self._disk_monitor.update_history(stats)
        history = self._disk_monitor.get_history()

        # Métricas originales con gráfica
        self._update_metric('disk',       stats['disk_usage'],    history['disk_usage'], "%",    60, 80)
        self._update_metric('nvme_temp',  stats['nvme_temp'],     history['nvme_temp'],  "°C",   60, 70)
        self._update_io('disk_write',     stats['disk_write_mb'], history['disk_write'])
        self._update_io('disk_read',      stats['disk_read_mb'],  history['disk_read'])

        self._header.status_label.configure(
            text=f"Uso {stats['disk_usage']:.0f}%  ·  NVMe {stats['nvme_temp']:.0f}°C")

        # SMART — solo cada _SMART_EVERY ciclos (smartctl es lento)
        self._smart_tick += 1
        if self._smart_tick >= _SMART_EVERY:
            self._smart_tick = 0
            self._refresh_smart()

        self.after(UPDATE_MS, self._update)

    def _refresh_smart(self):
        """
        Actualiza las etiquetas SMART del disco duro mediante la información obtenida de get_nvme_smart().

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
        smart = self._disk_monitor.get_nvme_smart()
        self._smart_cache = smart

        if not smart.get("available"):
            for key in ("power_on_hours", "power_cycles", "unsafe_shutdowns",
                        "data_written_tb", "data_read_tb", "percentage_used"):
                lbl = self._widgets.get(f"smart_{key}")
                if lbl:
                    lbl.configure(text="N/D", text_color=COLORS['text_dim'])
            return

        # Horas de uso
        self._set_smart("power_on_hours",
                        self._fmt_hours(smart.get("power_on_hours")),
                        warn=None)

        # Ciclos de encendido
        self._set_smart("power_cycles",
                        self._fmt_int(smart.get("power_cycles")),
                        warn=None)

        # Apagados bruscos — resaltar si hay muchos
        unsafe = smart.get("unsafe_shutdowns", 0) or 0
        self._set_smart("unsafe_shutdowns",
                        str(unsafe),
                        warn=unsafe > 10)

        # TB escritos
        self._set_smart("data_written_tb",
                        self._fmt_tb(smart.get("data_written_tb")),
                        warn=None)

        # TB leídos
        self._set_smart("data_read_tb",
                        self._fmt_tb(smart.get("data_read_tb")),
                        warn=None)

        # Vida útil consumida — color según nivel
        pct = smart.get("percentage_used")
        if pct is not None:
            if pct >= 90:
                color = COLORS['danger']
            elif pct >= 70:
                color = COLORS['warning']
            else:
                color = COLORS['primary']
            lbl = self._widgets.get("smart_percentage_used")
            if lbl:
                lbl.configure(text=f"{pct} %", text_color=color)
        else:
            self._set_smart("percentage_used", "--", warn=None)

    def _set_smart(self, key: str, text: str, warn):
        """
        Actualiza una etiqueta SMART con color según warn.

        Args:
            key (str): Clave de la etiqueta SMART.
            text (str): Texto a mostrar en la etiqueta.
            warn: Indica el color a utilizar en la etiqueta.

        Returns:
            None

        Raises:
            None
        """
        lbl = self._widgets.get(f"smart_{key}")
        if not lbl:
            return
        if warn is True:
            color = COLORS['warning']
        elif warn is False:
            color = COLORS['danger']
        else:
            color = COLORS['primary']
        lbl.configure(text=text, text_color=color)

    # ── Formateo ──────────────────────────────────────────────────────────────

    @staticmethod
    def _fmt_hours(hours) -> str:
        """
        Convierte horas totales de uso en formato legible 'Dd Hh'.

        Args:
            hours (float | None): Horas totales.

        Returns:
            str: Formato 'Dd Hh' o '--' si hours es None.
        """
        if hours is None:
            return "--"
        d = hours // 24
        h = hours % 24
        return f"{d}d {h}h"

    @staticmethod
    def _fmt_int(val) -> str:
        """
        Formatea un valor entero o None como cadena.

        Args:
            val (int | None): Valor a formatear.

        Returns:
            str: Representación en cadena del valor o '--' si es None.
        """
        return "--" if val is None else str(val)

    @staticmethod
    def _fmt_tb(val) -> str:
        """
        Formatea terabytes en TB o GB según magnitud.

        Args:
            val (float | None): TB a formatear.

        Returns:
            str: Representación formateada del valor en TB o GB, o '--' si el valor es None.
        """
        if val is None:
            return "--"
        if val < 1.0:
            return f"{val * 1024:.0f} GB"
        return f"{val:.2f} TB"

    # ── Métricas originales — sin cambios ────────────────────────────────────

    def _update_metric(self, key, value, history, unit, warn, crit):
        """
        Actualiza la etiqueta, el color y el gráfico de una métrica con umbrales.

        Args:
            key (str): Identificador de la métrica.
            value (float): Valor actual de la métrica.
            history (list): Historial de valores para el gráfico.
            unit (str): Unidad de medida de la métrica ('%', '°C').
            warn (float): Umbral de advertencia.
            crit (float): Umbral crítico.

        Returns:
            None

        Raises:
            None
        """
        color = self._disk_monitor.level_color(value, warn, crit)
        self._widgets[f"{key}_value"].configure(text=f"{value:.1f} {unit}", text_color=color)
        self._widgets[f"{key}_label"].configure(text_color=color)
        g = self._graphs[key]
        g['widget'].update(history, g['max_val'], color)

    def _update_io(self, key, value, history):
        """
        Actualiza label, color y gráfico para métricas de I/O (lectura/escritura).

        Usa umbrales fijos: warn=10, crit=50 MB/s.

        Args:
            key (str): 'disk_read' o 'disk_write'.
            value (float): MB/s actual.
            history (list): Historial.

        Returns:
            None

        Raises:
            None
        """
        color = self._disk_monitor.level_color(value, 10, 50)
        self._widgets[f"{key}_value"].configure(text=f"{value:.1f} MB/s", text_color=color)
        self._widgets[f"{key}_label"].configure(text_color=color)
        g = self._graphs[key]
        g['widget'].update(history, g['max_val'], color)
