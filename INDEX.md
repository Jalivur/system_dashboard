# 📚 Índice de Documentación - System Dashboard v3.1

Guía completa de toda la documentación del proyecto actualizada.

---

## 🚀 Documentos Esenciales

### **Para Empezar:**
1. **[README.md](README.md)** ⭐  
   Documentación completa del proyecto v3.1. **Empieza aquí.**

2. **[QUICKSTART.md](QUICKSTART.md)** ⚡  
   Instalación y ejecución en 5 minutos.

---

## 📖 Guías por Tema

### 🎨 **Personalización**

**[THEMES_GUIDE.md](THEMES_GUIDE.md)**  
- Lista completa de 15 temas
- Cómo crear temas personalizados
- Paletas de colores de cada tema
- Cambiar tema desde código

---

### 🔧 **Instalación**

**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)**  
- Instalación en Raspberry Pi OS
- Instalación en Kali Linux
- Instalación en otros Linux
- Solución de problemas comunes
- Métodos: venv, sin venv, script automático

---

### ⚙️ **Características Avanzadas**

**[PROCESS_MONITOR_GUIDE.md](PROCESS_MONITOR_GUIDE.md)**  
- Monitor de procesos completo
- Búsqueda y filtrado
- Terminación de procesos
- Personalización de columnas

**[SERVICE_MONITOR_GUIDE.md](SERVICE_MONITOR_GUIDE.md)**  
- Monitor de servicios systemd
- Start/Stop/Restart servicios
- Enable/Disable autostart
- Ver logs en tiempo real
- Implementación paso a paso

**[HISTORICO_DATOS_GUIDE.md](HISTORICO_DATOS_GUIDE.md)**  
- Sistema de histórico completo
- Base de datos SQLite
- Visualización con matplotlib
- Recolección automática
- Exportación CSV
- Implementación paso a paso

**[FAN_CONTROL_GUIDE.md](FAN_CONTROL_GUIDE.md)** (si existe)  
- Configuración de ventiladores PWM
- Crear curvas personalizadas
- Modos de operación
- Servicio background

**[NETWORK_GUIDE.md](NETWORK_GUIDE.md)** (si existe)  
- Monitor de tráfico de red
- Speedtest integrado (CLI oficial Ookla)
- Auto-detección de interfaz
- Lista de IPs

---

### 🏠 **Homebridge**

**Configuración rápida** — Ver sección en [QUICKSTART.md](QUICKSTART.md) y [README.md](README.md):
- Crear `.env` con IP, puerto, usuario y contraseña
- Activar Insecure Mode en Homebridge
- Verificar conectividad entre Pis

**5 tipos de dispositivo soportados**:
- `switch` — enchufe / interruptor (CTkSwitch táctil 90×46px)
- `light` — luz regulable (ON/OFF + brillo)
- `thermostat` — termostato (temp actual + botones +/− objetivo)
- `sensor` — sensor temperatura/humedad (solo lectura)
- `blind` — persiana / estor (posición %, control en HomeKit)

**Arquitectura**:
- `core/homebridge_monitor.py` — Sondeo 30s, JWT, caché en memoria, 5 tipos, `set_brightness()`, `set_target_temp()`
- `core/system_monitor.py` — Caché en background thread (cada 2s)
- `core/service_monitor.py` — Caché en background thread (cada 10s), is-enabled batch
- `ui/windows/homebridge.py` — Tarjetas adaptativas por tipo de dispositivo
- `ui/styles.py` — `make_homebridge_switch()` para switch/light
- Badges `hb_offline`, `hb_on`, `hb_fault` en `ui/main_window.py`

---

### 📲 **Alertas Telegram**

**Configuración rápida** — Ver sección en [QUICKSTART.md](QUICKSTART.md) y [README.md](README.md):
- Añadir `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` al `.env`
- Verificar con `alert_service.send_test()`

**Arquitectura**:
- `core/alert_service.py` — 8º servicio background, urllib stdlib, anti-spam edge-trigger + sustain 60s
- Métricas: temperatura, CPU, RAM, disco (warn + crit) y servicios fallidos
- Sin dependencias nuevas — usa `urllib` de la stdlib de Python

---

### 🏗️ **Arquitectura**

**[ARCHITECTURE.md](ARCHITECTURE.md)** (si existe)  
- Estructura del proyecto
- Patrones de diseño
- Flujo de datos
- Cómo extender funcionalidad

---

### 🤝 **Integración**

**[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)**  
- Integrar con fase1.py (OLED)
- Compartir estado de ventiladores
- API de archivos JSON
- Sincronización entre procesos

---

### 💡 **Ideas y Expansión**

**[IDEAS_EXPANSION.md](IDEAS_EXPANSION.md)**  
- ✅ Funcionalidades implementadas (hasta v3.1 inclusive)
- 🔄 En evaluación (Docker, Automatización)
- 💭 Ideas futuras (API REST, Red avanzada, Backup)
- Roadmap v3.1 y v3.2

---

## 📋 Archivos de Soporte

### **Configuración:**
- `requirements.txt` - Dependencias Python
- `.env` - Credenciales Homebridge + Telegram (NO en git)
- `.env.example` - Plantilla de configuración
- `install.sh` - Script de instalación automática
- `config/settings.py` - Configuración global
- `config/themes.py` - Definición de 15 temas

### **Scripts:**
- `main.py` - Punto de entrada
- `scripts/` - Scripts personalizados

### **Compatibilidad:**
- `COMPATIBILIDAD.md` - Sistemas soportados
- `REQUIREMENTS.md` - Requisitos detallados

---

## 🗂️ Estructura de Documentos v3.1

```
📚 Documentación/
├── README.md                    ⭐ Documento principal v3.1
├── QUICKSTART.md                ⚡ Inicio rápido
├── INDEX.md                     📑 Este archivo
├── INSTALL_GUIDE.md             🔧 Instalación
├── THEMES_GUIDE.md              🎨 Guía de temas
├── PROCESS_MONITOR_GUIDE.md     ⚙️ Monitor de procesos
├── SERVICE_MONITOR_GUIDE.md     🔧 Monitor de servicios
├── HISTORICO_DATOS_GUIDE.md     📊 Histórico de datos
├── INTEGRATION_GUIDE.md         🤝 Integración
├── IDEAS_EXPANSION.md           💡 Ideas futuras
├── COMPATIBILIDAD.md            🌐 Compatibilidad
└── REQUIREMENTS.md              📋 Requisitos
```

---

## 🎯 Flujo de Lectura Recomendado

### **Usuario Nuevo:**
1. README.md - Leer sección "Características"
2. QUICKSTART.md - Instalar y ejecutar
3. THEMES_GUIDE.md - Personalizar colores
4. Explorar las 15 ventanas del dashboard 🎉

### **Usuario Avanzado:**
1. README.md completo
2. PROCESS_MONITOR_GUIDE.md - Gestión avanzada
3. SERVICE_MONITOR_GUIDE.md - Control de servicios
4. HISTORICO_DATOS_GUIDE.md - Análisis de datos
5. QUICKSTART.md sección Homebridge - Control de accesorios HomeKit
6. QUICKSTART.md sección Telegram - Alertas externas

### **Desarrollador:**
1. ARCHITECTURE.md - Estructura del proyecto
2. README.md sección "Arquitectura"
3. `ui/styles.py` → `make_window_header()` para añadir nuevas ventanas
4. Código fuente en `core/` y `ui/`
5. IDEAS_EXPANSION.md - Ver qué se puede añadir

---

## 🔍 Buscar por Tema

### **¿Cómo hacer X?**
- **Cambiar tema** → THEMES_GUIDE.md
- **Instalar** → QUICKSTART.md o INSTALL_GUIDE.md
- **Ver procesos** → PROCESS_MONITOR_GUIDE.md
- **Gestionar servicios** → SERVICE_MONITOR_GUIDE.md
- **Ver histórico** → HISTORICO_DATOS_GUIDE.md
- **Configurar ventiladores** → FAN_CONTROL_GUIDE.md
- **Integrar con OLED** → INTEGRATION_GUIDE.md
- **Configurar Homebridge** → QUICKSTART.md sección Homebridge
- **Configurar alertas Telegram** → QUICKSTART.md sección Telegram / README.md
- **Ver logs del dashboard** → Botón "Visor de Logs" en el menú principal
- **Añadir nueva ventana con header** → `ui/styles.py` → `make_window_header()`
- **Añadir funciones** → ARCHITECTURE.md + IDEAS_EXPANSION.md

### **¿Tengo un problema?**
- **No arranca** → QUICKSTART.md sección "Problemas Comunes"
- **Ventiladores no funcionan** → FAN_CONTROL_GUIDE.md
- **Temperatura no se lee** → INSTALL_GUIDE.md
- **Speedtest falla** → README.md sección "Instalación Manual" (CLI Ookla)
- **Base de datos crece** → HISTORICO_DATOS_GUIDE.md
- **Servicios no se gestionan** → SERVICE_MONITOR_GUIDE.md
- **Homebridge no conecta** → QUICKSTART.md sección Homebridge / README.md Troubleshooting
- **Alertas Telegram no llegan** → README.md sección Telegram / verificar `.env`
- **Otro problema** → README.md sección "Troubleshooting"

---

## 📊 Estadísticas del Proyecto v3.1

- **Archivos Python**: 45
- **Ventanas**: 15 ventanas funcionales
- **Temas**: 15 temas pre-configurados
- **Documentos**: 12 guías
- **Servicios background**: 8 (FanAuto + SystemMonitor + ServiceMonitor + DataCollection + Cleanup + Homebridge + AlertService + main)
- **Badges en menú**: 9
- **Exports organizados**: 3 carpetas (csv, logs, screenshots) — máx. 10 por tipo
- **Tipos Homebridge**: 5 (switch, light, thermostat, sensor, blind)

---

## 🆕 Novedades en v3.1

### **Funcionalidades Nuevas:**
- ✅ **Alertas Telegram** — `AlertService` con anti-spam (edge-trigger + sustain 60s), monitoriza temp/CPU/RAM/disco y servicios fallidos, sin dependencias nuevas
- ✅ **Homebridge extendido** — 5 tipos de dispositivo: switch, luz regulable, termostato, sensor temperatura/humedad, persiana/estor
- ✅ **UI diálogo salir** — radiobuttons táctiles 30×30px, botones ajustados, layout corregido

---

## 📊 Evolución de la Documentación

| Versión | Documentos | Características |
|---------|------------|-----------------|
| **v1.0** | 8 | Básico |
| **v2.0** | 10 | + Procesos, Temas |
| **v2.5** | 12 | + Servicios, Histórico |
| **v2.6** | 12 | + Badges, CleanupService |
| **v2.7** | 12 | + Header unificado, Speedtest Ookla |
| **v2.8** | 12 | + Homebridge, 9 badges |
| **v2.9** | 14 | + Switches táctiles, caché background |
| **v3.0** | 15 | + Visor Logs, exports organizados, fix entries |
| **v3.1** | 15 | + Alertas Telegram, Homebridge extendido ⭐ |

---

## 📧 Ayuda Adicional

**¿No encuentras lo que buscas?**

1. Busca en README.md (Ctrl+F)
2. Revisa los ejemplos en las guías
3. Abre un Issue en GitHub
4. Revisa el código fuente (está comentado)

---

## 🔗 Enlaces Rápidos

| Tema | Documento |
|------|-----------|
| **Inicio Rápido** | [QUICKSTART.md](QUICKSTART.md) |
| **Características** | [README.md#características](README.md#características-principales) |
| **Instalación** | [INSTALL_GUIDE.md](INSTALL_GUIDE.md) |
| **Temas** | [THEMES_GUIDE.md](THEMES_GUIDE.md) |
| **Procesos** | [PROCESS_MONITOR_GUIDE.md](PROCESS_MONITOR_GUIDE.md) |
| **Servicios** | [SERVICE_MONITOR_GUIDE.md](SERVICE_MONITOR_GUIDE.md) |
| **Histórico** | [HISTORICO_DATOS_GUIDE.md](HISTORICO_DATOS_GUIDE.md) |
| **Homebridge** | [QUICKSTART.md#homebridge](QUICKSTART.md#-configurar-homebridge) |
| **Telegram** | [QUICKSTART.md#telegram](QUICKSTART.md#-configurar-alertas-telegram) |
| **Troubleshooting** | [README.md#troubleshooting](README.md#troubleshooting) |
| **Ideas Futuras** | [IDEAS_EXPANSION.md](IDEAS_EXPANSION.md) |

---

**¡Toda la información que necesitas está aquí!** 📚✨
