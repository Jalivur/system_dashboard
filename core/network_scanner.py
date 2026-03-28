"""
Escáner de red local usando arp-scan.
Requiere: sudo arp-scan (disponible en Kali por defecto)

Ejecuta arp-scan en un thread de background para no bloquear la UI.
"""
import subprocess
import threading
import socket
import re
import time
from typing import List, Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

ARP_TIMEOUT = 15

_ARP_LINE = re.compile(
    r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\t([\da-fA-F:]{17})\t(.*)$'
)


class NetworkScanner:
    """
    Activa el escáner de red para iniciar el proceso de detección de dispositivos.

    Args:
        Ninguno

    Returns:
        Ninguno

    Raises:
        Ninguno
    """

    def __init__(self):
        """
        Inicializa el NetworkScanner con listas de dispositivos y estado.

        Args: Ninguno

        Returns: Ninguno

        Raises: Ninguno
        """
        self._devices: List[Dict]       = []
        self._status                    = "idle"
        self._error                     = ""
        self._last_scan: Optional[float] = None
        self._lock                      = threading.Lock()
        self._running                   = True

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Inicia el escaneo de red.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._running = True
        logger.info("[NetworkScanner] Iniciado")

    def stop(self) -> None:
        """
        Detiene el escaneo de red y limpia la caché de dispositivos y estados.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
        self._running = False
        with self._lock:
            self._devices = []
            self._status  = "idle"
            self._error   = ""
        logger.info("[NetworkScanner] Detenido")
    
    def is_running(self) -> bool:
        """
        Indica si el servicio de escaneo de red está actualmente en ejecución.

        Args:
            None

        Returns:
            bool: True si el servicio está corriendo, False en caso contrario.

        Raises:
            None
        """
        return self._running

    # ── API pública ───────────────────────────────────────────────────────────

    def scan(self) -> None:
        """
        Inicia el escaneo de la red en segundo plano si no hay uno en curso.

        Args: Ninguno

        Returns: Ninguno

        Raises: Ninguno
        """
        if not self._running:
            logger.warning("[NetworkScanner] scan() ignorado — servicio parado")
            return
        with self._lock:
            if self._status == "scanning":
                return
            self._status = "scanning"
        threading.Thread(target=self._do_scan, daemon=True, name="ARPScan").start()
        logger.info("[NetworkScanner] Escaneo iniciado")

    def get_devices(self) -> List[Dict]:
        """
        Devuelve la lista de dispositivos del último escaneo almacenada en caché.

        Args:
            Ninguno

        Returns:
            List[Dict]: Lista de dispositivos detectados en el último escaneo.

        Raises:
            Ninguno
        """
        with self._lock:
            return list(self._devices)

    def get_status(self) -> str:
        """
        Obtiene el estado actual del escaneo de red.

        Args:
            Ninguno

        Returns:
            str: Estado actual del escaneo, puede ser 'idle', 'scanning', 'done' o 'error'.

        Raises:
            Ninguno
        """
        with self._lock:
            return self._status

    def get_error(self) -> str:
        """
        Obtiene el mensaje de error registrado en el escáner de red.

        Args:
            Ninguno

        Returns:
            str: El mensaje de error registrado.

        Raises:
            Ninguno
        """
        with self._lock:
            return self._error

    def get_last_scan_age(self) -> Optional[float]:
        """
        Devuelve la edad del último escaneo completado en segundos.

        Args:
            None

        Returns:
            float: Edad del último escaneo en segundos. 
            None: Si nunca se ha realizado un escaneo.

        Raises:
            None
        """
        with self._lock:
            if self._last_scan is None:
                return None
            return time.time() - self._last_scan

    # ── Escaneo ───────────────────────────────────────────────────────────────

    def _do_scan(self) -> None:
        """
        Ejecuta arp-scan para detectar dispositivos en la red local y parsea el resultado.

        Args: Ninguno

        Returns: Ninguno

        Raises: 
        - RuntimeError: Si arp-scan devuelve un código de salida distinto de cero.
        - subprocess.TimeoutExpired: Si arp-scan excede el tiempo límite establecido.
        - FileNotFoundError: Si no se encuentran archivos necesarios para arp-scan.
        """
        try:
            result = subprocess.run(
                [
                    "sudo", "arp-scan", "--localnet",
                    "--ouifile=/usr/share/arp-scan/ieee-oui.txt",
                    "--macfile=/etc/arp-scan/mac-vendor.txt",
                ],
                capture_output=True, text=True, timeout=ARP_TIMEOUT,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"arp-scan salió con código {result.returncode}: {result.stderr.strip()}"
                )
            devices = self._parse_output(result.stdout)
            with self._lock:
                self._devices   = devices
                self._status    = "done"
                self._last_scan = time.time()
                self._error     = ""
            logger.info("[NetworkScanner] Escaneo completado — %d dispositivos", len(devices))

        except subprocess.TimeoutExpired:
            with self._lock:
                self._status = "error"
                self._error  = f"Timeout ({ARP_TIMEOUT}s) — red puede ser grande"
            logger.warning("[NetworkScanner] Timeout en arp-scan")

        except FileNotFoundError:
            with self._lock:
                self._status = "error"
                self._error  = "arp-scan no encontrado — instalar con: sudo apt install arp-scan"
            logger.error("[NetworkScanner] arp-scan no instalado")

        except Exception as e:
            with self._lock:
                self._status = "error"
                self._error  = str(e)
            logger.error("[NetworkScanner] Error en escaneo: %s", e)

    def _parse_output(self, output: str) -> list:
        """
        Parsea la salida de arp-scan para extraer información de dispositivos en la red.

        Args:
            output (str): La salida de arp-scan a parsear.

        Returns:
            list: Una lista de diccionarios ordenados con la información de cada dispositivo, 
                  incluyendo IP, MAC, proveedor y nombre de host.

        Raises:
            None
        """
        devices = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith(('Interface:', 'Starting', 'WARNING', 'Ending')):
                continue
            if 'packets' in line or 'hosts' in line:
                continue

            m = _ARP_LINE.match(line)
            if not m:
                continue

            ip     = m.group(1)
            mac    = m.group(2).upper()
            vendor = m.group(3).strip().strip('()')
            vendor = vendor if vendor and vendor.lower() != 'unknown' else ""

            devices.append({
                "ip":       ip,
                "mac":      mac,
                "vendor":   vendor,
                "hostname": self._resolve_hostname(ip),
            })

        devices.sort(key=lambda d: tuple(int(x) for x in d["ip"].split(".")))
        return devices

    @staticmethod
    def _resolve_hostname(ip: str) -> str:
        """
        Resuelve el hostname asociado a una dirección IP.

        Args:
            ip (str): La dirección IP a resolver.

        Returns:
            str: El hostname asociado a la IP, o cadena vacía si falla la resolución.

        Raises:
            Exception: Si ocurre un error durante la resolución.
        """
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return ""
