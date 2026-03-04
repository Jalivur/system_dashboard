"""
Labels de botones del menu principal.

Fuente unica de verdad para los textos de botones que aparecen en:
  - ui/main_window.py      (buttons_config, _btn_active, _btn_idle)
  - ui/window_manager.py   (_BTN_MAP, _ALWAYS_VISIBLE)
  - core/service_registry.py  (no usa labels directamente, pero _BTN_MAP si)

Nunca escribir literales de icono fuera de este fichero.
Para anadir un boton nuevo: añadir aqui primero, luego referenciar en los tres sitios.
"""
from config.settings import Icons

# ── Botones controlables por WindowManager ────────────────────────────────────
HARDWARE_INFO       = f"{Icons.HARDWARE_INFO}  Info Hardware"
FAN_CONTROL         = f"{Icons.FAN_CONTROL}  Control Ventiladores"
LED_RGB             = f"{Icons.LED_RGB}  LEDs RGB"
MONITOR_PLACA       = f"{Icons.MONITOR_PLACA}  Monitor Placa"
MONITOR_RED         = f"{Icons.MONITOR_RED} Monitor Red"
MONITOR_USB         = f"{Icons.MONITOR_USB} Monitor USB"
MONITOR_DISCO       = f"{Icons.MONITOR_DISCO}  Monitor Disco"
LANZADORES          = f"{Icons.LANZADORES}  Lanzadores"
PROCESOS            = f"{Icons.PROCESOS} Monitor Procesos"
SERVICIOS           = f"{Icons.SERVICIOS} Monitor Servicios"
SERVICIOS_DASH      = f"{Icons.SERVICIOS}  Servicios Dashboard"
CRONTAB             = f"{Icons.CRONTAB}  Gestor Crontab"
HISTORICO           = f"{Icons.HISTORICO}  Hist\u00f3rico Datos"
ACTUALIZACIONES     = f"{Icons.ACTUALIZACIONES}  Actualizaciones"
HOMEBRIDGE          = f"{Icons.HOMEBRIDGE}  Homebridge"
VISOR_LOGS          = f"{Icons.VISOR_LOGS}  Visor de Logs"
RED_LOCAL           = f"{Icons.RED_LOCAL}  Red Local"
PIHOLE              = f"{Icons.PIHOLE}  Pi-hole"
VPN                 = f"{Icons.VPN}  Gestor VPN"
HISTORIAL_ALERTAS   = f"{Icons.HISTORIAL_ALERTAS}  Historial Alertas"
BRILLO              = f"{Icons.BRILLO}  Brillo Pantalla"
RESUMEN             = f"{Icons.RESUMEN}  Resumen Sistema"
CAMARA              = f"{Icons.CAMARA}  C\u00e1mara"
TEMA                = f"{Icons.TEMA}  Cambiar Tema"
SSH                 = f"{Icons.SSH}  Monitor SSH"
WIFI                = f"{Icons.WIFI}  Monitor WiFi"
CONFIG              = f"{Icons.CONFIG} Editor Config"

# ── Botones siempre visibles (no controlados por WindowManager) ───────────────
BOTONES             = f"{Icons.BOTONES}  Gestor de Botones"
REINICIAR           = f"{Icons.REINICIAR} Reiniciar"
SALIR               = f"{Icons.SALIR}  Salir"
