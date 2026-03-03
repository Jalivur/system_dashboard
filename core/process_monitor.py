"""
Monitor de procesos del sistema
"""
import threading
import psutil
from typing import List, Dict, Optional
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

PROCESS_POLL_INTERVAL = 10


class ProcessMonitor:
    """Monitor de procesos en tiempo real"""

    def __init__(self):
        self.sort_by      = "cpu"   # cpu | memory | name | pid
        self.sort_reverse = True
        self.filter_type  = "all"   # all | user | system

        self._lock: threading.Lock      = threading.Lock()
        self._cached_processes: List[Dict] = []

        self._running  = False
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self.start()

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """Arranca el sondeo en background (llamado automáticamente en __init__)."""
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="ProcessMonitorPoll"
        )
        self._thread.start()
        logger.info("[ProcessMonitor] Sondeo iniciado (cada %ds)", PROCESS_POLL_INTERVAL)

    def stop(self) -> None:
        """Detiene el sondeo limpiamente."""
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=6)
        with self._lock:
            self._cached_processes = []
        logger.info("[ProcessMonitor] Sondeo detenido")

    def _poll_loop(self) -> None:
        self._do_poll()
        while self._running:
            self._stop_evt.wait(timeout=PROCESS_POLL_INTERVAL)
            if self._stop_evt.is_set():
                break
            self._do_poll()

    def refresh_now(self) -> None:
        """Fuerza un refresco inmediato del caché en background."""
        threading.Thread(
            target=self._do_poll, daemon=True, name="ProcessMonitor-ForceRefresh"
        ).start()

    def _do_poll(self) -> None:
        try:
            processes = self.get_processes()
            with self._lock:
                self._cached_processes = processes
        except Exception as e:
            logger.error("[ProcessMonitor] Error en _do_poll: %s", e)

    # ── API pública ───────────────────────────────────────────────────────────

    def get_processes(self, limit: int = 20) -> List[Dict]:
        """
        Obtiene lista de procesos con su información.

        Args:
            limit: Número máximo de procesos a retornar

        Returns:
            Lista de diccionarios con información de procesos
        """
        processes = []
        current_user = psutil.Process().username()

        for proc in psutil.process_iter(
            ['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'cmdline', 'exe']
        ):
            try:
                pinfo = proc.info

                if self.filter_type == "user" and pinfo['username'] != current_user:
                    continue
                if self.filter_type == "system" and pinfo['username'] == current_user:
                    continue

                cmdline = pinfo['cmdline']
                exe     = pinfo['exe']
                name    = pinfo['name'] or 'N/A'

                if cmdline:
                    display_name = ' '.join(cmdline[:2])
                elif exe:
                    display_name = exe
                else:
                    display_name = name

                processes.append({
                    'pid':          pinfo['pid'],
                    'name':         name,
                    'display_name': display_name,
                    'username':     pinfo['username'] or 'N/A',
                    'cpu':          pinfo['cpu_percent'] or 0.0,
                    'memory':       pinfo['memory_percent'] or 0.0,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        key_map = {
            'cpu':    lambda x: x['cpu'],
            'memory': lambda x: x['memory'],
            'name':   lambda x: x['name'].lower(),
            'pid':    lambda x: x['pid'],
        }
        processes.sort(
            key=key_map.get(self.sort_by, lambda x: x['cpu']),
            reverse=self.sort_reverse
        )
        return processes[:limit]

    def search_processes(self, query: str) -> List[Dict]:
        """
        Busca procesos por nombre o descripción.

        Args:
            query: Texto a buscar

        Returns:
            Lista de procesos que coinciden
        """
        query = query.lower()
        all_processes = self.get_processes(limit=1000)
        return [
            p for p in all_processes
            if query in p['name'].lower() or query in p.get('display_name', '').lower()
        ]

    def kill_process(self, pid: int) -> tuple:
        """
        Mata un proceso por su PID.

        Args:
            pid: ID del proceso

        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            try:
                cmdline      = proc.cmdline()
                display_name = ' '.join(cmdline[:2]) if cmdline else name
            except (psutil.AccessDenied, psutil.ZombieProcess):
                display_name = name

            proc.terminate()
            proc.wait(timeout=3)
            logger.info("[ProcessMonitor] Proceso '%s' (PID %d) terminado", display_name, pid)
            return True, f"Proceso '{display_name}' (PID {pid}) terminado correctamente"

        except psutil.NoSuchProcess:
            logger.error("[ProcessMonitor] PID %d no existe", pid)
            return False, f"Proceso con PID {pid} no existe"
        except psutil.AccessDenied:
            logger.error("[ProcessMonitor] Sin permisos para terminar PID %d", pid)
            return False, f"Sin permisos para terminar proceso {pid}"
        except psutil.TimeoutExpired:
            try:
                proc.kill()
                logger.info("[ProcessMonitor] PID %d forzado a cerrar", pid)
                return True, f"Proceso '{display_name}' (PID {pid}) forzado a cerrar"
            except Exception as e:
                logger.error("[ProcessMonitor] Error forzando cierre PID %d: %s", pid, e)
                return False, f"Error: {str(e)}"
        except Exception as e:
            logger.error("[ProcessMonitor] Error terminando PID %d: %s", pid, e)
            return False, f"Error: {str(e)}"

    def get_system_stats(self) -> Dict:
        """
        Obtiene estadísticas generales del sistema.

        Returns:
            Diccionario con estadísticas
        """
        cpu_percent  = psutil.cpu_percent(interval=0.1)
        mem          = psutil.virtual_memory()
        boot_time    = datetime.fromtimestamp(psutil.boot_time())
        uptime       = datetime.now() - boot_time

        return {
            'cpu_percent':    cpu_percent,
            'mem_used_gb':    mem.used / (1024 ** 3),
            'mem_total_gb':   mem.total / (1024 ** 3),
            'mem_percent':    mem.percent,
            'total_processes': len(psutil.pids()),
            'uptime':         self._format_uptime(uptime.total_seconds()),
        }

    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """Formatea uptime en formato legible."""
        days    = int(seconds // 86400)
        hours   = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    # ── Configuración de vista ────────────────────────────────────────────────

    def set_sort(self, column: str, reverse: bool = True):
        self.sort_by      = column
        self.sort_reverse = reverse

    def set_filter(self, filter_type: str):
        self.filter_type = filter_type

    @staticmethod
    def get_process_color(value: float) -> str:
        """
        Obtiene color según porcentaje de uso.

        Args:
            value: Porcentaje (0-100)

        Returns:
            Clave de color en COLORS
        """
        if value >= 70:
            return "danger"
        elif value >= 30:
            return "warning"
        return "success"
