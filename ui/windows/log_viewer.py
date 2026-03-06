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

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Visor de Logs")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.lift()
        self.after(150, self.focus_set)

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

    # ── Placeholder helpers ──────────────────────────────────────────────────

    def _entry_focus_in(self, entry, var, placeholder):
        if var.get() == placeholder:
            var.set("")
            entry.configure(text_color=COLORS['text'])

    def _entry_focus_out(self, entry, var, placeholder):
        if var.get().strip() == "":
            var.set(placeholder)
            entry.configure(text_color=COLORS['text_dim'])

    def _entry_value(self, var, placeholder):
        v = var.get().strip()
        return "" if v == placeholder else v

    def _make_entry(self, parent, var, placeholder, width):
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
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        make_window_header(main, title="VISOR DE LOGS", on_close=self.destroy)
        self._create_filters(main)
        ctk.CTkFrame(main, fg_color=COLORS['border'], height=1,
                     corner_radius=0).pack(fill="x", padx=5, pady=(4, 0))
        self._create_results(main)
        self._create_bottom_bar(main)

    def _create_filters(self, parent):
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
        if self._loading:
            return
        self._loading = True
        self._set_text("Cargando log...", [])
        threading.Thread(target=self._read_log_thread, daemon=True).start()

    def _read_log_thread(self):
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
            logger.error(f"[LogViewerWindow] Error leyendo log: {e}")

        self._all_lines = lines
        self._loading = False
        modules = sorted(set(l["module"] for l in lines))
        self.after(0, lambda: self._update_modules(modules))
        self.after(0, self._apply_filters)

    def _parse_line(self, raw):
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
        self._modules = modules

    # ── Filtrado ─────────────────────────────────────────────────────────────

    def _on_quick_interval(self, value):
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
            logger.info(f"[LogViewerWindow] Log exportado: {export_path}")
            try:
                CleanupService().clean_log_exports()
            except Exception as e:
                logger.warning(f"[LogViewerWindow] No se pudo limpiar exports: {e}")
        except OSError as e:
            custom_msgbox(self, f"Error al exportar:\n{e}", "Error")
            logger.error(f"[LogViewerWindow] Error exportando: {e}")
