#!/usr/bin/env python3
"""
Sistema de Monitoreo y Control
Punto de entrada principal
"""
import sys
import os
import threading
import customtkinter as ctk
from config import DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from core import (SystemMonitor, FanController, NetworkMonitor, FanAutoService, DiskMonitor, ProcessMonitor,
                  ServiceMonitor, UpdateMonitor, CleanupService, HomebridgeMonitor, AlertService, NetworkScanner,
                  PiholeMonitor, DisplayService, VpnMonitor, LedService, HardwareMonitor, AudioAlertService,
                  SSHMonitor, WiFiMonitor, AudioService, WeatherService)
from core.data_collection_service import DataCollectionService
from core.data_logger import DataLogger
from core.service_registry import ServiceRegistry
from ui.main_window import MainWindow
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Filtro de excepciones ignoradas ──────────────────────────────────────────
# Suprime el traceback de Variable.__del__ que aparece al salir cuando el GC
# recoge StringVar/IntVar de CTkRadioButton tras root.destroy(). Es un bug
# conocido de CustomTkinter — cosmético, no afecta al comportamiento.
# "Exception ignored in:" no pasa por sys.stderr — requiere sys.unraisablehook.

def _unraisable_filter(unraisable):
    """Filtra RuntimeError de Variable.__del__ — deja pasar todo lo demás."""
    if (unraisable.exc_type is RuntimeError
            and "main thread is not in main loop" in str(unraisable.exc_value)
            and unraisable.object is not None
            and getattr(unraisable.object, "__qualname__", "") == "Variable.__del__"):
        return
    sys.__unraisablehook__(unraisable)

sys.unraisablehook = _unraisable_filter

# ─────────────────────────────────────────────────────────────────────────────


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
    system_monitor      = SystemMonitor()
    fan_controller      = FanController()
    network_monitor     = NetworkMonitor()
    disk_monitor        = DiskMonitor()
    process_monitor     = ProcessMonitor()
    service_monitor     = ServiceMonitor()
    update_monitor      = UpdateMonitor()
    homebridge_monitor  = HomebridgeMonitor()
    network_scanner     = NetworkScanner()
    pihole_monitor      = PiholeMonitor()
    display_service     = DisplayService()
    led_service         = LedService()
    hardware_monitor    = HardwareMonitor()
    vpn_monitor         = VpnMonitor()
    audio_alert_service = AudioAlertService(system_monitor, service_monitor)
    ssh_monitor         = SSHMonitor()
    wifi_monitor        = WiFiMonitor()
    audio_service       = AudioService()
    weather_service     = WeatherService()

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
    ssh_monitor.start()
    wifi_monitor.start()
    weather_service.start()

    # ── Registrar en el registry y aplicar configuración ─────────────────────
    registry = ServiceRegistry()
    registry.register("fan_controller",       fan_controller)
    registry.register("system_monitor",       system_monitor)
    registry.register("disk_monitor",         disk_monitor)
    registry.register("hardware_monitor",     hardware_monitor)
    registry.register("network_monitor",      network_monitor)
    registry.register("network_scanner",      network_scanner)
    registry.register("process_monitor",      process_monitor)
    registry.register("service_monitor",      service_monitor)
    registry.register("update_monitor",       update_monitor)
    registry.register("homebridge_monitor",   homebridge_monitor)
    registry.register("pihole_monitor",       pihole_monitor)
    registry.register("vpn_monitor",          vpn_monitor)
    registry.register("alert_service",        alert_service)
    registry.register("audio_alert_service",  audio_alert_service)
    registry.register("data_service",         data_service)
    registry.register("cleanup_service",      cleanup_service)
    registry.register("fan_service",          fan_service)
    registry.register("led_service",          led_service)
    registry.register("display_service",      display_service)
    registry.register("ssh_monitor",          ssh_monitor)
    registry.register("wifi_monitor",         wifi_monitor)
    registry.register("audio_service",        audio_service)
    registry.register("weather_service",      weather_service)
    # Para los servicios configurados como False en services.json
    registry.apply_config()

    # ── Comprobación inicial de actualizaciones en background ─────────────────
    threading.Thread(
        target=lambda: update_monitor.check_updates(force=True),
        daemon=True,
        name="UpdateCheck-Startup"
    ).start()

    # ── Cleanup centralizado ──────────────────────────────────────────────────
    _cleaned = False

    def cleanup():
        nonlocal _cleaned
        if _cleaned:
            return
        _cleaned = True

        # 1. Destruir la ventana primero — libera todos los StringVar/Tkinter
        #    desde el hilo principal antes de que los threads de fondo hagan GC
        try:
            root.destroy()
        except Exception:
            pass

        # 2. Parar los servicios de fondo
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
        wifi_monitor.stop()
        weather_service.stop()

    # ── Crear interfaz ────────────────────────────────────────────────────────
    app = MainWindow(root, registry=registry, update_interval=UPDATE_MS)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()
