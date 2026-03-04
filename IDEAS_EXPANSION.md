# 💡 IDEAS_EXPANSION.md
## Expansión y Roadmap — Sistema de Monitoreo v3.8

---

## ✅ Implementado

### v3.8 (actual) — SSH + WiFi + Config Editor + Refactors

- **Monitor SSH** (`SSHMonitor` + `SSHWindow`)
  - Sesiones activas en tiempo real con IP de origen, usuario y hora de conexión
  - Historial de sesiones con duración formateada (`1h 30min`, `15 min`)
  - Textos humanizados: `pts/0` → `Sesión 1`, IPs locales etiquetadas como `(red local)`
  - Detección de cortes por crash o apagado

- **Monitor WiFi** (`WiFiMonitor` + `WiFiWindow`)
  - Señal en tiempo real: SSID, dBm, calidad de enlace, bitrate
  - Barras visuales de señal (▂▄▆█) y gráfica histórica
  - Tráfico RX/TX con gráficas independientes
  - Servicio daemon con poll cada 5s

- **Editor de Configuración** (`ConfigEditorWindow`)
  - Edita `config/local_settings.py` por máquina sin tocar `settings.py`
  - Parámetros editables: pantalla, tiempos, umbrales CPU/Temp/RAM/Red, parámetros de red
  - Todos los `Icons.*` editables con preview en tiempo real del nuevo glifo
  - Carga diferida (lotes con `after()`) — no bloquea la UI al abrir
  - Merge inteligente: guardar un cambio no sobreescribe los anteriores
  - Guardar y reiniciar en un solo click

- **Refactor arquitectónico**
  - `core/crontab_service.py` y `core/camera_service.py` extraídos de UI a `core/`
  - Separación completa: `core/` sin imports tkinter, `ui/` sin lógica de sistema
  - Fix `StringVar`/`IntVar` con `master=` explícito — elimina `RuntimeError` al salir
  - `ServicesManagerWindow` migrada a `Icons.*` — cero literales Nerd Font fuera de `Icons`

### v3.7 — Crontab + Fixes + Multi-Pi
- **Gestor Crontab** (`CrontabWindow`)
  - Ver, añadir, editar y eliminar entradas del crontab
  - Selector de usuario: usuario / root
  - Accesos rápidos de programación (@reboot, cada hora, cada día, etc.)
  - Preview legible de la expresión cron

- **Fix grab modal** (`dialogs.py` + `main_window.py`)
  - `grab_release()` garantizado al cerrar `terminal_dialog` y `exit_application`
  - Elimina el bloqueo de foco en toda la app al cerrar diálogos

- **`make_entry()`** (`ui/styles.py`)
  - Reemplaza `ctk.CTkEntry()` en ventanas con entries
  - Fuerza foco al widget interno con `focus_force()` al hacer clic
  - Soluciona escritura en VNC con `overrideredirect(True)`

- **Soporte dual-Pi** (`config/local_settings.py`)
  - Configuración independiente por máquina sin tocar git
  - Pi 3B+: Xvfb `:1`, resolución 1024×762, VNC puerto 5901
  - Pi 5: Wayland + labwc, wayvnc `--output=DSI-2`, idle-delay 0

### v3.6.5
- **Gestor de Botones** (`ButtonManagerWindow` + `WindowManager`)
  - Mostrar/ocultar botones del menú principal desde la UI
  - Persistencia en `config/services.json` (sección `ui`)

### v3.6
- **Servicios Dashboard** (`ServicesManagerWindow`)
  - Activar/desactivar servicios background del dashboard desde la UI
  - Persistencia en `config/services.json` (sección `services`)

### v3.5
- **ServiceRegistry** (`core/service_registry.py`)
  - Registro centralizado de todos los servicios del dashboard
  - Base para `ServicesManagerWindow` y `ButtonManagerWindow`

### v3.4 — Hardware FNK0100K
- **LEDs RGB inteligentes** (`LedService` + `LedWindow`) — 6 modos, sin destellos
- **Temperatura chasis + Fan duty real** (`HardwareMonitor`) — via `hardware_state.json`
- **Alertas de audio** (`AudioAlertService`) — 11 .wav, TTS español, 4 métricas
- **Cámara OV5647 + Escáner OCR** (`CameraWindow`) — Tesseract local, `.txt` y `.md`
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
- **Alertas Telegram** (`AlertService`)
- **Homebridge extendido** — 5 tipos de dispositivo

### v3.0
- Visor de Logs con filtros y exportación

### v2.x
- Control Ventiladores PWM, monitores completos, 15 temas, badges, logging, SQLite

---

## 🔄 Ideas en evaluación para v3.9+

### 🌐 API REST local
- Endpoint `/status` que devuelva el estado del sistema en JSON
- `http.server` de stdlib — sin dependencias nuevas
- Permitiría integración con otros sistemas de la red

### 💾 Backup automático de configuración
- Copiar `data/` a NAS o USB al detectar dispositivo montado
- Restauración desde la UI

### 🖥️ Multi-pantalla / modo kiosk
- Detectar pantalla HDMI conectada y extender la UI
- Modo kiosk con rotación automática de vistas

### 📊 Dashboard web espejo
- Servir la UI como página HTML desde el propio Pi
- Sin dependencias de pantalla física

---

## 💭 Ideas futuras (backlog)

### Notificaciones push locales
- Avisos en pantalla sin Telegram (para uso sin internet)

### Historial de comandos crontab
- Log de ejecuciones con resultado (éxito/error)

### Perfiles de configuración
- Múltiples perfiles de `local_settings.py` intercambiables desde la UI

---

## 🗺️ Roadmap

```
v3.0  ✅ Visor Logs
v3.1  ✅ Telegram + Homebridge extendido
v3.2  ✅ Red Local + Pi-hole v6 + Historial Alertas
v3.3  ✅ Resumen Sistema + Brillo DSI + Gestor VPN
v3.4  ✅ LEDs RGB + Temp Chasis + Audio + Cámara OCR + SMART
v3.5  ✅ ServiceRegistry
v3.6  ✅ ServicesManagerWindow
v3.6.5 ✅ ButtonManagerWindow
v3.7  ✅ CrontabWindow + Fixes VNC/Wayland + Multi-Pi
v3.8  ✅ Monitor SSH + Monitor WiFi + Editor Config + Refactor core/  ← ACTUAL
v3.9  💭 API REST + Backup + Multi-pantalla?
```

---

## 📊 Cobertura por módulo (v3.8)

| Área | Cobertura | Notas |
|------|-----------|-------|
| Hardware CPU/RAM/Temp/Disco | ✅ Completa | SystemMonitor + DiskMonitor |
| NVMe SMART | ✅ Completa | TBW, horas, vida útil, ciclos |
| Red | ✅ Completa | NetworkMonitor + NetworkScanner |
| WiFi | ✅ Completa | WiFiMonitor — señal, calidad, tráfico *(v3.8)* |
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
| Monitor SSH | ✅ Completa | Sesiones activas + historial humanizado *(v3.8)* |
| Config por máquina | ✅ Completa | local_settings.py + Editor Config UI *(v3.8)* |
| Multi-Pi / local_settings | ✅ Completa | Pi 5 Wayland + Pi 3 Xvfb |
| API REST local | ❌ Pendiente | v3.9 |
| Backup automático | ❌ Pendiente | v3.9 |
