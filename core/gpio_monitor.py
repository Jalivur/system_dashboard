"""
Controlador de pines GPIO via gpiozero.

Soporta tres modos por pin:
  INPUT  — lectura de estado (Button sin pull interno)
  OUTPUT — escritura HIGH/LOW (LED de gpiozero)
  PWM    — señal PWM con duty cycle 0.0–1.0 (PWMLED de gpiozero)

Modos de operación globales:
  CONTROLANDO — dashboard reclama los pines con gpiozero.
                INPUT/OUTPUT/PWM operativos.
  LIBRE       — dashboard libera todos los pines (gpiozero cerrado).
                Los scripts externos pueden usar los pines sin conflictos.
                No se lee ningún estado de hardware.

Persistencia:
  La configuración de pines se guarda en local_settings.py via
  local_settings_io bajo la clave "gpio_pins_config".
  Formato: {bcm_pin_str: {"mode": str, "label": str}}
  Si no existe la clave se usa _DEFAULT_CONFIG.

Pines reservados por fase1.py — nunca tocar:
  I²C : GPIO 2 (SDA), 3 (SCL)
  PWM : GPIO 12, 13, 18, 19 (hardware PWM ventiladores)
  UART: GPIO 14, 15
"""
import threading
import gpiozero
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
from config.local_settings_io import update_params, read
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Modos de pin ──────────────────────────────────────────────────────────────
MODE_INPUT  = "INPUT"
MODE_OUTPUT = "OUTPUT"
MODE_PWM    = "PWM"
VALID_MODES = (MODE_INPUT, MODE_OUTPUT, MODE_PWM)

# ── Modos de operación global ─────────────────────────────────────────────────
OP_CONTROLANDO = "CONTROLANDO"
OP_LIBRE       = "LIBRE"

# ── Pines reservados ──────────────────────────────────────────────────────────
_RESERVED_PINS = {2, 3, 12, 13, 14, 15, 18, 19}

# ── Clave de persistencia en local_settings.py ───────────────────────────────
_SETTINGS_KEY = "gpio_pins_config"

# ── Configuración por defecto ─────────────────────────────────────────────────
_DEFAULT_CONFIG = {
    4:  {"mode": MODE_INPUT,  "label": "GPIO 4"},
    17: {"mode": MODE_INPUT,  "label": "GPIO 17"},
    27: {"mode": MODE_INPUT,  "label": "GPIO 27"},
    22: {"mode": MODE_INPUT,  "label": "GPIO 22"},
    10: {"mode": MODE_INPUT,  "label": "GPIO 10 (MOSI)"},
    9:  {"mode": MODE_INPUT,  "label": "GPIO 9  (MISO)"},
    11: {"mode": MODE_INPUT,  "label": "GPIO 11 (SCLK)"},
    5:  {"mode": MODE_OUTPUT, "label": "GPIO 5"},
    6:  {"mode": MODE_OUTPUT, "label": "GPIO 6"},
    16: {"mode": MODE_PWM,    "label": "GPIO 16"},
    20: {"mode": MODE_INPUT,  "label": "GPIO 20"},
    21: {"mode": MODE_INPUT,  "label": "GPIO 21"},
}


def _load_config() -> dict[int, dict]:
    """
    Carga la configuración de pines desde local_settings_io y devuelve un diccionario con pines como claves enteras y configuraciones como valores.

    Args: 
        Ninguno

    Returns:
        dict[int, dict]: Diccionario con pines como claves enteras y configuraciones como valores.

    Raises:
        Ninguna excepción específica, aunque se registran warnings en caso de errores.
    """
    try:
        params, _ = read()
        raw = params.get(_SETTINGS_KEY)
        if raw and isinstance(raw, dict):
            return {
                int(pin): dict(cfg)
                for pin, cfg in raw.items()
                if int(pin) not in _RESERVED_PINS
            }
    except Exception as exc:
        logger.warning("[GPIOMonitor] Error leyendo config persistida: %s", exc)
    return {pin: dict(cfg) for pin, cfg in _DEFAULT_CONFIG.items()}


def _save_config(pins_cfg: dict[int, dict]) -> None:
    """
    Persiste la configuración de pines en local_settings.py de manera segura.

    Args:
        pins_cfg: Diccionario con configuración de pines, donde cada clave es un pin y cada valor es otro diccionario con la configuración.

    Returns:
        None

    Raises:
        Exception: Si ocurre un error al guardar la configuración.
    """
    try:
        serializable = {str(pin): dict(cfg) for pin, cfg in pins_cfg.items()}
        update_params({_SETTINGS_KEY: serializable})
        logger.debug("[GPIOMonitor] Config persistida (%d pines)", len(pins_cfg))
    except Exception as exc:
        logger.warning("[GPIOMonitor] Error guardando config: %s", exc)


class GPIOMonitor:
    """
    Gestiona el estado y configuración de pines GPIO.

    La clase proporciona información sobre el estado de cada pin, incluyendo su modo (INPUT, OUTPUT o PWM), 
    etiqueta descriptiva, valor actual y ciclo de trabajo en caso de PWM.

    Args:
        config (dict, optional): Configuración de pines. Por defecto, carga configuración desde local_settings.
        op_mode (str): Modo de operación, OP_LIBRE o OP_CONTROLANDO.

    Returns:
        None

    Raises:
        None
    """

    POLL_INTERVAL = 1.0

    def __init__(self, config: dict | None = None, op_mode: str = OP_LIBRE):
        """
        Inicializa el monitor de GPIO con la configuración proporcionada.

        Args:
            config (dict, optional): Configuración de pines. Por defecto, carga la configuración desde local_settings.
            op_mode (str): Modo de operación, puede ser OP_LIBRE o OP_CONTROLANDO.

        Returns:
            None

        Raises:
            None
        """
        # Si no se pasa config explícita, cargar desde local_settings
        raw = config if config is not None else _load_config()
        self._pins_cfg: dict[int, dict] = {
            pin: dict(cfg) for pin, cfg in raw.items()
            if pin not in _RESERVED_PINS
        }

        self._lock     = threading.Lock()
        self._stop_evt = threading.Event()
        self._thread: threading.Thread | None = None
        self._running  = False

        self._op_mode        = op_mode
        self._gpio_available = False
        self._gz             = None
        self._devices: dict[int, object] = {}

        self._state: dict[int, dict] = {}
        self._init_state()


    # ── Estado inicial ────────────────────────────────────────────────────────

    def _init_state(self):
        """
        Inicializa el estado de los pines GPIO de manera thread-safe.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        with self._lock:
            self._state = {
                pin: {
                    "mode":  cfg.get("mode", MODE_INPUT),
                    "label": cfg.get("label", f"GPIO {pin}"),
                    "value": None,
                    "duty":  0.0,
                    "error": None,
                }
                for pin, cfg in self._pins_cfg.items()
            }


    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self):
        """
        Inicia el hilo daemon de monitoreo de GPIO con un intervalo de polling de 1 segundo.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="GPIOMonitor")
        self._thread.start()
        logger.info("[GPIOMonitor] Iniciado — op=%s pines=%s",
                    self._op_mode, sorted(self._pins_cfg))


    def stop(self):
        """
        Detiene el monitor de GPIO, liberando recursos y deteniendo el hilo de ejecución.

        Args: None

        Returns: None

        Raises: None
        """
        if not self._running:
            return
        self._stop_evt.set()
        if self._thread:
            self._thread.join(timeout=5)
        self._release_devices()
        self._running = False
        logger.info("[GPIOMonitor] Detenido")


    def is_running(self) -> bool:
        """
        Indica si el monitor de GPIO está actualmente en ejecución.

        Args:
            Ninguno

        Returns:
            bool: True si el monitor está corriendo, False en caso contrario.

        Raises:
            Ninguno
        """
        return self._running


    # ── Thread ────────────────────────────────────────────────────────────────

    def _run(self):
        """
        Ejecuta el bucle principal del thread daemon.

        Setup dispositivos si se está controlando, sondea entradas cada segundo y maneja el evento de parada.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if self._op_mode == OP_CONTROLANDO:
            self._setup_devices()
        try:
            while not self._stop_evt.is_set():
                if self._op_mode == OP_CONTROLANDO:
                    self._poll_inputs()
                self._stop_evt.wait(self.POLL_INTERVAL)
        finally:
            self._running = False


    # ── gpiozero ──────────────────────────────────────────────────────────────

    def _import_gpiozero(self) -> bool:
        """
        Intenta importar el módulo gpiozero y configura el estado de disponibilidad de GPIO.

        Args:
            Ninguno

        Returns:
            bool: True si gpiozero se importa correctamente, False en caso contrario.

        Raises:
            Ninguna excepción explícita, pero se registra un warning si gpiozero no está disponible.
        """
        try:
            self._gz = gpiozero
            self._gpio_available = True
            logger.info("[GPIOMonitor] gpiozero disponible")
            return True
        except ImportError:
            self._gpio_available = False
            logger.warning("[GPIOMonitor] gpiozero no disponible")
            with self._lock:
                for pin in self._state:
                    self._state[pin]["error"] = "gpiozero no instalado"
            return False


    def _setup_devices(self):
        """
        Configura los dispositivos gpiozero (Button/LED/PWMLED) para todos los pines en el estado actual.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Excepciones durante la recreación de LGPIOFactory.
        """
        if self._gz is None and not self._import_gpiozero():
            return
        # Recrear factory si fue cerrado en una liberación anterior
        try:
            if Device.pin_factory is None:
                Device.pin_factory = LGPIOFactory()
                logger.debug("[GPIOMonitor] LGPIOFactory recreado")
        except Exception as exc:
            logger.debug("[GPIOMonitor] factory reset: %s", exc)
        with self._lock:
            snapshot = {p: dict(d) for p, d in self._state.items()}
        for pin, data in snapshot.items():
            self._open_device(pin, data["mode"], data.get("duty", 0.0))


    def _open_device(self, pin: int, mode: str, duty: float = 0.0):
        """
        Abre un dispositivo GPIO según el modo especificado y lo registra para su uso posterior.

        Args:
            pin (int): El número de pin GPIO a abrir.
            mode (str): El modo de funcionamiento del pin (INPUT, OUTPUT o PWM).
            duty (float, opcional): El valor de duty cycle para modo PWM (por defecto 0.0).

        Returns:
            None

        Raises:
            Exception: Si ocurre un error al abrir el dispositivo, se registra en el estado de error.
        """
        self._close_device(pin)
        if self._gz is None:
            return
        try:
            if mode == MODE_INPUT:
                dev = self._gz.Button(pin, pull_up=None, active_state=True)
            elif mode == MODE_OUTPUT:
                dev = self._gz.LED(pin)
                dev.off()
            elif mode == MODE_PWM:
                dev = self._gz.PWMLED(pin)
                dev.value = max(0.0, min(1.0, duty))
            else:
                return
            self._devices[pin] = dev
            with self._lock:
                if pin in self._state:
                    self._state[pin]["error"] = None
        except Exception as exc:
            logger.warning("[GPIOMonitor] Pin %d error al abrir (%s): %s", pin, mode, exc)
            with self._lock:
                if pin in self._state:
                    self._state[pin]["error"] = str(exc)


    def _close_device(self, pin: int):
        """
        Cierra el dispositivo GPIO asociado a un pin específico.

        Args:
            pin (int): El número de pin GPIO a cerrar.

        Returns:
            None

        Raises:
            None
        """
        dev = self._devices.pop(pin, None)
        if dev is not None:
            try:
                dev.close()
            except Exception:
                pass


    def _release_devices(self):
        """
        Cierra todos los dispositivos gpiozero y el factory lgpio.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Excepción genérica si falla el cierre del factory lgpio.
        """
        for pin in list(self._devices):
            self._close_device(pin)
        # Cerrar el factory — en Pi 5 (lgpio) libera /dev/gpiochip0
        try:
            if Device.pin_factory is not None:
                Device.pin_factory.close()
                Device.pin_factory = None
        except Exception as exc:
            logger.debug("[GPIOMonitor] factory.close(): %s", exc)
        self._gz             = None
        self._gpio_available = False


    # ── Poll inputs ───────────────────────────────────────────────────────────

    def _poll_inputs(self):
        """
        Actualiza de forma segura el estado de los pines de entrada de la GPIO.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Excepciones relacionadas con la lectura de los dispositivos GPIO.
        """
        if not self._gpio_available:
            return
        with self._lock:
            snapshot = [(p, dict(d)) for p, d in self._state.items()]
        for pin, data in snapshot:
            if data["mode"] != MODE_INPUT:
                continue
            dev = self._devices.get(pin)
            if dev is None:
                continue
            try:
                value = dev.is_active
                with self._lock:
                    if pin in self._state:
                        self._state[pin]["value"] = value
                        self._state[pin]["error"] = None
            except Exception as exc:
                with self._lock:
                    if pin in self._state:
                        self._state[pin]["error"] = str(exc)


    # ── Persistencia ──────────────────────────────────────────────────────────

    def _persist(self) -> None:
        """
        Persiste una captura de la configuración actual de los pines en local_settings de manera segura para hilos concurrentes.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        """Guarda _pins_cfg actual en local_settings. Thread-safe."""
        with self._lock:
            snapshot = {pin: dict(cfg) for pin, cfg in self._pins_cfg.items()}
        _save_config(snapshot)


    # ── API pública — modo de operación ──────────────────────────────────────

    def get_op_mode(self) -> str:
        """
        Retorna el modo de operación actual del monitor GPIO.

        Args:
            Ninguno

        Returns:
            str: El modo de operación actual, OP_CONTROLANDO o OP_LIBRE.

        Raises:
            Ninguno
        """
        return self._op_mode

    def set_op_mode(self, mode: str) -> None:
        """
        Establece el modo de operación del monitor GPIO.

        Args:
            mode (str): Modo de operación, puede ser OP_CONTROLANDO o OP_LIBRE.

        Raises:
            None

        Returns:
            None
        """
        if mode not in (OP_CONTROLANDO, OP_LIBRE) or mode == self._op_mode:
            return
        if mode == OP_LIBRE:
            self._release_devices()
            with self._lock:
                for data in self._state.values():
                    data["value"] = None
                    data["error"] = None
            self._op_mode = mode
            logger.info("[GPIOMonitor] GPIO liberado — pines disponibles para otros procesos")
        else:
            self._op_mode = mode
            self._setup_devices()
            logger.info("[GPIOMonitor] GPIO bajo control del dashboard")

    # ── API pública — lectura ─────────────────────────────────────────────────

    def get_state(self) -> dict[int, dict]:
        """
        Obtiene un snapshot thread-safe del estado actual de todos los pines GPIO configurados.

        Returns:
            dict[int, dict]: Un diccionario donde cada clave es un número de pin BCM y cada valor es otro diccionario con los detalles del estado del pin.

        Raises:
            None
        """
        with self._lock:
            return {pin: dict(data) for pin, data in self._state.items()}

    def is_gpio_available(self) -> bool:
        """
        Indica si gpiozero está disponible e importado.

        Returns:
            bool: True si gpiozero está disponible.

        Raises:
            None
        """
        return self._gpio_available

    def get_pins(self) -> list[int]:
        """
        Obtiene una lista de todos los pines BCM configurados, excluyendo los reservados.

        Args:
            Ninguno

        Returns:
            list[int]: Una lista de pines BCM ordenados.

        Raises:
            Ninguno
        """
        return sorted(self._state.keys())

    @staticmethod
    def reserved_pins() -> set[int]:
        """
        Devuelve el conjunto de pines BCM reservados para uso de I2C, PWM y UART.

        Returns:
            set[int]: Conjunto de pines BCM reservados.
        """
        return set(_RESERVED_PINS)

    # ── API pública — OUTPUT ──────────────────────────────────────────────────

    def set_output(self, pin: int, high: bool) -> bool:
        """
        Establece el estado de salida de un pin GPIO en modo OUTPUT.

        Args:
            pin (int): Número del pin GPIO en modo BCM.
            high (bool): Estado del pin, True para HIGH y False para LOW.

        Returns:
            bool: True si el estado del pin se cambió correctamente.

        Raises:
            Exception: Si ocurre un error al cambiar el estado del pin.
        """
        if self._op_mode == OP_LIBRE:
            return False
        with self._lock:
            data = self._state.get(pin)
            if data is None or data["mode"] != MODE_OUTPUT:
                return False
        dev = self._devices.get(pin)
        if dev is None:
            return False
        try:
            dev.on() if high else dev.off()
            with self._lock:
                self._state[pin]["value"] = high
                self._state[pin]["error"] = None
            #logger.debug("[GPIOMonitor] GPIO %d → %s", pin, "HIGH" if high else "LOW")
            return True
        except Exception as exc:
            with self._lock:
                self._state[pin]["error"] = str(exc)
            return False

    # ── API pública — PWM ─────────────────────────────────────────────────────

    def set_pwm(self, pin: int, duty: float) -> bool:
        """
        Establece el ciclo de trabajo PWM en un pin específico.

        Args:
            pin (int): Número de pin en modo BCM PWM.
            duty (float): Ciclo de trabajo PWM, entre 0.0 (apagado) y 1.0 (completo).

        Returns:
            bool: True si el ciclo de trabajo PWM se estableció correctamente.

        Raises:
            Exception: Si ocurre un error al establecer el valor PWM.
        """
        if self._op_mode == OP_LIBRE:
            return False
        duty = max(0.0, min(1.0, duty))
        with self._lock:
            data = self._state.get(pin)
            if data is None or data["mode"] != MODE_PWM:
                return False
        dev = self._devices.get(pin)
        if dev is None:
            return False
        try:
            dev.value = duty
            with self._lock:
                self._state[pin]["duty"]  = duty
                self._state[pin]["error"] = None
            #logger.debug("[GPIOMonitor] GPIO %d PWM → %.1f%%", pin, duty * 100)
            return True
        except Exception as exc:
            with self._lock:
                self._state[pin]["error"] = str(exc)
            return False

    # ── API pública — configuración de pines ──────────────────────────────────

    def set_label(self, pin: int, label: str) -> bool:
        """
        Establece una etiqueta descriptiva para un pin GPIO específico y persiste el cambio.

        Args:
            pin (int): Número de pin BCM.
            label (str): Nueva etiqueta para el pin.

        Returns:
            bool: True si la etiqueta se actualizó correctamente.

        Raises:
            None
        """
        with self._lock:
            if pin not in self._state:
                return False
            self._state[pin]["label"]    = label
            self._pins_cfg[pin]["label"] = label
        self._persist()
        return True

    def set_mode(self, pin: int, mode: str) -> bool:
        """
        Establece el modo de un pin GPIO específico.

        Args:
            pin (int): Número del pin GPIO en formato BCM.
            mode (str): Modo del pin, puede ser INPUT, OUTPUT o PWM.

        Returns:
            bool: True si el modo del pin se ha cambiado correctamente.

        Raises:
            None
        """
        if mode not in VALID_MODES or pin in _RESERVED_PINS:
            return False
        with self._lock:
            if pin not in self._state:
                return False
            self._state[pin]["mode"]    = mode
            self._state[pin]["value"]   = None
            self._state[pin]["duty"]    = 0.0
            self._state[pin]["error"]   = None
            self._pins_cfg[pin]["mode"] = mode
        if self._op_mode == OP_CONTROLANDO and self._gpio_available:
            self._open_device(pin, mode, 0.0)
        self._persist()
        logger.info("[GPIOMonitor] GPIO %d modo → %s", pin, mode)
        return True

    def add_pin(self, pin: int, mode: str = MODE_INPUT, label: str = "") -> bool:
        """
        Añade un nuevo pin BCM a la configuración y estado persistente.

        Args:
            pin (int): Número de pin BCM no reservado.
            mode (str): Modo inicial del pin (MODE_INPUT, MODE_OUTPUT o MODE_PWM).
            label (str): Etiqueta para el pin, por defecto "GPIO N".

        Returns:
            bool: True si el pin fue añadido correctamente (no existía previamente).

        Raises:
            None
        """
        if pin in _RESERVED_PINS:
            logger.warning("[GPIOMonitor] Pin %d reservado — ignorado", pin)
            return False
        with self._lock:
            if pin in self._state:
                return False
            lbl = label or f"GPIO {pin}"
            self._state[pin] = {
                "mode": mode, "label": lbl,
                "value": None, "duty": 0.0, "error": None,
            }
            self._pins_cfg[pin] = {"mode": mode, "label": lbl}
        if self._op_mode == OP_CONTROLANDO and self._gpio_available:
            self._open_device(pin, mode, 0.0)
        self._persist()
        logger.info("[GPIOMonitor] Pin %d añadido (%s)", pin, mode)
        return True

    def remove_pin(self, pin: int) -> bool:
        """
        Elimina un pin de la configuración del monitor GPIO.

        Args:
            pin (int): Número del pin BCM a remover.

        Returns:
            bool: True si el pin fue eliminado correctamente.

        Raises:
            None
        """
        self._close_device(pin)
        with self._lock:
            removed = self._state.pop(pin, None)
            self._pins_cfg.pop(pin, None)
        if removed is not None:
            self._persist()
            logger.info("[GPIOMonitor] Pin %d eliminado", pin)
        return removed is not None
