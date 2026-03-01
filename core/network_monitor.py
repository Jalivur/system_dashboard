"""
Monitor de red
"""
import json
import threading
import subprocess
from collections import deque
from typing import Dict, Optional
from config.settings import (HISTORY, NET_MIN_SCALE, NET_MAX_SCALE, 
                             NET_IDLE_THRESHOLD, NET_IDLE_RESET_TIME, NET_MAX_MB, COLORS, NET_WARN, NET_CRIT)
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class NetworkMonitor:
    """Monitor de red con gestión de estadísticas y speedtest"""
    
    def __init__(self):
        self.system_utils = SystemUtils()
        self._running = True  # ── AÑADIDO ──

        # Historiales
        self.download_hist = deque(maxlen=HISTORY)
        self.upload_hist = deque(maxlen=HISTORY)
        
        # Estado
        self.last_net_io = {}
        self.last_used_iface = None
        self.dynamic_max = NET_MAX_MB
        self.idle_counter = 0
        
        # Speedtest
        self.speedtest_result = {
            "status": "idle",
            "ping": 0,
            "download": 0.0,
            "upload": 0.0
        }

    def start(self) -> None:  # ── AÑADIDO ──
        self._running = True
        logger.info("[NetworkMonitor] Iniciado")

    def stop(self) -> None:  # ── AÑADIDO ──
        self._running = False
        self.download_hist.clear()
        self.upload_hist.clear()
        self.speedtest_result = {"status": "idle", "ping": 0, "download": 0.0, "upload": 0.0}
        logger.info("[NetworkMonitor] Detenido")

    def get_current_stats(self, interface: Optional[str] = None) -> Dict:
        """
        Obtiene estadísticas actuales de red
        
        Args:
            interface: Interfaz de red específica o None para auto-detección
            
        Returns:
            Diccionario con estadísticas de red
        """
        if not self._running:  # ── AÑADIDO ──
            return {'interface': '', 'download_mb': 0.0, 'upload_mb': 0.0, 'ip': ''}

        iface, stats = self.system_utils.get_net_io(interface)
        
        prev = self.last_net_io.get(iface)
        dl, ul = self.system_utils.safe_net_speed(stats, prev)
        
        self.last_net_io[iface] = stats
        self.last_used_iface = iface
        
        return {
            'interface': iface,
            'download_mb': dl,
            'upload_mb': ul
        }
    
    def update_history(self, stats: Dict) -> None:
        """
        Actualiza historiales de red
        
        Args:
            stats: Estadísticas actuales
        """
        self.download_hist.append(stats['download_mb'])
        self.upload_hist.append(stats['upload_mb'])
    
    def adaptive_scale(self, current_max: float, recent_data: list) -> float:
        """
        Ajusta dinámicamente la escala del gráfico
        
        Args:
            current_max: Máximo actual
            recent_data: Datos recientes
            
        Returns:
            Nuevo máximo escalado
        """
        if not recent_data:
            return current_max
        
        peak = max(recent_data) if recent_data else 0
        
        if peak < NET_IDLE_THRESHOLD:
            self.idle_counter += 1
            if self.idle_counter >= NET_IDLE_RESET_TIME:
                self.idle_counter = 0
                return NET_MAX_MB
        else:
            self.idle_counter = 0
        
        if peak > current_max * 0.8:
            new_max = peak * 1.2
        elif peak < current_max * 0.3:
            new_max = max(peak * 1.5, NET_MIN_SCALE)
        else:
            new_max = current_max
        
        return max(NET_MIN_SCALE, min(NET_MAX_SCALE, new_max))
    
    def update_dynamic_scale(self) -> None:
        """Actualiza la escala dinámica basada en el historial"""
        all_data = list(self.download_hist) + list(self.upload_hist)
        self.dynamic_max = self.adaptive_scale(self.dynamic_max, all_data)
    
    def get_history(self) -> Dict:
        """
        Obtiene historiales de red
        
        Returns:
            Diccionario con historiales
        """
        if not self._running:  # ── AÑADIDO ──
            return {'download': [], 'upload': [], 'dynamic_max': NET_MAX_MB}

        return {
            'download': list(self.download_hist),
            'upload': list(self.upload_hist),
            'dynamic_max': self.dynamic_max
        }
    
    def run_speedtest(self) -> None:
        """Ejecuta speedtest (Ookla CLI) en un thread separado"""
        if not self._running:  # ── AÑADIDO ──
            logger.warning("[NetworkMonitor] run_speedtest() ignorado — servicio parado")
            return

        def _run():
            logger.info("[NetworkMonitor] Iniciando speedtest...")
            self.speedtest_result["status"] = "running"
            try:
                result = subprocess.run(
                    ["speedtest", "--format=json", "--accept-license", "--accept-gdpr"],
                    capture_output=True,
                    text=True,
                    timeout=90
                )

                if result.returncode == 0:
                    data = json.loads(result.stdout)

                    # El nuevo CLI devuelve bytes/s → convertir a MB/s
                    ping     = data["ping"]["latency"]
                    download = data["download"]["bandwidth"] / 1_000_000
                    upload   = data["upload"]["bandwidth"]   / 1_000_000

                    self.speedtest_result.update({
                        "status":   "done",
                        "ping":     round(ping, 1),
                        "download": round(download, 2),
                        "upload":   round(upload, 2),
                    })
                    logger.info(
                        f"[NetworkMonitor] Speedtest completado — "
                        f"Ping: {ping:.1f}ms, ↓{download:.2f} MB/s, ↑{upload:.2f} MB/s"
                    )
                else:
                    logger.error(
                        f"[NetworkMonitor] speedtest retornó código {result.returncode}: {result.stderr}"
                    )
                    self.speedtest_result["status"] = "error"

            except subprocess.TimeoutExpired:
                logger.warning("[NetworkMonitor] Speedtest timeout (>90s)")
                self.speedtest_result["status"] = "timeout"
            except FileNotFoundError:
                logger.error(
                    "[NetworkMonitor] speedtest no encontrado. "
                    "Instala el CLI oficial de Ookla: https://www.speedtest.net/apps/cli"
                )
                self.speedtest_result["status"] = "error"
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"[NetworkMonitor] Error parseando resultado de speedtest: {e}")
                self.speedtest_result["status"] = "error"
            except Exception as e:
                logger.error(f"[NetworkMonitor] Error inesperado en speedtest: {e}")
                self.speedtest_result["status"] = "error"

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
    
    def get_speedtest_result(self) -> Dict:
        """
        Obtiene el resultado del speedtest
        
        Returns:
            Diccionario con resultados
        """
        return self.speedtest_result.copy()
    
    def reset_speedtest(self) -> None:
        """Resetea el estado del speedtest"""
        self.speedtest_result = {
            "status": "idle",
            "ping": 0,
            "download": 0.0,
            "upload": 0.0
        }
    
    @staticmethod
    def net_color(value: float) -> str:
        """
        Determina el color según el tráfico de red
        
        Args:
            value: Velocidad en MB/s
            
        Returns:
            Color en formato hex
        """
        if value >= NET_CRIT:
            return COLORS['danger']
        elif value >= NET_WARN:
            return COLORS['warning']
        else:
            return COLORS['primary']
