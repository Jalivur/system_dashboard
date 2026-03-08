"""
Gestor centralizado de ventanas y botones del menu principal.
"""
import config.button_labels as BL
from utils.logger import get_logger

logger = get_logger(__name__)


class WindowManager:
    _BTN_MAP = {
        "hardware_info":        BL.HARDWARE_INFO,
        "fan_control":          BL.FAN_CONTROL,
        "led_window":           BL.LED_RGB,
        "monitor_window":       BL.MONITOR_PLACA,
        "network_window":       BL.MONITOR_RED,
        "usb_window":           BL.MONITOR_USB,
        "disk_window":          BL.MONITOR_DISCO,
        "launchers":            BL.LANZADORES,
        "process_window":       BL.PROCESOS,
        "service_window":       BL.SERVICIOS,
        "services_manager":     BL.SERVICIOS_DASH,
        "crontab_window":       BL.CRONTAB,
        "history_window":       BL.HISTORICO,
        "update_window":        BL.ACTUALIZACIONES,
        "homebridge":           BL.HOMEBRIDGE,
        "log_viewer":           BL.VISOR_LOGS,
        "network_local":        BL.RED_LOCAL,
        "pihole":               BL.PIHOLE,
        "vpn_window":           BL.VPN,
        "alert_history":        BL.HISTORIAL_ALERTAS,
        "display_window":       BL.BRILLO,
        "overview":             BL.RESUMEN,
        "camera_window":        BL.CAMARA,
        "theme_selector":       BL.TEMA,
        "ssh_window":           BL.SSH,
        "wifi_window":          BL.WIFI,
        "config_editor_window": BL.CONFIG,
        "audio_window":         BL.AUDIO,
        "weather_window":       BL.CLIMA,
        "i2c_window":           BL.I2C,
        "gpio_window":          BL.GPIO,
    }

    _ALWAYS_VISIBLE = [
        BL.BOTONES,
        BL.REINICIAR,
        BL.SALIR,
    ]

    def __init__(self, registry, menu_btns: dict):
        self._registry    = registry
        self._menu_btns   = menu_btns
        self._columns     = 2
        self._rerender_cb = None

    def set_rerender_callback(self, cb) -> None:
        self._rerender_cb = cb

    def apply_config(self) -> None:
        self._rerender()

    def show(self, key: str) -> None:
        self._registry._config["ui"][key] = True
        self._rerender()
        logger.info("[WindowManager] Boton visible: %s", key)

    def hide(self, key: str) -> None:
        self._registry._config["ui"][key] = False
        self._rerender()
        logger.info("[WindowManager] Boton oculto: %s", key)

    def is_enabled(self, key: str) -> bool:
        return self._registry.ui_enabled(key)

    def _rerender(self) -> None:
        if self._rerender_cb is not None:
            self._rerender_cb()
        else:
            logger.warning("[WindowManager] _rerender llamado sin callback registrado")
