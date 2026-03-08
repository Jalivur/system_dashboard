This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: ui/main_badges.py, ui/main_update_loop.py, ui/main_window.py
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)
</notes>

</file_summary>

<directory_structure>
ui/
  main_badges.py
  main_update_loop.py
  main_window.py
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path="ui/main_badges.py">
"""
Gestor de badges del menu principal.

Los badges son indicadores visuales circulares superpuestos sobre los botones
del menu que muestran contadores (servicios caidos, actualizaciones pendientes)
o valores de temperatura/CPU/RAM/disco.

Uso en MainWindow:
    self._badge_mgr = BadgeManager(menu_btns=self._menu_btns)
    self._badge_mgr.create(btn, key="updates", offset_index=0)
    self._badge_mgr.update("updates", value=3)
    self._badge_mgr.update_temp("temp_fan", temp=72, color="#ff4444")
"""
import tkinter as tk
from config.settings import COLORS, FONT_FAMILY, Icons


class BadgeManager:
    """
    Crea y actualiza los badges de notificacion sobre los botones del menu.

    Cada badge es un Canvas circular flotante (place) anclado a la esquina
    superior derecha del boton padre. Multiples badges en un mismo boton se
    desplazan horizontalmente via offset_index.
    """

    _BADGE_SIZE = 36

    # Umbrales para badges de sistema
    TEMP_WARN = 60
    TEMP_CRIT = 70
    CPU_WARN  = 75
    CPU_CRIT  = 90
    RAM_WARN  = 75
    RAM_CRIT  = 90
    DISK_WARN = 80
    DISK_CRIT = 90

    def __init__(self, menu_btns: dict):
        """
        Args:
            menu_btns: referencia al dict {label → CTkButton} de MainWindow.
                       Se usa para recuperar el widget padre al recrear badges
                       tras un cambio de pestana.
        """
        self._menu_btns = menu_btns
        self._badges: dict = {}   # key → (canvas, oval, txt, x_offset)

    # ── Creación ──────────────────────────────────────────────────────────────

    def create(self, btn, key: str, offset_index: int = 0) -> None:
        """
        Crea un badge sobre btn y lo registra bajo key.
        Si ya existia un badge con esa key lo sobreescribe.

        Args:
            btn:          CTkButton padre
            key:          clave interna (ej. "updates", "temp_fan")
            offset_index: desplazamiento horizontal (0 = mas a la derecha)
        """
        size     = self._BADGE_SIZE
        x_offset = -6 - offset_index * (size + 4)

        canvas = tk.Canvas(
            btn, width=size, height=size,
            bg=COLORS['bg_dark'], highlightthickness=0, bd=0)
        canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)

        oval = canvas.create_oval(
            1, 1, size - 1, size - 1,
            fill=COLORS['danger'], outline="")
        txt = canvas.create_text(
            size // 2, size // 2,
            text="0", fill="white",
            font=(FONT_FAMILY, 13, "bold"))

        self._badges[key] = (canvas, oval, txt, x_offset)
        canvas.place_forget()

    # ── Actualización ─────────────────────────────────────────────────────────

    def update(self, key: str, value: int, color: str = None) -> None:
        """
        Muestra u oculta el badge segun value.

        Args:
            key:   clave del badge
            value: si > 0 muestra el badge; si == 0 lo oculta
            color: color de fondo opcional; si None usa danger o warning segun key
        """
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        if value > 0:
            display = str(value) if value < 100 else "99+"
            canvas.itemconfigure(txt, text=display)
            if color is None:
                color = (COLORS['danger']
                         if key == "services"
                         else COLORS.get('warning', '#ffaa00'))
            canvas.itemconfigure(oval, fill=color)
            txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
            canvas.itemconfigure(txt, fill=txt_color)
            canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)
        else:
            canvas.place_forget()

    def update_temp(self, key: str, temp: int, color: str) -> None:
        """
        Muestra el badge con valor de temperatura.

        Args:
            key:   clave del badge
            temp:  valor entero de temperatura
            color: color de fondo
        """
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        canvas.itemconfigure(txt, text=f"{temp}{Icons.DEGREE}")
        canvas.itemconfigure(oval, fill=color)
        txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
        canvas.itemconfigure(txt, fill=txt_color)
        canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)

    def hide(self, key: str) -> None:
        """Oculta el badge sin cambiar su valor."""
        if key not in self._badges:
            return
        canvas = self._badges[key][0]
        canvas.place_forget()

    def __contains__(self, key: str) -> bool:
        return key in self._badges
</file>

<file path="ui/main_update_loop.py">
"""
Loop de actualizacion del menu principal.

Gestiona tres ciclos independientes:
  - Reloj / uptime: cada 1 segundo via root.after
  - Badges del menu: cada update_interval ms via root.after
  - Eventos del bus: procesa eventos publicados desde threads secundarios

Ambos ciclos leen exclusivamente caches de los monitores — nunca bloquean la UI.

Uso en MainWindow:
    self._update_loop = UpdateLoop(
        root=self.root,
        badge_mgr=self._badge_mgr,
        monitors={...},
        update_interval=2000,
        clock_label=self._clock_label,
        uptime_label=self._uptime_label,
    )
    self._update_loop.start()

    # Al salir, antes de root.destroy():
    self._update_loop.stop()
"""
from datetime import datetime
from config.settings import COLORS
from core.event_bus import get_event_bus
from utils.logger import get_logger

logger = get_logger(__name__)


class UpdateLoop:
    """
    Encapsula los dos loops de actualizacion del dashboard:
    reloj/uptime y badges del menu principal.
    """

    def __init__(self, root, badge_mgr, monitors: dict,
                 update_interval: int, clock_label, uptime_label):
        """
        Args:
            root:            widget Tk raiz
            badge_mgr:       instancia de BadgeManager
            monitors:        dict con los monitores necesarios:
                             system_monitor, update_monitor, homebridge_monitor,
                             pihole_monitor, vpn_monitor, service_monitor
            update_interval: intervalo en ms para el loop de badges
            clock_label:     CTkLabel del reloj en el header
            uptime_label:    CTkLabel del uptime en el header
        """
        self._root            = root
        self._badge_mgr       = badge_mgr
        self._monitors        = monitors
        self._update_interval = update_interval
        self._clock_label     = clock_label
        self._uptime_label    = uptime_label
        self._uptime_tick     = 0
        self._running         = False
        self._clock_after_id  = None
        self._badges_after_id = None

    # ── Arranque / parada ─────────────────────────────────────────────────────

    def start(self) -> None:
        """Arranca ambos loops. Llamar una sola vez tras construir la UI."""
        self._running = True
        self._tick_clock()
        self._update_badges()

    def stop(self) -> None:
        """
        Detiene ambos loops cancelando los after() pendientes.
        Llamar antes de root.destroy() para evitar callbacks sobre
        widgets ya destruidos.
        """
        self._running = False
        if self._clock_after_id is not None:
            try:
                self._root.after_cancel(self._clock_after_id)
            except Exception:
                pass
            self._clock_after_id = None
        if self._badges_after_id is not None:
            try:
                self._root.after_cancel(self._badges_after_id)
            except Exception:
                pass
            self._badges_after_id = None
        logger.debug("[UpdateLoop] Detenido")

    # ── Loop de reloj / uptime ────────────────────────────────────────────────

    def _tick_clock(self) -> None:
        if not self._running:
            return
        self._clock_label.configure(text=datetime.now().strftime("%H:%M:%S"))
        self._uptime_tick += 1
        if self._uptime_tick == 1 or self._uptime_tick >= 60:
            self._uptime_tick = 1
            try:
                uptime_str = (self._monitors["system_monitor"]
                              .get_current_stats().get("uptime_str", "--"))
                self._uptime_label.configure(text=uptime_str)
            except Exception:
                pass
        self._clock_after_id = self._root.after(1000, self._tick_clock)

    # ── Loop de badges ────────────────────────────────────────────────────────

    def _update_badges(self) -> None:
        """Actualiza todos los badges del menu. Solo lee caches — nunca bloquea la UI."""
        if not self._running:
            return
        # Procesar eventos publicados desde threads secundarios
        get_event_bus().process_events()

        self._update_misc_badges()
        self._update_service_badge()
        self._update_system_badges()
        self._badges_after_id = self._root.after(self._update_interval, self._update_badges)

    def _update_misc_badges(self) -> None:
        bm = self._badge_mgr
        try:
            pending = (self._monitors["update_monitor"]
                       .cached_result.get('pending', 0))
            bm.update("updates", pending)
            hb = self._monitors["homebridge_monitor"]
            bm.update("hb_offline", hb.get_offline_count())
            bm.update("hb_on",      hb.get_on_count(),
                      color=COLORS.get('warning', '#ffaa00'))
            bm.update("hb_fault",   hb.get_fault_count())
            bm.update("pihole_offline",
                      self._monitors["pihole_monitor"].get_offline_count())
            bm.update("vpn_offline",
                      self._monitors["vpn_monitor"].get_offline_count())
        except Exception:
            pass

    def _update_service_badge(self) -> None:
        bm = self._badge_mgr
        try:
            stats  = self._monitors["service_monitor"].get_stats()
            failed = stats.get('failed', 0)
            bm.update("services", failed)
        except Exception:
            pass

    def _update_system_badges(self) -> None:
        bm = self._badge_mgr
        try:
            stats = self._monitors["system_monitor"].get_current_stats()

            # Temperatura
            temp = stats['temp']
            if temp >= bm.TEMP_CRIT:
                bm.update_temp("temp_fan",     int(temp), COLORS['danger'])
                bm.update_temp("temp_monitor", int(temp), COLORS['danger'])
            elif temp >= bm.TEMP_WARN:
                warn = COLORS.get('warning', '#ffaa00')
                bm.update_temp("temp_fan",     int(temp), warn)
                bm.update_temp("temp_monitor", int(temp), warn)
            else:
                bm.update("temp_fan",     0)
                bm.update("temp_monitor", 0)

            # CPU
            cpu = stats['cpu']
            if cpu >= bm.CPU_CRIT:
                bm.update("cpu", int(cpu), COLORS['danger'])
            elif cpu >= bm.CPU_WARN:
                bm.update("cpu", int(cpu), COLORS.get('warning', '#ffaa00'))
            else:
                bm.update("cpu", 0)

            # RAM
            ram = stats['ram']
            if ram >= bm.RAM_CRIT:
                bm.update("ram", int(ram), COLORS['danger'])
            elif ram >= bm.RAM_WARN:
                bm.update("ram", int(ram), COLORS.get('warning', '#ffaa00'))
            else:
                bm.update("ram", 0)

            # Disco
            disk = stats['disk_usage']
            if disk >= bm.DISK_CRIT:
                bm.update("disk", int(disk), COLORS['danger'])
            elif disk >= bm.DISK_WARN:
                bm.update("disk", int(disk), COLORS.get('warning', '#ffaa00'))
            else:
                bm.update("disk", 0)

        except Exception:
            pass
</file>

<file path="ui/main_window.py">
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
                        HardwareInfoWindow, SSHWindow, WiFiWindow, ConfigEditorWindow, AudioWindow, WeatherWindow)
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

        self._menu_btns   = {}
        self._active_tab  = UICfg.MENU_TABS[0][0]
        self._tab_buttons = {}

        logger.info(f"[MainWindow] Dashboard iniciado en {self.system_utils.get_hostname()}")

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
            lambda: WeatherWindow(root, self.weather_service))
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
            BL.CLIMA:             (lambda: self._wlm.open("weather_window"),       []),
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
</file>

</files>
