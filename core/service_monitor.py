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
    Monitor de servicios systemd con caché en background.

    El método get_services() en versiones anteriores lanzaba systemctl
    en el hilo de UI cada 2s, bloqueando Tkinter. Ahora:
    - Un thread de background sondea systemctl cada 10s.
    - get_services() y get_stats() devuelven el caché sin bloquear.
    - La ventana ServiceWindow puede forzar un refresco con refresh_now().
    """

    def __init__(self):
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
        """Arranca el sondeo en background (llamado automáticamente en __init__)."""
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
        """Detiene el sondeo limpiamente."""
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=6)
        with self._lock:
            self._cached_services = []
        logger.info("[ServiceMonitor] Sondeo detenido")

    def _poll_loop(self) -> None:
        self._do_poll()
        while self._running:
            self._stop_evt.wait(timeout=SERVICES_POLL_INTERVAL)
            if self._stop_evt.is_set():
                break
            self._do_poll()

    def refresh_now(self) -> None:
        """Fuerza un refresco inmediato del caché en background."""
        threading.Thread(
            target=self._do_poll, daemon=True, name="ServiceMonitor-ForceRefresh"
        ).start()

    # ── Sondeo ────────────────────────────────────────────────────────────────

    def _do_poll(self) -> None:
        """Ejecuta systemctl en background y actualiza el caché."""
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
        Obtiene la lista de servicios con una sola llamada a systemctl
        y enriquece con el estado enabled en una segunda llamada batch.
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
        Obtiene el estado enabled de todos los servicios en UNA sola
        llamada a systemctl. Devuelve un set con los units habilitados.
        """
        try:
            result = subprocess.run(
                ["systemctl", "is-enabled", "--"] + units,
                capture_output=True, text=True, timeout=20,
            )
            enabled = set()
            for unit, state in zip(units, result.stdout.strip().split('\n')):
                if state.strip() == "enabled":
                    enabled.add(unit)
            return enabled
        except Exception as e:
            logger.warning("[ServiceMonitor] Error en is-enabled batch: %s", e)
            return set()

    def _compute_stats(self, services: List[Dict]) -> Dict:
        return {
            'total':    len(services),
            'active':   sum(1 for s in services if s['active'] == 'active'),
            'inactive': sum(1 for s in services if s['active'] == 'inactive'),
            'failed':   sum(1 for s in services if s['active'] == 'failed'),
            'enabled':  sum(1 for s in services if s['enabled']),
        }

    # ── API pública ───────────────────────────────────────────────────────────

    def get_services(self) -> List[Dict]:
        """Devuelve la lista del caché aplicando filtro. No bloquea el hilo de UI."""
        with self._lock:
            services = list(self._cached_services)
        if self.filter_type != "all":
            services = [s for s in services if s['active'] == self.filter_type]
        return services

    def get_stats(self) -> Dict:
        """Devuelve las estadísticas del caché. No bloquea el hilo de UI."""
        if not self._running:
            return {'total': 0, 'active': 0, 'inactive': 0, 'failed': 0, 'enabled': 0}
        with self._lock:
            return dict(self._cached_stats)

    def search_services(self, query: str) -> List[Dict]:
        """Busca servicios por nombre o descripción (en el caché)."""
        query = query.lower()
        with self._lock:
            all_services = list(self._cached_services)
        return [
            s for s in all_services
            if query in s['name'].lower() or query in s['description'].lower()
        ]

    # ── Control de servicios ──────────────────────────────────────────────────

    def start_service(self, name: str) -> tuple:
        ok, msg = self._run_systemctl("start", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def stop_service(self, name: str) -> tuple:
        ok, msg = self._run_systemctl("stop", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def restart_service(self, name: str) -> tuple:
        ok, msg = self._run_systemctl("restart", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def enable_service(self, name: str) -> tuple:
        ok, msg = self._run_systemctl("enable", name, sudo=False)
        if ok:
            self.refresh_now()
        return ok, msg

    def disable_service(self, name: str) -> tuple:
        ok, msg = self._run_systemctl("disable", name, sudo=False)
        if ok:
            self.refresh_now()
        return ok, msg

    def _run_systemctl(self, action: str, name: str, sudo: bool = True) -> tuple:
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
        """Obtiene logs de un servicio vía journalctl."""
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
        self.sort_by      = column
        self.sort_reverse = reverse

    def set_filter(self, filter_type: str) -> None:
        self.filter_type = filter_type

    @staticmethod
    def get_state_color(state: str) -> str:
        if state == "active":
            return "success"
        elif state == "failed":
            return "danger"
        return "text_dim"
