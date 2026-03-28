"""
core/i2c_monitor.py

Escaner I2C de solo lectura usando smbus2.
Detecta dispositivos en todos los buses /dev/i2c-* disponibles.

Arquitectura:
  - Thread daemon que escanea cada INTERVAL_SECONDS
  - get_stats() devuelve cache — nunca bloquea la UI
  - SOLO LECTURA: usa read_byte() para detectar ACK, nunca escribe
  - smbus2 es opcional — si no está instalado devuelve error descriptivo
"""
import threading
import os
from utils.logger import get_logger

logger = get_logger(__name__)

INTERVAL_SECONDS = 30

# Rango estándar de direcciones I2C válidas (evita reservadas)
_ADDR_MIN = 0x03
_ADDR_MAX = 0x77

# Nombres conocidos de dispositivos por dirección (referencia común)
_KNOWN_DEVICES = {
    0x20: "PCF8574 / MCP23017",
    0x21: "PCF8574 / MCP23017",
    0x22: "PCF8574 / MCP23017",
    0x23: "PCF8574 / MCP23017",
    0x27: "PCF8574 (LCD)",
    0x3C: "SSD1306 OLED",
    0x3D: "SSD1306 OLED",
    0x40: "INA219 / PCA9685",
    0x41: "INA219",
    0x48: "ADS1115 / TMP102",
    0x49: "ADS1115",
    0x4A: "ADS1115",
    0x4B: "ADS1115",
    0x57: "AT24C32 EEPROM",
    0x60: "MCP4725 DAC",
    0x68: "DS3231 RTC / MPU6050",
    0x69: "MPU6050",
    0x70: "TCA9548A Multiplexer",
    0x76: "BME280 / BMP280",
    0x77: "BME280 / BMP280",
}


class I2CMonitor:
    """
    Monitoriza el bus I2C mediante escaneo periódico y almacena en caché los resultados.
    No realiza escrituras en el bus, solo lectura.

    Args:
        Ninguno

    Returns:
        Ninguno

    Raises:
        Ninguno
    """

    def __init__(self):
        """
        Inicializa el monitor I2C con mecanismos de bloqueo y estado vacío.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._lock    = threading.Lock()
        self._stats   = {}
        self._running = False
        self._stop_evt = threading.Event()
        self._thread  = None

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Inicia el hilo daemon de escaneo periódico de monitoreo I2C.

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
        self._thread  = threading.Thread(
            target=self._loop, daemon=True, name="I2CMonitor")
        self._thread.start()
        logger.info("[I2CMonitor] Iniciado")

    def stop(self) -> None:
        """
        Detiene el monitor de I2C y limpia la caché de estadísticas.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        with self._lock:
            self._stats   = {}
        logger.info("[I2CMonitor] Detenido")
    
    def is_running(self) -> bool:
        """
        Indica si el monitor de I2C está actualmente en ejecución.

        Returns:
            bool: True si el monitor está escaneando, False en caso contrario.
        """
        return self._running

    # ── API pública ───────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """
        Retorna estadísticas thread-safe del último escaneo.

        Args:
            Ninguno

        Returns:
            dict: Diccionario con estadísticas, incluyendo 'error', 'buses' y 'total'.

        Raises:
            Ninguno
        """
        with self._lock:
            return dict(self._stats)

    def scan_now(self) -> None:
        """
        Fuerza un escaneo inmediato del bus I2C en un hilo daemon separado.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
        threading.Thread(
            target=self._scan, daemon=True, name="I2CScanNow").start()

    # ── Lógica interna ────────────────────────────────────────────────────────

    def _loop(self) -> None:
        """
        Ejecuta un bucle en un hilo daemon que realiza un escaneo inicial y luego 
        se repite a intervalos regulares hasta ser detenido.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._scan()
        while not self._stop_evt.wait(timeout=INTERVAL_SECONDS):
            if self._running:
                self._scan()

    def _scan(self) -> None:
        """
        Realiza un escaneo interno de buses I2C disponibles y cachea los resultados de manera thread-safe.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno

        Nota: En caso de error, se actualiza el estado con un mensaje de error y una lista vacía de buses.
        """
        try:
            import smbus2
        except ImportError:
            with self._lock:
                self._stats = {
                    "error":  "smbus2 no instalado — ejecuta: pip install smbus2",
                    "buses":  [],
                    "total":  0,
                }
            return

        
        # Detectar buses disponibles
        buses = sorted([
            int(f[5:]) for f in os.listdir("/dev")
            if f.startswith("i2c-") and f[5:].isdigit()
        ])

        if not buses:
            with self._lock:
                self._stats = {
                    "error": "No se encontraron buses I2C en /dev/i2c-*",
                    "buses": [],
                    "total": 0,
                }
            return

        result_buses = []
        total = 0

        for bus_num in buses:
            devices = []
            try:
                bus = smbus2.SMBus(bus_num)
                for addr in range(_ADDR_MIN, _ADDR_MAX + 1):
                    try:
                        bus.read_byte(addr)
                        name = _KNOWN_DEVICES.get(addr, "Desconocido")
                        devices.append({
                            "addr":     addr,
                            "addr_hex": f"0x{addr:02X}",
                            "name":     name,
                        })
                    except OSError:
                        pass   # Sin ACK — dirección vacía
                bus.close()
            except Exception as e:
                logger.debug("[I2CMonitor] Bus %d error: %s", bus_num, e)
                pass
            result_buses.append({
                "bus":     bus_num,
                "label":   f"i2c-{bus_num}",
                "devices": devices,
                "count":   len(devices),
            })
            total += len(devices)

        with self._lock:
            self._stats = {
                "error": "",
                "buses": result_buses,
                "total": total,
            }
        logger.debug("[I2CMonitor] Escaneo completado: %d dispositivo(s) en %d bus(es)",
                    total, len(buses))
