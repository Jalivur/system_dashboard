# 🚀 Inicio Rápido - Dashboard v4.2

---

## ⚡ Instalación (2 Comandos)

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

El script instala automáticamente las dependencias del sistema y Python, la CLI oficial de Ookla para speedtest, y pregunta si quieres configurar sensores de temperatura.

---

## 🔁 Alternativa con Entorno Virtual

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
```

> Recuerda activar el entorno (`source venv/bin/activate`) cada vez que quieras ejecutar.

---

## 📋 Requisitos Mínimos

- ✅ Raspberry Pi 3/4/5
- ✅ Raspberry Pi OS (cualquier versión)
- ✅ Python 3.8+
- ✅ Conexión a internet (para instalación)

---

## 🖥️ Config por máquina (multi-Pi)

Si tienes varias Pi con configuraciones distintas, crea `config/local_settings.py` (en `.gitignore`, no se sube a git):

```python
# Ejemplo Pi 3B+ con Xvfb
DSI_X = 0
DSI_Y = 0
DSI_WIDTH = 1024
DSI_HEIGHT = 762
```

También puedes editarlo directamente desde la UI con el **Editor de Configuración**.

---

## 🗂️ Menú por Pestañas (v4.0)

El menú está organizado en **6 pestañas con scroll horizontal táctil**. Cada pestaña agrupa los botones por categoría:

| Pestaña | Botones |
|---------|---------|
| **Sistema** | Resumen, Monitor Placa, Monitor Disco, Monitor USB, Monitor Procesos, Actualizaciones |
| **Red** | Monitor Red, Red Local, Monitor WiFi, Monitor SSH, Pi-hole, VPN |
| **Hardware** | Info Hardware, Control Ventiladores, LEDs RGB, Brillo Pantalla, Audio Control, Cámara, I²C Scanner, GPIO Monitor |
| **Servicios** | Monitor Servicios, Servicios Dashboard, Gestor Crontab, Homebridge, Lanzadores, Service Watchdog |
| **Registros** | Histórico Datos, Historial Alertas, Visor Logs, Config Logging |
| **Config** | Editor Config, Cambiar Tema |

El **footer** (Gestor Botones, Reiniciar, Salir) es siempre visible independientemente de la pestaña activa.

> Puedes ocultar botones que no uses con el **Gestor de Botones**.

---

## 🖥️ Las 32 Ventanas

**1. Info Hardware** — Modelo, revisión, SoC, RAM, almacenamiento, uptime

**2. Control Ventiladores** — Modo Auto/Manual/Silent/Normal/Performance, curvas PWM

**3. LEDs RGB** — 6 modos (auto, apagado, color fijo, secuencial, respiración, arcoíris)

**4. Monitor Placa** — CPU, RAM, temperatura, temperatura chasis, fan duty real

**5. Monitor Red** — Download/Upload, speedtest Ookla, lista de IPs

**6. Monitor USB** — Dispositivos conectados, expulsión segura

**7. Monitor Disco** — Espacio, temperatura NVMe, velocidad I/O, SMART extendido

**8. Lanzadores** — Scripts personalizados con terminal en vivo

**9. Monitor Procesos** — Top 20 procesos, búsqueda, matar procesos

**10. Monitor Servicios** — Start/Stop/Restart systemd, ver logs

**11. Servicios Dashboard** — Activar/desactivar servicios background del dashboard

**12. Gestor Crontab** — Ver/añadir/editar/eliminar entradas del crontab por usuario

**13. Histórico Datos** — 8 gráficas CPU/RAM/Temp/Red/Disco/PWM en 24h, 7d, 30d

**14. Actualizaciones** — Estado de paquetes, instalar con terminal integrada

**15. Homebridge** — Control de 5 tipos de dispositivos HomeKit

**16. Visor de Logs** — Filtros por nivel, módulo, texto e intervalo; exportación

**17. Red Local** — Escáner arp-scan con IP, MAC y fabricante

**18. Pi-hole** — Estadísticas de bloqueo DNS en tiempo real (solo v6)

**19. Gestor VPN** — Estado, badge en menú, conectar/desconectar

**20. Historial Alertas** — Registro persistente de alertas Telegram enviadas

**21. Brillo Pantalla** — Control brillo DSI, modo ahorro, encendido/apagado

**22. Resumen Sistema** — Vista unificada de todas las métricas (ideal como reposo)

**23. Cámara / Escáner OCR** — Foto con OV5647 + OCR Tesseract local

**24. Cambiar Tema** — 15 temas (Cyberpunk, Matrix, Dracula, Nord...)

**25. Monitor SSH** — Sesiones activas e historial SSH con textos legibles

**26. Monitor WiFi** — Señal dBm, calidad, SSID, bitrate, tráfico RX/TX, selector de interfaz

**27. Editor Config** — Edita `local_settings.py` con preview de iconos en tiempo real

**28. Audio Control** — Volumen ALSA, mute, VU meter, selector de control

**29. Widget Clima** — Temperatura exterior, previsión, AQI, drill-down horas, favoritos

**30. I²C Scanner** — Dispositivos por bus, badge hex, escaneo manual

**31. GPIO Monitor/Control** — INPUT/OUTPUT/PWM por pin, toggle LIBRE/CONTROLANDO

**32. Service Watchdog** — Monitor servicios críticos con auto-reinicio y badge

**33. Config Logging** — Niveles de log en runtime por handler y módulo, persistentes

---

## 🔧 Configuración Básica

### Ajustar posición en pantalla:
Edita `config/settings.py` o usa el **Editor de Configuración** directamente desde la UI:
```python
DSI_X = 0
DSI_Y = 0
DSI_WIDTH = 800
DSI_HEIGHT = 480
```

### Añadir scripts en Lanzadores:
```python
LAUNCHERS = [
    {"label": "Mi Script", "script": str(SCRIPTS_DIR / "mi_script.sh")},
]
```

---

## 🏠 Configurar Homebridge

```env
HOMEBRIDGE_HOST=192.168.1.X
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña
```

> Activa el **Insecure Mode** en Homebridge.

---

## 📲 Configurar Alertas Telegram

```env
TELEGRAM_TOKEN=123456789:ABCdefGHI...
TELEGRAM_CHAT_ID=987654321
```

---

## 📋 Ver Logs del Sistema

```bash
tail -f data/logs/dashboard.log
grep ERROR data/logs/dashboard.log
```

> Para reducir el volumen del log, abre **Config Logging** (pestaña Registros) y sube el nivel de Fichero a `INFO` o `WARNING`.

---

## ❓ Problemas Comunes

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto` |
| Speedtest falla | Instalar CLI oficial Ookla |
| Pi-hole no conecta | Solo compatible con v6; verificar `.env` |
| GPIO pin busy | Usar modo LIBRE desde la ventana GPIO |
| I²C buses vacíos | Habilitar I²C en `raspi-config` |
| Audio sin control | `aplay -l` → verificar dispositivo activo |
| WiFi no lista interfaces | Verificar interfaces `wlan*` en `/proc/net/dev` |
| Uptime incorrecto | Normal sin RTC — se corrige al conectar red (NTP) |
| Log lleno de DEBUG | Config Logging → nivel Fichero a INFO o WARNING |
| Ver errores | `grep ERROR data/logs/dashboard.log` |
