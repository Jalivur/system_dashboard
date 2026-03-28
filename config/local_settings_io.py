"""
config/local_settings_io.py

Lectura y escritura de config/local_settings.py de forma segura y sin
conflictos entre módulos que necesitan persistir claves distintas.

Formato del fichero:
  - Sección "# ── Parámetros" — variables sueltas (DSI_X, CPU_WARN, WEATHER_*)
  - Sección "# ── Iconos"     — asignaciones Icons.ATTR = "\\Uxxxxxxxx"

Cualquier módulo que necesite leer o escribir local_settings.py debe
importar este módulo y usar read() / write_params() / write_icons().
Nunca escribir directamente el fichero desde fuera de este módulo.
"""
import os
import re
import logging

logger = logging.getLogger(__name__)

_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "local_settings.py"
))


# ── Lectura ───────────────────────────────────────────────────────────────────

def read() -> tuple:
    """
    Lee el contenido de local_settings.py y devuelve los parámetros y overrides de iconos.

    Args:
        Ninguno

    Returns:
        tuple: (param_overrides, icon_overrides) donde param_overrides es un diccionario de variables sueltas y icon_overrides es un diccionario de overrides de iconos.

    Raises:
        Ninguno
    """
    param_overrides: dict = {}
    icon_overrides:  dict = {}

    if not os.path.exists(_PATH):
        return param_overrides, icon_overrides

    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            raw = f.read()

        # Extraer Icons.ATTR = "escape" antes de exec() para no perderlos
        for m in re.finditer(
            r'^Icons\.(\w+)\s*=\s*"(\\U[0-9A-Fa-f]{8})"', raw, re.MULTILINE
        ):
            icon_overrides[m.group(1)] = m.group(2)

        # exec para el resto de variables sueltas
        ns: dict = {}
        exec(raw, ns)  # noqa: S102
        for k, v in ns.items():
            if k.startswith("_") or k == "Icons":
                continue
            param_overrides[k] = v

    except Exception as e:
        logger.warning("[local_settings_io] Error leyendo: %s", e)

    return param_overrides, icon_overrides


# ── Escritura ─────────────────────────────────────────────────────────────────

def write(param_overrides: dict, icon_overrides: dict) -> None:
    """
    Escribe el contenido completo de local_settings.py con parámetros e iconos sobrescritos.

    Args:
        param_overrides (dict): Diccionario de parámetros a sobrescribir.
        icon_overrides (dict): Diccionario de iconos a sobrescribir.

    Returns:
        None

    Raises:
        Ninguna excepción específica.
    """
    lines = [
        '"""',
        "Overrides locales — generado automáticamente.",
        "No editar manualmente: usa la ventana de configuración del dashboard.",
        '"""',
        "",
    ]
    if param_overrides:
        lines.append("# ── Parámetros ───────────────────────────────────────────────────────────────")
        for key, val in param_overrides.items():
            lines.append(
                f'{key} = "{val}"' if isinstance(val, str)
                else f"{key} = {val!r}"
            )
        lines.append("")
    if icon_overrides:
        lines.append("# ── Iconos ───────────────────────────────────────────────────────────────────")
        lines.append("from config.settings import Icons")
        for attr, escape in icon_overrides.items():
            lines.append(f'Icons.{attr} = "{escape}"')
        lines.append("")

    os.makedirs(os.path.dirname(_PATH), exist_ok=True)
    with open(_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    logger.info("[local_settings_io] Escrito: %d params, %d iconos", len(param_overrides), len(icon_overrides))


def update_params(new_params: dict) -> None:
    """
    Actualiza los parámetros existentes con nuevos valores de manera segura.

    Args:
        new_params: Diccionario con los nuevos parámetros a aplicar.

    Returns:
        None

    Raises:
        None
    """
    params, icons = read()
    params.update(new_params)
    write(params, icons)


def write_params(param_overrides: dict) -> None:
    """
    Sobreescribe parámetros en un archivo preservando los iconos existentes.

    Args:
        param_overrides: Diccionario con parámetros a sobreescribir.

    Returns:
        None

    Raises:
        None
    """
    _, icons = read()
    write(param_overrides, icons)


def write_icons(icon_overrides: dict) -> None:
    """
    Sobreescribe los iconos de los parámetros existentes con los valores proporcionados.

    Args:
        icon_overrides (dict): Diccionario con los iconos a sobreescribir.

    Returns:
        None

    Raises:
        None
    """
    params, _ = read()
    write(params, icon_overrides)


def update_icons(new_icons: dict) -> None:
    """
    Actualiza los iconos existentes con nuevos iconos proporcionados.

    Args:
        new_icons: Un diccionario con los nuevos iconos que se van a agregar.

    Returns:
        None

    Raises:
        None
    """
    params, icons = read()
    icons.update(new_icons)
    write(params, icons)


def get_param(key: str, default=None):
    """
    Recuperar el valor de un parámetro específico desde la configuración de local_settings.py.

    Args:
        key (str): Clave del parámetro a recuperar.
        default: Valor predeterminado a retornar si el parámetro no existe.

    Returns:
        Valor del parámetro si existe, o el valor predeterminado si no existe.
    """
    params, _ = read()
    return params.get(key, default)
