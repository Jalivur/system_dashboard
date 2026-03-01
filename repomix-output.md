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
- Only files matching these patterns are included: main.py, core/service_registry.py
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
core/
  service_registry.py
main.py
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

## File: main.py
```python
#!/usr/bin/env python3
"""
Sistema de Monitoreo y Control
Punto de entrada principal
"""
import sys
import os
import atexit
import threading
import customtkinter as ctk
from config import DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from core import (SystemMonitor, FanController, NetworkMonitor, FanAutoService, DiskMonitor, ProcessMonitor,
                  ServiceMonitor, UpdateMonitor, CleanupService, HomebridgeMonitor, AlertService, NetworkScanner,
                  PiholeMonitor, DisplayService, VpnMonitor, LedService, HardwareMonitor, AudioAlertService)
from core.data_collection_service import DataCollectionService
from core.data_logger import DataLogger
from core.service_registry import ServiceRegistry
from ui.main_window import MainWindow
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Función principal"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("Sistema de Monitoreo")

    root.withdraw()
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.configure(bg="#111111")
    root.update_idletasks()
    root.overrideredirect(True)
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.update_idletasks()
    root.deiconify()

    # ── Instanciar servicios ──────────────────────────────────────────────────
    system_monitor    = SystemMonitor()
    fan_controller    = FanController()
    network_monitor   = NetworkMonitor()
    disk_monitor      = DiskMonitor()
    process_monitor   = ProcessMonitor()
    service_monitor   = ServiceMonitor()
    update_monitor    = UpdateMonitor()
    homebridge_monitor = HomebridgeMonitor()
    network_scanner   = NetworkScanner()
    pihole_monitor    = PiholeMonitor()
    display_service   = DisplayService()
    led_service       = LedService()
    hardware_monitor  = HardwareMonitor()
    vpn_monitor       = VpnMonitor()
    audio_alert_service = AudioAlertService(system_monitor, service_monitor)

    data_service = DataCollectionService(
        system_monitor=system_monitor,
        fan_controller=fan_controller,
        network_monitor=network_monitor,
        disk_monitor=disk_monitor,
        update_monitor=update_monitor,
        interval_minutes=5
    )

    alert_service = AlertService(
        system_monitor=system_monitor,
        service_monitor=service_monitor,
    )

    cleanup_service = CleanupService(
        data_logger=DataLogger(),
        max_csv=10,
        max_png=10,
        db_days=90,
        interval_hours=24,
    )

    fan_service = FanAutoService(fan_controller, system_monitor)

    # ── Arrancar los que requieren start() explícito ──────────────────────────
    homebridge_monitor.start()
    pihole_monitor.start()
    hardware_monitor.start()
    vpn_monitor.start()
    audio_alert_service.start()
    data_service.start()
    alert_service.start()
    cleanup_service.start()
    fan_service.start()

    # ── Registrar en el registry y aplicar configuración ─────────────────────
    registry = ServiceRegistry()
    registry.register("system_monitor",     system_monitor)
    registry.register("disk_monitor",       disk_monitor)
    registry.register("hardware_monitor",   hardware_monitor)
    registry.register("network_monitor",    network_monitor)
    registry.register("network_scanner",    network_scanner)
    registry.register("process_monitor",    process_monitor)
    registry.register("service_monitor",    service_monitor)
    registry.register("update_monitor",     update_monitor)
    registry.register("homebridge_monitor", homebridge_monitor)
    registry.register("pihole_monitor",     pihole_monitor)
    registry.register("vpn_monitor",        vpn_monitor)
    registry.register("alert_service",      alert_service)
    registry.register("audio_alert_service",audio_alert_service)
    registry.register("data_service",       data_service)
    registry.register("cleanup_service",    cleanup_service)
    registry.register("fan_service",        fan_service)
    registry.register("led_service",        led_service)
    registry.register("display_service",    display_service)

    # Para los servicios configurados como False en services.json
    registry.apply_config()

    # ── Comprobación inicial de actualizaciones en background ─────────────────
    threading.Thread(
        target=lambda: update_monitor.check_updates(force=True),
        daemon=True,
        name="UpdateCheck-Startup"
    ).start()

    # ── Cleanup centralizado ──────────────────────────────────────────────────
    def cleanup():
        fan_service.stop()
        data_service.stop()
        cleanup_service.stop()
        homebridge_monitor.stop()
        system_monitor.stop()
        service_monitor.stop()
        alert_service.stop()
        pihole_monitor.stop()
        display_service.disable_dim_on_idle()
        display_service.screen_on()
        vpn_monitor.stop()
        hardware_monitor.stop()
        audio_alert_service.stop()

    atexit.register(cleanup)

    # ── Crear interfaz ────────────────────────────────────────────────────────
    app = MainWindow(root, registry=registry, update_interval=UPDATE_MS)

    try:
        root.mainloop()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
```
