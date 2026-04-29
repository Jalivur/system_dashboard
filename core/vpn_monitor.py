"""
Monitor de estado de VPN dual (OpenVPN + WireGuard).

Monitoriza simultáneamente las interfaces tun0 (OpenVPN) y wg0 (WireGuard).
Sin dependencias nuevas — usa subprocess con comandos estándar.
"""
import subprocess
import threading
import time
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Interfaces monitorizadas ──────────────────────────────────────────────────
VPN_INTERFACES = {
    "openvpn":   "tun0",
    "wireguard": "wg0",
}

# Intervalo de sondeo (segundos)
CHECK_INTERVAL = 10


class VpnMonitor:
    """
    Servicio background que monitoriza el estado de ambas VPNs simultáneamente.

    Expone estado independiente para OpenVPN (tun0) y WireGuard (wg0).
    Sigue el patrón daemon estándar del proyecto.
    """

    def __init__(self):
        """
        Inicializa el monitor VPN dual.

        Configura el lock, el estado inicial desconectado para ambas VPNs
        y el evento de parada.
        """
        self._lock     = threading.Lock()
        self._running  = False
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Caché de estado — una entrada por VPN
        self._state: dict[str, dict] = {
            key: {"connected": False, "ip": "", "interface": iface}
            for key, iface in VPN_INTERFACES.items()
        }

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Inicia el sondeo de ambas VPNs en segundo plano.

        Returns:
            None
        """
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="VpnMonitor"
        )
        self._thread.start()
        logger.info("[VpnMonitor] Sondeo iniciado (cada %ds) — interfaces: %s",
                    CHECK_INTERVAL, list(VPN_INTERFACES.values()))

    def stop(self) -> None:
        """
        Detiene el servicio de monitoreo de forma limpia.

        Returns:
            None
        """
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        with self._lock:
            for key in self._state:
                self._state[key]["connected"] = False
                self._state[key]["ip"]        = ""
        logger.info("[VpnMonitor] Servicio detenido")

    def is_running(self) -> bool:
        """
        Indica si el servicio está activo.

        Returns:
            bool: True si el servicio está corriendo.
        """
        return self._running

    # ── Bucle de sondeo ───────────────────────────────────────────────────────

    def _loop(self) -> None:
        """
        Bucle principal del thread de sondeo.

        Sondea ambas interfaces en cada iteración.

        Returns:
            None
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
        Actualiza el estado de ambas VPNs en la caché.

        Returns:
            None
        """
        new_state = {}
        for key, iface in VPN_INTERFACES.items():
            connected, ip = self._check_interface(iface)
            new_state[key] = {
                "connected": connected,
                "ip":        ip,
                "interface": iface,
            }
        with self._lock:
            self._state = new_state

    def _check_interface(self, iface: str) -> tuple[bool, str]:
        """
        Comprueba si una interfaz de red está activa y obtiene su IPv4.

        Args:
            iface (str): Nombre de la interfaz de red a comprobar.

        Returns:
            tuple[bool, str]: (conectada, ip). ip vacío si no hay IP asignada.
        """
        try:
            result = subprocess.run(
                ["ip", "addr", "show", iface],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return False, ""
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("inet ") and "inet6" not in line:
                    ip = line.split()[1].split("/")[0]
                    return True, ip
            return False, ""
        except FileNotFoundError:
            return self._check_interface_ifconfig(iface)
        except Exception as e:
            logger.debug("[VpnMonitor] Error comprobando interfaz %s: %s", iface, e)
            return False, ""

    def _check_interface_ifconfig(self, iface: str) -> tuple[bool, str]:
        """
        Fallback: comprueba la interfaz usando ifconfig.

        Args:
            iface (str): Nombre de la interfaz de red a verificar.

        Returns:
            tuple[bool, str]: (conectada, ip).
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
                    idx   = parts.index("inet")
                    return True, parts[idx + 1]
            return False, ""
        except Exception:
            return False, ""

    # ── API pública ───────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        """
        Devuelve el estado actual de ambas VPNs desde caché.

        Returns:
            dict: {"openvpn": {"connected", "ip", "interface"},
                   "wireguard": {"connected", "ip", "interface"}}
        """
        if not self._running:
            return {
                key: {"connected": False, "ip": "", "interface": iface}
                for key, iface in VPN_INTERFACES.items()
            }
        with self._lock:
            return {k: dict(v) for k, v in self._state.items()}

    def is_connected(self) -> bool:
        """
        Indica si alguna de las VPNs está activa.

        Returns:
            bool: True si al menos una interfaz VPN tiene IP asignada.
        """
        with self._lock:
            return any(v["connected"] for v in self._state.values())

    def get_offline_count(self) -> int:
        """
        Devuelve el número de VPNs desconectadas.

        Usado por el sistema de badges del dashboard.

        Returns:
            int: 0 si alguna VPN está conectada, 1 si ninguna lo está.
        """
        with self._lock:
            any_connected = any(v["connected"] for v in self._state.values())
            return 0 if any_connected else 1

    def force_poll(self) -> None:
        """
        Fuerza una comprobación inmediata del estado en un hilo separado.

        Útil después de eventos de conexión o desconexión manual.

        Returns:
            None
        """
        if not self._running:
            return
        threading.Thread(
            target=self._poll, daemon=True, name="VpnMonitor-ForcePoll"
        ).start()
