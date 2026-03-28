"""
Servicio de gestión de crontab.
Encapsula la lectura, escritura y parseo del crontab del sistema.
"""
import subprocess
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Tablas de datos (no son lógica de UI) ─────────────────────────────────────

CRON_DESCRIPTIONS = {
    "* * * * *":    "Cada minuto",
    "*/5 * * * *":  "Cada 5 minutos",
    "*/10 * * * *": "Cada 10 minutos",
    "*/15 * * * *": "Cada 15 minutos",
    "*/30 * * * *": "Cada 30 minutos",
    "0 * * * *":    "Cada hora (en punto)",
    "0 */2 * * *":  "Cada 2 horas",
    "0 */6 * * *":  "Cada 6 horas",
    "0 */12 * * *": "Cada 12 horas",
    "0 0 * * *":    "Cada día a medianoche",
    "0 8 * * *":    "Cada día a las 8:00",
    "0 12 * * *":   "Cada día a las 12:00",
    "0 20 * * *":   "Cada día a las 20:00",
    "0 0 * * 0":    "Cada domingo a medianoche",
    "0 0 * * 1":    "Cada lunes a medianoche",
    "0 0 1 * *":    "El día 1 de cada mes",
    "@reboot":      "Al arrancar el sistema",
    "@hourly":      "Cada hora",
    "@daily":       "Cada día",
    "@weekly":      "Cada semana",
    "@monthly":     "Cada mes",
    "@yearly":      "Cada año",
}

QUICK_SCHEDULES = [
    ("Cada minuto", "*",       "*", "*", "*", "*"),
    ("Cada hora",   "0",       "*", "*", "*", "*"),
    ("Cada día 0h", "0",       "0", "*", "*", "*"),
    ("Cada día 8h", "0",       "8", "*", "*", "*"),
    ("Cada semana", "0",       "0", "*", "*", "0"),
    ("Al arrancar", "@reboot", "",  "",  "",  "" ),
]


# ── Funciones de negocio ──────────────────────────────────────────────────────

def describe_cron(minute: str, hour: str, day: str, month: str, weekday: str) -> str:
    """
    Convierte una expresión cron a texto legible en español.

    Args:
        minute (str): Minuto de la expresión cron.
        hour (str): Hora de la expresión cron.
        day (str): Día del mes de la expresión cron.
        month (str): Mes de la expresión cron.
        weekday (str): Día de la semana de la expresión cron.

    Returns:
        str: Descripción legible de la expresión cron.

    Raises:
        Ninguna excepción relevante.
    """
    if minute.startswith("@"):
        return CRON_DESCRIPTIONS.get(minute, minute)
    expr = f"{minute} {hour} {day} {month} {weekday}"
    if expr in CRON_DESCRIPTIONS:
        return CRON_DESCRIPTIONS[expr]
    parts = []
    if minute  != "*": parts.append(f"min={minute}")
    if hour    != "*": parts.append(f"hora={hour}")
    if day     != "*": parts.append(f"día={day}")
    if month   != "*": parts.append(f"mes={month}")
    if weekday != "*": parts.append(f"sem={weekday}")
    return ", ".join(parts) if parts else "Expresión personalizada"


def read_crontab(user: str) -> list[str]:
    """
    Lee las líneas del crontab del usuario indicado.

    Args:
        user: nombre de usuario. Utiliza "root" para leer el crontab de root mediante sudo.

    Returns:
        Lista de líneas raw del crontab. Si no hay crontab o hay error, devuelve una lista vacía.

    Raises:
        Exception: si ocurre un error al leer el crontab.
    """
    try:
        if user == "root":
            result = subprocess.run(
                ["sudo", "crontab", "-l", "-u", "root"],
                capture_output=True, text=True, timeout=5
            )
        else:
            result = subprocess.run(
                ["crontab", "-l"],
                capture_output=True, text=True, timeout=5
            )
        if result.returncode == 0:
            return result.stdout.splitlines()
        if "no crontab" in result.stderr.lower():
            return []
        logger.warning("[CrontabService] crontab -l stderr: %s", result.stderr.strip())
        return []
    except Exception as e:
        logger.error("[CrontabService] Error leyendo crontab: %s", e)
        return []


def write_crontab(user: str, lines: list[str]) -> tuple[bool, str]:
    """
    Escribe las líneas dadas como el nuevo crontab del usuario especificado.

    Args:
        user: nombre de usuario cuyo crontab se actualizará
        lines: lista de líneas a escribir en el crontab

    Returns:
        Tupla con un booleano indicando éxito y un mensaje descriptivo

    Raises:
        Excepción en caso de error al escribir el crontab
    """
    content = "\n".join(lines) + "\n"
    try:
        if user == "root":
            proc = subprocess.run(
                ["sudo", "crontab", "-u", "root", "-"],
                input=content, capture_output=True, text=True, timeout=5
            )
        else:
            proc = subprocess.run(
                ["crontab", "-"],
                input=content, capture_output=True, text=True, timeout=5
            )
        if proc.returncode == 0:
            logger.info("[CrontabService] Crontab escrito para usuario '%s'", user)
            return True, "Crontab guardado correctamente."
        return False, f"Error: {proc.stderr.strip()}"
    except Exception as e:
        logger.error("[CrontabService] Error escribiendo crontab: %s", e)
        return False, f"Excepción: {e}"


def parse_line(line: str) -> dict | None:
    """
    Parsea una línea de crontab a un diccionario.

    Args:
        line (str): La línea de crontab a parsear.

    Returns:
        dict | None: Un diccionario con la información de la línea de crontab o None si la línea es inválida.

    Raises:
        No se lanzan excepciones explícitas, pero puede retornar None si la línea es vacía, comentario o malformada.
    """
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None

    if stripped.startswith("@"):
        parts   = stripped.split(None, 1)
        special = parts[0]
        command = parts[1] if len(parts) > 1 else ""
        return {
            "special": special,
            "minute":  special,
            "hour":    "",
            "day":     "",
            "month":   "",
            "weekday": "",
            "command": command,
            "raw":     line,
        }

    parts = stripped.split(None, 5)
    if len(parts) < 6:
        return None

    return {
        "special": None,
        "minute":  parts[0],
        "hour":    parts[1],
        "day":     parts[2],
        "month":   parts[3],
        "weekday": parts[4],
        "command": parts[5],
        "raw":     line,
    }


def parse_crontab(lines: list[str]) -> list[dict]:
    """
    Parsea una lista de líneas crontab y devuelve las entradas válidas.

    Args:
        lines: Lista de líneas crontab en formato raw.

    Returns:
        Lista de dicts, cada uno representando una entrada crontab válida.

    Raises:
        None
    """
    return [entry for line in lines if (entry := parse_line(line)) is not None]


def build_line(minute: str, hour: str, day: str, month: str,
               weekday: str, command: str) -> str:
    """
    Construye una línea de crontab a partir de sus campos.

    Args:
        minute (str): Minuto de la línea de crontab.
        hour (str): Hora de la línea de crontab.
        day (str): Día del mes de la línea de crontab.
        month (str): Mes de la línea de crontab.
        weekday (str): Día de la semana de la línea de crontab.
        command (str): Comando a ejecutar.

    Returns:
        str: La línea de crontab construida.
    """
    if minute.startswith("@"):
        return f"{minute} {command}"
    return f"{minute} {hour} {day} {month} {weekday} {command}"
