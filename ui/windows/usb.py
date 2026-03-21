"""
Ventana de monitoreo de dispositivos USB
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class USBWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de dispositivos USB"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self._system_utils = SystemUtils()
        self._device_widgets = []
        
        self.title("Monitor USB")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        self._create_ui()
        self._refresh_devices()
        logger.info("[USBWindow] Ventana Abierta")

    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="DISPOSITIVOS USB",
            on_close=self.destroy,
        )
        # Botón Actualizar
        refresh_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        refresh_bar.pack(fill="x", padx=10, pady=(0, 5))
        make_futuristic_button(
            refresh_bar,
            text="Actualizar",
            command=self._refresh_devices,
            width=15,
            height=5
        ).pack(side="right")
        
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        self._canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=self._canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        self._canvas.configure(yscrollcommand=scrollbar.set)
        
        self._devices_frame = ctk.CTkFrame(self._canvas, fg_color=COLORS['bg_medium'])
        self._canvas.create_window(
            (0, 0),
            window=self._devices_frame,
            anchor="nw",
            width=DSI_WIDTH-50
        )
        
        self._devices_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )
        
    
    def _refresh_devices(self):
        """Refresca la lista de dispositivos USB"""
        for widget in self._device_widgets:
            widget.destroy()
        self._device_widgets.clear()
        
        storage_devices = self._system_utils.list_usb_storage_devices()
        other_devices = self._system_utils.list_usb_other_devices()
        
        logger.debug("[USBWindow] Dispositivos detectados: %d almacenamiento, %d otros", len(storage_devices), len(other_devices))
        
        if storage_devices:
            self._create_storage_section(storage_devices)
        
        if other_devices:
            self._create_other_devices_section(other_devices)
        
        if not storage_devices and not other_devices:
            no_devices = ctk.CTkLabel(
                self._devices_frame,
                text="No se detectaron dispositivos USB",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                justify="center"
            )
            no_devices.pack(pady=50)
            self._device_widgets.append(no_devices)
    
    def _create_storage_section(self, storage_devices: list):
        """Crea la sección de almacenamiento USB"""
        title = ctk.CTkLabel(
            self._devices_frame,
            text="ALMACENAMIENTO USB",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(10, 10), padx=10)
        self._device_widgets.append(title)
        
        for idx, device in enumerate(storage_devices):
            self._create_storage_device_widget(device, idx)
    
    def _create_storage_device_widget(self, device: dict, index: int):
        """Crea widget para un dispositivo de almacenamiento"""
        device_frame = ctk.CTkFrame(
            self._devices_frame,
            fg_color=COLORS['bg_dark'],
            border_width=2,
            border_color=COLORS['success']
        )
        device_frame.pack(fill="x", pady=5, padx=10)
        self._device_widgets.append(device_frame)
        
        name = device.get('name', 'USB Disk')
        size = device.get('size', '?')
        dev_type = device.get('type', 'disk')
        
        header = ctk.CTkLabel(
            device_frame,
            text=f"{Icons.MONITOR_USB} {name} ({dev_type}) - {size}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        header.pack(anchor="w", padx=10, pady=(10, 5))
        
        dev_path = device.get('dev', '?')
        info = ctk.CTkLabel(
            device_frame,
            text=f"Dispositivo: {dev_path}",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        info.pack(anchor="w", padx=10, pady=(0, 5))
        
        eject_btn = make_futuristic_button(
            device_frame,
            text="Expulsar",
            command=lambda d=device: self._eject_device(d),
            width=15,
            height=4
        )
        eject_btn.pack(anchor="w", padx=20, pady=(5, 10))
        
        children = device.get('children', [])
        if children:
            for child in children:
                self._create_partition_widget(device_frame, child)
    
    def _create_partition_widget(self, parent, partition: dict):
        """Crea widget para una partición"""
        name = partition.get('name', '?')
        mount = partition.get('mount')
        size = partition.get('size', '?')
        
        part_text = f"  └─ Partición: {name} ({size})"
        if mount:
            part_text += f" | {Icons.FOLDER} Montado en: {mount}"
        else:
            part_text += " | No montado"
        
        part_label = ctk.CTkLabel(
            parent,
            text=part_text,
            text_color=COLORS['primary'] if mount else COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=DSI_WIDTH - 80,
            anchor="w",
            justify="left"
        )
        part_label.pack(anchor="w", padx=30, pady=2)
    
    def _create_other_devices_section(self, other_devices: list):
        """Crea la sección de otros dispositivos USB"""
        title = ctk.CTkLabel(
            self._devices_frame,
            text="OTROS DISPOSITIVOS USB",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(20, 10), padx=10)
        self._device_widgets.append(title)
        
        for idx, device_line in enumerate(other_devices):
            self._create_other_device_widget(device_line, idx)
    
    def _create_other_device_widget(self, device_line: str, index: int):
        """Crea widget para otro dispositivo USB"""
        device_info = self._parse_lsusb_line(device_line)
        
        device_frame = ctk.CTkFrame(
            self._devices_frame,
            fg_color=COLORS['bg_dark'],
            border_width=1,
            border_color=COLORS['primary']
        )
        device_frame.pack(fill="x", pady=3, padx=10)
        self._device_widgets.append(device_frame)
        
        inner = ctk.CTkFrame(device_frame, fg_color=COLORS['bg_dark'])
        inner.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            inner,
            text=f"#{index + 1}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            width=30
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            inner,
            text=device_info['bus'],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            inner,
            text=device_info['description'],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=DSI_WIDTH - 200,
            anchor="w",
            justify="left"
        ).pack(side="left", padx=5, fill="x", expand=True)
    
    def _parse_lsusb_line(self, line: str) -> dict:
        """Parsea una línea de lsusb"""
        parts = line.split()
        
        try:
            bus_idx = parts.index("Bus") + 1
            bus = f"Bus {parts[bus_idx]}"
            
            dev_idx = parts.index("Device") + 1
            device_num = parts[dev_idx].rstrip(':')
            bus += f" Dev {device_num}"
            
            id_idx = parts.index("ID") + 2
            description = " ".join(parts[id_idx:])
            
            if len(description) > 50:
                description = description[:47] + "..."
            
        except (ValueError, IndexError):
            bus = "Bus ?"
            description = line
        
        return {'bus': bus, 'description': description}
    
    def _eject_device(self, device: dict):
        """Expulsa un dispositivo USB"""
        device_name = device.get('name', 'dispositivo')
        
        logger.info("[USBWindow] Intentando expulsar: '%s' (%s)", device_name, device.get('dev', '?'))
        
        success, message = self._system_utils.eject_usb_device(device)
        
        if success:
            logger.info("[USBWindow] Expulsión exitosa: '%s'", device_name)
            custom_msgbox(
                self,
                f"{Icons.OK} {device_name}\n\n{message}\n\nAhora puedes desconectar el dispositivo de forma segura.",
                "Expulsión Exitosa"
            )
            self._refresh_devices()
        else:
            logger.error("[USBWindow] Error expulsando '%s': %s", device_name, message)
            custom_msgbox(
                self,
                f"{Icons.ERROR} Error al expulsar {device_name}:\n\n{message}",
                "Error"
            )
