# 💡 IDEAS_EXPANSION.md
## Expansión y Roadmap — Sistema de Monitoreo v3.3

---

## ✅ Implementado

### v3.3 (actual)
- **Resumen del Sistema / Pantalla de Reposo** (`OverviewWindow`) — grid de 6 tarjetas + fila Pi-hole, refresco 2s, sin servicio nuevo
- **Control de Brillo DSI** (`DisplayService` + `DisplayWindow`) — sysfs/wlr-randr/xrandr, dim 2min, scroll en ventana, DSI_OUTPUT=DSI-2
- **Gestor VPN** (`VpnMonitor` + `VpnWindow`) — sondeo 10s via `ip addr show`, badge `vpn_offline`, terminal en vivo, `force_poll()` tras acción

### v3.2
- **Escáner Red Local** (`NetworkScanner`) — arp-scan, IP/MAC/fabricante, auto-refresco 60s
- **Pi-hole v6** (`PiholeMonitor`) — API v6 sesión sid, sondeo 60s, badge offline
- **Historial de Alertas** (`AlertHistoryWindow`) — JSON máx.100, tarjetas por nivel, orden cronológico inverso

### v3.1
- **Alertas Telegram** (`AlertService`) — anti-spam edge-trigger+sustain, urllib stdlib
- **Homebridge extendido** — 5 tipos: switch, light, thermostat, sensor, blind

### v3.0
- Visor de Logs con filtros y exportación

### v2.x
- Control Ventiladores PWM, Monitor Placa, Monitor Red (speedtest Ookla), Monitor USB, Monitor Disco, Lanzadores, Monitor Procesos, Monitor Servicios, Histórico SQLite, Actualizaciones, Homebridge, 15 temas, Badges en menú, Logging completo, CleanupService, DataCollectionService

---

## 🔄 Ideas en evaluación para v3.4+

### 🐳 Monitor Docker
- Listar contenedores activos/detenidos
- Start/Stop/Restart desde la UI
- Usar `docker ps --format json` — sin dependencias nuevas
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
- Permite integrar con scripts externos o dashboards adicionales
- `flask` o `http.server` de stdlib

### Backup automático de configuración
- Copiar `data/` a NAS o USB al detectar dispositivo montado
- Trigger: USB inserted → `rsync data/ /mnt/usb/backup/`

### Multi-pantalla / modo kiosk
- Detectar pantalla HDMI conectada y extender la UI
- O redirigir la ventana principal al monitor externo

### Monitor de temperatura por zonas
- Usar el GPIO Board del FNK0100K (I2C 0x21, registro `0xFC`)
- Temperatura del chasis (sensor integrado en el GPIO Board)
- Complementa la temperatura de CPU del SystemMonitor

---

## 🗺️ Roadmap

```
v3.0  ✅ Visor Logs
v3.1  ✅ Telegram + Homebridge extendido
v3.2  ✅ Red Local + Pi-hole v6 + Historial Alertas
v3.3  ✅ Resumen Sistema + Brillo DSI + Gestor VPN  ← ACTUAL
v3.4  🔄 Docker Monitor? Automatización?
v4.0  💭 API REST + Backup + Multi-pantalla?
```

---

## 📊 Cobertura por módulo (v3.3)

| Área | Cobertura | Notas |
|------|-----------|-------|
| Hardware (CPU/RAM/Temp/Disco) | ✅ Completa | SystemMonitor + DiskMonitor |
| Red | ✅ Completa | NetworkMonitor + NetworkScanner |
| Procesos / Servicios | ✅ Completa | ProcessMonitor + ServiceMonitor |
| Fans | ✅ Completa | FanController + FanAutoService |
| Pantalla | ✅ Completa | DisplayService (brillo DSI) |
| VPN | ✅ Básica | VpnMonitor (estado + conectar/desconectar) |
| Homebridge / HomeKit | ✅ Avanzada | 5 tipos de dispositivo |
| Pi-hole | ✅ Completa | API v6, estadísticas, badge |
| Alertas | ✅ Completa | Telegram + historial JSON |
| Histórico / Análisis | ✅ Completa | SQLite + matplotlib |
| Docker | ❌ Pendiente | — |
| MQTT / HA | ❌ Pendiente | — |
