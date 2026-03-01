"""
Gestor centralizado de ventanas y botones del menú principal.

Controla qué botones son visibles según la sección "ui" de services.json.
Los servicios y los botones son decisiones INDEPENDIENTES — parar un servicio
no oculta su botón, y ocultar un botón no para su servicio.

Uso en MainWindow:
    self._wm = WindowManager(registry, self._menu_btns)
    self._wm.apply_config()   # oculta los botones deshabilitados en el JSON
"""
from utils.logger import get_logger

logger = get_logger(__name__)


class WindowManager:
    """
    Gestiona la visibilidad de botones del menú según la configuración de UI.

    Mapeo: clave del JSON "ui" → texto exacto del botón en MainWindow.
    Si una clave está en False, el botón correspondiente se oculta con grid_remove().
    """

    # Mapeo clave_json → texto exacto del botón (iconos incluidos tal cual)
    _BTN_MAP = {
        "fan_control":      "󰈐  Control Ventiladores",
        "led_window":       "󰟖  LEDs RGB",
        "monitor_window":   "󰚗  Monitor Placa",
        "network_window":   "  Monitor Red",
        "usb_window":       "󱇰 Monitor USB",
        "disk_window":      "  Monitor Disco",
        "launchers":        "󱓞  Lanzadores",
        "process_window":   "⚙️ Monitor Procesos",
        "service_window":   "⚙️ Monitor Servicios",
        "services_manager": "⚙️  Servicios Dashboard",
        "history_window":   "󱘿  Histórico Datos",
        "update_window":    "󰆧  Actualizaciones",
        "homebridge":       "󰟐  Homebridge",
        "log_viewer":       "󰷐  Visor de Logs",
        "network_local":    "🖧  Red Local",
        "pihole":           "🕳  Pi-hole",
        "vpn_window":       "🔒  Gestor VPN",
        "alert_history":    "  Historial Alertas",
        "display_window":   "󰃟  Brillo Pantalla",
        "overview":         "📊  Resumen Sistema",
        "camera_window":    "📷  Cámara",
        "theme_selector":   "󰔎  Cambiar Tema",
        # Reiniciar y Salir son siempre visibles — no están en el JSON
    }

    def __init__(self, registry, menu_btns: dict):
        """
        Args:
            registry:   ServiceRegistry con la config de UI
            menu_btns:  dict {texto_botón: CTkButton} de MainWindow
        """
        self._registry  = registry
        self._menu_btns = menu_btns

    def apply_config(self) -> None:
        """Oculta los botones cuya clave esté en False en services.json ui."""
        for key, btn_text in self._BTN_MAP.items():
            enabled = self._registry.ui_enabled(key)
            btn = self._menu_btns.get(btn_text)
            if btn is None:
                continue
            if enabled:
                btn.grid()        # restaurar si estaba oculto
            else:
                btn.grid_remove() # ocultar sin destruir
                logger.info("[WindowManager] Botón oculto: %s", key)

    def show(self, key: str) -> None:
        """Muestra un botón por su clave de config y actualiza el JSON."""
        self._set(key, True)

    def hide(self, key: str) -> None:
        """Oculta un botón por su clave de config y actualiza el JSON."""
        self._set(key, False)

    def _set(self, key: str, visible: bool) -> None:
        btn_text = self._BTN_MAP.get(key)
        if btn_text is None:
            return
        btn = self._menu_btns.get(btn_text)
        if btn is None:
            return
        if visible:
            btn.grid()
        else:
            btn.grid_remove()
        # Actualizar config en memoria (se persistirá con save_config())
        self._registry._config["ui"][key] = visible
