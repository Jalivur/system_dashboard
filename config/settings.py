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
    GPIO                = "\U000f0335"          # 󰌵  nf-md-integrated_circuit_chip (alias I2C visual)

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
    I2C                 = "\U000F0335"          # 󰌵  nf-md-integrated_circuit_chip

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
                "I2C",
                "GPIO",
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
