This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: ui/window_manager.py, ui/main_window.py, config/settings.py, config/button_labels.py, ui/windows/button_manager_window.py, main.py
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)
</notes>

</file_summary>

<directory_structure>
config/
  button_labels.py
  settings.py
ui/
  windows/
    button_manager_window.py
  main_window.py
  window_manager.py
main.py
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path="config/button_labels.py">
"""
Labels de botones del menu principal.

Fuente unica de verdad para los textos de botones que aparecen en:
  - ui/main_window.py      (buttons_config, _btn_active, _btn_idle)
  - ui/window_manager.py   (_BTN_MAP, _ALWAYS_VISIBLE)
  - core/service_registry.py  (no usa labels directamente, pero _BTN_MAP si)

Nunca escribir literales de icono fuera de este fichero.
Para anadir un boton nuevo: añadir aqui primero, luego referenciar en los tres sitios.
"""
from config.settings import Icons

# ── Botones controlables por WindowManager ────────────────────────────────────
HARDWARE_INFO       = f"{Icons.HARDWARE_INFO}  Info Hardware"
FAN_CONTROL         = f"{Icons.FAN_CONTROL}  Control Ventiladores"
LED_RGB             = f"{Icons.LED_RGB}  LEDs RGB"
MONITOR_PLACA       = f"{Icons.MONITOR_PLACA}  Monitor Placa"
MONITOR_RED         = f"{Icons.MONITOR_RED} Monitor Red"
MONITOR_USB         = f"{Icons.MONITOR_USB} Monitor USB"
MONITOR_DISCO       = f"{Icons.MONITOR_DISCO}  Monitor Disco"
LANZADORES          = f"{Icons.LANZADORES}  Lanzadores"
PROCESOS            = f"{Icons.PROCESOS} Monitor Procesos"
SERVICIOS           = f"{Icons.SERVICIOS} Monitor Servicios"
SERVICIOS_DASH      = f"{Icons.SERVICIOS}  Servicios Dashboard"
CRONTAB             = f"{Icons.CRONTAB}  Gestor Crontab"
HISTORICO           = f"{Icons.HISTORICO}  Hist\u00f3rico Datos"
ACTUALIZACIONES     = f"{Icons.ACTUALIZACIONES}  Actualizaciones"
HOMEBRIDGE          = f"{Icons.HOMEBRIDGE}  Homebridge"
VISOR_LOGS          = f"{Icons.VISOR_LOGS}  Visor de Logs"
RED_LOCAL           = f"{Icons.RED_LOCAL}  Red Local"
PIHOLE              = f"{Icons.PIHOLE}  Pi-hole"
VPN                 = f"{Icons.VPN}  Gestor VPN"
HISTORIAL_ALERTAS   = f"{Icons.HISTORIAL_ALERTAS}  Historial Alertas"
BRILLO              = f"{Icons.BRILLO}  Brillo Pantalla"
AUDIO               = f"{Icons.AUDIO}  Control Audio"
CLIMA               = f"{Icons.CLIMA}  Widget Clima"
RESUMEN             = f"{Icons.RESUMEN}  Resumen Sistema"
CAMARA              = f"{Icons.CAMARA}  C\u00e1mara"
TEMA                = f"{Icons.TEMA}  Cambiar Tema"
SSH                 = f"{Icons.SSH}  Monitor SSH"
WIFI                = f"{Icons.WIFI}  Monitor WiFi"
CONFIG              = f"{Icons.CONFIG} Editor Config"

# ── Botones siempre visibles (no controlados por WindowManager) ───────────────
BOTONES             = f"{Icons.BOTONES}  Gestor de Botones"
REINICIAR           = f"{Icons.REINICIAR} Reiniciar"
SALIR               = f"{Icons.SALIR}  Salir"
</file>

<file path="ui/windows/button_manager_window.py">
"""
Ventana de gestión de visibilidad de botones del menú principal.
Permite activar/desactivar qué botones aparecen en el dashboard.
Los cambios son inmediatos en la UI y se persisten con "Guardar predeterminado".
"""
import customtkinter as ctk
import config.button_labels as BL
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import custom_msgbox
from utils.logger import get_logger

logger = get_logger(__name__)

# Fuente única de verdad: clave JSON → constante BL.*
# El orden determina cómo aparecen en la lista.
_BTN_LABELS = {
    "hardware_info":        BL.HARDWARE_INFO,
    "fan_control":          BL.FAN_CONTROL,
    "led_window":           BL.LED_RGB,
    "monitor_window":       BL.MONITOR_PLACA,
    "network_window":       BL.MONITOR_RED,
    "usb_window":           BL.MONITOR_USB,
    "disk_window":          BL.MONITOR_DISCO,
    "launchers":            BL.LANZADORES,
    "process_window":       BL.PROCESOS,
    "service_window":       BL.SERVICIOS,
    "services_manager":     BL.SERVICIOS_DASH,
    "crontab_window":       BL.CRONTAB,
    "history_window":       BL.HISTORICO,
    "update_window":        BL.ACTUALIZACIONES,
    "homebridge":           BL.HOMEBRIDGE,
    "log_viewer":           BL.VISOR_LOGS,
    "network_local":        BL.RED_LOCAL,
    "pihole":               BL.PIHOLE,
    "vpn_window":           BL.VPN,
    "ssh_window":           BL.SSH,
    "wifi_window":          BL.WIFI,
    "alert_history":        BL.HISTORIAL_ALERTAS,
    "display_window":       BL.BRILLO,
    "overview":             BL.RESUMEN,
    "camera_window":        BL.CAMARA,
    "theme_selector":       BL.TEMA,
    "config_editor_window": BL.CONFIG,
    "audio_window":         BL.AUDIO,
    "weather_window":       BL.CLIMA,
}


class ButtonManagerWindow(ctk.CTkToplevel):
    """Ventana para gestionar la visibilidad de botones del menú principal."""

    def __init__(self, parent, registry, window_manager):
        """
        Args:
            parent:         ventana padre (root)
            registry:       ServiceRegistry (para leer/guardar config ui)
            window_manager: WindowManager activo en MainWindow
        """
        super().__init__(parent)
        self.registry       = registry
        self.window_manager = window_manager

        self.title("Gestor de Botones")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._switches: dict = {}

        self._create_ui()
        logger.info("[ButtonManagerWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="GESTOR DE BOTONES", on_close=self.destroy)

        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        sb = ctk.CTkScrollbar(scroll_container, orientation="vertical", command=canvas.yview, width=30)
        sb.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(sb)
        canvas.configure(yscrollcommand=sb.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        ctk.CTkLabel(
            inner,
            text="Activa o desactiva qué botones aparecen en el menú principal.\n"
                 "Los cambios son inmediatos. Usa 'Guardar predeterminado' para que\n"
                 "persistan al reiniciar el dashboard.",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            justify="left",
        ).pack(anchor="w", padx=14, pady=(6, 10))

        for key, label in _BTN_LABELS.items():
            enabled = self.registry.ui_enabled(key)
            self._create_row(inner, key, label, enabled)

        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", padx=10, pady=(0, 8))

        make_futuristic_button(
            bottom,
            text=f"{Icons.SAVE} Guardar predeterminado",
            command=self._save,
            width=28, height=8, font_size=15,
        ).pack(side="left", padx=5)

        make_futuristic_button(
            bottom,
            text=f"{Icons.CHECK} Activar todos",
            command=self._enable_all,
            width=18, height=8, font_size=15,
        ).pack(side="left", padx=5)

        make_futuristic_button(
            bottom,
            text=f"{Icons.CROSS} Desactivar todos",
            command=self._disable_all,
            width=18, height=8, font_size=15,
        ).pack(side="left", padx=5)

    def _create_row(self, parent, key: str, label: str, enabled: bool):
        """Crea una fila con el nombre del botón y su switch ON/OFF."""
        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=6)
        row.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(
            row,
            text=label,
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text'],
            anchor="w",
        ).pack(side="left", padx=14, pady=10, expand=True, fill="x")

        switch = ctk.CTkSwitch(
            row,
            text="",
            command=lambda k=key: self._on_toggle(k),
            width=56, height=28,
            switch_width=56, switch_height=28,
            progress_color=COLORS['primary'],
        )
        switch.pack(side="right", padx=14, pady=10)

        if enabled:
            switch.select()
        else:
            switch.deselect()

        self._switches[key] = switch

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_toggle(self, key: str):
        """Aplica el cambio inmediatamente en la UI del menú principal."""
        enabled = bool(self._switches[key].get())
        if enabled:
            self.window_manager.show(key)
        else:
            self.window_manager.hide(key)
        logger.debug("[ButtonManagerWindow] %s → %s", key, "visible" if enabled else "oculto")

    def _enable_all(self):
        """Activa todos los switches y aplica los cambios."""
        for key, switch in self._switches.items():
            switch.select()
            self.window_manager.show(key)

    def _disable_all(self):
        """Desactiva todos los switches y aplica los cambios."""
        for key, switch in self._switches.items():
            switch.deselect()
            self.window_manager.hide(key)

    def _save(self):
        """Persiste el estado actual al JSON via registry.save_config()."""
        self.registry.save_config()
        logger.info("[ButtonManagerWindow] Configuración de botones guardada")
        custom_msgbox(
            parent=self,
            text=f"{Icons.SAVE}  Configuración guardada\n\n"
                 f"{Icons.CHECK}  Los botones activos se aplicarán\n"
                 f"     al reiniciar el dashboard.",
            title="Guardado",
        )
</file>

<file path="config/settings.py">
"""
Configuración centralizada del sistema de monitoreo
"""
from pathlib import Path
from config.themes import load_selected_theme, get_theme_colors
# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Subdirectorios de exportación
EXPORTS_DIR      = DATA_DIR / "exports"
EXPORTS_CSV_DIR  = EXPORTS_DIR / "csv"
EXPORTS_LOG_DIR  = EXPORTS_DIR / "logs"
EXPORTS_SCR_DIR  = EXPORTS_DIR / "screenshots"

# Asegurar que los directorios existan
DATA_DIR.mkdir(exist_ok=True)
SCRIPTS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
EXPORTS_CSV_DIR.mkdir(exist_ok=True)
EXPORTS_LOG_DIR.mkdir(exist_ok=True)
EXPORTS_SCR_DIR.mkdir(exist_ok=True)

# Archivos de estado
STATE_FILE = DATA_DIR / "fan_state.json"
CURVE_FILE = DATA_DIR / "fan_curve.json"

# Configuración de pantalla DSI
DSI_WIDTH = 800
DSI_HEIGHT = 480
DSI_X = 1124
DSI_Y = 1080

# Configuración de actualización
UPDATE_MS = 2000
HISTORY = 60
GRAPH_WIDTH = 800
GRAPH_HEIGHT = 20

# Umbrales de advertencia y críticos
CPU_WARN = 60
CPU_CRIT = 85
TEMP_WARN = 60
TEMP_CRIT = 75
RAM_WARN = 65
RAM_CRIT = 85

# Configuración de red
NET_WARN = 2.0  # MB/s
NET_CRIT = 6.0
NET_INTERFACE = None  # None = auto | "eth0" | "wlan0"
NET_MAX_MB = 10.0
NET_MIN_SCALE = 0.5
NET_MAX_SCALE = 200.0
NET_IDLE_THRESHOLD = 0.2
NET_IDLE_RESET_TIME = 15  # segundos

# ========================================
# SISTEMA DE TEMAS
# ========================================

SELECTED_THEME = load_selected_theme()
COLORS = get_theme_colors(SELECTED_THEME)

# Fuente
FONT_FAMILY = "FiraMono Nerd Font"
FONT_SIZES = {
    "small": 14,
    "medium": 18,
    "large": 20,
    "xlarge": 24,
    "xxlarge": 30
}


class Icons:
    """
    Iconos Nerd Font y emoji usados en la UI.
    Definidos como escape Unicode para evitar corrupcion al editar.
    Todos los literales de icono deben vivir AQUI — nunca en otros ficheros.
    """

    # Botones del menu principal
    HARDWARE_INFO       = "\U0001f5a5\ufe0f"   # 🖥️
    FAN_CONTROL         = "\U000f0210"          # 󰈐
    LED_RGB             = "\U000f07d6"          # 󰟖
    MONITOR_PLACA       = "\U000f0697"          # 󰚗
    MONITOR_RED         = "\U0001f310"          # 🌐
    MONITOR_USB         = "\U000f11f0"          # 󱇰
    MONITOR_DISCO       = "\ue271"              # 
    LANZADORES          = "\U000f14de"          # 󱓞
    PROCESOS            = "\u2699\ufe0f"        # ⚙️
    SERVICIOS           = "\u2699\ufe0f"        # ⚙️
    CRONTAB             = "\U0001f550"          # 🕐
    BOTONES             = "\uf2a8"              # 
    HISTORICO           = "\U000f163f"          # 󱘿
    ACTUALIZACIONES     = "\U000f01a7"          # 󰆧
    HOMEBRIDGE          = "\U000f07d0"          # 󰟐
    VISOR_LOGS          = "\U000f0dd0"          # 󰷐
    RED_LOCAL           = "\U0001f5a7"          # 🖧
    PIHOLE              = "\U0001f573"          # 🕳
    VPN                 = "\U0001f512"          # 🔒
    HISTORIAL_ALERTAS   = "\uf421"              # 
    BRILLO              = "\U000f00df"          # 󰃟
    RESUMEN             = "\U0001f4ca"          # 📊
    CAMARA              = "\U0001f4f7"          # 📷
    TEMA                = "\U000f050e"          # 󰔎
    AUDIO               = "\U000f075a"          # 󰝚  nf-md-music_note
    VOLUME_HIGH         = "\U000f057e"          # 󰕾  nf-md-volume_high
    VOLUME_MUTE         = "\U000f0580"          # 󰖀  nf-md-volume_mute
    CLIMA               = "\U0001f324\ufe0f"    # 🌤️  nf-weather icon
    REINICIAR           = "\U000f0453"          # 󰑓
    SALIR               = "\U000f0fc5"          # 󰿅
    CONFIG              = "\ueb52"

    # Header principal
    UPTIME              = "\u23f1"             # ⏱

    # Dialogos
    WARNING             = "\u26a0\ufe0f"       # ⚠️
    POWER_OFF           = "\U000f0425"         # 󰐥

    # Misc
    DEGREE              = "\u00b0"             # °
    TRASH               = "\uea81"
    CHECK               = "\uf42e"
    CROSS               = "\uf00d"
    SAVE                = "\uf0c7"
    STOP                = "\uf04d"
    PLAY                = "\uf04b"
    PLUS                = "\uf067"
    PENCIL              = "\uf01f"
    DOWN                = "\uf063"
    UP                  = "\uf062"
    SSH                 = "\U000F08C0"         # 
    WIFI                = "\U000F05A9"         #
    TAP                 = "\U000F0741"
    ETHERNET            = "\U000F0200"
    CALENDAR_RANGE      = "\U000F0679"         # 󰙹  nf-md-calendar_range
    CALENDAR            = "\U000F0150"         # 󰅐  nf-md-calendar
    CLOCK               = "\U000F0954"         # 󰥔  nf-md-clock_outline
    # Lanzadores
    NAS                 = "\U000F08F3"         # 󰣳
    MONTAR              = "\U000F0318"         # 󰌘
    DESMONTAR           = "\U000F0319"         # 󰌙
    UPDATE_SCRIPT       = "\U000F06B0"         # 󰚰
    SHUTDOWN            = "\U000F0159"         # 󰅙

    # Estado y feedback
    OK                  = "\u2705"              # ✅
    ERROR               = "\u274c"              # ❌
    NO_ENTRY            = "\u26d4"              # ⛔
    CHECK_MARK          = "\u2713"              # ✓
    CLOSE_X             = "\u2715"              # ✕
    CROSS_MARK          = "\u2717"              # ✗
    WAITING             = "\u23f3"              # ⏳
    PAUSE               = "\u23f8"              # ⏸
    STOP_MEDIA          = "\u23f9"              # ⏹
    REFRESH             = "\U0001f504"          # 🔄
    SEARCH              = "\U0001f50d"          # 🔍

    # Hardware / sensores
    RAM                 = "\U000f035b"          # 󰍛  nf-md-memory
    THERMOMETER         = "\U0001f321"          # 🌡
    FIRE                = "\U0001f525"          # 🔥

    # Clima — iconos Nerd Font para garantizar render con FiraMono
    WEATHER_HUMIDITY    = "\U000f058e"          # 󰖎  nf-md-water_percent
    WEATHER_WIND        = "\U000f059d"          # 󰖝  nf-md-weather_windy
    WEATHER_PRECIP_PCT  = "\U000f0597"          # 󰖗  nf-md-weather_rainy
    SUN                 = "\U000f0599"          # 󰖙  nf-md-weather_sunny
    SUNRISE             = "\U000f059a"          # 󰖚  nf-md-weather_sunset_up
    SUNSET              = "\U000f059b"          # 󰖛  nf-md-weather_sunset_down
    BACK                = "\U000F004D"          # 󰁍  nf-md-arrow_left_bold
    AIR                 = "\U000F0595"          # 󰖕  nf-md-weather_windy_variant

    # Círculos de color (estado / LEDs)
    RED_CIRCLE          = "\U0001f534"          # 🔴
    GREEN_CIRCLE        = "\U0001f7e2"          # 🟢
    BLUE_CIRCLE         = "\U0001f535"          # 🔵
    YELLOW_CIRCLE       = "\U0001f7e1"          # 🟡
    PURPLE_CIRCLE       = "\U0001f7e3"          # 🟣
    WHITE_CIRCLE        = "\u26aa"              # ⚪

    # Archivos y carpetas
    FOLDER              = "\U0001f4c1"          # 📁
    FOLDER_OPEN         = "\U0001f4c2"          # 📂
    DOCUMENT            = "\U0001f4c4"          # 📄
    CLIPBOARD           = "\U0001f4cb"          # 📋

    # Misc UI
    HOME                = "\U0001f3e0"          # 🏠
    EYE                 = "\U0001f441"          # 👁
    HAND                = "\U0001f590"          # 🖐
    DROPLET             = "\U0001f4a7"          # 💧
    UNLOCK              = "\U0001f513"          # 🔓
    DELETE              = "\U0001f5d1"          # 🗑
    STAR                = "\U0001f31f"          # 🌟

    # Brillo (fases de luna)
    MOON_NEW            = "\U0001f311"          # 🌑
    MOON_CRESCENT       = "\U0001f312"          # 🌒
    MOON_HALF           = "\U0001f313"          # 🌓
    MOON_FULL           = "\U0001f315"          # 🌕

    # Pestañas del menú principal
    TAB_SISTEMA         = "\U000f0697"          # 󰚗  (mismo que MONITOR_PLACA)
    TAB_RED             = "\U0001f310"          # 🌐
    TAB_HARDWARE        = "\U0001f5a5\ufe0f"    # 🖥️
    TAB_SERVICIOS       = "\u2699\ufe0f"        # ⚙️
    TAB_REGISTROS       = "\U000f163f"          # 󱘿
    TAB_CONFIG          = "\ueb52"              # (mismo que CONFIG)
    TAB_CLIMA           = "\U0001f324\ufe0f"    # 🌤️


# ── Menú principal por pestañas ───────────────────────────────────────────────

class UI:
    """
    Configuración visual del menú principal.
    MENU_COLUMNS: número de columnas del grid de botones (ajustable sin tocar lógica).
    MENU_TABS: definición de pestañas — lista de (clave, icono, label, [button_labels_keys]).
    Los button_labels_keys deben coincidir exactamente con los atributos de config.button_labels.
    """
    MENU_COLUMNS = 2

    # Cada entrada: (clave_tab, icono, label_visible, [claves BL en orden])
    # Las claves BL se resuelven en main_window._create_menu_buttons()
    MENU_TABS = [
        (
            "sistema",
            Icons.TAB_SISTEMA,
            "Sistema",
            [
                "RESUMEN",
                "MONITOR_PLACA",
                "MONITOR_DISCO",
                "MONITOR_USB",
                "PROCESOS",
                "ACTUALIZACIONES",
            ],
        ),
        (
            "red",
            Icons.TAB_RED,
            "Red",
            [
                "MONITOR_RED",
                "RED_LOCAL",
                "WIFI",
                "SSH",
                "PIHOLE",
                "VPN",
            ],
        ),
        (
            "hardware",
            Icons.TAB_HARDWARE,
            "Hardware",
            [
                "HARDWARE_INFO",
                "FAN_CONTROL",
                "LED_RGB",
                "BRILLO",
                "AUDIO",
                "CAMARA",
            ],
        ),
        (
            "servicios",
            Icons.TAB_SERVICIOS,
            "Servicios",
            [
                "SERVICIOS",
                "SERVICIOS_DASH",
                "CRONTAB",
                "HOMEBRIDGE",
                "LANZADORES",
            ],
        ),
        (
            "registros",
            Icons.TAB_REGISTROS,
            "Registros",
            [
                "HISTORICO",
                "HISTORIAL_ALERTAS",
                "VISOR_LOGS",
            ],
        ),
        (
            "config",
            Icons.TAB_CONFIG,
            "Config",
            [
                "CONFIG",
                "TEMA",
            ],
        ),
        (
            "clima",
            Icons.TAB_CLIMA,
            "Clima",
            [
                "CLIMA",
            ],
        ),
    ]


# Lanzadores de scripts
# Los labels se construyen desde Icons — nunca escribir literales de icono aqui.
LAUNCHERS = [
    {
        "label": f"{Icons.NAS} {Icons.MONTAR} Montar NAS",
        "script": str(SCRIPTS_DIR / "montarnas.sh")
    },
    {
        "label": f"{Icons.NAS} {Icons.DESMONTAR} Desmontar NAS",
        "script": str(SCRIPTS_DIR / "desmontarnas.sh")
    },
    {
        "label": f"{Icons.UPDATE_SCRIPT}  Update System",
        "script": str(SCRIPTS_DIR / "update.sh")
    },
    {
        "label": f"{Icons.MONTAR}  Conectar VPN",
        "script": str(SCRIPTS_DIR / "conectar_vpn.sh")
    },
    {
        "label": f"{Icons.DESMONTAR}  Desconectar VPN",
        "script": str(SCRIPTS_DIR / "desconectar_vpn.sh")
    },
    {
        "label": f"{Icons.LANZADORES}  Iniciar fase1",
        "script": str(SCRIPTS_DIR / "fase1.sh")
    },
    {
        "label": f"{Icons.SHUTDOWN}  Shutdown",
        "script": str(SCRIPTS_DIR / "apagado.sh")
    }
]


try:
    from config.local_settings import *
except ImportError:
    pass
</file>

<file path="ui/window_manager.py">
"""
Gestor centralizado de ventanas y botones del menu principal.

Controla que botones son visibles segun la seccion "ui" de services.json.
Los servicios y los botones son decisiones INDEPENDIENTES — parar un servicio
no oculta su boton, y ocultar un boton no para su servicio.

Con el menu por pestanas, el WindowManager ya no manipula widgets directamente.
En su lugar, invoca un callback registrado por MainWindow que repopula la pestana
activa filtrando los botones deshabilitados. Esto mantiene la separacion limpia:
WindowManager es fuente de verdad sobre que esta habilitado; MainWindow decide
como renderizarlo.

Uso en MainWindow:
    self._wm = WindowManager(registry, self._menu_btns)
    self._wm.set_rerender_callback(lambda: self._switch_tab(self._active_tab))
"""
import config.button_labels as BL
from utils.logger import get_logger

logger = get_logger(__name__)


class WindowManager:
    """
    Gestiona la visibilidad de botones del menu recolocandolos sin huecos.

    Mapeo: clave del JSON "ui" → constante de config.button_labels.
    Cuando cambia la visibilidad de cualquier boton se invoca el callback
    de rerender registrado por MainWindow (normalmente _switch_tab), que
    repopula el area de botones de la pestana activa filtrando los deshabilitados.

    El WindowManager es la fuente de verdad sobre que esta habilitado via
    registry.ui_enabled(key), pero delega el rerender al MainWindow para
    no asumir nada sobre la estructura de widgets del menu.
    """

    _BTN_MAP = {
        "hardware_info":        BL.HARDWARE_INFO,
        "fan_control":          BL.FAN_CONTROL,
        "led_window":           BL.LED_RGB,
        "monitor_window":       BL.MONITOR_PLACA,
        "network_window":       BL.MONITOR_RED,
        "usb_window":           BL.MONITOR_USB,
        "disk_window":          BL.MONITOR_DISCO,
        "launchers":            BL.LANZADORES,
        "process_window":       BL.PROCESOS,
        "service_window":       BL.SERVICIOS,
        "services_manager":     BL.SERVICIOS_DASH,
        "crontab_window":       BL.CRONTAB,
        "history_window":       BL.HISTORICO,
        "update_window":        BL.ACTUALIZACIONES,
        "homebridge":           BL.HOMEBRIDGE,
        "log_viewer":           BL.VISOR_LOGS,
        "network_local":        BL.RED_LOCAL,
        "pihole":               BL.PIHOLE,
        "vpn_window":           BL.VPN,
        "alert_history":        BL.HISTORIAL_ALERTAS,
        "display_window":       BL.BRILLO,
        "overview":             BL.RESUMEN,
        "camera_window":        BL.CAMARA,
        "theme_selector":       BL.TEMA,
        "ssh_window":           BL.SSH,
        "wifi_window":          BL.WIFI,
        "config_editor_window": BL.CONFIG,
        "audio_window":         BL.AUDIO,
        "weather_window":       BL.CLIMA,
    }

    _ALWAYS_VISIBLE = [
        BL.BOTONES,
        BL.REINICIAR,
        BL.SALIR,
    ]

    def __init__(self, registry, menu_btns: dict):
        self._registry    = registry
        self._menu_btns   = menu_btns
        self._columns     = 2
        self._rerender_cb = None   # callable() registrado por MainWindow

    def set_rerender_callback(self, cb) -> None:
        """Registra el callable que MainWindow ejecutara al cambiar visibilidad.
        Normalmente: lambda: self._switch_tab(self._active_tab)
        """
        self._rerender_cb = cb

    def apply_config(self) -> None:
        """Aplica la configuracion inicial invocando el rerender."""
        self._rerender()

    def show(self, key: str) -> None:
        self._registry._config["ui"][key] = True
        self._rerender()
        logger.info("[WindowManager] Boton visible: %s", key)

    def hide(self, key: str) -> None:
        self._registry._config["ui"][key] = False
        self._rerender()
        logger.info("[WindowManager] Boton oculto: %s", key)

    def is_enabled(self, key: str) -> bool:
        """Devuelve True si el boton con clave JSON key esta habilitado."""
        return self._registry.ui_enabled(key)

    def _rerender(self) -> None:
        """Invoca el callback de rerender registrado por MainWindow."""
        if self._rerender_cb is not None:
            self._rerender_cb()
        else:
            logger.warning("[WindowManager] _rerender llamado sin callback registrado")
</file>

<file path="main.py">
#!/usr/bin/env python3
"""
Sistema de Monitoreo y Control
Punto de entrada principal
"""
import sys
import os
import threading
import customtkinter as ctk
from config import DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from core import (SystemMonitor, FanController, NetworkMonitor, FanAutoService, DiskMonitor, ProcessMonitor,
                  ServiceMonitor, UpdateMonitor, CleanupService, HomebridgeMonitor, AlertService, NetworkScanner,
                  PiholeMonitor, DisplayService, VpnMonitor, LedService, HardwareMonitor, AudioAlertService,
                  SSHMonitor, WiFiMonitor, AudioService, WeatherService)
from core.data_collection_service import DataCollectionService
from core.data_logger import DataLogger
from core.service_registry import ServiceRegistry
from ui.main_window import MainWindow
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Filtro de excepciones ignoradas ──────────────────────────────────────────
# Suprime el traceback de Variable.__del__ que aparece al salir cuando el GC
# recoge StringVar/IntVar de CTkRadioButton tras root.destroy(). Es un bug
# conocido de CustomTkinter — cosmético, no afecta al comportamiento.
# "Exception ignored in:" no pasa por sys.stderr — requiere sys.unraisablehook.

def _unraisable_filter(unraisable):
    """Filtra RuntimeError de Variable.__del__ — deja pasar todo lo demás."""
    if (unraisable.exc_type is RuntimeError
            and "main thread is not in main loop" in str(unraisable.exc_value)
            and unraisable.object is not None
            and getattr(unraisable.object, "__qualname__", "") == "Variable.__del__"):
        return
    sys.__unraisablehook__(unraisable)

sys.unraisablehook = _unraisable_filter

# ─────────────────────────────────────────────────────────────────────────────


def main():
    """Función principal"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("Sistema de Monitoreo")

    root.withdraw()
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.configure(bg="#111111")
    root.update_idletasks()
    root.overrideredirect(True)
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.update_idletasks()
    root.deiconify()

    # ── Instanciar servicios ──────────────────────────────────────────────────
    system_monitor      = SystemMonitor()
    fan_controller      = FanController()
    network_monitor     = NetworkMonitor()
    disk_monitor        = DiskMonitor()
    process_monitor     = ProcessMonitor()
    service_monitor     = ServiceMonitor()
    update_monitor      = UpdateMonitor()
    homebridge_monitor  = HomebridgeMonitor()
    network_scanner     = NetworkScanner()
    pihole_monitor      = PiholeMonitor()
    display_service     = DisplayService()
    led_service         = LedService()
    hardware_monitor    = HardwareMonitor()
    vpn_monitor         = VpnMonitor()
    audio_alert_service = AudioAlertService(system_monitor, service_monitor)
    ssh_monitor         = SSHMonitor()
    wifi_monitor        = WiFiMonitor()
    audio_service       = AudioService()
    weather_service     = WeatherService()

    data_service = DataCollectionService(
        system_monitor=system_monitor,
        fan_controller=fan_controller,
        network_monitor=network_monitor,
        disk_monitor=disk_monitor,
        update_monitor=update_monitor,
        interval_minutes=5
    )

    alert_service = AlertService(
        system_monitor=system_monitor,
        service_monitor=service_monitor,
    )

    cleanup_service = CleanupService(
        data_logger=DataLogger(),
        max_csv=10,
        max_png=10,
        db_days=90,
        interval_hours=24,
    )

    fan_service = FanAutoService(fan_controller, system_monitor)

    # ── Arrancar los que requieren start() explícito ──────────────────────────
    homebridge_monitor.start()
    pihole_monitor.start()
    hardware_monitor.start()
    vpn_monitor.start()
    audio_alert_service.start()
    data_service.start()
    alert_service.start()
    cleanup_service.start()
    fan_service.start()
    ssh_monitor.start()
    wifi_monitor.start()
    weather_service.start()

    # ── Registrar en el registry y aplicar configuración ─────────────────────
    registry = ServiceRegistry()
    registry.register("fan_controller",       fan_controller)
    registry.register("system_monitor",       system_monitor)
    registry.register("disk_monitor",         disk_monitor)
    registry.register("hardware_monitor",     hardware_monitor)
    registry.register("network_monitor",      network_monitor)
    registry.register("network_scanner",      network_scanner)
    registry.register("process_monitor",      process_monitor)
    registry.register("service_monitor",      service_monitor)
    registry.register("update_monitor",       update_monitor)
    registry.register("homebridge_monitor",   homebridge_monitor)
    registry.register("pihole_monitor",       pihole_monitor)
    registry.register("vpn_monitor",          vpn_monitor)
    registry.register("alert_service",        alert_service)
    registry.register("audio_alert_service",  audio_alert_service)
    registry.register("data_service",         data_service)
    registry.register("cleanup_service",      cleanup_service)
    registry.register("fan_service",          fan_service)
    registry.register("led_service",          led_service)
    registry.register("display_service",      display_service)
    registry.register("ssh_monitor",          ssh_monitor)
    registry.register("wifi_monitor",         wifi_monitor)
    registry.register("audio_service",        audio_service)
    registry.register("weather_service",      weather_service)
    # Para los servicios configurados como False en services.json
    registry.apply_config()

    # ── Comprobación inicial de actualizaciones en background ─────────────────
    threading.Thread(
        target=lambda: update_monitor.check_updates(force=True),
        daemon=True,
        name="UpdateCheck-Startup"
    ).start()

    # ── Cleanup centralizado ──────────────────────────────────────────────────
    _cleaned = False

    def cleanup():
        nonlocal _cleaned
        if _cleaned:
            return
        _cleaned = True

        # 1. Destruir la ventana primero — libera todos los StringVar/Tkinter
        #    desde el hilo principal antes de que los threads de fondo hagan GC
        try:
            root.destroy()
        except Exception:
            pass

        # 2. Parar los servicios de fondo
        fan_service.stop()
        data_service.stop()
        cleanup_service.stop()
        homebridge_monitor.stop()
        system_monitor.stop()
        service_monitor.stop()
        alert_service.stop()
        pihole_monitor.stop()
        display_service.disable_dim_on_idle()
        display_service.screen_on()
        vpn_monitor.stop()
        hardware_monitor.stop()
        audio_alert_service.stop()
        wifi_monitor.stop()
        weather_service.stop()

    # ── Crear interfaz ────────────────────────────────────────────────────────
    app = MainWindow(root, registry=registry, update_interval=UPDATE_MS)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()
</file>

<file path="ui/main_window.py">
"""
Ventana principal del sistema de monitoreo.

Responsabilidades de este fichero:
  - Construir el layout (header, pestanas, area de botones, footer)
  - Gestionar el cambio de pestana y el filtrado de botones por visibilidad
  - Coordinar BadgeManager, UpdateLoop y WindowLifecycleManager

Todo lo demas vive en modulos especializados:
  ui/main_badges.py         — BadgeManager
  ui/main_update_loop.py    — UpdateLoop
  ui/main_system_actions.py — exit_application, restart_application
  ui/window_lifecycle.py    — WindowLifecycleManager
  ui/window_manager.py      — WindowManager (visibilidad JSON)
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, Icons
import config.button_labels as BL
from config.settings import UI as UICfg
from ui.styles import StyleManager, make_futuristic_button
from ui.windows import (FanControlWindow, MonitorWindow, NetworkWindow, USBWindow, ProcessWindow, ServiceWindow,
                        HistoryWindow, LaunchersWindow, ThemeSelector, DiskWindow, UpdatesWindow, HomebridgeWindow,
                        NetworkLocalWindow, PiholeWindow, AlertHistoryWindow, DisplayWindow, VpnWindow, OverviewWindow,
                        LedWindow, CameraWindow, ServicesManagerWindow, LogViewerWindow, ButtonManagerWindow, CrontabWindow,
                        HardwareInfoWindow, SSHWindow, WiFiWindow, ConfigEditorWindow, AudioWindow, WeatherWindow)
from ui.window_manager import WindowManager
from ui.window_lifecycle import WindowLifecycleManager
from ui.main_badges import BadgeManager
from ui.main_update_loop import UpdateLoop
from ui.main_system_actions import exit_application, restart_application
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow:
    """Ventana principal del dashboard"""

    def __init__(self, root, registry, update_interval=2000):
        self.root            = root
        self.registry        = registry
        self.update_interval = update_interval
        self.system_utils    = SystemUtils()

        self.system_monitor      = registry.get("system_monitor")
        self.fan_controller      = registry.get("fan_controller")
        self.fan_service         = registry.get("fan_service")
        self.data_service        = registry.get("data_service")
        self.network_monitor     = registry.get("network_monitor")
        self.disk_monitor        = registry.get("disk_monitor")
        self.process_monitor     = registry.get("process_monitor")
        self.service_monitor     = registry.get("service_monitor")
        self.update_monitor      = registry.get("update_monitor")
        self.cleanup_service     = registry.get("cleanup_service")
        self.homebridge_monitor  = registry.get("homebridge_monitor")
        self.network_scanner     = registry.get("network_scanner")
        self.pihole_monitor      = registry.get("pihole_monitor")
        self.alert_service       = registry.get("alert_service")
        self.display_service     = registry.get("display_service")
        self.vpn_monitor         = registry.get("vpn_monitor")
        self.led_service         = registry.get("led_service")
        self.hardware_monitor    = registry.get("hardware_monitor")
        self.audio_alert_service = registry.get("audio_alert_service")
        self.ssh_monitor         = registry.get("ssh_monitor")
        self.wifi_monitor        = registry.get("wifi_monitor")
        self.audio_service       = registry.get("audio_service")
        self.weather_service     = registry.get("weather_service")

        self._menu_btns   = {}
        self._active_tab  = UICfg.MENU_TABS[0][0]
        self._tab_buttons = {}

        logger.info(f"[MainWindow] Dashboard iniciado en {self.system_utils.get_hostname()}")

        self._create_ui()
        self._update_loop.start()

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _create_ui(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # ── Header ───────────────────────────────────────────────────────────
        header_bar = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'], height=56)
        header_bar.pack(fill="x", padx=5, pady=(5, 0))
        header_bar.pack_propagate(False)

        ctk.CTkLabel(
            header_bar,
            text=f"  {self.system_utils.get_hostname()}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="w",
        ).pack(side="left", padx=12)

        ctk.CTkLabel(
            header_bar,
            text="SISTEMA DE MONITOREO",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
            anchor="center",
        ).pack(side="left", expand=True)

        uptime_label = ctk.CTkLabel(
            header_bar,
            text=f"{Icons.UPTIME} --",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            anchor="e",
        )
        uptime_label.pack(side="right", padx=(0, 4))

        clock_label = ctk.CTkLabel(
            header_bar,
            text="00:00:00",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="e",
        )
        clock_label.pack(side="right", padx=12)

        ctk.CTkFrame(main_frame, fg_color=COLORS['border'], height=1,
                     corner_radius=0).pack(fill="x", padx=5, pady=(0, 4))

        # ── Zona scrollable (pestañas + botones + footer) ─────────────────────
        scroll_container = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        self._menu_canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        self._menu_canvas.pack(side="left", fill="both", expand=True)

        menu_scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=self._menu_canvas.yview, width=30)
        menu_scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(menu_scrollbar)
        self._menu_canvas.configure(yscrollcommand=menu_scrollbar.set)

        menu_inner = ctk.CTkFrame(self._menu_canvas, fg_color=COLORS['bg_medium'])
        self._menu_canvas.create_window(
            (0, 0), window=menu_inner, anchor="nw", width=DSI_WIDTH - 50)
        menu_inner.bind(
            "<Configure>",
            lambda e: self._menu_canvas.configure(
                scrollregion=self._menu_canvas.bbox("all")))

        # ── Pestañas con scroll horizontal ───────────────────────────────────
        _TAB_W, _TAB_H = 130, 44

        tab_wrapper = ctk.CTkFrame(menu_inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        tab_wrapper.pack(fill="x", padx=8, pady=(8, 0))

        tab_canvas = tk.Canvas(tab_wrapper, bg=COLORS['bg_dark'],
                               highlightthickness=0, height=_TAB_H + 8)
        tab_canvas.pack(fill="x", expand=True)

        tab_scrollbar = ctk.CTkScrollbar(
            tab_wrapper, orientation="horizontal",
            command=tab_canvas.xview, height=30)
        tab_scrollbar.pack(fill="x", padx=4, pady=(0, 4))
        StyleManager.style_scrollbar_ctk(tab_scrollbar)
        tab_canvas.configure(xscrollcommand=tab_scrollbar.set)

        tab_inner = ctk.CTkFrame(tab_canvas, fg_color=COLORS['bg_dark'])
        tab_canvas.create_window((0, 0), window=tab_inner, anchor="nw")
        tab_inner.bind("<Configure>",
                       lambda e: tab_canvas.configure(
                           scrollregion=tab_canvas.bbox("all")))

        for key, icon, label, _ in UICfg.MENU_TABS:
            btn = ctk.CTkButton(
                tab_inner,
                text=f"{icon}  {label}",
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                fg_color=COLORS['bg_dark'],
                text_color=COLORS['text_dim'],
                hover_color=COLORS['bg_light'],
                corner_radius=6,
                width=_TAB_W, height=_TAB_H,
                command=lambda k=key: self._switch_tab(k),
            )
            btn.pack(side="left", padx=4, pady=4)
            self._tab_buttons[key] = btn

        # ── Área de botones ───────────────────────────────────────────────────
        self._btn_area = ctk.CTkFrame(menu_inner, fg_color=COLORS['bg_medium'])
        self._btn_area.pack(fill="both", expand=True, padx=4, pady=4)

        # ── Footer ────────────────────────────────────────────────────────────
        footer = ctk.CTkFrame(menu_inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        footer.pack(fill="x", padx=8, pady=(4, 8))

        btn_gestor = make_futuristic_button(
            footer, BL.BOTONES, command=lambda: self._wlm.open("button_manager"),
            font_size=FONT_SIZES['small'], width=20, height=10)
        btn_gestor.pack(side="left", padx=8, pady=8, expand=True, fill="x")
        self._menu_btns[BL.BOTONES] = btn_gestor

        make_futuristic_button(
            footer, BL.REINICIAR, command=lambda: restart_application(self.root, self._update_loop),
            font_size=FONT_SIZES['small'], width=20, height=10
        ).pack(side="left", padx=4, pady=8, expand=True, fill="x")

        make_futuristic_button(
            footer, BL.SALIR, command=lambda: exit_application(self.root, self._update_loop),
            font_size=FONT_SIZES['small'], width=20, height=10
        ).pack(side="left", padx=(4, 8), pady=8, expand=True, fill="x")

        # ── Módulos de soporte ────────────────────────────────────────────────
        self._badge_mgr = BadgeManager(menu_btns=self._menu_btns)

        self._wlm = WindowLifecycleManager(
            on_btn_active=self._btn_active,
            on_btn_idle=self._btn_idle,
        )
        self._register_windows()
        self._buttons_meta = self._build_buttons_meta()

        self._wm = WindowManager(self.registry, self._menu_btns)
        self._wm.set_rerender_callback(lambda: self._switch_tab(self._active_tab))

        self._update_loop = UpdateLoop(
            root=self.root,
            badge_mgr=self._badge_mgr,
            monitors={
                "system_monitor":     self.system_monitor,
                "update_monitor":     self.update_monitor,
                "homebridge_monitor": self.homebridge_monitor,
                "pihole_monitor":     self.pihole_monitor,
                "vpn_monitor":        self.vpn_monitor,
                "service_monitor":    self.service_monitor,
            },
            update_interval=self.update_interval,
            clock_label=clock_label,
            uptime_label=uptime_label,
            weather_service=self.weather_service,
        )

        # ── Render inicial ────────────────────────────────────────────────────
        self._switch_tab(self._active_tab)

    # ── Registro de ventanas hijas ────────────────────────────────────────────

    def _register_windows(self):
        r    = self._wlm.register
        root = self.root

        r("hardware_info",        BL.HARDWARE_INFO,
            lambda: HardwareInfoWindow(root, self.system_monitor))
        r("fan_control",          BL.FAN_CONTROL,
            lambda: FanControlWindow(root, self.fan_controller, self.system_monitor,
                                     fan_service=self.fan_service),
            badge_keys=["temp_fan"])
        r("led_window",           BL.LED_RGB,
            lambda: LedWindow(root, self.led_service))
        r("monitor_window",       BL.MONITOR_PLACA,
            lambda: MonitorWindow(root, self.system_monitor, self.hardware_monitor),
            badge_keys=["temp_monitor", "cpu", "ram"])
        r("network_window",       BL.MONITOR_RED,
            lambda: NetworkWindow(root, network_monitor=self.network_monitor))
        r("usb_window",           BL.MONITOR_USB,
            lambda: USBWindow(root))
        r("disk_window",          BL.MONITOR_DISCO,
            lambda: DiskWindow(root, self.disk_monitor),
            badge_keys=["disk"])
        r("launchers",            BL.LANZADORES,
            lambda: LaunchersWindow(root))
        r("process_window",       BL.PROCESOS,
            lambda: ProcessWindow(root, self.process_monitor))
        r("service_window",       BL.SERVICIOS,
            lambda: ServiceWindow(root, self.service_monitor),
            badge_keys=["services"])
        r("services_manager",     BL.SERVICIOS_DASH,
            lambda: ServicesManagerWindow(root, registry=self.registry))
        r("crontab_window",       BL.CRONTAB,
            lambda: CrontabWindow(root))
        r("history_window",       BL.HISTORICO,
            lambda: HistoryWindow(root, self.cleanup_service))
        r("update_window",        BL.ACTUALIZACIONES,
            lambda: UpdatesWindow(root, self.update_monitor),
            badge_keys=["updates"])
        r("homebridge",           BL.HOMEBRIDGE,
            lambda: HomebridgeWindow(root, self.homebridge_monitor),
            badge_keys=["hb_offline", "hb_on", "hb_fault"])
        r("log_viewer",           BL.VISOR_LOGS,
            lambda: LogViewerWindow(root))
        r("network_local",        BL.RED_LOCAL,
            lambda: NetworkLocalWindow(root, network_scanner=self.network_scanner))
        r("pihole",               BL.PIHOLE,
            lambda: PiholeWindow(root, self.pihole_monitor),
            badge_keys=["pihole_offline"])
        r("vpn_window",           BL.VPN,
            lambda: VpnWindow(root, self.vpn_monitor),
            badge_keys=["vpn_offline"])
        r("alert_history",        BL.HISTORIAL_ALERTAS,
            lambda: AlertHistoryWindow(root, self.alert_service))
        r("display_window",       BL.BRILLO,
            lambda: DisplayWindow(root, self.display_service))
        r("overview",             BL.RESUMEN,
            lambda: OverviewWindow(root,
                system_monitor=self.system_monitor,
                service_monitor=self.service_monitor,
                pihole_monitor=self.pihole_monitor,
                network_monitor=self.network_monitor,
                disk_monitor=self.disk_monitor))
        r("camera_window",        BL.CAMARA,
            lambda: CameraWindow(root))
        r("theme_selector",       BL.TEMA,
            lambda: ThemeSelector(root))
        r("ssh_window",           BL.SSH,
            lambda: SSHWindow(root, self.ssh_monitor))
        r("wifi_window",          BL.WIFI,
            lambda: WiFiWindow(root, self.wifi_monitor))
        r("config_editor_window", BL.CONFIG,
            lambda: ConfigEditorWindow(root))
        r("audio_window",         BL.AUDIO,
            lambda: AudioWindow(root, self.audio_service))
        r("weather_window",       BL.CLIMA,
            lambda: WeatherWindow(root, self.weather_service),
            badge_keys=["weather_rain"])
        r("button_manager",       BL.BOTONES,
            lambda: ButtonManagerWindow(root,
                registry=self.registry, window_manager=self._wm))

    # ── Mapa de botones: label → (command, [badge_keys]) ─────────────────────

    def _build_buttons_meta(self):
        return {
            BL.HARDWARE_INFO:     (lambda: self._wlm.open("hardware_info"),        []),
            BL.FAN_CONTROL:       (lambda: self._wlm.open("fan_control"),          ["temp_fan"]),
            BL.LED_RGB:           (lambda: self._wlm.open("led_window"),           []),
            BL.MONITOR_PLACA:     (lambda: self._wlm.open("monitor_window"),       ["temp_monitor", "cpu", "ram"]),
            BL.MONITOR_RED:       (lambda: self._wlm.open("network_window"),       []),
            BL.MONITOR_USB:       (lambda: self._wlm.open("usb_window"),           []),
            BL.MONITOR_DISCO:     (lambda: self._wlm.open("disk_window"),          ["disk"]),
            BL.LANZADORES:        (lambda: self._wlm.open("launchers"),            []),
            BL.PROCESOS:          (lambda: self._wlm.open("process_window"),       []),
            BL.SERVICIOS:         (lambda: self._wlm.open("service_window"),       ["services"]),
            BL.SERVICIOS_DASH:    (lambda: self._wlm.open("services_manager"),     []),
            BL.CRONTAB:           (lambda: self._wlm.open("crontab_window"),       []),
            BL.HISTORICO:         (lambda: self._wlm.open("history_window"),       []),
            BL.ACTUALIZACIONES:   (lambda: self._wlm.open("update_window"),        ["updates"]),
            BL.HOMEBRIDGE:        (lambda: self._wlm.open("homebridge"),           ["hb_offline", "hb_on", "hb_fault"]),
            BL.VISOR_LOGS:        (lambda: self._wlm.open("log_viewer"),           []),
            BL.RED_LOCAL:         (lambda: self._wlm.open("network_local"),        []),
            BL.PIHOLE:            (lambda: self._wlm.open("pihole"),               ["pihole_offline"]),
            BL.VPN:               (lambda: self._wlm.open("vpn_window"),           ["vpn_offline"]),
            BL.HISTORIAL_ALERTAS: (lambda: self._wlm.open("alert_history"),        []),
            BL.BRILLO:            (lambda: self._wlm.open("display_window"),       []),
            BL.RESUMEN:           (lambda: self._wlm.open("overview"),             []),
            BL.CAMARA:            (lambda: self._wlm.open("camera_window"),        []),
            BL.TEMA:              (lambda: self._wlm.open("theme_selector"),       []),
            BL.SSH:               (lambda: self._wlm.open("ssh_window"),           []),
            BL.WIFI:              (lambda: self._wlm.open("wifi_window"),          []),
            BL.CONFIG:            (lambda: self._wlm.open("config_editor_window"), []),
            BL.AUDIO:             (lambda: self._wlm.open("audio_window"),         []),
            BL.CLIMA:             (lambda: self._wlm.open("weather_window"),       ["weather_rain"]),
        }

    # ── Cambio de pestaña ─────────────────────────────────────────────────────

    # Mapa inverso BL label → clave JSON para consultar ui_enabled
    _BL_TO_KEY = {v: k for k, v in {
        "hardware_info":        BL.HARDWARE_INFO,
        "fan_control":          BL.FAN_CONTROL,
        "led_window":           BL.LED_RGB,
        "monitor_window":       BL.MONITOR_PLACA,
        "network_window":       BL.MONITOR_RED,
        "usb_window":           BL.MONITOR_USB,
        "disk_window":          BL.MONITOR_DISCO,
        "launchers":            BL.LANZADORES,
        "process_window":       BL.PROCESOS,
        "service_window":       BL.SERVICIOS,
        "services_manager":     BL.SERVICIOS_DASH,
        "crontab_window":       BL.CRONTAB,
        "history_window":       BL.HISTORICO,
        "update_window":        BL.ACTUALIZACIONES,
        "homebridge":           BL.HOMEBRIDGE,
        "log_viewer":           BL.VISOR_LOGS,
        "network_local":        BL.RED_LOCAL,
        "pihole":               BL.PIHOLE,
        "vpn_window":           BL.VPN,
        "alert_history":        BL.HISTORIAL_ALERTAS,
        "display_window":       BL.BRILLO,
        "overview":             BL.RESUMEN,
        "camera_window":        BL.CAMARA,
        "theme_selector":       BL.TEMA,
        "ssh_window":           BL.SSH,
        "wifi_window":          BL.WIFI,
        "config_editor_window": BL.CONFIG,
        "audio_window":         BL.AUDIO,
        "weather_window":       BL.CLIMA,
    }.items()}

    def _switch_tab(self, key: str) -> None:
        self._active_tab = key

        for k, btn in self._tab_buttons.items():
            if k == key:
                btn.configure(fg_color=COLORS['primary'], text_color=COLORS['bg_dark'])
            else:
                btn.configure(fg_color=COLORS['bg_dark'], text_color=COLORS['text_dim'])

        for widget in self._btn_area.winfo_children():
            widget.destroy()

        bl_keys = next(
            (bl for tab_key, _, _, bl in UICfg.MENU_TABS if tab_key == key), [])

        columns  = UICfg.MENU_COLUMNS
        grid_pos = 0
        for bl_key in bl_keys:
            label = getattr(BL, bl_key, None)
            if label is None:
                logger.warning(f"[MainWindow] BL.{bl_key} no existe — omitido")
                continue
            json_key = self._BL_TO_KEY.get(label)
            if json_key is not None and not self.registry.ui_enabled(json_key):
                continue
            meta = self._buttons_meta.get(label)
            if meta is None:
                logger.warning(f"[MainWindow] Sin meta para '{label}' — omitido")
                continue
            command, badge_keys = meta
            btn = make_futuristic_button(
                self._btn_area, label, command=command,
                font_size=FONT_SIZES['large'], width=30, height=15)
            btn.grid(row=grid_pos // columns, column=grid_pos % columns,
                     padx=10, pady=10, sticky="nsew")
            self._menu_btns[label] = btn
            for j, bkey in enumerate(badge_keys):
                self._badge_mgr.create(btn, bkey, offset_index=j)
            grid_pos += 1

        for c in range(columns):
            self._btn_area.grid_columnconfigure(c, weight=1)

        self._btn_area.update_idletasks()
        self._menu_canvas.configure(scrollregion=self._menu_canvas.bbox("all"))

    # ── Estado de botones (usado por WindowLifecycleManager) ─────────────────

    def _btn_active(self, text_key: str) -> None:
        btn = self._menu_btns.get(text_key)
        if btn:
            try:
                btn.configure(fg_color=COLORS['bg_light'],
                              border_color=COLORS['primary'], border_width=2)
            except Exception:
                pass

    def _btn_idle(self, text_key: str) -> None:
        btn = self._menu_btns.get(text_key)
        if btn:
            try:
                btn.configure(fg_color=COLORS['bg_dark'],
                              border_color=COLORS['border'], border_width=1)
            except Exception:
                pass
</file>

</files>
