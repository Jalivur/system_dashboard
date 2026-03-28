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

    Args:
        interface (str): Nombre de interfaz VPN (default "tun0").

    Características:
    * Configura lock para acceso thread-safe.
    * Estado inicial: desconectado.

    Atributos:
    * _interface: Nombre de interfaz VPN.
    * _lock: Lock para acceso thread-safe.
    * _running: Estado de ejecución.
    * _stop_evt: Evento de parada.
    * _thread: Hilo de ejecución.
    * _connected: Estado de conexión.
    * _vpn_ip: Dirección IP asignada.
    """

    def __init__(self, interface: str = VPN_INTERFACE):
        """
        Inicializa el monitor VPN.

        Args:
            interface (str): Nombre de interfaz VPN (por defecto "tun0").

        Configura el bloqueo, el estado inicial desconectado y el evento de parada.
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
        Inicia el sondeo de VPN en segundo plano.

        Args: 
            None

        Returns: 
            None

        Raises: 
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
        logger.info("[VpnMonitor] Sondeo iniciado (cada %ds) — interfaz: %s",
                    CHECK_INTERVAL, self._interface)

    def stop(self) -> None:
        """
        Detiene el servicio de monitoreo de VPN de manera limpia.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
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
        """
        Indica si el servicio de monitoreo de VPN está actualmente en ejecución.

        Args:
            None

        Returns:
            bool: True si el servicio está corriendo, False en caso contrario.

        Raises:
            None
        """
        return self._running

    # ── Bucle de sondeo ───────────────────────────────────────────────────────

    def _loop(self) -> None:
        """
        Ejecuta el bucle principal del thread de sondeo.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno

        Nota: 
            Llama a _poll() y wait(CHECK_INTERVAL) en un ciclo, manejando excepciones.
            Se detiene cuando self._running es False o self._stop_evt está seteado.
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
        Actualiza el estado de la conexión VPN.

        Actualiza la caché protegida por bloqueo, llamando previamente a `_check_interface()`.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        connected, ip = self._check_interface(self._interface)
        with self._lock:
            self._connected = connected
            self._vpn_ip    = ip

    def _check_interface(self, iface: str):
        """
        Comprueba si una interfaz de red está activa y obtiene su dirección IP.

        Args:
            iface (str): Nombre de la interfaz de red a comprobar.

        Returns:
            tuple: Un tupla con dos valores, el primero indica si la interfaz está conectada (bool) y el segundo la dirección IP de la interfaz (str).

        Raises:
            Exception: Si ocurre un error durante la comprobación de la interfaz, se registra el error y se devuelve False junto con una cadena vacía.
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
        Verifica el estado de una interfaz de red y su dirección IP mediante ifconfig.

        Args:
            iface (str): Nombre de la interfaz de red a verificar.

        Returns:
            tuple[bool, str]: Tupla con un booleano que indica si la interfaz está conectada y la dirección IP asignada.

        Raises:
            Exception: Si ocurre un error durante la ejecución de ifconfig.
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
        Obtiene el estado actual de la VPN desde caché de manera segura para hilos.

        Args:
            None

        Returns:
            dict: Diccionario con el estado de la VPN. 
                  {"connected": bool, "ip": str, "interface": str}

        Raises:
            None
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
        Indica si la conexión VPN está actualmente activa.

        Args:
            None

        Returns:
            bool: True si la interfaz VPN tiene una IP IPv4 asignada.

        Raises:
            None
        """
        with self._lock:
            return self._connected

    def get_offline_count(self) -> int:
        """
        Obtiene el estado de conexión de la VPN para mostrar en la interfaz de usuario.

        Args:
            Ninguno

        Returns:
            int: 1 si la VPN está desconectada, 0 si está conectada.

        Raises:
            Ninguno
        """
        with self._lock:
            return 0 if self._connected else 1

    def force_poll(self) -> None:
        """
        Fuerza una comprobación inmediata del estado de la VPN en un hilo separado.

        Útil después de eventos de conexión o desconexión manual.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if not self._running:
            return
        threading.Thread(target=self._poll, daemon=True, name="VpnMonitor-ForcePoll").start()

