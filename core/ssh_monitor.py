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
        logger.warning(f"[SSHMonitor] Error ejecutando {cmd}: {e}")
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
    """Servicio de monitoreo de sesiones SSH."""

    def __init__(self):
        self._running  = False
        self._stop_evt = threading.Event()
        self._lock     = threading.Lock()
        self._thread   = None

        self._sessions: list = []   # who
        self._history:  list = []   # last
        self._last_update: str = ""

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self):
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
        self._running = False
        self._stop_evt.set()
        logger.info("[SSHMonitor] Servicio detenido")

    # ── Loop interno ──────────────────────────────────────────────────────────

    def _loop(self):
        self._poll()   # primera lectura inmediata
        while not self._stop_evt.wait(_POLL_INTERVAL):
            self._poll()

    def _poll(self):
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
            logger.error(f"[SSHMonitor] Error en poll: {e}")

    # ── Acceso a datos ────────────────────────────────────────────────────────

    def get_sessions(self) -> list:
        with self._lock:
            return list(self._sessions)

    def get_history(self) -> list:
        with self._lock:
            return list(self._history)

    def get_last_update(self) -> str:
        with self._lock:
            return self._last_update

    def get_stats(self) -> dict:
        """Lectura no bloqueante — si el lock está cogido devuelve snapshot vacío."""
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
