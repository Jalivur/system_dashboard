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
    SSH                 = "\U000F08C0"         # 
    WIFI                = "\U000F05A9"         #
    # Lanzadores
    NAS                 = "\U000F08F3"         # 󰣳
    MONTAR              = "\U000F0318"         # 󰌘
    DESMONTAR           = "\U000F0319"         # 󰌙
    UPDATE_SCRIPT       = "\U000F06B0"         # 󰚰
    SHUTDOWN            = "\U000F0159"         # 󰅙


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
