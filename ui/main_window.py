"""
Ventana principal del sistema de monitoreo
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_X, DSI_Y, SCRIPTS_DIR, Icons
import config.button_labels as BL
from config.settings import UI as UICfg
from ui.styles import StyleManager, make_futuristic_button
from ui.windows import (FanControlWindow, MonitorWindow, NetworkWindow, USBWindow, ProcessWindow, ServiceWindow,
                        HistoryWindow, LaunchersWindow, ThemeSelector, DiskWindow, UpdatesWindow, HomebridgeWindow,
                        NetworkLocalWindow, PiholeWindow, AlertHistoryWindow, DisplayWindow, VpnWindow, OverviewWindow,
                        LedWindow, CameraWindow, ServicesManagerWindow, LogViewerWindow, ButtonManagerWindow, CrontabWindow,
                        HardwareInfoWindow, SSHWindow, WiFiWindow, ConfigEditorWindow)
from ui.widgets import confirm_dialog, terminal_dialog
from ui.window_manager import WindowManager
from ui.window_lifecycle import WindowLifecycleManager
from utils.system_utils import SystemUtils
from utils.logger import get_logger
import sys
import os
from datetime import datetime

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

        self._badges       = {}
        self._menu_btns    = {}
        self._uptime_tick  = 0
        self._active_tab   = UICfg.MENU_TABS[0][0]
        self._tab_buttons  = {}

        logger.info(f"[MainWindow] Dashboard iniciado en {self.system_utils.get_hostname()}")

        self._create_ui()
        self._start_update_loop()

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _create_ui(self):
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # ── Header ───────────────────────────────────────────────────────────
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

        # ── Zona scrollable (pestañas + botones + footer) ─────────────────────
        scroll_container = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        self.menu_canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        self.menu_canvas.pack(side="left", fill="both", expand=True)

        menu_scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=self.menu_canvas.yview, width=30)
        menu_scrollbar.pack(side="right", fill="y")

        StyleManager.style_scrollbar_ctk(menu_scrollbar)
        self.menu_canvas.configure(yscrollcommand=menu_scrollbar.set)

        self.menu_inner = ctk.CTkFrame(self.menu_canvas, fg_color=COLORS['bg_medium'])
        self._canvas_window_id = self.menu_canvas.create_window(
            (0, 0), window=self.menu_inner, anchor="nw", width=DSI_WIDTH - 50)
        self.menu_inner.bind(
            "<Configure>",
            lambda e: self.menu_canvas.configure(
                scrollregion=self.menu_canvas.bbox("all")))

        # ── Pestañas con scroll horizontal ───────────────────────────────────
        _TAB_BTN_WIDTH  = 130   # ancho fijo táctil por pestaña (px)
        _TAB_BTN_HEIGHT = 44    # alto fijo táctil

        tab_wrapper = ctk.CTkFrame(self.menu_inner, fg_color=COLORS['bg_dark'],
                                   corner_radius=8)
        tab_wrapper.pack(fill="x", padx=8, pady=(8, 0))

        self._tab_canvas = tk.Canvas(
            tab_wrapper,
            bg=COLORS['bg_dark'],
            highlightthickness=0,
            height=_TAB_BTN_HEIGHT + 8,
        )
        self._tab_canvas.pack(fill="x", expand=True)

        tab_scrollbar = ctk.CTkScrollbar(
            tab_wrapper,
            orientation="horizontal",
            command=self._tab_canvas.xview,
            height=30,
        )
        tab_scrollbar.pack(fill="x", padx=4, pady=(0, 4))
        StyleManager.style_scrollbar_ctk(tab_scrollbar)
        self._tab_canvas.configure(xscrollcommand=tab_scrollbar.set)

        self._tab_inner = ctk.CTkFrame(self._tab_canvas, fg_color=COLORS['bg_dark'])
        self._tab_canvas_win = self._tab_canvas.create_window(
            (0, 0), window=self._tab_inner, anchor="nw")
        self._tab_inner.bind(
            "<Configure>",
            lambda e: self._tab_canvas.configure(
                scrollregion=self._tab_canvas.bbox("all")))

        for key, icon, label, _ in UICfg.MENU_TABS:
            btn = ctk.CTkButton(
                self._tab_inner,
                text=f"{icon}  {label}",
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                fg_color=COLORS['bg_dark'],
                text_color=COLORS['text_dim'],
                hover_color=COLORS['bg_light'],
                corner_radius=6,
                width=_TAB_BTN_WIDTH,
                height=_TAB_BTN_HEIGHT,
                command=lambda k=key: self._switch_tab(k),
            )
            btn.pack(side="left", padx=4, pady=4)
            self._tab_buttons[key] = btn

        # ── Área de botones de la pestaña activa ──────────────────────────────
        self._btn_area = ctk.CTkFrame(self.menu_inner, fg_color=COLORS['bg_medium'])
        self._btn_area.pack(fill="both", expand=True, padx=4, pady=4)

        # ── Footer (Gestor de Botones + Reiniciar + Salir) ────────────────────
        footer = ctk.CTkFrame(self.menu_inner, fg_color=COLORS['bg_dark'],
                              corner_radius=8)
        footer.pack(fill="x", padx=8, pady=(4, 8))

        btn_gestor = make_futuristic_button(
            footer, BL.BOTONES, command=lambda: self._wlm.open("button_manager"),
            font_size=FONT_SIZES['small'], width=20, height=10)
        btn_gestor.pack(side="left", padx=8, pady=8, expand=True, fill="x")
        self._menu_btns[BL.BOTONES] = btn_gestor

        btn_reiniciar = make_futuristic_button(
            footer, BL.REINICIAR, command=self.restart_application,
            font_size=FONT_SIZES['small'], width=20, height=10)
        btn_reiniciar.pack(side="left", padx=4, pady=8, expand=True, fill="x")

        btn_salir = make_futuristic_button(
            footer, BL.SALIR, command=self.exit_application,
            font_size=FONT_SIZES['small'], width=20, height=10)
        btn_salir.pack(side="left", padx=(4, 8), pady=8, expand=True, fill="x")

        # ── Ciclo de vida de ventanas hijas ───────────────────────────────────
        self._wlm = WindowLifecycleManager(
            on_btn_active=self._btn_active,
            on_btn_idle=self._btn_idle,
        )
        self._register_windows()

        # ── Mapa de botones con sus badges ────────────────────────────────────
        self._buttons_meta = self._build_buttons_meta()

        # ── WindowManager — visibilidad de botones por JSON ───────────────────
        self._wm = WindowManager(self.registry, self._menu_btns)
        self._wm.set_rerender_callback(lambda: self._switch_tab(self._active_tab))

        # ── Render inicial ────────────────────────────────────────────────────
        self._switch_tab(self._active_tab)

    # ── Registro de ventanas hijas ────────────────────────────────────────────

    def _register_windows(self):
        r    = self._wlm.register   # alias local para legibilidad
        root = self.root

        r("hardware_info",    BL.HARDWARE_INFO,
            lambda: HardwareInfoWindow(root, self.system_monitor))
        r("fan_control",      BL.FAN_CONTROL,
            lambda: FanControlWindow(root, self.fan_controller, self.system_monitor,
                                     fan_service=self.fan_service),
            badge_keys=["temp_fan"])
        r("led_window",       BL.LED_RGB,
            lambda: LedWindow(root, self.led_service))
        r("monitor_window",   BL.MONITOR_PLACA,
            lambda: MonitorWindow(root, self.system_monitor, self.hardware_monitor),
            badge_keys=["temp_monitor", "cpu", "ram"])
        r("network_window",   BL.MONITOR_RED,
            lambda: NetworkWindow(root, network_monitor=self.network_monitor))
        r("usb_window",       BL.MONITOR_USB,
            lambda: USBWindow(root))
        r("disk_window",      BL.MONITOR_DISCO,
            lambda: DiskWindow(root, self.disk_monitor),
            badge_keys=["disk"])
        r("launchers",        BL.LANZADORES,
            lambda: LaunchersWindow(root))
        r("process_window",   BL.PROCESOS,
            lambda: ProcessWindow(root, self.process_monitor))
        r("service_window",   BL.SERVICIOS,
            lambda: ServiceWindow(root, self.service_monitor),
            badge_keys=["services"])
        r("services_manager", BL.SERVICIOS_DASH,
            lambda: ServicesManagerWindow(root, registry=self.registry))
        r("crontab_window",   BL.CRONTAB,
            lambda: CrontabWindow(root))
        r("history_window",   BL.HISTORICO,
            lambda: HistoryWindow(root, self.cleanup_service))
        r("update_window",    BL.ACTUALIZACIONES,
            lambda: UpdatesWindow(root, self.update_monitor),
            badge_keys=["updates"])
        r("homebridge",       BL.HOMEBRIDGE,
            lambda: HomebridgeWindow(root, self.homebridge_monitor),
            badge_keys=["hb_offline", "hb_on", "hb_fault"])
        r("log_viewer",       BL.VISOR_LOGS,
            lambda: LogViewerWindow(root))
        r("network_local",    BL.RED_LOCAL,
            lambda: NetworkLocalWindow(root, network_scanner=self.network_scanner))
        r("pihole",           BL.PIHOLE,
            lambda: PiholeWindow(root, self.pihole_monitor),
            badge_keys=["pihole_offline"])
        r("vpn_window",       BL.VPN,
            lambda: VpnWindow(root, self.vpn_monitor),
            badge_keys=["vpn_offline"])
        r("alert_history",    BL.HISTORIAL_ALERTAS,
            lambda: AlertHistoryWindow(root, self.alert_service))
        r("display_window",   BL.BRILLO,
            lambda: DisplayWindow(root, self.display_service))
        r("overview",         BL.RESUMEN,
            lambda: OverviewWindow(root,
                system_monitor=self.system_monitor,
                service_monitor=self.service_monitor,
                pihole_monitor=self.pihole_monitor,
                network_monitor=self.network_monitor,
                disk_monitor=self.disk_monitor))
        r("camera_window",    BL.CAMARA,
            lambda: CameraWindow(root))
        r("theme_selector",   BL.TEMA,
            lambda: ThemeSelector(root))
        r("ssh_window",       BL.SSH,
            lambda: SSHWindow(root, self.ssh_monitor))
        r("wifi_window",      BL.WIFI,
            lambda: WiFiWindow(root, self.wifi_monitor))
        r("config_editor_window", BL.CONFIG,
            lambda: ConfigEditorWindow(root))
        r("button_manager",   BL.BOTONES,
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
        }

    # ── Cambio de pestaña ─────────────────────────────────────────────────────

    # Mapa inverso BL label → clave JSON, para consultar ui_enabled en _switch_tab
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
    }.items()}

    def _switch_tab(self, key):
        self._active_tab = key

        # Actualizar estilos de las pestañas
        for k, btn in self._tab_buttons.items():
            if k == key:
                btn.configure(fg_color=COLORS['primary'], text_color=COLORS['bg_dark'])
            else:
                btn.configure(fg_color=COLORS['bg_dark'], text_color=COLORS['text_dim'])

        # Destruir botones del área anterior
        for widget in self._btn_area.winfo_children():
            widget.destroy()

        # Obtener claves BL de la pestaña activa
        bl_keys = next(
            (bl for tab_key, _, _, bl in UICfg.MENU_TABS if tab_key == key), [])

        columns  = UICfg.MENU_COLUMNS
        grid_pos = 0
        for bl_key in bl_keys:
            label = getattr(BL, bl_key, None)
            if label is None:
                logger.warning(f"[MainWindow] BL.{bl_key} no existe — omitido")
                continue
            json_key = self._BL_TO_KEY.get(label)
            if json_key is not None and not self.registry.ui_enabled(json_key):
                continue
            meta = self._buttons_meta.get(label)
            if meta is None:
                logger.warning(f"[MainWindow] Sin meta para '{label}' — omitido")
                continue
            command, badge_keys = meta
            btn = make_futuristic_button(
                self._btn_area, label, command=command,
                font_size=FONT_SIZES['large'], width=30, height=15)
            btn.grid(row=grid_pos // columns, column=grid_pos % columns,
                     padx=10, pady=10, sticky="nsew")
            self._menu_btns[label] = btn
            for j, bkey in enumerate(badge_keys):
                self._create_badge(btn, bkey, offset_index=j)
            grid_pos += 1

        for c in range(columns):
            self._btn_area.grid_columnconfigure(c, weight=1)

        self._btn_area.update_idletasks()
        self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox("all"))

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
            text=f"{Icons.WARNING} ¿Qué deseas hacer?",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        ).pack(pady=(10, 10))

        selection_var = ctk.StringVar(master=selection_window, value="exit")
        options_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'])
        options_frame.pack(fill="x", pady=5, padx=20)

        exit_radio = ctk.CTkRadioButton(
            options_frame, text="  Salir de la aplicación",
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
                    text="¿Confirmar salir de la aplicación?",
                    title=" Confirmar Salida", on_confirm=do_exit, on_cancel=None)
            else:
                def do_shutdown():
                    logger.info("[MainWindow] Iniciando apagado del sistema")
                    shutdown_script = str(SCRIPTS_DIR / "apagado.sh")
                    terminal_dialog(parent=self.root, script_path=shutdown_script,
                                    title=f"{Icons.POWER_OFF}  APAGANDO SISTEMA...")
                confirm_dialog(
                    parent=self.root,
                    text=f"{Icons.WARNING} ¿Confirmar APAGAR el sistema?\n\nEsta acción apagará completamente el equipo.",
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
            text="¿Reiniciar el dashboard?\n\nSe aplicarán los cambios realizados.",
            title=f"{Icons.REINICIAR} Reiniciar Dashboard",
            on_confirm=do_restart, on_cancel=None)

    # ── Loop de actualización ─────────────────────────────────────────────────

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
        """Actualiza los badges del menú. Solo lee caches — nunca bloquea la UI."""
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
