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
    Servicio background que monitoriza el estado de la VPN.
    Lee las interfaces de red para determinar si VPN está activa.
    """

    def __init__(self, interface: str = VPN_INTERFACE):
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
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        self._status = {'connected': False, 'interface': '', 'ip': ''}
        logger.info("[VpnMonitor] Servicio detenido")

    # ── Bucle de sondeo ───────────────────────────────────────────────────────

    def _loop(self) -> None:
        while self._running:
            try:
                self._poll()
            except Exception as e:
                logger.error("[VpnMonitor] Error en _loop: %s", e)
            self._stop_evt.wait(timeout=CHECK_INTERVAL)
            if self._stop_evt.is_set():
                break

    def _poll(self) -> None:
        """Lee el estado de la interfaz VPN."""
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
        """Fallback usando ifconfig si 'ip' no está disponible."""
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
        """Devuelve el estado actual de la VPN desde caché."""
        if not self._running:
            return {'connected': False, 'interface': '', 'ip': ''}
        with self._lock:
            return {
                "connected": self._connected,
                "ip":        self._vpn_ip,
                "interface": self._interface,
            }

    def is_connected(self) -> bool:
        """True si la VPN está activa."""
        with self._lock:
            return self._connected

    def get_offline_count(self) -> int:
        """Devuelve 1 si VPN está desconectada (para badge en menú), 0 si conectada."""
        with self._lock:
            return 0 if self._connected else 1

    def force_poll(self) -> None:
        """Fuerza una comprobación inmediata (útil tras conectar/desconectar)."""
        if not self._running:
            return
        threading.Thread(target=self._poll, daemon=True).start()