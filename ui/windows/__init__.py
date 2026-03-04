"""
Paquete de ventanas secundarias
"""
from .fan_control import FanControlWindow
from .monitor import MonitorWindow
from .network import NetworkWindow
from .usb import USBWindow
from .launchers import LaunchersWindow
from .disk import DiskWindow
from .process_window import ProcessWindow
from .service import ServiceWindow
from .update import UpdatesWindow
from .history import HistoryWindow
from .theme_selector import ThemeSelector
from .homebridge import HomebridgeWindow
from .network_local import NetworkLocalWindow
from .pihole_window import PiholeWindow
from .alert_history import AlertHistoryWindow
from .display_window import DisplayWindow
from .vpn_window import VpnWindow
from .overview import OverviewWindow
from .led_window import LedWindow
from .camera_window import CameraWindow
from .services_manager_window import ServicesManagerWindow
from .button_manager_window import ButtonManagerWindow
from .log_viewer import LogViewerWindow
from .crontab_window import CrontabWindow
from .hardware_info_window import HardwareInfoWindow
from .ssh_window import SSHWindow

__all__ = [
    'FanControlWindow',
    'MonitorWindow',
    'NetworkWindow',
    'USBWindow',
    'LaunchersWindow',
    'DiskWindow',
    'ProcessWindow',
    'ServiceWindow',
    'UpdatesWindow',
    'HistoryWindow',
    'ThemeSelector',
    'HomebridgeWindow',
    'NetworkLocalWindow',
    'PiholeWindow',
    'AlertHistoryWindow',
    'DisplayWindow',
    'VpnWindow',
    'OverviewWindow',
    'LedWindow',
    'CameraWindow',
    'ServicesManagerWindow',
    'ButtonManagerWindow',
    'LogViewerWindow',
    'CrontabWindow',
    'HardwareInfoWindow',
    'SSHWindow',
    
]
