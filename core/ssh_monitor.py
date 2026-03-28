"""
Monitor de sesiones SSH.
Recopila sesiones activas via `who` e historial via `last`.
Corre en thread daemon con refresco cada 30 segundos.
"""
import subprocess
import threading
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

_POLL_INTERVAL = 30   # segundos
_HISTORY_LINES = 50   # entradas de `last`


def _run(cmd: list) -> str:
    """
    Ejecuta un comando y devuelve la salida estándar o una cadena vacía si falla.

    Args:
        cmd (list): Lista de comando y argumentos a ejecutar.

    Returns:
        str: Salida estándar del comando ejecutado.

    Raises:
        Exception: Si ocurre un error durante la ejecución del comando.
    """
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        logger.warning("[SSHMonitor] Error ejecutando %s: %s", cmd, e)
        return ""


def _parse_who(raw: str) -> list:
    """
    Parsea la salida de `who` y devuelve una lista de diccionarios con información de sesión.

    Args:
        raw (str): Salida de `who` a parsear.

    Returns:
        list: Lista de diccionarios con claves "user", "tty", "date", "time" e "ip".

    Raises:
        Ninguna excepción específica.
    """
    sessions = []
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        user = parts[0]
        tty  = parts[1]
        # Fecha y hora pueden estar en partes[2] y partes[3]
        date = parts[2] if len(parts) > 2 else ""
        time = parts[3] if len(parts) > 3 else ""
        # IP origen entre paréntesis al final
        ip = ""
        for part in parts[4:]:
            if part.startswith("(") and part.endswith(")"):
                ip = part[1:-1]
                break
        sessions.append({
            "user": user,
            "tty":  tty,
            "date": date,
            "time": time,
            "ip":   ip,
        })
    return sessions


def _parse_last(raw: str) -> list:
    """
    Parsea la salida de `last -n 50` y devuelve una lista de diccionarios con información de sesión.

    Args:
        raw (str): La salida de `last -n 50` como cadena de texto.

    Returns:
        list: Lista de diccionarios con claves "user", "tty", "ip" y "time_info".

    Raises:
        Ninguna excepción es lanzada explícitamente.
    """
    entries = []
    for line in raw.splitlines():
        # Ignorar líneas vacías y la línea de resumen final
        if not line.strip() or line.startswith("wtmp begins"):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        user   = parts[0]
        tty    = parts[1]
        # La IP puede no estar (consola local)
        ip     = parts[2] if not parts[2].startswith(("Mon","Tue","Wed","Thu","Fri","Sat","Sun")) else ""
        # El resto de la línea como info de tiempo
        time_info = " ".join(parts[3:]) if ip else " ".join(parts[2:])
        entries.append({
            "user":      user,
            "tty":       tty,
            "ip":        ip,
            "time_info": time_info,
        })
    return entries


class SSHMonitor:
    """
    Servicio de monitoreo de sesiones SSH activas e historial.

    Args: Ninguno

    Returns: Ninguno

    Raises: Ninguno

    Características:
    * Inicializa flags de estado, evento de parada, bloqueo de threading y estructuras de datos vacías.
    * No inicia el monitoreo automáticamente, requiere llamada explícita a start().
    """

    def __init__(self):
        """
        Inicializa el monitor SSH.

        Configura flags de estado, evento de parada, bloqueo de threading y estructuras de datos vacías.
        No inicia el monitoreo automáticamente, requiere llamada explícita a start().

        Args: Ninguno

        Returns: Ninguno

        Raises: Ninguno
        """
        self._running  = False
        self._stop_evt = threading.Event()
        self._lock     = threading.Lock()
        self._thread   = None

        self._sessions: list = []   # who
        self._history:  list = []   # last
        self._last_update: str = ""

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self):
        """
        Inicia el servicio de monitoreo en segundo plano.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno

        Nota: Si el servicio ya está ejecutándose, este método no tiene efecto.
        El servicio se ejecuta en un hilo daemon y realiza una primera verificación inmediata,
        posteriormente ejecuta verificaciones cada intervalo configurado.
        """
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="SSHMonitor"
        )
        self._thread.start()
        logger.info("[SSHMonitor] Servicio iniciado")

    def stop(self):
        """
        Detiene el servicio de monitoreo SSH de manera limpia.

        Args: Ninguno

        Returns: Ninguno

        Raises: Ninguno
        """
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=6)
        with self._lock:
            self._sessions=[]
            self._history=[]
            self._last_update=""
        logger.info("[SSHMonitor] Servicio detenido")
        
    def is_running(self) -> bool:
        """
        Verifica si el servicio de monitoreo SSH está en ejecución.

        Args:
            None

        Returns:
            bool: True si el servicio está corriendo, False en caso contrario.

        Raises:
            None
        """
        return self._running

    # ── Loop interno ──────────────────────────────────────────────────────────

    def _loop(self):
        """
        Ejecuta el bucle principal del thread de monitoreo.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._poll()   # primera lectura inmediata
        while not self._stop_evt.wait(_POLL_INTERVAL):
            self._poll()

    def _poll(self):
        """
        Realiza un ciclo de polling completo para obtener información de sesiones activas y historial.

        Args: Ninguno

        Returns: Ninguno

        Raises: Exception - Si ocurre un error durante la ejecución, se registra en el log de errores.
        """
        try:
            who_raw  = _run(["who"])
            last_raw = _run(["last", "-n", str(_HISTORY_LINES), "--time-format", "iso"])

            sessions = _parse_who(who_raw)
            history  = _parse_last(last_raw)
            ts       = datetime.now().strftime("%H:%M:%S")

            with self._lock:
                self._sessions     = sessions
                self._history      = history
                self._last_update  = ts

            """logger.debug(
                f"[SSHMonitor] Poll: {len(sessions)} sesiones activas, "
                f"{len(history)} entradas historial"
            )"""
        except Exception as e:
            logger.error("[SSHMonitor] Error en poll: %s", e)

    # ── Acceso a datos ────────────────────────────────────────────────────────

    def get_sessions(self) -> list:
        """
        Retorna una lista de sesiones SSH activas actuales.

        Args:
            Ninguno

        Returns:
            list[dict]: Lista de diccionarios con información de sesiones SSH, 
                         cada diccionario contiene: "user", "tty", "date", "time", "ip".

        Raises:
            Ninguno
        """
        with self._lock:
            return list(self._sessions)

    def get_history(self) -> list:
        """
        Retorna el historial reciente de logins.

        Args:
            Ninguno

        Returns:
            list[dict]: Lista de diccionarios con información de los últimos logins. 
                         Cada diccionario contiene: "user" (str), "tty" (str), "ip" (str) y "time_info" (str).

        Raises:
            Ninguno
        """
        with self._lock:
            return list(self._history)

    def get_last_update(self) -> str:
        """
        Retorna el timestamp de la última actualización en formato HH:MM:SS.

        Args:
            Ninguno

        Returns:
            str: Fecha y hora de última actualización en formato "%H:%M:%S" o cadena vacía si no se ha actualizado.

        Raises:
            Ninguno
        """
        with self._lock:
            return self._last_update

    def get_stats(self) -> dict:
        """
        Obtiene un snapshot completo de las estadísticas actuales del monitor SSH.

        Args:
            Ninguno

        Returns:
            dict: Un diccionario con las estadísticas, incluyendo "sessions", "history" y "last_update".

        Raises:
            Ninguno

        Notas: Si el bloqueo interno está ocupado, devuelve un diccionario vacío.
        """
        acquired = self._lock.acquire(blocking=False)
        if not acquired:
            return {"sessions": [], "history": [], "last_update": ""}
        try:
            return {
                "sessions":    list(self._sessions),
                "history":     list(self._history),
                "last_update": self._last_update,
            }
        finally:
            self._lock.release()


