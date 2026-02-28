"""
Monitor de procesos del sistema
"""
import psutil
from typing import List, Dict, Optional
from datetime import datetime
from utils import DashboardLogger
import threading

PROCCES_POLL_INTERVAL = 10

class ProcessMonitor:
    """Monitor de procesos en tiempo real"""
    
    def __init__(self):
        """Inicializa el monitor de procesos"""
        self.sort_by = "cpu"  # cpu, memory, name, pid
        self.sort_reverse = True
        self.filter_type = "all"  # all, user, system
        self.dashboard_logger = DashboardLogger()
        self._logger = self.dashboard_logger.get_logger(__name__)
        
        self._lock: threading.Lock = threading.Lock()
        self._cached_procces: List[Dict] = []
        
        self._running = False
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.start()
        
    def start(self) -> None:
        """Arranca el sondeo en background (llamado automáticamente en __init__)."""
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
            name="ServiceMonitorPoll",
        )
        self._thread.start()
        self._logger.info(
            "[ProcessMonitor] Sondeo iniciado (cada %ds)", PROCCES_POLL_INTERVAL
        )
    
    def stop(self) -> None:
        """Detiene el sondeo limpiamente."""
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=6)
        self._cache = {}
        self._logger.info("[ServiceMonitor] Sondeo detenido")
    
    def _poll_loop(self) -> None:
        """Bucle de background: sondea process y actualiza el caché."""
        self._do_poll()  # primera lectura inmediata
        while self._running:
            self._stop_evt.wait(timeout=PROCCES_POLL_INTERVAL)
            if self._stop_evt.is_set():
                break
            self._do_poll()
    
    def refresh_now(self) -> None:
        """
        Fuerza un refresco inmediato del caché en background.
        Llamar desde ServiceWindow tras start/stop/restart/enable/disable.
        """
        threading.Thread(
            target=self._do_poll,
            daemon=True,
            name="ProcessMonitor-ForceRefresh",
        ).start()
    
    def _do_poll(self) -> None:
        try:
            processes = self.get_processes()
            
            with self._lock:
                self._cached_procces = processes
        except Exception as e:
            self._logger.error("[ProccesMonitor] Error en _do_poll: %s", e)
    
    def get_processes(self, limit: int = 20) -> List[Dict]:
        """
        Obtiene lista de procesos con su información
        
        Args:
            limit: Número máximo de procesos a retornar
            
        Returns:
            Lista de diccionarios con información de procesos
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'cmdline', 'exe']):
            try:
                pinfo = proc.info
                
                # Aplicar filtro
                if self.filter_type == "user":
                    # Solo procesos del usuario actual
                    if pinfo['username'] != psutil.Process().username():
                        continue
                elif self.filter_type == "system":
                    # Solo procesos del sistema (root, etc)
                    if pinfo['username'] == psutil.Process().username():
                        continue
                
                # Obtener descripción más detallada
                cmdline = pinfo['cmdline']
                exe = pinfo['exe']
                name = pinfo['name'] or 'N/A'
                
                # Crear descripción mejor
                if cmdline:
                    # Si hay cmdline, usar el primer argumento como descripción
                    display_name = ' '.join(cmdline[:2])  # Primeros 2 argumentos
                elif exe:
                    # Si no hay cmdline pero hay exe, usar el path
                    display_name = exe
                else:
                    display_name = name
                
                processes.append({
                    'pid': pinfo['pid'],
                    'name': name,
                    'display_name': display_name,  # Nueva columna descriptiva
                    'username': pinfo['username'] or 'N/A',
                    'cpu': pinfo['cpu_percent'] or 0.0,
                    'memory': pinfo['memory_percent'] or 0.0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Ordenar según criterio
        if self.sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu'], reverse=self.sort_reverse)
        elif self.sort_by == "memory":
            processes.sort(key=lambda x: x['memory'], reverse=self.sort_reverse)
        elif self.sort_by == "name":
            processes.sort(key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
        elif self.sort_by == "pid":
            processes.sort(key=lambda x: x['pid'], reverse=self.sort_reverse)
        
        return processes[:limit]
    
    def search_processes(self, query: str) -> List[Dict]:
        """
        Busca procesos por nombre o descripción
        
        Args:
            query: Texto a buscar en nombre de proceso
            
        Returns:
            Lista de procesos que coinciden
        """
        query = query.lower()
        all_processes = self.get_processes(limit=1000)  # Obtener todos
        
        return [p for p in all_processes 
                if query in p['name'].lower() or query in p.get('display_name', '').lower()]
    



    def kill_process(self, pid: int) -> tuple[bool, str]:
        """
        Mata un proceso por su PID
        
        Args:
            pid: ID del proceso
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            proc = psutil.Process(pid)
            name = proc.name()

            # Obtener display_name igual que en get_processes
            try:
                cmdline = proc.cmdline()
                display_name = ' '.join(cmdline[:2]) if cmdline else name
            except (psutil.AccessDenied, psutil.ZombieProcess):
                display_name = name

            proc.terminate()  # Intenta cerrar limpiamente
            
            # Esperar un poco
            proc.wait(timeout=3)
            self.dashboard_logger.get_logger(__name__).info(f"[ProcessMonitor] Proceso '{display_name}' (PID {pid}) terminado correctamente")
            return True, f"Proceso '{display_name}' (PID {pid}) terminado correctamente"
        except psutil.NoSuchProcess:
            self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Proceso con PID {pid} no existe")
            return False, f"Proceso con PID {pid} no existe"
        except psutil.AccessDenied:
            self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Sin permisos para terminar proceso {pid}")
            return False, f"Sin permisos para terminar proceso {pid}"
        except psutil.TimeoutExpired:
            # Si no se cierra, forzar
            try:
                proc.kill()
                self.dashboard_logger.get_logger(__name__).info(f"[ProcessMonitor] Proceso '{display_name}' (PID {pid}) forzado a cerrar")
                return True, f"Proceso '{display_name}' (PID {pid}) forzado a cerrar"
            except Exception as e:
                self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Error forzando cierre del proceso '{display_name}' (PID {pid}): {e}")
                return False, f"Error: {str(e)}"
        except Exception as e:
            self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Error terminando proceso '{display_name}' (PID {pid}): {e}")
            return False, f"Error: {str(e)}"
    def get_system_stats(self) -> Dict:
        """
        Obtiene estadísticas generales del sistema
        
        Returns:
            Diccionario con estadísticas
        """
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # RAM
        mem = psutil.virtual_memory()
        mem_used_gb = mem.used / (1024**3)
        mem_total_gb = mem.total / (1024**3)
        mem_percent = mem.percent
        
        # Procesos
        total_processes = len(psutil.pids())
        
        # Uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = self._format_uptime(uptime.total_seconds())
        
        return {
            'cpu_percent': cpu_percent,
            'mem_used_gb': mem_used_gb,
            'mem_total_gb': mem_total_gb,
            'mem_percent': mem_percent,
            'total_processes': total_processes,
            'uptime': uptime_str
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """
        Formatea uptime en formato legible
        
        Args:
            seconds: Segundos de uptime
            
        Returns:
            String formateado
        """
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def set_sort(self, column: str, reverse: bool = True):
        """
        Configura el orden de procesos
        
        Args:
            column: Columna por la que ordenar (cpu, memory, name, pid)
            reverse: Si ordenar de mayor a menor
        """
        self.sort_by = column
        self.sort_reverse = reverse
    
    def set_filter(self, filter_type: str):
        """
        Configura el filtro de procesos
        
        Args:
            filter_type: Tipo de filtro (all, user, system)
        """
        self.filter_type = filter_type
    
    def get_process_color(self, value: float) -> str:
        """
        Obtiene color según porcentaje de uso
        
        Args:
            value: Porcentaje (0-100)
            
        Returns:
            Nombre del color en COLORS
        """
        if value >= 70:
            return "danger"
        elif value >= 30:
            return "warning"
        else:
            return "success"
