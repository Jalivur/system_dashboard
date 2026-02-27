# 📚 Índice de Documentación - System Dashboard v3.3

---

## 🚀 Documentos Esenciales

**[README.md](README.md)** ⭐ — Documentación completa v3.3. **Empieza aquí.**

**[QUICKSTART.md](QUICKSTART.md)** ⚡ — Instalación y ejecución en 5 minutos.

---

## 📖 Guías v3.3 (nuevas features)

**[GUIA_DASHBOARD_RESUMEN.md](GUIA_DASHBOARD_RESUMEN.md)**
- Descripción del layout (grid 6 tarjetas + fila Pi-hole)
- Fuentes de datos de cada widget y umbrales de color
- Cómo se usa como pantalla de reposo

**[GUIA_BRILLO_DSI.md](GUIA_BRILLO_DSI.md)**
- Configuración real del hardware FNK0100K (`DSI_OUTPUT="DSI-2"`, backlight `11-0045`)
- Diagnóstico si el brillo no funciona (`wlr-randr`, sysfs, permisos udev)
- Modo ahorro por inactividad — cómo activar el apagado automático

**[GUIA_GESTOR_VPN.md](GUIA_GESTOR_VPN.md)**
- Scripts requeridos (`conectar_vpn.sh` / `desconectar_vpn.sh`)
- Cambiar interfaz OpenVPN ↔ WireGuard (`tun0` / `wg0`)
- Sudoers para ejecutar sin contraseña
- Badge `vpn_offline` y flujo tras conectar/desconectar

---

## 📖 Guías por tema

### 🎨 Personalización
**[THEMES_GUIDE.md](THEMES_GUIDE.md)** — 15 temas, crear personalizados, paletas.

### 🔧 Instalación
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — RPi OS, Kali, venv, script automático.

### ⚙️ Características avanzadas
**[PROCESS_MONITOR_GUIDE.md](PROCESS_MONITOR_GUIDE.md)** — Procesos, filtros, terminación.

**[SERVICE_MONITOR_GUIDE.md](SERVICE_MONITOR_GUIDE.md)** — Servicios systemd, start/stop, logs.

**[HISTORICO_DATOS_GUIDE.md](HISTORICO_DATOS_GUIDE.md)** — SQLite, matplotlib, exportación CSV.

### 🏠 Homebridge
Configuración: ver sección en README.md.  
5 tipos: `switch`, `light`, `thermostat`, `sensor`, `blind`.  
Arquitectura: `core/homebridge_monitor.py` + `ui/windows/homebridge.py`.

### 🕳️ Pi-hole (v3.2)
Configuración: añadir `PIHOLE_HOST`, `PIHOLE_PORT`, `PIHOLE_PASSWORD` al `.env`.  
Solo compatible con **Pi-hole v6**.  
Arquitectura: `core/pihole_monitor.py` + `ui/windows/pihole_window.py`.

### 🖧 Red Local (v3.2)
Instalar: `sudo apt install arp-scan`.  
Sudoers: `usuario ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan`.  
Arquitectura: `core/network_scanner.py` + `ui/windows/network_local.py`.

### 📲 Alertas Telegram
Configuración: `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID` en `.env`.  
Arquitectura: `core/alert_service.py` + `ui/windows/alert_history.py`.

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

---

## 🗂️ Estructura de documentos v3.3

```
📚 Documentación/
├── README.md                    ⭐ Principal v3.3
├── QUICKSTART.md                ⚡ Inicio rápido
├── INDEX.md                     📑 Este archivo
├── INSTALL_GUIDE.md             🔧 Instalación
├── THEMES_GUIDE.md              🎨 Temas
├── PROCESS_MONITOR_GUIDE.md     ⚙️ Procesos
├── SERVICE_MONITOR_GUIDE.md     🔧 Servicios
├── HISTORICO_DATOS_GUIDE.md     📊 Histórico
├── INTEGRATION_GUIDE.md         🤝 Integración fase1
├── IDEAS_EXPANSION.md           💡 Roadmap v3.4+
├── COMPATIBILIDAD.md            🌐 Compatibilidad
├── REQUIREMENTS.md              📋 Requisitos
├── GUIA_DASHBOARD_RESUMEN.md    📊 Resumen Sistema (v3.3)
├── GUIA_BRILLO_DSI.md           💡 Brillo DSI (v3.3)
└── GUIA_GESTOR_VPN.md           🔒 Gestor VPN (v3.3)
```

---

## 🎯 Flujo de lectura recomendado

**Usuario nuevo:**
1. README.md → sección Características
2. QUICKSTART.md → instalar y ejecutar
3. Explorar las 19 ventanas 🎉

**Usuario avanzado / configurar integraciones:**
1. README.md completo
2. Sección Homebridge → `.env` + Insecure Mode
3. Sección Pi-hole → `.env` + compatibilidad v6
4. Sección Telegram → `.env` + `send_test()`
5. GUIA_GESTOR_VPN.md → scripts + interfaz

**Diagnóstico de brillo:**
1. GUIA_BRILLO_DSI.md → Paso 0
2. Verificar `wlr-randr` y `DSI_OUTPUT`

**Desarrollador / extender:**
1. README.md sección Arquitectura
2. `ui/styles.py` → `make_window_header()` para nuevas ventanas
3. IDEAS_EXPANSION.md → ver qué se puede añadir

---

## 🔍 Buscar por problema

| Problema | Dónde mirar |
|----------|-------------|
| No arranca | QUICKSTART.md → Problemas Comunes |
| Brillo no funciona | GUIA_BRILLO_DSI.md → Paso 0 |
| VPN badge siempre rojo | GUIA_GESTOR_VPN.md → interfaz `tun0`/`wg0` |
| Pi-hole no conecta | README.md Troubleshooting (solo v6) |
| Red Local no escanea | README.md Troubleshooting (arp-scan + sudoers) |
| Homebridge no conecta | README.md Troubleshooting |
| Alertas Telegram no llegan | README.md sección Telegram / `.env` |
| Temperatura no se lee | INSTALL_GUIDE.md → sensors-detect |
| Speedtest falla | README.md sección Instalación Manual |
| Ver errores | `grep ERROR data/logs/dashboard.log` |

---

## 📊 Estadísticas del proyecto v3.3

| Métrica | Valor |
|---------|-------|
| Versión | 3.3 |
| Archivos Python | 53 |
| Ventanas | 19 |
| Temas | 15 |
| Badges en menú | 12 |
| Servicios background | 12 |
| Documentos | 15 |
| Tipos Homebridge | 5 |
