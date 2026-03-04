# 🌐 Compatibilidad Multiplataforma - Resumen

## 🎯 ¿En qué sistemas funciona?

### ✅ Funciona al 100% (TODO)
- **Raspberry Pi OS** (Raspbian)
- **Kali Linux** (en Raspberry Pi)

### ✅ Funciona al ~85% (sin ventiladores ni WiFi GPIO)
- **Ubuntu** (20.04, 22.04, 23.04+)
- **Debian** (11, 12+)
- **Linux Mint**
- **Fedora, CentOS, RHEL**
- **Arch Linux, Manjaro**

---

## 📊 Tabla de Compatibilidad

| Componente | Raspberry Pi | Otros Linux | Notas |
|------------|--------------|-------------|-------|
| **Interfaz gráfica** | ✅ | ✅ | 100% compatible |
| **Monitor sistema** | ✅ | ✅ | CPU, RAM, Temp, Disco |
| **Monitor red** | ✅ | ✅ | Download, Upload, Speedtest |
| **Monitor USB** | ✅ | ✅ | Con dependencias |
| **Monitor SSH** | ✅ | ✅ | Requiere `who` y `last` |
| **Lanzadores** | ✅ | ✅ | Scripts bash |
| **Temas** | ✅ | ✅ | 15 temas |
| **Editor Config** | ✅ | ✅ | Edita local_settings.py |
| **Monitor WiFi** | ✅ | ⚠️ | Requiere interfaz wlan + `wireless-tools` |
| **Control ventiladores** | ✅ | ❌ | Solo con GPIO |

---

## 🔧 Dependencias por Sistema

### Ubuntu/Debian/Raspberry Pi:
```bash
sudo apt-get install lm-sensors usbutils udisks2 wireless-tools
pip3 install --break-system-packages customtkinter psutil
```

### Fedora/RHEL:
```bash
sudo dnf install lm-sensors usbutils udisks2 wireless-tools
pip3 install customtkinter psutil
```

### Arch Linux:
```bash
sudo pacman -S lm-sensors usbutils udisks2 wireless_tools
pip3 install customtkinter psutil
```

---

## ⚠️ Limitaciones

### Control de Ventiladores
El control de ventiladores PWM **SOLO funciona en Raspberry Pi** porque requiere:
- GPIO pins
- Hardware específico
- Librería de control GPIO

**En otros sistemas Linux:** El botón de ventiladores no funcionará, pero el resto del dashboard (85%) funciona perfectamente.

### Monitor WiFi
Requiere una interfaz inalámbrica activa (`wlan0` u otra) y el paquete `wireless-tools` instalado (`iwconfig`).
En sistemas sin interfaz WiFi (servidor con solo ethernet), el Monitor WiFi no mostrará datos.

---

## 💡 Uso Recomendado

- **Raspberry Pi:** Usa TODO al 100%, incluyendo WiFi y ventiladores
- **Ubuntu/Debian Desktop:** Monitor de sistema completo (sin ventiladores; WiFi si tienes wlan)
- **Servidores:** Requiere X11 para la interfaz gráfica; Monitor SSH funciona perfectamente
- **Kali Linux (RPi):** Funciona al 100% igual que Raspbian

---

## 🚀 Verificación Rápida

```bash
# Verificar Python
python3 --version  # Debe ser 3.8+

# Verificar temperatura
sensors  # o vcgencmd measure_temp

# Verificar USB
lsusb
lsblk

# Verificar WiFi (si aplica)
iwconfig

# Verificar sesiones SSH
who
last -n 5
```

---

**Conclusión:** El dashboard funciona en cualquier Linux con interfaz gráfica. El control de ventiladores es específico de Raspberry Pi con GPIO. El Monitor WiFi requiere interfaz inalámbrica. El Monitor SSH funciona en cualquier sistema Linux.
