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

# Timeout para arp-scan (segundos)
ARP_TIMEOUT = 15

# Regex para parsear líneas de arp-scan:
# Regex actualizado — fabricante con paréntesis opcional
_ARP_LINE = re.compile(
    r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\t([\da-fA-F:]{17})\t(.*)$'
)

class NetworkScanner:
    """
    Escáner de red local con arp-scan.

    Uso:
        scanner = NetworkScanner()
        scanner.scan()                    # lanza en background
        devices = scanner.get_devices()   # lee caché (no bloquea)
        status  = scanner.get_status()    # 'idle' | 'scanning' | 'done' | 'error'
    """

    def __init__(self):
        self._devices: List[Dict] = []
        self._status  = "idle"     # idle | scanning | done | error
        self._error   = ""
        self._last_scan: Optional[float] = None
        self._lock    = threading.Lock()
        self._running = True  # ── AÑADIDO ──

    # ── Gestión de ciclo de vida ──────────────────────────────────────────────

    def start(self) -> None:  # ── AÑADIDO ──
        self._running = True
        logger.info("[NetworkScanner] Iniciado")

    def stop(self) -> None:  # ── AÑADIDO ──
        self._running = False
        with self._lock:
            self._devices = []
            self._status  = "idle"
            self._error   = ""
        logger.info("[NetworkScanner] Detenido")

    # ── API pública ───────────────────────────────────────────────────────────

    def scan(self) -> None:
        """Lanza el escaneo en background. Si ya hay uno en curso, no hace nada."""
        if not self._running:  # ── AÑADIDO ──
            logger.warning("[NetworkScanner] scan() ignorado — servicio parado")
            return
        with self._lock:
            if self._status == "scanning":
                return
            self._status = "scanning"
        threading.Thread(target=self._do_scan, daemon=True, name="ARPScan").start()
        logger.info("[NetworkScanner] Escaneo iniciado")

    def get_devices(self) -> List[Dict]:
        """Devuelve la lista de dispositivos del último escaneo (caché)."""
        with self._lock:
            return list(self._devices)

    def get_status(self) -> str:
        """Estado actual: 'idle' | 'scanning' | 'done' | 'error'."""
        with self._lock:
            return self._status

    def get_error(self) -> str:
        """Mensaje de error si status == 'error'."""
        with self._lock:
            return self._error

    def get_last_scan_age(self) -> Optional[float]:
        """Segundos desde el último escaneo completado. None si nunca se ha escaneado."""
        with self._lock:
            if self._last_scan is None:
                return None
            return time.time() - self._last_scan

    # ── Escaneo ───────────────────────────────────────────────────────────────

    def _do_scan(self) -> None:
        """Ejecuta arp-scan y parsea el resultado."""
        try:
            result = subprocess.run(
                [
                    "sudo", "arp-scan", "--localnet",
                    "--ouifile=/usr/share/arp-scan/ieee-oui.txt",
                    "--macfile=/etc/arp-scan/mac-vendor.txt",
                ],
                capture_output=True,
                text=True,
                timeout=ARP_TIMEOUT,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"arp-scan salió con código {result.returncode}: {result.stderr.strip()}"
                )
            devices = self._parse_output(result.stdout)
            with self._lock:
                self._devices    = devices
                self._status     = "done"
                self._last_scan  = time.time()
                self._error      = ""
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
        devices = []
        for line in output.splitlines():
            line = line.strip()
            # Ignorar líneas de cabecera, pie y vacías
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
            vendor = m.group(3).strip().strip('()')  # quita los paréntesis de (Unknown)
            vendor = vendor if vendor and vendor.lower() != 'unknown' else ""

            hostname = self._resolve_hostname(ip)
            devices.append({
                "ip":       ip,
                "mac":      mac,
                "vendor":   vendor,
                "hostname": hostname,
            })

        devices.sort(key=lambda d: tuple(int(x) for x in d["ip"].split(".")))
        return devices

    @staticmethod
    def _resolve_hostname(ip: str) -> str:
        """Intenta resolver el hostname de una IP. Devuelve '' si falla."""
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return ""
