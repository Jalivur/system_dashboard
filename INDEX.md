# 📚 Índice de Documentación - System Dashboard v3.8

---

## 🚀 Documentos Esenciales

**[README.md](README.md)** ⭐ — Documentación completa v3.8. **Empieza aquí.**

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
**[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** — Compartir estado fans via JSON, OLED.

### 💡 Ideas y Expansión
**[IDEAS_EXPANSION.md](IDEAS_EXPANSION.md)** — Roadmap, backlog, cobertura por módulo.

### 🖥️ Multi-Pi (v3.7)
Crear `config/local_settings.py` (en `.gitignore`) con los valores de `DSI_X/Y/WIDTH/HEIGHT` para cada máquina.
El **Editor de Configuración** *(v3.8)* permite editar este fichero directamente desde la UI sin SSH.
- **Pi 5 Wayland**: `wayvnc --output=DSI-2 0.0.0.0 5901` + `gsettings set org.gnome.desktop.session idle-delay 0`
- **Pi 3B+ Xvfb**: display virtual `:1`, VNC puerto `5901`, resolución configurable

---

## 📋 Archivos de soporte

| Archivo | Propósito |
|---------|-----------|
| `requirements.txt` | Dependencias Python |
| `REQUIREMENTS.md` | Requisitos detallados con sistema |
| `.env` | Credenciales (NO en git) |
| `.env.example` | Plantilla |
| `config/settings.py` | Constantes globales + clase Icons |
| `config/button_labels.py` | Labels de botones (fuente única de verdad) |
| `config/local_settings.py` | Config por máquina (NO en git, generado por Editor Config) |
| `config/themes.py` | 15 temas |
| `config/services.json` | Servicios activos/inactivos + visibilidad botones (NO en git) |
| `scripts/generate_sounds.py` | Genera los 11 audios de alerta |
| `scripts/sounds/` | Archivos .wav (tono + voz TTS español) |
| `data/fan_state.json` | fase1 lee — modo y PWM del ventilador |
| `data/led_state.json` | fase1 lee — modo y color de los LEDs |
| `data/hardware_state.json` | fase1 escribe — temp chasis + fan duty real |
| `data/photos/` | Fotos capturadas con la cámara OV5647 |
| `data/scans/` | Escaneos OCR (.txt + .md) |

> **Nota v3.8**: `data/services.json` y `data/button_config.json` se han unificado en `config/services.json` (secciones `services` y `ui`).

---

## 🗂️ Estructura de documentos v3.8

```
📚 Documentación/
├── README.md                         ⭐ Principal v3.8
├── QUICKSTART.md                     ⚡ Inicio rápido
├── INDEX.md                          📑 Este archivo
├── REQUIREMENTS.md                   📋 Requisitos
├── INSTALL_GUIDE.md                  🔧 Instalación
├── THEMES_GUIDE.md                   🎨 Temas
├── INTEGRATION_GUIDE.md              🤝 Integración fase1
├── IDEAS_EXPANSION.md                💡 Roadmap v3.9+
└── COMPATIBILIDAD.md                 🌐 Compatibilidad
```

---

## 🎯 Flujo de lectura recomendado

**Usuario nuevo:**
1. README.md → sección Características
2. QUICKSTART.md → instalar y ejecutar
3. Explorar las 27 ventanas 🎉

**Usuario avanzado / configurar integraciones:**
1. README.md completo
2. Sección Homebridge → `.env` + Insecure Mode
3. Sección Pi-hole → `.env` + compatibilidad v6
4. Sección Telegram → `.env` + `send_test()`
5. GUIA_GESTOR_VPN.md → scripts + interfaz
6. Sección Multi-Pi → `local_settings.py` + wayvnc / Xvfb
7. **Editor de Configuración** *(v3.8)* → ajustar umbrales e iconos desde la UI

**Desarrollador / extender:**
1. README.md sección Arquitectura
2. `ui/styles.py` → `make_window_header()` y `make_entry()` para nuevas ventanas
3. `core/service_registry.py` → registrar nuevos servicios
4. `config/button_labels.py` → añadir label antes de registrar en `_BTN_MAP`
5. IDEAS_EXPANSION.md → ver qué se puede añadir en v3.9

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
| No puedo escribir en entries (VNC) | README.md → `make_entry()` en `ui/styles.py` |
| Foco perdido tras inactividad (Pi 5) | `gsettings set org.gnome.desktop.session idle-delay 0` |
| Dashboard no visible por VNC en Pi 5 | `wayvnc --output=DSI-2 0.0.0.0 5901` |
| Configuración distinta por máquina | `config/local_settings.py` o Editor de Configuración *(v3.8)* |
| Homebridge no conecta | README.md Troubleshooting |
| Alertas Telegram no llegan | README.md sección Telegram / `.env` |
| SMART muestra N/D | Sudoers smartctl + `sudo smartctl -A /dev/nvme0` |
| Audio no suena | `aplay -l` → verificar dispositivo HDMI activo |
| Cámara no encuentra rpicam-still | `sudo apt install rpicam-apps` |
| WiFi no muestra datos | `sudo apt install wireless-tools` |
| SSH monitor vacío | Verificar que `who` y `last` funcionan en el sistema |
| Ver errores | `grep ERROR data/logs/dashboard.log` |

---

## 📊 Estadísticas del proyecto v3.8

| Métrica | v3.7 | v3.8 |
|---------|------|------|
| Versión | 3.7 | **3.8** |
| Archivos Python | 63 | **68** |
| Ventanas | 24 | **27** |
| Temas | 15 | 15 |
| Badges en menú | 12 | 12 |
| Servicios background | 14 | **16** |
| Documentos | 9 | 9 |

### Ventanas nuevas en v3.8
- `SSHWindow` — Monitor de sesiones SSH activas e historial
- `WiFiWindow` — Monitor de señal, calidad y tráfico WiFi
- `ConfigEditorWindow` — Editor de `local_settings.py` desde la UI

### Infraestructura nueva en v3.8
- `SSHMonitor` — servicio daemon en `core/`
- `WiFiMonitor` — servicio daemon en `core/`
- `crontab_service.py` / `camera_service.py` — extraídos de UI a `core/`
- `config/button_labels.py` — fuente única de verdad para labels de botones
- Fix `StringVar`/`IntVar` con `master=` explícito (elimina `RuntimeError` al salir)
