# 🚀 Inicio Rápido - Dashboard v3.1

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

## 🎯 Menú Principal (15 botones)

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
│  Homebridge     │  Visor de Logs   │
├─────────────────┼──────────────────┤
│  Cambiar Tema   │  Reiniciar       │
├─────────────────┼──────────────────┤
│  Salir          │                  │
└─────────────────┴──────────────────┘
```

---

## 🖥️ Las 15 Ventanas

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

**11. Homebridge** — Control de **5 tipos de dispositivos HomeKit**: switches/enchufes, luces con brillo, termostatos, sensores temperatura/humedad, persianas

**12. Visor de Logs** — Filtros por nivel, módulo, texto e intervalo de tiempo; exportación a `data/exports/logs/`

**13. Cambiar Tema** — 15 temas (Cyberpunk, Matrix, Dracula, Nord...)

**14. Reiniciar** — Reinicia el dashboard aplicando cambios de código

**15. Salir** — Salir de la app o apagar el sistema

> **Todas las ventanas** incluyen header unificado con título, status en tiempo real y botón ✕ táctil (52×42px) optimizado para pantalla DSI.

> **Exports organizados** en `data/exports/{csv,logs,screenshots}` — carpetas creadas automáticamente, máx. 10 archivos por tipo.

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

La ventana Homebridge muestra los accesorios en grid de 2 columnas con tarjetas adaptativas según el tipo:

- **Switch / Enchufe / Luz básica**: CTkSwitch táctil (90×46px)
- **Luz regulable**: switch ON/OFF con control de brillo
- **Termostato**: temperatura actual + botones +/− 0.5°C para temperatura objetivo
- **Sensor**: temperatura y/o humedad en modo solo lectura
- **Persiana / Estor**: posición actual (%) con barra visual

Si un dispositivo tiene `StatusFault=1` aparece ⚠ FALLO en rojo y el switch queda bloqueado.

---

## 📲 Configurar Alertas Telegram

Añade al mismo archivo `.env`:

```env
TELEGRAM_TOKEN=123456789:ABCdefGHI...   # Token del bot (@BotFather)
TELEGRAM_CHAT_ID=987654321              # ID del chat o canal destino
```

Las alertas se envían cuando temperatura, CPU, RAM o disco superan los umbrales durante 60 segundos sostenidos (anti-spam). También avisa si hay servicios en estado FAILED.

> Si no configuras estas variables, el dashboard funciona igual — las alertas simplemente no se envían.

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
| Servicios tardan en aparecer | Normal — ServiceMonitor sondea systemctl cada 10s al arrancar |
| No puedo escribir en los entries | Asegúrate de usar v3.0+ — el bug de `grab_set` está corregido |
| Alertas Telegram no llegan | Verificar `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` en `.env` |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 🆕 Novedades v3.1

✅ **Alertas Telegram** — `AlertService` con anti-spam (edge-trigger + sustain 60s), monitoriza temp/CPU/RAM/disco y servicios  
✅ **Homebridge extendido** — 5 tipos de dispositivo: switch, luz regulable, termostato, sensor, persiana  
✅ **UI diálogo salir** — radiobuttons táctiles 30×30px, botones ajustados, layout corregido  

### v3.0 (referencia)
✅ **Visor de Logs** — Filtros por nivel, módulo, texto e intervalo; exportación incluida  
✅ **Exports organizados** — `data/exports/{csv,logs,screenshots}` creadas automáticamente  
✅ **Limpieza al exportar** — CleanupService actúa también al guardar, no solo cada 24h  
✅ **Fix entries** — Eliminado `grab_set()` en FanControl que bloqueaba el teclado  

### v2.9 (referencia)
✅ **Switches táctiles Homebridge** — CTkSwitch de 90×46px, optimizado para el dedo en DSI  
✅ **Sin bloqueos en UI** — SystemMonitor y ServiceMonitor con caché en background thread  
✅ **ServiceMonitor optimizado** — is-enabled en llamada batch, sondeo cada 10s  
✅ **Logging completo** — Todos los servicios registran inicio y parada  

---

## 📚 Más Información

**[README.md](README.md)** — Documentación completa  
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — Instalación detallada  
**[INDEX.md](INDEX.md)** — Índice de toda la documentación

---

**Dashboard v3.1** 🚀🏠📲✨
