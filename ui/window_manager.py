"""
Gestor centralizado de ventanas y botones del menu principal.

Controla que botones son visibles segun la seccion "ui" de services.json.
Los servicios y los botones son decisiones INDEPENDIENTES — parar un servicio
no oculta su boton, y ocultar un boton no para su servicio.

Uso en MainWindow:
    self._wm = WindowManager(registry, self._menu_btns)
    self._wm.apply_config()   # oculta los botones deshabilitados en el JSON
"""
import config.button_labels as BL
from utils.logger import get_logger

logger = get_logger(__name__)


class WindowManager:
    """
    Gestiona la visibilidad de botones del menu recolocandolos sin huecos.

    Mapeo: clave del JSON "ui" → constante de config.button_labels.
    Cuando cambia la visibilidad de cualquier boton se rehace el grid completo
    solo con los botones visibles, en orden, 2 columnas.
    """

    _BTN_MAP = {
        "hardware_info":    BL.HARDWARE_INFO,
        "fan_control":      BL.FAN_CONTROL,
        "led_window":       BL.LED_RGB,
        "monitor_window":   BL.MONITOR_PLACA,
        "network_window":   BL.MONITOR_RED,
        "usb_window":       BL.MONITOR_USB,
        "disk_window":      BL.MONITOR_DISCO,
        "launchers":        BL.LANZADORES,
        "process_window":   BL.PROCESOS,
        "service_window":   BL.SERVICIOS,
        "services_manager": BL.SERVICIOS_DASH,
        "crontab_window":   BL.CRONTAB,
        "history_window":   BL.HISTORICO,
        "update_window":    BL.ACTUALIZACIONES,
        "homebridge":       BL.HOMEBRIDGE,
        "log_viewer":       BL.VISOR_LOGS,
        "network_local":    BL.RED_LOCAL,
        "pihole":           BL.PIHOLE,
        "vpn_window":       BL.VPN,
        "alert_history":    BL.HISTORIAL_ALERTAS,
        "display_window":   BL.BRILLO,
        "overview":         BL.RESUMEN,
        "camera_window":    BL.CAMARA,
        "theme_selector":   BL.TEMA,
        "ssh_window":       BL.SSH,
        "wifi_window":      BL.WIFI,
        "config_editor_windo":    BL.CONFIG,
    }

    _ALWAYS_VISIBLE = [
        BL.BOTONES,
        BL.REINICIAR,
        BL.SALIR,
    ]

    def __init__(self, registry, menu_btns: dict):
        self._registry  = registry
        self._menu_btns = menu_btns
        self._columns   = 2

    def apply_config(self) -> None:
        self._regrid()

    def show(self, key: str) -> None:
        self._registry._config["ui"][key] = True
        self._regrid()
        logger.info("[WindowManager] Boton visible: %s", key)

    def hide(self, key: str) -> None:
        self._registry._config["ui"][key] = False
        self._regrid()
        logger.info("[WindowManager] Boton oculto: %s", key)

    def _regrid(self) -> None:
        for btn in self._menu_btns.values():
            btn.grid_remove()

        visible = []
        for key, btn_text in self._BTN_MAP.items():
            btn = self._menu_btns.get(btn_text)
            if btn is None:
                continue
            if self._registry.ui_enabled(key):
                visible.append(btn)

        for btn_text in self._ALWAYS_VISIBLE:
            btn = self._menu_btns.get(btn_text)
            if btn is not None:
                visible.append(btn)

        for i, btn in enumerate(visible):
            btn.grid(row=i // self._columns, column=i % self._columns,
                     padx=10, pady=10, sticky="nsew")
