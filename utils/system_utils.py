"""
Utilidades para obtener información del sistema
"""
import re
import socket
import psutil
import subprocess
import glob
from typing import Tuple, Dict, Optional, Any
from collections import namedtuple
from config.settings import UPDATE_MS
import json
from utils.logger import get_logger

logger = get_logger(__name__)


class SystemUtils:
    """Utilidades para interactuar con el sistema"""
    
    # Variable de clase para mantener estado de red entre llamadas
    _last_net_io = {}
    
    @staticmethod
    def get_cpu_temp() -> float:
        """
        Obtiene la temperatura de la CPU
        
        Returns:
            Temperatura en grados Celsius
        """
        # Método 1: vcgencmd (Raspberry Pi - método oficial)
        try:
            out = subprocess.check_output(
                ["vcgencmd", "measure_temp"],
                universal_newlines=True,
                timeout=2
            )
            temp_str = out.replace("temp=", "").replace("'C", "").strip()
            return float(temp_str)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        except ValueError as e:
            logger.warning(f"[SystemUtils] get_cpu_temp: formato inesperado de vcgencmd: {e}")
        
        # Método 2: sensors (Linux genérico)
        try:
            out = subprocess.check_output(["sensors"], universal_newlines=True, timeout=2)
            for line in out.split('\n'):
                if 'Package id 0:' in line or 'Tdie:' in line or 'CPU:' in line:
                    m = re.search(r'[\+\-](\d+\.\d+).C', line)
                    if m:
                        return float(m.group(1))
                        
            for line in out.split('\n'):
                if 'temp' in line.lower():
                    m = re.search(r'[\+\-](\d+\.\d+).C', line)
                    if m:
                        return float(m.group(1))
        except subprocess.TimeoutExpired:
            logger.warning("[SystemUtils] get_cpu_temp: timeout leyendo sensors")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Método 3: Fallback - leer de thermal_zone
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                val = f.read().strip()
                return float(val) / 1000.0
        except FileNotFoundError:
            logger.warning("[SystemUtils] get_cpu_temp: no se encontró thermal_zone0, retornando 0.0")
        except ValueError as e:
            logger.error(f"[SystemUtils] get_cpu_temp: error leyendo thermal_zone0: {e}")
        
        return 0.0
    
    @staticmethod
    def get_hostname() -> str:
        """
        Obtiene el nombre del host
        
        Returns:
            Nombre del host o "unknown"
        """
        try:
            return socket.gethostname()
        except Exception as e:
            logger.warning(f"[SystemUtils] get_hostname: {e}")
            return "unknown"
    
    @staticmethod
    def get_net_io(interface: Optional[str] = None) -> Tuple[str, Any]:
        """
        Obtiene estadísticas de red con auto-detección de interfaz activa
        
        Args:
            interface: Nombre de la interfaz o None para auto-detección
            
        Returns:
            Tupla (nombre_interfaz, estadísticas)
        """
        if not SystemUtils._last_net_io:
            SystemUtils._last_net_io = psutil.net_io_counters(pernic=True)
        
        stats = psutil.net_io_counters(pernic=True)
        
        if interface and interface in stats:
            SystemUtils._last_net_io = stats
            return interface, stats[interface]
        
        best_name = None
        best_speed = -1
        
        for name in stats:
            if name not in SystemUtils._last_net_io:
                continue
            
            curr = stats[name]
            prev = SystemUtils._last_net_io[name]
            
            speed = (
                (curr.bytes_recv - prev.bytes_recv) +
                (curr.bytes_sent - prev.bytes_sent)
            )
            
            if speed < 0 or speed > 500 * 1024 * 1024:
                continue
            
            if speed > best_speed:
                best_speed = speed
                best_name = name
        
        SystemUtils._last_net_io = stats
        
        if best_name:
            return best_name, stats[best_name]
        
        for iface, s in stats.items():
            if iface.startswith(('eth', 'enp', 'wlan', 'wlp', 'tun')):
                if s.bytes_sent > 0 or s.bytes_recv > 0:
                    return iface, s
        
        if stats:
            first = list(stats.items())[0]
            return first[0], first[1]
        
        EmptyStats = namedtuple('EmptyStats', 
            ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv',
             'errin', 'errout', 'dropin', 'dropout'])
        return "none", EmptyStats(0, 0, 0, 0, 0, 0, 0, 0)
    
    @staticmethod
    def safe_net_speed(current: Any, previous: Optional[Any]) -> Tuple[float, float]:
        """
        Calcula velocidad de red de forma segura
        
        Args:
            current: Estadísticas actuales
            previous: Estadísticas anteriores
            
        Returns:
            Tupla (download_mb, upload_mb)
        """
        if previous is None:
            return 0.0, 0.0
        
        try:
            dl_bytes = max(0, current.bytes_recv - previous.bytes_recv)
            ul_bytes = max(0, current.bytes_sent - previous.bytes_sent)
            
            seconds = UPDATE_MS / 1000.0
            
            dl_mb = (dl_bytes / (1024 * 1024)) / seconds
            ul_mb = (ul_bytes / (1024 * 1024)) / seconds
            
            return dl_mb, ul_mb
        except (AttributeError, TypeError) as e:
            logger.warning(f"[SystemUtils] safe_net_speed: error calculando velocidad de red: {e}")
            return 0.0, 0.0
    
    @staticmethod
    def list_usb_storage_devices() -> list:
        """
        Lista dispositivos USB de almacenamiento (discos)
        
        Returns:
            Lista de diccionarios con información de almacenamiento USB
        """
        storage_devices = []
        
        try:
            result = subprocess.run(
                ['lsblk', '-o', 'NAME,MODEL,TRAN,MOUNTPOINT,SIZE,TYPE', '-J'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                for block in data.get('blockdevices', []):
                    if block.get('tran') == 'usb':
                        dev = {
                            'name': block.get('model', 'USB Disk').strip(),
                            'type': block.get('type', 'disk'),
                            'mount': block.get('mountpoint'),
                            'dev': '/dev/' + block.get('name', ''),
                            'size': block.get('size', ''),
                            'children': []
                        }
                        
                        for child in block.get('children', []):
                            child_dev = {
                                'name': child.get('name', ''),
                                'type': child.get('type', 'part'),
                                'mount': child.get('mountpoint'),
                                'dev': '/dev/' + child.get('name', ''),
                                'size': child.get('size', '')
                            }
                            dev['children'].append(child_dev)
                        
                        storage_devices.append(dev)
            else:
                logger.warning(f"[SystemUtils] list_usb_storage_devices: lsblk retornó código {result.returncode}")
        
        except subprocess.TimeoutExpired:
            logger.error("[SystemUtils] list_usb_storage_devices: timeout ejecutando lsblk")
        except FileNotFoundError:
            logger.error("[SystemUtils] list_usb_storage_devices: lsblk no encontrado")
        except json.JSONDecodeError as e:
            logger.error(f"[SystemUtils] list_usb_storage_devices: error parseando JSON de lsblk: {e}")
        
        return storage_devices
    
    @staticmethod
    def list_usb_other_devices() -> list:
        """
        Lista otros dispositivos USB (no almacenamiento)
        
        Returns:
            Lista de strings con información de dispositivos USB
        """
        try:
            result = subprocess.run(
                ['lsusb'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                devices = [line for line in result.stdout.strip().split('\n') if line]
                return devices
            else:
                logger.warning(f"[SystemUtils] list_usb_other_devices: lsusb retornó código {result.returncode}")
            
        except subprocess.TimeoutExpired:
            logger.error("[SystemUtils] list_usb_other_devices: timeout ejecutando lsusb")
        except FileNotFoundError:
            logger.error("[SystemUtils] list_usb_other_devices: lsusb no encontrado")
        
        return []
    
    @staticmethod
    def list_usb_devices() -> list:
        """
        Lista TODOS los dispositivos USB (mantener para compatibilidad)
        
        Returns:
            Lista de strings con lsusb
        """
        return SystemUtils.list_usb_other_devices()
    
    @staticmethod
    def eject_usb_device(device: dict) -> Tuple[bool, str]:
        """
        Expulsa un dispositivo USB de forma segura
        
        Args:
            device: Diccionario con información del dispositivo
                   (debe tener 'children' con particiones)
        
        Returns:
            Tupla (success: bool, message: str)
        """
        device_name = device.get('name', 'desconocido')
        
        try:
            unmounted = []
            for partition in device.get('children', []):
                if partition.get('mount'):
                    result = subprocess.run(
                        ['udisksctl', 'unmount', '-b', partition['dev']],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        unmounted.append(partition['name'])
                        logger.info(f"[SystemUtils] Partición {partition['name']} desmontada correctamente")
                    else:
                        logger.error(f"[SystemUtils] Error desmontando {partition['name']}: {result.stderr}")
                        return (False, f"Error desmontando {partition['name']}: {result.stderr}")
            
            if unmounted:
                logger.info(f"[SystemUtils] Dispositivo '{device_name}' expulsado: {', '.join(unmounted)}")
                return (True, f"Desmontado correctamente: {', '.join(unmounted)}")
            else:
                logger.info(f"[SystemUtils] Dispositivo '{device_name}': no había particiones montadas")
                return (True, "No había particiones montadas")
        
        except subprocess.TimeoutExpired:
            logger.error(f"[SystemUtils] eject_usb_device: timeout desmontando '{device_name}'")
            return (False, "Timeout al desmontar el dispositivo")
        except FileNotFoundError:
            logger.error("[SystemUtils] eject_usb_device: udisksctl no encontrado")
            return (False, "udisksctl no encontrado. Instala: sudo apt-get install udisks2")
        except Exception as e:
            logger.error(f"[SystemUtils] eject_usb_device: error inesperado con '{device_name}': {e}")
            return (False, f"Error: {str(e)}")
    
    @staticmethod
    def run_script(script_path: str) -> Tuple[bool, str]:
        """
        Ejecuta un script de sistema
        
        Args:
            script_path: Ruta al script
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["bash", script_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"[SystemUtils] Script ejecutado correctamente: {script_path}")
                return True, "Script ejecutado exitosamente"
            else:
                logger.error(f"[SystemUtils] Script falló ({script_path}): {result.stderr}")
                return False, f"Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            logger.error(f"[SystemUtils] run_script: timeout ejecutando {script_path}")
            return False, "Timeout: El script tardó demasiado"
        except FileNotFoundError:
            logger.error(f"[SystemUtils] run_script: script no encontrado: {script_path}")
            return False, f"Script no encontrado: {script_path}"
        except Exception as e:
            logger.error(f"[SystemUtils] run_script: error inesperado ({script_path}): {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def get_interfaces_ips() -> Dict[str, str]:
        """
        Obtiene las IPs de todas las interfaces de red
        
        Returns:
            Diccionario {interfaz: IP}
        """
        result = {}
        try:
            addrs = psutil.net_if_addrs()
            for iface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family == socket.AF_INET:
                        result[iface] = addr.address
                        break
        except Exception as e:
            logger.warning(f"[SystemUtils] get_interfaces_ips: {e}")
        
        return result
    
    @staticmethod
    def get_nvme_temp() -> float:
        """
        Obtiene la temperatura del disco NVMe.
        Solo lee sensores asociados a dispositivos NVMe reales.

        Returns:
            Temperatura en °C o 0.0 si no hay NVMe o no se puede leer
        """
        # Método 1: smartctl
        try:
            result = subprocess.run(
                ["sudo", "smartctl", "-a", "/dev/nvme0"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Temperature:' in line or 'Temperature Sensor' in line:
                        match = re.search(r'(\d+)\s*Celsius', line)
                        if match:
                            return float(match.group(1))
            else:
                logger.debug(f"[SystemUtils] get_nvme_temp: smartctl retornó código {result.returncode}")
        except subprocess.TimeoutExpired:
            logger.warning("[SystemUtils] get_nvme_temp: timeout ejecutando smartctl")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Método 2: sysfs — solo hwmon asociado a dispositivos NVMe reales
        try:
            for temp_file in glob.glob("/sys/block/nvme*/device/hwmon/hwmon*/temp1_input"):
                with open(temp_file, 'r') as f:
                    return int(f.read().strip()) / 1000.0
        except (FileNotFoundError, ValueError, PermissionError):
            pass

        return 0.0
