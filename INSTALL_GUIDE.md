# 🔧 Guía de Instalación Completa

Guía detallada para instalar el Dashboard en cualquier sistema Linux.

---

## 🎯 Sistemas Soportados

### ✅ **Soporte Completo (100%)**
- Raspberry Pi OS (Bullseye, Bookworm)
- Kali Linux (en Raspberry Pi)

### ✅ **Soporte Parcial (~85%)**
- Ubuntu (20.04, 22.04, 23.04+, 24.04)
- Debian (11, 12+)
- Linux Mint
- Fedora / CentOS / RHEL
- Arch Linux / Manjaro

**Nota**: En sistemas no-Raspberry Pi, el control de ventiladores PWM y el Monitor WiFi pueden no funcionar. Todo lo demás funciona perfectamente.

---

## ⚡ Método 1: Instalación Automática (Recomendado)

### **Script de Instalación**

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard

# 2. Dar permisos y ejecutar
chmod +x install_system.sh
sudo ./install_system.sh

# 3. Ejecutar
python3 main.py
```

**El script instalará automáticamente:**
- ✅ Dependencias del sistema (python3-pip, python3-tk, lm-sensors, wireless-tools)
- ✅ Dependencias Python (customtkinter, psutil, Pillow)
- ✅ CLI oficial de Ookla para speedtest
- ✅ Configurará sensores

---

## 🛠️ Método 2: Instalación Manual con Entorno Virtual

### **Paso 1: Instalar Dependencias del Sistema**

```bash
# Actualizar repositorios
sudo apt update

# Instalar herramientas básicas
sudo apt install -y python3 python3-pip python3-venv python3-tk git

# Instalar lm-sensors para temperatura
sudo apt install -y lm-sensors

# Instalar wireless-tools para Monitor WiFi
sudo apt install -y wireless-tools

# Instalar CLI oficial de Ookla para speedtest
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest

# Detectar sensores (primera vez)
sudo sensors-detect --auto
```

### **Paso 2: Clonar Repositorio**

```bash
cd ~
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
```

### **Paso 3: Crear Entorno Virtual**

```bash
# Crear venv
python3 -m venv venv

# Activar venv
source venv/bin/activate

# Tu prompt debería cambiar a: (venv) user@host:~$
```

### **Paso 4: Instalar Dependencias Python**

```bash
# Dentro del venv
pip install --upgrade pip
pip install -r requirements.txt
```

### **Paso 5: Ejecutar**

```bash
# Asegurarte que el venv está activo
source venv/bin/activate

# Ejecutar
python3 main.py
```

### **Paso 6: Crear Launcher (Opcional)**

```bash
chmod +x create_desktop_launcher.sh
./create_desktop_launcher.sh
```

---

## 🚀 Método 3: Instalación Sin Entorno Virtual

**⚠️ Advertencia**: En Ubuntu 23.04+ y Debian 12+ necesitarás usar `--break-system-packages` o el script automático.

### **Opción A: Usar Script Automático** ⭐

```bash
cd system-dashboard
sudo ./install_system.sh
```

### **Opción B: Manual**

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install -y python3 python3-pip python3-tk lm-sensors wireless-tools

# Instalar CLI oficial de Ookla para speedtest
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest

# Instalar dependencias Python (método según tu sistema)
```

#### **En sistemas antiguos (Ubuntu 22.04, Debian 11):**
```bash
pip install -r requirements.txt
```

#### **En sistemas modernos (Ubuntu 23.04+, Debian 12+):**
```bash
pip install -r requirements.txt --break-system-packages
```

### **Ejecutar**

```bash
python3 main.py
```

---

## 🐛 Solución de Problemas

### **Error: externally-managed-environment**

**Síntoma:**
```
error: externally-managed-environment
```

**Causa**: Sistema moderno (Ubuntu 23.04+, Debian 12+) que protege paquetes del sistema.

**Soluciones:**

1. **Opción 1: Usar venv** (Recomendado)
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Opción 2: Usar --break-system-packages**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```

---

### **Error: ModuleNotFoundError: No module named 'customtkinter'**

**Causa**: Dependencias no instaladas.

**Solución:**
```bash
# Si usas venv
source venv/bin/activate
pip install customtkinter

# Si no usas venv
pip install customtkinter --break-system-packages
```

---

### **Error: No se detecta temperatura**

**Síntoma:**
```
Temp: N/A
```

**Solución:**
```bash
sudo sensors-detect --auto
sudo systemctl restart lm-sensors
sensors
```

**Si aún no funciona:**
```bash
sudo modprobe coretemp
```

---

### **Error: Ventiladores no responden**

**Causa**: Pin GPIO incorrecto o sin permisos.

**Solución:**

1. **Probar con sudo** (temporal):
   ```bash
   sudo python3 main.py
   ```

2. **Añadir usuario a grupo gpio** (permanente):
   ```bash
   sudo usermod -a -G gpio $USER
   # Cerrar sesión y volver a entrar
   ```

---

### **Error: ImportError: libGL.so.1**

**Causa**: Falta librería OpenGL.

**Solución:**
```bash
sudo apt install -y libgl1-mesa-glx
```

---

### **Speedtest no funciona**

**Causa**: CLI oficial de Ookla no instalada, o instalado el paquete antiguo `speedtest-cli` de Python (incompatible).

**Solución:**
```bash
# Desinstalar el paquete antiguo si estuviera instalado
sudo apt remove speedtest-cli

# Instalar la CLI oficial de Ookla
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest

# Verificar
speedtest --version
```

> ⚠️ El paquete `speedtest-cli` de apt/pip es incompatible. El proyecto usa exclusivamente la CLI oficial de Ookla (comando `speedtest`).

---

### **Monitor WiFi no muestra datos**

**Causa**: `iwconfig` no está instalado o la interfaz no es inalámbrica.

**Solución:**
```bash
sudo apt install wireless-tools

# Verificar interfaz WiFi disponible
iwconfig
```

---

### **Monitor SSH aparece vacío**

**Causa**: `who` o `last` no están disponibles o no hay sesiones activas.

**Solución:**
```bash
# Verificar que funcionan
who
last -n 10
```

---

### **Error: No se ve la ventana**

**Causa**: Posición incorrecta.

**Solución**: Crear `config/local_settings.py` o usar el **Editor de Configuración** *(v3.8)*:
```python
DSI_X = 0
DSI_Y = 0
DSI_WIDTH = 800
DSI_HEIGHT = 480
```

---

## 📦 Dependencias Completas

### **Dependencias del Sistema:**
```bash
python3          # >= 3.8
python3-pip      # Gestor de paquetes
python3-venv     # Entornos virtuales (opcional)
python3-tk       # Tkinter
lm-sensors       # Lectura de sensores
wireless-tools   # Monitor WiFi (iwconfig)
speedtest        # CLI oficial de Ookla (NO speedtest-cli)
git              # Control de versiones
```

### **Dependencias Python:**
```
customtkinter    # UI moderna
psutil           # Info del sistema
Pillow           # Procesamiento de imágenes
matplotlib       # Gráficas históricas
python-dotenv    # Variables de entorno (.env)
```

### **Dependencias opcionales por función:**

| Paquete sistema | Función | Obligatorio |
|----------------|---------|-------------|
| `lm-sensors` | Temperatura CPU | ✅ Sí |
| `usbutils` | Listar dispositivos USB | ✅ Sí |
| `udisks2` | Expulsión segura USB | ✅ Sí |
| `smartmontools` | Temperatura NVMe + SMART | ✅ Sí |
| `arp-scan` | Escáner de red local | ✅ Sí |
| `wireless-tools` | Monitor WiFi (iwconfig) | ⚙️ Solo si usas WiFi |
| `speedtest` (Ookla CLI) | Speedtest integrado | ⚙️ Opcional |
| `rpicam-apps` | Cámara OV5647 | ⚙️ Opcional |
| `tesseract-ocr` | OCR en cámara | ⚙️ Opcional |
| `espeak-ng` | Alertas audio TTS | ⚙️ Opcional |

### **Sudoers necesarios:**

```bash
# arp-scan (Red Local)
echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan" | sudo tee /etc/sudoers.d/arp-scan

# smartctl (SMART NVMe)
echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/bin/smartctl" | sudo tee /etc/sudoers.d/smartctl
```

---

## 🔐 Permisos

### **GPIO (para ventiladores):**

```bash
sudo usermod -a -G gpio,i2c,spi $USER
# Cerrar sesión y volver a entrar
```

### **Cámara:**

```bash
sudo usermod -aG video $(whoami)
# Cerrar sesión y volver a entrar
```

---

## 🚀 Autoarranque (Opcional)

### **Método 1: systemd**

```bash
sudo nano /etc/systemd/system/dashboard.service
```

Contenido:
```ini
[Unit]
Description=System Dashboard
After=graphical.target

[Service]
Type=simple
User=tu-usuario
WorkingDirectory=/home/tu-usuario/system-dashboard
ExecStart=/home/tu-usuario/system-dashboard/venv/bin/python3 main.py
Restart=on-failure

[Install]
WantedBy=graphical.target
```

Activar:
```bash
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
```

---

### **Método 2: autostart**

```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/dashboard.desktop
```

Contenido:
```ini
[Desktop Entry]
Type=Application
Name=System Dashboard
Exec=/home/tu-usuario/system-dashboard/venv/bin/python3 /home/tu-usuario/system-dashboard/main.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

---

## 🧪 Verificación de Instalación

```bash
# 1. Verificar Python
python3 --version  # Debe ser >= 3.8

# 2. Verificar módulos
python3 -c "import customtkinter; print('CustomTkinter OK')"
python3 -c "import psutil; print('psutil OK')"
python3 -c "import PIL; print('Pillow OK')"

# 3. Verificar sensores
sensors

# 4. Verificar speedtest (CLI oficial Ookla)
speedtest --version

# 5. Verificar WiFi (si aplica)
iwconfig

# 6. Ejecutar dashboard
python3 main.py
```

---

## 💡 Tips de Instalación

1. **Usa el script automático** si es tu primera vez
2. **Usa venv** si quieres mantener el sistema limpio
3. **No instales `speedtest-cli`** — usa siempre la CLI oficial de Ookla (`speedtest`)
4. **Detecta sensores** la primera vez con `sudo sensors-detect`
5. **Instala `wireless-tools`** si vas a usar el Monitor WiFi
6. **Revisa los logs** si algo falla: `grep ERROR data/logs/dashboard.log`

---

## 📊 Tiempos de Instalación

| Método | Tiempo | Dificultad |
|--------|--------|------------|
| Script automático | ~5 min | ⭐ Fácil |
| Manual con venv | ~10 min | ⭐⭐ Media |
| Manual sin venv | ~8 min | ⭐⭐ Media |

---

## 🆘 Ayuda Adicional

1. Revisa esta guía completa
2. Verifica [QUICKSTART.md](QUICKSTART.md) para problemas comunes
3. Revisa [README.md](README.md) sección Troubleshooting
4. Abre un Issue en GitHub con el SO, versión de Python y mensaje de error completo

---

**¡Instalación completa!** 🎉
