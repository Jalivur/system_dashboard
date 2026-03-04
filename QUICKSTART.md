# 🚀 Inicio Rápido - Dashboard v3.8

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

Si tienes varias Pi con configuraciones distintas, crea `config/local_settings.py` (está en `.gitignore`, no se sube a git):

```python
# Ejemplo Pi 3B+ con Xvfb
DSI_X = 0
DSI_Y = 0
DSI_WIDTH = 1024
DSI_HEIGHT = 762
```

Este fichero sobreescribe los valores de `config/settings.py` sin tocar el repositorio.
También puedes editarlo directamente desde la UI con el **Editor de Configuración** *(v3.8)*.

---

## 🎯 Menú Principal (29 botones)

```
┌─────────────────────────────────────┐
│  Control         │  LEDs RGB         │
│  Ventiladores    │                   │
├──────────────────┼───────────────────┤
│  Monitor Placa   │  Monitor Red      │
├──────────────────┼───────────────────┤
│  Monitor USB     │  Monitor Disco    │
├──────────────────┼───────────────────┤
│  Lanzadores      │  Monitor Procesos │
├──────────────────┼───────────────────┤
│  Monitor         │  Servicios        │
│  Servicios       │  Dashboard        │
├──────────────────┼───────────────────┤
│  Gestor Crontab  │  Gestor Botones   │
├──────────────────┼───────────────────┤
│  Histórico Datos │  Actualizaciones  │
├──────────────────┼───────────────────┤
│  Homebridge      │  Visor de Logs    │
├──────────────────┼───────────────────┤
│  🖧 Red Local    │  🕳 Pi-hole       │
├──────────────────┼───────────────────┤
│  🔒 Gestor VPN  │  🔔 Historial     │
├──────────────────┼───────────────────┤
│  💡 Brillo       │  📊 Resumen       │
├──────────────────┼───────────────────┤
│  📷 Cámara       │  Cambiar Tema     │
├──────────────────┼───────────────────┤
│  Monitor SSH     │  Monitor WiFi     │
├──────────────────┼───────────────────┤
│  Editor Config   │  Info Hardware    │
├──────────────────┼───────────────────┤
│  Reiniciar       │  Salir            │
└──────────────────┴───────────────────┘
```

> Puedes ocultar botones que no uses con el **Gestor de Botones**.

---

## 🖥️ Las 27 Ventanas

**1. Control Ventiladores** — Modo Auto/Manual/Silent/Normal/Performance, curvas PWM

**2. LEDs RGB** — 6 modos (auto, apagado, color fijo, secuencial, respiración, arcoíris)

**3. Monitor Placa** — CPU, RAM, temperatura, temperatura chasis, fan duty real

**4. Monitor Red** — Download/Upload, speedtest Ookla, lista de IPs

**5. Monitor USB** — Dispositivos conectados, expulsión segura

**6. Monitor Disco** — Espacio, temperatura NVMe, velocidad I/O, SMART extendido

**7. Lanzadores** — Scripts personalizados con terminal en vivo

**8. Monitor Procesos** — Top 20 procesos, búsqueda, matar procesos

**9. Monitor Servicios** — Start/Stop/Restart systemd, ver logs

**10. Servicios Dashboard** — Activar/desactivar servicios background del dashboard

**11. Gestor Crontab** — Ver/añadir/editar/eliminar entradas del crontab por usuario

**12. Gestor de Botones** — Mostrar/ocultar botones del menú principal

**13. Histórico Datos** — 8 gráficas CPU/RAM/Temp/Red/Disco/PWM en 24h, 7d, 30d

**14. Actualizaciones** — Estado de paquetes, instalar con terminal integrada

**15. Homebridge** — Control de 5 tipos de dispositivos HomeKit

**16. Visor de Logs** — Filtros por nivel, módulo, texto e intervalo; exportación

**17. 🖧 Red Local** — Escáner arp-scan con IP, MAC y fabricante

**18. 🕳 Pi-hole** — Estadísticas de bloqueo DNS en tiempo real (solo v6)

**19. 🔒 Gestor VPN** — Estado, badge en menú, conectar/desconectar

**20. 🔔 Historial Alertas** — Registro persistente de alertas Telegram enviadas

**21. 💡 Brillo Pantalla** — Control brillo DSI, modo ahorro, encendido/apagado

**22. 📊 Resumen Sistema** — Vista unificada de todas las métricas (ideal como reposo)

**23. 📷 Cámara / Escáner OCR** — Foto con OV5647 + OCR Tesseract local

**24. Cambiar Tema** — 15 temas (Cyberpunk, Matrix, Dracula, Nord...)

**25. Monitor SSH** *(v3.8)* — Sesiones activas e historial SSH con textos legibles

**26. Monitor WiFi** *(v3.8)* — Señal dBm, calidad, SSID, bitrate, tráfico RX/TX

**27. Editor Config** *(v3.8)* — Edita `local_settings.py` con preview de iconos en tiempo real

---

## 🔧 Configuración Básica

### Ajustar posición en pantalla (`config/settings.py`):
```python
DSI_X = 0
DSI_Y = 0
DSI_WIDTH = 800
DSI_HEIGHT = 480
```

> También puedes usar el **Editor de Configuración** desde la propia UI *(v3.8)*.

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

> Activa el **Insecure Mode** en Homebridge (`homebridge-config-ui-x → Configuración → Homebridge`).

---

## 📲 Configurar Alertas Telegram

```env
TELEGRAM_TOKEN=123456789:ABCdefGHI...
TELEGRAM_CHAT_ID=987654321
```

Las alertas se envían cuando temp/CPU/RAM/disco superan umbrales durante 60s sostenidos (anti-spam). También avisa si hay servicios FAILED.

---

## 📋 Ver Logs del Sistema

```bash
tail -f data/logs/dashboard.log
grep ERROR data/logs/dashboard.log
```

---

## ❓ Problemas Comunes

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Speedtest falla | Instalar CLI Ookla: `sudo apt install speedtest` |
| USB no expulsa | `sudo apt install udisks2` |
| Homebridge no conecta | Revisar `.env` y activar Insecure Mode |
| WiFi no muestra datos | `sudo apt install wireless-tools` |
| SSH monitor vacío | Verificar que `who` y `last` funcionan en el sistema |
| No puedo escribir en entries (VNC) | Verificar que se usa `make_entry()` de `ui/styles.py` |
| Foco perdido tras inactividad (Wayland) | `gsettings set org.gnome.desktop.session idle-delay 0` |
| Dashboard no visible por VNC en Pi 5 | `wayvnc --output=DSI-2 0.0.0.0 5901` |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 📚 Más Información

**[README.md](README.md)** — Documentación completa
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — Instalación detallada
**[INDEX.md](INDEX.md)** — Índice de toda la documentación

---

**Dashboard v3.8** 🚀
