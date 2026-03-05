"""
Ventana de gestión de crontab.
Permite ver, añadir, editar y eliminar entradas del crontab
para el usuario actual (jalivur) o root.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import custom_msgbox, confirm_dialog
from core.crontab_service import (
    read_crontab, write_crontab, parse_crontab, build_line,
    describe_cron, QUICK_SCHEDULES,
)
from utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM_USER = "jalivur"


class CrontabWindow(ctk.CTkToplevel):
    """Ventana de gestión de crontab — ver, añadir, editar y eliminar."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Gestión de Crontab")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._user_var   = ctk.StringVar(value=_SYSTEM_USER)
        self._lines      = []    # líneas raw del crontab
        self._parsed     = []    # entradas parseadas (solo las válidas)
        self._edit_index = None  # índice en _parsed de la entrada en edición
        self._panel_open = False

        # Variables del formulario
        self._f_minute  = ctk.StringVar(value="*")
        self._f_hour    = ctk.StringVar(value="*")
        self._f_day     = ctk.StringVar(value="*")
        self._f_month   = ctk.StringVar(value="*")
        self._f_weekday = ctk.StringVar(value="*")
        self._f_command = ctk.StringVar(value="")

        self._create_ui()
        self._load()
        logger.info("[CrontabWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        self._main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        self._main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(self._main, title="GESTIÓN DE CRONTAB", on_close=self.destroy)

        # ── Selector de usuario + botón añadir ──
        top_bar = ctk.CTkFrame(self._main, fg_color=COLORS['bg_dark'], corner_radius=8)
        top_bar.pack(fill="x", padx=5, pady=(0, 4))

        ctk.CTkLabel(top_bar, text="Usuario:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(12, 6), pady=8)

        for label, value in [(_SYSTEM_USER, _SYSTEM_USER), ("root", "root")]:
            rb = ctk.CTkRadioButton(
                top_bar, text=label,
                variable=self._user_var, value=value,
                command=self._on_user_change,
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text'],
            )
            StyleManager.style_radiobutton_ctk(rb)
            rb.pack(side="left", padx=10, pady=8)

        make_futuristic_button(
            top_bar, text=f"{Icons.PLUS} Nueva entrada",
            command=self._open_new_form,
            width=16, height=6, font_size=14,
        ).pack(side="right", padx=10, pady=6)

        # ── Panel de edición / nueva entrada (oculto por defecto) ──
        self._edit_panel = ctk.CTkFrame(self._main, fg_color=COLORS['bg_dark'], corner_radius=8)
        self._build_edit_panel(self._edit_panel)

        # ── Lista scrollable ──
        self._scroll_container = ctk.CTkFrame(self._main, fg_color=COLORS['bg_medium'])
        self._scroll_container.pack(fill="both", expand=True, padx=5, pady=4)

        canvas = ctk.CTkCanvas(
            self._scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        sb = ctk.CTkScrollbar(
            self._scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        sb.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(sb)
        canvas.configure(yscrollcommand=sb.set)

        self._list_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self._list_frame, anchor="nw",
                              width=DSI_WIDTH - 50)
        self._list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # ── Panel formulario de edición / nueva entrada ───────────────────────────

    def _build_edit_panel(self, parent):
        self._panel_title = ctk.CTkLabel(
            parent, text="NUEVA ENTRADA",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['primary'],
        )
        self._panel_title.pack(anchor="w", padx=14, pady=(10, 4))

        # ── Accesos rápidos ──
        ctk.CTkLabel(parent, text="Accesos rápidos:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(anchor="w", padx=14, pady=(4, 2))

        quick_row = ctk.CTkFrame(parent, fg_color="transparent")
        quick_row.pack(fill="x", padx=10, pady=(0, 6))
        for label, m, h, d, mo, wd in QUICK_SCHEDULES:
            make_futuristic_button(
                quick_row, text=label,
                command=lambda _m=m, _h=h, _d=d, _mo=mo, _wd=wd:
                    self._apply_quick(_m, _h, _d, _mo, _wd),
                width=12, height=5, font_size=11,
            ).pack(side="left", padx=3, pady=2)

        # ── Campos de expresión cron ──
        fields_row = ctk.CTkFrame(parent, fg_color="transparent")
        fields_row.pack(fill="x", padx=10, pady=4)

        for label, var in [
            ("Minuto\n(0-59)",  self._f_minute),
            ("Hora\n(0-23)",    self._f_hour),
            ("Día mes\n(1-31)", self._f_day),
            ("Mes\n(1-12)",     self._f_month),
            ("Día sem\n(0-6)",  self._f_weekday),
        ]:
            col = ctk.CTkFrame(fields_row, fg_color="transparent")
            col.pack(side="left", padx=4)
            ctk.CTkLabel(col, text=label,
                         font=(FONT_FAMILY, FONT_SIZES['small']),
                         text_color=COLORS['text_dim'],
                         justify="center").pack()
            ctk.CTkEntry(col, textvariable=var, width=60,
                         font=(FONT_FAMILY, FONT_SIZES['small']),
                         fg_color=COLORS['bg_medium'],
                         border_color=COLORS['primary']).pack()

        # ── Comando ──
        cmd_row = ctk.CTkFrame(parent, fg_color="transparent")
        cmd_row.pack(fill="x", padx=14, pady=(4, 2))
        ctk.CTkLabel(cmd_row, text="Comando:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 8))
        ctk.CTkEntry(cmd_row, textvariable=self._f_command,
                     width=DSI_WIDTH - 220,
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     fg_color=COLORS['bg_medium'],
                     border_color=COLORS['primary']).pack(side="left")

        # ── Preview expresión ──
        self._preview_label = ctk.CTkLabel(
            parent, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        )
        self._preview_label.pack(anchor="w", padx=14, pady=(2, 4))

        for var in (self._f_minute, self._f_hour, self._f_day,
                    self._f_month, self._f_weekday):
            var.trace_add("write", lambda *_: self._update_preview())

        # ── Botones del formulario ──
        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(2, 10))

        make_futuristic_button(
            btn_row, text=f"{Icons.SAVE} Guardar",
            command=self._save_entry,
            width=12, height=6, font_size=14,
        ).pack(side="left", padx=4)

        make_futuristic_button(
            btn_row, text=f"{Icons.CROSS} Cancelar",
            command=self._close_form,
            width=12, height=6, font_size=14,
        ).pack(side="left", padx=4)

    def _update_preview(self):
        if not hasattr(self, "_preview_label"):
            return
        m  = self._f_minute.get().strip()  or "*"
        h  = self._f_hour.get().strip()    or "*"
        d  = self._f_day.get().strip()     or "*"
        mo = self._f_month.get().strip()   or "*"
        wd = self._f_weekday.get().strip() or "*"
        self._preview_label.configure(text=f"→ {describe_cron(m, h, d, mo, wd)}")

    def _apply_quick(self, m, h, d, mo, wd):
        if m.startswith("@"):
            self._f_minute.set(m)
            for v in (self._f_hour, self._f_day, self._f_month, self._f_weekday):
                v.set("")
        else:
            self._f_minute.set(m)
            self._f_hour.set(h)
            self._f_day.set(d)
            self._f_month.set(mo)
            self._f_weekday.set(wd)
        self._update_preview()

    # ── Abrir / cerrar formulario ─────────────────────────────────────────────

    def _open_new_form(self):
        self._edit_index = None
        self._panel_title.configure(text="NUEVA ENTRADA")
        for v, default in [
            (self._f_minute,  "*"), (self._f_hour,    "*"),
            (self._f_day,     "*"), (self._f_month,   "*"),
            (self._f_weekday, "*"), (self._f_command, ""),
        ]:
            v.set(default)
        self._update_preview()
        if not self._panel_open:
            self._edit_panel.pack(fill="x", padx=5, pady=(0, 4),
                                  before=self._scroll_container)
            self._panel_open = True

    def _open_edit_form(self, index: int):
        entry = self._parsed[index]
        self._edit_index = index
        self._panel_title.configure(text="EDITAR ENTRADA")
        if entry["special"]:
            self._f_minute.set(entry["special"])
            for v in (self._f_hour, self._f_day, self._f_month, self._f_weekday):
                v.set("")
        else:
            self._f_minute.set(entry["minute"])
            self._f_hour.set(entry["hour"])
            self._f_day.set(entry["day"])
            self._f_month.set(entry["month"])
            self._f_weekday.set(entry["weekday"])
        self._f_command.set(entry["command"])
        self._update_preview()
        if not self._panel_open:
            self._edit_panel.pack(fill="x", padx=5, pady=(0, 4),
                                  before=self._scroll_container)
            self._panel_open = True

    def _close_form(self):
        self._edit_panel.pack_forget()
        self._panel_open = False
        self._edit_index = None

    # ── Guardar entrada ───────────────────────────────────────────────────────

    def _save_entry(self):
        m   = self._f_minute.get().strip()
        h   = self._f_hour.get().strip()
        d   = self._f_day.get().strip()
        mo  = self._f_month.get().strip()
        wd  = self._f_weekday.get().strip()
        cmd = self._f_command.get().strip()

        if not cmd:
            custom_msgbox(self, "El campo Comando no puede estar vacío.", "Error")
            return

        if not m.startswith("@"):
            for field, name in [(m, "Minuto"), (h, "Hora"), (d, "Día mes"),
                                 (mo, "Mes"), (wd, "Día semana")]:
                if not field:
                    custom_msgbox(self, f"El campo '{name}' no puede estar vacío.", "Error")
                    return

        new_line = build_line(m, h, d, mo, wd, cmd)

        if self._edit_index is not None:
            old_raw = self._parsed[self._edit_index]["raw"]
            for i, line in enumerate(self._lines):
                if line == old_raw:
                    self._lines[i] = new_line
                    break
        else:
            self._lines.append(new_line)

        ok, msg = write_crontab(self._user_var.get(), self._lines)
        if ok:
            self._close_form()
            self._load()
        else:
            custom_msgbox(self, msg, "Error al guardar")

    # ── Eliminar entrada ──────────────────────────────────────────────────────

    def _delete_entry(self, index: int):
        raw = self._parsed[index]["raw"]

        def do_delete():
            new_lines = [l for l in self._lines if l != raw]
            ok, msg = write_crontab(self._user_var.get(), new_lines)
            if ok:
                self._load()
            else:
                custom_msgbox(self, msg, "Error al eliminar")

        confirm_dialog(
            parent=self,
            text=f"¿Eliminar esta entrada?\n\n{raw}",
            title=f"{Icons.TRASH} Confirmar",
            on_confirm=do_delete,
        )

    # ── Carga y renderizado ───────────────────────────────────────────────────

    def _load(self):
        self._lines  = read_crontab(self._user_var.get())
        self._parsed = parse_crontab(self._lines)
        self._render_list()

    def _render_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        if not self._parsed:
            ctk.CTkLabel(
                self._list_frame,
                text="No hay entradas en el crontab.\n"
                     "Pulsa '＋ Nueva entrada' para añadir una.",
                text_color=COLORS['text_dim'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                justify="center",
            ).pack(pady=40)
            return

        hdr = ctk.CTkFrame(self._list_frame, fg_color=COLORS['bg_dark'], corner_radius=6)
        hdr.pack(fill="x", padx=6, pady=(4, 2))
        hdr.grid_columnconfigure(0, weight=2)
        hdr.grid_columnconfigure(1, weight=3)
        hdr.grid_columnconfigure(2, weight=0)

        for col, text in enumerate(["Expresión", "Comando", "Acciones"]):
            ctk.CTkLabel(hdr, text=text,
                         font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                         text_color=COLORS['text_dim']).grid(
                row=0, column=col, padx=10, pady=6, sticky="w")

        for i, entry in enumerate(self._parsed):
            self._create_entry_row(i, entry)

    def _create_entry_row(self, index: int, entry: dict):
        row = ctk.CTkFrame(self._list_frame, fg_color=COLORS['bg_dark'], corner_radius=6)
        row.pack(fill="x", padx=6, pady=2)
        row.grid_columnconfigure(0, weight=2)
        row.grid_columnconfigure(1, weight=3)
        row.grid_columnconfigure(2, weight=0)

        expr_col = ctk.CTkFrame(row, fg_color="transparent")
        expr_col.grid(row=0, column=0, padx=10, pady=8, sticky="w")

        expr_text = (entry["special"] if entry["special"]
                     else f"{entry['minute']} {entry['hour']} "
                          f"{entry['day']} {entry['month']} {entry['weekday']}")

        ctk.CTkLabel(
            expr_col, text=expr_text,
            font=("Courier New", 13, "bold"),
            text_color=COLORS['primary'], anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            expr_col,
            text=describe_cron(entry["minute"], entry["hour"],
                               entry["day"], entry["month"], entry["weekday"]),
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'], anchor="w",
        ).pack(anchor="w")

        cmd_text = entry["command"]
        if len(cmd_text) > 55:
            cmd_text = cmd_text[:52] + "…"
        ctk.CTkLabel(
            row, text=cmd_text,
            font=("Courier New", 12),
            text_color=COLORS['text'], anchor="w", wraplength=300,
        ).grid(row=0, column=1, padx=10, pady=8, sticky="w")

        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=8, pady=6)

        make_futuristic_button(
            btn_frame, text=Icons.PENCIL,
            command=lambda i=index: self._open_edit_form(i),
            width=5, height=5, font_size=14,
        ).pack(side="left", padx=3)

        make_futuristic_button(
            btn_frame, text=Icons.TRASH,
            command=lambda i=index: self._delete_entry(i),
            width=5, height=5, font_size=14,
        ).pack(side="left", padx=3)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_user_change(self):
        self._close_form()
        self._load()
