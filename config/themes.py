"""
Sistema de temas personalizados
"""
import json
import os
from pathlib import Path
# ========================================
# TEMAS DISPONIBLES
# ========================================

THEMES = {
    "cyberpunk": {
        "name": "Cyberpunk (Original)",
        "colors": {
            "primary": "#00ffff",      # Cyan brillante
            "secondary": "#14611E",    # Verde oscuro ✓ OK
            "success": "#1ae313",      # Verde neón
            "warning": "#ffaa00",      # Naranja
            "danger": "#ff3333",       # Rojo
            "bg_dark": "#111111",      # Negro profundo
            "bg_medium": "#212121",    # Gris muy oscuro
            "bg_light": "#222222",     # Gris oscuro
            "text": "#ffffff",         # Blanco
            "text_dim": "#aaaaaa",     # Gris claro
            "border": "#00ffff"        # Cyan
        }
    },
    
    "matrix": {
        "name": "Matrix",
        "colors": {
            "primary": "#00ff00",      # Verde Matrix brillante
            "secondary": "#00ff88",    # Verde-cyan (bien diferente)
            "success": "#33ff33",      # Verde claro
            "warning": "#ffff00",      # Amarillo puro (muy diferente)
            "danger": "#ff0000",       # Rojo
            "bg_dark": "#000000",      # Negro puro
            "bg_medium": "#001a00",    # Negro verdoso sutil
            "bg_light": "#003300",     # Verde muy oscuro
            "text": "#00ff00",         # Verde brillante
            "text_dim": "#009900",     # Verde medio oscuro
            "border": "#00ff00"        # Verde brillante
        }
    },
    
    "sunset": {
        "name": "Sunset (Atardecer)",
        "colors": {
            "primary": "#ff6b35",      # Naranja cálido
            "secondary": "#f7931e",    # Naranja dorado ✓ CORREGIDO
            "success": "#ffd23f",      # Amarillo dorado
            "warning": "#ffd23f",      # Amarillo dorado
            "danger": "#d62828",       # Rojo oscuro
            "bg_dark": "#1a1423",      # Púrpura muy oscuro
            "bg_medium": "#2d1b3d",    # Púrpura oscuro
            "bg_light": "#3e2a47",     # Púrpura medio
            "text": "#f8f0e3",         # Beige claro
            "text_dim": "#c4b5a0",     # Beige oscuro
            "border": "#ff6b35"        # Naranja
        }
    },
    
    "ocean": {
        "name": "Ocean (Océano)",
        "colors": {
            "primary": "#00d4ff",      # Azul cielo
            "secondary": "#48dbfb",    # Azul claro ✓ CORREGIDO
            "success": "#1dd1a1",      # Verde agua
            "warning": "#feca57",      # Amarillo suave
            "danger": "#ee5a6f",       # Rosa coral
            "bg_dark": "#0c2233",      # Azul muy oscuro
            "bg_medium": "#163447",    # Azul oscuro
            "bg_light": "#1e4a5f",     # Azul medio
            "text": "#e0f7ff",         # Azul muy claro
            "text_dim": "#8899aa",     # Azul grisáceo
            "border": "#00d4ff"        # Azul cielo
        }
    },
    
    "dracula": {
        "name": "Dracula",
        "colors": {
            "primary": "#bd93f9",      # Púrpura pastel
            "secondary": "#ff79c6",    # Rosa ✓ CORREGIDO
            "success": "#50fa7b",      # Verde pastel
            "warning": "#f1fa8c",      # Amarillo pastel
            "danger": "#ff5555",       # Rojo pastel
            "bg_dark": "#1e1f29",      # Azul muy oscuro
            "bg_medium": "#282a36",    # Gris azulado
            "bg_light": "#44475a",     # Gris medio
            "text": "#f8f8f2",         # Blanco suave
            "text_dim": "#6272a4",     # Azul grisáceo
            "border": "#bd93f9"        # Púrpura
        }
    },
    
    "nord": {
        "name": "Nord (Nórdico)",
        "colors": {
            "primary": "#88c0d0",      # Azul hielo
            "secondary": "#5e81ac",    # Azul oscuro ✓ CORREGIDO
            "success": "#a3be8c",      # Verde suave
            "warning": "#ebcb8b",      # Amarillo suave
            "danger": "#bf616a",       # Rojo suave
            "bg_dark": "#1e2229",      # Negro azulado
            "bg_medium": "#2e3440",    # Gris polar
            "bg_light": "#3b4252",     # Gris claro
            "text": "#eceff4",         # Blanco nieve
            "text_dim": "#8899aa",     # Gris azulado
            "border": "#88c0d0"        # Azul hielo
        }
    },
    
    "tokyo_night": {
        "name": "Tokyo Night",
        "colors": {
            "primary": "#7aa2f7",      # Azul brillante
            "secondary": "#bb9af7",    # Púrpura ✓ CORREGIDO
            "success": "#9ece6a",      # Verde
            "warning": "#e0af68",      # Naranja suave
            "danger": "#f7768e",       # Rosa
            "bg_dark": "#16161e",      # Negro azulado
            "bg_medium": "#1a1b26",    # Azul noche
            "bg_light": "#24283b",     # Azul oscuro
            "text": "#c0caf5",         # Azul claro
            "text_dim": "#565f89",     # Azul oscuro
            "border": "#7aa2f7"        # Azul
        }
    },
    
    "monokai": {
        "name": "Monokai",
        "colors": {
            "primary": "#66d9ef",      # Azul claro
            "secondary": "#fd971f",    # Naranja ✓ CORREGIDO
            "success": "#a6e22e",      # Verde lima
            "warning": "#e6db74",      # Amarillo
            "danger": "#f92672",       # Rosa fucsia
            "bg_dark": "#1e1f1c",      # Negro verdoso
            "bg_medium": "#272822",    # Verde muy oscuro
            "bg_light": "#3e3d32",     # Verde grisáceo
            "text": "#f8f8f2",         # Blanco suave
            "text_dim": "#75715e",     # Gris verdoso
            "border": "#66d9ef"        # Azul claro
        }
    },
    
    "gruvbox": {
        "name": "Gruvbox",
        "colors": {
            "primary": "#fe8019",      # Naranja
            "secondary": "#d65d0e",    # Naranja oscuro ✓ CORREGIDO
            "success": "#b8bb26",      # Verde lima
            "warning": "#fabd2f",      # Amarillo
            "danger": "#fb4934",       # Rojo
            "bg_dark": "#1d2021",      # Negro marrón
            "bg_medium": "#282828",    # Gris oscuro
            "bg_light": "#3c3836",     # Gris medio
            "text": "#ebdbb2",         # Beige claro
            "text_dim": "#a89984",     # Beige oscuro
            "border": "#fe8019"        # Naranja
        }
    },
    
    "solarized_dark": {
        "name": "Solarized Dark",
        "colors": {
            "primary": "#268bd2",      # Azul
            "secondary": "#2aa198",    # Cyan ✓ CORREGIDO
            "success": "#859900",      # Verde oliva
            "warning": "#b58900",      # Amarillo oscuro
            "danger": "#dc322f",       # Rojo
            "bg_dark": "#002b36",      # Azul noche
            "bg_medium": "#073642",    # Azul oscuro
            "bg_light": "#586e75",     # Gris azulado
            "text": "#fdf6e3",         # Beige muy claro
            "text_dim": "#839496",     # Gris azulado
            "border": "#268bd2"        # Azul
        }
    },
    
    "one_dark": {
        "name": "One Dark",
        "colors": {
            "primary": "#61afef",      # Azul claro
            "secondary": "#56b6c2",    # Cyan ✓ CORREGIDO
            "success": "#98c379",      # Verde
            "warning": "#e5c07b",      # Amarillo
            "danger": "#e06c75",       # Rojo suave
            "bg_dark": "#1e2127",      # Negro azulado
            "bg_medium": "#282c34",    # Gris oscuro
            "bg_light": "#3e4451",     # Gris medio
            "text": "#abb2bf",         # Gris claro
            "text_dim": "#5c6370",     # Gris oscuro
            "border": "#61afef"        # Azul
        }
    },
    
    "synthwave": {
        "name": "Synthwave 84",
        "colors": {
            "primary": "#f92aad",      # Rosa neón
            "secondary": "#fe4450",    # Rojo neón ✓ CORREGIDO
            "success": "#72f1b8",      # Verde neón
            "warning": "#fede5d",      # Amarillo neón
            "danger": "#fe4450",       # Rojo neón
            "bg_dark": "#0e0b16",      # Negro púrpura
            "bg_medium": "#241734",    # Púrpura oscuro
            "bg_light": "#2d1b3d",     # Púrpura medio
            "text": "#ffffff",         # Blanco
            "text_dim": "#ff7edb",     # Rosa claro
            "border": "#f92aad"        # Rosa neón
        }
    },
    
    "github_dark": {
        "name": "GitHub Dark",
        "colors": {
            "primary": "#58a6ff",      # Azul GitHub
            "secondary": "#1f6feb",    # Azul oscuro ✓ CORREGIDO
            "success": "#3fb950",      # Verde
            "warning": "#d29922",      # Amarillo
            "danger": "#f85149",       # Rojo
            "bg_dark": "#0d1117",      # Negro
            "bg_medium": "#161b22",    # Gris muy oscuro
            "bg_light": "#21262d",     # Gris oscuro
            "text": "#c9d1d9",         # Gris claro
            "text_dim": "#8b949e",     # Gris medio
            "border": "#58a6ff"        # Azul
        }
    },
    
    "material": {
        "name": "Material Dark",
        "colors": {
            "primary": "#82aaff",      # Azul material
            "secondary": "#c792ea",    # Púrpura ✓ CORREGIDO
            "success": "#c3e88d",      # Verde claro
            "warning": "#ffcb6b",      # Amarillo
            "danger": "#f07178",       # Rojo suave
            "bg_dark": "#0f111a",      # Negro azulado
            "bg_medium": "#1e2029",    # Gris oscuro
            "bg_light": "#292d3e",     # Gris azulado
            "text": "#eeffff",         # Blanco azulado
            "text_dim": "#546e7a",     # Gris azulado
            "border": "#82aaff"        # Azul
        }
    },
    
    "ayu_dark": {
        "name": "Ayu Dark",
        "colors": {
            "primary": "#59c2ff",      # Azul cielo
            "secondary": "#39bae6",    # Azul claro ✓ CORREGIDO
            "success": "#aad94c",      # Verde lima
            "warning": "#ffb454",      # Naranja
            "danger": "#f07178",       # Rosa
            "bg_dark": "#0a0e14",      # Negro azulado
            "bg_medium": "#0d1017",    # Negro
            "bg_light": "#1c2128",     # Gris muy oscuro
            "text": "#b3b1ad",         # Gris claro
            "text_dim": "#626a73",     # Gris oscuro
            "border": "#59c2ff"        # Azul
        }
    }
}

# Tema por defecto
DEFAULT_THEME = "cyberpunk"

# ========================================
# FUNCIONES DE GESTIÓN DE TEMAS
# ========================================

def get_theme(theme_name: str) -> dict:
    """
    Recuperación de un tema mediante su nombre.

    Args:
        theme_name (str): Nombre del tema a recuperar.

    Returns:
        dict: Diccionario con los colores asociados al tema.

    Raises:
        KeyError: Si el tema por defecto no está configurado.
    """
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])


def get_available_themes() -> list:
    """
    Obtiene una lista de temas disponibles.

    Returns:
        list: Lista de tuplas que contienen el identificador y el nombre descriptivo de cada tema.
    """
    return [(key, theme["name"]) for key, theme in THEMES.items()]


def get_theme_colors(theme_name: str) -> dict:
    """
    Recupera los colores asociados a un tema específico.

    Args:
        theme_name (str): Nombre del tema del que obtener los colores.

    Returns:
        dict: Diccionario que contiene los colores del tema.

    Raises:
        Exception: Si el tema no existe o no tiene colores definidos.
    """
    theme = get_theme(theme_name)
    return theme["colors"]


# ========================================
# PREVIEW DE TEMAS (Para mostrar al usuario)
# ========================================

def get_theme_preview() -> str:
    """
    Obtiene una vista previa en texto de todos los temas disponibles.

    Returns:
        str: Cadena con la lista de temas y sus colores principales.

    Raises:
        None
    """
    preview = "TEMAS DISPONIBLES:\n\n"
    
    for theme_id, theme_data in THEMES.items():
        colors = theme_data["colors"]
        preview += f"• {theme_data['name']} ({theme_id})\n"
        preview += f"  Color principal: {colors['primary']}\n"
        preview += f"  Fondo: {colors['bg_dark']}\n"
        preview += f"  Texto: {colors['text']}\n\n"
    
    return preview


# ========================================
# CREAR TEMA PERSONALIZADO
# ========================================

def create_custom_theme(name: str, colors: dict) -> dict:
    """
    Crea un tema personalizado con un nombre descriptivo y colores específicos.

    Args:
        name (str): Nombre descriptivo del tema.
        colors (dict): Diccionario con los colores personalizados.

    Returns:
        dict: Diccionario del tema creado.

    Raises:
        ValueError: Si falta algún color requerido en el tema personalizado.
    """
    # Validar que tenga todos los colores necesarios
    required_keys = ["primary", "secondary", "success", "warning", "danger",
                     "bg_dark", "bg_medium", "bg_light", "text", "border"]
    
    for key in required_keys:
        if key not in colors:
            raise ValueError(f"Falta el color '{key}' en el tema personalizado")
    
    return {
        "name": name,
        "colors": colors
    }


# ========================================
# GUARDAR/CARGAR TEMA SELECCIONADO
# ========================================


THEME_CONFIG_FILE = Path(__file__).parent.parent / "data" / "theme_config.json"


def save_selected_theme(theme_name: str):
    """
    Guarda el tema seleccionado en un archivo de configuración.

    Args:
        theme_name (str): Nombre del tema a guardar.

    Returns:
        None

    Raises:
        None
    """
    # Asegurar que el directorio existe
    THEME_CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    config = {"selected_theme": theme_name}
    
    tmp_file = str(THEME_CONFIG_FILE) + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(config, f, indent=2)
    os.replace(tmp_file, THEME_CONFIG_FILE)


def load_selected_theme() -> str:
    """
    Carga el tema seleccionado desde archivo de configuración.

    Args:
        Ninguno

    Returns:
        str: Nombre del tema seleccionado o el tema predeterminado.

    Raises:
        Ninguna excepción relevante, se maneja internamente.
    """
    try:
        with open(THEME_CONFIG_FILE) as f:
            config = json.load(f)
            theme = config.get("selected_theme", DEFAULT_THEME)
            
            # Verificar que el tema existe
            if theme in THEMES:
                return theme
            else:
                return DEFAULT_THEME
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_THEME
