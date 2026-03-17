# 🖥️ Sistema de Monitoreo y Control - Dashboard v4.2

Sistema completo de monitoreo y control para Raspberry Pi con interfaz gráfica DSI, menú por pestañas con scroll táctil, control de ventiladores PWM, temas personalizables, histórico de datos, gestión avanzada del sistema, integración con Homebridge, alertas externas por Telegram, escáner de red local, integración Pi-hole, gestor VPN, control de brillo, pantalla de resumen, LEDs RGB inteligentes, alertas de audio con voz TTS, cámara con OCR, SMART extendido de NVMe, monitor WiFi, monitor SSH, editor de configuración local, control de audio ALSA, widget de clima, escáner I²C y monitor/control GPIO.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![Version](https://img.shields.io/badge/Version-4.2-orange.svg)]()

---

## ✨ Características Principales

### 🗂️ **Menú por Pestañas con Scroll Táctil** *(v4.0)*
- **6 pestañas categorizadas**: Sistema, Red, Hardware, Servicios, Registros, Config
- **Scroll horizontal táctil** en la barra de pestañas — ancho fijo 130px por pestaña, escala a cualquier número sin encoger
- **Footer siempre visible**: Gestor Botones, Reiniciar, Salir — accesibles desde cualquier pestaña
- Pestañas definidas en `config/settings.py → class UI` — añadir una pestaña nueva es solo una línea de configuración

### 🖥️ **Monitoreo Completo del Sistema**
- **CPU**: Uso en tiempo real, frecuencia, gráficas históricas
- **RAM**: Memoria usada/total, porcentaje, visualización dinámica
- **Temperatura**: Monitoreo de CPU con alertas por color
- **Disco**: Espacio usado/disponible, temperatura NVMe, I/O en tiempo real

### 🪟 **UI Unificada con Header Táctil**
- **Header en todas las ventanas**: título + status dinámico + botón ✕ (52×42px táctil)
- **Status en tiempo real** en el header: CPU/RAM/Temp (Monitor Placa), Disco/NVMe (Monitor Disco), interfaz/velocidades (Monitor Red)
- Función `make_window_header()` centralizada en `ui/styles.py`

### 🌡️ **Control Inteligente de Ventiladores**
- **5 Modos**: Auto (curva), Manual, Silent (30%), Normal (50%), Performance (100%)
- **Curvas personalizables**: Define hasta 8 puntos temperatura-PWM
- **Servicio background**: Funciona incluso con ventana cerrada

### 🌐 **Monitor de Red Avanzado**
- **Tráfico en tiempo real**: Download/Upload con gráficas
- **Auto-detección**: Interfaz activa (eth0, wlan0, tun0)
- **Speedtest integrado**: CLI oficial de Ookla

### 󰖩 **Monitor WiFi** *(v3.8)*
- Señal en tiempo real: dBm, calidad de enlace, SSID, bitrate
- Barras visuales de señal (▂▄▆█) y gráfica histórica
- Tráfico RX/TX con gráficas independientes

### **Monitor SSH** *(v3.8)*
- Sesiones activas en tiempo real con IP de origen y hora de conexión
- Historial con duración formateada y detección de cortes
- Textos legibles: `pts/0` → `Sesión 1`, IPs locales etiquetadas

### 🔧 **Editor de Configuración** *(v3.8)*
- Edita `config/local_settings.py` por máquina sin tocar `settings.py`
- Parámetros editables: pantalla, tiempos, umbrales CPU/Temp/RAM/Red
- Iconos editables con preview en tiempo real, merge inteligente

### 🖧 **Escáner de Red Local**
- Escaneo con arp-scan: IP, MAC y fabricante (OUI lookup)
- Auto-refresco cada 60s en background

### 🕳️ **Integración Pi-hole v6**
- API v6 nativa, estadísticas en tiempo real
- Badge en menú: 🔴 si Pi-hole está offline

### 📲 **Alertas Externas por Telegram**
- Sin dependencias nuevas: usa `urllib` de stdlib
- Anti-spam: edge-trigger + sustain de 60s

### 🏠 **Integración Homebridge Extendida**
- 5 tipos de dispositivo: switch, luz, termostato, sensor, persiana
- 3 badges en el menú: offline, encendidos, con fallo

### ⚙️ **Monitor de Servicios systemd**
- Gestión completa: Start/Stop/Restart, estado visual, logs en tiempo real

### 🐕 **Service Watchdog** *(v4.2)*
- Monitor servicios **críticos** con umbral fallos consecutivos + auto-reinicio
- Umbral/Intervalo configurables via **text entries precisas** (1-10, 30-300s, debounce 400ms)
- Gestión lista críticos persistente, stats globales, filtrado/búsqueda en vivo
- [SERVICE_WATCHDOG.md](SERVICE_WATCHDOG.md)

### ⚙️ **Servicios Dashboard** *(v3.5/v3.6)*
- ServiceRegistry: registro centralizado de todos los servicios
- ServicesManagerWindow: activar/desactivar servicios desde la UI

### 🔧 **Gestor de Botones del Menú** *(v3.6.5)*
- Mostrar/ocultar botones del menú principal por máquina

### 🕐 **Gestor de Crontab** *(v3.7)*
- Ver, añadir, editar y eliminar entradas del crontab
- Selector de usuario: usuario / root

### 📊 **Histórico de Datos**
- Recolección automática cada 5 minutos en background (SQLite)
- 8 gráficas en 24h, 7d, 30d con exportación CSV

### 🔒 **Gestor de Conexiones VPN**
- Estado en tiempo real, badge en menú, conectar/desconectar
- Compatible con WireGuard y OpenVPN

### 💡 **Control LEDs RGB**
- 6 modos: auto, apagado, color fijo, secuencial, respiración, arcoíris

### 🔊 **Alertas de Audio**
- Voz TTS en español con `espeak-ng` + tono sintético
- 11 archivos .wav

### 📷 **Cámara + Escáner OCR**
- Cámara OV5647 via `rpicam-still`, OCR con Tesseract local

### 󰔎 **15 Temas Personalizables**
- Cambio con un clic, preview en vivo

### 🔊 **Control de Audio ALSA** *(v4.1)*
- Control de volumen y mute via `amixer` desde la UI
- VU meter configurable, selector de control ALSA
- Sin dependencias nuevas — solo `subprocess`

### 🌦️ **Widget de Clima** *(v4.1)*
- Open-Meteo sin clave API, temperatura exterior + previsión diaria
- Color dinámico por temperatura, barra de progreso del día
- Drill-down días → horas, AQI, fondo dinámico por código WMO
- Badge de lluvia en el menú principal
- Favoritos persistidos en `local_settings.py`

### 🔌 **Escáner I²C** *(v4.1)*
- `smbus2` solo lectura — detecta dispositivos en todos los buses disponibles
- Cards por bus con badge hex por dispositivo, botón escaneo manual
- Seguro — no interfiere con fase1.py

### ⚡ **Monitor / Control GPIO** *(v4.1)*
- Tres modos por pin: INPUT (lectura), OUTPUT (toggle HIGH/LOW), PWM (slider duty cycle)
- Modo **LIBRE**: libera todos los pines (`/dev/gpiochip0`) para scripts externos
- Modo **CONTROLANDO**: dashboard reclama los pines con gpiozero
- Configuración de pines persistida en `local_settings.py`
- Pines reservados por fase1.py protegidos automáticamente

---

## 🖥️ Soporte Multi-máquina

`config/local_settings.py` (en `.gitignore`) permite configuración independiente por máquina sin tocar git. El **Editor de Configuración** genera y mantiene este fichero desde la propia UI.

### Pi 5 (pantalla DSI física + Wayland)
- Compositor: **labwc** sobre Wayland
- Acceso remoto: `wayvnc --output=DSI-2 0.0.0.0 5901`
- Resolución DSI: 800×480
- Idle desactivado: `gsettings set org.gnome.desktop.session idle-delay 0`

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

# CLI oficial de Ookla (speedtest)
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
│   ├── system_monitor.py
│   ├── fan_controller.py, fan_auto_service.py
│   ├── network_monitor.py, network_scanner.py
│   ├── disk_monitor.py, process_monitor.py
│   ├── service_monitor.py, update_monitor.py
│   ├── homebridge_monitor.py, pihole_monitor.py
│   ├── alert_service.py, led_service.py
│   ├── hardware_monitor.py, audio_alert_service.py
│   ├── display_service.py, vpn_monitor.py
│   ├── crontab_service.py, camera_service.py
│   ├── ssh_monitor.py, wifi_monitor.py
│   ├── audio_service.py            # Control ALSA via amixer (v4.1)
│   ├── weather_service.py          # Open-Meteo + AQI + favoritos (v4.1)
│   ├── i2c_monitor.py              # smbus2 solo lectura (v4.1)
│   ├── gpio_monitor.py             # gpiozero INPUT/OUTPUT/PWM + LIBRE/CONTROLANDO (v4.1)
│   ├── data_logger.py, data_analyzer.py
│   ├── data_collection_service.py, cleanup_service.py
│   └── hardware_info_monitor.py
├── ui/
│   ├── main_window.py              # Layout, pestañas, coordinación (~450 líneas)
│   ├── main_badges.py              # BadgeManager — crear y actualizar badges (v4.0)
│   ├── main_update_loop.py         # UpdateLoop — reloj, uptime, loop de badges (v4.0)
│   ├── main_system_actions.py      # exit_application, restart_application (v4.0)
│   ├── window_lifecycle.py         # WindowLifecycleManager (v4.0)
│   ├── window_manager.py           # Visibilidad botones via JSON, patrón callback
│   ├── styles.py
│   ├── widgets/
│   │   ├── graphs.py
│   │   └── dialogs.py
│   └── windows/
│       └── (una ventana por fichero — 31 ventanas)
├── utils/
│   ├── file_manager.py, system_utils.py, logger.py
├── data/                           # Auto-generado al ejecutar
├── scripts/
│   ├── sounds/
│   └── generate_sounds.py
├── .env, .env.example
├── install_system.sh, install.sh
├── main.py
└── requirements.txt
```

### Módulos ui/ (v4.0+)

| Fichero | Responsabilidad |
|---------|----------------|
| `main_window.py` | Layout, pestañas, coordinación (~450 líneas) |
| `main_badges.py` | `BadgeManager`: crear y actualizar badges de menú |
| `main_update_loop.py` | `UpdateLoop`: reloj, uptime, loop de badges |
| `main_system_actions.py` | `exit_application`, `restart_application` |
| `window_lifecycle.py` | `WindowLifecycleManager`: ciclo de vida ventanas hijas |
| `window_manager.py` | Visibilidad de botones via JSON, patrón callback |

---

## 🗂️ Menú por Pestañas (v4.0)

El menú está organizado en 6 pestañas con scroll horizontal táctil. La configuración vive en `config/settings.py → class UI`:

| Pestaña | Contenido |
|---------|-----------|
| **Sistema** | Resumen, Monitor Placa, Control Ventiladores, LEDs RGB, Brillo, Cámara, Lanzadores, Audio Control |
| **Red** | Monitor Red, Red Local, Pi-hole, VPN, Homebridge, Monitor WiFi |
| **Hardware** | Info Hardware, Monitor Disco, Monitor USB, I²C Scanner, GPIO Monitor, Widget Clima |
| **Servicios** | Monitor Servicios, Servicios Dashboard, Monitor Procesos, Gestor Crontab, Actualizaciones |
| **Registros** | Visor Logs, Histórico Datos, Historial Alertas, Monitor SSH |
| **Config** | Editor Config, Cambiar Tema, Gestor Botones |

> El footer (Gestor Botones, Reiniciar, Salir) es fijo y visible desde cualquier pestaña.

---

## 🔗 Relación fase1.py ↔ Dashboard

`fase1.py` es un proceso independiente que corre en paralelo. Comunicación exclusivamente via JSON:

| Fichero | Quién escribe | Quién lee |
|---------|--------------|-----------|
| `data/fan_state.json` | Dashboard (`FanController`) | `fase1.py` |
| `data/led_state.json` | Dashboard (`LedService`) | `fase1.py` |
| `data/hardware_state.json` | `fase1.py` | Dashboard (`HardwareMonitor`) |

El hardware I²C del módulo Expansion Freenove (ventiladores, LEDs, OLED) es **exclusivo de fase1.py** — nunca se accede desde el dashboard.

> **GPIO**: los pines usados por fase1.py (GPIO 2, 3, 12, 13, 14, 15, 18, 19) están protegidos en `GPIOMonitor._RESERVED_PINS` y nunca se abren desde el dashboard.

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
| Pi-hole no conecta | Verificar `.env`; solo compatible con v6 |
| WiFi no muestra datos | `sudo apt install wireless-tools` |
| SSH monitor vacío | Verificar que `who` y `last` funcionan en el sistema |
| No puedo escribir en entries (VNC) | Verificar que se usa `make_entry()` de `ui/styles.py` |
| Foco perdido tras inactividad (Wayland) | `gsettings set org.gnome.desktop.session idle-delay 0` |
| Dashboard no visible por VNC en Pi 5 | `wayvnc --output=DSI-2 0.0.0.0 5901` |
| Audio no suena | `aplay -l` → verificar dispositivo HDMI |
| Cámara no encontrada | `sudo apt install rpicam-apps` |
| I²C buses no aparecen | Verificar que I²C está habilitado en `raspi-config` |
| GPIO pin busy al arrancar | Pin ocupado por otro proceso — usar modo LIBRE o revisar `_RESERVED_PINS` |
| GPIO no libera en Pi 5 | lgpio mantiene `/dev/gpiochip0` — usar botón "Liberar GPIO" desde la ventana |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 📚 Documentación

- [QUICKSTART.md](QUICKSTART.md) — Inicio rápido
- [INSTALL_GUIDE.md](INSTALL_GUIDE.md) — Instalación detallada
- [THEMES_GUIDE.md](THEMES_GUIDE.md) — Guía de temas
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) — Integración con fase1.py / OLED
- [COMPATIBILIDAD.md](COMPATIBILIDAD.md) — Compatibilidad multiplataforma
- [IDEAS_EXPANSION.md](IDEAS_EXPANSION.md) — Roadmap y backlog
- [INDEX.md](INDEX.md) — Índice completo

---

## 📊 Estadísticas del Proyecto

| Métrica | v4.0 | v4.1 |
|---------|------|------|
| Versión | 4.0 | **4.2** |
| Archivos Python | 73 | **79** |
| Ventanas | 27 | **31** |
| Temas | 15 | 15 |
| Badges en menú | 12 | **13** |
| Servicios background | 16 | **20** |
| Módulos ui/main_* | 5 | 5 |
| Documentos | 9 | **10** |

---

## Changelog

### **v4.2** - 2024 ⭐ ACTUAL

- ✅ **NUEVO**: **Service Watchdog** — monitor críticos systemd w/ text entries precisas + debounce, [SERVICE_WATCHDOG.md](SERVICE_WATCHDOG.md)
- ✅ **NUEVO**: Control de Audio ALSA (`AudioService` + `AudioWindow`) — volumen, mute, VU meter, selector control
- ✅ **NUEVO**: Widget de Clima (`WeatherService` + `WeatherWindow`) — Open-Meteo, AQI, drill-down, badge lluvia, fondo dinámico WMO
- ✅ **NUEVO**: Escáner I²C (`I2CMonitor` + `I2CWindow`) — smbus2 solo lectura, cards por bus, badge hex por dispositivo
- ✅ **NUEVO**: Monitor/Control GPIO (`GPIOMonitor` + `GPIOWindow`) — INPUT/OUTPUT/PWM, toggle LIBRE/CONTROLANDO, persistencia config en `local_settings.py`
- ✅ **NUEVO**: `config/local_settings_io.py` — módulo compartido lectura/escritura de `local_settings.py`, API `read()` / `write()` / `update_params()`

### **v4.0** - 2026-03-05

- ✅ **NUEVO**: Menú por pestañas con scroll horizontal táctil — 6 pestañas, ancho fijo 130px táctil
- ✅ **NUEVO**: `WindowLifecycleManager` (`ui/window_lifecycle.py`) — elimina 27 métodos `open_*`
- ✅ **NUEVO**: `BadgeManager` (`ui/main_badges.py`)
- ✅ **NUEVO**: `UpdateLoop` (`ui/main_update_loop.py`)
- ✅ **NUEVO**: `main_system_actions.py`
- ✅ **REFACTOR**: `main_window.py` 891 → 451 líneas (−49%)
- ✅ **REFACTOR**: `WindowManager` — patrón callback
- ✅ **REFACTOR**: `config/settings.py → class UI` — pestañas como configuración pura

### **v3.8** - 2026-03-XX
- ✅ Monitor WiFi, Monitor SSH, Editor de Configuración
- ✅ Refactor: `crontab_service.py` y `camera_service.py` a `core/`
- ✅ Fix `RuntimeError` al salir — `StringVar`/`IntVar` con `master=` explícito

### **v3.7** - 2026-03-02
- ✅ Gestor Crontab, fix grab modal, `make_entry()`, soporte dual-Pi

### **v3.6.5** - 2026-02-XX
- ✅ Gestor de Botones (`ButtonManagerWindow` + `WindowManager`)

### **v3.6** - 2026-02-XX
- ✅ Servicios Dashboard (`ServicesManagerWindow`)

### **v3.5** - 2026-02-XX
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

### v1.0 - 2025-01
- Release inicial

---

## Licencia

MIT License

---

## Agradecimientos

CustomTkinter · psutil · matplotlib · Ookla Speedtest CLI · Homebridge · Pi-hole · Raspberry Pi Foundation
