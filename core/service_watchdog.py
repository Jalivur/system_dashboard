"""
Service Watchdog v4.2 — Auto-restart servicios críticos del sistema (FIXED: maneja inactive).

Monitoriza servicios críticos definidos en local_settings.py.
Cada SERVICE_WATCHDOG_INTERVAL segs (default 60s), chequea si NO active consecutivas >= THRESHOLD (default 3).
Si sí, auto-restart via service_monitor + log/alert + reset counter.

Uso:
  wd = ServiceWatchdog(service_monitor)
  wd.start()
  registry.register('service_watchdog', wd)
"""
import threading
import time
from typing import Dict, List
from pathlib import Path
import json
from utils.logger import get_logger
from config.settings import SERVICE_WATCHDOG_INTERVAL, SERVICE_WATCHDOG_THRESHOLD
from config.local_settings_io import get_param, update_params
from core.service_monitor import ServiceMonitor

logger = get_logger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
WD_STATE_FILE = DATA_DIR / "service_watchdog_state.json"


class ServiceWatchdog:
    """
    Watchdog profesional para monitoreo y auto-reinicio de servicios críticos systemd.

    Características principales:
    * Verificación periódica del estado 'active' cada INTERVAL segundos (predeterminado: 60s).
    * Reinicio automático al superar THRESHOLD fallos consecutivos (predeterminado: 3).
    * Persistencia de contadores de reinicios diarios en data/service_watchdog_state.json.
    * Configuración dinámica mediante parámetros en local_settings.py:
      - watchdog_critical_services: Lista de servicios críticos.
      - watchdog_threshold: Umbral de fallos.
      - watchdog_interval: Intervalo de polling.
    * Logging detallado con niveles INFO/WARNING y estadísticas exportables para UI/dashboard.
    * Ejecución en thread daemon no bloqueante con métodos start/stop limpios (join con timeout 5s).
    * Manejo robusto de errores: servicios no encontrados, JSON corrupto, etc.
    * Reset automático de contadores al cambiar de día.

    Uso recomendado:
        wd = ServiceWatchdog(service_monitor)
        wd.start()
        # Opcional: registry.register('service_watchdog', wd)

    Dependencias: ServiceMonitor para operaciones de servicio, utils.logger, config.local_settings_io.
    Compatible con systemd servicios.
    """
    def __init__(self, service_monitor: ServiceMonitor):
        """
        Inicializa el ServiceWatchdog.

        Args:
            service_monitor (ServiceMonitor): Instancia para restart servicios.

        Inicializa counters de restarts/fallos, carga estado persistido.
        """
        self._service_monitor = service_monitor
        self._critical_services: List[str] = get_param('watchdog_critical_services', [])
        self._threshold = get_param('watchdog_threshold', SERVICE_WATCHDOG_THRESHOLD)
        self._interval = get_param('watchdog_interval', SERVICE_WATCHDOG_INTERVAL)
        self._running = False
        self._thread: threading.Thread = None
        self._stop_event = threading.Event()
        self._restart_counts: Dict[str, int] = {}  # Today restarts per service
        self._consec_failed: Dict[str, int] = {}   # Consec failed checks
        DATA_DIR.mkdir(exist_ok=True)
        self._load_state()

    def start(self):
        """
        Inicia el hilo de monitoreo del watchdog en background (daemon).

        Pollea cada self._interval segs los servicios críticos.
        """
        if self._running:
            return
        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        logger.info("[ServiceWatchdog] Iniciado: %d críticos, thresh %d, poll %ds",
                    len(self._critical_services), self._threshold, self._interval)

    def stop(self):
        """
        Detiene el watchdog limpiamente y persiste estado.

        Espera hasta 5s al thread, guarda restarts del día.
        """
        self._running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self._persist_state()
        logger.info("[ServiceWatchdog] Detenido")
    
    def is_running(self) -> bool:
        """
        Verifica si el watchdog está activo.

        Returns:
            bool: True si el thread está corriendo.
        """
        return self._running

    def set_critical_services(self, services: List[str]):
        """
        Actualiza la lista de servicios críticos a monitorear.

        Args:
            services (List[str]): Nuevos nombres de servicios críticos.
        """
        self._critical_services = services
        update_params({'watchdog_critical_services': services})

    def set_threshold(self, thresh: int):
        """
        Cambia el umbral de fallos consecutivos para auto-restart.

        Args:
            thresh (int): Número de fallos seguidos (default 3).
        """
        self._threshold = thresh
        update_params({'watchdog_threshold': thresh})

    def set_interval(self, interval: int):
        """
        Cambia el intervalo de polling en segundos.

        Args:
            interval (int): Segundos entre chequeos (default 60).
        """
        self._interval = interval
        update_params({'watchdog_interval': interval})
    
    def add_critical_service(self, name: str) -> bool:
        """
        Añade un servicio crítico si no existe ya.

        Args:
            name (str): Nombre del servicio systemd.

        Returns:
            bool: True si añadido, False si ya estaba.
        """
        if name in self._critical_services:
            return False
        self._critical_services.append(name)
        return True

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del watchdog para UI.

        Returns:
            Dict: Counters restarts, servicios, estado, etc.
        """
        return {
            'critical_count': len(self._critical_services),
            'restarts_today': sum(self._restart_counts.values()),
            'services': self._critical_services,
            'threshold': self._threshold,
            'interval': self._interval,
            'running': self._running,
            'restart_counts': dict(self._restart_counts),
            'consec_failed': dict(self._consec_failed)
        }

    def _watch_loop(self):
        """
        Bucle principal privado del watchdog (thread daemon).
        Espera self._interval y chequea servicios.
        """
        while self._running and not self._stop_event.wait(timeout=self._interval):
            self._check_services()

    def _check_services(self):
        """
        Chequea estado de servicios críticos, incrementa counters fallos.
        Si >= threshold, trigger auto_restart().
        """
        services = self._service_monitor.get_services()
        for name in self._critical_services:
            service = next((s for s in services if s['name'] == name), None)
            if not service:
                logger.warning("[ServiceWatchdog] Critical '%s' no encontrado", name)
                continue
            if service['active'] == 'active':
                self._consec_failed[name] = 0
                continue
            self._consec_failed[name] = self._consec_failed.get(name, 0) + 1
            logger.info("[ServiceWatchdog] Servicio '%s' NO active (consec: %d/%d)", name, self._consec_failed[name], self._threshold)
            if self._consec_failed[name] >= self._threshold:
                self._auto_restart(name)
                self._consec_failed[name] = 0

    def _auto_restart(self, name: str):
        """
        Reinicia servicio crítico via service_monitor y actualiza counters.
        """
        logger.warning("[ServiceWatchdog] AUTO-RESTART '%s' (thresh %d)", name, self._threshold)
        success, msg = self._service_monitor.restart_service(name)
        if success:
            self._restart_counts[name] = self._restart_counts.get(name, 0) + 1
            logger.info("[ServiceWatchdog] Restart OK: %s (today: %d)", name, self._restart_counts[name])
        self._persist_state()

    def _persist_state(self):
        """
        Guarda counters restarts en data/service_watchdog_state.json (diario).
        """
        state = {
            'restart_counts': self._restart_counts,
            'last_reset': time.strftime('%Y-%m-%d')
        }
        WD_STATE_FILE.write_text(json.dumps(state))

    def _load_state(self):
        """
        Carga counters del día desde JSON persistido.
        Reset automático si nuevo día.
        """
        if WD_STATE_FILE.exists():
            try:
                data = json.loads(WD_STATE_FILE.read_text())
                today = time.strftime('%Y-%m-%d')
                if data.get('last_reset') == today:
                    self._restart_counts = data.get('restart_counts', {})
                # Si es otro día se deja restart_counts vacío — reset automático
            except Exception:
                pass
