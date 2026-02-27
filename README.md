# 🖥️ Sistema de Monitoreo y Control - Dashboard v3.3

Sistema completo de monitoreo y control para Raspberry Pi con interfaz gráfica DSI, control de ventiladores PWM, temas personalizables, histórico de datos, gestión avanzada del sistema, integración con Homebridge, alertas externas por Telegram, escáner de red local, integración Pi-hole, gestor VPN, control de brillo y pantalla de resumen.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![Version](https://img.shields.io/badge/Version-3.3-orange.svg)]()

---

## ✨ Características Principales

### 🖥️ **Monitoreo Completo del Sistema**
- **CPU**: Uso en tiempo real, frecuencia, gráficas históricas
- **RAM**: Memoria usada/total, porcentaje, visualización dinámica
- **Temperatura**: Monitoreo de CPU con alertas por color
- **Disco**: Espacio usado/disponible, temperatura NVMe, I/O en tiempo real

### 🪟 **UI Unificada con Header Táctil**
- **Header en todas las ventanas**: título + status dinámico + botón ✕ (52×42px táctil)
- **Status en tiempo real** en el header: CPU/RAM/Temp (Monitor Placa), Disco/NVMe (Monitor Disco), interfaz/velocidades (Monitor Red)
- **Botón ✕ táctil** optimizado para pantalla DSI de 4,5" sin teclado
- Función `make_window_header()` centralizada en `ui/styles.py`

### 🌡️ **Control Inteligente de Ventiladores**
- **5 Modos**: Auto (curva), Manual, Silent (30%), Normal (50%), Performance (100%)
- **Curvas personalizables**: Define hasta 8 puntos temperatura-PWM
- **Servicio background**: Funciona incluso con ventana cerrada
- **Visualización en vivo**: Gráfica de curva activa y PWM actual

### 🌐 **Monitor de Red Avanzado**
- **Tráfico en tiempo real**: Download/Upload con gráficas
- **Auto-detección**: Interfaz activa (eth0, wlan0, tun0)
- **Lista de IPs**: Todas las interfaces con iconos por tipo
- **Speedtest integrado**: CLI oficial de Ookla (JSON nativo, resultados en MB/s reales)
- **Status en header**: interfaz activa + velocidades actuales

### 🖧 **Escáner de Red Local** *(nuevo en v3.2)*
- **Escaneo con arp-scan**: Detecta todos los dispositivos activos en la red local
- **Información por dispositivo**: IP, MAC y fabricante (OUI lookup)
- **Auto-refresco cada 60s** en background sin bloquear la UI
- **Lista scrollable** con todos los dispositivos encontrados
- **Sudoers preconfigurado**: `usuario ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan`

### 🕳️ **Integración Pi-hole v6** *(nuevo en v3.2)*
- **API v6 nativa**: autenticación por sesión (`POST /api/auth` → sid), compatible con Pi-hole v6
- **Estadísticas en tiempo real**: consultas totales, bloqueadas, porcentaje de bloqueo, clientes activos, dominios en lista negra
- **Renovación automática de sesión**: refresca antes de que expire (margen de 60s sobre 1800s)
- **Logout limpio**: `DELETE /api/auth` al parar el servicio
- **Badge en menú**: 🔴 si Pi-hole está offline
- **Configuración por `.env`**: `PIHOLE_HOST`, `PIHOLE_PORT`, `PIHOLE_PASSWORD`

### 📲 **Alertas Externas por Telegram**
- **Sin dependencias nuevas**: usa `urllib` de la stdlib de Python
- **Métricas monitorizadas**: temperatura, CPU, RAM, disco y servicios fallidos
- **Umbrales configurables**: warn y crit independientes por métrica
- **Anti-spam inteligente**: edge-trigger + sustain de 60s (condición debe mantenerse antes de enviar)
- **Reseteo automático**: cuando la condición baja del umbral, permite una nueva alerta en el siguiente flanco
- **Configurable por `.env`**: `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID`
- **Mensaje de prueba**: `alert_service.send_test()` para verificar la configuración

### 🔔 **Historial de Alertas** *(nuevo en v3.2)*
- **Registro persistente**: guarda en `data/alert_history.json` cada alerta enviada a Telegram
- **Máximo 100 entradas** (FIFO — las más antiguas se descartan)
- **Ventana dedicada**: tarjetas con franja de color lateral (naranja=aviso, rojo=crítico)
- **Información completa**: tipo de alerta, valor, unidad y timestamp
- **Orden cronológico inverso**: la alerta más reciente aparece primero
- **Acciones**: actualizar lista y borrar historial completo con confirmación

### 🏠 **Integración Homebridge Extendida**
- **5 tipos de dispositivo**: switch/enchufe, luz regulable (brillo), termostato, sensor temperatura/humedad, persiana/estor
- **CTkSwitch táctil** (90×46px): Toggle grande optimizado para uso con el dedo en pantalla DSI
- **Tarjetas adaptativas**: Cada tipo muestra su propia interfaz de control
  - **Luces**: switch ON/OFF igual que enchufes
  - **Termostatos**: temperatura actual + botones +/− 0.5°C para temperatura objetivo
  - **Sensores**: temperatura y/o humedad en modo solo lectura
  - **Persianas**: posición actual (%) con barra visual (control desde HomeKit)
- **Indicador visual**: switch verde ON / gris OFF, ⚠ rojo bloqueado si `StatusFault=1`
- **Sondeo ligero en background**: Cada 30 segundos sin bloquear la UI
- **Autenticación JWT** con renovación automática en 401
- **3 badges en el menú**: offline (🔴), dispositivos encendidos (🟠), dispositivos con fallo (🔴)
- **Configuración por `.env`**: IP, puerto, usuario y contraseña de Homebridge
- Requiere **Insecure Mode** activado en Homebridge para acceder a accesorios

### ⚙️ **Monitor de Procesos**
- **Lista en tiempo real**: Top 20 procesos con CPU/RAM
- **Búsqueda inteligente**: Por nombre o comando completo
- **Filtros**: Todos / Usuario / Sistema
- **Terminar procesos**: Con confirmación y feedback

### ⚙️ **Monitor de Servicios systemd**
- **Gestión completa**: Start/Stop/Restart servicios
- **Estado visual**: active, inactive, failed con iconos
- **Autostart**: Enable/Disable con confirmación
- **Logs en tiempo real**: Ver últimas 50 líneas
- **Caché en background**: Sondeo cada 10s sin bloquear la UI; `is-enabled` en llamada batch

### 📊 **Histórico de Datos**
- **Recolección automática**: Cada 5 minutos en background
- **Base de datos SQLite**: Ligera y eficiente
- **Visualización gráfica**: 8 gráficas (CPU, RAM, Temperatura, Red Download, Red Upload, Disk Read, Disk Write, PWM)
- **Periodos**: 24 horas, 7 días, 30 días
- **Estadísticas**: Promedios, mínimos, máximos
- **Detección de anomalías**: Alertas automáticas
- **Exportación CSV**: Para análisis externo

### 󱇰 **Monitor USB**
- **Detección automática**: Dispositivos conectados
- **Separación inteligente**: Mouse/teclado vs almacenamiento
- **Expulsión segura**: Unmount + eject con confirmación

###  **Monitor de Disco**
- **Particiones**: Uso de espacio de todas las unidades
- **Temperatura NVMe**: Monitoreo térmico del SSD (smartctl/sysfs)
- **Velocidad I/O**: Lectura/escritura en MB/s
- **Status en header**: espacio disponible + temperatura NVMe en tiempo real

### 󱓞 **Lanzadores de Scripts**
- **Terminal integrada**: Visualiza la ejecución en tiempo real
- **Layout en grid**: Organización visual en columnas
- **Confirmación previa**: Diálogo antes de ejecutar

### 󰆧 **Actualizaciones del Sistema**
- **Verificación al arranque**: En background sin bloquear la UI
- **Sistema de caché 12h**: No repite `apt update` innecesariamente
- **Terminal integrada**: Instala viendo el output en vivo
- **Botón Buscar**: Fuerza comprobación manual

### 󰆧 **15 Temas Personalizables**
- **Cambio con un clic**: Reinicio automático
- **Paletas completas**: Cyberpunk, Matrix, Dracula, Nord, Tokyo Night, etc.
- **Preview en vivo**: Ve los colores antes de aplicar

### /󰿅 **Reinicio y Apagado**
- **Botón Reiniciar**: Reinicia el dashboard aplicando cambios de código
- **Botón Salir**: Salir de la app o apagar el sistema con radiobuttons táctiles (30×30px)
- **Terminal de apagado**: Visualiza `apagado.sh` en tiempo real
- **Con confirmación**: Evita acciones accidentales

### 📋 **Visor de Logs**
- **Filtros avanzados**: Por nivel (DEBUG/INFO/WARNING/ERROR), módulo, texto libre e intervalo de fechas/horas
- **Colores por nivel**: gris / azul / naranja / rojo
- **Selector rápido**: 15min, 1h, 6h, 24h o rango manual
- **Exportación**: Guarda el resultado filtrado en `data/exports/logs/`
- **Recarga manual**: Lee también el archivo rotado `.log.1`

### 🔔 **Badges de Notificación Visual**
- **12 badges** en el menú principal con alertas en tiempo real
- **Temperatura**: naranja >60°C, rojo >70°C (Control Ventiladores + Monitor Placa)
- **CPU y RAM**: naranja >75%, rojo >90% (Monitor Placa)
- **Disco**: naranja >80%, rojo >90% (Monitor Disco)
- **Servicios fallidos**: rojo con contador (Monitor Servicios)
- **Actualizaciones pendientes**: naranja con contador (Actualizaciones)
- **Homebridge offline**: rojo si sin conexión
- **Dispositivos encendidos**: naranja con contador
- **Dispositivos con fallo**: rojo si `StatusFault=1`
- **Pi-hole offline**: rojo si sin conexión *(v3.2)*
- **VPN offline**: rojo si VPN desconectada *(nuevo en v3.3)*

### 📊 **Resumen del Sistema / Pantalla de Reposo** *(nuevo en v3.3)*
- **Vista unificada**: CPU, RAM, Temperatura, Disco, Red y Servicios en un solo vistazo
- **Fila Pi-hole**: queries totales, bloqueadas y porcentaje de bloqueo en ancho completo
- **Refresco cada 2s** leyendo directamente los cachés de los monitores — sin servicio adicional
- **Colores por umbrales** en cada tarjeta (verde → naranja → rojo)
- **Ideal como pantalla de reposo**: siempre visible sin abrir otras ventanas

### 💡 **Control de Brillo de Pantalla** *(nuevo en v3.3)*
- **Detección automática** del método disponible: `sysfs` (backlight kernel), `wlr-randr` (Wayland) o `xrandr` (X11)
- **Compatible con Freenove FNK0100K**: detecta la ruta de backlight o usa `wlr-randr` en Raspberry Pi OS Bookworm
- **Slider táctil** de 0-100% con 4 niveles rápidos predefinidos
- **Modo ahorro**: dim automático al 20% tras 2 minutos de inactividad, apagado completo a los 4 minutos
- **Encendido/Apagado** de pantalla con un botón
- **Persistencia** del nivel entre reinicios en `data/display_state.json`

### 🔒 **Gestor de Conexiones VPN** *(nuevo en v3.3)*
- **Estado en tiempo real**: conectado/desconectado, IP asignada e interfaz activa (`tun0`/`wg0`)
- **Compatible con WireGuard y OpenVPN**: detecta la interfaz vía `ip addr show`
- **Conectar/Desconectar** desde la UI usando los scripts existentes de Lanzadores — con terminal en vivo
- **Badge en menú**: 🔴 cuando la VPN está desconectada
- **Sondeo cada 10s** en background sin bloquear la UI
- **Fuerza sondeo inmediato** tras conectar/desconectar para reflejar el nuevo estado al instante


- **CleanupService**: servicio background singleton
- Limpia CSV exportados (máx. 10), PNG exportados (máx. 10), logs exportados (máx. 10)
- Limpieza automática también al exportar — no solo en el ciclo de 24h
- Limpia BD SQLite: registros >30 días cada 24h
- Red de seguridad: si BD supera 5MB limpia a 7 días al arrancar
- Botón "Limpiar Antiguos" fuerza limpieza manual completa

### 📋 **Sistema de Logging Completo**
- **Cobertura total**: Todos los módulos core y UI incluyendo todos los servicios background
- **Niveles diferenciados**: DEBUG, INFO, WARNING, ERROR
- **Rotación automática**: 2MB máximo con backup
- **Ubicación**: `data/logs/dashboard.log`
- **Todos los servicios** registran inicio y parada en el log

---

## 📦 Instalación

###  **Requisitos del Sistema**
- **Hardware**: Raspberry Pi 3/4/5
- **OS**: Raspberry Pi OS (Bullseye/Bookworm) o Kali Linux
- **Pantalla**: Touchscreen DSI 4,5" (800x480) o HDMI
- **Python**: 3.8 o superior

### ⚡ **Instalación Recomendada**

Usa el script de instalación directa (sin entorno virtual):

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

El script `install_system.sh` instala automáticamente:
- Dependencias del sistema (`lm-sensors`, `usbutils`, `udisks2`, `arp-scan`)
- Dependencias Python con `--break-system-packages`
- CLI oficial de Ookla para speedtest
- Ofrece configurar sensores de temperatura

### 🛠️ **Instalación Manual**

Si prefieres instalar paso a paso:

```bash
# 1. Dependencias del sistema
sudo apt-get update
sudo apt-get install -y lm-sensors usbutils udisks2 smartmontools arp-scan

# 2. CLI oficial de Ookla (speedtest)
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest

# 3. Detectar sensores
sudo sensors-detect --auto

# 4. Dependencias Python
pip3 install --break-system-packages -r requirements.txt

# 5. Sudoers para arp-scan (Red Local)
echo "usuario ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan" | sudo tee /etc/sudoers.d/arp-scan

# 6. Ejecutar
python3 main.py
```

###  **Alternativa con Entorno Virtual**

Si prefieres aislar las dependencias Python:

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
```

> **Nota**: Con venv necesitas activar el entorno (`source venv/bin/activate`) cada vez antes de ejecutar.

---

## 🏠 Configuración de Homebridge

La integración con Homebridge requiere un archivo `.env` en la raíz del proyecto:

```env
HOMEBRIDGE_HOST=192.168.1.X    # IP de la Raspberry Pi con Homebridge
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña
```

> **Importante**: Activa el **Insecure Mode** en Homebridge (`homebridge-config-ui-x → Configuración → Homebridge`) para que la API permita acceder y controlar los accesorios.

El archivo `.env` está en `.gitignore` y nunca se sube al repositorio.

La ventana Homebridge muestra los accesorios en un grid de 2 columnas con tarjetas adaptativas según el tipo de dispositivo.

---

## 🕳️ Configuración de Pi-hole

Añade al archivo `.env` existente:

```env
PIHOLE_HOST=192.168.1.X        # IP del servidor Pi-hole
PIHOLE_PORT=80                 # Puerto (80 por defecto)
PIHOLE_PASSWORD=tu_contraseña  # Contraseña del panel web Pi-hole v6
```

> Compatible exclusivamente con **Pi-hole v6**. La API v5 (`api.php` + token) no está soportada.

Si `PIHOLE_PASSWORD` no está configurado, `PiholeMonitor` arranca igualmente pero registra un warning y muestra el badge offline.

---

## 📲 Configuración de Alertas Telegram

Añade al archivo `.env` existente:

```env
TELEGRAM_TOKEN=123456789:ABCdefGHI...   # Token del bot (@BotFather)
TELEGRAM_CHAT_ID=987654321              # ID del chat o canal destino
```

> Si `TELEGRAM_TOKEN` o `TELEGRAM_CHAT_ID` no están configurados, `AlertService` arranca igualmente pero registra un warning y no envía nada.

Para verificar la configuración desde Python:

```python
alert_service.send_test()
```

### Umbrales por defecto

| Métrica  | Aviso (🟠) | Crítico (🔴) |
|----------|-----------|------------|
| Temperatura | 60°C | 70°C |
| CPU | 85% | 95% |
| RAM | 85% | 95% |
| Disco | 85% | 95% |
| Servicios | — | cualquier FAILED |

---

## 󰍜 Menú Principal (21 botones)

```
┌─────────────────────────────────────┐
│  Control         │  Monitor          │
│  Ventiladores    │  Placa            │
├──────────────────┼───────────────────┤
│  Monitor         │  Monitor          │
│  Red             │  USB              │
├──────────────────┼───────────────────┤
│  Monitor         │  Lanzadores       │
│  Disco           │                   │
├──────────────────┼───────────────────┤
│  Monitor         │  Monitor          │
│  Procesos        │  Servicios        │
├──────────────────┼───────────────────┤
│  Histórico       │  Actualizaciones  │
│  Datos           │                   │
├──────────────────┼───────────────────┤
│  Homebridge      │  Visor de Logs    │
├──────────────────┼───────────────────┤
│  🖧 Red Local    │  🕳 Pi-hole       │
├──────────────────┼───────────────────┤
│  🔒 Gestor VPN  │  🔔 Historial     │
│                  │  Alertas          │
├──────────────────┼───────────────────┤
│  💡 Brillo       │  📊 Resumen       │
│  Pantalla        │  Sistema          │
├──────────────────┼───────────────────┤
│  Cambiar Tema    │  Reiniciar        │
├──────────────────┼───────────────────┤
│  Salir           │                   │
└──────────────────┴───────────────────┘
```

### **Las 19 Ventanas:**

1. **Control Ventiladores** - Configura modos y curvas PWM
2. **Monitor Placa** - CPU, RAM, temperatura en tiempo real (status en header)
3. **Monitor Red** - Tráfico, speedtest Ookla, interfaces e IPs (status en header)
4. **Monitor USB** - Dispositivos y expulsión segura
5. **Monitor Disco** - Espacio, temperatura NVMe, I/O (status en header)
6. **Lanzadores** - Ejecuta scripts con terminal en vivo
7. **Monitor Procesos** - Gestión avanzada de procesos
8. **Monitor Servicios** - Control de servicios systemd
9. **Histórico Datos** - Visualización de métricas históricas con exportación CSV
10. **Actualizaciones** - Gestión de paquetes del sistema
11. **Homebridge** - Control de 5 tipos de dispositivos HomeKit
12. **Visor de Logs** - Visualización y exportación del log del dashboard
13. **🖧 Red Local** *(v3.2)* - Escáner arp-scan con IP, MAC y fabricante
14. **🕳 Pi-hole** *(v3.2)* - Estadísticas de bloqueo DNS en tiempo real
15. **🔒 Gestor VPN** *(v3.3)* - Estado en tiempo real + conectar/desconectar
16. **🔔 Historial Alertas** *(v3.2)* - Registro persistente de alertas Telegram enviadas
17. **💡 Brillo Pantalla** *(v3.3)* - Control de brillo DSI con modo ahorro
18. **📊 Resumen Sistema** *(v3.3)* - Vista unificada de todas las métricas
19. **Cambiar Tema** - Selecciona entre 15 temas

---

## 󰔎 Temas Disponibles

| Tema | Colores | Estilo |
|------|---------|--------|
| **Cyberpunk** | Cyan + Verde | Original neón |
| **Matrix** | Verde brillante | Película Matrix |
| **Sunset** | Naranja + Púrpura | Atardecer cálido |
| **Ocean** | Azul + Aqua | Océano refrescante |
| **Dracula** | Púrpura + Rosa | Elegante oscuro |
| **Nord** | Azul hielo | Minimalista nórdico |
| **Tokyo Night** | Azul + Púrpura | Noche de Tokio |
| **Monokai** | Cyan + Verde | IDE clásico |
| **Gruvbox** | Naranja + Beige | Retro cálido |
| **Solarized** | Azul + Cyan | Científico |
| **One Dark** | Azul claro | Atom editor |
| **Synthwave** | Rosa + Verde | Neón 80s |
| **GitHub Dark** | Azul GitHub | Profesional |
| **Material** | Azul material | Google Design |
| **Ayu Dark** | Azul cielo | Minimalista |

---

## 📊 Arquitectura del Proyecto

```
system_dashboard/
├── config/
│   ├── settings.py                 # Constantes globales, LAUNCHERS y rutas de exports
│   └── themes.py                   # 15 temas pre-configurados
├── core/
│   ├── fan_controller.py           # Control PWM y curvas
│   ├── fan_auto_service.py         # Servicio background ventiladores
│   ├── system_monitor.py           # CPU, RAM, temp — caché en background thread
│   ├── network_monitor.py          # Red, speedtest Ookla CLI, interfaces
│   ├── network_scanner.py          # Escáner arp-scan (Red Local) — v3.2
│   ├── disk_monitor.py             # Disco, NVMe, I/O
│   ├── process_monitor.py          # Gestión de procesos
│   ├── service_monitor.py          # Servicios systemd — caché 10s, batch is-enabled
│   ├── update_monitor.py           # Actualizaciones con caché 12h
│   ├── homebridge_monitor.py       # Integración Homebridge (JWT, sondeo 30s, 5 tipos)
│   ├── pihole_monitor.py           # Integración Pi-hole v6 (sesión sid, sondeo) — v3.2
│   ├── alert_service.py            # Alertas Telegram + historial JSON — v3.2
│   ├── display_service.py          # Control brillo DSI (sysfs/wlr-randr/xrandr) — v3.3
│   ├── vpn_monitor.py              # Monitor VPN (tun0/wg0, sondeo 10s) — v3.3
│   ├── data_logger.py              # SQLite logging
│   ├── data_analyzer.py            # Análisis histórico
│   ├── data_collection_service.py  # Recolección automática (singleton)
│   ├── cleanup_service.py          # Limpieza automática background (singleton)
│   └── __init__.py
├── ui/
│   ├── main_window.py              # Ventana principal (21 botones + badges)
│   ├── styles.py                   # make_window_header(), make_futuristic_button(),
│   │                               # make_homebridge_switch(), StyleManager
│   ├── widgets/
│   │   ├── graphs.py               # Gráficas personalizadas
│   │   └── dialogs.py              # custom_msgbox, confirm_dialog, terminal_dialog
│   └── windows/
│       ├── monitor.py, network.py, usb.py, disk.py
│       ├── process_window.py, service.py, history.py
│       ├── update.py, fan_control.py
│       ├── launchers.py, theme_selector.py
│       ├── homebridge.py           # 5 tarjetas adaptativas por tipo de dispositivo
│       ├── log_viewer.py           # Visor de logs con filtros y exportación
│       ├── network_local.py        # Escáner de red local (arp-scan) — v3.2
│       ├── pihole_window.py        # Estadísticas Pi-hole v6 — v3.2
│       ├── alert_history.py        # Historial de alertas Telegram — v3.2
│       ├── vpn_window.py           # Gestor VPN — v3.3
│       ├── display_window.py       # Control de brillo DSI — v3.3
│       ├── overview.py             # Resumen del sistema / pantalla reposo — v3.3
│       └── __init__.py
├── utils/
│   ├── file_manager.py             # Gestión de JSON (escritura atómica)
│   ├── system_utils.py             # Utilidades del sistema
│   └── logger.py                   # DashboardLogger (rotación 2MB)
├── data/                            # Auto-generado al ejecutar
│   ├── fan_state.json, fan_curve.json, theme_config.json
│   ├── alert_history.json          # Historial de alertas (máx. 100) — v3.2
│   ├── display_state.json          # Brillo de pantalla persistido — v3.3
│   ├── history.db                  # SQLite histórico
│   ├── logs/dashboard.log          # Log del sistema
│   └── exports/                    # Archivos exportados (máx. 10 por tipo)
│       ├── csv/                    # Exportaciones CSV del histórico
│       ├── logs/                   # Exportaciones del visor de logs
│       └── screenshots/            # Capturas de gráficas
├── scripts/                         # Scripts personalizados del usuario
├── .env                             # Credenciales Homebridge + Telegram + Pi-hole (NO en git)
├── .env.example                     # Plantilla de configuración
├── install_system.sh               # Instalación directa (recomendada)
├── install.sh                      # Instalación con venv (alternativa)
├── main.py
└── requirements.txt
```

---

##  Configuración

### **`config/settings.py`**

```python
# Posición en pantalla DSI
DSI_WIDTH = 800
DSI_HEIGHT = 480
DSI_X = 0
DSI_Y = 0

# Scripts personalizados en Lanzadores
LAUNCHERS = [
    {"label": "Montar NAS",   "script": str(SCRIPTS_DIR / "montarnas.sh")},
    {"label": "Conectar VPN", "script": str(SCRIPTS_DIR / "conectar_vpn.sh")},
    # Añade tus scripts aquí
]
```

### **`.env` (Homebridge + Telegram + Pi-hole)**

```env
HOMEBRIDGE_HOST=192.168.1.X
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña

TELEGRAM_TOKEN=123456789:ABCdefGHI...
TELEGRAM_CHAT_ID=987654321

PIHOLE_HOST=192.168.1.X
PIHOLE_PORT=80
PIHOLE_PASSWORD=tu_contraseña_pihole
```

---

## 📋 Sistema de Logging

```bash
# Ver logs en tiempo real
tail -f data/logs/dashboard.log

# Solo errores
grep ERROR data/logs/dashboard.log

# Eventos de hoy
grep "$(date +%Y-%m-%d)" data/logs/dashboard.log
```

**Niveles:** `DEBUG` (operaciones normales) · `INFO` (eventos importantes) · `WARNING` (degradación) · `ERROR` (fallos)

Todos los servicios background registran su inicio y parada. Al arrancar verás entradas como:
```
[SystemMonitor]     Sondeo iniciado (cada 2.0s)
[ServiceMonitor]    Sondeo iniciado (cada 10s)
[HomebridgeMonitor] Sondeo iniciado (cada 30s)
[PiholeMonitor]     Sondeo iniciado (cada 60s)
[FanAutoService]    Servicio iniciado
[DataCollection]    Servicio iniciado (cada 5 min)
[CleanupService]    Servicio iniciado
[AlertService]      Servicio iniciado (cada 15s)
```

---

## 📈 Rendimiento

- **Uso CPU**: ~5-10% en idle
- **Uso RAM**: ~100-150 MB
- **Base de datos**: ~5 MB por 10,000 registros
- **Actualización UI**: 2 segundos (configurable en `UPDATE_MS`) — solo lectura de caché, sin syscalls bloqueantes
- **Threads background**: 12 (FanAuto + SystemMonitor + ServiceMonitor + DataCollection + Cleanup + Homebridge + AlertService + PiholeMonitor + NetworkScanner + VpnMonitor + DisplayService(timer) + main)
- **Log**: máx. 2MB con rotación automática

---

##  Troubleshooting

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto && sudo systemctl restart lm-sensors` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Ventiladores no responden | `sudo python3 main.py` |
| Speedtest falla | Instalar CLI oficial Ookla: ver sección Instalación Manual |
| USB no expulsa | `sudo apt install udisks2` |
| Homebridge no conecta | Verificar IP/puerto en `.env` y que Insecure Mode esté activo |
| Badge hb_offline siempre rojo | Comprobar `HOMEBRIDGE_HOST` en `.env` y red entre Pis |
| Red Local no escanea | `sudo apt install arp-scan` y configurar sudoers |
| Pi-hole no conecta | Verificar `PIHOLE_HOST` y `PIHOLE_PASSWORD` en `.env`; solo compatible con v6 |
| VPN badge siempre rojo | Verificar que `VPN_INTERFACE` en `vpn_monitor.py` coincide con tu interfaz (`tun0`/`wg0`) |
| Brillo no disponible | Ejecutar diagnóstico del Paso 0 en `GUIA_BRILLO_DSI.md`; instalar `wlr-randr` si Wayland |
| Servicios tardan en aparecer | Normal — ServiceMonitor sondea systemctl cada 10s al arrancar |
| No puedo escribir en los entries | Asegúrate de usar v3.0+ — el bug de `grab_set` está corregido |
| Alertas Telegram no llegan | Verificar `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` en `.env`; ejecutar `send_test()` |
| Historial alertas vacío | Las alertas solo se guardan si Telegram está configurado y el envío tiene éxito |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 📚 Documentación

- [QUICKSTART.md](QUICKSTART.md) — Inicio rápido
- [INSTALL_GUIDE.md](INSTALL_GUIDE.md) — Instalación detallada
- [THEMES_GUIDE.md](THEMES_GUIDE.md) — Guía de temas
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) — Integración con OLED
- [INDEX.md](INDEX.md) — Índice completo

---

## 📊 Estadísticas del Proyecto

| Métrica | Valor |
|---------|-------|
| Versión | 3.3 |
| Archivos Python | 53 |
| Ventanas | 19 |
| Temas | 15 |
| Servicios background | 12 (FanAuto + SystemMonitor + ServiceMonitor + DataCollection + Cleanup + Homebridge + AlertService + PiholeMonitor + NetworkScanner + VpnMonitor + DisplayService + main) |
| Badges en menú | 12 |
| Cobertura logging | 100% módulos core y UI |
| Exports organizados | 3 carpetas (csv, logs, screenshots) — máx. 10 por tipo |
| Tipos Homebridge | 5 (switch, light, thermostat, sensor, blind) |

---

## Changelog

### **v3.3** - 2026-02-27 ⭐ ACTUAL
- ✅ **NUEVO**: Resumen del Sistema — `OverviewWindow` con grid de 6 tarjetas (CPU, RAM, Temp, Disco, Red, Servicios) + fila Pi-hole, refresco 2s, ideal como pantalla de reposo
- ✅ **NUEVO**: Control de Brillo DSI — `DisplayService` con detección automática de método (sysfs/wlr-randr/xrandr), slider táctil, modo ahorro por inactividad, persistencia en JSON
- ✅ **NUEVO**: Gestor VPN — `VpnMonitor` con sondeo 10s via `ip addr show`, badge en menú, conectar/desconectar con terminal en vivo reutilizando scripts existentes
- ✅ **MEJORA**: Menú principal ampliado de 18 a 21 botones; uptime en cabecera

### **v3.2** - 2026-02-27
- ✅ **NUEVO**: Escáner de Red Local — `NetworkScanner` con arp-scan, IP/MAC/fabricante, auto-refresco 60s, ventana `NetworkLocalWindow`
- ✅ **NUEVO**: Integración Pi-hole v6 — `PiholeMonitor` con API v6 (sesión sid), estadísticas en tiempo real, badge offline en menú, ventana `PiholeWindow`
- ✅ **NUEVO**: Historial de Alertas — persistencia en `data/alert_history.json` (máx. 100), ventana `AlertHistoryWindow` con tarjetas coloreadas por nivel
- ✅ **MEJORA**: Visor de Logs — filtro de módulo migrado de `CTkOptionMenu` a `CTkEntry`
- ✅ **MEJORA**: Menú principal ampliado de 15 a 18 botones

### **v3.1** - 2026-02-26
- ✅ **NUEVO**: Alertas externas por Telegram — `AlertService` con anti-spam (edge-trigger + sustain 60s), umbrales para temp/CPU/RAM/disco y servicios, sin dependencias nuevas (urllib stdlib)
- ✅ **NUEVO**: Homebridge extendido — soporte para 5 tipos de dispositivo: switch, luz regulable, termostato, sensor temperatura/humedad, persiana
- ✅ **NUEVO**: `set_brightness()` y `set_target_temp()` en `HomebridgeMonitor`
- ✅ **NUEVO**: Tarjetas adaptativas en `HomebridgeWindow` según tipo de dispositivo
- ✅ **MEJORA**: Diálogo salir — radiobuttons táctiles (30×30px), botones ajustados, layout corregido

### **v3.0** - 2026-02-26
- ✅ **NUEVO**: Visor de Logs — ventana con filtros por nivel, módulo, texto libre e intervalo de fechas/horas
- ✅ **NUEVO**: Exportación de logs filtrados a `data/exports/logs/`
- ✅ **NUEVO**: Carpetas organizadas para exports — `data/exports/{csv,logs,screenshots}` (creadas automáticamente al arrancar)
- ✅ **MEJORA**: Limpieza automática al exportar — no solo en el ciclo de 24h o al pulsar manualmente
- ✅ **MEJORA**: `CleanupService` gestiona ahora también logs exportados (máx. 10)
- ✅ **FIX**: Eliminado `grab_set()` en `FanControlWindow` que bloqueaba el teclado en todas las ventanas al cerrarse

### **v2.9** - 2026-02-24
- ✅ **MEJORA**: `SystemMonitor` — caché en background thread (cada 2s); la UI nunca llama psutil directamente
- ✅ **MEJORA**: `ServiceMonitor` — caché en background thread (cada 10s); `is-enabled` en llamada batch en lugar de N subprocesses
- ✅ **MEJORA**: `_update()` de `MainWindow` solo lee cachés — hilo de UI completamente libre de syscalls bloqueantes
- ✅ **MEJORA**: `HomebridgeWindow` usa `CTkSwitch` (90×46px) en lugar de botones ON/OFF — más intuitivo y táctil
- ✅ **MEJORA**: `make_homebridge_switch()` añadida a `ui/styles.py` con soporte de estado disabled (fallo)
- ✅ **MEJORA**: Todos los servicios background registran inicio y parada en el log (`FanAutoService` incluido)

### **v2.8** - 2026-02-23
- ✅ **NUEVO**: Integración Homebridge — ventana de control de accesorios HomeKit (enchufes e interruptores)
- ✅ **NUEVO**: `HomebridgeMonitor` en `core/` — sondeo ligero cada 30s, autenticación JWT con renovación automática
- ✅ **NUEVO**: 3 badges Homebridge en menú principal (`hb_offline` 🔴, `hb_on` 🟠, `hb_fault` 🔴)
- ✅ **NUEVO**: Toggle táctil por dispositivo con indicador ● color y ⚠ en StatusFault
- ✅ **NUEVO**: Configuración por `.env` (credenciales fuera del código)

### **v2.7** - 2026-02-23
- ✅ **NUEVO**: Header unificado `make_window_header()` en todas las ventanas (título + status + botón ✕ táctil 52×42px)
- ✅ **NUEVO**: Status dinámico en tiempo real en el header (CPU/RAM/Temp, Disco/NVMe, interfaz/velocidades)
- ✅ **MEJORA**: Speedtest migrado a CLI oficial de Ookla (`--format=json`), resultados en MB/s reales
- ✅ **MEJORA**: Botón ✕ táctil optimizado para pantalla DSI sin teclado

### **v2.6** - 2026-02-22
- ✅ **NUEVO**: 6 badges de notificación visual en menú principal
- ✅ **NUEVO**: `CleanupService` — limpieza automática background de CSV, PNG y BD
- ✅ **NUEVO**: Fan control con entries en lugar de sliders

### v2.5.1 - 2026-02-19
- Logging completo, Ventana Actualizaciones, Fix atexit DataCollectionService

### v2.5 - 2026-02-17
- Monitor Servicios systemd, Historico SQLite, Boton Reiniciar

### v2.0 - 2026-02-16
- Monitor Procesos, 15 temas, fix Speedtest

### v1.0 - 2025-01
- Release inicial

---

## Licencia

MIT License

---

## Agradecimientos

CustomTkinter - psutil - matplotlib - Ookla Speedtest CLI - Homebridge - Pi-hole - Raspberry Pi Foundation

---

Dashboard v3.3: Profesional, Unificado, Táctil, Auto-mantenido, conectado a HomeKit y Pi-hole, con Alertas Telegram, Historial, Gestor VPN, Control de Brillo y Pantalla de Resumen — sin bloqueos en UI
