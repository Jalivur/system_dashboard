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
    Carga la configuración de pines desde local_settings_io.
    Si no existe la clave devuelve _DEFAULT_CONFIG.
    Las claves se almacenan como strings — se convierten a int.
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
    Persiste la configuración en local_settings.py via update_params.
    Merge seguro — no machaca otras claves del fichero.
    """
    try:
        serializable = {str(pin): dict(cfg) for pin, cfg in pins_cfg.items()}
        update_params({_SETTINGS_KEY: serializable})
        logger.debug("[GPIOMonitor] Config persistida (%d pines)", len(pins_cfg))
    except Exception as exc:
        logger.warning("[GPIOMonitor] Error guardando config: %s", exc)


class GPIOMonitor:
    """
    Gestiona pines GPIO con soporte INPUT, OUTPUT y PWM.

    Estado por pin:
      {
        "mode":  str        — INPUT | OUTPUT | PWM
        "label": str        — etiqueta descriptiva
        "value": bool|None  — estado leído/escrito; None si LIBRE
        "duty":  float      — PWM duty cycle 0.0–1.0; 0.0 en otros modos
        "error": str|None   — mensaje de error o None
      }
    """

    POLL_INTERVAL = 1.0

    def __init__(self, config: dict | None = None, op_mode: str = OP_LIBRE):
        """
        Inicializa monitor GPIO.

        Args:
            config (dict, optional): Config pines. Defaults _load_config().
            op_mode (str): OP_LIBRE o OP_CONTROLANDO.

        Configura locks, state, carga pins desde local_settings.
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
        Inicializa dict _state thread-safe con modos/labels desde _pins_cfg.
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
        Inicia thread daemon de polling GPIO (1s intervalo).

        Setup devices si OP_CONTROLANDO.
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
        Detiene thread, libera dispositivos gpiozero, cierra factory LGPIO.

        Espera 5s join max, _running=False.
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
        Retorna estado del monitor (thread activo).

        Returns:
            bool: True si corriendo.
        """
        return self._running


    # ── Thread ────────────────────────────────────────────────────────────────

    def _run(self):
        """
        Bucle principal thread daemon.

        Setup devices si controlando, poll inputs 1s, maneja stop_evt.
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
        Importa gpiozero module, set _gz y _gpio_available.
        Error: set state error todos pins.

        Returns:
            bool: True si disponible.
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
        Crea/abre gpiozero devices (Button/LED/PWMLED) para todos pines en state.
        Recrear LGPIOFactory si cerrado.
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
        Crea gpiozero device según mode:
        INPUT: Button(pull_up=None)
        OUTPUT: LED(off)
        PWM: PWMLED(value=duty clamped 0-1)

        Catch exceptions → state error.
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
        Cierra gpiozero device (call dev.close()), remove de _devices.
        Silencioso exceptions.
        """
        dev = self._devices.pop(pin, None)
        if dev is not None:
            try:
                dev.close()
            except Exception:
                pass


    def _release_devices(self):
        """
        Cleanup total: close devices + LGPIOFactory.close() + None states.
        """
        """Cierra todos los dispositivos gpiozero y el factory lgpio."""
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
        Lee is_active Button INPUT pins → state['value'] thread-safe snapshot.
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
        Persiste _pins_cfg snapshot en local_settings thread-safe.
        """
        """Guarda _pins_cfg actual en local_settings. Thread-safe."""
        with self._lock:
            snapshot = {pin: dict(cfg) for pin, cfg in self._pins_cfg.items()}
        _save_config(snapshot)


    # ── API pública — modo de operación ──────────────────────────────────────

    def get_op_mode(self) -> str:
        """
        Retorna modo de operación actual.

        Returns:
            str: OP_CONTROLANDO o OP_LIBRE.
        """
        return self._op_mode

    def set_op_mode(self, mode: str) -> None:
        """
        Cambia modo operación. LIBRE libera dispositivos, CONTROLANDO los reclama.

        Args:
            mode (str): OP_CONTROLANDO o OP_LIBRE.
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
        Snapshot thread-safe del estado de todos los pines GPIO configurados.

        Returns:
            dict[int, dict]: Estado por BCM pin.
        """
        with self._lock:
            return {pin: dict(data) for pin, data in self._state.items()}

    def is_gpio_available(self) -> bool:
        """
        Indica si gpiozero está disponible e importado.

        Returns:
            bool: True si Pi5+lgpio OK.
        """
        return self._gpio_available

    def get_pins(self) -> list[int]:
        """
        Lista de todos los pines BCM configurados (excluye reservados).

        Returns:
            list[int]: Pines BCM ordenados.
        """
        return sorted(self._state.keys())

    @staticmethod
    def reserved_pins() -> set[int]:
        """
        Pines BCM reservados por fase1.py (I2C/PWM/UART).

        Returns:
            set[int]: {2,3,12,13,14,15,18,19}
        """
        return set(_RESERVED_PINS)

    # ── API pública — OUTPUT ──────────────────────────────────────────────────

    def set_output(self, pin: int, high: bool) -> bool:
        """
        Establece salida OUTPUT HIGH/LOW en pin BCM.

        Args:
            pin (int): BCM pin en modo OUTPUT.
            high (bool): True=ON/HIGH, False=OFF/LOW.

        Returns:
            bool: True si cambiado correctamente.
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
        Establece duty cycle PWM (0.0-1.0) en pin BCM PWMLED.

        Args:
            pin (int): BCM pin en modo PWM.
            duty (float): 0.0=off, 1.0=full, clamped.

        Returns:
            bool: True si seteado correctamente.
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
        Cambia etiqueta descriptiva del pin (persiste).

        Args:
            pin (int): BCM pin.
            label (str): Nueva etiqueta.

        Returns:
            bool: True si actualizado.
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
        Cambia modo del pin (INPUT/OUTPUT/PWM), persiste, recrea device si controlando.

        Args:
            pin (int): BCM pin.
            mode (str): MODE_INPUT/OUTPUT/PWM.

        Returns:
            bool: True si cambiado.
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
        Añade nuevo pin BCM a configuración y state (persiste).

        Args:
            pin (int): BCM pin no reservado.
            mode (str): Inicial MODE_INPUT/OUTPUT/PWM.
            label (str): Etiqueta o "GPIO N".

        Returns:
            bool: True si añadido (no existía).
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
        Elimina pin de configuración, cierra device, persiste.

        Args:
            pin (int): BCM pin a remover.

        Returns:
            bool: True si eliminado (existía).
        """
        self._close_device(pin)
        with self._lock:
            removed = self._state.pop(pin, None)
            self._pins_cfg.pop(pin, None)
        if removed is not None:
            self._persist()
            logger.info("[GPIOMonitor] Pin %d eliminado", pin)
        return removed is not None
