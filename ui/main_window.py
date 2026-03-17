"""
Ventana principal del sistema de monitoreo.

Responsabilidades de este fichero:
  - Construir el layout (header, pestanas, area de botones, footer)
  - Gestionar el cambio de pestana y el filtrado de botones por visibilidad
  - Coordinar BadgeManager, UpdateLoop y WindowLifecycleManager

Todo lo demas vive en modulos especializados:
  ui/main_badges.py         — BadgeManager
  ui/main_update_loop.py    — UpdateLoop
  ui/main_system_actions.py — exit_application, restart_application
  ui/window_lifecycle.py    — WindowLifecycleManager
  ui/window_manager.py      — WindowManager (visibilidad JSON)
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, Icons
import config.button_labels as BL
from config.settings import UI as UICfg
from ui.styles import StyleManager, make_futuristic_button
from ui.windows import (FanControlWindow, MonitorWindow, NetworkWindow, USBWindow, ProcessWindow, ServiceWindow,
                        HistoryWindow, LaunchersWindow, ThemeSelector, DiskWindow, UpdatesWindow, HomebridgeWindow,
                        NetworkLocalWindow, PiholeWindow, AlertHistoryWindow, DisplayWindow, VpnWindow, OverviewWindow,
                        LedWindow, CameraWindow, ServicesManagerWindow, LogViewerWindow, ButtonManagerWindow, CrontabWindow,
                        HardwareInfoWindow, SSHWindow, WiFiWindow, ConfigEditorWindow, AudioWindow, WeatherWindow,
                        I2CWindow, GPIOWindow, ServiceWatchdogWindow)
from ui.window_manager import WindowManager
from ui.window_lifecycle import WindowLifecycleManager
from ui.main_badges import BadgeManager
from ui.main_update_loop import UpdateLoop
from ui.main_system_actions import exit_application, restart_application
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow:
    """Ventana principal del dashboard"""

    def __init__(self, root, registry, update_interval=2000):
        self.root            = root
        self.registry        = registry
        self.update_interval = update_interval
        self.system_utils    = SystemUtils()

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
        self.ssh_monitor         = registry.get("ssh_monitor")
        self.wifi_monitor        = registry.get("wifi_monitor")
        self.audio_service       = registry.get("audio_service")
        self.weather_service     = registry.get("weather_service")
        self.i2c_monitor         = registry.get("i2c_monitor")
        self.gpio_monitor        = registry.get("gpio_monitor")
        self.service_watchdog   = registry.get("service_watchdog")

        self._menu_btns   = {}
        self._active_tab  = UICfg.MENU_TABS[0][0]
        self._tab_buttons = {}

        logger.info("[MainWindow] Dashboard iniciado en %s", self.system_utils.get_hostname())

        self._create_ui()
        self._update_loop.start()

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _create_ui(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # ── Header ───────────────────────────────────────────────────────────
        header_bar = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'], height=56)
        header_bar.pack(fill="x", padx=5, pady=(5, 0))
        header_bar.pack_propagate(False)

        ctk.CTkLabel(
            header_bar,
            text=f"  {self.system_utils.get_hostname()}",
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

        uptime_label = ctk.CTkLabel(
            header_bar,
            text=f"{Icons.UPTIME} --",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            anchor="e",
        )
        uptime_label.pack(side="right", padx=(0, 4))

        clock_label = ctk.CTkLabel(
            header_bar,
            text="00:00:00",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="e",
        )
        clock_label.pack(side="right", padx=12)

        ctk.CTkFrame(main_frame, fg_color=COLORS['border'], height=1,
                     corner_radius=0).pack(fill="x", padx=5, pady=(0, 4))

        # ── Zona scrollable (pestañas + botones + footer) ─────────────────────
        scroll_container = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        self._menu_canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        self._menu_canvas.pack(side="left", fill="both", expand=True)

        menu_scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=self._menu_canvas.yview, width=30)
        menu_scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(menu_scrollbar)
        self._menu_canvas.configure(yscrollcommand=menu_scrollbar.set)

        menu_inner = ctk.CTkFrame(self._menu_canvas, fg_color=COLORS['bg_medium'])
        self._menu_canvas.create_window(
            (0, 0), window=menu_inner, anchor="nw", width=DSI_WIDTH - 50)
        menu_inner.bind(
            "<Configure>",
            lambda e: self._menu_canvas.configure(
                scrollregion=self._menu_canvas.bbox("all")))

        # ── Pestañas con scroll horizontal ───────────────────────────────────
        _TAB_W, _TAB_H = 130, 44

        tab_wrapper = ctk.CTkFrame(menu_inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        tab_wrapper.pack(fill="x", padx=8, pady=(8, 0))

        tab_canvas = tk.Canvas(tab_wrapper, bg=COLORS['bg_dark'],
                               highlightthickness=0, height=_TAB_H + 8)
        tab_canvas.pack(fill="x", expand=True)

        tab_scrollbar = ctk.CTkScrollbar(
            tab_wrapper, orientation="horizontal",
            command=tab_canvas.xview, height=30)
        tab_scrollbar.pack(fill="x", padx=4, pady=(0, 4))
        StyleManager.style_scrollbar_ctk(tab_scrollbar)
        tab_canvas.configure(xscrollcommand=tab_scrollbar.set)

        tab_inner = ctk.CTkFrame(tab_canvas, fg_color=COLORS['bg_dark'])
        tab_canvas.create_window((0, 0), window=tab_inner, anchor="nw")
        tab_inner.bind("<Configure>",
                       lambda e: tab_canvas.configure(
                           scrollregion=tab_canvas.bbox("all")))

        for key, icon, label, _ in UICfg.MENU_TABS:
            btn = ctk.CTkButton(
                tab_inner,
                text=f"{icon}  {label}",
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                fg_color=COLORS['bg_dark'],
                text_color=COLORS['text_dim'],
                hover_color=COLORS['bg_light'],
                corner_radius=6,
                width=_TAB_W, height=_TAB_H,
                command=lambda k=key: self._switch_tab(k),
            )
            btn.pack(side="left", padx=4, pady=4)
            self._tab_buttons[key] = btn

        # ── Área de botones ───────────────────────────────────────────────────
        self._btn_area = ctk.CTkFrame(menu_inner, fg_color=COLORS['bg_medium'])
        self._btn_area.pack(fill="both", expand=True, padx=4, pady=4)

        # ── Footer ────────────────────────────────────────────────────────────
        footer = ctk.CTkFrame(menu_inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        footer.pack(fill="x", padx=8, pady=(4, 8))

        btn_gestor = make_futuristic_button(
            footer, BL.BOTONES, command=lambda: self._wlm.open("button_manager"),
            font_size=FONT_SIZES['small'], width=20, height=10)
        btn_gestor.pack(side="left", padx=8, pady=8, expand=True, fill="x")
        self._menu_btns[BL.BOTONES] = btn_gestor

        make_futuristic_button(
            footer, BL.REINICIAR, command=lambda: restart_application(self.root, self._update_loop),
            font_size=FONT_SIZES['small'], width=20, height=10
        ).pack(side="left", padx=4, pady=8, expand=True, fill="x")

        make_futuristic_button(
            footer, BL.SALIR, command=lambda: exit_application(self.root, self._update_loop),
            font_size=FONT_SIZES['small'], width=20, height=10
        ).pack(side="left", padx=(4, 8), pady=8, expand=True, fill="x")

        # ── Módulos de soporte ────────────────────────────────────────────────
        self._badge_mgr = BadgeManager(menu_btns=self._menu_btns)

        self._wlm = WindowLifecycleManager(
            on_btn_active=self._btn_active,
            on_btn_idle=self._btn_idle,
        )
        self._register_windows()
        self._buttons_meta = self._build_buttons_meta()

        self._wm = WindowManager(self.registry, self._menu_btns)
        self._wm.set_rerender_callback(lambda: self._switch_tab(self._active_tab))

        self._update_loop = UpdateLoop(
            root=self.root,
            badge_mgr=self._badge_mgr,
            monitors={
                "system_monitor":     self.system_monitor,
                "update_monitor":     self.update_monitor,
                "homebridge_monitor": self.homebridge_monitor,
                "pihole_monitor":     self.pihole_monitor,
                "vpn_monitor":        self.vpn_monitor,
                "service_monitor":    self.service_monitor,
            },
            update_interval=self.update_interval,
            clock_label=clock_label,
            uptime_label=uptime_label,
            weather_service=self.weather_service,
        )

        # ── Render inicial ────────────────────────────────────────────────────
        self._switch_tab(self._active_tab)

    # ── Registro de ventanas hijas ────────────────────────────────────────────

    def _register_windows(self):
        r    = self._wlm.register
        root = self.root

        r("hardware_info",        BL.HARDWARE_INFO,
            lambda: HardwareInfoWindow(root, self.system_monitor))
        r("fan_control",          BL.FAN_CONTROL,
            lambda: FanControlWindow(root, self.fan_controller, self.system_monitor,
                                     fan_service=self.fan_service),
            badge_keys=["temp_fan"])
        r("led_window",           BL.LED_RGB,
            lambda: LedWindow(root, self.led_service))
        r("monitor_window",       BL.MONITOR_PLACA,
            lambda: MonitorWindow(root, self.system_monitor, self.hardware_monitor),
            badge_keys=["temp_monitor", "cpu", "ram"])
        r("network_window",       BL.MONITOR_RED,
            lambda: NetworkWindow(root, network_monitor=self.network_monitor))
        r("usb_window",           BL.MONITOR_USB,
            lambda: USBWindow(root))
        r("disk_window",          BL.MONITOR_DISCO,
            lambda: DiskWindow(root, self.disk_monitor),
            badge_keys=["disk"])
        r("launchers",            BL.LANZADORES,
            lambda: LaunchersWindow(root))
        r("process_window",       BL.PROCESOS,
            lambda: ProcessWindow(root, self.process_monitor))
        r("service_window",       BL.SERVICIOS,
            lambda: ServiceWindow(root, self.service_monitor),
            badge_keys=["services"])
        r("services_manager",     BL.SERVICIOS_DASH,
            lambda: ServicesManagerWindow(root, registry=self.registry))
        r("crontab_window",       BL.CRONTAB,
            lambda: CrontabWindow(root))
        r("history_window",       BL.HISTORICO,
            lambda: HistoryWindow(root, self.cleanup_service))
        r("update_window",        BL.ACTUALIZACIONES,
            lambda: UpdatesWindow(root, self.update_monitor),
            badge_keys=["updates"])
        r("homebridge",           BL.HOMEBRIDGE,
            lambda: HomebridgeWindow(root, self.homebridge_monitor),
            badge_keys=["hb_offline", "hb_on", "hb_fault"])
        r("log_viewer",           BL.VISOR_LOGS,
            lambda: LogViewerWindow(root))
        r("network_local",        BL.RED_LOCAL,
            lambda: NetworkLocalWindow(root, network_scanner=self.network_scanner))
        r("pihole",               BL.PIHOLE,
            lambda: PiholeWindow(root, self.pihole_monitor),
            badge_keys=["pihole_offline"])
        r("vpn_window",           BL.VPN,
            lambda: VpnWindow(root, self.vpn_monitor),
            badge_keys=["vpn_offline"])
        r("alert_history",        BL.HISTORIAL_ALERTAS,
            lambda: AlertHistoryWindow(root, self.alert_service))
        r("display_window",       BL.BRILLO,
            lambda: DisplayWindow(root, self.display_service))
        r("overview",             BL.RESUMEN,
            lambda: OverviewWindow(root,
                system_monitor=self.system_monitor,
                service_monitor=self.service_monitor,
                pihole_monitor=self.pihole_monitor,
                network_monitor=self.network_monitor,
                disk_monitor=self.disk_monitor))
        r("camera_window",        BL.CAMARA,
            lambda: CameraWindow(root))
        r("theme_selector",       BL.TEMA,
            lambda: ThemeSelector(root))
        r("ssh_window",           BL.SSH,
            lambda: SSHWindow(root, self.ssh_monitor))
        r("wifi_window",          BL.WIFI,
            lambda: WiFiWindow(root, self.wifi_monitor))
        r("config_editor_window", BL.CONFIG,
            lambda: ConfigEditorWindow(root))
        r("audio_window",         BL.AUDIO,
            lambda: AudioWindow(root, self.audio_service))
        r("weather_window",       BL.CLIMA,
            lambda: WeatherWindow(root, self.weather_service),
            badge_keys=["weather_rain"])
        r("i2c_window",           BL.I2C,
            lambda: I2CWindow(root, self.i2c_monitor))
        r("gpio_window",          BL.GPIO,
            lambda: GPIOWindow(root, self.gpio_monitor))
        r("service_watchdog",     BL.SERVICE_WATCHDOG,
            lambda: ServiceWatchdogWindow(root, self.service_monitor, self.service_watchdog),
            badge_keys=["service_watchdog_restarts"])
        r("button_manager",       BL.BOTONES,
            lambda: ButtonManagerWindow(root,
                registry=self.registry, window_manager=self._wm))

    # ── Mapa de botones: label → (command, [badge_keys]) ─────────────────────

    def _build_buttons_meta(self):
        return {
            BL.HARDWARE_INFO:     (lambda: self._wlm.open("hardware_info"),        []),
            BL.FAN_CONTROL:       (lambda: self._wlm.open("fan_control"),          ["temp_fan"]),
            BL.LED_RGB:           (lambda: self._wlm.open("led_window"),           []),
            BL.MONITOR_PLACA:     (lambda: self._wlm.open("monitor_window"),       ["temp_monitor", "cpu", "ram"]),
            BL.MONITOR_RED:       (lambda: self._wlm.open("network_window"),       []),
            BL.MONITOR_USB:       (lambda: self._wlm.open("usb_window"),           []),
            BL.MONITOR_DISCO:     (lambda: self._wlm.open("disk_window"),          ["disk"]),
            BL.LANZADORES:        (lambda: self._wlm.open("launchers"),            []),
            BL.PROCESOS:          (lambda: self._wlm.open("process_window"),       []),
            BL.SERVICIOS:         (lambda: self._wlm.open("service_window"),       ["services"]),
            BL.SERVICIOS_DASH:    (lambda: self._wlm.open("services_manager"),     []),
            BL.CRONTAB:           (lambda: self._wlm.open("crontab_window"),       []),
            BL.HISTORICO:         (lambda: self._wlm.open("history_window"),       []),
            BL.ACTUALIZACIONES:   (lambda: self._wlm.open("update_window"),        ["updates"]),
            BL.HOMEBRIDGE:        (lambda: self._wlm.open("homebridge"),           ["hb_offline", "hb_on", "hb_fault"]),
            BL.VISOR_LOGS:        (lambda: self._wlm.open("log_viewer"),           []),
            BL.RED_LOCAL:         (lambda: self._wlm.open("network_local"),        []),
            BL.PIHOLE:            (lambda: self._wlm.open("pihole"),               ["pihole_offline"]),
            BL.VPN:               (lambda: self._wlm.open("vpn_window"),           ["vpn_offline"]),
            BL.HISTORIAL_ALERTAS: (lambda: self._wlm.open("alert_history"),        []),
            BL.BRILLO:            (lambda: self._wlm.open("display_window"),       []),
            BL.RESUMEN:           (lambda: self._wlm.open("overview"),             []),
            BL.CAMARA:            (lambda: self._wlm.open("camera_window"),        []),
            BL.TEMA:              (lambda: self._wlm.open("theme_selector"),       []),
            BL.SSH:               (lambda: self._wlm.open("ssh_window"),           []),
            BL.WIFI:              (lambda: self._wlm.open("wifi_window"),          []),
            BL.CONFIG:            (lambda: self._wlm.open("config_editor_window"), []),
            BL.AUDIO:             (lambda: self._wlm.open("audio_window"),         []),
            BL.CLIMA:             (lambda: self._wlm.open("weather_window"),       ["weather_rain"]),
            BL.I2C:               (lambda: self._wlm.open("i2c_window"),           []),
            BL.GPIO:              (lambda: self._wlm.open("gpio_window"),          []),
            BL.SERVICE_WATCHDOG:  (lambda: self._wlm.open("service_watchdog"),     ["service_watchdog_restarts"]),

        }

    # ── Cambio de pestaña ─────────────────────────────────────────────────────

    # Mapa inverso BL label → clave JSON para consultar ui_enabled
    _BL_TO_KEY = {v: k for k, v in {
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
        "service_watchdog":     BL.SERVICE_WATCHDOG,
    }.items()}

    def _switch_tab(self, key: str) -> None:
        self._active_tab = key

        for k, btn in self._tab_buttons.items():
            if k == key:
                btn.configure(fg_color=COLORS['primary'], text_color=COLORS['bg_dark'])
            else:
                btn.configure(fg_color=COLORS['bg_dark'], text_color=COLORS['text_dim'])

        for widget in self._btn_area.winfo_children():
            widget.destroy()

        bl_keys = next(
            (bl for tab_key, _, _, bl in UICfg.MENU_TABS if tab_key == key), [])

        columns  = UICfg.MENU_COLUMNS
        grid_pos = 0
        for bl_key in bl_keys:
            label = getattr(BL, bl_key, None)
            if label is None:
                logger.warning("[MainWindow] BL.%s no existe — omitido", bl_key)
                continue
            json_key = self._BL_TO_KEY.get(label)
            if json_key is not None and not self.registry.ui_enabled(json_key):
                continue
            meta = self._buttons_meta.get(label)
            if meta is None:
                logger.warning("[MainWindow] Sin meta para '%s' — omitido", label)
                continue
            command, badge_keys = meta
            btn = make_futuristic_button(
                self._btn_area, label, command=command,
                font_size=FONT_SIZES['large'], width=30, height=15)
            btn.grid(row=grid_pos // columns, column=grid_pos % columns,
                     padx=10, pady=10, sticky="nsew")
            self._menu_btns[label] = btn
            for j, bkey in enumerate(badge_keys):
                self._badge_mgr.create(btn, bkey, offset_index=j)
            grid_pos += 1

        for c in range(columns):
            self._btn_area.grid_columnconfigure(c, weight=1)

        self._btn_area.update_idletasks()
        self._menu_canvas.configure(scrollregion=self._menu_canvas.bbox("all"))

    # ── Estado de botones (usado por WindowLifecycleManager) ─────────────────

    def _btn_active(self, text_key: str) -> None:
        btn = self._menu_btns.get(text_key)
        if btn:
            try:
                btn.configure(fg_color=COLORS['bg_light'],
                              border_color=COLORS['primary'], border_width=2)
            except Exception:
                pass

    def _btn_idle(self, text_key: str) -> None:
        btn = self._menu_btns.get(text_key)
        if btn:
            try:
                btn.configure(fg_color=COLORS['bg_dark'],
                              border_color=COLORS['border'], border_width=1)
            except Exception:
                pass
