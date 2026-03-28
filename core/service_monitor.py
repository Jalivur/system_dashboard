"""
Monitor de servicios systemd
"""
import subprocess
import threading
from typing import List, Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Intervalo de actualización del caché de servicios (segundos).
SERVICES_POLL_INTERVAL = 10


class ServiceMonitor:
    """
    Monitoriza servicios systemd con caché en segundo plano.

    Args:
        Ninguno

    Returns:
        Ninguno

    Nota: Configuración inicial: 
        - sort_by: 'name' (name | state)
        - sort_reverse: False
        - filter_type: 'all' (all | active | inactive | failed)
    """

    def __init__(self):
        """
        Inicializa el monitor de servicios con configuración por defecto.

        Args:
            Ninguno

        Returns:
            Ninguno

        Nota: Configuración inicial: 
            - sort_by: 'name' (name | state)
            - sort_reverse: False
            - filter_type: 'all' (all | active | inactive | failed)
        """
        self.sort_by      = "name"   # name | state
        self.sort_reverse = False
        self.filter_type  = "all"    # all | active | inactive | failed

        self._lock: threading.Lock      = threading.Lock()
        self._cached_services: List[Dict] = []
        self._cached_stats: Dict = {
            'total': 0, 'active': 0, 'inactive': 0, 'failed': 0, 'enabled': 0
        }

        self._running  = False
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self.start()

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Inicia el servicio de monitorización en segundo plano.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="ServiceMonitorPoll"
        )
        self._thread.start()
        logger.info("[ServiceMonitor] Sondeo iniciado (cada %ds)", SERVICES_POLL_INTERVAL)

    def stop(self) -> None:
        """
        Detiene el sondeo de servicios limpiamente.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=6)
        with self._lock:
            self._cached_services = []
        logger.info("[ServiceMonitor] Sondeo detenido")
        
    def is_running(self) -> bool:
        """
        Verifica si el monitor de servicios está corriendo activamente.

        Returns:
            bool: True si el monitor está activo
        """
        return self._running

    def toggle_sort(self, column: str) -> None:
        """
        Alterna el criterio de ordenación o invierte el orden actual de la columna especificada.

        Args:
            column (str): Columna para ordenar, ya sea 'name' o 'state'.

        Returns:
            None

        Raises:
            None
        """
        if self.sort_by == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.set_sort(column, reverse=False)
        
    def _poll_loop(self) -> None:
        """
        Ejecuta el bucle principal de sondeo en segundo plano.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
        self._do_poll()
        while self._running:
            self._stop_evt.wait(timeout=SERVICES_POLL_INTERVAL)
            if self._stop_evt.is_set():
                break
            self._do_poll()

    def refresh_now(self) -> None:
        """
        Fuerza un refresco inmediato de la lista de servicios en background.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
        threading.Thread(
            target=self._do_poll, daemon=True, name="ServiceMonitor-ForceRefresh"
        ).start()

    # ── Sondeo ────────────────────────────────────────────────────────────────

    def _do_poll(self) -> None:
        """
        Realiza un sondeo único de servicios y actualiza los cachés internos.

        Args: 
            Ninguno

        Returns: 
            None

        Raises: 
            Exception: Si ocurre un error durante el sondeo o el cálculo de estadísticas.
        """
        try:
            services = self._fetch_services()
            stats    = self._compute_stats(services)
            with self._lock:
                self._cached_services = services
                self._cached_stats    = stats
        except Exception as e:
            logger.error("[ServiceMonitor] Error en _do_poll: %s", e)

    def _fetch_services(self) -> List[Dict]:
        """
        Obtiene la lista de servicios del sistema mediante una llamada a systemctl.

        Args: 
            Ninguno

        Returns:
            List[Dict]: Lista de servicios, donde cada servicio es un diccionario.

        Raises:
            Ninguna excepción relevante.
        """
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--all", "--no-pager"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0:
            return []

        services = []
        for line in result.stdout.strip().split('\n'):
            if (not line.strip()
                    or line.startswith('UNIT')
                    or line.startswith('●')
                    or 'loaded units listed' in line):
                continue

            parts = line.split()
            if len(parts) < 4:
                continue

            unit = parts[0]
            if not unit.endswith('.service'):
                continue

            name = unit.replace('.service', '')
            services.append({
                'name':        name,
                'unit':        unit,
                'load':        parts[1],
                'active':      parts[2],
                'sub':         parts[3],
                'description': ' '.join(parts[4:]) if len(parts) > 4 else '',
                'enabled':     False,
            })

        if not services:
            return []

        enabled_set = self._fetch_enabled_batch([s['unit'] for s in services])
        for s in services:
            s['enabled'] = s['unit'] in enabled_set

        if self.sort_by == "name":
            services.sort(key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
        elif self.sort_by == "state":
            order = {'active': 0, 'inactive': 1, 'failed': 2}
            services.sort(
                key=lambda x: order.get(x['active'], 3), reverse=self.sort_reverse
            )

        return services

    def _fetch_enabled_batch(self, units: List[str]) -> set:
        """
        Obtiene el conjunto de servicios habilitados a partir de una lista de unidades.

        Args:
            units: Lista de nombres de unidades de servicio.

        Returns:
            Un conjunto de nombres de unidades de servicio que están habilitados.

        Raises:
            Exception: Si ocurre un error al ejecutar el comando systemctl.
        """
        _CHUNK = 30
        enabled = set()
        for i in range(0, len(units), _CHUNK):
            chunk = units[i:i + _CHUNK]
            try:
                result = subprocess.run(
                    ["systemctl", "is-enabled", "--"] + chunk,
                    capture_output=True, text=True, timeout=20,
                )
                for unit, state in zip(chunk, result.stdout.strip().split('\n')):
                    if state.strip() == "enabled":
                        enabled.add(unit)
            except Exception as e:
                logger.warning("[ServiceMonitor] Error en is-enabled batch chunk %d: %s", i, e)
        return enabled

    def _compute_stats(self, services: List[Dict]) -> Dict:
        """
        Calcula estadísticas resumidas a partir de la lista de servicios.

        Args:
            services (List[Dict]): Lista de diccionarios de servicios

        Returns:
            Dict: Conteo de servicios total, activos, inactivos, fallidos y habilitados.

        Raises:
            Ninguna excepción explícita.
        """
        return {
            'total':    len(services),
            'active':   sum(1 for s in services if s['active'] == 'active'),
            'inactive': sum(1 for s in services if s['active'] == 'inactive'),
            'failed':   sum(1 for s in services if s['active'] == 'failed'),
            'enabled':  sum(1 for s in services if s['enabled']),
        }

    # ── API pública ───────────────────────────────────────────────────────────

    def get_services(self) -> List[Dict]:
        """
        Recupera la lista de servicios filtrados del caché.

        Args:
            Ninguno

        Returns:
            List[Dict]: Lista de servicios filtrados.

        Raises:
            Ninguno
        """
        with self._lock:
            services = list(self._cached_services)
        if self.filter_type != "all":
            services = [s for s in services if s['active'] == self.filter_type]
        return services

    def get_stats(self) -> Dict:
        """
        Devuelve las estadísticas actuales del servicio de monitorización.

        Args:
            Ninguno

        Returns:
            Dict: Un diccionario con las estadísticas del servicio, incluyendo 'total', 'active', 'inactive', 'failed' y 'enabled'.

        Raises:
            Ninguno
        """
        if not self._running:
            return {'total': 0, 'active': 0, 'inactive': 0, 'failed': 0, 'enabled': 0}
        with self._lock:
            return dict(self._cached_stats)

    def search_services(self, query: str) -> List[Dict]:
        """
        Busca servicios por nombre o descripción en el caché.

        Args:
            query (str): Cadena de búsqueda.

        Returns:
            List[Dict]: Lista de servicios que coinciden con la búsqueda.

        Raises:
            None
        """
        query = query.lower()
        with self._lock:
            all_services = list(self._cached_services)
        return [
            s for s in all_services
            if query in s['name'].lower() or query in s['description'].lower()
        ]

    # ── Control de servicios ──────────────────────────────────────────────────

    def start_service(self, name: str) -> tuple:
        """
        Inicia un servicio systemd y actualiza el estado del monitor si es exitoso.

        Args:
            name: Nombre del servicio (sin extensión .service)

        Returns:
            tuple: Un tupla con un booleano que indica si la operación fue exitosa y un mensaje de resultado.

        Raises:
            None
        """
        ok, msg = self._run_systemctl("start", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def stop_service(self, name: str) -> tuple:
        """
        Detiene un servicio systemd y actualiza el estado del monitor si es exitoso.

        Args:
            name: Nombre del servicio (sin .service)

        Returns:
            tuple: (éxito, mensaje)

        Raises:
            None
        """
        ok, msg = self._run_systemctl("stop", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def restart_service(self, name: str) -> tuple:
        """
        Reinicia un servicio systemd y actualiza el estado del monitor si es exitoso.

        Args:
            name: Nombre del servicio (sin extensión .service)

        Returns:
            tuple: (éxito, mensaje) donde éxito es un booleano y mensaje es una cadena de texto.

        Raises:
            None
        """
        ok, msg = self._run_systemctl("restart", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def enable_service(self, name: str) -> tuple:
        """
        Habilita un servicio systemd para inicio automático.

        Args:
            name: Nombre del servicio (sin .service)

        Returns:
            tuple: (éxito, mensaje)
        """
        ok, msg = self._run_systemctl("enable", name, sudo=False)
        if ok:
            self.refresh_now()
        return ok, msg

    def disable_service(self, name: str) -> tuple:
        """
        Deshabilita un servicio systemd para evitar su inicio automático.

        Args:
            name (str): Nombre del servicio (sin extensión .service)

        Returns:
            tuple: Un tupla con dos elementos: éxito (bool) y mensaje (str)

        Raises:
            None
        """
        ok, msg = self._run_systemctl("disable", name, sudo=False)
        if ok:
            self.refresh_now()
        return ok, msg

    def _run_systemctl(self, action: str, name: str, sudo: bool = True) -> tuple:
        """
        Ejecuta un comando systemctl y devuelve el resultado.

        Args:
            action (str): Acción a realizar ('start', 'stop', 'restart', 'enable', 'disable').
            name (str): Nombre del servicio (sin extensión .service).
            sudo (bool): Indica si se debe utilizar sudo (por defecto True).

        Returns:
            tuple: Un tupla con dos elementos: éxito (bool) y mensaje descriptivo (str).

        Raises:
            Exception: Si ocurre un error durante la ejecución del comando.
        """
        cmd = (["sudo"] if sudo else []) + ["systemctl", action, f"{name}.service"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("[ServiceMonitor] %s '%s' OK", action, name)
                return True, f"Servicio '{name}' {action} correctamente"
            logger.error("[ServiceMonitor] Error en %s '%s': %s", action, name, result.stderr)
            return False, f"Error: {result.stderr}"
        except Exception as e:
            logger.error("[ServiceMonitor] Error en %s '%s': %s", action, name, e)
            return False, f"Error: {str(e)}"

    def get_logs(self, name: str, lines: int = 50) -> str:
        """
        Obtiene los logs de un servicio específico vía journalctl.

        Args:
            name (str): Nombre del servicio.
            lines (int): Número de líneas de logs a obtener (por defecto, 50).

        Returns:
            str: Los logs del servicio o un mensaje de error.

        Raises:
            Exception: Si ocurre un error durante la ejecución de journalctl.
        """
        try:
            result = subprocess.run(
                ["journalctl", "-u", f"{name}.service", "-n", str(lines), "--no-pager"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout
            return f"Error obteniendo logs: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"

    # ── Configuración de vista ────────────────────────────────────────────────

    def set_sort(self, column: str, reverse: bool = False) -> None:
        """
        Establece el criterio de ordenación de la lista de servicios.

        Args:
            column (str): Columna para ordenar ('name', 'state')
            reverse (bool): Si ordenar de forma descendente (por defecto False)

        Returns:
            None

        Raises:
            None
        """
        self.sort_by      = column
        self.sort_reverse = reverse

    def set_filter(self, filter_type: str) -> None:
        """
        Establece el filtro de visualización de servicios.

        Args:
            filter_type (str): Tipo de filtro ('all', 'active', 'inactive', 'failed')

        Returns:
            None

        Raises:
            Ninguna excepción específica.
        """
        self.filter_type = filter_type

    @staticmethod
    def get_state_color(state: str) -> str:
        """
        Obtiene el color CSS según el estado del servicio.

        Args:
            state (str): Estado del servicio.

        Returns:
            str: Clave de color.

        Raises:
            None
        """
        if state == "active":
            return "success"
        elif state == "failed":
            return "danger"
        return "text_dim"
