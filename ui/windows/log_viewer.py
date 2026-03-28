"""
Ventana de visualización del log del dashboard.
Permite filtrar por nivel, módulo, texto libre e intervalo de tiempo
y exportar el resultado filtrado a un archivo .log
"""
import re
import threading
from datetime import datetime, timedelta
from pathlib import Path

import customtkinter as ctk

from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, DATA_DIR, EXPORTS_LOG_DIR
)
from ui.styles import make_window_header, make_futuristic_button, StyleManager
from ui.widgets.dialogs import custom_msgbox
from utils.logger import get_logger
from core.cleanup_service import CleanupService

logger = get_logger(__name__)

LOG_FILE = DATA_DIR / "logs" / "dashboard.log"
LOG_LEVELS = ["TODOS", "DEBUG", "INFO", "WARNING", "ERROR"]
LEVEL_COLORS = {
    "DEBUG":   "#888888",
    "INFO":    "#00BFFF",
    "WARNING": "#FFA500",
    "ERROR":   "#FF4444",
}

_PH_SEARCH = "buscar..."
_PH_MODULE = "módulo..."
_PH_DATE   = "YYYY-MM-DD"
_PH_TIME   = "HH:MM"

LOG_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+Dashboard(?:\.(\S+?))?: (.*)$'
)


class LogViewerWindow(ctk.CTkToplevel):
    """
    Ventana principal para visualización y filtrado de logs del dashboard.

    Args:
        parent: Ventana padre de la aplicación.

    Raises:
        Ninguna excepción específica.

    Returns:
        Ninguno.
    """

    def __init__(self, parent):
        """
        Inicializa la ventana del visor de logs.

        Configura la geometría, variables de estado y filtros, UI, y carga inicial de logs.

        Args:
            parent: La ventana padre.

        Raises:
            Ninguna excepción específica.

        Returns:
            Ninguno
        """
        super().__init__(parent)
        self.title("Visor de Logs")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.lift()
        self.after(150, self.focus_set)
        self._cleanup_service = CleanupService()
        self._all_lines: list = []
        self._modules:   list = []
        self._loading         = False

        self._level_var  = ctk.StringVar(master=self, value="TODOS")
        self._module_var = ctk.StringVar(master=self,value=_PH_MODULE)
        self._search_var = ctk.StringVar(master=self,value=_PH_SEARCH)
        self._quick_var  = ctk.StringVar(master=self,value="1h")
        self._date_from  = ctk.StringVar(master=self,value=_PH_DATE)
        self._time_from  = ctk.StringVar(master=self,value=_PH_TIME)
        self._date_to    = ctk.StringVar(master=self,value=_PH_DATE)
        self._time_to    = ctk.StringVar(master=self,value=_PH_TIME)

        self._create_ui()
        self._load_log()
        logger.info("[LogViewerWindow] Ventana Abierta")


    # ── Placeholder helpers ──────────────────────────────────────────────────

    def _entry_focus_in(self, entry, var, placeholder):
        """
        Limpia el texto placeholder de un campo de texto cuando recibe el foco.

            Args:
                entry: Widget CTkEntry que recibió el foco.
                var: Variable StringVar asociada al campo de texto.
                placeholder: Texto placeholder a limpiar.

            Returns:
                None
        """
        if var.get() == placeholder:
            var.set("")
            entry.configure(text_color=COLORS['text'])

    def _entry_focus_out(self, entry, var, placeholder):
        """
        Restaura el texto placeholder en un campo de texto cuando pierde el foco.

        Args:
            entry: Widget CTkEntry que ha perdido el foco.
            var: Variable StringVar asociada al campo de texto.
            placeholder: Texto placeholder a restaurar cuando el campo está vacío.

        Returns:
            None

        Raises:
            None
        """
        if var.get().strip() == "":
            var.set(placeholder)
            entry.configure(text_color=COLORS['text_dim'])

    def _entry_value(self, var, placeholder):
        """
        Obtiene el valor real del campo de entrada, ignorando placeholder.

        Args:
            var: Variable StringVar del campo.
            placeholder: Texto placeholder de referencia.

        Returns:
            str: Valor limpio o cadena vacía si solo tenía placeholder.
        """
        v = var.get().strip()
        return "" if v == placeholder else v

    def _make_entry(self, parent, var, placeholder, width):
        """
        Crea un CTkEntry con manejo automático de placeholders y bindings.

        Args:
            parent: Contenedor padre.
            var: Variable StringVar.
            placeholder: Texto placeholder inicial.
            width: Ancho del entry en píxeles.

        Returns:
            CTkEntry: Instancia configurada con eventos de foco.
        """
        e = ctk.CTkEntry(
            parent,
            textvariable=var,
            width=width,
            height=28,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['primary'],
            text_color=COLORS['text_dim'],
        )
        e.bind("<FocusIn>",  lambda ev: self._entry_focus_in(e, var, placeholder))
        e.bind("<FocusOut>", lambda ev: self._entry_focus_out(e, var, placeholder))
        return e

    # ── UI ───────────────────────────────────────────────────────────────────

    def _create_ui(self):
        """
        Construye la interfaz de usuario completa del visor de logs.

        Crea el frame principal, header, panel de filtros, área de resultados 
        y barra inferior de controles.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        make_window_header(main, title="VISOR DE LOGS", on_close=self.destroy)
        self._create_filters(main)
        ctk.CTkFrame(main, fg_color=COLORS['border'], height=1,
                     corner_radius=0).pack(fill="x", padx=5, pady=(4, 0))
        self._create_results(main)
        self._create_bottom_bar(main)

    def _create_filters(self, parent):
        """
        Crea el panel de filtros avanzados para la ventana de visualización de registros.

        Args:
            parent: Frame contenedor donde se ubicará el panel de filtros.

        """
        filters = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        filters.pack(fill="x", padx=5, pady=(4, 0))

        # Fila 1: Nivel · Módulo · Búsqueda
        row1 = ctk.CTkFrame(filters, fg_color="transparent")
        row1.pack(fill="x", padx=8, pady=(6, 2))

        ctk.CTkLabel(row1, text="Nivel:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        ctk.CTkOptionMenu(
            row1, variable=self._level_var, values=LOG_LEVELS, width=100,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'], button_color=COLORS['primary'],
            command=lambda _: self._apply_filters()
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(row1, text="Módulo:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        self._module_entry = self._make_entry(row1, self._module_var, _PH_MODULE, width=160)
        self._module_entry.bind("<Return>",     lambda e: self._apply_filters())
        self._module_entry.bind("<KeyRelease>", lambda e: self.after(300, self._apply_filters))
        self._module_entry.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(row1, text="Buscar:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        search_entry = self._make_entry(row1, self._search_var, _PH_SEARCH, width=140)
        search_entry.bind("<Return>",     lambda e: self._apply_filters())
        search_entry.bind("<KeyRelease>", lambda e: self.after(400, self._apply_filters))
        search_entry.pack(side="left")

        # Fila 2: Intervalo rápido | Intervalo manual
        row2 = ctk.CTkFrame(filters, fg_color="transparent")
        row2.pack(fill="x", padx=8, pady=(2, 6))

        ctk.CTkLabel(row2, text="Últimos:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        ctk.CTkOptionMenu(
            row2, variable=self._quick_var,
            values=["15min", "1h", "6h", "24h", "Todo"], width=80,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'], button_color=COLORS['primary'],
            command=self._on_quick_interval
        ).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(row2, text="│", text_color=COLORS['border'],
                     font=(FONT_FAMILY, FONT_SIZES['medium'])).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(row2, text="Desde:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        self._make_entry(row2, self._date_from, _PH_DATE, width=90).pack(side="left", padx=(0, 4))
        self._make_entry(row2, self._time_from, _PH_TIME, width=60).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(row2, text="Hasta:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        self._make_entry(row2, self._date_to, _PH_DATE, width=90).pack(side="left", padx=(0, 4))
        self._make_entry(row2, self._time_to, _PH_TIME, width=60).pack(side="left", padx=(0, 8))

        make_futuristic_button(
            row2, text="Aplicar", command=self._apply_filters,
            width=8, height=4, font_size=13
        ).pack(side="left")

    def _create_results(self, parent):
        """
        Crea el área de visualización de resultados con textbox coloreado.

        Configura tags de color por nivel de log y estilos de scrollbars.

        Args:
            parent: Frame contenedor.

        Raises:
            None
        """
        result_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        result_frame.pack(fill="both", expand=True, padx=5, pady=4)

        self._textbox = ctk.CTkTextbox(
            result_frame,
            fg_color=COLORS['bg_dark'],
            text_color=COLORS['text'],
            font=("Courier New", 12),
            wrap="none",
            state="disabled",
        )
        self._textbox.pack(fill="both", expand=True, padx=4, pady=4)

        self._textbox._textbox.tag_config("DEBUG",   foreground=LEVEL_COLORS["DEBUG"])
        self._textbox._textbox.tag_config("INFO",    foreground=LEVEL_COLORS["INFO"])
        self._textbox._textbox.tag_config("WARNING", foreground=LEVEL_COLORS["WARNING"])
        self._textbox._textbox.tag_config("ERROR",   foreground=LEVEL_COLORS["ERROR"])

        try:
            children = self._textbox._textbox.master.children
            vsb = children.get('!ctkscrollbar')
            hsb = children.get('!ctkscrollbar2')
            if vsb:
                StyleManager.style_scrollbar_ctk(vsb)
                vsb.configure(width=22)
            if hsb:
                StyleManager.style_scrollbar_ctk(hsb)
                hsb.configure(height=22)
        except Exception:
            pass

    def _create_bottom_bar(self, parent):
        """
        Crea la barra inferior con controles de contador, exportar y recargar.

        Args:
            parent: Frame contenedor.

        Returns:
            None

        Raises:
            None
        """
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.pack(fill="x", padx=5, pady=(0, 4))

        self._count_label = ctk.CTkLabel(
            bar, text="0 entradas",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim']
        )
        self._count_label.pack(side="left", padx=8)

        make_futuristic_button(
            bar, text="↓ Exportar", command=self._export,
            width=10, height=5, font_size=14
        ).pack(side="right", padx=4)

        make_futuristic_button(
            bar, text="↺ Recargar", command=self._load_log,
            width=10, height=5, font_size=14
        ).pack(side="right", padx=4)

    # ── Carga ────────────────────────────────────────────────────────────────

    def _load_log(self):
        """
        Inicia la carga asíncrona de logs desde archivo.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if self._loading:
            return
        self._loading = True
        self._set_text("Cargando log...", [])
        threading.Thread(target=self._read_log_thread, daemon=True).start()

    def _read_log_thread(self):
        """
        Hilo secundario para lectura y parseo de logs.

        Lee logs principales y rotados, parsea líneas con regex y actualiza 
        módulos/lista de líneas en un entorno thread-safe.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Exception: Si ocurre un error al leer o parsear el log.
        """
        lines = []
        try:
            rotated = Path(str(LOG_FILE) + ".1")
            if rotated.exists():
                with open(rotated, "r", encoding="utf-8", errors="replace") as f:
                    for raw in f:
                        p = self._parse_line(raw.rstrip())
                        if p:
                            lines.append(p)
            if LOG_FILE.exists():
                with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                    for raw in f:
                        p = self._parse_line(raw.rstrip())
                        if p:
                            lines.append(p)
        except Exception as e:
            logger.error("[LogViewerWindow] Error leyendo log: %s", e)

        self._all_lines = lines
        self._loading = False
        modules = sorted(set(l["module"] for l in lines))
        self.after(0, lambda: self._update_modules(modules))
        self.after(0, self._apply_filters)

    def _parse_line(self, raw):
        """
        Parsea una línea de log cruda usando regex, extrayendo timestamp, nivel, módulo y mensaje, y validando la fecha.

        Args:
            raw (str): Línea de log como string.

        Returns:
            dict o None: Estructura parseada con ts, ts_str, level, module, message y raw, o None si no coincide patrón.

        Raises:
            None
        """
        m = LOG_PATTERN.match(raw)
        if not m:
            return None
        ts_str, level, module, message = m.groups()
        if not module:
            module = "general"
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
        return {"ts": ts, "ts_str": ts_str, "level": level,
                "module": module, "message": message, "raw": raw}

    def _update_modules(self, modules):
        """
        Actualiza la lista de módulos únicos detectados en logs.

        Args:
            modules: Lista ordenada de nombres de módulos.

        Returns:
            None

        Raises:
            None
        """
        self._modules = modules

    # ── Filtrado ─────────────────────────────────────────────────────────────

    def _on_quick_interval(self, value):
        """
        Configura intervalos de tiempo rápidos automáticamente.

        Actualiza campos fecha/hora basados en selección y aplica filtros inmediatamente.

        Args:
            value (str): Opción seleccionada (ej: '15min', '1h', '6h', '24h', 'Todo').

        Raises:
            Ninguna excepción específica.
        """
        now = datetime.now()
        deltas = {"15min": timedelta(minutes=15), "1h": timedelta(hours=1),
                  "6h": timedelta(hours=6), "24h": timedelta(hours=24)}
        if value == "Todo":
            for var, ph in [(self._date_from, _PH_DATE), (self._time_from, _PH_TIME),
                            (self._date_to,   _PH_DATE), (self._time_to,   _PH_TIME)]:
                var.set(ph)
        else:
            since = now - deltas[value]
            self._date_from.set(since.strftime("%Y-%m-%d"))
            self._time_from.set(since.strftime("%H:%M"))
            self._date_to.set(now.strftime("%Y-%m-%d"))
            self._time_to.set(now.strftime("%H:%M"))
        self._apply_filters()

    def _apply_filters(self):
        """
        Aplica todos los filtros activos y actualiza la visualización.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        level  = self._level_var.get()
        module = self._entry_value(self._module_var, _PH_MODULE).lower()
        search = self._entry_value(self._search_var, _PH_SEARCH).lower()
        dt_from = self._parse_datetime(
            self._entry_value(self._date_from, _PH_DATE),
            self._entry_value(self._time_from, _PH_TIME), False)
        dt_to = self._parse_datetime(
            self._entry_value(self._date_to, _PH_DATE),
            self._entry_value(self._time_to, _PH_TIME), True)

        result = []
        for line in self._all_lines:
            if level  != "TODOS" and line["level"]  != level:  continue
            if module and module not in line["module"].lower(): continue
            if search and search not in line["raw"].lower():   continue
            if dt_from and line["ts"] < dt_from:               continue
            if dt_to   and line["ts"] > dt_to:                 continue
            result.append(line)

        self._set_text(None, result)
        self._count_label.configure(text=f"{len(result)} entradas")

    def _parse_datetime(self, date_str, time_str, is_end):
        """
        Convierte strings de fecha/hora a objeto datetime.

        Aplica defaults (00:00 inicio, 23:59 fin) si faltan hora.

        Args:
            date_str (str): Fecha en formato YYYY-MM-DD.
            time_str (str): Hora en formato HH:MM.
            is_end (bool): True para usar 23:59 si falta hora.

        Returns:
            datetime o None: Objeto parseado o None si inválido.
        """
        if not date_str:
            return None
        if not time_str:
            time_str = "23:59" if is_end else "00:00"
        try:
            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            return None

    # ── Renderizado ──────────────────────────────────────────────────────────

    def _set_text(self, loading_msg, lines):
        """
        Renderiza logs filtrados o mensaje de carga en textbox.

        Aplica tags de color por nivel y posiciona scroll al final.

        Args:
            loading_msg (str o None): Mensaje de carga o None.
            lines (lista de dicts): Lista de dicts parseados de logs.

        Returns:
            None

        Raises:
            Ninguna excepción.
        """
        self._textbox.configure(state="normal")
        self._textbox._textbox.delete("1.0", "end")
        if loading_msg:
            self._textbox._textbox.insert("end", loading_msg)
        else:
            for line in lines:
                lvl = line["level"]
                tag = lvl if lvl in LEVEL_COLORS else "INFO"
                self._textbox._textbox.insert(
                    "end",
                    f"{line['ts_str']} [{lvl}] {line['module']}: {line['message']}\n",
                    tag
                )
            self._textbox._textbox.see("end")
        self._textbox.configure(state="disabled")

    # ── Exportar ─────────────────────────────────────────────────────────────

    def _export(self):
        """
        Exporta logs filtrados a archivo .log con timestamp único.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        level  = self._level_var.get()
        module = self._entry_value(self._module_var, _PH_MODULE).lower()
        search = self._entry_value(self._search_var, _PH_SEARCH).lower()
        dt_from = self._parse_datetime(
            self._entry_value(self._date_from, _PH_DATE),
            self._entry_value(self._time_from, _PH_TIME), False)
        dt_to = self._parse_datetime(
            self._entry_value(self._date_to, _PH_DATE),
            self._entry_value(self._time_to, _PH_TIME), True)

        result = []
        for line in self._all_lines:
            if level  != "TODOS" and line["level"]  != level:  continue
            if module and module not in line["module"].lower(): continue
            if search and search not in line["raw"].lower():   continue
            if dt_from and line["ts"] < dt_from:               continue
            if dt_to   and line["ts"] > dt_to:                 continue
            result.append(line["raw"])

        if not result:
            custom_msgbox(self, "No hay entradas que exportar.", "Exportar")
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = EXPORTS_LOG_DIR / f"log_export_{ts}.log"
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                f.write("\n".join(result))
            custom_msgbox(self, f"Exportado en:\n{export_path}", "Exportar")
            logger.info("[LogViewerWindow] Log exportado: %s", export_path)
            if self._cleanup_service is not None:
                try:
                    self._cleanup_service.clean_log_exports()
                except Exception as e:
                    logger.warning("[LogViewerWindow] No se pudo limpiar exports: %s", e)
        except OSError as e:
            custom_msgbox(self, f"Error al exportar:\n{e}", "Error")
            logger.error("[LogViewerWindow] Error exportando: %s", e)
