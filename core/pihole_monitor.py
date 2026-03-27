"""
Monitor de Pi-hole v6.
Sondea la API REST de Pi-hole v6 cada POLL_INTERVAL_S segundos.
Credenciales leídas desde .env: PIHOLE_HOST, PIHOLE_PORT, PIHOLE_PASSWORD.

Sin dependencias nuevas — usa urllib de la stdlib.
"""
import json
import os
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Carga de .env ─────────────────────────────────────────────────────────────
def _load_env():
    """
    Carga las variables de entorno desde el archivo .env del proyecto.

    Busca el archivo .env en el directorio padre del módulo actual.
    Intenta usar python-dotenv si está disponible; si no, realiza
    el parsing manual del archivo línea por línea.
    """
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=False)
    except ImportError:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value

_load_env()

PIHOLE_HOST     = os.environ.get("PIHOLE_HOST",     "")
PIHOLE_PORT     = int(os.environ.get("PIHOLE_PORT", "80"))
PIHOLE_PASSWORD = os.environ.get("PIHOLE_PASSWORD", "")

POLL_INTERVAL_S  = 60
REQUEST_TIMEOUT  = 5
SESSION_VALIDITY = 1800  # segundos — renovar antes de que expire

_EMPTY_STATS: Dict = {
    "status":          "unknown",
    "queries_today":   0,
    "blocked_today":   0,
    "percent_blocked": 0.0,
    "domains_blocked": 0,
    "unique_clients":  0,
    "reachable":       False,
}


class PiholeMonitor:
    """
    Monitor de Pi-hole v6 con sondeo en background.
    Autenticación por sesión (sid) con renovación automática antes de expirar.
    """

    def __init__(self):
        """
        Inicializa el monitor de Pi-hole con sus configuraciones y locks.

        Configura las estadísticas iniciales, los locks para thread-safety,
        y verifica si PIHOLE_HOST está configurado en las variables de entorno.
        Si no está configurado, el monitor permanece desactivado.
        """
        self._stats: Dict       = dict(_EMPTY_STATS)
        self._sid: Optional[str] = None
        self._sid_obtained: Optional[float] = None  # timestamp de cuando se obtuvo
        self._stats_lock        = threading.Lock()
        self._sid_lock          = threading.Lock()
        self._running           = False
        self._stop_evt          = threading.Event()
        self._thread: Optional[threading.Thread] = None

        if not PIHOLE_HOST:
            logger.warning(
                "[PiholeMonitor] PIHOLE_HOST no configurado en .env — monitor desactivado"
            )
        else:
            logger.info(
                "[PiholeMonitor] Inicializado — http://%s:%d (v6)", PIHOLE_HOST, PIHOLE_PORT
            )

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Inicia el monitor de Pi-hole en un thread daemon.

        No hace nada si ya está corriendo o si PIHOLE_HOST no está configurado.
        """
        if self._running or not PIHOLE_HOST:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="PiholePoll")
        self._thread.start()
        logger.info("[PiholeMonitor] Sondeo iniciado (cada %ds)", POLL_INTERVAL_S)

    def stop(self) -> None:
        """
        Detiene el monitor de Pi-hole de forma ordenada.

        Señaliza la parada al thread de sondeo, espera a que termine,
        cierra la sesión en Pi-hole y limpia las estadísticas en caché.
        """
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=REQUEST_TIMEOUT + 1)
        self._logout()
        # ── limpiar caché ──
        with self._stats_lock:
            self._stats = dict(_EMPTY_STATS)
        logger.info("[PiholeMonitor] Sondeo detenido")
    
    def is_running(self) -> bool:
        """
        Estado del monitor de Pi-hole.

        Returns:
            bool: True si el thread de sondeo está activo.
        """
        return self._running
    
    def fetch_now(self) -> None:
        """
        Fuerza sondeo inmediato de Pi-hole en thread separado (non-blocking).

        No bloquea el caller.
        """
        if not self._running:
            return
        threading.Thread(target=self._fetch, daemon=True, name='PiholeFetchNow').start()

    def _poll_loop(self) -> None:
        """
        Bucle principal del thread daemon de sondeo periódico.
        """
        while self._running:
            try:
                self._fetch()
            except Exception as e:
                logger.error("[PiholeMonitor] Error en poll_loop: %s", e)
            self._stop_evt.wait(timeout=POLL_INTERVAL_S)
            if self._stop_evt.is_set():
                break

    # ── Autenticación ─────────────────────────────────────────────────────────

    def _authenticate(self) -> bool:
        """Obtiene un sid de sesión. Devuelve True si tiene éxito."""
        if not PIHOLE_PASSWORD:
            # Sin contraseña — Pi-hole puede permitir acceso anónimo
            logger.debug("[PiholeMonitor] Sin contraseña configurada — intentando sin auth")
            return True

        payload = json.dumps({"password": PIHOLE_PASSWORD}).encode("utf-8")
        req = urllib.request.Request(
            f"http://{PIHOLE_HOST}:{PIHOLE_PORT}/api/auth",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                sid = data.get("session", {}).get("sid")
                if sid:
                    with self._sid_lock:
                        self._sid         = sid
                        self._sid_obtained = time.time()
                    logger.info("[PiholeMonitor] Autenticación correcta (sid obtenido)")
                    return True
                logger.warning("[PiholeMonitor] Respuesta sin sid: %s", data)
                return False
        except Exception as e:
            logger.error("[PiholeMonitor] Error de autenticación: %s", e)
            return False

    def _sid_valid(self) -> bool:
        """
        Verifica si el token de sesión (sid) sigue siendo válido.

        Returns:
            bool: True si el sid existe y no ha expirado (con margen de 60s).
        """
        with self._sid_lock:
            if not self._sid or self._sid_obtained is None:
                return False
            return (time.time() - self._sid_obtained) < (SESSION_VALIDITY - 60)

    def _get_sid(self) -> Optional[str]:
        """Devuelve el sid válido, autenticando si es necesario."""
        if not self._sid_valid():
            if not self._authenticate():
                return None
        with self._sid_lock:
            return self._sid

    def _logout(self) -> None:
        """
        Cierra la sesión en Pi-hole al parar el monitor.

        Envía una petición DELETE a la API de autenticación para
        invalidar el token de sesión actual (sid).
        """
        with self._sid_lock:
            sid = self._sid
            self._sid = None
        if not sid:
            return
        try:
            req = urllib.request.Request(
                f"http://{PIHOLE_HOST}:{PIHOLE_PORT}/api/auth",
                headers={"sid": sid},
                method="DELETE",
            )
            urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT)
            logger.debug("[PiholeMonitor] Sesión cerrada correctamente")
        except Exception:
            pass

    # ── Fetch ─────────────────────────────────────────────────────────────────

    def _fetch(self) -> None:
        """Llama a la API v6 de Pi-hole y actualiza la caché."""
        # Si no estamos corriendo, no hacemos nada (evita fetch innecesarios al parar)
        if not self._running:
            return
        try:
            sid = self._get_sid()
            headers = {"sid": sid} if sid else {}

            req = urllib.request.Request(
                f"http://{PIHOLE_HOST}:{PIHOLE_PORT}/api/stats/summary",
                headers=headers,
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            # Estructura de respuesta v6:
            # {"queries": {"total": X, "blocked": X, "percent_blocked": X, ...},
            #  "clients": {"active": X, ...},
            #  "gravity": {"domains_being_blocked": X}}
            queries  = data.get("queries",  {})
            clients  = data.get("clients",  {})
            gravity  = data.get("gravity",  {})

            stats = {
                "status":          "enabled",  # si llegamos aquí, está activo
                "queries_today":   int(queries.get("total",            0)),
                "blocked_today":   int(queries.get("blocked",          0)),
                "percent_blocked": float(queries.get("percent_blocked", 0.0)),
                "domains_blocked": int(gravity.get("domains_being_blocked", 0)),
                "unique_clients":  int(clients.get("active",           0)),
                "reachable":       True,
            }
            with self._stats_lock:
                self._stats = stats
            logger.debug(
                "[PiholeMonitor] OK — %d queries, %.1f%% bloqueado",
                stats["queries_today"], stats["percent_blocked"]
            )

        except urllib.error.HTTPError as e:
            if e.code == 401:
                # Sesión expirada — forzar reautenticación en el próximo ciclo
                logger.warning("[PiholeMonitor] Sesión expirada (401) — renovando")
                with self._sid_lock:
                    self._sid = None
            else:
                logger.warning("[PiholeMonitor] HTTP %d en /api/stats/summary", e.code)
            with self._stats_lock:
                self._stats = {**_EMPTY_STATS, "reachable": False}

        except Exception as e:
            with self._stats_lock:
                self._stats = {**_EMPTY_STATS, "reachable": False}
            logger.warning("[PiholeMonitor] Sin conexión con Pi-hole: %s", e)

    # ── API pública ───────────────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        """
        Devuelve las estadísticas de Pi-hole almacenadas en caché.

        No realiza ninguna petición HTTP, solo devuelve los datos
        del último sondeo realizado por el thread de fondo.

        Returns:
            Dict: Diccionario con estadísticas de consultas, bloqueos,
                  dominios bloqueados, clientes únicos y estado de conexión.
                  Devuelve estadísticas vacías si el monitor está parado.
        """
        # ── devolver vacío si parado ──
        if not self._running:
            return dict(_EMPTY_STATS)
        with self._stats_lock:
            return dict(self._stats)

    def is_reachable(self) -> bool:
        """
        Indica si Pi-hole está alcanzable en la red.

        Returns:
            bool: True si la última conexión con Pi-hole fue exitosa.
        """
        with self._stats_lock:
            return self._stats.get("reachable", False)

    def is_enabled(self) -> bool:
        """
        Verifica si el bloqueo de Pi-hole está activado.

        Returns:
            bool: True si el estado de Pi-hole es 'enabled'.
        """
        with self._stats_lock:
            return self._stats.get("status") == "enabled"

    def get_offline_count(self) -> int:
        """Para badge: 1 si Pi-hole no responde, 0 si ok."""
        with self._stats_lock:
            if not self._stats.get("reachable", False) and PIHOLE_HOST:
                return 1
        return 0