# 💡 IDEAS_EXPANSION.md
## Expansión y Roadmap — Sistema de Monitoreo v4.0

---

## ✅ Implementado

### v4.0 (actual) — Refactorización Arquitectural

- **Menú por pestañas con scroll horizontal táctil**
  - 6 pestañas categorizadas: Sistema, Red, Hardware, Servicios, Registros, Config
  - Ancho fijo 130px por pestaña — táctil, escala sin límite
  - Footer fijo (Gestor Botones, Reiniciar, Salir) visible desde cualquier pestaña
  - Pestañas definidas en `config/settings.py → class UI` — configuración pura

- **`WindowLifecycleManager`** (`ui/window_lifecycle.py`)
  - Elimina 27 métodos `open_*` dispersos en `main_window.py`
  - Ciclo de vida unificado: factory, lift, `_btn_active`/`_btn_idle`, bind `<Destroy>`
  - Registro en una línea por ventana: `r("clave", BL.LABEL, lambda: Ventana(...))`

- **Modularización de `main_window.py`** (891 → 451 líneas, −49%)
  - `ui/main_badges.py` — `BadgeManager`: crear y actualizar badges
  - `ui/main_update_loop.py` — `UpdateLoop`: reloj, uptime, loop de badges
  - `ui/main_system_actions.py` — `exit_application`, `restart_application`

- **`WindowManager` refactorizado** — patrón callback (`set_rerender_callback`) en lugar de reGrid directo

### v3.8 — SSH + WiFi + Config Editor + Refactors

- **Monitor SSH** (`SSHMonitor` + `SSHWindow`)
  - Sesiones activas en tiempo real con IP de origen, usuario y hora de conexión
  - Historial de sesiones con duración formateada (`1h 30min`, `15 min`)
  - Textos humanizados: `pts/0` → `Sesión 1`, IPs locales etiquetadas como `(red local)`

- **Monitor WiFi** (`WiFiMonitor` + `WiFiWindow`)
  - Señal en tiempo real: SSID, dBm, calidad de enlace, bitrate
  - Barras visuales de señal (▂▄▆█) y gráfica histórica
  - Tráfico RX/TX con gráficas independientes

- **Editor de Configuración** (`ConfigEditorWindow`)
  - Edita `config/local_settings.py` por máquina sin tocar `settings.py`
  - Iconos editables con preview en tiempo real, merge inteligente

- **Refactor arquitectónico**
  - `core/crontab_service.py` y `core/camera_service.py` extraídos de UI a `core/`
  - Fix `StringVar`/`IntVar` con `master=` explícito — elimina `RuntimeError` al salir

### v3.7 — Crontab + Fixes + Multi-Pi
- **Gestor Crontab** — ver/añadir/editar/eliminar entradas crontab, selector usuario/root
- **Fix grab modal** — `grab_release()` garantizado al cerrar diálogos
- **`make_entry()`** — soluciona escritura en VNC con `overrideredirect(True)`
- **Soporte dual-Pi** — `config/local_settings.py`, Pi 3B+ Xvfb + Pi 5 Wayland

### v3.6.5
- **Gestor de Botones** (`ButtonManagerWindow` + `WindowManager`) — persistencia en `services.json`

### v3.6
- **Servicios Dashboard** (`ServicesManagerWindow`) — persistencia en `services.json`

### v3.5
- **ServiceRegistry** — registro centralizado de todos los servicios del dashboard

### v3.4 — Hardware FNK0100K
- **LEDs RGB inteligentes** — 6 modos, sin destellos
- **Temperatura chasis + Fan duty real** — via `hardware_state.json`
- **Alertas de audio** — 11 .wav, TTS español, 4 métricas
- **Cámara OV5647 + Escáner OCR** — Tesseract local
- **NVMe SMART extendido** — TBW, horas, ciclos, % vida útil

### v3.3
- **Resumen del Sistema** (`OverviewWindow`)
- **Control de Brillo DSI** (`DisplayService` + `DisplayWindow`)
- **Gestor VPN** (`VpnMonitor` + `VpnWindow`)

### v3.2
- **Escáner Red Local** (`NetworkScanner`) — arp-scan
- **Pi-hole v6** (`PiholeMonitor`) — API v6
- **Historial de Alertas** (`AlertHistoryWindow`)

### v3.1
- **Alertas Telegram**, Homebridge extendido — 5 tipos de dispositivo

### v3.0
- Visor de Logs con filtros y exportación

### v2.x
- Control Ventiladores PWM, monitores completos, 15 temas, badges, logging, SQLite

---

## 🔄 Ideas en evaluación para v4.1

### 🎵 Audio Monitor / Control
- Control de volumen ALSA desde la UI (jack + óptico del kit Freenove)
- Sin dependencias nuevas (`subprocess amixer/aplay`)
- Más simple de implementar — recomendado como primera feature v4.1

### 🌦️ Widget de Clima
- Open-Meteo (sin clave API, gratuita)
- Temperatura exterior + previsión 3 días
- Independiente del resto del sistema

### 🔌 I²C Scanner
- `smbus2` en modo solo lectura
- Detecta dispositivos conectados al bus I²C del Pi
- Seguro — no interfiere con fase1.py

### ⚡ GPIO Monitor / Control
- `gpiozero` — requiere planificación previa de pines libres
- Más complejo: inventariar pines ya usados por fase1.py antes de implementar

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
v4.0   ✅ Pestañas táctiles + WindowLifecycleManager + Modularización main_*  ← ACTUAL
v4.1   💭 Audio Control + Clima + I²C Scanner + GPIO?
```

---

## 📊 Cobertura por módulo (v4.0)

| Área | Cobertura | Notas |
|------|-----------|-------|
| Hardware CPU/RAM/Temp/Disco | ✅ Completa | SystemMonitor + DiskMonitor |
| NVMe SMART | ✅ Completa | TBW, horas, vida útil, ciclos |
| Red | ✅ Completa | NetworkMonitor + NetworkScanner |
| WiFi | ✅ Completa | WiFiMonitor — señal, calidad, tráfico |
| Procesos / Servicios systemd | ✅ Completa | ProcessMonitor + ServiceMonitor |
| Servicios Dashboard | ✅ Completa | ServiceRegistry + ServicesManagerWindow |
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
| Audio Control | ❌ Pendiente | v4.1 |
| Widget Clima | ❌ Pendiente | v4.1 |
| I²C Scanner | ❌ Pendiente | v4.1 |
| GPIO Monitor | ❌ Pendiente | v4.1 |
| API REST local | ❌ Pendiente | futuro |
| Backup automático | ❌ Pendiente | futuro |
