# 📚 Índice de Documentación - System Dashboard v3.4

---

## 🚀 Documentos Esenciales

**[README.md](README.md)** ⭐ — Documentación completa v3.4. **Empieza aquí.**

**[QUICKSTART.md](QUICKSTART.md)** ⚡ — Instalación y ejecución en 5 minutos.

---

## 📖 Guías v3.4 (hardware FNK0100K)

**[GUIA_V34_HARDWARE_FNK0100K.md](GUIA_V34_HARDWARE_FNK0100K.md)** ⭐ — Guía maestra v3.4.
- Arquitectura completa (fase1.py ↔ JSONs ↔ dashboard)
- fase1.py modificado completo
- Todos los archivos nuevos con código

**[FIX_LED_DESTELLOS.md](FIX_LED_DESTELLOS.md)**
- Causa de los destellos en modos follow/breathing
- `apply_led_state()` con lógica edge — solo escribe I2C cuando cambia algo

**[INTEGRACION_MONITOR_HARDWARE.md](INTEGRACION_MONITOR_HARDWARE.md)**
- `monitor.py` completo con tarjeta temperatura chasis + fan duty real
- Patrón exacto que encaja con la estructura de `MonitorWindow`

---

## 📖 Guías v3.3

**[GUIA_DASHBOARD_RESUMEN.md](GUIA_DASHBOARD_RESUMEN.md)**
- Layout (grid 6 tarjetas + fila Pi-hole con 4 columnas)
- Fuentes de datos y umbrales de color

**[GUIA_BRILLO_DSI.md](GUIA_BRILLO_DSI.md)**
- Configuración real: `DSI_OUTPUT="DSI-2"`, backlight `11-0045`
- Diagnóstico, wlr-randr, permisos udev

**[GUIA_GESTOR_VPN.md](GUIA_GESTOR_VPN.md)**
- Scripts requeridos, interfaz tun0/wg0, sudoers

---

## 📖 Guías por tema

### 🎨 Personalización
**[THEMES_GUIDE.md](THEMES_GUIDE.md)** — 15 temas, crear personalizados.

### 🔧 Instalación
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — RPi OS, Kali, venv, script automático.

### ⚙️ Características avanzadas
**[PROCESS_MONITOR_GUIDE.md](PROCESS_MONITOR_GUIDE.md)** — Procesos, filtros, terminación.

**[SERVICE_MONITOR_GUIDE.md](SERVICE_MONITOR_GUIDE.md)** — Servicios systemd, start/stop, logs.

**[HISTORICO_DATOS_GUIDE.md](HISTORICO_DATOS_GUIDE.md)** — SQLite, matplotlib, exportación CSV.

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
**[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** — Compartir estado fans via JSON, OLED.

### 💡 Ideas y Expansión
**[IDEAS_EXPANSION.md](IDEAS_EXPANSION.md)** — Roadmap, backlog, cobertura por módulo.

---

## 📋 Archivos de soporte

| Archivo | Propósito |
|---------|-----------|
| `requirements.txt` | Dependencias Python |
| `REQUIREMENTS.md` | Requisitos detallados con sistema |
| `.env` | Credenciales (NO en git) |
| `.env.example` | Plantilla |
| `config/settings.py` | Constantes globales |
| `config/themes.py` | 15 temas |
| `scripts/generate_sounds.py` | Genera los 11 audios de alerta |
| `scripts/sounds/` | Archivos .wav (tono + voz TTS español) |
| `data/fan_state.json` | fase1 lee — modo y PWM del ventilador |
| `data/led_state.json` | fase1 lee — modo y color de los LEDs |
| `data/hardware_state.json` | fase1 escribe — temp chasis + fan duty real |
| `data/photos/` | Fotos capturadas con la cámara OV5647 |
| `data/scans/` | Escaneos OCR (.txt + .md) |

---

## 🗂️ Estructura de documentos v3.4

```
📚 Documentación/
├── README.md                         ⭐ Principal v3.4
├── QUICKSTART.md                     ⚡ Inicio rápido
├── INDEX.md                          📑 Este archivo
├── INSTALL_GUIDE.md                  🔧 Instalación
├── THEMES_GUIDE.md                   🎨 Temas
├── PROCESS_MONITOR_GUIDE.md          ⚙️ Procesos
├── SERVICE_MONITOR_GUIDE.md          🔧 Servicios
├── HISTORICO_DATOS_GUIDE.md          📊 Histórico
├── INTEGRATION_GUIDE.md              🤝 Integración fase1
├── IDEAS_EXPANSION.md                💡 Roadmap v3.5+
├── COMPATIBILIDAD.md                 🌐 Compatibilidad
├── REQUIREMENTS.md                   📋 Requisitos
├── GUIA_DASHBOARD_RESUMEN.md         📊 Resumen Sistema (v3.3)
├── GUIA_BRILLO_DSI.md                💡 Brillo DSI (v3.3)
├── GUIA_GESTOR_VPN.md                🔒 Gestor VPN (v3.3)
├── GUIA_V34_HARDWARE_FNK0100K.md     🔧 Hardware completo (v3.4)
├── FIX_LED_DESTELLOS.md              💡 Fix LEDs animados (v3.4)
└── INTEGRACION_MONITOR_HARDWARE.md   🌡️ Monitor chasis (v3.4)
```

---

## 🎯 Flujo de lectura recomendado

**Usuario nuevo:**
1. README.md → sección Características
2. QUICKSTART.md → instalar y ejecutar
3. Explorar las 21 ventanas 🎉

**Usuario avanzado / configurar integraciones:**
1. README.md completo
2. Sección Homebridge → `.env` + Insecure Mode
3. Sección Pi-hole → `.env` + compatibilidad v6
4. Sección Telegram → `.env` + `send_test()`
5. GUIA_GESTOR_VPN.md → scripts + interfaz

**Implementar v3.4 desde cero:**
1. GUIA_V34_HARDWARE_FNK0100K.md → leer arquitectura completa
2. Modificar fase1.py (Parte 1 de la guía)
3. Implementar features en orden: HardwareMonitor → LEDs → Audio → Cámara → SMART

**Fix destellos LEDs:**
1. FIX_LED_DESTELLOS.md → reemplazar `apply_led_state()` y añadir `_last_led_applied`

**Diagnóstico de brillo:**
1. GUIA_BRILLO_DSI.md → Paso 0

**Desarrollador / extender:**
1. README.md sección Arquitectura
2. `ui/styles.py` → `make_window_header()` para nuevas ventanas
3. IDEAS_EXPANSION.md → ver qué se puede añadir en v3.5

---

## 🔍 Buscar por problema

| Problema | Dónde mirar |
|----------|-------------|
| No arranca | QUICKSTART.md → Problemas Comunes |
| Brillo no funciona | GUIA_BRILLO_DSI.md → Paso 0 |
| VPN badge siempre rojo | GUIA_GESTOR_VPN.md → interfaz `tun0`/`wg0` |
| Pi-hole no conecta | README.md Troubleshooting (solo v6) |
| Red Local no escanea | README.md Troubleshooting (arp-scan + sudoers) |
| LEDs con destellos | FIX_LED_DESTELLOS.md |
| LEDs no responden | Verificar `led_state.json` + fase1 activo |
| Temperatura chasis N/D | Verificar `hardware_state.json` + fase1 activo |
| Audio no suena | `aplay -l` → verificar dispositivo HDMI activo |
| Cámara no encuentra rpicam-still | `sudo apt install rpicam-apps` |
| OCR no detecta texto | Mejorar iluminación + usar resolución 2592x1944 |
| SMART muestra N/D | Sudoers smartctl + `sudo smartctl -A /dev/nvme0` |
| Homebridge no conecta | README.md Troubleshooting |
| Alertas Telegram no llegan | README.md sección Telegram / `.env` |
| Temperatura no se lee | INSTALL_GUIDE.md → sensors-detect |
| Speedtest falla | README.md sección Instalación Manual |
| Ver errores | `grep ERROR data/logs/dashboard.log` |

---

## 📊 Estadísticas del proyecto v3.4

| Métrica | v3.3 | v3.4 |
|---------|------|------|
| Versión | 3.3 | **3.4** |
| Archivos Python | 53 | **60** |
| Ventanas | 19 | **21** |
| Temas | 15 | 15 |
| Badges en menú | 12 | 12 |
| Servicios background | 12 | **14** |
| Documentos | 15 | **18** |
| JSONs de estado | 1 | **3** |
| Archivos de audio | 0 | **11** |

### Ventanas nuevas en v3.4
- `LedWindow` — Control LEDs RGB del GPIO Board
- `CameraWindow` — Cámara OV5647 + Escáner OCR Tesseract

### Servicios nuevos en v3.4
- `LedService` — escribe `led_state.json`
- `HardwareMonitor` — lee `hardware_state.json`
- `AudioAlertService` — alertas sonoras por altavoces del case
