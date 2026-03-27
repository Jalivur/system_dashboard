# 🖥️ Sistema de Monitoreo y Control - Dashboard v4.2

Sistema completo de monitoreo y control para Raspberry Pi con interfaz gráfica DSI, menú por pestañas con scroll táctil, control de ventiladores PWM, temas personalizables, histórico de datos, gestión avanzada del sistema, integración con Homebridge, alertas externas por Telegram, escáner de red local, integración Pi-hole, gestor VPN, control de brillo, pantalla de resumen, LEDs RGB inteligentes, alertas de audio con voz TTS, cámara con OCR, SMART extendido de NVMe, monitor WiFi con selector de interfaz, monitor SSH, editor de configuración local, control de audio ALSA, widget de clima, escáner I²C, monitor/control GPIO, service watchdog y configuración de logging en runtime.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![Version](https://img.shields.io/badge/Version-4.2-blue.svg)]()

---

## ✨ Características Principales

### 🗂️ **Menú por Pestañas con Scroll Táctil** *(v4.0)*
- **6 pestañas categorizadas**: Sistema, Red, Hardware, Servicios, Registros, Config
- **Scroll horizontal táctil** en la barra de pestañas — ancho fijo 130px por pestaña
- **Footer siempre visible**: Gestor Botones, Reiniciar, Salir — accesibles desde cualquier pestaña
- Pestañas definidas en `config/settings.py → class UI` — añadir una pestaña nueva es solo una línea

### 🖥️ **Monitoreo Completo del Sistema**
- **CPU**: Uso en tiempo real, frecuencia, gráficas históricas
- **RAM**: Memoria usada/total, porcentaje, visualización dinámica
- **Temperatura**: Monitoreo de CPU con alertas por color
- **Disco**: Espacio usado/disponible, temperatura NVMe, I/O en tiempo real
- **Uptime**: Calculado desde `/proc/uptime` — correcto desde el primer segundo, independiente del reloj del sistema

### 🪟 **UI Unificada con Header Táctil**
- **Header en todas las ventanas**: título + status dinámico + botón ✕ (52×42px táctil)
- Función `make_window_header()` centralizada en `ui/styles.py`

### 🌡️ **Control Inteligente de Ventiladores**
- **5 Modos**: Auto (curva), Manual, Silent (30%), Normal (50%), Performance (100%)
- **Curvas personalizables**: Define hasta 8 puntos temperatura-PWM
- **Servicio background**: Funciona incluso con ventana cerrada

### 🌐 **Monitor de Red Avanzado**
- **Tráfico en tiempo real**: Download/Upload con gráficas
- **Auto-detección**: Interfaz activa (eth0, wlan0, tun0)
- **Speedtest integrado**: CLI oficial de Ookla

### 󰖩 **Monitor WiFi** *(v3.8+)*
- Señal en tiempo real: dBm, calidad de enlace, SSID, bitrate
- Tráfico RX/TX con gráficas independientes
- **Selector de interfaz** en el header — visible si hay más de una `wlan*`, persistido en `local_settings.py`

### **Monitor SSH** *(v3.8)*
- Sesiones activas en tiempo real con IP de origen y hora de conexión
- Historial con duración formateada y detección de cortes

### 🔧 **Editor de Configuración** *(v3.8)*
- Edita `config/local_settings.py` por máquina sin tocar `settings.py`
- Parámetros editables: pantalla, tiempos, umbrales CPU/Temp/RAM/Red
- Iconos editables con preview en tiempo real, merge inteligente

### 🖧 **Escáner de Red Local**
- Escaneo con arp-scan: IP, MAC y fabricante (OUI lookup)

### 🕳️ **Integración Pi-hole v6**
- API v6 nativa, estadísticas en tiempo real, badge en menú

### 📲 **Alertas Externas por Telegram**
- Sin dependencias nuevas: usa `urllib` de stdlib
- Anti-spam: edge-trigger + sustain de 60s

### 🏠 **Integración Homebridge Extendida**
- 5 tipos de dispositivo: switch, luz, termostato, sensor, persiana
- 3 badges en el menú: offline, encendidos, con fallo

### ⚙️ **Monitor de Servicios systemd**
- Gestión completa: Start/Stop/Restart, estado visual, logs en tiempo real

### 🐕 **Service Watchdog** *(v4.2)*
- Monitor de servicios críticos con umbral de fallos consecutivos + auto-reinicio
- Umbral e intervalo configurables, badge de reinicios en el menú

### ⚙️ **Servicios Dashboard** *(v3.5/v3.6)*
- ServiceRegistry: registro centralizado de todos los servicios
- ServicesManagerWindow: activar/desactivar servicios desde la UI

### 🔧 **Gestor de Botones del Menú** *(v3.6.5)*
- Mostrar/ocultar botones del menú principal por máquina

### 🕐 **Gestor de Crontab** *(v3.7)*
- Ver, añadir, editar y eliminar entradas del crontab por usuario

### 📊 **Histórico de Datos**
- Recolección automática cada 5 minutos en background (SQLite)
- 8 gráficas en 24h, 7d, 30d con exportación CSV

### 🔒 **Gestor de Conexiones VPN**
- Estado en tiempo real, badge en menú, conectar/desconectar

### 💡 **Control LEDs RGB**
- 6 modos: auto, apagado, color fijo, secuencial, respiración, arcoíris

### 🔊 **Alertas de Audio**
- Voz TTS en español con `espeak-ng` + tono sintético, 11 archivos .wav

### 📷 **Cámara + Escáner OCR**
- Cámara OV5647 via `rpicam-still`, OCR con Tesseract local

### 󰔎 **15 Temas Personalizables**
- Cambio con un clic, preview en vivo

### 🔊 **Control de Audio ALSA** *(v4.2)*
- Control de volumen y mute via `amixer` desde la UI
- VU meter configurable, selector de control ALSA

### 🌦️ **Widget de Clima** *(v4.2)*
- Open-Meteo sin clave API, temperatura exterior + previsión diaria
- Drill-down días → horas, AQI, fondo dinámico por código WMO
- Badge de lluvia en el menú, favoritos persistidos

### 🔌 **Escáner I²C** *(v4.2)*
- `smbus2` solo lectura — detecta dispositivos en todos los buses disponibles
- Cards por bus con badge hex, escaneo manual — seguro con fase1.py

### ⚡ **Monitor / Control GPIO** *(v4.2)*
- Tres modos por pin: INPUT, OUTPUT, PWM
- Modo LIBRE / CONTROLANDO, configuración persistida
- Pines reservados por fase1.py protegidos automáticamente

### 📋 **Config Logging** *(v4.2)*
- Control de niveles de logging en runtime desde la UI
- Por handler (fichero/consola) y por módulo individual
- Persistido en `local_settings.py` — se restaura al arrancar
- Forzar rotación manual del log

---

## 🖥️ Soporte Multi-máquina

`config/local_settings.py` (en `.gitignore`) permite configuración independiente por máquina.

### Pi 5 (pantalla DSI física + Wayland)
- Compositor: **labwc** sobre Wayland
- Acceso remoto: `wayvnc --output=DSI-2 0.0.0.0 5901`
- Resolución DSI: 800×480

### Pi 3B+ (sin pantalla física + X11)
- Display virtual `:1` con **Xvfb**
- Acceso remoto: x11vnc en puerto `5901` sobre `:1`
- `local_settings.py`: `DSI_X=0, DSI_Y=0, DSI_WIDTH=1024, DSI_HEIGHT=762`

---

## 📦 Instalación

### ⚡ Instalación Recomendada

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

### 🛠️ Instalación Manual

```bash
sudo apt-get update
sudo apt-get install -y lm-sensors usbutils udisks2 smartmontools arp-scan wireless-tools

curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest

sudo sensors-detect --auto
pip3 install --break-system-packages -r requirements.txt

echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan" | sudo tee /etc/sudoers.d/arp-scan
echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/bin/smartctl"  | sudo tee /etc/sudoers.d/smartctl

# Hardware FNK0100K — cámara y OCR (opcional)
sudo apt install rpicam-apps tesseract-ocr tesseract-ocr-spa espeak-ng
pip install pytesseract --break-system-packages

python3 main.py
```

---

## 📊 Arquitectura del Proyecto (v4.2)

```
system_dashboard/
├── config/
│   ├── settings.py                 # Constantes globales + class Icons + class UI (pestañas)
│   ├── button_labels.py            # Labels de botones (fuente única de verdad)
│   ├── themes.py                   # 15 temas pre-configurados
│   ├── local_settings_io.py        # Módulo compartido lectura/escritura local_settings.py
│   ├── services.json               # Config servicios y UI (auto-generado, en .gitignore)
│   └── local_settings.py           # Overrides por máquina (en .gitignore)
├── core/
│   ├── service_registry.py
│   ├── system_monitor.py           # Uptime via /proc/uptime (correcto sin RTC)
│   ├── fan_controller.py, fan_auto_service.py
│   ├── network_monitor.py, network_scanner.py
│   ├── disk_monitor.py, process_monitor.py
│   ├── service_monitor.py, update_monitor.py
│   ├── homebridge_monitor.py, pihole_monitor.py
│   ├── alert_service.py, led_service.py
│   ├── hardware_monitor.py, audio_alert_service.py
│   ├── display_service.py, vpn_monitor.py
│   ├── crontab_service.py, camera_service.py
│   ├── ssh_monitor.py, wifi_monitor.py  # selector interfaz + persistencia
│   ├── audio_service.py            # Control ALSA via amixer
│   ├── weather_service.py          # Open-Meteo + AQI + favoritos
│   ├── i2c_monitor.py              # smbus2 solo lectura
│   ├── gpio_monitor.py             # gpiozero INPUT/OUTPUT/PWM + LIBRE/CONTROLANDO
│   ├── service_watchdog.py         # Monitor críticos + auto-reinicio
│   ├── data_logger.py, data_analyzer.py
│   ├── data_collection_service.py, cleanup_service.py
│   └── hardware_info_monitor.py
├── ui/
│   ├── main_window.py              # Layout, pestañas, coordinación (~450 líneas)
│   ├── main_badges.py              # BadgeManager
│   ├── main_update_loop.py         # UpdateLoop — reloj, uptime, badges
│   ├── main_system_actions.py      # exit_application, restart_application
│   ├── window_lifecycle.py         # WindowLifecycleManager
│   ├── window_manager.py           # Visibilidad botones via JSON
│   ├── styles.py
│   ├── widgets/
│   │   ├── graphs.py
│   │   └── dialogs.py
│   └── windows/
│       └── (una ventana por fichero — 32 ventanas)
├── utils/
│   ├── file_manager.py, system_utils.py
│   └── logger.py                   # Niveles persistidos en local_settings.py
├── data/
├── scripts/
├── .env, .env.example
├── install_system.sh, install.sh
├── main.py
└── requirements.txt
```

---

## 🗂️ Menú por Pestañas (v4.0)

| Pestaña | Contenido |
|---------|-----------|
| **Sistema** | Resumen, Monitor Placa, Monitor Disco, Monitor USB, Monitor Procesos, Actualizaciones |
| **Red** | Monitor Red, Red Local, Monitor WiFi, Monitor SSH, Pi-hole, VPN |
| **Hardware** | Info Hardware, Control Ventiladores, LEDs RGB, Brillo Pantalla, Audio Control, Cámara, I²C Scanner, GPIO Monitor |
| **Servicios** | Monitor Servicios, Servicios Dashboard, Gestor Crontab, Homebridge, Lanzadores, Service Watchdog |
| **Registros** | Histórico Datos, Historial Alertas, Visor Logs, Config Logging |
| **Config** | Editor Config, Cambiar Tema |

---

## 🔗 Relación fase1.py ↔ Dashboard

`fase1.py` es un proceso independiente. Comunicación exclusivamente via JSON:

| Fichero | Quién escribe | Quién lee |
|---------|--------------|-----------|
| `data/fan_state.json` | Dashboard (`FanController`) | `fase1.py` |
| `data/led_state.json` | Dashboard (`LedService`) | `fase1.py` |
| `data/hardware_state.json` | `fase1.py` | Dashboard (`HardwareMonitor`) |

El hardware I²C del módulo Expansion Freenove es **exclusivo de fase1.py**. Los pines {2, 3, 12, 13, 14, 15, 18, 19} están protegidos en `GPIOMonitor._RESERVED_PINS`.

---

## 🏠 Configuración de Homebridge

```env
HOMEBRIDGE_HOST=192.168.1.X
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña
```

---

## 🕳️ Configuración de Pi-hole

```env
PIHOLE_HOST=192.168.1.X
PIHOLE_PORT=80
PIHOLE_PASSWORD=tu_contraseña
```

> Compatible exclusivamente con **Pi-hole v6**.

---

## 📲 Configuración de Alertas Telegram

```env
TELEGRAM_TOKEN=123456789:ABCdefGHI...
TELEGRAM_CHAT_ID=987654321
```

---

## 🔧 Troubleshooting

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto && sudo systemctl restart lm-sensors` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Speedtest falla | Instalar CLI oficial Ookla |
| USB no expulsa | `sudo apt install udisks2` |
| Homebridge no conecta | Verificar `.env` y activar Insecure Mode |
| Red Local no escanea | `sudo apt install arp-scan` y configurar sudoers |
| Pi-hole no conecta | Solo compatible con v6; verificar `.env` |
| WiFi no muestra datos | `sudo apt install wireless-tools` |
| WiFi no lista interfaces | Verificar interfaces `wlan*` en `/proc/net/dev` |
| SSH monitor vacío | Verificar que `who` y `last` funcionan |
| No puedo escribir en entries (VNC) | Verificar que se usa `make_entry()` de `ui/styles.py` |
| Foco perdido tras inactividad (Wayland) | `gsettings set org.gnome.desktop.session idle-delay 0` |
| Dashboard no visible por VNC en Pi 5 | `wayvnc --output=DSI-2 0.0.0.0 5901` |
| Audio no suena | `aplay -l` → verificar dispositivo HDMI |
| Cámara no encontrada | `sudo apt install rpicam-apps` |
| I²C buses no aparecen | Habilitar I²C en `raspi-config` |
| GPIO pin busy al arrancar | Pin ocupado — usar modo LIBRE o revisar `_RESERVED_PINS` |
| GPIO no libera en Pi 5 | lgpio mantiene `/dev/gpiochip0` — usar botón "Liberar GPIO" |
| Uptime incorrecto al arrancar | Normal sin RTC — se corrige al conectar red (NTP) |
| Log lleno de DEBUG | Config Logging → nivel Fichero a INFO o WARNING |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 📊 Estadísticas del Proyecto

| Métrica | v4.0 | v4.2 |
|---------|------|------|
| Archivos Python | 73 | **81** |
| Ventanas | 27 | **32** |
| Temas | 15 | 15 |
| Badges en menú | 12 | **13** |
| Servicios background | 16 | **20** |
| Módulos ui/main_* | 5 | 5 |
| Documentos | 9 | 10 |

---

## Changelog

### **v4.2** ← ACTUAL

- ✅ **NUEVO**: Control de Audio ALSA (`AudioService` + `AudioWindow`)
- ✅ **NUEVO**: Widget de Clima (`WeatherService` + `WeatherWindow`) — Open-Meteo, AQI, drill-down, badge lluvia
- ✅ **NUEVO**: Escáner I²C (`I2CMonitor` + `I2CWindow`) — smbus2 solo lectura, cards por bus
- ✅ **NUEVO**: Monitor/Control GPIO (`GPIOMonitor` + `GPIOWindow`) — INPUT/OUTPUT/PWM, LIBRE/CONTROLANDO
- ✅ **NUEVO**: Service Watchdog (`ServiceWatchdog` + `ServiceWatchdogWindow`) — auto-reinicio, badge
- ✅ **NUEVO**: Config Logging (`LogConfigWindow`) — niveles runtime por handler y módulo, persistentes
- ✅ **NUEVO**: `config/local_settings_io.py` — módulo compartido persistencia `local_settings.py`
- ✅ **NUEVO**: Selector de interfaz WiFi en header de `WiFiWindow` — persistido, cambio en caliente
- ✅ **FIX**: Uptime calculado desde `/proc/uptime` — correcto sin RTC, independiente de NTP
- ✅ **AUDIT**: Auditoría completa ui/ (Fases 1-6) — encapsulación core/ui, ARCH-01 (`is_running()`), issues UI-F2 a UI-F6

### **v4.0** - 2026-03-05

- ✅ Menú por pestañas con scroll horizontal táctil — 6 pestañas, ancho fijo 130px
- ✅ `WindowLifecycleManager` — elimina 27 métodos `open_*`
- ✅ `BadgeManager`, `UpdateLoop`, `main_system_actions.py`
- ✅ `main_window.py` 891 → 451 líneas (−49%)
- ✅ `WindowManager` — patrón callback

### **v3.8** - 2026-03
- ✅ Monitor WiFi, Monitor SSH, Editor de Configuración
- ✅ Refactor: `crontab_service.py` y `camera_service.py` a `core/`
- ✅ Fix `StringVar`/`IntVar` con `master=` explícito

### **v3.7** - 2026-03-02
- ✅ Gestor Crontab, fix grab modal, `make_entry()`, soporte dual-Pi

### **v3.6.5**
- ✅ Gestor de Botones (`ButtonManagerWindow` + `WindowManager`)

### **v3.6**
- ✅ Servicios Dashboard (`ServicesManagerWindow`)

### **v3.5**
- ✅ `ServiceRegistry`

### **v3.4** - 2026-02-27
- ✅ LEDs RGB, temperatura chasis, alertas audio, cámara OCR, SMART NVMe extendido

### **v3.3** - 2026-02-27
- ✅ Resumen Sistema, control brillo DSI, gestor VPN

### **v3.2** - 2026-02-27
- ✅ Escáner red local, Pi-hole v6, historial alertas

### **v3.1** - 2026-02-26
- ✅ Alertas Telegram, Homebridge extendido (5 tipos)

### **v3.0** - 2026-02-26
- ✅ Visor de Logs

### v2.x
- Monitor completo, servicios systemd, histórico SQLite, 15 temas, badges

---

## Licencia

MIT License

---

## Agradecimientos

CustomTkinter · psutil · matplotlib · Ookla Speedtest CLI · Homebridge · Pi-hole · Raspberry Pi Foundation
