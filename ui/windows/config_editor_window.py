"""
Ventana de edición de configuración local.
Lee los valores actuales en memoria y permite modificarlos.
Al guardar escribe config/local_settings.py con solo los valores
que difieran de los defaults — nunca toca settings.py.
Incluye botón "Guardar y reiniciar" para aplicar cambios.

Iconos: se leen automáticamente desde Icons.__dict__ — no requiere
mantenimiento manual al añadir iconos nuevos a settings.py.

Carga diferida: las filas de iconos se construyen en lotes con after()
para no bloquear el hilo principal al abrir la ventana.
"""
import os
import sys
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
, Icons)
import config.settings as _settings
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import confirm_dialog, custom_msgbox
from utils.logger import get_logger

logger = get_logger(__name__)

# Ruta del fichero que este editor escribe — nunca settings.py
_LOCAL_SETTINGS_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "config", "local_settings.py"
))

# ── Definición de parámetros editables ───────────────────────────────────────
# Formato: (clave, label, tipo, min, max, paso, descripción)
# tipo: "int" | "float"
_SECTIONS = [
    {
        "title": "PANTALLA",
        "color": "primary",
        "params": [
            ("DSI_X",  "Posición X",  "int",   0,    3840, 1,   "Offset horizontal de la ventana (px)"),
            ("DSI_Y",  "Posición Y",  "int",   0,    2160, 1,   "Offset vertical de la ventana (px)"),
        ],
    },
    {
        "title": "TIEMPOS",
        "color": "primary",
        "params": [
            ("UPDATE_MS", "Refresco UI (ms)", "int", 500, 10000, 100,
             "Intervalo de actualización de la interfaz"),
        ],
    },
    {
        "title": "UMBRALES — CPU",
        "color": "warning",
        "params": [
            ("CPU_WARN", "Aviso CPU (%)",   "int", 1, 99, 1, "CPU% para mostrar aviso"),
            ("CPU_CRIT", "Crítico CPU (%)", "int", 1, 99, 1, "CPU% para alerta crítica"),
        ],
    },
    {
        "title": "UMBRALES — TEMPERATURA",
        "color": "warning",
        "params": [
            ("TEMP_WARN", "Aviso Temp (°C)",   "int", 1, 100, 1, "Temperatura para mostrar aviso"),
            ("TEMP_CRIT", "Crítico Temp (°C)", "int", 1, 100, 1, "Temperatura para alerta crítica"),
        ],
    },
    {
        "title": "UMBRALES — RAM",
        "color": "warning",
        "params": [
            ("RAM_WARN", "Aviso RAM (%)",   "int", 1, 99, 1, "RAM% para mostrar aviso"),
            ("RAM_CRIT", "Crítico RAM (%)", "int", 1, 99, 1, "RAM% para alerta crítica"),
        ],
    },
    {
        "title": "UMBRALES — RED",
        "color": "warning",
        "params": [
            ("NET_WARN", "Aviso Red (MB/s)",   "float", 0.1, 100.0, 0.1, "Velocidad para mostrar aviso"),
            ("NET_CRIT", "Crítico Red (MB/s)", "float", 0.1, 100.0, 0.1, "Velocidad para alerta crítica"),
        ],
    },
    {
        "title": "RED",
        "color": "primary",
        "params": [
            ("NET_MAX_MB",          "Escala máx. gráfica (MB/s)", "float", 1.0, 1000.0, 1.0,
             "Límite superior del gráfico de red"),
            ("NET_IDLE_RESET_TIME", "Reset escala inactiva (s)",  "int",   5,   300,    5,
             "Segundos sin tráfico antes de resetear la escala"),
        ],
    },
]

# Iconos excluidos del editor (internos, no son botones de menú)
_ICONS_EXCLUDE = {"UPTIME", "WARNING", "POWER_OFF", "DEGREE", "TRASH"}

# Filas de iconos construidas por tick de after()
_ICON_BATCH = 4


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_editable_icons() -> list:
    """
    Lee Icons.__dict__ en tiempo de ejecución.
    Automático — cualquier icono nuevo en settings.py aparece aquí sin
    tocar este fichero.
    """
    result = []
    for attr, val in vars(Icons).items():
        if attr.startswith("_") or attr in _ICONS_EXCLUDE:
            continue
        if not isinstance(val, str):
            continue
        result.append((attr, val))
    return sorted(result, key=lambda x: x[0])


def _surrogate_to_cp(high: int, low: int) -> int:
    return 0x10000 + (high - 0xD800) * 0x400 + (low - 0xDC00)


def _parse_codepoint(raw: str):
    """
    Acepta: \\udb81\\udda9 | \\U000F06A9 | F06A9 | 0xF06A9
    Devuelve (int codepoint, str escape) o raise ValueError.
    """
    cleaned = raw.strip().replace("\\u", " ").replace("\\U", " ").replace(",", " ")
    tokens  = [t.strip().lstrip("uU0x") for t in cleaned.split() if t.strip()]
    if not tokens:
        raise ValueError("Entrada vacía")
    values = []
    for t in tokens:
        try:
            values.append(int(t, 16))
        except ValueError:
            raise ValueError(f"Valor hexadecimal no válido: '{t}'")
    if len(values) == 2 and 0xD800 <= values[0] <= 0xDBFF and 0xDC00 <= values[1] <= 0xDFFF:
        cp = _surrogate_to_cp(values[0], values[1])
    elif len(values) == 1:
        cp = values[0]
    else:
        raise ValueError(f"Formato no reconocido ({len(values)} valores)")
    if cp > 0x10FFFF:
        raise ValueError(f"Codepoint fuera de rango Unicode: U+{cp:X}")
    return cp, f"\\U{cp:08X}"


def _load_local_settings() -> tuple:
    """
    Lee local_settings.py y devuelve (param_overrides, icon_overrides).
    param_overrides: {clave: valor}   — variables sueltas (CPU_WARN, DSI_X…)
    icon_overrides:  {attr: escape}   — iconos como \\Uxxxxxxxx
    Separados para poder mergear correctamente al guardar.
    """
    param_overrides = {}
    icon_overrides  = {}
    if not os.path.exists(_LOCAL_SETTINGS_PATH):
        return param_overrides, icon_overrides
    try:
        # Leer el fichero línea a línea para detectar asignaciones Icons.*
        with open(_LOCAL_SETTINGS_PATH, "r", encoding="utf-8") as f:
            raw = f.read()
        # Extraer Icons.ATTR = "escape" antes de exec() para no perderlos
        import re
        for m in re.finditer(r'^Icons\.(\w+)\s*=\s*"(\\U[0-9A-Fa-f]{8})"', raw, re.MULTILINE):
            icon_overrides[m.group(1)] = m.group(2)
        # exec para el resto de variables sueltas
        ns = {}
        exec(raw, ns)
        known_icons_attrs = {a for a, _ in _get_editable_icons()}
        for k, v in ns.items():
            if k.startswith("_") or k == "Icons":
                continue
            if k in known_icons_attrs:
                continue   # icono ya capturado arriba
            param_overrides[k] = v
    except Exception as e:
        logger.warning("[ConfigEditor] Error leyendo local_settings.py: %s", e)
    return param_overrides, icon_overrides


def _write_local_settings(param_overrides: dict, icon_overrides: dict):
    lines = [
        '"""',
        "Overrides locales generados por Config Editor.",
        "No editar manualmente — usa la ventana de configuración del dashboard.",
        '"""',
        "",
    ]
    if param_overrides:
        lines.append("# ── Parámetros ───────────────────────────────────────────────────────────────")
        for key, val in param_overrides.items():
            lines.append(f'{key} = "{val}"' if isinstance(val, str) else f"{key} = {val}")
        lines.append("")
    if icon_overrides:
        lines.append("# ── Iconos ───────────────────────────────────────────────────────────────────")
        lines.append("from config.settings import Icons")
        for attr, escape in icon_overrides.items():
            lines.append(f'Icons.{attr} = "{escape}"')
        lines.append("")
    os.makedirs(os.path.dirname(_LOCAL_SETTINGS_PATH), exist_ok=True)
    with open(_LOCAL_SETTINGS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("[ConfigEditor] local_settings.py escrito en %s", _LOCAL_SETTINGS_PATH)


# ── Ventana ───────────────────────────────────────────────────────────────────

class ConfigEditorWindow(ctk.CTkToplevel):
    """Editor de configuración local del dashboard."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Editor de Configuración")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._vars:          dict = {}
        self._icon_vars:     dict = {}
        self._icon_previews: dict = {}

        self._saved_params, self._saved_icons = _load_local_settings()
        self._editable_icons   = _get_editable_icons()
        self._icon_build_idx   = 0
        self._icon_card        = None
        self._icon_loading_lbl = None

        self._create_ui()
        logger.info("[ConfigEditorWindow] Ventana abierta (%d iconos detectados)",
                    len(self._editable_icons))

    # ── Construcción UI ───────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main, title="EDITOR DE CONFIGURACIÓN",
            on_close=self.destroy,
            status_text="Los cambios se aplican al reiniciar",
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

        for section in _SECTIONS:
            self._build_section(self._inner, section)

        self._icon_card, self._icon_loading_lbl = self._build_icons_header(self._inner)

        # Barra inferior
        bar = ctk.CTkFrame(main, fg_color="transparent")
        bar.pack(fill="x", padx=5, pady=(0, 4))

        make_futuristic_button(
            bar, text="Restaurar defaults",
            command=self._restore_defaults,
            width=16, height=6, font_size=13,
        ).pack(side="left", padx=4)

        make_futuristic_button(
            bar, text="Guardar",
            command=self._save,
            width=12, height=6, font_size=13,
        ).pack(side="right", padx=4)

        make_futuristic_button(
            bar, text="Guardar y reiniciar",
            command=self._save_and_restart,
            width=18, height=6, font_size=13,
        ).pack(side="right", padx=4)

        # Carga diferida de iconos
        self.after(50, self._build_icon_batch)

    # ── Secciones de parámetros ───────────────────────────────────────────────

    def _build_section(self, parent, section: dict):
        color = COLORS.get(section["color"], COLORS['primary'])
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(6, 2))

        ctk.CTkLabel(
            card, text=section["title"],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=color, anchor="w",
        ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkFrame(
            card, fg_color=COLORS['border'], height=1, corner_radius=0
        ).pack(fill="x", padx=14, pady=(0, 6))

        for key, label, typ, vmin, vmax, step, desc in section["params"]:
            self._build_param_row(card, key, label, typ, vmin, vmax, step, desc)

        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

    def _build_param_row(self, parent, key, label, typ, vmin, vmax, step, desc):
        current = getattr(_settings, key, None)
        if key in self._saved_params:
            current = self._saved_params[key]

        var = ctk.StringVar(master=self, value=str(current))
        self._vars[key] = var

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=4)

        left = ctk.CTkFrame(row, fg_color="transparent", width=220)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(
            left, text=label,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['text'], anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            left, text=desc,
            font=(FONT_FAMILY, FONT_SIZES['small'] - 2),
            text_color=COLORS['text_dim'], anchor="w",
            wraplength=210,
        ).pack(anchor="w")

        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="right", fill="y", padx=(10, 0))

        entry = ctk.CTkEntry(
            right, textvariable=var,
            width=90, height=36,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['border'],
            justify="center",
        )
        entry.pack()

        btn_row = ctk.CTkFrame(right, fg_color="transparent")
        btn_row.pack(pady=(4, 0))

        make_futuristic_button(
            btn_row, text="−",
            command=lambda k=key, t=typ, s=step, mn=vmin: self._step_value(k, t, -s, mn, None),
            width=5, height=4, font_size=14,
        ).pack(side="left", padx=2)

        make_futuristic_button(
            btn_row, text="+",
            command=lambda k=key, t=typ, s=step, mx=vmax: self._step_value(k, t, s, None, mx),
            width=5, height=4, font_size=14,
        ).pack(side="left", padx=2)

    # ── Sección de iconos — carga diferida ────────────────────────────────────

    def _build_icons_header(self, parent):
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(6, 2))

        ctk.CTkLabel(
            card, text="ICONOS",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'], anchor="w",
        ).pack(anchor="w", padx=14, pady=(10, 2))

        ctk.CTkLabel(
            card,
            text=(
                "Introduce el codepoint del nuevo icono (surrogate pair o directo).\n"
                "Ejemplo:  \\udb81\\udda9  |  F06A9  |  \\U000F06A9"
            ),
            font=(FONT_FAMILY, FONT_SIZES['small'] - 2),
            text_color=COLORS['text_dim'], anchor="w", justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 4))

        loading = ctk.CTkLabel(
            card,
            text=f"Cargando iconos... 0/{len(self._editable_icons)}",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        )
        loading.pack(pady=6)

        ctk.CTkFrame(
            card, fg_color=COLORS['border'], height=1, corner_radius=0
        ).pack(fill="x", padx=14, pady=(0, 6))

        return card, loading

    def _build_icon_batch(self):
        if not self.winfo_exists():
            return

        icons = self._editable_icons
        start = self._icon_build_idx
        end   = min(start + _ICON_BATCH, len(icons))

        for i in range(start, end):
            attr, current_char = icons[i]
            self._build_icon_row(self._icon_card, attr, current_char)

        self._icon_build_idx = end

        if end < len(icons):
            self._icon_loading_lbl.configure(
                text=f"Cargando iconos... {end}/{len(icons)}")
            self.after(10, self._build_icon_batch)
        else:
            self._icon_loading_lbl.configure(text="")
            self._icon_loading_lbl.pack_forget()
            ctk.CTkFrame(self._icon_card, fg_color="transparent", height=6).pack()

    def _build_icon_row(self, parent, attr: str, current_char: str):
        var = ctk.StringVar(master=self, value="")
        self._icon_vars[attr] = var

        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=6)
        row.pack(fill="x", padx=14, pady=2)

        # Icono actual — sin width fijo, padding generoso para glifos anchos
        ctk.CTkLabel(
            row,
            text=current_char,
            font=(FONT_FAMILY, FONT_SIZES['large']),
            text_color=COLORS['primary'],
            padx=10, pady=4,
        ).pack(side="left")

        # Nombre del atributo
        ctk.CTkLabel(
            row, text=attr,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['text'], anchor="w",
            width=200,
        ).pack(side="left", padx=(0, 8))

        # Preview nuevo icono — sin width fijo
        preview = ctk.CTkLabel(
            row, text="",
            font=(FONT_FAMILY, FONT_SIZES['large']),
            text_color=COLORS['success'],
            padx=10, pady=4,
        )
        preview.pack(side="right")
        self._icon_previews[attr] = preview

        # Entrada codepoint
        entry = ctk.CTkEntry(
            row, textvariable=var,
            width=170, height=32,
            font=(FONT_FAMILY, FONT_SIZES['small'] - 2),
            text_color=COLORS['text'],
            fg_color=COLORS['bg_dark'],
            border_color=COLORS['border'],
            placeholder_text="codepoint...",
        )
        entry.pack(side="right", padx=(0, 8))

        var.trace_add(
            "write",
            lambda *_, a=attr, v=var, p=preview: self._update_icon_preview(a, v, p)
        )

    # ── Lógica de edición ─────────────────────────────────────────────────────

    def _step_value(self, key, typ, delta, vmin, vmax):
        try:
            if typ == "int":
                val = int(float(self._vars[key].get())) + int(delta)
                if vmin is not None: val = max(vmin, val)
                if vmax is not None: val = min(vmax, val)
                self._vars[key].set(str(val))
            else:
                val = round(float(self._vars[key].get()) + delta, 3)
                if vmin is not None: val = max(vmin, val)
                if vmax is not None: val = min(vmax, val)
                self._vars[key].set(str(val))
        except ValueError:
            pass

    def _update_icon_preview(self, attr: str, var: ctk.StringVar, preview: ctk.CTkLabel):
        raw = var.get().strip()
        if not raw:
            preview.configure(text="")
            return
        try:
            cp, _ = _parse_codepoint(raw)
            preview.configure(text=chr(cp), text_color=COLORS['success'])
        except ValueError:
            preview.configure(text="" + Icons.CROSS_MARK + "", text_color=COLORS['danger'])

    # ── Recoger y validar ─────────────────────────────────────────────────────

    def _collect(self):
        param_overrides = {}
        icon_overrides  = {}
        errors          = []

        for section in _SECTIONS:
            for key, label, typ, vmin, vmax, step, _ in section["params"]:
                raw     = self._vars[key].get().strip()
                default = getattr(_settings, key, None)
                try:
                    if typ == "int":
                        val = int(float(raw))
                        if vmin is not None and val < vmin:
                            errors.append(f"{label}: mínimo {vmin}"); continue
                        if vmax is not None and val > vmax:
                            errors.append(f"{label}: máximo {vmax}"); continue
                    else:
                        val = round(float(raw), 6)
                        if vmin is not None and val < vmin:
                            errors.append(f"{label}: mínimo {vmin}"); continue
                        if vmax is not None and val > vmax:
                            errors.append(f"{label}: máximo {vmax}"); continue
                    if val != default:
                        param_overrides[key] = val
                except ValueError:
                    errors.append(f"{label}: valor no válido '{raw}'")

        for attr, current_char in self._editable_icons:
            raw = self._icon_vars.get(attr, ctk.StringVar(master=self)).get().strip()
            if not raw:
                continue
            try:
                cp, escape = _parse_codepoint(raw)
                # Comparar con el codepoint actual del icono
                try:
                    current_cp = ord(current_char)
                except TypeError:
                    current_cp = -1
                if cp != current_cp:
                    icon_overrides[attr] = escape
            except ValueError as e:
                errors.append(f"Icono {attr}: {e}")

        # Mergear con overrides ya guardados — los nuevos tienen prioridad,
        # pero los que no están en el formulario se conservan intactos.
        merged_params = dict(self._saved_params)
        merged_params.update(param_overrides)
        # Eliminar los que han vuelto al default
        merged_params = {k: v for k, v in merged_params.items()
                         if v != getattr(_settings, k, None)}

        merged_icons = dict(self._saved_icons)
        merged_icons.update(icon_overrides)

        return merged_params, merged_icons, errors

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _save(self):
        param_overrides, icon_overrides, errors = self._collect()
        if errors:
            custom_msgbox(self, "Errores:\n\n" + "\n".join(f"• {e}" for e in errors), "Error")
            return
        if not param_overrides and not icon_overrides:
            custom_msgbox(self, "No hay cambios respecto a los valores actuales.", "Sin cambios")
            return
        try:
            _write_local_settings(param_overrides, icon_overrides)
            n = len(param_overrides) + len(icon_overrides)
            custom_msgbox(
                self,
                f"{n} cambio{'s' if n != 1 else ''} guardado{'s' if n != 1 else ''}.\n\n"
                "Reinicia el dashboard para aplicarlos.",
                "Guardado"
            )
            self._saved_params, self._saved_icons = _load_local_settings()
        except Exception as e:
            logger.error("[ConfigEditor] Error guardando: %s", e)
            custom_msgbox(self, f"Error al guardar:\n{e}", "Error")

    def _save_and_restart(self):
        param_overrides, icon_overrides, errors = self._collect()
        if errors:
            custom_msgbox(self, "Errores:\n\n" + "\n".join(f"• {e}" for e in errors), "Error")
            return
        if not param_overrides and not icon_overrides:
            custom_msgbox(self, "No hay cambios respecto a los valores actuales.", "Sin cambios")
            return
        n = len(param_overrides) + len(icon_overrides)

        def do_save_restart():
            try:
                _write_local_settings(param_overrides, icon_overrides)
            except Exception as e:
                logger.error("[ConfigEditor] Error guardando: %s", e)
                custom_msgbox(self, f"Error al guardar:\n{e}", "Error")
                return
            python = sys.executable
            script = os.path.abspath(sys.argv[0])
            self.master.quit()
            self.master.destroy()
            os.execv(python, [python, script] + sys.argv[1:])

        confirm_dialog(
            parent=self,
            text=f"¿Guardar {n} cambio{'s' if n != 1 else ''} y reiniciar el dashboard?",
            title=f"{Icons.REINICIAR} Guardar y reiniciar",
            on_confirm=do_save_restart,
        )

    def _restore_defaults(self):
        def do_restore():
            for section in _SECTIONS:
                for key, *_ in section["params"]:
                    default = getattr(_settings, key, None)
                    if default is not None:
                        self._vars[key].set(str(default))
            for attr, _ in self._editable_icons:
                if attr in self._icon_vars:
                    self._icon_vars[attr].set("")
                if attr in self._icon_previews:
                    self._icon_previews[attr].configure(text="")
            if os.path.exists(_LOCAL_SETTINGS_PATH):
                try:
                    os.remove(_LOCAL_SETTINGS_PATH)
                    logger.info("[ConfigEditor] local_settings.py eliminado")
                except Exception as e:
                    logger.error("[ConfigEditor] Error borrando local_settings.py: %s", e)
            self._saved_params = {}
            self._saved_icons  = {}
            custom_msgbox(self, "Valores restaurados a los defaults.\n\nReinicia para aplicar.", "Restaurado")

        confirm_dialog(
            parent=self,
            text="¿Restaurar todos los valores a los defaults de settings.py?\n\nEsto eliminará local_settings.py.",
            title=f"{Icons.WARNING} Restaurar defaults",
            on_confirm=do_restore,
        )
