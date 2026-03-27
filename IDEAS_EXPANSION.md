# 💡 IDEAS_EXPANSION.md
## Expansión y Roadmap — Sistema de Monitoreo v4.2

---

## ✅ Implementado

### v4.2 (actual) — Audio + Clima + I²C + GPIO + ServiceWatchdog + LogConfig

- **Control de Audio ALSA** (`AudioService` + `AudioWindow`)
  - Control de volumen y mute via `amixer` desde la UI
  - VU meter configurable (40 segmentos verde→amarillo→rojo)
  - Selector de control ALSA, sin dependencias nuevas

- **Widget de Clima** (`WeatherService` + `WeatherWindow`)
  - Open-Meteo sin clave API — temperatura exterior + previsión diaria
  - Color dinámico por temperatura, barra de progreso del día
  - Drill-down días → horas (24h por día), AQI desde Open-Meteo
  - Fondo dinámico por código WMO, badge de lluvia en el menú principal
  - Favoritos de ubicaciones persistidos en `local_settings.py`

- **Escáner I²C** (`I2CMonitor` + `I2CWindow`)
  - `smbus2` solo lectura — escanea todos los buses `/dev/i2c-*`
  - Rango estándar 0x03–0x77, diccionario de dispositivos conocidos
  - Cards por bus con badge hex por dispositivo, botón escaneo manual, refresco 30s
  - Seguro — no interfiere con fase1.py (lectura especulativa)

- **Monitor / Control GPIO** (`GPIOMonitor` + `GPIOWindow`)
  - Tres modos por pin: INPUT (lectura), OUTPUT (toggle HIGH/LOW), PWM (slider duty cycle)
  - Modo **LIBRE**: libera todos los pines (`/dev/gpiochip0` via `Device.pin_factory.close()`) para scripts externos sin conflictos
  - Modo **CONTROLANDO**: dashboard reclama los pines con gpiozero
  - Configuración de pines (modo + etiqueta) persistida en `local_settings.py` via `local_settings_io`
  - Panel de configuración: añadir/eliminar pines, cambiar modo en caliente, feedback visual
  - Pines reservados por fase1.py protegidos automáticamente: {2, 3, 12, 13, 14, 15, 18, 19}
  - Arranque por defecto en modo LIBRE

- **Service Watchdog** (`ServiceWatchdog` + `ServiceWatchdogWindow`)
  - Monitor de servicios críticos con umbral de fallos consecutivos + auto-reinicio
  - Umbral e intervalo configurables, gestión de lista de críticos persistente
  - Stats globales, badge de reinicios en el menú principal

- **Config Logging** (`LogConfigWindow`)
  - Control de niveles de logging en runtime (fichero, consola, por módulo)
  - `tk.Listbox` nativo para lista de módulos — ligero en Wayland/labwc
  - Niveles persistidos en `local_settings.py` — se restauran al arrancar
  - Forzar rotación manual del log

- **`config/local_settings_io.py`** — módulo compartido para lectura/escritura de `local_settings.py`
  - API: `read() → (params, icons)`, `write(params, icons)`, `update_params(dict)`, `get_param(key, default)`
  - Usado por: `WeatherService`, `ConfigEditorWindow`, `GPIOMonitor`, `WiFiMonitor`, `DashboardLogger`

- **Selector de interfaz WiFi** (`WiFiWindow` + `WiFiMonitor`)
  - Selector en el header de la ventana — visible solo si hay más de una interfaz `wlan*`
  - Cambio en caliente: resetea históricos, fuerza refresco inmediato
  - Interfaz elegida persistida en `local_settings.py` como `wifi_interface`

- **Fix uptime** (`SystemMonitor`)
  - Uptime calculado desde `/proc/uptime` en lugar de `psutil.boot_time()`
  - Correcto desde el primer segundo, independiente del reloj del sistema y NTP
  - Elimina el problema de uptime inflado en Pi sin RTC tras arranque sin red

### v4.0 — Refactorización Arquitectural

- **Menú por pestañas con scroll horizontal táctil**
  - 6 pestañas categorizadas: Sistema, Red, Hardware, Servicios, Registros, Config
  - Ancho fijo 130px por pestaña — táctil, escala sin límite
  - Footer fijo (Gestor Botones, Reiniciar, Salir) visible desde cualquier pestaña
  - Pestañas definidas en `config/settings.py → class UI` — configuración pura

- **`WindowLifecycleManager`** (`ui/window_lifecycle.py`)
  - Elimina 27 métodos `open_*` dispersos en `main_window.py`
  - Ciclo de vida unificado: factory, lift, `_btn_active`/`_btn_idle`, bind `<Destroy>`

- **Modularización de `main_window.py`** (891 → 451 líneas, −49%)
  - `ui/main_badges.py` — `BadgeManager`
  - `ui/main_update_loop.py` — `UpdateLoop`
  - `ui/main_system_actions.py` — `exit_application`, `restart_application`

- **`WindowManager` refactorizado** — patrón callback (`set_rerender_callback`)

### v3.8 — SSH + WiFi + Config Editor + Refactors

- **Monitor SSH** — sesiones activas, historial humanizado
- **Monitor WiFi** — dBm, calidad, SSID, bitrate, tráfico RX/TX
- **Editor de Configuración** — edita `local_settings.py` desde la UI
- **Refactor arquitectónico** — `crontab_service.py` y `camera_service.py` a `core/`
- **Fix** `StringVar`/`IntVar` con `master=` explícito

### v3.7 — Crontab + Fixes + Multi-Pi
- Gestor Crontab, fix grab modal, `make_entry()`, soporte dual-Pi

### v3.6.5
- Gestor de Botones (`ButtonManagerWindow` + `WindowManager`)

### v3.6
- Servicios Dashboard (`ServicesManagerWindow`)

### v3.5
- `ServiceRegistry`

### v3.4 — Hardware FNK0100K
- LEDs RGB, temperatura chasis, alertas audio, cámara OCR, SMART NVMe extendido

### v3.3
- Resumen Sistema, control brillo DSI, gestor VPN

### v3.2
- Escáner Red Local, Pi-hole v6, historial alertas

### v3.1
- Alertas Telegram, Homebridge extendido (5 tipos)

### v3.0
- Visor de Logs

### v2.x
- Control Ventiladores PWM, monitores completos, 15 temas, badges, logging, SQLite

---

## 🔄 Ideas en evaluación para v4.3

### 🌐 API REST local
- Endpoint `/status` en JSON — `http.server` de stdlib, sin deps nuevas
- Permitiría integración con otros sistemas de la red

### 💾 Backup automático de configuración
- Copiar `data/` a NAS o USB al detectar dispositivo montado
- Restauración desde la UI

---

## 💭 Ideas futuras (backlog)

- **Notificaciones push locales** — avisos en pantalla sin Telegram
- **Historial de comandos crontab** — log de ejecuciones con resultado
- **Perfiles de configuración** — múltiples `local_settings.py` intercambiables
- **Dashboard web espejo** — servir la UI como página HTML desde el propio Pi
- **Multi-pantalla / modo kiosk** — detectar HDMI y extender la UI

---

## 🗺️ Roadmap

```
v2.x   ✅ Monitor completo, temas, SQLite, badges
v3.0   ✅ Visor Logs
v3.1   ✅ Telegram + Homebridge extendido
v3.2   ✅ Red Local + Pi-hole v6 + Historial Alertas
v3.3   ✅ Resumen Sistema + Brillo DSI + Gestor VPN
v3.4   ✅ LEDs RGB + Temp Chasis + Audio + Cámara OCR + SMART
v3.5   ✅ ServiceRegistry
v3.6   ✅ ServicesManagerWindow
v3.6.5 ✅ ButtonManagerWindow
v3.7   ✅ CrontabWindow + Fixes VNC/Wayland + Multi-Pi
v3.8   ✅ Monitor SSH + Monitor WiFi + Editor Config + Refactor core/
v4.0   ✅ Pestañas táctiles + WindowLifecycleManager + Modularización main_*
v4.2   ✅ Audio + Clima + I²C + GPIO + ServiceWatchdog + LogConfig + fixes  ← ACTUAL
v4.3   💭 API REST local + Backup automático
```

---

## 📊 Cobertura por módulo (v4.2)

| Área | Cobertura | Notas |
|------|-----------|-------|
| Hardware CPU/RAM/Temp/Disco | ✅ Completa | SystemMonitor + DiskMonitor |
| NVMe SMART | ✅ Completa | TBW, horas, vida útil, ciclos |
| Red | ✅ Completa | NetworkMonitor + NetworkScanner |
| WiFi | ✅ Completa | WiFiMonitor — señal, calidad, tráfico, selector interfaz |
| Procesos / Servicios systemd | ✅ Completa | ProcessMonitor + ServiceMonitor |
| Servicios Dashboard | ✅ Completa | ServiceRegistry + ServicesManagerWindow |
| Service Watchdog | ✅ Completa | Auto-reinicio, badge, persistencia |
| Fans | ✅ Completa | FanController + FanAutoService |
| Crontab | ✅ Completa | CrontabWindow, usuario/root |
| Menú configurable | ✅ Completa | ButtonManagerWindow + WindowManager |
| Pantalla | ✅ Completa | DisplayService (brillo DSI) |
| VPN | ✅ Básica | VpnMonitor (estado + conectar/desconectar) |
| Homebridge / HomeKit | ✅ Avanzada | 5 tipos de dispositivo |
| Pi-hole | ✅ Completa | API v6, estadísticas, badge |
| Alertas Telegram | ✅ Completa | edge-trigger + historial JSON |
| Alertas Audio | ✅ Completa | 11 sonidos TTS español, 4 métricas |
| Histórico / Análisis | ✅ Completa | SQLite + matplotlib |
| LEDs RGB GPIO Board | ✅ Completa | 6 modos, sin destellos |
| Temperatura chasis | ✅ Completa | Via fase1.py + hardware_state.json |
| Fan duty real | ✅ Completa | Via fase1.py + hardware_state.json |
| Cámara OV5647 | ✅ Completa | rpicam-still + OCR Tesseract |
| Monitor SSH | ✅ Completa | Sesiones activas + historial humanizado |
| Config por máquina | ✅ Completa | local_settings.py + Editor Config UI |
| Multi-Pi / local_settings | ✅ Completa | Pi 5 Wayland + Pi 3 Xvfb |
| Audio Control | ✅ Completa | amixer/aplay, VU meter, mute |
| Widget Clima | ✅ Completa | Open-Meteo, AQI, drill-down, badge |
| I²C Scanner | ✅ Completa | smbus2 solo lectura, cards por bus |
| GPIO Monitor/Control | ✅ Completa | INPUT/OUTPUT/PWM, LIBRE/CONTROLANDO, persistencia |
| Config Logging | ✅ Completa | Niveles runtime, por módulo, persistencia |
| API REST local | ❌ Pendiente | v4.3 |
| Backup automático | ❌ Pendiente | v4.3 |
