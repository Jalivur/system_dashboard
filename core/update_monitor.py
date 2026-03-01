"""
Monitor de actualizaciones del sistema
"""
import subprocess
import time
from typing import Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class UpdateMonitor:
    """Lógica para verificar actualizaciones del sistema con caché"""

    def __init__(self):
        self._running = True
        # Inicializar con tiempo actual para que la caché sea válida desde el inicio
        # Solo ejecuta apt update real cuando: arranque (main.py) o usuario pulsa "Buscar"
        self.last_check_time = time.time()
        self.cached_result = {"pending": 0, "status": "Unknown", "message": "No comprobado"}
        self.check_interval = 43200  # 12 horas en segundos

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        self._running = True
        logger.info("[UpdateMonitor] Iniciado")

    def stop(self) -> None:
        self._running = False
        self.cached_result = {"pending": 0, "status": "Unknown", "message": "Servicio parado"}
        logger.info("[UpdateMonitor] Detenido")

    # ── API pública ───────────────────────────────────────────────────────────

    def check_updates(self, force=False) -> Dict:
        """
        Verifica actualizaciones pendientes con sistema de caché.

        Args:
            force: Si True, ignora el caché y ejecuta apt update real

        Returns:
            Diccionario con pending, status y message
        """
        if not self._running:
            logger.warning("[UpdateMonitor] check_updates() ignorado — servicio parado")
            return {"pending": 0, "status": "Stopped", "message": "Servicio parado"}

        current_time = time.time()

        # Devolver caché si no ha pasado el intervalo y no se fuerza
        if not force and (current_time - self.last_check_time) < self.check_interval:
            logger.debug("[UpdateMonitor] Devolviendo resultado en caché")
            return self.cached_result

        try:
            logger.info("[UpdateMonitor] Ejecutando búsqueda real de actualizaciones (apt update)...")

            result = subprocess.run(
                ["sudo", "apt", "update"],
                capture_output=True,
                timeout=20
            )
            if result.returncode != 0:
                logger.warning(f"[UpdateMonitor] apt update retornó código {result.returncode}")

            cmd = "apt-get -s upgrade | grep '^Inst ' | wc -l"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            count = int(output) if output else 0

            if count > 0:
                logger.info(f"[UpdateMonitor] {count} paquetes pendientes de actualización")
            else:
                logger.debug("[UpdateMonitor] Sistema al día, sin actualizaciones pendientes")

            self.cached_result = {
                "pending": count,
                "status": "Ready" if count > 0 else "Updated",
                "message": f"{count} paquetes pendientes" if count > 0 else "Sistema al día"
            }
            self.last_check_time = current_time
            return self.cached_result

        except subprocess.TimeoutExpired:
            logger.error("[UpdateMonitor] check_updates: timeout ejecutando apt update (>20s)")
            return {"pending": 0, "status": "Error", "message": "Timeout ejecutando apt update"}
        except FileNotFoundError:
            logger.error("[UpdateMonitor] check_updates: apt no encontrado en el sistema")
            return {"pending": 0, "status": "Error", "message": "apt no encontrado"}
        except ValueError as e:
            logger.error(f"[UpdateMonitor] check_updates: error parseando resultado: {e}")
            return {"pending": 0, "status": "Error", "message": str(e)}
        except Exception as e:
            logger.error(f"[UpdateMonitor] check_updates: error inesperado: {e}")
            return {"pending": 0, "status": "Error", "message": str(e)}
