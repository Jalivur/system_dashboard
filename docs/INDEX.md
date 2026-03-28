# Dashboard RPi — Documentación de código

> Generado automáticamente el 2026-03-28 12:27

> Script: `generate_docs.py` · Parseo estático via `ast` — sin ejecución del código

> **89 módulos** · **79 clases** · **884 métodos** · **80 funciones** · Cobertura global: **🟢 100%**


---

## Core — Servicios y monitores

| Módulo | Clases | Métodos | Funciones | Cobertura |
|--------|--------|---------|-----------|-----------|
| [`core.__init__`](core/core___init__.md) | 0 | 0 | 0 | N/A |
| [`core.alert_service`](core/core_alert_service.md) | 1 | 14 | 1 | 🟢 100% |
| [`core.audio_alert_service`](core/core_audio_alert_service.md) | 2 | 11 | 1 | 🟢 100% |
| [`core.audio_service`](core/core_audio_service.md) | 1 | 8 | 0 | 🟢 100% |
| [`core.camera_service`](core/core_camera_service.md) | 0 | 0 | 16 | 🟢 100% |
| [`core.cleanup_service`](core/core_cleanup_service.md) | 1 | 14 | 0 | 🟢 100% |
| [`core.crontab_service`](core/core_crontab_service.md) | 0 | 0 | 6 | 🟢 100% |
| [`core.data_analyzer`](core/core_data_analyzer.md) | 1 | 14 | 1 | 🟢 100% |
| [`core.data_collection_service`](core/core_data_collection_service.md) | 1 | 8 | 0 | 🟢 100% |
| [`core.data_logger`](core/core_data_logger.md) | 1 | 8 | 0 | 🟢 100% |
| [`core.disk_monitor`](core/core_disk_monitor.md) | 1 | 11 | 0 | 🟢 100% |
| [`core.display_service`](core/core_display_service.md) | 1 | 22 | 2 | 🟢 100% |
| [`core.event_bus`](core/core_event_bus.md) | 1 | 8 | 1 | 🟢 100% |
| [`core.fan_auto_service`](core/core_fan_auto_service.md) | 1 | 9 | 0 | 🟢 100% |
| [`core.fan_controller`](core/core_fan_controller.md) | 1 | 9 | 0 | 🟢 100% |
| [`core.gpio_monitor`](core/core_gpio_monitor.md) | 1 | 25 | 2 | 🟢 100% |
| [`core.hardware_monitor`](core/core_hardware_monitor.md) | 1 | 8 | 0 | 🟢 100% |
| [`core.homebridge_monitor`](core/core_homebridge_monitor.md) | 1 | 17 | 1 | 🟢 100% |
| [`core.i2c_monitor`](core/core_i2c_monitor.md) | 1 | 8 | 0 | 🟢 100% |
| [`core.led_service`](core/core_led_service.md) | 1 | 9 | 0 | 🟢 100% |
| [`core.network_monitor`](core/core_network_monitor.md) | 1 | 13 | 0 | 🟢 100% |
| [`core.network_scanner`](core/core_network_scanner.md) | 1 | 12 | 0 | 🟢 100% |
| [`core.pihole_monitor`](core/core_pihole_monitor.md) | 1 | 15 | 1 | 🟢 100% |
| [`core.process_monitor`](core/core_process_monitor.md) | 1 | 16 | 0 | 🟢 100% |
| [`core.service_monitor`](core/core_service_monitor.md) | 1 | 24 | 0 | 🟢 100% |
| [`core.service_registry`](core/core_service_registry.md) | 1 | 10 | 0 | 🟢 100% |
| [`core.service_watchdog`](core/core_service_watchdog.md) | 1 | 14 | 0 | 🟢 100% |
| [`core.ssh_monitor`](core/core_ssh_monitor.md) | 1 | 10 | 3 | 🟢 100% |
| [`core.system_monitor`](core/core_system_monitor.md) | 1 | 10 | 0 | 🟢 100% |
| [`core.update_monitor`](core/core_update_monitor.md) | 1 | 5 | 0 | 🟢 100% |
| [`core.vpn_monitor`](core/core_vpn_monitor.md) | 1 | 12 | 0 | 🟢 100% |
| [`core.weather_service`](core/core_weather_service.md) | 1 | 19 | 1 | 🟢 100% |
| [`core.wifi_monitor`](core/core_wifi_monitor.md) | 1 | 17 | 3 | 🟢 100% |

## UI — Módulos principales

| Módulo | Clases | Métodos | Funciones | Cobertura |
|--------|--------|---------|-----------|-----------|
| [`ui.__init__`](ui_main/ui___init__.md) | 0 | 0 | 0 | N/A |
| [`ui.main_badges`](ui_main/ui_main_badges.md) | 1 | 6 | 0 | 🟢 100% |
| [`ui.main_system_actions`](ui_main/ui_main_system_actions.md) | 0 | 0 | 2 | 🟢 100% |
| [`ui.main_update_loop`](ui_main/ui_main_update_loop.md) | 1 | 10 | 0 | 🟢 100% |
| [`ui.main_window`](ui_main/ui_main_window.md) | 1 | 7 | 0 | 🟢 100% |
| [`ui.styles`](ui_main/ui_styles.md) | 1 | 8 | 3 | 🟢 100% |
| [`ui.widgets.__init__`](ui_main/ui_widgets___init__.md) | 0 | 0 | 0 | N/A |
| [`ui.widgets.dialogs`](ui_main/ui_widgets_dialogs.md) | 0 | 0 | 3 | 🟢 100% |
| [`ui.widgets.graphs`](ui_main/ui_widgets_graphs.md) | 1 | 6 | 2 | 🟢 100% |
| [`ui.window_lifecycle`](ui_main/ui_window_lifecycle.md) | 1 | 6 | 0 | 🟢 100% |
| [`ui.window_manager`](ui_main/ui_window_manager.md) | 1 | 7 | 0 | 🟢 100% |

## UI — Ventanas

| Módulo | Clases | Métodos | Funciones | Cobertura |
|--------|--------|---------|-----------|-----------|
| [`ui.windows.__init__`](ui_windows/ui_windows___init__.md) | 0 | 0 | 0 | N/A |
| [`ui.windows.alert_history`](ui_windows/ui_windows_alert_history.md) | 1 | 6 | 0 | 🟢 100% |
| [`ui.windows.audio_window`](ui_windows/ui_windows_audio_window.md) | 1 | 18 | 0 | 🟢 100% |
| [`ui.windows.button_manager_window`](ui_windows/ui_windows_button_manager_window.md) | 1 | 7 | 0 | 🟢 100% |
| [`ui.windows.camera_window`](ui_windows/ui_windows_camera_window.md) | 1 | 23 | 0 | 🟢 100% |
| [`ui.windows.config_editor_window`](ui_windows/ui_windows_config_editor_window.md) | 1 | 13 | 5 | 🟢 100% |
| [`ui.windows.crontab_window`](ui_windows/ui_windows_crontab_window.md) | 1 | 14 | 0 | 🟢 100% |
| [`ui.windows.disk`](ui_windows/ui_windows_disk.md) | 1 | 12 | 0 | 🟢 100% |
| [`ui.windows.display_window`](ui_windows/ui_windows_display_window.md) | 1 | 10 | 0 | 🟢 100% |
| [`ui.windows.fan_control`](ui_windows/ui_windows_fan_control.md) | 1 | 16 | 0 | 🟢 100% |
| [`ui.windows.gpio_window`](ui_windows/ui_windows_gpio_window.md) | 2 | 26 | 0 | 🟢 100% |
| [`ui.windows.hardware_info_window`](ui_windows/ui_windows_hardware_info_window.md) | 1 | 8 | 4 | 🟢 100% |
| [`ui.windows.history`](ui_windows/ui_windows_history.md) | 1 | 22 | 0 | 🟢 100% |
| [`ui.windows.homebridge`](ui_windows/ui_windows_homebridge.md) | 1 | 14 | 0 | 🟢 100% |
| [`ui.windows.i2c_window`](ui_windows/ui_windows_i2c_window.md) | 1 | 10 | 0 | 🟢 100% |
| [`ui.windows.launchers`](ui_windows/ui_windows_launchers.md) | 1 | 4 | 0 | 🟢 100% |
| [`ui.windows.led_window`](ui_windows/ui_windows_led_window.md) | 1 | 12 | 0 | 🟢 100% |
| [`ui.windows.log_config_window`](ui_windows/ui_windows_log_config_window.md) | 1 | 13 | 1 | 🟢 100% |
| [`ui.windows.log_viewer`](ui_windows/ui_windows_log_viewer.md) | 1 | 18 | 0 | 🟢 100% |
| [`ui.windows.monitor`](ui_windows/ui_windows_monitor.md) | 1 | 5 | 0 | 🟢 100% |
| [`ui.windows.network`](ui_windows/ui_windows_network.md) | 1 | 10 | 0 | 🟢 100% |
| [`ui.windows.network_local`](ui_windows/ui_windows_network_local.md) | 1 | 7 | 0 | 🟢 100% |
| [`ui.windows.overview`](ui_windows/ui_windows_overview.md) | 1 | 9 | 0 | 🟢 100% |
| [`ui.windows.pihole_window`](ui_windows/ui_windows_pihole_window.md) | 1 | 6 | 0 | 🟢 100% |
| [`ui.windows.process_window`](ui_windows/ui_windows_process_window.md) | 1 | 14 | 0 | 🟢 100% |
| [`ui.windows.service`](ui_windows/ui_windows_service.md) | 1 | 19 | 0 | 🟢 100% |
| [`ui.windows.service_watchdog`](ui_windows/ui_windows_service_watchdog.md) | 1 | 20 | 0 | 🟢 100% |
| [`ui.windows.services_manager_window`](ui_windows/ui_windows_services_manager_window.md) | 1 | 11 | 0 | 🟢 100% |
| [`ui.windows.ssh_window`](ui_windows/ui_windows_ssh_window.md) | 1 | 9 | 4 | 🟢 100% |
| [`ui.windows.theme_selector`](ui_windows/ui_windows_theme_selector.md) | 1 | 6 | 0 | 🟢 100% |
| [`ui.windows.update`](ui_windows/ui_windows_update.md) | 1 | 7 | 0 | 🟢 100% |
| [`ui.windows.usb`](ui_windows/ui_windows_usb.md) | 1 | 10 | 0 | 🟢 100% |
| [`ui.windows.vpn_window`](ui_windows/ui_windows_vpn_window.md) | 1 | 7 | 0 | 🟢 100% |
| [`ui.windows.weather_window`](ui_windows/ui_windows_weather_window.md) | 1 | 28 | 0 | 🟢 100% |
| [`ui.windows.wifi_window`](ui_windows/ui_windows_wifi_window.md) | 1 | 12 | 0 | 🟢 100% |

## Config

| Módulo | Clases | Métodos | Funciones | Cobertura |
|--------|--------|---------|-----------|-----------|
| [`config.__init__`](config/config___init__.md) | 0 | 0 | 0 | N/A |
| [`config.button_labels`](config/config_button_labels.md) | 0 | 0 | 0 | N/A |
| [`config.local_settings`](config/config_local_settings.md) | 0 | 0 | 0 | N/A |
| [`config.local_settings_io`](config/config_local_settings_io.md) | 0 | 0 | 7 | 🟢 100% |
| [`config.settings`](config/config_settings.md) | 2 | 0 | 0 | 🟢 100% |
| [`config.themes`](config/config_themes.md) | 0 | 0 | 7 | 🟢 100% |

## Utils

| Módulo | Clases | Métodos | Funciones | Cobertura |
|--------|--------|---------|-----------|-----------|
| [`utils.__init__`](utils/utils___init__.md) | 0 | 0 | 0 | N/A |
| [`utils.file_manager`](utils/utils_file_manager.md) | 1 | 4 | 0 | 🟢 100% |
| [`utils.logger`](utils/utils_logger.md) | 2 | 13 | 3 | 🟢 100% |
| [`utils.system_utils`](utils/utils_system_utils.md) | 1 | 11 | 0 | 🟢 100% |
