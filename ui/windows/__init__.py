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
    
]
