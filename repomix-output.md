This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: ui/main_window.py, ui/window_manager.py, core/service_registry.py, config/services.json
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
core/
  service_registry.py
ui/
  main_window.py
  window_manager.py
```

# Files

## File: core/service_registry.py
```python
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
    registry.apply_config()    # para los que estén en False en services.json
    registry.save_config()     # persiste el estado actual al JSON
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
    }
}


class ServiceRegistry:
    """Registro centralizado de servicios del dashboard."""

    def __init__(self, config_path: str = None):
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
        """Persiste el estado actual de _running de cada servicio al JSON."""
        for key, svc in self._services.items():
            self._config["services"][key] = getattr(svc, "_running", True)
        try:
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, "w") as f:
                json.dump(self._config, f, indent=2)
            logger.info("[ServiceRegistry] Config guardada en %s", self._config_path)
        except Exception as e:
            logger.error("[ServiceRegistry] Error guardando config: %s", e)

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
```

## File: ui/window_manager.py
```python
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
```

## File: ui/main_window.py
```python
"""
Ventana principal del sistema de monitoreo
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_X, DSI_Y, SCRIPTS_DIR, Icons
import config.button_labels as BL
from ui.styles import StyleManager, make_futuristic_button
from ui.windows import (FanControlWindow, MonitorWindow, NetworkWindow, USBWindow, ProcessWindow, ServiceWindow,
                        HistoryWindow, LaunchersWindow, ThemeSelector, DiskWindow, UpdatesWindow, HomebridgeWindow,
                        NetworkLocalWindow, PiholeWindow, AlertHistoryWindow, DisplayWindow, VpnWindow, OverviewWindow,
                        LedWindow, CameraWindow, ServicesManagerWindow, LogViewerWindow, ButtonManagerWindow, CrontabWindow,
                        HardwareInfoWindow)
from ui.widgets import confirm_dialog, terminal_dialog
from ui.window_manager import WindowManager
from utils.system_utils import SystemUtils
from utils.logger import get_logger
import sys
import os
from datetime import datetime

logger = get_logger(__name__)


class MainWindow:
    """Ventana principal del dashboard"""

    def __init__(self, root, registry, update_interval=2000):
        self.root = root
        self.registry = registry
        self.update_interval = update_interval
        self.system_utils = SystemUtils()

        self.system_monitor      = registry.get("system_monitor")
        self.fan_controller      = registry.get("fan_controller")
        self.fan_service         = registry.get("fan_service")
        self.data_service        = registry.get("data_service")
        self.network_monitor     = registry.get("network_monitor")
        self.disk_monitor        = registry.get("disk_monitor")
        self.process_monitor     = registry.get("process_monitor")
        self.service_monitor     = registry.get("service_monitor")
        self.update_monitor      = registry.get("update_monitor")
        self.cleanup_service     = registry.get("cleanup_service")
        self.homebridge_monitor  = registry.get("homebridge_monitor")
        self.network_scanner     = registry.get("network_scanner")
        self.pihole_monitor      = registry.get("pihole_monitor")
        self.alert_service       = registry.get("alert_service")
        self.display_service     = registry.get("display_service")
        self.vpn_monitor         = registry.get("vpn_monitor")
        self.led_service         = registry.get("led_service")
        self.hardware_monitor    = registry.get("hardware_monitor")
        self.audio_alert_service = registry.get("audio_alert_service")

        self._badges    = {}
        self._menu_btns = {}

        self.hardware_info_window    = None
        self.fan_window              = None
        self.monitor_window          = None
        self.network_window          = None
        self.usb_window              = None
        self.launchers_window        = None
        self.disk_window             = None
        self.process_window          = None
        self.service_window          = None
        self.crontab_window          = None
        self.history_window          = None
        self.update_window           = None
        self.theme_window            = None
        self.homebridge_window       = None
        self.log_viewer_window       = None
        self.network_local_window    = None
        self.pihole_window           = None
        self.alert_history_window    = None
        self.display_window          = None
        self.vpn_window              = None
        self.overview_window         = None
        self.led_window              = None
        self.camera_window           = None
        self.services_manager_window = None
        self.button_manager_window   = None

        self._uptime_tick = 0

        logger.info(f"[MainWindow] Dashboard iniciado en {self.system_utils.get_hostname()}")

        self._create_ui()
        self._start_update_loop()

    def _create_ui(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        header_bar = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'], height=56)
        header_bar.pack(fill="x", padx=5, pady=(5, 0))
        header_bar.pack_propagate(False)

        hostname = self.system_utils.get_hostname()
        ctk.CTkLabel(
            header_bar,
            text=f"  {hostname}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="w",
        ).pack(side="left", padx=12)

        ctk.CTkLabel(
            header_bar,
            text="SISTEMA DE MONITOREO",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
            anchor="center",
        ).pack(side="left", expand=True)

        self._uptime_label = ctk.CTkLabel(
            header_bar,
            text=f"{Icons.UPTIME} --",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            anchor="e",
        )
        self._uptime_label.pack(side="right", padx=(0, 4))

        self._clock_label = ctk.CTkLabel(
            header_bar,
            text="00:00:00",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="e",
        )
        self._clock_label.pack(side="right", padx=12)

        ctk.CTkFrame(main_frame, fg_color=COLORS['border'], height=1,
                     corner_radius=0).pack(fill="x", padx=5, pady=(0, 4))

        menu_container = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'])
        menu_container.pack(fill="both", expand=True, padx=5, pady=5)

        self.menu_canvas = ctk.CTkCanvas(
            menu_container, bg=COLORS['bg_medium'], highlightthickness=0)
        self.menu_canvas.pack(side="left", fill="both", expand=True)

        menu_scrollbar = ctk.CTkScrollbar(
            menu_container, orientation="vertical",
            command=self.menu_canvas.yview, width=30)
        menu_scrollbar.pack(side="right", fill="y")

        StyleManager.style_scrollbar_ctk(menu_scrollbar)
        self.menu_canvas.configure(yscrollcommand=menu_scrollbar.set)

        self.menu_inner = ctk.CTkFrame(self.menu_canvas, fg_color=COLORS['bg_medium'])
        self.menu_canvas.create_window(
            (0, 0), window=self.menu_inner, anchor="nw", width=DSI_WIDTH - 50)
        self.menu_inner.bind(
            "<Configure>",
            lambda e: self.menu_canvas.configure(
                scrollregion=self.menu_canvas.bbox("all")))

        self._create_menu_buttons()

        self._wm = WindowManager(self.registry, self._menu_btns)
        self._wm.apply_config()

    def _create_menu_buttons(self):
        buttons_config = [
            (BL.HARDWARE_INFO,     self.open_hardware_info,    []),
            (BL.FAN_CONTROL,       self.open_fan_control,      ["temp_fan"]),
            (BL.LED_RGB,           self.open_led_window,       []),
            (BL.MONITOR_PLACA,     self.open_monitor_window,   ["temp_monitor", "cpu", "ram"]),
            (BL.MONITOR_RED,       self.open_network_window,   []),
            (BL.MONITOR_USB,       self.open_usb_window,       []),
            (BL.MONITOR_DISCO,     self.open_disk_window,      ["disk"]),
            (BL.LANZADORES,        self.open_launchers,        []),
            (BL.PROCESOS,          self.open_process_window,   []),
            (BL.SERVICIOS,         self.open_service_window,   ["services"]),
            (BL.SERVICIOS_DASH,    self.open_services_manager, []),
            (BL.CRONTAB,           self.open_crontab_window,   []),
            (BL.BOTONES,           self.open_button_manager,   []),
            (BL.HISTORICO,         self.open_history_window,   []),
            (BL.ACTUALIZACIONES,   self.open_update_window,    ["updates"]),
            (BL.HOMEBRIDGE,        self.open_homebridge,       ["hb_offline", "hb_on", "hb_fault"]),
            (BL.VISOR_LOGS,        self.open_log_viewer,       []),
            (BL.RED_LOCAL,         self.open_network_local,    []),
            (BL.PIHOLE,            self.open_pihole,           ["pihole_offline"]),
            (BL.VPN,               self.open_vpn_window,       ["vpn_offline"]),
            (BL.HISTORIAL_ALERTAS, self.open_alert_history,    []),
            (BL.BRILLO,            self.open_display_window,   []),
            (BL.RESUMEN,           self.open_overview,         []),
            (BL.CAMARA,            self.open_camera_window,    []),
            (BL.TEMA,              self.open_theme_selector,   []),
            (BL.REINICIAR,         self.restart_application,   []),
            (BL.SALIR,             self.exit_application,      []),
        ]

        columns = 2
        for i, (text, command, badge_keys) in enumerate(buttons_config):
            row = i // columns
            col = i % columns
            btn = make_futuristic_button(
                self.menu_inner, text, command=command,
                font_size=FONT_SIZES['large'], width=30, height=15)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self._menu_btns[text] = btn
            for j, key in enumerate(badge_keys):
                self._create_badge(btn, key, offset_index=j)

        for c in range(columns):
            self.menu_inner.grid_columnconfigure(c, weight=1)

    # ── Badges ────────────────────────────────────────────────────────────────

    def _btn_active(self, text_key):
        btn = self._menu_btns.get(text_key)
        if btn:
            try:
                btn.configure(fg_color=COLORS['bg_light'],
                              border_color=COLORS['primary'], border_width=2)
            except Exception:
                pass

    def _btn_idle(self, text_key):
        btn = self._menu_btns.get(text_key)
        if btn:
            try:
                btn.configure(fg_color=COLORS['bg_dark'],
                              border_color=COLORS['border'], border_width=1)
            except Exception:
                pass

    def _create_badge(self, btn, key, offset_index=0):
        BADGE_SIZE = 36
        x_offset = -6 - offset_index * (BADGE_SIZE + 4)
        badge_canvas = tk.Canvas(
            btn, width=BADGE_SIZE, height=BADGE_SIZE,
            bg=COLORS['bg_dark'], highlightthickness=0, bd=0)
        badge_canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)
        oval = badge_canvas.create_oval(
            1, 1, BADGE_SIZE - 1, BADGE_SIZE - 1,
            fill=COLORS['danger'], outline="")
        txt = badge_canvas.create_text(
            BADGE_SIZE // 2, BADGE_SIZE // 2,
            text="0", fill="white", font=(FONT_FAMILY, 13, "bold"))
        self._badges[key] = (badge_canvas, oval, txt, x_offset)
        badge_canvas.place_forget()

    _TEMP_WARN = 60
    _TEMP_CRIT = 70
    _CPU_WARN  = 75
    _CPU_CRIT  = 90
    _RAM_WARN  = 75
    _RAM_CRIT  = 90
    _DISK_WARN = 80
    _DISK_CRIT = 90

    def _update_badge(self, key, value, color=None):
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        if value > 0:
            display = str(value) if value < 100 else "99+"
            canvas.itemconfigure(txt, text=display)
            if color is None:
                color = COLORS['danger'] if key == "services" else COLORS.get('warning', '#ffaa00')
            canvas.itemconfigure(oval, fill=color)
            txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
            canvas.itemconfigure(txt, fill=txt_color)
            canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)
        else:
            canvas.place_forget()

    def _update_badge_temp(self, key, temp, color):
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        canvas.itemconfigure(txt, text=f"{temp}{Icons.DEGREE}")
        canvas.itemconfigure(oval, fill=color)
        txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
        canvas.itemconfigure(txt, fill=txt_color)
        canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)

    # ── Apertura de ventanas ──────────────────────────────────────────────────

    def open_hardware_info(self):
        if self.hardware_info_window is None or not self.hardware_info_window.winfo_exists():
            self._btn_active(BL.HARDWARE_INFO)
            self.hardware_info_window = HardwareInfoWindow(self.root, self.system_monitor)
            self.hardware_info_window.bind("<Destroy>", lambda e: self._btn_idle(BL.HARDWARE_INFO))
        else:
            self.hardware_info_window.lift()

    def open_fan_control(self):
        if self.fan_window is None or not self.fan_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Control Ventiladores")
            self._btn_active(BL.FAN_CONTROL)
            self.fan_window = FanControlWindow(self.root, self.fan_controller, self.system_monitor, fan_service=self.fan_service)
            self.fan_window.bind("<Destroy>", lambda e: self._btn_idle(BL.FAN_CONTROL))
        else:
            self.fan_window.lift()

    def open_led_window(self):
        if self.led_window is None or not self.led_window.winfo_exists():
            self._btn_active(BL.LED_RGB)
            self.led_window = LedWindow(self.root, self.led_service)
            self.led_window.bind("<Destroy>", lambda e: self._btn_idle(BL.LED_RGB))
        else:
            self.led_window.lift()

    def open_monitor_window(self):
        if self.monitor_window is None or not self.monitor_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Placa")
            self._btn_active(BL.MONITOR_PLACA)
            self.monitor_window = MonitorWindow(self.root, self.system_monitor, self.hardware_monitor)
            self.monitor_window.bind("<Destroy>", lambda e: self._btn_idle(BL.MONITOR_PLACA))
        else:
            self.monitor_window.lift()

    def open_network_window(self):
        if self.network_window is None or not self.network_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Red")
            self._btn_active(BL.MONITOR_RED)
            self.network_window = NetworkWindow(self.root, network_monitor=self.network_monitor)
            self.network_window.bind("<Destroy>", lambda e: self._btn_idle(BL.MONITOR_RED))
        else:
            self.network_window.lift()

    def open_usb_window(self):
        if self.usb_window is None or not self.usb_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor USB")
            self._btn_active(BL.MONITOR_USB)
            self.usb_window = USBWindow(self.root)
            self.usb_window.bind("<Destroy>", lambda e: self._btn_idle(BL.MONITOR_USB))
        else:
            self.usb_window.lift()

    def open_disk_window(self):
        if self.disk_window is None or not self.disk_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Disco")
            self._btn_active(BL.MONITOR_DISCO)
            self.disk_window = DiskWindow(self.root, self.disk_monitor)
            self.disk_window.bind("<Destroy>", lambda e: self._btn_idle(BL.MONITOR_DISCO))
        else:
            self.disk_window.lift()

    def open_launchers(self):
        if self.launchers_window is None or not self.launchers_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Lanzadores")
            self._btn_active(BL.LANZADORES)
            self.launchers_window = LaunchersWindow(self.root)
            self.launchers_window.bind("<Destroy>", lambda e: self._btn_idle(BL.LANZADORES))
        else:
            self.launchers_window.lift()

    def open_process_window(self):
        if self.process_window is None or not self.process_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Procesos")
            self._btn_active(BL.PROCESOS)
            self.process_window = ProcessWindow(self.root, self.process_monitor)
            self.process_window.bind("<Destroy>", lambda e: self._btn_idle(BL.PROCESOS))
        else:
            self.process_window.lift()

    def open_service_window(self):
        if self.service_window is None or not self.service_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Servicios")
            self._btn_active(BL.SERVICIOS)
            self.service_window = ServiceWindow(self.root, self.service_monitor)
            self.service_window.bind("<Destroy>", lambda e: self._btn_idle(BL.SERVICIOS))
        else:
            self.service_window.lift()

    def open_services_manager(self):
        if self.services_manager_window is None or not self.services_manager_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Servicios Dashboard")
            self._btn_active(BL.SERVICIOS_DASH)
            self.services_manager_window = ServicesManagerWindow(self.root, registry=self.registry)
            self.services_manager_window.bind("<Destroy>", lambda e: self._btn_idle(BL.SERVICIOS_DASH))
        else:
            self.services_manager_window.lift()

    def open_crontab_window(self):
        if self.crontab_window is None or not self.crontab_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Gestor Crontab")
            self._btn_active(BL.CRONTAB)
            self.crontab_window = CrontabWindow(self.root)
            self.crontab_window.bind("<Destroy>", lambda e: self._btn_idle(BL.CRONTAB))
        else:
            self.crontab_window.lift()

    def open_button_manager(self):
        if self.button_manager_window is None or not self.button_manager_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Gestor de Botones")
            self._btn_active(BL.BOTONES)
            self.button_manager_window = ButtonManagerWindow(self.root, registry=self.registry, window_manager=self._wm)
            self.button_manager_window.bind("<Destroy>", lambda e: self._btn_idle(BL.BOTONES))
        else:
            self.button_manager_window.lift()

    def open_history_window(self):
        if self.history_window is None or not self.history_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Historico Datos")
            self._btn_active(BL.HISTORICO)
            self.history_window = HistoryWindow(self.root, self.cleanup_service)
            self.history_window.bind("<Destroy>", lambda e: self._btn_idle(BL.HISTORICO))
        else:
            self.history_window.lift()

    def open_update_window(self):
        if self.update_window is None or not self.update_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Actualizaciones")
            self._btn_active(BL.ACTUALIZACIONES)
            self.update_window = UpdatesWindow(self.root, self.update_monitor)
            self.update_window.bind("<Destroy>", lambda e: self._btn_idle(BL.ACTUALIZACIONES))
        else:
            self.update_window.lift()

    def open_homebridge(self):
        if self.homebridge_window is None or not self.homebridge_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Homebridge")
            self._btn_active(BL.HOMEBRIDGE)
            self.homebridge_window = HomebridgeWindow(self.root, self.homebridge_monitor)
            self.homebridge_window.bind("<Destroy>", lambda e: self._btn_idle(BL.HOMEBRIDGE))
        else:
            self.homebridge_window.lift()

    def open_log_viewer(self):
        if self.log_viewer_window is None or not self.log_viewer_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Visor de Logs")
            self._btn_active(BL.VISOR_LOGS)
            self.log_viewer_window = LogViewerWindow(self.root)
            self.log_viewer_window.bind("<Destroy>", lambda e: self._btn_idle(BL.VISOR_LOGS))
        else:
            self.log_viewer_window.lift()

    def open_network_local(self):
        if self.network_local_window is None or not self.network_local_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Red Local")
            self._btn_active(BL.RED_LOCAL)
            self.network_local_window = NetworkLocalWindow(self.root, network_scanner=self.network_scanner)
            self.network_local_window.bind("<Destroy>", lambda e: self._btn_idle(BL.RED_LOCAL))
        else:
            self.network_local_window.lift()

    def open_pihole(self):
        if self.pihole_window is None or not self.pihole_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Pi-hole")
            self._btn_active(BL.PIHOLE)
            self.pihole_window = PiholeWindow(self.root, self.pihole_monitor)
            self.pihole_window.bind("<Destroy>", lambda e: self._btn_idle(BL.PIHOLE))
        else:
            self.pihole_window.lift()

    def open_vpn_window(self):
        if self.vpn_window is None or not self.vpn_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Gestor VPN")
            self._btn_active(BL.VPN)
            self.vpn_window = VpnWindow(self.root, self.vpn_monitor)
            self.vpn_window.bind("<Destroy>", lambda e: self._btn_idle(BL.VPN))
        else:
            self.vpn_window.lift()

    def open_alert_history(self):
        if self.alert_history_window is None or not self.alert_history_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Historial Alertas")
            self._btn_active(BL.HISTORIAL_ALERTAS)
            self.alert_history_window = AlertHistoryWindow(self.root, self.alert_service)
            self.alert_history_window.bind("<Destroy>", lambda e: self._btn_idle(BL.HISTORIAL_ALERTAS))
        else:
            self.alert_history_window.lift()

    def open_display_window(self):
        if self.display_window is None or not self.display_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Brillo Pantalla")
            self._btn_active(BL.BRILLO)
            self.display_window = DisplayWindow(self.root, self.display_service)
            self.display_window.bind("<Destroy>", lambda e: self._btn_idle(BL.BRILLO))
        else:
            self.display_window.lift()

    def open_overview(self):
        if self.overview_window is None or not self.overview_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Resumen Sistema")
            self._btn_active(BL.RESUMEN)
            self.overview_window = OverviewWindow(
                self.root,
                system_monitor=self.system_monitor,
                service_monitor=self.service_monitor,
                pihole_monitor=self.pihole_monitor,
                network_monitor=self.network_monitor,
                disk_monitor=self.disk_monitor,
            )
            self.overview_window.bind("<Destroy>", lambda e: self._btn_idle(BL.RESUMEN))
        else:
            self.overview_window.lift()

    def open_camera_window(self):
        if self.camera_window is None or not self.camera_window.winfo_exists():
            self._btn_active(BL.CAMARA)
            self.camera_window = CameraWindow(self.root)
            self.camera_window.bind("<Destroy>", lambda e: self._btn_idle(BL.CAMARA))
        else:
            self.camera_window.lift()

    def open_theme_selector(self):
        if self.theme_window is None or not self.theme_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Cambiar Tema")
            self._btn_active(BL.TEMA)
            self.theme_window = ThemeSelector(self.root)
            self.theme_window.bind("<Destroy>", lambda e: self._btn_idle(BL.TEMA))
        else:
            self.theme_window.lift()

    # ── Salir / Reiniciar ─────────────────────────────────────────────────────

    def exit_application(self):
        selection_window = ctk.CTkToplevel(self.root)
        selection_window.title("Opciones de Salida")
        selection_window.configure(fg_color=COLORS['bg_medium'])
        selection_window.geometry("450x280")
        selection_window.resizable(False, False)
        selection_window.overrideredirect(True)
        selection_window.update_idletasks()
        x = DSI_X + (450 // 2) - 40
        y = DSI_Y + (280 // 2) - 40
        selection_window.geometry(f"450x280+{x}+{y}")
        selection_window.transient(self.root)
        selection_window.after(150, selection_window.focus_set)
        selection_window.grab_set()

        main_frame = ctk.CTkFrame(selection_window, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=5)

        ctk.CTkLabel(
            main_frame,
            text=f"{Icons.WARNING} \u00bfQu\u00e9 deseas hacer?",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        ).pack(pady=(10, 10))

        selection_var = ctk.StringVar(master=selection_window, value="exit")
        options_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'])
        options_frame.pack(fill="x", pady=5, padx=20)

        exit_radio = ctk.CTkRadioButton(
            options_frame, text="  Salir de la aplicaci\u00f3n",
            variable=selection_var, value="exit",
            text_color=COLORS['text'], font=(FONT_FAMILY, FONT_SIZES['medium']))
        exit_radio.pack(anchor="w", padx=20, pady=12)

        shutdown_radio = ctk.CTkRadioButton(
            options_frame, text=f"{Icons.POWER_OFF}  Apagar el sistema",
            variable=selection_var, value="shutdown",
            text_color=COLORS['text'], font=(FONT_FAMILY, FONT_SIZES['medium']))
        shutdown_radio.pack(anchor="w", padx=20, pady=12)

        StyleManager.style_radiobutton_ctk(exit_radio, radiobutton_width=30, radiobutton_height=30)
        StyleManager.style_radiobutton_ctk(shutdown_radio, radiobutton_width=30, radiobutton_height=30)

        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(side="bottom", fill="x", pady=(5, 10))

        def on_confirm():
            selected = selection_var.get()
            selection_window.grab_release()
            selection_window.destroy()
            if selected == "exit":
                def do_exit():
                    logger.info("[MainWindow] Cerrando dashboard por solicitud del usuario")
                    self.root.quit()
                    self.root.destroy()
                confirm_dialog(
                    parent=self.root,
                    text="\u00bfConfirmar salir de la aplicaci\u00f3n?",
                    title=" Confirmar Salida", on_confirm=do_exit, on_cancel=None)
            else:
                def do_shutdown():
                    logger.info("[MainWindow] Iniciando apagado del sistema")
                    shutdown_script = str(SCRIPTS_DIR / "apagado.sh")
                    terminal_dialog(parent=self.root, script_path=shutdown_script,
                                    title=f"{Icons.POWER_OFF}  APAGANDO SISTEMA...")
                confirm_dialog(
                    parent=self.root,
                    text=f"{Icons.WARNING} \u00bfConfirmar APAGAR el sistema?\n\nEsta acci\u00f3n apagar\u00e1 completamente el equipo.",
                    title=" Confirmar Apagado", on_confirm=do_shutdown, on_cancel=None)

        def on_cancel():
            logger.debug("[MainWindow] Dialogo de salida cancelado")
            selection_window.grab_release()
            selection_window.destroy()

        make_futuristic_button(buttons_frame, text="Cancelar", command=on_cancel,
                               width=20, height=10).pack(side="right", padx=5)
        make_futuristic_button(buttons_frame, text="Continuar", command=on_confirm,
                               width=15, height=8).pack(side="right", padx=5)
        selection_window.bind("<Escape>", lambda e: on_cancel())

    def restart_application(self):
        def do_restart():
            logger.info("[MainWindow] Reiniciando dashboard")
            self.root.quit()
            self.root.destroy()
            os.execv(sys.executable,
                     [sys.executable, os.path.abspath(sys.argv[0])] + sys.argv[1:])
        confirm_dialog(
            parent=self.root,
            text="\u00bfReiniciar el dashboard?\n\nSe aplicar\u00e1n los cambios realizados.",
            title=f"{Icons.REINICIAR} Reiniciar Dashboard",
            on_confirm=do_restart, on_cancel=None)

    # ── Loop de actualizacion ─────────────────────────────────────────────────

    def _tick_clock(self):
        self._clock_label.configure(text=datetime.now().strftime("%H:%M:%S"))
        self._uptime_tick += 1
        if self._uptime_tick == 1 or self._uptime_tick >= 60:
            self._uptime_tick = 1
            try:
                uptime_str = self.system_monitor.get_current_stats().get("uptime_str", "--")
                self._uptime_label.configure(text=uptime_str)
            except Exception:
                pass
        self.root.after(1000, self._tick_clock)

    def _start_update_loop(self):
        self._tick_clock()
        self._update()

    def _update(self):
        """Actualiza los badges del menu. Solo lee caches — nunca bloquea la UI."""
        try:
            pending = self.update_monitor.cached_result.get('pending', 0)
            self._update_badge("updates", pending)
            self._update_badge("hb_offline", self.homebridge_monitor.get_offline_count())
            self._update_badge("hb_on", self.homebridge_monitor.get_on_count(),
                               color=COLORS.get('warning', '#ffaa00'))
            self._update_badge("hb_fault", self.homebridge_monitor.get_fault_count())
            self._update_badge("pihole_offline", self.pihole_monitor.get_offline_count())
            self._update_badge("vpn_offline", self.vpn_monitor.get_offline_count())
        except Exception:
            pass

        try:
            stats  = self.service_monitor.get_stats()
            failed = stats.get('failed', 0)
            self._update_badge("services", failed)
        except Exception:
            pass

        try:
            sys_stats = self.system_monitor.get_current_stats()
            temp = sys_stats['temp']
            if temp >= self._TEMP_CRIT:
                temp_color, show_temp = COLORS['danger'], True
            elif temp >= self._TEMP_WARN:
                temp_color, show_temp = COLORS.get('warning', '#ffaa00'), True
            else:
                show_temp = False

            if show_temp:
                self._update_badge_temp("temp_fan",     int(temp), temp_color)
                self._update_badge_temp("temp_monitor", int(temp), temp_color)
            else:
                self._update_badge("temp_fan", 0)
                self._update_badge("temp_monitor", 0)

            cpu = sys_stats['cpu']
            if cpu >= self._CPU_CRIT:
                self._update_badge("cpu", int(cpu), COLORS['danger'])
            elif cpu >= self._CPU_WARN:
                self._update_badge("cpu", int(cpu), COLORS.get('warning', '#ffaa00'))
            else:
                self._update_badge("cpu", 0)

            ram = sys_stats['ram']
            if ram >= self._RAM_CRIT:
                self._update_badge("ram", int(ram), COLORS['danger'])
            elif ram >= self._RAM_WARN:
                self._update_badge("ram", int(ram), COLORS.get('warning', '#ffaa00'))
            else:
                self._update_badge("ram", 0)

            disk = sys_stats['disk_usage']
            if disk >= self._DISK_CRIT:
                self._update_badge("disk", int(disk), COLORS['danger'])
            elif disk >= self._DISK_WARN:
                self._update_badge("disk", int(disk), COLORS.get('warning', '#ffaa00'))
            else:
                self._update_badge("disk", 0)
        except Exception:
            pass

        self.root.after(self.update_interval, self._update)
```
