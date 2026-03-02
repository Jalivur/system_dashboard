# 📚 Índice de Documentación - System Dashboard v3.7

---

## 🚀 Documentos Esenciales

**[README.md](README.md)** ⭐ — Documentación completa v3.7. **Empieza aquí.**

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
| `config/settings.py` | Constantes globales |
| `config/local_settings.py` | Config por máquina (NO en git) |
| `config/themes.py` | 15 temas |
| `scripts/generate_sounds.py` | Genera los 11 audios de alerta |
| `scripts/sounds/` | Archivos .wav (tono + voz TTS español) |
| `data/fan_state.json` | fase1 lee — modo y PWM del ventilador |
| `data/led_state.json` | fase1 lee — modo y color de los LEDs |
| `data/hardware_state.json` | fase1 escribe — temp chasis + fan duty real |
| `data/services.json` | Servicios dashboard activos/inactivos |
| `data/button_config.json` | Visibilidad de botones del menú |
| `data/photos/` | Fotos capturadas con la cámara OV5647 |
| `data/scans/` | Escaneos OCR (.txt + .md) |

---

## 🗂️ Estructura de documentos v3.7

```
📚 Documentación/
├── README.md                         ⭐ Principal v3.7
├── QUICKSTART.md                     ⚡ Inicio rápido
├── INDEX.md                          📑 Este archivo
├── REQUIREMENTS.md                   📋 Requisitos
├── INSTALL_GUIDE.md                  🔧 Instalación
├── THEMES_GUIDE.md                   🎨 Temas
├── INTEGRATION_GUIDE.md              🤝 Integración fase1
├── IDEAS_EXPANSION.md                💡 Roadmap v3.8+
└── COMPATIBILIDAD.md                 🌐 Compatibilidad
```

---

## 🎯 Flujo de lectura recomendado

**Usuario nuevo:**
1. README.md → sección Características
2. QUICKSTART.md → instalar y ejecutar
3. Explorar las 24 ventanas 🎉

**Usuario avanzado / configurar integraciones:**
1. README.md completo
2. Sección Homebridge → `.env` + Insecure Mode
3. Sección Pi-hole → `.env` + compatibilidad v6
4. Sección Telegram → `.env` + `send_test()`
5. GUIA_GESTOR_VPN.md → scripts + interfaz
6. Sección Multi-Pi → `local_settings.py` + wayvnc / Xvfb

**Desarrollador / extender:**
1. README.md sección Arquitectura
2. `ui/styles.py` → `make_window_header()` y `make_entry()` para nuevas ventanas
3. `core/service_registry.py` → registrar nuevos servicios
4. IDEAS_EXPANSION.md → ver qué se puede añadir en v3.8

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
| Configuración distinta por máquina | `config/local_settings.py` (en `.gitignore`) |
| Homebridge no conecta | README.md Troubleshooting |
| Alertas Telegram no llegan | README.md sección Telegram / `.env` |
| SMART muestra N/D | Sudoers smartctl + `sudo smartctl -A /dev/nvme0` |
| Audio no suena | `aplay -l` → verificar dispositivo HDMI activo |
| Cámara no encuentra rpicam-still | `sudo apt install rpicam-apps` |
| Ver errores | `grep ERROR data/logs/dashboard.log` |

---

## 📊 Estadísticas del proyecto v3.7

| Métrica | v3.4 | v3.7 |
|---------|------|------|
| Versión | 3.4 | **3.7** |
| Archivos Python | 60 | **63** |
| Ventanas | 21 | **24** |
| Temas | 15 | 15 |
| Badges en menú | 12 | 12 |
| Servicios background | 14 | 14 |
| Documentos | 18 | 18 |

### Ventanas nuevas desde v3.4
- `ServicesManagerWindow` — Gestión servicios dashboard *(v3.6)*
- `ButtonManagerWindow` — Visibilidad botones menú *(v3.6.5)*
- `CrontabWindow` — Gestor de crontab *(v3.7)*

### Infraestructura nueva desde v3.4
- `ServiceRegistry` — registro centralizado *(v3.5)*
- `WindowManager` — gestión visibilidad botones *(v3.6.5)*
- `make_entry()` — entries compatibles con VNC/Wayland *(v3.7)*
- `local_settings.py` — config por máquina sin tocar git *(v3.7)*
