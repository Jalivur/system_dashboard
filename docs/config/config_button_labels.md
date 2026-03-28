# `config.button_labels`

> **Ruta**: `config/button_labels.py`

> **Cobertura de documentación**: N/A (0/0)

Labels de botones del menu principal.

Fuente unica de verdad para los textos de botones que aparecen en:
  - ui/main_window.py      (buttons_config, _btn_active, _btn_idle)
  - ui/window_manager.py   (_BTN_MAP, _ALWAYS_VISIBLE)
  - core/service_registry.py  (no usa labels directamente, pero _BTN_MAP si)

Nunca escribir literales de icono fuera de este fichero.
Para anadir un boton nuevo: añadir aqui primero, luego referenciar en los tres sitios.

---

## Dependencias internas

- `config.settings`

## Imports

```python
from config.settings import Icons
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `HARDWARE_INFO` | `f'{Icons.HARDWARE_INFO}  Info Hardware'` |
| `FAN_CONTROL` | `f'{Icons.FAN_CONTROL}  Control Ventiladores'` |
| `LED_RGB` | `f'{Icons.LED_RGB}  LEDs RGB'` |
| `MONITOR_PLACA` | `f'{Icons.MONITOR_PLACA}  Monitor Placa'` |
| `MONITOR_RED` | `f'{Icons.MONITOR_RED} Monitor Red'` |
| `MONITOR_USB` | `f'{Icons.MONITOR_USB} Monitor USB'` |
| `MONITOR_DISCO` | `f'{Icons.MONITOR_DISCO}  Monitor Disco'` |
| `LANZADORES` | `f'{Icons.LANZADORES}  Lanzadores'` |
| `PROCESOS` | `f'{Icons.PROCESOS} Monitor Procesos'` |
| `SERVICIOS` | `f'{Icons.SERVICIOS} Monitor Servicios'` |
| `SERVICIOS_DASH` | `f'{Icons.SERVICIOS}  Servicios Dashboard'` |
| `CRONTAB` | `f'{Icons.CRONTAB}  Gestor Crontab'` |
| `HISTORICO` | `f'{Icons.HISTORICO}  Histórico Datos'` |
| `ACTUALIZACIONES` | `f'{Icons.ACTUALIZACIONES}  Actualizaciones'` |
| `HOMEBRIDGE` | `f'{Icons.HOMEBRIDGE}  Homebridge'` |
| `VISOR_LOGS` | `f'{Icons.VISOR_LOGS}  Visor de Logs'` |
| `LOG_CONFIG` | `f'{Icons.LOG_CONFIG}  Config Logging'` |
| `RED_LOCAL` | `f'{Icons.RED_LOCAL}  Red Local'` |
| `PIHOLE` | `f'{Icons.PIHOLE}  Pi-hole'` |
| `VPN` | `f'{Icons.VPN}  Gestor VPN'` |
| `HISTORIAL_ALERTAS` | `f'{Icons.HISTORIAL_ALERTAS}  Historial Alertas'` |
| `BRILLO` | `f'{Icons.BRILLO}  Brillo Pantalla'` |
| `AUDIO` | `f'{Icons.AUDIO}  Control Audio'` |
| `CLIMA` | `f'{Icons.CLIMA}  Widget Clima'` |
| `RESUMEN` | `f'{Icons.RESUMEN}  Resumen Sistema'` |
| `CAMARA` | `f'{Icons.CAMARA}  Cámara'` |
| `TEMA` | `f'{Icons.TEMA}  Cambiar Tema'` |
| `SSH` | `f'{Icons.SSH}  Monitor SSH'` |
| `WIFI` | `f'{Icons.WIFI}  Monitor WiFi'` |
| `CONFIG` | `f'{Icons.CONFIG} Editor Config'` |
