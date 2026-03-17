# 📚 Índice de Documentación - System Dashboard v4.2

---

## 🚀 Documentos Esenciales

**[README.md](README.md)** ⭐ — Documentación completa v4.1. **Empieza aquí.**

**[QUICKSTART.md](QUICKSTART.md)** ⚡ — Instalación y ejecución en 5 minutos.

---

## 📖 Guías por tema

### 🎨 Personalización
**[THEMES_GUIDE.md](THEMES_GUIDE.md)** — 15 temas, crear personalizados.

### 🔧 Instalación
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — RPi OS, Kali, venv, script automático.

### 🏠 Homebridge
Configuración: ver sección en README.md.
5 tipos: `switch`, `light`, `thermostat`, `sensor`, `blind`.

### 🕳️ Pi-hole (v3.2)
Solo compatible con **Pi-hole v6**.
Añadir `PIHOLE_HOST`, `PIHOLE_PORT`, `PIHOLE_PASSWORD` al `.env`.

### 🖧 Red Local (v3.2)
Instalar: `sudo apt install arp-scan`.
Sudoers: `usuario ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan`.

### 📲 Alertas Telegram
Configurar `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID` en `.env`.

### 🤝 Integración con fase1.py
**[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** — Compartir estado fans/LEDs via JSON, OLED.

### 💡 Ideas y Expansión
**[IDEAS_EXPANSION.md](IDEAS_EXPANSION.md)** — Roadmap v4.2+, backlog, cobertura por módulo.

### 🖥️ Multi-Pi (v3.7)
Crear `config/local_settings.py` (en `.gitignore`) con los valores de `DSI_X/Y/WIDTH/HEIGHT` para cada máquina.
El **Editor de Configuración** *(v3.8)* permite editar este fichero directamente desde la UI sin SSH.
- **Pi 5 Wayland**: `wayvnc --output=DSI-2 0.0.0.0 5901` + `gsettings set org.gnome.desktop.session idle-delay 0`
- **Pi 3B+ Xvfb**: display virtual `:1`, VNC puerto `5901`, resolución configurable

### 🗂️ Menú por Pestañas (v4.0)
Pestañas definidas en `config/settings.py → class UI`:
- `MENU_COLUMNS` — número de columnas de botones
- `MENU_TABS` — lista de `(clave, icono, label, [claves_BL])`
Añadir una pestaña nueva es añadir una línea a `MENU_TABS`.

### ⚡ GPIO Monitor/Control (v4.1)
- Arranque por defecto en modo **LIBRE** — no reclama ningún pin.
- Pulsar **"Tomar control"** para reclamar pines con gpiozero.
- Pulsar **"Liberar GPIO"** antes de lanzar scripts externos que usen los mismos pines.
- Pines reservados por fase1.py: {2, 3, 12, 13, 14, 15, 18, 19} — nunca disponibles.
- Configuración de pines persistida automáticamente en `local_settings.py`.

---

## 📋 Archivos de configuración

| Archivo | En git | Gestiona |
|---------|--------|---------|
| `config/settings.py` | ✅ | Constantes globales, Icons, UI (pestañas), LAUNCHERS |
| `config/button_labels.py` | ✅ | Labels de botones (fuente única de verdad) |
| `config/themes.py` | ✅ | 15 temas |
| `config/local_settings_io.py` | ✅ | Módulo compartido lectura/escritura local_settings.py |
| `config/services.json` | ❌ | Estado servicios + visibilidad botones UI |
| `config/local_settings.py` | ❌ | Overrides por máquina (editable via Config Editor) |
| `.env` | ❌ | Credenciales (Homebridge, PiHole, Telegram, VPN) |

---

## 🗂️ Estructura de documentos v4.1

```
📚 Documentación/
├── README.md                         ⭐ Principal v4.1
├── QUICKSTART.md                     ⚡ Inicio rápido
├── INDEX.md                          📑 Este archivo
├── REQUIREMENTS.md                   📋 Requisitos
├── INSTALL_GUIDE.md                  🔧 Instalación
├── THEMES_GUIDE.md                   🎨 Temas
├── INTEGRATION_GUIDE.md              🤝 Integración fase1
├── IDEAS_EXPANSION.md                💡 Roadmap v4.2+
└── COMPATIBILIDAD.md                 🌐 Compatibilidad
```

---

## 🎯 Flujo de lectura recomendado

**Usuario nuevo:**
1. README.md → sección Características
2. QUICKSTART.md → instalar y ejecutar
3. Explorar las 31 ventanas 🎉

**Usuario avanzado / configurar integraciones:**
1. README.md completo
2. Sección Homebridge → `.env` + Insecure Mode
3. Sección Pi-hole → `.env` + compatibilidad v6
4. Sección Telegram → `.env`
5. Sección Multi-Pi → `local_settings.py` + wayvnc / Xvfb
6. **Editor de Configuración** *(v3.8)* → ajustar umbrales e iconos desde la UI

**Desarrollador / extender:**
1. README.md sección Arquitectura
2. `config/settings.py → class UI` → entender estructura de pestañas
3. `ui/window_lifecycle.py` → patrón de registro de ventanas
4. `ui/styles.py` → `make_window_header()` y `make_entry()` para nuevas ventanas
5. `core/service_registry.py` → registrar nuevos servicios
6. `config/local_settings_io.py` → persistir config de nuevos módulos
7. IDEAS_EXPANSION.md → ver qué se puede añadir en v4.2

---

## 🔍 Buscar por problema

| Problema | Dónde mirar |
|----------|-------------|
| No arranca | QUICKSTART.md → Problemas Comunes |
| VPN badge siempre rojo | README.md Troubleshooting (interfaz `tun0`/`wg0`) |
| Pi-hole no conecta | README.md Troubleshooting (solo v6) |
| Red Local no escanea | README.md Troubleshooting (arp-scan + sudoers) |
| No puedo escribir en entries (VNC) | README.md → `make_entry()` en `ui/styles.py` |
| Foco perdido tras inactividad (Pi 5) | `gsettings set org.gnome.desktop.session idle-delay 0` |
| Dashboard no visible por VNC en Pi 5 | `wayvnc --output=DSI-2 0.0.0.0 5901` |
| Configuración distinta por máquina | `config/local_settings.py` o Editor de Configuración |
| Homebridge no conecta | README.md Troubleshooting |
| Alertas Telegram no llegan | README.md sección Telegram / `.env` |
| SMART muestra N/D | Sudoers smartctl + `sudo smartctl -A /dev/nvme0` |
| Audio no suena | `aplay -l` → verificar dispositivo HDMI activo |
| Cámara no encuentra rpicam-still | `sudo apt install rpicam-apps` |
| WiFi no muestra datos | `sudo apt install wireless-tools` |
| SSH monitor vacío | Verificar que `who` y `last` funcionan en el sistema |
| I²C buses vacíos | Habilitar I²C en `raspi-config` |
| GPIO pin busy al arrancar | Pin ocupado por otro proceso — usar modo LIBRE |
| GPIO no libera en Pi 5 | Usar botón "Liberar GPIO" desde la ventana GPIO |
| Service Watchdog vacío | `systemctl list-units --type=service` verificar activos |
| Valores inválidos Watchdog | Clamp automático en Apply (1-10 umbral, 30-300s intervalo) |
| Ver errores | `grep ERROR data/logs/dashboard.log` |

---

## 📊 Estadísticas del proyecto v4.2

| Métrica | v4.0 | v4.2 |
|---------|------|------|
| Versión | 4.0 | **4.2** |
| Archivos Python | 73 | **79** |
| Ventanas | 27 | **31** |
| Temas | 15 | 15 |
| Badges en menú | 12 | **13** |
| Servicios background | 16 | **20** |
| Módulos ui/main_* | 5 | 5 |
| Documentos | 9 | 9 |

### Nuevos módulos en v4.2
- `core/audio_service.py` — `AudioService`: control ALSA sin thread
- `core/weather_service.py` — `WeatherService`: Open-Meteo + AQI + favoritos
- `core/i2c_monitor.py` — `I2CMonitor`: smbus2 solo lectura, daemon thread
- `core/gpio_monitor.py` — `GPIOMonitor`: gpiozero INPUT/OUTPUT/PWM, LIBRE/CONTROLANDO
- `config/local_settings_io.py` — módulo compartido persistencia `local_settings.py`
- `ui/windows/audio_window.py` — `AudioWindow`
- `ui/windows/weather_window.py` — `WeatherWindow`
- `ui/windows/i2c_window.py` — `I2CWindow`
- `ui/windows/gpio_window.py` — `GPIOWindow` + `_GPIOConfigDialog`
