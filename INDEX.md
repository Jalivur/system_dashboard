# 📚 Índice de Documentación - System Dashboard v4.0

---

## 🚀 Documentos Esenciales

**[README.md](README.md)** ⭐ — Documentación completa v4.0. **Empieza aquí.**

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
**[IDEAS_EXPANSION.md](IDEAS_EXPANSION.md)** — Roadmap v4.1+, backlog, cobertura por módulo.

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

---

## 📋 Archivos de configuración

| Archivo | En git | Gestiona |
|---------|--------|---------|
| `config/settings.py` | ✅ | Constantes globales, Icons, UI (pestañas), LAUNCHERS |
| `config/button_labels.py` | ✅ | Labels de botones (fuente única de verdad) |
| `config/themes.py` | ✅ | 15 temas |
| `config/services.json` | ❌ | Estado servicios + visibilidad botones UI |
| `config/local_settings.py` | ❌ | Overrides por máquina (editable via Config Editor) |
| `.env` | ❌ | Credenciales (Homebridge, PiHole, Telegram, VPN) |

---

## 🗂️ Estructura de documentos v4.0

```
📚 Documentación/
├── README.md                         ⭐ Principal v4.0
├── QUICKSTART.md                     ⚡ Inicio rápido
├── INDEX.md                          📑 Este archivo
├── REQUIREMENTS.md                   📋 Requisitos
├── INSTALL_GUIDE.md                  🔧 Instalación
├── THEMES_GUIDE.md                   🎨 Temas
├── INTEGRATION_GUIDE.md              🤝 Integración fase1
├── IDEAS_EXPANSION.md                💡 Roadmap v4.1+
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
4. Sección Telegram → `.env`
5. Sección Multi-Pi → `local_settings.py` + wayvnc / Xvfb
6. **Editor de Configuración** *(v3.8)* → ajustar umbrales e iconos desde la UI

**Desarrollador / extender:**
1. README.md sección Arquitectura
2. `config/settings.py → class UI` → entender estructura de pestañas
3. `ui/window_lifecycle.py` → patrón de registro de ventanas
4. `ui/styles.py` → `make_window_header()` y `make_entry()` para nuevas ventanas
5. `core/service_registry.py` → registrar nuevos servicios
6. IDEAS_EXPANSION.md → ver qué se puede añadir en v4.1

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
| Ver errores | `grep ERROR data/logs/dashboard.log` |

---

## 📊 Estadísticas del proyecto v4.0

| Métrica | v3.8 | v4.0 |
|---------|------|------|
| Versión | 3.8 | **4.0** |
| Archivos Python | 68 | **73** |
| Ventanas | 27 | 27 |
| Temas | 15 | 15 |
| Badges en menú | 12 | 12 |
| Servicios background | 16 | 16 |
| Módulos ui/main_* | 1 | **5** |
| Documentos | 9 | 9 |

### Cambios arquitecturales en v4.0
- `ui/main_badges.py` — `BadgeManager` (nuevo)
- `ui/main_update_loop.py` — `UpdateLoop` (nuevo)
- `ui/main_system_actions.py` — exit/restart (nuevo)
- `ui/window_lifecycle.py` — `WindowLifecycleManager` (nuevo)
- `ui/main_window.py` — 891 → 451 líneas (refactorizado)
- `config/settings.py → class UI` — definición de pestañas (nuevo)
