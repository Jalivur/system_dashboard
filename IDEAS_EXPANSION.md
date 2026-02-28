# 💡 IDEAS_EXPANSION.md
## Expansión y Roadmap — Sistema de Monitoreo v3.4

---

## ✅ Implementado

### v3.4 (actual) — Hardware FNK0100K
- **LEDs RGB inteligentes** (`LedService` + `LedWindow`)
  - 6 modos: auto, off, static, follow, breathing, rainbow
  - Dashboard escribe `led_state.json` → fase1.py aplica via I2C
  - Fix destellos: solo escribe I2C cuando modo/color cambia (`_last_led_applied`)
  - Colores rápidos, preview en tiempo real, selector RGB con sliders

- **Temperatura chasis + Fan duty real** (`HardwareMonitor`)
  - fase1.py lee `board.get_temp()` + `board.get_fan0/1_duty()` cada 5s
  - Escribe `hardware_state.json` → dashboard lee y muestra en Monitor Placa
  - Integrado en `MonitorWindow` como tarjeta extra debajo del grid

- **Alertas de audio** (`AudioAlertService`)
  - 11 archivos .wav: tono sintético + voz TTS español (`espeak-ng`)
  - Un archivo por métrica y nivel: `{metric}_{warn|crit|ok}.wav`
  - Lógica correcta: warn.wav cada 5min mientras siga en aviso,
    crit.wav cada 30s mientras siga crítico, ok.wav una vez al recuperarse
  - 4 métricas independientes: temp, cpu, ram, services
  - `services` sin nivel warn (siempre es 0 cuando todo está bien)

- **Cámara OV5647 + Escáner OCR** (`CameraWindow`)
  - `rpicam-still` (Bookworm), resoluciones hasta 2592x1944
  - OCR con Tesseract local (sin internet): spa, eng, spa+eng
  - Preprocesado PIL: escala de grises + contraste + nitidez
  - Guarda `.txt` y `.md` con metadata en `data/scans/`
  - Dos tabs (Foto / Escáner) con scroll propio del proyecto

- **NVMe SMART extendido** (`DiskWindow` + `DiskMonitor.get_nvme_smart()`)
  - Horas de uso, ciclos de encendido, apagados bruscos
  - TB escritos/leídos en vida, % de vida útil consumida
  - Actualización cada 30s (smartctl es lento, no bloquea la UI)
  - Integrado en `DiskWindow` como tarjeta debajo del grid existente

### v3.3
- **Resumen del Sistema / Pantalla de Reposo** (`OverviewWindow`)
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
- Control Ventiladores PWM, Monitor Placa, Monitor Red, Monitor USB,
  Monitor Disco, Lanzadores, Monitor Procesos, Monitor Servicios,
  Histórico SQLite, Actualizaciones, Homebridge, 15 temas, Badges,
  Logging completo, CleanupService, DataCollectionService

---

## 🔄 Ideas en evaluación para v3.5+

### 🐳 Monitor Docker
- Listar contenedores activos/detenidos
- Start/Stop/Restart desde la UI
- `docker ps --format json` — sin dependencias nuevas
- Badge con nº de contenedores caídos

### 🤖 Automatización / Tareas Programadas
- Interfaz para ver y gestionar cron jobs del usuario
- Añadir/eliminar tareas sin editar crontab a mano

### 📡 Monitor MQTT / Home Assistant
- Suscribirse a topics MQTT y mostrar valores en tiempo real
- Alternativa ligera si no se usa Homebridge

---

## 💭 Ideas futuras (backlog)

### API REST local
- Endpoint `/status` que devuelva el estado del sistema en JSON
- `flask` o `http.server` de stdlib

### Backup automático de configuración
- Copiar `data/` a NAS o USB al detectar dispositivo montado
- `rsync data/ /mnt/usb/backup/`

### Multi-pantalla / modo kiosk
- Detectar pantalla HDMI conectada y extender la UI

---

## 🗺️ Roadmap

```
v3.0  ✅ Visor Logs
v3.1  ✅ Telegram + Homebridge extendido
v3.2  ✅ Red Local + Pi-hole v6 + Historial Alertas
v3.3  ✅ Resumen Sistema + Brillo DSI + Gestor VPN
v3.4  ✅ LEDs RGB + Temp Chasis + Audio + Cámara OCR + SMART  ← ACTUAL
v3.5  🔄 Docker? Automatización? MQTT?
v4.0  💭 API REST + Backup + Multi-pantalla?
```

---

## 📊 Cobertura por módulo (v3.4)

| Área | Cobertura | Notas |
|------|-----------|-------|
| Hardware CPU/RAM/Temp/Disco | ✅ Completa | SystemMonitor + DiskMonitor |
| NVMe SMART | ✅ Completa | TBW, horas, vida útil, ciclos |
| Red | ✅ Completa | NetworkMonitor + NetworkScanner |
| Procesos / Servicios | ✅ Completa | ProcessMonitor + ServiceMonitor |
| Fans | ✅ Completa | FanController + FanAutoService |
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
| Docker | ❌ Pendiente | v3.5 |
| MQTT / HA | ❌ Pendiente | v3.5 |
