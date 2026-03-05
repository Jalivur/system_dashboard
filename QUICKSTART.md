# 🚀 Inicio Rápido - Dashboard v4.0

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
| **Sistema** | Resumen, Monitor Placa, Control Ventiladores, LEDs RGB, Brillo, Cámara, Lanzadores |
| **Red** | Monitor Red, Red Local, Pi-hole, VPN, Homebridge, Monitor WiFi |
| **Hardware** | Info Hardware, Monitor Disco, Monitor USB |
| **Servicios** | Monitor Servicios, Servicios Dashboard, Monitor Procesos, Gestor Crontab, Actualizaciones |
| **Registros** | Visor Logs, Histórico Datos, Historial Alertas, Monitor SSH |
| **Config** | Editor Config, Cambiar Tema, Gestor Botones |

El **footer** (Gestor Botones, Reiniciar, Salir) es siempre visible independientemente de la pestaña activa.

> Puedes ocultar botones que no uses con el **Gestor de Botones**.

---

## 🖥️ Las 27 Ventanas

**1. Info Hardware** — Modelo, revision, SoC, RAM, almacenamiento, uptime

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

**26. Monitor WiFi** — Señal dBm, calidad, SSID, bitrate, tráfico RX/TX

**27. Editor Config** — Edita `local_settings.py` con preview de iconos en tiempo real

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

**Dashboard v4.0** 🚀
