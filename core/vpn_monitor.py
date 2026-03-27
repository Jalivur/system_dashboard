"""
Monitor de estado de VPN.
Detecta si la interfaz VPN está activa leyendo /proc/net/if_inet6 o ip link.
Sin dependencias nuevas — usa subprocess con comandos estándar.
"""
import subprocess
import threading
import time
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Nombre de la interfaz VPN — ajusta según tu configuración
# WireGuard → "wg0"   |   OpenVPN → "tun0"
VPN_INTERFACE = "tun0"

# Intervalo de sondeo (segundos)
CHECK_INTERVAL = 10


class VpnMonitor:
    """
    Servicio background profesional que monitoriza el estado de la VPN.

    Características:
    * Sondeo cada 10s de estado de interfaz tun0/wg0 via 'ip addr' o fallback 'ifconfig'.
    * Extracción automática de IP IPv4 asignada si interfaz UP.
    * Thread daemon con lock para acceso thread-safe.
    * API pública: get_status(), is_connected(), get_offline_count() para UI badge.
    * force_poll() para comprobación inmediata.
    """

    def __init__(self, interface: str = VPN_INTERFACE):
        """
        Inicializa el monitor VPN.

        Args:
            interface (str): Nombre de interfaz VPN (default "tun0").

        Configura lock, estado inicial desconectado, event stop.
        """
        self._interface = interface
        self._lock      = threading.Lock()
        self._running   = False
        self._stop_evt  = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Caché de estado
        self._connected = False
        self._vpn_ip    = ""
        self._iface     = interface

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Inicia el sondeo background (thread daemon).

        Idempotente, log con intervalo e interfaz.
        """
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="VpnMonitor"
        )
        self._thread.start()
        logger.info("[VpnMonitor] Sondeo iniciado (cada %ds) — interfaz: %s",
                    CHECK_INTERVAL, self._interface)

    def stop(self) -> None:
        """
        Detiene el servicio limpiamente.

        Join timeout 5s, resetea caché. Log de detención.
        """
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        with self._lock:
            self._connected = False
            self._vpn_ip    = ""
        logger.info("[VpnMonitor] Servicio detenido")
        
    def is_running(self) -> bool:
        """Verifica si el servicio está corriendo."""
        return self._running

    # ── Bucle de sondeo ───────────────────────────────────────────────────────

    def _loop(self) -> None:
        """
        Bucle principal del thread de sondeo (privado).

        Llama _poll() + wait(CHECK_INTERVAL), maneja exceptions.
        """
        while self._running:
            try:
                self._poll()
            except Exception as e:
                logger.error("[VpnMonitor] Error en _loop: %s", e)
            self._stop_evt.wait(timeout=CHECK_INTERVAL)
            if self._stop_evt.is_set():
                break

    def _poll(self) -> None:
        """
        Actualiza estado de VPN (privado).

        Llama _check_interface(), actualiza caché protegida por lock.
        """
        connected, ip = self._check_interface(self._interface)
        with self._lock:
            self._connected = connected
            self._vpn_ip    = ip

    def _check_interface(self, iface: str):
        """
        Comprueba si la interfaz está activa y obtiene su IP.
        Devuelve (connected: bool, ip: str).
        """
        try:
            result = subprocess.run(
                ["ip", "addr", "show", iface],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return False, ""

            output = result.stdout
            # Buscar inet (IPv4)
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("inet ") and "inet6" not in line:
                    ip = line.split()[1].split("/")[0]
                    return True, ip
            # Interfaz existe pero sin IP asignada aún
            return False, ""
        except FileNotFoundError:
            # 'ip' no disponible — intentar con ifconfig
            return self._check_interface_ifconfig(iface)
        except Exception as e:
            logger.debug("[VpnMonitor] Error comprobando interfaz %s: %s", iface, e)
            return False, ""

    def _check_interface_ifconfig(self, iface: str):
        """
        Fallback usando ifconfig si 'ip' no está disponible (privado).
        
        Returns:
            tuple[bool, str]: (connected, ip)
        """
        try:
            result = subprocess.run(
                ["ifconfig", iface],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return False, ""
            for line in result.stdout.splitlines():
                line = line.strip()
                if "inet " in line:
                    parts = line.split()
                    idx = parts.index("inet")
                    ip = parts[idx + 1]
                    return True, ip
            return False, ""
        except Exception:
            return False, ""

    # ── API pública ───────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """
        Devuelve el estado actual de la VPN desde caché (thread-safe).

        Returns:
            dict: {"connected": bool, "ip": str, "interface": str}
        """
        if not self._running:
            return {'connected': False, 'interface': '', 'ip': ''}
        with self._lock:
            return {
                "connected": self._connected,
                "ip":        self._vpn_ip,
                "interface": self._interface,
            }

    def is_connected(self) -> bool:
        """
        Estado rápido de conexión VPN (thread-safe).

        Returns:
            bool: True si interfaz tiene IP IPv4 asignada.
        """
        with self._lock:
            return self._connected

    def get_offline_count(self) -> int:
        """
        Para badge UI: 1 si desconectada, 0 si conectada (thread-safe).

        Returns:
            int: 1 (offline) o 0 (online).
        """
        with self._lock:
            return 0 if self._connected else 1

    def force_poll(self) -> None:
        """
        Fuerza comprobación inmediata en thread separado.

        Útil tras eventos connect/disconnect manual.
        """
        if not self._running:
            return
        threading.Thread(target=self._poll, daemon=True, name="VpnMonitor-ForcePoll").start()

