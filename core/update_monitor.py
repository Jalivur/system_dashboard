"""
Monitor de actualizaciones del sistema.
Verifica paquetes pendientes via 'apt list --upgradable' con caché de 12h y lock thread-safe.
Ejecuta 'sudo apt update' solo cuando necesario (force o timeout caché).
"""
import subprocess
import time
import threading
from typing import Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class UpdateMonitor:
    """
    Inicializa el monitor de actualizaciones.

    Configura el estado de ejecución, un bloqueo para acceso concurrente, 
    una caché inicial con estado desconocido y un intervalo de comprobación 
    de 12 horas. No inicia hilos automáticos; requiere llamada explícita a start().
    """

    def __init__(self):
        """
        Inicializa el monitor de actualizaciones.

        Configura el estado de ejecución, bloqueo de acceso, caché inicial de resultado desconocido,
        timestamp actual y un intervalo de comprobación de 12 horas. No inicia hilos automáticos,
        requiere llamada explícita a start() para comenzar la monitorización.
        """
        self._running = True
        self._lock          = threading.Lock()
        # Inicializar con tiempo actual para que la caché sea válida desde el inicio
        # Solo ejecuta apt update real cuando: arranque (main.py) o usuario pulsa "Buscar"
        self._last_check_time = time.time()
        self._cached_result = {"pending": 0, "status": "Unknown", "message": "No comprobado"}
        self._check_interval = 43200  # 12 horas en segundos

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Inicia el servicio de monitoreo de actualizaciones.

        Args: 
            None

        Returns: 
            None

        Raises: 
            None
        """
        self._running = True
        logger.info("[UpdateMonitor] Iniciado")

    def stop(self) -> None:
        """
        Detiene el servicio de monitoreo de actualizaciones.

        Args: 
            None

        Returns: 
            None

        Raises: 
            None
        """
        self._running = False
        with self._lock:
            self._cached_result = {"pending": 0, "status": "Unknown", "message": "Servicio parado"}
        logger.info("[UpdateMonitor] Detenido")

    def is_running(self) -> bool:
        """
        Indica si el servicio de actualización está actualmente en ejecución.

        Args:
            Ninguno

        Returns:
            bool: True si el servicio está corriendo, False en caso contrario.

        Raises:
            Ninguno
        """
        return self._running

    # ── API pública ───────────────────────────────────────────────────────────

    def check_updates(self, force=False) -> Dict:
        """
        Verifica actualizaciones pendientes del sistema con un mecanismo de caché.

        Args:
            force (bool): Si True, ignora la caché y los intervalos de actualización, ejecutando 'apt update' inmediatamente.

        Returns:
            Dict: Un diccionario con el número de paquetes actualizables, el estado de la actualización y un mensaje descriptivo.

        Raises:
            None
        """
        if not self._running:
            logger.warning("[UpdateMonitor] check_updates() ignorado — servicio parado")
            return {"pending": 0, "status": "Stopped", "message": "Servicio parado"}

        current_time = time.time()
        with self._lock:
            cached = dict(self._cached_result)
            last   = self._last_check_time

        # Devolver caché si no ha pasado el intervalo y no se fuerza
        if not force and (current_time - last) < self._check_interval:
            logger.debug("[UpdateMonitor] Devolviendo resultado en caché")
            return cached

        try:
            logger.info("[UpdateMonitor] Ejecutando búsqueda real de actualizaciones (apt update)...")

            result = subprocess.run(
                ["sudo", "apt", "update"],
                capture_output=True,
                timeout=60
            )
            if result.returncode != 0:
                logger.warning("[UpdateMonitor] apt update retornó código %d", result.returncode)

            # Usar apt list --upgradable — más fiable que apt-get -s upgrade
            # ya que detecta actualizaciones desde oldstable y otros casos edge.
            # grep -vc excluye la línea de cabecera "Listando... Hecho".
            # CalledProcessError cuando count==0 (grep -v devuelve 1) — se captura.
            cmd = "apt list --upgradable 2>/dev/null | grep -vc '^Listando'"
            try:
                output = subprocess.check_output(cmd, shell=True).decode().strip()
                count = int(output) if output else 0
            except subprocess.CalledProcessError as e:
                # grep -v devuelve código 1 si no hay líneas que no coincidan
                output = e.output.decode().strip() if e.output else "0"
                count = int(output) if output else 0

            if count > 0:
                logger.info("[UpdateMonitor] %d paquetes pendientes de actualización", count)
            else:
                logger.debug("[UpdateMonitor] Sistema al día, sin actualizaciones pendientes")

            new_result = {
                "pending": count,
                "status":  "Ready"   if count > 0 else "Updated",
                "message": f"{count} paquetes pendientes" if count > 0 else "Sistema al día",
            }
            with self._lock:
                self._cached_result   = new_result
                self._last_check_time = current_time
            return new_result

        except subprocess.TimeoutExpired:
            logger.error("[UpdateMonitor] check_updates: timeout ejecutando apt update (>60s)")
            return {"pending": 0, "status": "Error", "message": "Timeout ejecutando apt update"}
        except FileNotFoundError:
            logger.error("[UpdateMonitor] check_updates: apt no encontrado en el sistema")
            return {"pending": 0, "status": "Error", "message": "apt no encontrado"}
        except ValueError as e:
            logger.error("[UpdateMonitor] check_updates: error parseando resultado: %s", e)
            return {"pending": 0, "status": "Error", "message": str(e)}
        except Exception as e:
            logger.error("[UpdateMonitor] check_updates: error inesperado: %s", e)
            return {"pending": 0, "status": "Error", "message": str(e)}

