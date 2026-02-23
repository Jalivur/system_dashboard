# 🚀 Inicio Rápido - Dashboard v2.8

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

Si prefieres aislar las dependencias:

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
```

> Recuerda activar el entorno (`source venv/bin/activate`) cada vez que quieras ejecutar el dashboard.

---

## 📋 Requisitos Mínimos

- ✅ Raspberry Pi 3/4/5
- ✅ Raspberry Pi OS (cualquier versión)
- ✅ Python 3.8+
- ✅ Conexión a internet (para instalación)

---

## 🎯 Menú Principal (14 botones)

```
┌───────────────────────────────────┐
│  Control        │  Monitor         │
│  Ventiladores   │  Placa           │
├─────────────────┼──────────────────┤
│  Monitor        │  Monitor         │
│  Red            │  USB             │
├─────────────────┼──────────────────┤
│  Monitor        │  Lanzadores      │
│  Disco          │                  │
├─────────────────┼──────────────────┤
│  Monitor        │  Monitor         │
│  Procesos       │  Servicios       │
├─────────────────┼──────────────────┤
│  Histórico      │  Actualizaciones │
│  Datos          │                  │
├─────────────────┼──────────────────┤
│  Homebridge     │  Cambiar Tema    │
├─────────────────┼──────────────────┤
│  Reiniciar      │  Salir           │
└─────────────────┴──────────────────┘
```

---

## 🖥️ Las 14 Ventanas

**1. Monitor Placa** — CPU, RAM y temperatura en tiempo real (status en header)

**2. Monitor Red** — Download/Upload en vivo, speedtest Ookla, lista de IPs (status en header)

**3. Monitor USB** — Dispositivos conectados, expulsión segura

**4. Monitor Disco** — Espacio, temperatura NVMe, velocidad I/O (status en header)

**5. Monitor Procesos** — Top 20 procesos, búsqueda, matar procesos

**6. Monitor Servicios** — Start/Stop/Restart systemd, ver logs

**7. Histórico Datos** — 8 gráficas CPU/RAM/Temp/Red/Disco/PWM en 24h, 7d, 30d, exportar CSV

**8. Control Ventiladores** — Modo Auto/Manual/Silent/Normal/Performance, curvas PWM

**9. Lanzadores** — Scripts personalizados con terminal en vivo

**10. Actualizaciones** — Estado de paquetes, instalar con terminal integrada

**11. Homebridge** — Control de enchufes e interruptores HomeKit, toggle táctil por dispositivo

**12. Cambiar Tema** — 15 temas (Cyberpunk, Matrix, Dracula, Nord...)

**13. Reiniciar** — Reinicia el dashboard aplicando cambios de código

**14. Salir** — Salir de la app o apagar el sistema

> **Todas las ventanas** incluyen header unificado con título, status en tiempo real y botón ✕ táctil (52×42px) optimizado para pantalla DSI.

---

## 🔧 Configuración Básica

### Ajustar posición en pantalla DSI (`config/settings.py`):
```python
DSI_X = 0     # Posición horizontal
DSI_Y = 0     # Posición vertical
```

### Añadir scripts en Lanzadores:
```python
LAUNCHERS = [
    {"label": "Mi Script", "script": str(SCRIPTS_DIR / "mi_script.sh")},
]
```

---

## 🏠 Configurar Homebridge

Crea el archivo `.env` en la raíz del proyecto (cópialo desde `.env.example`):

```env
HOMEBRIDGE_HOST=192.168.1.X    # IP de la Pi con Homebridge
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña
```

> **Importante**: Activa el **Insecure Mode** en Homebridge (`homebridge-config-ui-x → Configuración → Homebridge`). Sin él, la API no permite acceder a los accesorios.

El panel Homebridge del dashboard muestra los accesorios en grid de 2 columnas. Cada botón muestra el nombre del dispositivo, un indicador ● de color (on/off) y permite hacer toggle con un toque. Si un dispositivo tiene `StatusFault=1` aparece ⚠ en rojo.

---

## 📋 Ver Logs del Sistema

```bash
# En tiempo real
tail -f data/logs/dashboard.log

# Solo errores
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
| Homebridge no conecta | Revisar `.env` y activar Insecure Mode en Homebridge |
| Badge hb_offline siempre rojo | Comprobar conectividad entre Pis y `HOMEBRIDGE_HOST` |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 🆕 Novedades v2.8

✅ **Integración Homebridge** — Ventana de control de accesorios HomeKit (enchufes e interruptores)  
✅ **HomebridgeMonitor** — Sondeo ligero en background cada 30s, JWT con renovación automática  
✅ **3 badges Homebridge** — offline 🔴, enchufes encendidos 🟠, dispositivos con fallo 🔴  
✅ **Toggle táctil** — Activa/desactiva cada dispositivo directamente desde la pantalla DSI  
✅ **Configuración `.env`** — Credenciales separadas del código fuente  

---

## 📚 Más Información

**[README.md](README.md)** — Documentación completa  
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — Instalación detallada  
**[INDEX.md](INDEX.md)** — Índice de toda la documentación

---

**Dashboard v2.8** 🚀🏠✨
