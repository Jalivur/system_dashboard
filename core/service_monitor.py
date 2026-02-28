"""
Monitor de servicios systemd
"""
import subprocess
import threading
from typing import List, Dict, Optional
from utils import DashboardLogger


# Intervalo de actualización del caché de servicios (segundos).
# Los servicios cambian raramente — 10s es más que suficiente para el badge
# y no sobrecarga la Pi con systemctl cada 2s.
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
        self.sort_by     = "name"   # name | state
        self.sort_reverse = False
        self.filter_type  = "all"   # all | active | inactive | failed
        self.dashboard_logger = DashboardLogger()
        self._logger = self.dashboard_logger.get_logger(__name__)

        # Caché thread-safe
        self._lock: threading.Lock = threading.Lock()
        self._cached_services: List[Dict] = []
        self._cached_stats: Dict = {
            'total': 0, 'active': 0, 'inactive': 0, 'failed': 0, 'enabled': 0
        }

        # Control del thread
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
            target=self._poll_loop,
            daemon=True,
            name="ServiceMonitorPoll",
        )
        self._thread.start()
        self._logger.info(
            "[ServiceMonitor] Sondeo iniciado (cada %ds)", SERVICES_POLL_INTERVAL
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
        """Bucle de background: sondea systemctl y actualiza el caché."""
        self._do_poll()  # primera lectura inmediata
        while self._running:
            self._stop_evt.wait(timeout=SERVICES_POLL_INTERVAL)
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
            name="ServiceMonitor-ForceRefresh",
        ).start()

    # ── Sondeo ────────────────────────────────────────────────────────────────

    def _do_poll(self) -> None:
        """
        Ejecuta systemctl en background y actualiza el caché.
        Obtiene todos los servicios Y su estado enabled en dos llamadas,
        evitando el antipatrón de N subprocesses (uno por servicio).
        """
        try:
            services = self._fetch_services()
            stats    = self._compute_stats(services)

            with self._lock:
                self._cached_services = services
                self._cached_stats    = stats

        except Exception as e:
            self._logger.error("[ServiceMonitor] Error en _do_poll: %s", e)

    def _fetch_services(self) -> List[Dict]:
        """
        Obtiene la lista de servicios con una sola llamada a systemctl
        y enriquece con el estado enabled en una segunda llamada batch.
        """
        # ── 1. Listar unidades ─────────────────────────────────────────────
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--all", "--no-pager"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if result.returncode != 0:
            return []

        services = []
        lines = result.stdout.strip().split('\n')
        for line in lines:
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

            load        = parts[1]
            active      = parts[2]
            sub         = parts[3]
            description = ' '.join(parts[4:]) if len(parts) > 4 else ''
            name        = unit.replace('.service', '')

            services.append({
                'name':        name,
                'unit':        unit,
                'load':        load,
                'active':      active,
                'sub':         sub,
                'description': description,
                'enabled':     False,   # se rellena en el paso 2
            })

        if not services:
            return []

        # ── 2. Estado enabled — una sola llamada para todos ────────────────
        enabled_set = self._fetch_enabled_batch([s['unit'] for s in services])
        for s in services:
            s['enabled'] = s['unit'] in enabled_set

        # ── 3. Ordenar ─────────────────────────────────────────────────────
        if self.sort_by == "name":
            services.sort(key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
        elif self.sort_by == "state":
            order = {'active': 0, 'inactive': 1, 'failed': 2}
            services.sort(
                key=lambda x: order.get(x['active'], 3),
                reverse=self.sort_reverse,
            )

        return services

    def _fetch_enabled_batch(self, units: List[str]) -> set:
        """
        Obtiene el estado enabled de todos los servicios en UNA sola
        llamada a systemctl, en lugar de N llamadas separadas.
        Devuelve un set con los nombres de unidades que están enabled.
        """
        try:
            result = subprocess.run(
                ["systemctl", "is-enabled", "--"] + units,
                capture_output=True,
                text=True,
                timeout=8,
            )
            # La salida tiene una línea por unidad, en el mismo orden
            lines = result.stdout.strip().split('\n')
            enabled = set()
            for unit, state in zip(units, lines):
                if state.strip() == "enabled":
                    enabled.add(unit)
            return enabled
        except Exception as e:
            self._logger.warning("[ServiceMonitor] Error en is-enabled batch: %s", e)
            return set()

    def _compute_stats(self, services: List[Dict]) -> Dict:
        """Calcula las estadísticas a partir de la lista de servicios."""
        return {
            'total':    len(services),
            'active':   sum(1 for s in services if s['active'] == 'active'),
            'inactive': sum(1 for s in services if s['active'] == 'inactive'),
            'failed':   sum(1 for s in services if s['active'] == 'failed'),
            'enabled':  sum(1 for s in services if s['enabled']),
        }

    # ── API pública (lee del caché, no bloquea) ───────────────────────────────

    def get_services(self) -> List[Dict]:
        """
        Devuelve la lista de servicios del caché aplicando filtro actual.
        No lanza ningún subprocess — nunca bloquea el hilo de UI.
        """
        with self._lock:
            services = list(self._cached_services)

        # Aplicar filtro en memoria
        if self.filter_type != "all":
            services = [s for s in services if s['active'] == self.filter_type]

        return services

    def get_stats(self) -> Dict:
        """
        Devuelve las estadísticas del caché.
        No lanza ningún subprocess — nunca bloquea el hilo de UI.
        """
        if not self._running:
            return {'total': 0, 'running': 0, 'failed': 0, 'services': []}
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

    # ── Control de servicios (subprocesses bloqueantes, solo bajo demanda) ────

    def start_service(self, name: str) -> tuple:
        """Inicia un servicio y fuerza refresco del caché."""
        ok, msg = self._run_systemctl("start", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def stop_service(self, name: str) -> tuple:
        """Detiene un servicio y fuerza refresco del caché."""
        ok, msg = self._run_systemctl("stop", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def restart_service(self, name: str) -> tuple:
        """Reinicia un servicio y fuerza refresco del caché."""
        ok, msg = self._run_systemctl("restart", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def enable_service(self, name: str) -> tuple:
        """Habilita autostart y fuerza refresco del caché."""
        ok, msg = self._run_systemctl("enable", name, sudo=False)
        if ok:
            self.refresh_now()
        return ok, msg

    def disable_service(self, name: str) -> tuple:
        """Deshabilita autostart y fuerza refresco del caché."""
        ok, msg = self._run_systemctl("disable", name, sudo=False)
        if ok:
            self.refresh_now()
        return ok, msg

    def _run_systemctl(self, action: str, name: str, sudo: bool = True) -> tuple:
        """Ejecuta un comando systemctl. Uso interno."""
        cmd = (["sudo"] if sudo else []) + ["systemctl", action, f"{name}.service"]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                self._logger.info("[ServiceMonitor] %s '%s' OK", action, name)
                return True, f"Servicio '{name}' {action} correctamente"
            self._logger.error(
                "[ServiceMonitor] Error en %s '%s': %s", action, name, result.stderr
            )
            return False, f"Error: {result.stderr}"
        except Exception as e:
            self._logger.error("[ServiceMonitor] Error en %s '%s': %s", action, name, e)
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
        self.sort_by     = column
        self.sort_reverse = reverse

    def set_filter(self, filter_type: str) -> None:
        self.filter_type = filter_type

    def get_state_color(self, state: str) -> str:
        if state == "active":
            return "success"
        elif state == "failed":
            return "danger"
        return "text_dim"
