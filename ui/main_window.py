"""
Ventana principal del sistema de monitoreo
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_X, DSI_Y, SCRIPTS_DIR
from ui.styles import StyleManager, make_futuristic_button
from ui.windows import (FanControlWindow, MonitorWindow, NetworkWindow, USBWindow, ProcessWindow, ServiceWindow, 
                        HistoryWindow, LaunchersWindow, ThemeSelector, DiskWindow, UpdatesWindow, HomebridgeWindow, 
                        NetworkLocalWindow)
from ui.windows.log_viewer import LogViewerWindow
from ui.widgets import confirm_dialog, terminal_dialog
from utils.system_utils import SystemUtils
from utils.logger import get_logger
import sys
import os
from datetime import datetime
import psutil  # uptime badge
logger = get_logger(__name__)


class MainWindow:
    """Ventana principal del dashboard"""
    
    def __init__(self, root, system_monitor, fan_controller, network_monitor,
                 disk_monitor, process_monitor, service_monitor, update_monitor, cleanup_service, homebridge_monitor, network_scanner,
                 update_interval=2000):
        self.root = root
        self.system_monitor = system_monitor
        self.fan_controller = fan_controller
        self.network_monitor = network_monitor
        self.disk_monitor = disk_monitor
        self.process_monitor = process_monitor
        self.service_monitor = service_monitor
        self.update_monitor = update_monitor
        self.cleanup_service = cleanup_service
        self.homebridge_monitor = homebridge_monitor
        self.network_scanner = network_scanner
        
        self.update_interval = update_interval
        self.system_utils = SystemUtils()
        
        # Referencias a badges (canvas item ids)
        self._badges = {}  # key -> (canvas, oval_id, text_id)

        # Referencias a botones del menú para feedback visual
        self._menu_btns = {}  # label_key -> CTkButton

        # Referencias a ventanas secundarias
        self.fan_window = None
        self.monitor_window = None
        self.network_window = None
        self.usb_window = None
        self.launchers_window = None
        self.disk_window = None
        self.process_window = None
        self.service_window = None
        self.history_window = None
        self.update_window = None
        self.theme_window = None
        self.homebridge_window = None
        self.log_viewer_window = None
        self.network_local_window = None

        self._uptime_tick = 0  # uptime badge: contador para actualizar cada ~60s

        logger.info(f"[MainWindow] Dashboard iniciado en {self.system_utils.get_hostname()}")

        self._create_ui()
        self._start_update_loop()
    
    def _create_ui(self):
        """Crea la interfaz principal"""
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Barra de cabecera: hostname (izq) + título (centro) + reloj (der) ──
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

        self._uptime_label = ctk.CTkLabel(  # uptime badge
            header_bar,
            text="⏱ --",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            anchor="e",
        )
        self._uptime_label.pack(side="right", padx=(0, 4))  # izq del reloj

        self._clock_label = ctk.CTkLabel(
            header_bar,
            text="00:00:00",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="e",
        )
        self._clock_label.pack(side="right", padx=12)

        # Separador
        ctk.CTkFrame(main_frame, fg_color=COLORS['border'], height=1, corner_radius=0).pack(fill="x", padx=5, pady=(0, 4))
        
        menu_container = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'])
        menu_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.menu_canvas = ctk.CTkCanvas(
            menu_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        self.menu_canvas.pack(side="left", fill="both", expand=True)
        
        menu_scrollbar = ctk.CTkScrollbar(
            menu_container,
            orientation="vertical",
            command=self.menu_canvas.yview,
            width=30
        )
        menu_scrollbar.pack(side="right", fill="y")
        

        StyleManager.style_scrollbar_ctk(menu_scrollbar)
        
        self.menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
        
        self.menu_inner = ctk.CTkFrame(self.menu_canvas, fg_color=COLORS['bg_medium'])
        self.menu_canvas.create_window(
            (0, 0),
            window=self.menu_inner,
            anchor="nw",
            width=DSI_WIDTH - 50
        )
        
        self.menu_inner.bind(
            "<Configure>",
            lambda e: self.menu_canvas.configure(
                scrollregion=self.menu_canvas.bbox("all")
            )
        )
        
        self._create_menu_buttons()
    
    def _create_menu_buttons(self):
        """Crea los botones del menú principal"""
        buttons_config = [
            ("󰈐  Control Ventiladores", self.open_fan_control,     ["temp_fan"]),
            ("󰚗  Monitor Placa",         self.open_monitor_window,  ["temp_monitor", "cpu", "ram"]),
            ("  Monitor Red",               self.open_network_window,  []),
            ("󱇰 Monitor USB",            self.open_usb_window,      []),
            ("  Monitor Disco",             self.open_disk_window,     ["disk"]),
            ("󱓞  Lanzadores",            self.open_launchers,       []),
            ("⚙️ Monitor Procesos",     self.open_process_window,  []),
            ("⚙️ Monitor Servicios",    self.open_service_window,  ["services"]),
            ("󱘿  Histórico Datos",       self.open_history_window,  []),
            ("󰆧  Actualizaciones",       self.open_update_window,   ["updates"]),
            ("󰟐  Homebridge",        self.open_homebridge,     ["hb_offline", "hb_on", "hb_fault"]),
            ("󰷐  Visor de Logs",        self.open_log_viewer,      []),
            ("🖧  Red Local",   self.open_network_local,   []),
            ("󰔎  Cambiar Tema",          self.open_theme_selector,  []),
            ("  Reiniciar",                 self.restart_application,  []),
            ("󰿅  Salir",                 self.exit_application,     []),
        ]
        
        columns = 2
        
        for i, (text, command, badge_keys) in enumerate(buttons_config):
            row = i // columns
            col = i % columns
            
            btn = make_futuristic_button(
                self.menu_inner,
                text,
                command=command,
                font_size=FONT_SIZES['large'],
                width=30,
                height=15
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Guardar referencia para feedback visual
            self._menu_btns[text] = btn

            # Múltiples badges por botón, colocados de derecha a izquierda
            for j, key in enumerate(badge_keys):
                self._create_badge(btn, key, offset_index=j)
        
        for c in range(columns):
            self.menu_inner.grid_columnconfigure(c, weight=1)

    # ── Badges ────────────────────────────────────────────────────────────────

    # ── Feedback visual de botones ───────────────────────────────────────────

    def _btn_active(self, text_key):
        """Oscurece el botón mientras su ventana está abierta"""
        btn = self._menu_btns.get(text_key)
        if btn:
            try:
                btn.configure(fg_color=COLORS['bg_light'], border_color=COLORS['primary'], border_width=2)
            except Exception:
                pass

    def _btn_idle(self, text_key):
        """Restaura el botón a su estado normal"""
        btn = self._menu_btns.get(text_key)
        if btn:
            try:
                btn.configure(fg_color=COLORS['bg_dark'], border_color=COLORS['border'], border_width=1)
            except Exception:
                pass

    def _create_badge(self, btn, key, offset_index=0):
        """Crea un badge circular en la esquina superior-derecha del botón.
        offset_index separa horizontalmente múltiples badges en el mismo botón."""
        BADGE_SIZE = 36
        x_offset = -6 - offset_index * (BADGE_SIZE + 4)
        badge_canvas = tk.Canvas(
            btn,
            width=BADGE_SIZE,
            height=BADGE_SIZE,
            bg=COLORS['bg_dark'],
            highlightthickness=0,
            bd=0
        )
        badge_canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)

        oval = badge_canvas.create_oval(
            1, 1, BADGE_SIZE - 1, BADGE_SIZE - 1,
            fill=COLORS['danger'],
            outline=""
        )
        txt = badge_canvas.create_text(
            BADGE_SIZE // 2, BADGE_SIZE // 2,
            text="0",
            fill="white",
            font=(FONT_FAMILY, 13, "bold")
        )

        self._badges[key] = (badge_canvas, oval, txt, x_offset)
        badge_canvas.place_forget()

    # Umbrales de temperatura
    _TEMP_WARN = 60   # °C — badge naranja
    _TEMP_CRIT = 70   # °C — badge rojo

    # Umbrales CPU / RAM (%)
    _CPU_WARN  = 75
    _CPU_CRIT  = 90
    _RAM_WARN  = 75
    _RAM_CRIT  = 90

    # Umbrales disco (%)
    _DISK_WARN = 80
    _DISK_CRIT = 90

    def _update_badge(self, key, value, color=None):
        """Actualiza el valor y visibilidad de un badge."""
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
    
    # ── Apertura de ventanas ──────────────────────────────────────────────────

    def open_fan_control(self):
        """Abre la ventana de control de ventiladores"""
        if self.fan_window is None or not self.fan_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Control Ventiladores")
            self._btn_active("󰈐  Control Ventiladores")
            self.fan_window = FanControlWindow(self.root, self.fan_controller, self.system_monitor)
            self.fan_window.bind("<Destroy>", lambda e: self._btn_idle("󰈐  Control Ventiladores"))
        else:
            self.fan_window.lift()
    
    def open_monitor_window(self):
        """Abre la ventana de monitoreo del sistema"""
        if self.monitor_window is None or not self.monitor_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Placa")
            self._btn_active("󰚗  Monitor Placa")
            self.monitor_window = MonitorWindow(self.root, self.system_monitor)
            self.monitor_window.bind("<Destroy>", lambda e: self._btn_idle("󰚗  Monitor Placa"))
        else:
            self.monitor_window.lift()
    
    def open_network_window(self):
        """Abre la ventana de monitoreo de red"""
        if self.network_window is None or not self.network_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Red")
            self._btn_active("  Monitor Red")
            self.network_window = NetworkWindow(self.root, self.network_monitor)
            self.network_window.bind("<Destroy>", lambda e: self._btn_idle("  Monitor Red"))
        else:
            self.network_window.lift()
    
    def open_usb_window(self):
        """Abre la ventana de monitoreo USB"""
        if self.usb_window is None or not self.usb_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor USB")
            self._btn_active("󱇰 Monitor USB")
            self.usb_window = USBWindow(self.root)
            self.usb_window.bind("<Destroy>", lambda e: self._btn_idle("󱇰 Monitor USB"))
        else:
            self.usb_window.lift()
    
    def open_process_window(self):
        """Abre el monitor de procesos"""
        if self.process_window is None or not self.process_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Procesos")
            self._btn_active("⚙️ Monitor Procesos")
            self.process_window = ProcessWindow(self.root, self.process_monitor)
            self.process_window.bind("<Destroy>", lambda e: self._btn_idle("⚙️ Monitor Procesos"))
        else:
            self.process_window.lift()
    
    def open_service_window(self):
        """Abre el monitor de servicios"""
        if self.service_window is None or not self.service_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Servicios")
            self._btn_active("⚙️ Monitor Servicios")
            self.service_window = ServiceWindow(self.root, self.service_monitor)
            self.service_window.bind("<Destroy>", lambda e: self._btn_idle("⚙️ Monitor Servicios"))
        else:
            self.service_window.lift()
    
    def open_history_window(self):
        """Abre la ventana de histórico"""
        if self.history_window is None or not self.history_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Histórico Datos")
            self._btn_active("󱘿  Histórico Datos")
            self.history_window = HistoryWindow(self.root, self.cleanup_service)
            self.history_window.bind("<Destroy>", lambda e: self._btn_idle("󱘿  Histórico Datos"))
        else:
            self.history_window.lift()
    
    def open_launchers(self):
        """Abre la ventana de lanzadores"""
        if self.launchers_window is None or not self.launchers_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Lanzadores")
            self._btn_active("󱓞  Lanzadores")
            self.launchers_window = LaunchersWindow(self.root)
            self.launchers_window.bind("<Destroy>", lambda e: self._btn_idle("󱓞  Lanzadores"))
        else:
            self.launchers_window.lift()
    
    def open_theme_selector(self):
        """Abre el selector de temas"""
        if self.theme_window is None or not self.theme_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Cambiar Tema")
            self._btn_active("󰔎  Cambiar Tema")
            self.theme_window = ThemeSelector(self.root)
            self.theme_window.bind("<Destroy>", lambda e: self._btn_idle("󰔎  Cambiar Tema"))
        else:
            self.theme_window.lift()
    
    def open_disk_window(self):
        """Abre la ventana de monitor de disco"""
        if self.disk_window is None or not self.disk_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Disco")
            self._btn_active("  Monitor Disco")
            self.disk_window = DiskWindow(self.root, self.disk_monitor)
            self.disk_window.bind("<Destroy>", lambda e: self._btn_idle("  Monitor Disco"))
        else:
            self.disk_window.lift()
    
    def open_update_window(self):
        """Abre la ventana de actualizaciones"""
        if self.update_window is None or not self.update_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Actualizaciones")
            self._btn_active("󰆧  Actualizaciones")
            self.update_window = UpdatesWindow(self.root, self.update_monitor)
            self.update_window.bind("<Destroy>", lambda e: self._btn_idle("󰆧  Actualizaciones"))
        else:
            self.update_window.lift()
    
    def open_homebridge(self):
        """Abre la ventana de control de Homebridge"""
        if self.homebridge_window is None or not self.homebridge_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Homebridge")
            self.homebridge_window = HomebridgeWindow(self.root, self.homebridge_monitor)
        else:
            self.homebridge_window.lift()

    def open_log_viewer(self):
        """Abre el visor de logs del dashboard"""
        if self.log_viewer_window is None or not self.log_viewer_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Visor de Logs")
            self._btn_active("󰷐  Visor de Logs")
            self.log_viewer_window = LogViewerWindow(self.root)
            self.log_viewer_window.bind("<Destroy>", lambda e: self._btn_idle("󰷐  Visor de Logs"))
        else:
            self.log_viewer_window.lift()
    
    def open_network_local(self):
        """Abre el panel de red local."""
        if self.network_local_window is None or not self.network_local_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Red Local")
            self._btn_active("🖧  Red Local")
            self.network_local_window = NetworkLocalWindow(self.root)
            self.network_local_window.bind(
                "<Destroy>", lambda e: self._btn_idle("🖧  Red Local"))
        else:
            self.network_local_window.lift()

    
    # ── Salir / Reiniciar ─────────────────────────────────────────────────────

    def exit_application(self):
        """Cierra la aplicación con opciones de salida o apagado"""
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
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="⚠️ ¿Qué deseas hacer?",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title_label.pack(pady=(10, 10))
        
        selection_var = ctk.StringVar(value="exit")
        
        options_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'])
        options_frame.pack(fill="x", pady=5, padx=20)
        
        exit_radio = ctk.CTkRadioButton(
            options_frame,
            text="  Salir de la aplicación",
            variable=selection_var,
            value="exit",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium']),
        )
        exit_radio.pack(anchor="w", padx=20, pady=12)
        
        shutdown_radio = ctk.CTkRadioButton(
            options_frame,
            text="󰐥  Apagar el sistema",
            variable=selection_var,
            value="shutdown",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        shutdown_radio.pack(anchor="w", padx=20, pady=12)
        

        StyleManager.style_radiobutton_ctk(exit_radio, radiobutton_width=30, radiobutton_height=30)
        StyleManager.style_radiobutton_ctk(shutdown_radio, radiobutton_width=30, radiobutton_height=30)
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(side="bottom", fill="x", pady=(5, 10))
        
        def on_confirm():
            selected = selection_var.get()
            selection_window.destroy()
            
            if selected == "exit":
                def do_exit():
                    logger.info("[MainWindow] Cerrando dashboard por solicitud del usuario")
                    self.root.quit()
                    self.root.destroy()
                
                confirm_dialog(
                    parent=self.root,
                    text="¿Confirmar salir de la aplicación?",
                    title=" Confirmar Salida",
                    on_confirm=do_exit,
                    on_cancel=None
                )
            
            else:  # shutdown
                def do_shutdown():
                    logger.info("[MainWindow] Iniciando apagado del sistema")
                    shutdown_script = str(SCRIPTS_DIR / "apagado.sh")
                    terminal_dialog(
                        parent=self.root,
                        script_path=shutdown_script,
                        title="󰐥  APAGANDO SISTEMA..."
                    )
                
                confirm_dialog(
                    parent=self.root,
                    text="⚠️ ¿Confirmar APAGAR el sistema?\n\nEsta acción apagará completamente el equipo.",
                    title=" Confirmar Apagado",
                    on_confirm=do_shutdown,
                    on_cancel=None
                )
        
        def on_cancel():
            logger.debug("[MainWindow] Diálogo de salida cancelado")
            selection_window.destroy()
        
        cancel_btn = make_futuristic_button(
            buttons_frame,
            text="Cancelar",
            command=on_cancel,
            width=20,
            height=10
        )
        cancel_btn.pack(side="right", padx=5)
        
        confirm_btn = make_futuristic_button(
            buttons_frame,
            text="Continuar",
            command=on_confirm,
            width=15,
            height=8
        )
        confirm_btn.pack(side="right", padx=5)
        
        selection_window.bind("<Escape>", lambda e: on_cancel())
    
    def restart_application(self):
        """Reinicia la aplicación"""
        def do_restart():

            logger.info("[MainWindow] Reiniciando dashboard")
            self.root.quit()
            self.root.destroy()
            os.execv(sys.executable, [sys.executable, os.path.abspath(sys.argv[0])] + sys.argv[1:])
        
        confirm_dialog(
            parent=self.root,
            text="¿Reiniciar el dashboard?\n\nSe aplicarán los cambios realizados.",
            title=" Reiniciar Dashboard",
            on_confirm=do_restart,
            on_cancel=None
        )
    
    # ── Loop de actualización ─────────────────────────────────────────────────

    def _tick_clock(self):
        """Actualiza el reloj cada segundo y el uptime cada minuto."""
        self._clock_label.configure(text=datetime.now().strftime("%H:%M:%S"))

        # Uptime badge: recalcular cada 60 ticks (~60s) y en el primero
        self._uptime_tick += 1
        if self._uptime_tick == 1 or self._uptime_tick >= 60:
            self._uptime_tick = 1
            try:
                import time as _time
                uptime_s = _time.time() - psutil.boot_time()
                days    = int(uptime_s // 86400)
                hours   = int((uptime_s % 86400) // 3600)
                minutes = int((uptime_s % 3600) // 60)
                uptime_str = f"⏱ {days}d {hours}h" if days > 0 else f"⏱ {hours}h {minutes}m"
                self._uptime_label.configure(text=uptime_str)
            except Exception:
                pass

        self.root.after(1000, self._tick_clock)

    def _start_update_loop(self):
        """Inicia el bucle de actualización"""
        self._tick_clock()
        self._update()
    
    def _update(self):
        """Actualiza los badges del menú. Solo lee cachés — nunca bloquea la UI."""
        try:
            pending = self.update_monitor.cached_result.get('pending', 0)
            self._update_badge("updates", pending)

            # Homebridge — lectura desde memoria, sin HTTP
            self._update_badge("hb_offline", self.homebridge_monitor.get_offline_count())
            self._update_badge(
                "hb_on",
                self.homebridge_monitor.get_on_count(),
                color=COLORS.get('warning', '#ffaa00'),
            )
            self._update_badge("hb_fault", self.homebridge_monitor.get_fault_count())

        except Exception:
            pass

        try:
            # get_stats() ahora es lectura de caché — no lanza systemctl
            stats  = self.service_monitor.get_stats()
            failed = stats.get('failed', 0)
            self._update_badge("services", failed)
        except Exception:
            pass

        try:
            # get_current_stats() ahora es lectura de caché — no llama psutil
            sys_stats = self.system_monitor.get_current_stats()

            # Temperatura
            temp = sys_stats['temp']
            if temp >= self._TEMP_CRIT:
                temp_color = COLORS['danger']
                show_temp  = True
            elif temp >= self._TEMP_WARN:
                temp_color = COLORS.get('warning', '#ffaa00')
                show_temp  = True
            else:
                show_temp = False

            if show_temp:
                self._update_badge_temp("temp_fan",     int(temp), temp_color)
                self._update_badge_temp("temp_monitor", int(temp), temp_color)
            else:
                self._update_badge("temp_fan",     0)
                self._update_badge("temp_monitor", 0)

            # CPU
            cpu = sys_stats['cpu']
            if cpu >= self._CPU_CRIT:
                self._update_badge("cpu", int(cpu), COLORS['danger'])
            elif cpu >= self._CPU_WARN:
                self._update_badge("cpu", int(cpu), COLORS.get('warning', '#ffaa00'))
            else:
                self._update_badge("cpu", 0)

            # RAM
            ram = sys_stats['ram']
            if ram >= self._RAM_CRIT:
                self._update_badge("ram", int(ram), COLORS['danger'])
            elif ram >= self._RAM_WARN:
                self._update_badge("ram", int(ram), COLORS.get('warning', '#ffaa00'))
            else:
                self._update_badge("ram", 0)

            # Disco
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


    def _update_badge_temp(self, key, temp, color):
        """Muestra la temperatura en el badge con el color indicado."""
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        canvas.itemconfigure(txt, text=f"{temp}°")
        canvas.itemconfigure(oval, fill=color)
        txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
        canvas.itemconfigure(txt, fill=txt_color)
        canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)