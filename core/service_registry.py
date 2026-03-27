"""
Registro centralizado de servicios del Dashboard.

Gestiona el ciclo de vida de todos los servicios según configuración JSON.
Servicios y visibilidad de botones son configuraciones INDEPENDIENTES:
  - "services": controla si el servicio arranca al inicio
  - "ui":       controla si el botón aparece en el menú (WindowManager)

Uso en main.py:
    registry = ServiceRegistry()
    registry.register("system_monitor", SystemMonitor())
    ...
    registry.apply_config()              # para los que estén en False en services.json
    registry.set_service_enabled(k, v)   # marca habilitado/deshabilitado y persiste
    registry.save_config()               # persiste _config al JSON (sin leer estado live)
"""
import json
import os
from utils.logger import get_logger

logger = get_logger(__name__)

_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config", "services.json"
)

_DEFAULT_CONFIG = {
    "services": {
        "system_monitor":      True,
        "disk_monitor":        True,
        "hardware_monitor":    True,
        "network_monitor":     True,
        "network_scanner":     True,
        "process_monitor":     True,
        "service_monitor":     True,
        "update_monitor":      True,
        "homebridge_monitor":  True,
        "pihole_monitor":      True,
        "vpn_monitor":         True,
        "alert_service":       True,
        "audio_alert_service": True,
        "data_service":        True,
        "cleanup_service":     True,
        "fan_service":         True,
        "led_service":         True,
        "display_service":     True,
        "ssh_monitor":         True,
        "wifi_monitor":        True,
        "fan_controller":      True,
        "audio_service":       True,
        "weather_service":     True,
        "i2c_monitor":         True,
        "gpio_monitor":        True,
        "service_watchdog":    True
    },
    "ui": {
        "hardware_info":    True,
        "fan_control":      True,
        "led_window":       True,
        "monitor_window":   True,
        "network_window":   True,
        "usb_window":       True,
        "disk_window":      True,
        "launchers":        True,
        "process_window":   True,
        "service_window":   True,
        "services_manager": True,
        "history_window":   True,
        "update_window":    True,
        "homebridge":       True,
        "log_viewer":       True,
        "network_local":    True,
        "pihole":           True,
        "vpn_window":       True,
        "alert_history":    True,
        "display_window":   True,
        "overview":         True,
        "camera_window":    True,
        "theme_selector":   True,
        "ssh_window":       True,
        "wifi_window":      True,
        "config_editor_window": True,
        "crontab_window":   True,
        "audio_window":     True,
        "weather_window":   True,
        "i2c_window":       True,
        "gpio_window":      True,
        "service_watchdog": True

    }
}


class ServiceRegistry:
    """Registro centralizado de servicios del dashboard."""

    def __init__(self, config_path: str = None):
        """
        Inicializa el registro de servicios.
        
        Args:
            config_path: Ruta opcional al archivo services.json
        """
        self._config_path = os.path.abspath(config_path or _CONFIG_PATH)
        self._config = {
            "services": dict(_DEFAULT_CONFIG["services"]),
            "ui":       dict(_DEFAULT_CONFIG["ui"]),
        }
        self._services: dict = {}
        self._load_config()

    # ── Configuración ─────────────────────────────────────────────────────────

    def _load_config(self):
        """Carga services.json. Si no existe lo crea con valores por defecto."""
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r") as f:
                    loaded = json.load(f)
                for section in ("services", "ui"):
                    if section in loaded:
                        self._config[section].update(loaded[section])
                logger.info("[ServiceRegistry] Config cargada desde %s", self._config_path)
            except Exception as e:
                logger.error("[ServiceRegistry] Error leyendo config: %s — usando defaults", e)
        else:
            self.save_config()
            logger.info("[ServiceRegistry] services.json creado en %s", self._config_path)

    def save_config(self):
        """Persiste la configuración actual (_config) al JSON.
        No lee el estado live de los servicios — guarda lo que se haya
        establecido explícitamente via set_service_enabled()."""
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, "w") as f:
                json.dump(self._config, f, indent=2)
            logger.info("[ServiceRegistry] Config guardada en %s", self._config_path)
        except Exception as e:
            logger.error("[ServiceRegistry] Error guardando config: %s", e)

    def set_service_enabled(self, key: str, enabled: bool) -> None:
        """Marca un servicio como habilitado/deshabilitado en la config y persiste."""
        self._config["services"][key] = enabled
        self.save_config()

    # ── Registro y acceso ─────────────────────────────────────────────────────

    def register(self, key: str, instance) -> None:
        """Registra un servicio. Solo lo almacena, no lo para ni arranca."""
        self._services[key] = instance

    def apply_config(self) -> None:
        """Para todos los servicios configurados como False en services.json."""
        for key, svc in self._services.items():
            enabled = self._config["services"].get(key, True)
            if not enabled:
                try:
                    svc.stop()
                    logger.info("[ServiceRegistry] %s arranca PARADO (config)", key)
                except Exception as e:
                    logger.error("[ServiceRegistry] Error parando %s: %s", key, e)

    def get(self, key: str):
        """Devuelve la instancia de un servicio por clave."""
        return self._services.get(key)

    def get_all(self) -> dict:
        """Devuelve todos los servicios registrados."""
        return dict(self._services)

    # ── Consultas de configuración ────────────────────────────────────────────

    def service_enabled(self, key: str) -> bool:
        """True si el servicio está configurado para arrancar."""
        return self._config["services"].get(key, True)

    def ui_enabled(self, key: str) -> bool:
        """True si el botón de UI está habilitado en la configuración."""
        return self._config["ui"].get(key, True)
