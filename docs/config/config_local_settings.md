# `config.local_settings`

> **Ruta**: `config/local_settings.py`

Overrides locales — generado automáticamente.
No editar manualmente: usa la ventana de configuración del dashboard.

## Imports

```python
from config.settings import Icons
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `WEATHER_CITY` | `'Cáseda, España'` |
| `WEATHER_LAT` | `42.52255` |
| `WEATHER_LON` | `-1.36636` |
| `WEATHER_FAVORITES` | `['Falces, España', 'Cáseda, España']` |
| `gpio_pins_config` | `{'17': {'mode': 'PWM', 'label': 'RED_LED'}, '27': {'mode': 'PWM', 'label': 'GREE...` |
| `watchdog_critical_services` | `['wayvnc-dsi', 'wayvnc', 'wayvnc-control', 'alsa-restore']` |
| `watchdog_threshold` | `1` |
| `watchdog_interval` | `30` |
| `log_file_level` | `20` |
| `log_console_level` | `30` |
| `log_console_exact` | `False` |
| `log_module_levels` | `{}` |
| `wifi_interface` | `'wlan1'` |
