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
    Lee local_settings.py y devuelve (param_overrides, icon_overrides).

      param_overrides : dict  {str: any}          — variables sueltas
      icon_overrides  : dict  {str: str}           — {ATTR: "\\Uxxxxxxxx"}
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
    Escribe local_settings.py completo con ambas secciones.
    Sobrescribe el fichero — llamar siempre con el estado completo.
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
    Merge seguro: lee el estado actual, aplica new_params encima y escribe.
    Los iconos y el resto de parámetros existentes se conservan intactos.
    """
    params, icons = read()
    params.update(new_params)
    write(params, icons)


def write_params(param_overrides: dict) -> None:
    """
    Escribe solo parámetros, preservando los iconos existentes.
    """
    _, icons = read()
    write(param_overrides, icons)


def write_icons(icon_overrides: dict) -> None:
    """
    Escribe solo iconos, preservando los parámetros existentes.
    """
    params, _ = read()
    write(params, icon_overrides)


def update_icons(new_icons: dict) -> None:
    """
    Merge seguro: lee el estado actual, aplica new_icons encima y escribe.
    Los parámetros y el resto de iconos existentes se conservan intactos.
    """
    params, icons = read()
    icons.update(new_icons)
    write(params, icons)


def get_param(key: str, default=None):
    """Lee un único parámetro de local_settings.py sin importar el módulo."""
    params, _ = read()
    return params.get(key, default)
