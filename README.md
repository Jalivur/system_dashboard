# 🖥️ Sistema de Monitoreo y Control - Dashboard v3.8

Sistema completo de monitoreo y control para Raspberry Pi con interfaz gráfica DSI, control de ventiladores PWM, temas personalizables, histórico de datos, gestión avanzada del sistema, integración con Homebridge, alertas externas por Telegram, escáner de red local, integración Pi-hole, gestor VPN, control de brillo, pantalla de resumen, LEDs RGB inteligentes, alertas de audio con voz TTS, cámara con OCR, SMART extendido de NVMe, monitor WiFi, monitor SSH y editor de configuración local.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![Version](https://img.shields.io/badge/Version-3.8-orange.svg)]()

---

## ✨ Características Principales

### 🖥️ **Monitoreo Completo del Sistema**
- **CPU**: Uso en tiempo real, frecuencia, gráficas históricas
- **RAM**: Memoria usada/total, porcentaje, visualización dinámica
- **Temperatura**: Monitoreo de CPU con alertas por color
- **Disco**: Espacio usado/disponible, temperatura NVMe, I/O en tiempo real

### 🪟 **UI Unificada con Header Táctil**
- **Header en todas las ventanas**: título + status dinámico + botón ✕ (52×42px táctil)
- **Status en tiempo real** en el header: CPU/RAM/Temp (Monitor Placa), Disco/NVMe (Monitor Disco), interfaz/velocidades (Monitor Red)
- **Botón ✕ táctil** optimizado para pantalla DSI de 4,5" sin teclado
- Función `make_window_header()` centralizada en `ui/styles.py`

### 🌡️ **Control Inteligente de Ventiladores**
- **5 Modos**: Auto (curva), Manual, Silent (30%), Normal (50%), Performance (100%)
- **Curvas personalizables**: Define hasta 8 puntos temperatura-PWM
- **Servicio background**: Funciona incluso con ventana cerrada
- **Visualización en vivo**: Gráfica de curva activa y PWM actual

### 🌐 **Monitor de Red Avanzado**
- **Tráfico en tiempo real**: Download/Upload con gráficas
- **Auto-detección**: Interfaz activa (eth0, wlan0, tun0)
- **Lista de IPs**: Todas las interfaces con iconos por tipo
- **Speedtest integrado**: CLI oficial de Ookla (JSON nativo, resultados en MB/s reales)
- **Status en header**: interfaz activa + velocidades actuales

### 󰖩 **Monitor WiFi** *(v3.8)*
- **Señal en tiempo real**: dBm, calidad de enlace, SSID, bitrate
- **Barras visuales** de señal (▂▄▆█) y gráfica histórica
- **Tráfico WiFi**: RX/TX con gráficas independientes
- Servicio daemon `WiFiMonitor` en `core/wifi_monitor.py`

### **Monitor SSH** *(v3.8)*
- **Sesiones activas**: lista en tiempo real con IP de origen y hora de conexión
- **Historial de sesiones**: con duración formateada y detección de cortes
- **Textos legibles**: `pts/0` → `Sesión 1`, IPs locales etiquetadas, duraciones en `1h 30min`
- Servicio daemon `SSHMonitor` en `core/ssh_monitor.py`

### 🔧 **Editor de Configuración** *(v3.8)*
- **Edita `local_settings.py`** por máquina sin tocar `settings.py`
- **Parámetros editables**: pantalla (DSI_X/Y), tiempos, umbrales CPU/Temp/RAM/Red, parámetros de red
- **Iconos editables**: todos los `Icons.*` con preview en tiempo real del nuevo glifo
- **Carga diferida**: sección de iconos se construye en lotes para no bloquear la UI
- **Merge inteligente**: guardar un cambio no sobreescribe los anteriores
- **Guardar y reiniciar** en un solo click

### 🖧 **Escáner de Red Local**
- **Escaneo con arp-scan**: Detecta todos los dispositivos activos en la red local
- **Información por dispositivo**: IP, MAC y fabricante (OUI lookup)
- **Auto-refresco cada 60s** en background sin bloquear la UI
- **Sudoers preconfigurado**: `usuario ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan`

### 🕳️ **Integración Pi-hole v6**
- **API v6 nativa**: autenticación por sesión (`POST /api/auth` → sid)
- **Estadísticas en tiempo real**: consultas totales, bloqueadas, porcentaje de bloqueo, clientes activos
- **Renovación automática de sesión** y logout limpio al parar
- **Badge en menú**: 🔴 si Pi-hole está offline

### 📲 **Alertas Externas por Telegram**
- **Sin dependencias nuevas**: usa `urllib` de la stdlib de Python
- **Métricas monitorizadas**: temperatura, CPU, RAM, disco y servicios fallidos
- **Anti-spam inteligente**: edge-trigger + sustain de 60s
- **Reseteo automático**: cuando la condición baja del umbral

### 🔔 **Historial de Alertas**
- **Registro persistente**: guarda en `data/alert_history.json` cada alerta enviada a Telegram
- **Máximo 100 entradas** (FIFO)
- **Ventana dedicada**: tarjetas con franja de color lateral (naranja=aviso, rojo=crítico)

### 🏠 **Integración Homebridge Extendida**
- **5 tipos de dispositivo**: switch/enchufe, luz regulable, termostato, sensor temperatura/humedad, persiana/estor
- **CTkSwitch táctil** (90×46px)
- **Tarjetas adaptativas** por tipo de dispositivo
- **Autenticación JWT** con renovación automática en 401
- **3 badges en el menú**: offline (🔴), encendidos (🟠), con fallo (🔴)

### ⚙️ **Monitor de Procesos**
- Lista en tiempo real: Top 20 procesos con CPU/RAM
- Búsqueda inteligente, filtros, terminar procesos con confirmación

### ⚙️ **Monitor de Servicios systemd**
- Gestión completa: Start/Stop/Restart, estado visual, autostart, logs en tiempo real
- Caché en background: sondeo cada 10s, `is-enabled` en llamada batch

### ⚙️ **Servicios Dashboard** *(v3.5/v3.6)*
- **ServiceRegistry**: registro centralizado de todos los servicios del dashboard
- **ServicesManagerWindow**: activar/desactivar servicios background desde la UI
- **Persistencia**: configuración guardada en `config/services.json`

### 🔧 **Gestor de Botones del Menú** *(v3.6.5)*
- **ButtonManagerWindow**: mostrar/ocultar botones del menú principal
- **Persistencia**: configuración guardada en `config/services.json` (sección `ui`)
- Ideal para simplificar el menú en cada máquina según sus capacidades

### 🕐 **Gestor de Crontab** *(v3.7)*
- **Ver, añadir, editar y eliminar** entradas del crontab
- **Selector de usuario**: `usuario` / `root`
- **Accesos rápidos** de programación: @reboot, cada hora, cada día, etc.
- **Preview legible** de la expresión cron

### 📊 **Histórico de Datos**
- Recolección automática cada 5 minutos en background (SQLite)
- 8 gráficas (CPU, RAM, Temperatura, Red, Disco, PWM) en 24h, 7d, 30d
- Estadísticas, detección de anomalías, exportación CSV

### 󱇰 **Monitor USB**
- Detección automática, separación inteligente, expulsión segura

###  **Monitor de Disco**
- Particiones, temperatura NVMe, velocidad I/O
- SMART extendido: horas de uso, ciclos, TB escritos/leídos, % vida útil

### 󱓞 **Lanzadores de Scripts**
- Terminal integrada, layout en grid, confirmación previa

### 󰆧 **Actualizaciones del Sistema**
- Verificación al arranque, caché 12h, terminal integrada

### 󰔎 **15 Temas Personalizables**
- Cambio con un clic, paletas completas, preview en vivo

### 📊 **Resumen del Sistema / Pantalla de Reposo**
- Vista unificada: CPU, RAM, Temperatura, Disco, Red y Servicios
- Fila Pi-hole, refresco cada 2s

### 💡 **Control de Brillo de Pantalla**
- Detección automática del método: `sysfs`, `wlr-randr` (Wayland) o `xrandr` (X11)
- Slider táctil, modo ahorro, encendido/apagado, persistencia

### 🔒 **Gestor de Conexiones VPN**
- Estado en tiempo real, badge en menú, conectar/desconectar con terminal en vivo
- Compatible con WireGuard y OpenVPN

### 💡 **Control LEDs RGB**
- 6 modos: auto, apagado, color fijo, secuencial, respiración, arcoíris
- Sin destellos, sliders RGB, preview en tiempo real

### 🔊 **Alertas de Audio**
- Voz TTS en español con `espeak-ng` + tono sintético por nivel
- 11 archivos .wav, lógica correcta por nivel y métrica

### 📷 **Cámara + Escáner OCR**
- Cámara OV5647 via `rpicam-still`, resoluciones hasta 2592×1944
- OCR con Tesseract local, preprocesado PIL, guarda `.txt` y `.md`

### 🌡️ **Hardware FNK0100K extendido**
- Temperatura del chasis, fan duty real, NVMe SMART extendido
- Arquitectura sin acoplamiento via `hardware_state.json`

---

## 🖥️ Soporte Multi-máquina

El dashboard soporta múltiples Raspberry Pi con configuraciones distintas sin tocar git.

### Config por máquina
`config/settings.py` al final carga opcionalmente:
```python
try:
    from config.local_settings import *
except ImportError:
    pass
```
`config/local_settings.py` está en `.gitignore` — cada máquina tiene el suyo.
El **Editor de Configuración** genera y mantiene este fichero desde la propia UI.

### Pi 5 (pantalla DSI física + Wayland)
- Compositor: **labwc** sobre Wayland
- Acceso remoto: **wayvnc** (`wayvnc --output=DSI-2 0.0.0.0 5901`)
- Resolución DSI: 800×480 en posición 1124,1080
- Idle desactivado: `gsettings set org.gnome.desktop.session idle-delay 0`

### Pi 3B+ (sin pantalla física + X11)
- Display virtual `:1` con **Xvfb** (resolución configurable)
- Dashboard corre en `:1`, aislado del escritorio XFCE en `:0`
- Acceso remoto: x11vnc en puerto `5901` sobre `:1`
- XFCE/RealVNC sigue en `:0` puerto `5900` sin cambios
- `local_settings.py`: `DSI_X=0, DSI_Y=0, DSI_WIDTH=1024, DSI_HEIGHT=762`

---

## 📦 Instalación

### Requisitos del Sistema
- **Hardware**: Raspberry Pi 3/4/5
- **OS**: Raspberry Pi OS (Bullseye/Bookworm) o Kali Linux
- **Pantalla**: Touchscreen DSI 4,5" (800×480) o HDMI
- **Python**: 3.8 o superior

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
# 1. Dependencias del sistema
sudo apt-get update
sudo apt-get install -y lm-sensors usbutils udisks2 smartmontools arp-scan wireless-tools

# 2. CLI oficial de Ookla (speedtest)
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest

# 3. Detectar sensores
sudo sensors-detect --auto

# 4. Dependencias Python
pip3 install --break-system-packages -r requirements.txt

# 5. Sudoers para arp-scan y smartctl
echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan" | sudo tee /etc/sudoers.d/arp-scan
echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/bin/smartctl"  | sudo tee /etc/sudoers.d/smartctl

# 6. Hardware FNK0100K — cámara y OCR (opcional)
sudo apt install rpicam-apps tesseract-ocr tesseract-ocr-spa espeak-ng
pip install pytesseract --break-system-packages
sudo usermod -aG video $(whoami)

# 7. Generar archivos de audio (opcional)
python3 scripts/generate_sounds.py

# 8. Ejecutar
python3 main.py
```

### Alternativa con Entorno Virtual

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
```

---

## 🏠 Configuración de Homebridge

```env
HOMEBRIDGE_HOST=192.168.1.X
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña
```

> Activa el **Insecure Mode** en Homebridge para que la API permita acceder a los accesorios.

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

### Umbrales por defecto

| Métrica  | Aviso (🟠) | Crítico (🔴) |
|----------|-----------|------------|
| Temperatura | 60°C | 75°C |
| CPU | 60% | 85% |
| RAM | 65% | 85% |
| Disco | — | — |
| Servicios | — | cualquier FAILED |

> Los umbrales son editables desde el **Editor de Configuración** sin reiniciar git.

---

## 󰍜 Menú Principal (29 botones)

```
┌─────────────────────────────────────┐
│  Info Hardware   │  Control          │
│                  │  Ventiladores     │
├──────────────────┼───────────────────┤
│  LEDs RGB        │  Monitor          │
│                  │  Placa            │
├──────────────────┼───────────────────┤
│  Monitor         │  Monitor          │
│  Red             │  USB              │
├──────────────────┼───────────────────┤
│  Monitor         │  Lanzadores       │
│  Disco           │                   │
├──────────────────┼───────────────────┤
│  Monitor         │  Monitor          │
│  Procesos        │  Servicios        │
├──────────────────┼───────────────────┤
│  Servicios       │  Gestor           │
│  Dashboard       │  Crontab          │
├──────────────────┼───────────────────┤
│  Gestor          │  Histórico        │
│  de Botones      │  Datos            │
├──────────────────┼───────────────────┤
│  Actualizaciones │  Homebridge       │
├──────────────────┼───────────────────┤
│  Visor de Logs   │  🖧 Red Local     │
├──────────────────┼───────────────────┤
│  🕳 Pi-hole      │  🔒 Gestor VPN   │
├──────────────────┼───────────────────┤
│  🔔 Historial    │  💡 Brillo        │
│  Alertas         │  Pantalla         │
├──────────────────┼───────────────────┤
│  📊 Resumen      │  📷 Cámara        │
│  Sistema         │                   │
├──────────────────┼───────────────────┤
│  Cambiar Tema    │   Monitor SSH     │
├──────────────────┼───────────────────┤
│  󰖩 Monitor WiFi │  🔧 Editor Config  │
├──────────────────┼───────────────────┤
│  Reiniciar       │  Salir            │
└──────────────────┴───────────────────┘
```

### Las 27 Ventanas

1. **Info Hardware** - Información detallada del hardware
2. **Control Ventiladores** - Configura modos y curvas PWM
3. **LEDs RGB** - Control LEDs RGB GPIO Board con 6 modos *(v3.4)*
4. **Monitor Placa** - CPU, RAM, temperatura + chasis + fan duty *(v3.4)*
5. **Monitor Red** - Tráfico, speedtest Ookla, interfaces e IPs
6. **Monitor USB** - Dispositivos y expulsión segura
7. **Monitor Disco** - Espacio, temperatura NVMe, I/O + SMART *(v3.4)*
8. **Lanzadores** - Scripts con terminal en vivo
9. **Monitor Procesos** - Gestión avanzada de procesos
10. **Monitor Servicios** - Control de servicios systemd
11. **Servicios Dashboard** - Activar/desactivar servicios background *(v3.5/v3.6)*
12. **Gestor Crontab** - Ver/añadir/editar/eliminar entradas cron *(v3.7)*
13. **Gestor de Botones** - Visibilidad de botones del menú *(v3.6.5)*
14. **Histórico Datos** - Visualización de métricas históricas con exportación CSV
15. **Actualizaciones** - Gestión de paquetes del sistema
16. **Homebridge** - Control de 5 tipos de dispositivos HomeKit
17. **Visor de Logs** - Visualización y exportación del log del dashboard
18. **🖧 Red Local** - Escáner arp-scan con IP, MAC y fabricante *(v3.2)*
19. **🕳 Pi-hole** - Estadísticas de bloqueo DNS en tiempo real *(v3.2)*
20. **🔒 Gestor VPN** - Estado en tiempo real + conectar/desconectar *(v3.3)*
21. **🔔 Historial Alertas** - Registro persistente de alertas Telegram *(v3.2)*
22. **💡 Brillo Pantalla** - Control de brillo DSI con modo ahorro *(v3.3)*
23. **📊 Resumen Sistema** - Vista unificada de todas las métricas *(v3.3)*
24. **📷 Cámara / Escáner OCR** - Captura + OCR con Tesseract *(v3.4)*
25. **Cambiar Tema** - Selecciona entre 15 temas
26. **Monitor SSH** - Sesiones activas e historial SSH *(v3.8)*
27. **Monitor WiFi** - Señal, calidad, tráfico WiFi *(v3.8)*
28. **Editor Config** - Edita `local_settings.py` desde la UI *(v3.8)*

---

## 󰔎 Temas Disponibles

| Tema | Colores | Estilo |
|------|---------|--------|
| **Cyberpunk** | Cyan + Verde | Original neón |
| **Matrix** | Verde brillante | Película Matrix |
| **Sunset** | Naranja + Púrpura | Atardecer cálido |
| **Ocean** | Azul + Aqua | Océano refrescante |
| **Dracula** | Púrpura + Rosa | Elegante oscuro |
| **Nord** | Azul hielo | Minimalista nórdico |
| **Tokyo Night** | Azul + Púrpura | Noche de Tokio |
| **Monokai** | Cyan + Verde | IDE clásico |
| **Gruvbox** | Naranja + Beige | Retro cálido |
| **Solarized** | Azul + Cyan | Científico |
| **One Dark** | Azul claro | Atom editor |
| **Synthwave** | Rosa + Verde | Neón 80s |
| **GitHub Dark** | Azul GitHub | Profesional |
| **Material** | Azul material | Google Design |
| **Ayu Dark** | Azul cielo | Minimalista |

---

## 📊 Arquitectura del Proyecto

```
system_dashboard/
├── config/
│   ├── settings.py                 # Constantes globales + clase Icons
│   ├── button_labels.py            # Labels de botones (fuente única de verdad)
│   ├── themes.py                   # 15 temas pre-configurados
│   ├── services.json               # Config servicios y UI (auto-generado, en .gitignore)
│   └── local_settings.py           # Overrides por máquina (en .gitignore)
├── core/
│   ├── fan_controller.py
│   ├── fan_auto_service.py
│   ├── system_monitor.py
│   ├── network_monitor.py
│   ├── network_scanner.py
│   ├── disk_monitor.py
│   ├── process_monitor.py
│   ├── service_monitor.py
│   ├── service_registry.py         # Registro centralizado de servicios (v3.5)
│   ├── update_monitor.py
│   ├── homebridge_monitor.py
│   ├── pihole_monitor.py
│   ├── alert_service.py
│   ├── led_service.py
│   ├── hardware_monitor.py
│   ├── audio_alert_service.py
│   ├── display_service.py
│   ├── vpn_monitor.py
│   ├── crontab_service.py          # Servicio crontab (v3.7)
│   ├── camera_service.py           # Servicio cámara/OCR (v3.7)
│   ├── ssh_monitor.py              # Monitor sesiones SSH (v3.8)
│   ├── wifi_monitor.py             # Monitor conexión WiFi (v3.8)
│   ├── data_logger.py
│   ├── data_analyzer.py
│   ├── data_collection_service.py
│   └── cleanup_service.py
├── ui/
│   ├── main_window.py
│   ├── styles.py                   # make_window_header(), make_futuristic_button(),
│   │                               # make_homebridge_switch(), make_entry(), StyleManager
│   ├── window_manager.py           # Gestión de visibilidad de botones
│   ├── widgets/
│   │   ├── graphs.py
│   │   └── dialogs.py              # custom_msgbox, confirm_dialog, terminal_dialog
│   └── windows/
│       ├── monitor.py, network.py, usb.py, disk.py
│       ├── process_window.py, service.py, history.py
│       ├── update.py, fan_control.py
│       ├── launchers.py, theme_selector.py
│       ├── homebridge.py
│       ├── log_viewer.py
│       ├── network_local.py
│       ├── pihole_window.py
│       ├── alert_history.py
│       ├── vpn_window.py
│       ├── display_window.py
│       ├── overview.py
│       ├── led_window.py
│       ├── camera_window.py
│       ├── services_manager_window.py  # Gestión servicios dashboard (v3.6)
│       ├── button_manager_window.py    # Visibilidad botones menú (v3.6.5)
│       ├── crontab_window.py           # Gestor crontab (v3.7)
│       ├── ssh_window.py               # Monitor SSH (v3.8)
│       ├── wifi_window.py              # Monitor WiFi (v3.8)
│       ├── config_editor_window.py     # Editor configuración local (v3.8)
│       └── __init__.py
├── utils/
│   ├── file_manager.py
│   ├── system_utils.py
│   └── logger.py
├── data/                            # Auto-generado al ejecutar
│   ├── fan_state.json, fan_curve.json, theme_config.json
│   ├── led_state.json
│   ├── hardware_state.json
│   ├── alert_history.json
│   ├── display_state.json
│   ├── history.db
│   ├── logs/dashboard.log
│   ├── photos/
│   ├── scans/
│   └── exports/
│       ├── csv/
│       ├── logs/
│       └── screenshots/
├── scripts/
│   ├── sounds/                     # 11 archivos .wav
│   └── generate_sounds.py
├── .env                             # Credenciales (NO en git)
├── .env.example
├── install_system.sh
├── install.sh
├── main.py
└── requirements.txt
```

---

## 🔧 Configuración

### `config/settings.py`

```python
DSI_WIDTH = 800
DSI_HEIGHT = 480
DSI_X = 0
DSI_Y = 0

CPU_WARN = 60
CPU_CRIT = 85
TEMP_WARN = 60
TEMP_CRIT = 75
RAM_WARN = 65
RAM_CRIT = 85
```

### `config/local_settings.py` (por máquina, NO en git)

Generado y mantenido por el **Editor de Configuración**. Ejemplo manual:

```python
# Ejemplo Pi 3B+ con Xvfb
DSI_X = 0
DSI_Y = 0
DSI_WIDTH = 1024
DSI_HEIGHT = 762

# Override de icono
from config.settings import Icons
Icons.WIFI = "\U000F05A9"
```

### `config/services.json` (auto-generado, NO en git)

Controla qué servicios arrancan y qué botones son visibles. Se gestiona desde **Servicios Dashboard** y **Gestor de Botones**. Secciones:

- `"services"`: `true`/`false` por cada servicio background
- `"ui"`: `true`/`false` por cada botón del menú

---

## 📋 Sistema de Logging

```bash
tail -f data/logs/dashboard.log
grep ERROR data/logs/dashboard.log
grep "$(date +%Y-%m-%d)" data/logs/dashboard.log
```

---

## 📈 Rendimiento

- **Uso CPU**: ~5-10% en idle
- **Uso RAM**: ~100-150 MB
- **Actualización UI**: 2 segundos — solo lectura de caché
- **Threads background**: 16
- **Log**: máx. 2MB con rotación automática

---

## 🔧 Troubleshooting

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto && sudo systemctl restart lm-sensors` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Ventiladores no responden | `sudo python3 main.py` |
| Speedtest falla | Instalar CLI oficial Ookla |
| USB no expulsa | `sudo apt install udisks2` |
| Homebridge no conecta | Verificar `.env` y que Insecure Mode esté activo |
| Red Local no escanea | `sudo apt install arp-scan` y configurar sudoers |
| Pi-hole no conecta | Verificar `.env`; solo compatible con v6 |
| VPN badge siempre rojo | Verificar que la interfaz (`tun0`/`wg0`) coincide en `vpn_monitor.py` |
| Brillo no disponible | Instalar `wlr-randr` si Wayland |
| No puedo escribir en entries (VNC) | Verificar que se usa `make_entry()` de `ui/styles.py` |
| Foco perdido tras inactividad (Wayland) | `gsettings set org.gnome.desktop.session idle-delay 0` |
| Dashboard no visible por VNC en Pi 5 | Usar `wayvnc --output=DSI-2 0.0.0.0 5901` |
| LEDs con destellos | Ver `FIX_LED_DESTELLOS.md` |
| Audio no suena | `aplay -l` → verificar dispositivo HDMI |
| Cámara no encontrada | `sudo apt install rpicam-apps` + `sudo usermod -aG video $(whoami)` |
| SMART muestra N/D | `sudo smartctl -A /dev/nvme0` + revisar sudoers |
| WiFi no muestra datos | Verificar que `iwconfig` está disponible (`sudo apt install wireless-tools`) |
| SSH monitor vacío | Verificar que `who` y `last` funcionan en el sistema |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 📚 Documentación

- [QUICKSTART.md](QUICKSTART.md) — Inicio rápido
- [INSTALL_GUIDE.md](INSTALL_GUIDE.md) — Instalación detallada
- [THEMES_GUIDE.md](THEMES_GUIDE.md) — Guía de temas
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) — Integración con OLED
- [INDEX.md](INDEX.md) — Índice completo

---

## 📊 Estadísticas del Proyecto

| Métrica | v3.7 | v3.8 |
|---------|------|------|
| Versión | 3.7 | **3.8** |
| Archivos Python | 63 | **68** |
| Ventanas | 24 | **27** |
| Temas | 15 | 15 |
| Servicios background | 14 | **16** |
| Badges en menú | 12 | 12 |
| Documentos | 9 | 9 |

---

## Changelog

### **v3.8** - 2026-03-XX ⭐ ACTUAL
- ✅ **NUEVO**: Monitor WiFi — `WiFiMonitor` (core) + `WiFiWindow` (ui): señal dBm, calidad, SSID, bitrate, tráfico RX/TX, gráficas históricas
- ✅ **NUEVO**: Monitor SSH — `SSHMonitor` (core) + `SSHWindow` (ui): sesiones activas con IP/hora, historial con duración legible, textos humanizados (`pts/0` → `Sesión 1`)
- ✅ **NUEVO**: Editor de Configuración — `ConfigEditorWindow`: edita `local_settings.py` por máquina desde la UI, parámetros numéricos + iconos con preview en tiempo real, merge inteligente, guardar y reiniciar
- ✅ **REFACTOR**: `crontab_service.py` y `camera_service.py` extraídos de UI a `core/` — separación arquitectónica completa
- ✅ **FIX**: `RuntimeError` al salir — `StringVar`/`IntVar` instanciados con `master=` explícito en `main_window.py`, `homebridge.py` y `main.py`
- ✅ **MEJORA**: `ServicesManagerWindow` — iconos migrados a `Icons.*`, entradas SSH y WiFi añadidas a `_DEFINITIONS`
- ✅ **MEJORA**: `services.json` — nuevas entradas `ssh_monitor`, `wifi_monitor` en `services`; `ssh_window`, `wifi_window`, `config_editor_window` en `ui`

### **v3.7** - 2026-03-02
- ✅ **NUEVO**: Gestor Crontab — `CrontabWindow` con ver/añadir/editar/eliminar entradas, selector de usuario (usuario/root), accesos rápidos de programación, preview legible de expresión cron
- ✅ **FIX**: `grab_release()` garantizado al cerrar popups modales
- ✅ **FIX**: `make_entry()` en `ui/styles.py` — fuerza foco al widget interno en VNC
- ✅ **MEJORA**: Soporte dual-Pi sin tocar git — `config/local_settings.py`
- ✅ **MEJORA**: Pi 3B+ Xvfb + Pi 5 Wayland documentados

### **v3.6.5** - 2026-02-XX
- ✅ **NUEVO**: Gestor de Botones — `ButtonManagerWindow`
- ✅ **NUEVO**: `WindowManager` en `ui/window_manager.py`

### **v3.6** - 2026-02-XX
- ✅ **NUEVO**: Servicios Dashboard — `ServicesManagerWindow`

### **v3.5** - 2026-02-XX
- ✅ **NUEVO**: `ServiceRegistry` — registro centralizado de servicios

### **v3.4** - 2026-02-27
- ✅ Control LEDs RGB, temperatura chasis, alertas audio, cámara OCR, SMART NVMe extendido

### **v3.3** - 2026-02-27
- ✅ Resumen Sistema, control brillo DSI, gestor VPN

### **v3.2** - 2026-02-27
- ✅ Escáner red local, Pi-hole v6, historial alertas

### **v3.1** - 2026-02-26
- ✅ Alertas Telegram, Homebridge extendido (5 tipos)

### **v3.0** - 2026-02-26
- ✅ Visor de Logs, exports organizados, fix grab_set FanControl

### v2.x
- Monitor completo, servicios systemd, histórico SQLite, 15 temas, badges, logging

### v1.0 - 2025-01
- Release inicial

---

## Licencia

MIT License

---

## Agradecimientos

CustomTkinter · psutil · matplotlib · Ookla Speedtest CLI · Homebridge · Pi-hole · Raspberry Pi Foundation
