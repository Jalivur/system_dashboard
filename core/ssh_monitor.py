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
    """Ejecuta un comando y devuelve stdout o string vacío si falla."""
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
    Parsea la salida de `who` y devuelve lista de dicts.
    Formato típico:
        jalivur  pts/0        2026-03-04 10:22 (192.168.1.10)
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
    Parsea la salida de `last -n 50` y devuelve lista de dicts.
    Formato típico:
        jalivur  pts/0   192.168.1.10  Tue Mar  4 10:22   still logged in
        jalivur  pts/1   192.168.1.10  Mon Mar  3 21:10 - 21:45  (00:35)
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
    Servicio profesional de monitoreo de sesiones SSH activas e historial.

    Características:
    * Polling cada 30s de `who` (sesiones actuales) y `last -n 50` (historial reciente).
    * Parsing robusto de formatos variable con extracción de user/tty/IP/tiempos.
    * Thread daemon con lock para acceso concurrente seguro (thread-safe).
    * Métodos start/stop/is_running para ciclo de vida.
    * Getters optimizados: bloqueante y no-bloqueante (get_stats).
    * Logging apropiado para debug/error.

    Datos retornados:
    - sessions: list[dict{"user", "tty", "date", "time", "ip"}]
    - history: list[dict{"user", "tty", "ip", "time_info"}]
    """

    def __init__(self):
        """
        Inicializa el monitor SSH.

        Configura flags de estado, event stop, lock threading y estructuras de datos vacías.
        No inicia polling automáticamente — llamar start().
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
        Inicia el servicio de monitoreo en background (thread daemon).

        Primera poll inmediata, luego cada _POLL_INTERVAL segs.
        Idempotente: si ya corriendo, no hace nada.
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
        Detiene el servicio limpiamente.

        Setea evento stop, join thread (timeout 6s), limpia datos internos.
        Logging de detención.
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
        """Verifica si el servicio está corriendo."""
        return self._running

    # ── Loop interno ──────────────────────────────────────────────────────────

    def _loop(self):
        """
        Bucle principal del thread de monitoreo (privado).

        Poll inicial inmediato + wait(POLL_INTERVAL) entre iteraciones.
        Sale al detectar _stop_evt.
        """
        self._poll()   # primera lectura inmediata
        while not self._stop_evt.wait(_POLL_INTERVAL):
            self._poll()

    def _poll(self):
        """
        Realiza un ciclo de polling completo (privado).

        Ejecuta who/last, parsea, actualiza datos protegidos por lock.
        Timestamp de última actualización.
        Manejo de excepciones con log error.
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
        Retorna lista de sesiones SSH activas actuales (copia).

        Returns:
            list[dict]: [{"user": str, "tty": str, "date": str, "time": str, "ip": str}, ...]
        """
        with self._lock:
            return list(self._sessions)

    def get_history(self) -> list:
        """
        Retorna historial reciente de logins (últimas 50 entradas, copia).

        Returns:
            list[dict]: [{"user": str, "tty": str, "ip": str, "time_info": str}, ...]
        """
        with self._lock:
            return list(self._history)

    def get_last_update(self) -> str:
        """
        Retorna timestamp de última actualización (HH:MM:SS, copia).

        Returns:
            str: Formato "%H:%M:%S" o vacío si no actualizado.
        """
        with self._lock:
            return self._last_update

    def get_stats(self) -> dict:
        """
        Lectura no bloqueante de snapshot completo — si lock ocupado devuelve datos vacíos.

        Returns:
            dict: {"sessions": list, "history": list, "last_update": str}
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


