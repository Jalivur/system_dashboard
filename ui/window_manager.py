"""
Gestor centralizado de ventanas y botones del menu principal.

Controla que botones son visibles segun la seccion "ui" de services.json.
Los servicios y los botones son decisiones INDEPENDIENTES — parar un servicio
no oculta su boton, y ocultar un boton no para su servicio.

Con el menu por pestanas, el WindowManager ya no manipula widgets directamente.
En su lugar, invoca un callback registrado por MainWindow que repopula la pestana
activa filtrando los botones deshabilitados. Esto mantiene la separacion limpia:
WindowManager es fuente de verdad sobre que esta habilitado; MainWindow decide
como renderizarlo.

Uso en MainWindow:
    self._wm = WindowManager(registry, self._menu_btns)
    self._wm.set_rerender_callback(lambda: self._switch_tab(self._active_tab))
"""
import config.button_labels as BL
from utils.logger import get_logger

logger = get_logger(__name__)


class WindowManager:
    """
    Gestiona la visibilidad de botones del menu recolocandolos sin huecos.

    Mapeo: clave del JSON "ui" → constante de config.button_labels.
    Cuando cambia la visibilidad de cualquier boton se invoca el callback
    de rerender registrado por MainWindow (normalmente _switch_tab), que
    repopula el area de botones de la pestana activa filtrando los deshabilitados.

    El WindowManager es la fuente de verdad sobre que esta habilitado via
    registry.ui_enabled(key), pero delega el rerender al MainWindow para
    no asumir nada sobre la estructura de widgets del menu.
    """

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
        self._rerender_cb = None   # callable() registrado por MainWindow

    def set_rerender_callback(self, cb) -> None:
        """Registra el callable que MainWindow ejecutara al cambiar visibilidad.
        Normalmente: lambda: self._switch_tab(self._active_tab)
        """
        self._rerender_cb = cb

    def apply_config(self) -> None:
        """Aplica la configuracion inicial invocando el rerender."""
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
        """Devuelve True si el boton con clave JSON key esta habilitado."""
        return self._registry.ui_enabled(key)

    def _rerender(self) -> None:
        """Invoca el callback de rerender registrado por MainWindow."""
        if self._rerender_cb is not None:
            self._rerender_cb()
        else:
            logger.warning("[WindowManager] _rerender llamado sin callback registrado")
