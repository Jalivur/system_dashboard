This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

<file_summary>
This section contains a summary of this file.

<purpose>
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.
</purpose>

<file_format>
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  - File path as an attribute
  - Full contents of the file
</file_format>

<usage_guidelines>
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.
</usage_guidelines>

<notes>
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: **.md
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)
</notes>

</file_summary>

<directory_structure>
COMPATIBILIDAD.md
IDEAS_EXPANSION.md
INDEX.md
INSTALL_GUIDE.md
INTEGRATION_GUIDE.md
QUICKSTART.md
README.md
REQUIREMENTS.md
THEMES_GUIDE.md
</directory_structure>

<files>
This section contains the contents of the repository's files.

<file path="COMPATIBILIDAD.md">
# 🌐 Compatibilidad Multiplataforma - Resumen

## 🎯 ¿En qué sistemas funciona?

### ✅ Funciona al 100% (TODO)
- **Raspberry Pi OS** (Raspbian)
- **Kali Linux** (en Raspberry Pi)

### ✅ Funciona al ~85% (sin control de ventiladores)
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
| **Lanzadores** | ✅ | ✅ | Scripts bash |
| **Temas** | ✅ | ✅ | 15 temas |
| **Control ventiladores** | ✅ | ❌ | Solo con GPIO |

---

## 🔧 Dependencias por Sistema

### Ubuntu/Debian/Raspberry Pi:
```bash
sudo apt-get install lm-sensors usbutils udisks2
pip3 install --break-system-packages customtkinter psutil
```

### Fedora/RHEL:
```bash
sudo dnf install lm-sensors usbutils udisks2
pip3 install customtkinter psutil
```

### Arch Linux:
```bash
sudo pacman -S lm-sensors usbutils udisks2
pip3 install customtkinter psutil
```

---

## ⚠️ Limitación: Control de Ventiladores

El control de ventiladores PWM **SOLO funciona en Raspberry Pi** porque requiere:
- GPIO pins
- Hardware específico
- Librería de control GPIO

**En otros sistemas Linux:** El botón de ventiladores no funcionará, pero el resto del dashboard (85%) funciona perfectamente.

---

## 💡 Uso Recomendado

- **Raspberry Pi:** Usa TODO al 100%
- **Ubuntu/Debian Desktop:** Monitor de sistema completo (sin ventiladores)
- **Servidores:** Requiere X11 para la interfaz gráfica
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
```

---

**Conclusión:** El dashboard funciona en cualquier Linux con interfaz gráfica. Solo el control de ventiladores es específico de Raspberry Pi con GPIO.
</file>

<file path="INTEGRATION_GUIDE.md">
# 🔗 Guía de Integración con fase1.py

Esta guía explica cómo integrar tu aplicación OLED (`fase1.py`) con el Dashboard para que ambos funcionen juntos.

---

## 🎯 ¿Cómo Funciona la Integración?

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  DASHBOARD (system_dashboard)                          │
│  - Interfaz gráfica                                    │
│  - Control de ventiladores                             │
│  - Guarda estado en: data/fan_state.json              │
│                                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Escribe fan_state.json
                   │ {"mode": "auto", "target_pwm": 128}
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  ARCHIVO COMPARTIDO                                     │
│  📄 data/fan_state.json                                │
│  {"mode": "auto", "target_pwm": 128}                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Lee fan_state.json
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  OLED MONITOR (fase1.py / integration_fase1.py)       │
│  - Muestra CPU, RAM, Temp en OLED                     │
│  - Controla LEDs RGB                                   │
│  - Aplica PWM de ventiladores                         │
│  - Lee estado desde: data/fan_state.json              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Pasos de Integración

### 1️⃣ Instalar el Dashboard

```bash
# Descargar y extraer system_dashboard
cd ~
unzip system_dashboard_WITH_THEMES.zip
cd system_dashboard

# Instalar dependencias
sudo ./install_system.sh
```

### 2️⃣ Configurar Ruta en fase1.py

Edita tu `fase1.py` (o usa el nuevo `integration_fase1.py`):

```python
# En la línea ~13, cambia:
STATE_FILE = "/home/jalivur/system_dashboard/data/fan_state.json"

# Ajusta la ruta donde hayas puesto el proyecto
```

### 3️⃣ Ejecutar Ambos Programas

**Terminal 1** - Dashboard:
```bash
cd ~/system_dashboard
python3 main.py
```

**Terminal 2** - OLED Monitor:
```bash
cd /ruta/a/tu/fase1
python3 integration_fase1.py
# O tu fase1.py modificado
```

---

## 🔄 Flujo de Datos

### Cuando Cambias el Modo en el Dashboard:

1. **Usuario** hace clic en "Control Ventiladores"
2. **Dashboard** cambia el modo a "Manual" y PWM a 200
3. **Dashboard** guarda en `data/fan_state.json`:
   ```json
   {
     "mode": "manual",
     "target_pwm": 200
   }
   ```
4. **fase1.py** lee el archivo cada 1 segundo
5. **fase1.py** aplica PWM=200 a los ventiladores
6. **OLED** muestra "Fan1:78% Fan2:78%" (200/255 = 78%)

### Sincronización:

- ✅ Dashboard escribe cada vez que cambias algo
- ✅ fase1 lee cada 1 segundo
- ✅ PWM se aplica inmediatamente si cambia
- ✅ Sin conflictos (escritura atómica con .tmp)

---

## ⚙️ Modos Disponibles

El Dashboard soporta 5 modos:

| Modo | PWM | Descripción |
|------|-----|-------------|
| **Auto** | Dinámico | Basado en curva temperatura-PWM |
| **Manual** | Usuario | Tú eliges el valor (0-255) |
| **Silent** | 77 | Silencioso (30%) |
| **Normal** | 128 | Normal (50%) |
| **Performance** | 255 | Máximo (100%) |

El archivo `fan_state.json` siempre tiene `target_pwm` calculado, independientemente del modo.

---

## 🛠️ Configuración Avanzada

### Opción 1: Usar Rutas Relativas (Recomendado)

Modifica `integration_fase1.py`:

```python
import os
from pathlib import Path

# Ruta relativa al home del usuario
HOME = Path.home()
STATE_FILE = HOME / "system_dashboard" / "data" / "fan_state.json"
```

### Opción 2: Variable de Entorno

```bash
# En ~/.bashrc o ~/.profile
export DASHBOARD_DATA="/home/jalivur/system_dashboard/data"

# En fase1.py
STATE_FILE = os.environ.get("DASHBOARD_DATA", "/home/jalivur/system_dashboard/data") + "/fan_state.json"
```

### Opción 3: Enlace Simbólico

```bash
# Crear enlace en ubicación fija
ln -s ~/system_dashboard/data/fan_state.json /tmp/fan_state.json

# En fase1.py
STATE_FILE = "/tmp/fan_state.json"
```

---

## 🚀 Autostart de Ambos Programas

### Método 1: systemd (Recomendado)

**Dashboard:**
```bash
# Crear servicio
sudo nano /etc/systemd/system/dashboard.service
```

```ini
[Unit]
Description=System Dashboard
After=graphical.target

[Service]
Type=simple
User=jalivur
WorkingDirectory=/home/jalivur/system_dashboard
Environment="DISPLAY=:0"
ExecStart=/usr/bin/python3 /home/jalivur/system_dashboard/main.py
Restart=always

[Install]
WantedBy=graphical.target
```

**OLED Monitor:**
```bash
sudo nano /etc/systemd/system/oled-monitor.service
```

```ini
[Unit]
Description=OLED Monitor
After=network.target

[Service]
Type=simple
User=jalivur
WorkingDirectory=/home/jalivur/proyectopantallas
ExecStart=/usr/bin/python3 /home/jalivur/proyectopantallas/integration_fase1.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Activar:**
```bash
sudo systemctl enable dashboard.service
sudo systemctl enable oled-monitor.service

sudo systemctl start dashboard.service
sudo systemctl start oled-monitor.service

# Ver logs
sudo journalctl -u dashboard.service -f
sudo journalctl -u oled-monitor.service -f
```

### Método 2: Crontab @reboot

```bash
crontab -e
```

Añadir:
```cron
@reboot sleep 30 && DISPLAY=:0 /usr/bin/python3 /home/jalivur/system_dashboard/main.py &
@reboot sleep 10 && /usr/bin/python3 /home/jalivur/proyectopantallas/integration_fase1.py &
```

---

## 🐛 Solución de Problemas

### El OLED no muestra cambios de ventilador

**Verificar que el archivo existe:**
```bash
ls -la ~/system_dashboard/data/fan_state.json
```

**Ver contenido:**
```bash
cat ~/system_dashboard/data/fan_state.json
# Debe mostrar: {"mode": "...", "target_pwm": ...}
```

**Ver logs de fase1:**
```bash
# Añadir debug al inicio
python3 integration_fase1.py
# Verás: "Estado leído: modo=auto, PWM=128"
```

### El PWM no cambia

**Verificar permisos:**
```bash
chmod 644 ~/system_dashboard/data/fan_state.json
```

**Verificar que fase1 lee el archivo:**
```python
# Añadir en el código de fase1:
if state:
    print(f"DEBUG: Estado leído = {state}")
```

### Los dos programas pelean por los ventiladores

**Esto NO debería pasar** porque:
- Dashboard solo ESCRIBE el estado
- fase1 solo LEE el estado
- fase1 es quien aplica el PWM físicamente

Si pasa:
1. Cierra el Dashboard
2. Solo ejecuta fase1
3. Verifica que funciona
4. Vuelve a abrir Dashboard

---

## 💡 Tips y Trucos

### Ver Estado en Tiempo Real

```bash
# Terminal dedicado
watch -n 1 cat ~/system_dashboard/data/fan_state.json
```

### Script de Debug

```bash
#!/bin/bash
# debug_integration.sh

echo "=== Estado del Dashboard ==="
cat ~/system_dashboard/data/fan_state.json | python3 -m json.tool

echo ""
echo "=== Procesos corriendo ==="
ps aux | grep -E "main.py|fase1.py|integration_fase1.py"

echo ""
echo "=== Temperatura actual ==="
vcgencmd measure_temp
```

### Notificaciones de Cambio

Añade a `integration_fase1.py`:

```python
last_mode = None

# En el bucle:
if state and state.get("mode") != last_mode:
    new_mode = state.get("mode")
    print(f"🔔 Modo cambiado: {last_mode} → {new_mode}")
    # Opcionalmente, mostrar en OLED temporalmente
    last_mode = new_mode
```

---

## 📊 Monitoreo

### Ver Logs en Tiempo Real

```bash
# Dashboard
tail -f ~/system_dashboard/dashboard.log

# OLED Monitor
tail -f ~/proyectopantallas/oled_monitor.log
```

### Crear Logs

Añade al inicio de `integration_fase1.py`:

```python
import logging

logging.basicConfig(
    filename='/home/jalivur/proyectopantallas/oled_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# En el bucle:
if state:
    logging.info(f"PWM aplicado: {fan_pwm}, Modo: {state.get('mode')}")
```

---

## ✅ Checklist de Integración

- [ ] Dashboard instalado y funcionando
- [ ] Archivo `fan_state.json` se crea al cambiar modo
- [ ] Ruta correcta configurada en fase1.py
- [ ] fase1.py lee el archivo correctamente
- [ ] PWM se aplica a los ventiladores físicos
- [ ] OLED muestra el porcentaje correcto
- [ ] Ambos programas arrancan al inicio (opcional)
- [ ] Logs configurados (opcional)

---

## 🎯 Resultado Final

Una vez integrado correctamente:

✅ Cambias modo en Dashboard → Ventiladores responden inmediatamente
✅ OLED muestra estado actual de ventiladores
✅ LEDs cambian color según temperatura
✅ Todo funciona sin conflictos
✅ Puedes cerrar Dashboard, fase1 sigue funcionando
✅ Puedes cerrar fase1, Dashboard sigue guardando estado

---

## 📞 ¿Problemas?

Si tienes problemas con la integración:

1. Verifica rutas con `ls -la`
2. Verifica contenido con `cat`
3. Añade `print()` para debug
4. Ejecuta manualmente primero (no autostart)
5. Revisa logs de systemd si usas servicios

---

**¡Disfruta de tu sistema integrado!** 🎉
</file>

<file path="THEMES_GUIDE.md">
# 🎨 Guía de Temas - System Dashboard

El dashboard incluye **15 temas profesionales** pre-configurados y la capacidad de crear temas personalizados.

---

## 🌈 Temas Disponibles

### 1. **Cyberpunk** (Original) ⚡
```
Colores: Cyan neón + Verde oscuro
Estilo: Futurista, neón brillante
Ideal para: Look cyberpunk clásico
```
**Paleta:**
- Primary: `#00ffff` (Cyan brillante)
- Secondary: `#14611E` (Verde oscuro)
- Success: `#1ae313` (Verde neón)
- Warning: `#ffaa00` (Naranja)
- Danger: `#ff3333` (Rojo)

---

### 2. **Matrix** 💚
```
Colores: Verde Matrix brillante
Estilo: Película Matrix
Ideal para: Fans de Matrix
```
**Paleta:**
- Primary: `#00ff00` (Verde Matrix)
- Secondary: `#0aff0a` (Verde brillante)
- Success: `#00ff00` (Verde puro)
- Warning: `#ccff00` (Verde-amarillo lima)
- Danger: `#ff0000` (Rojo)

**✨ Colores optimizados** para alto contraste.

---

### 3. **Sunset** 🌅
```
Colores: Naranja cálido + Púrpura
Estilo: Atardecer cálido
Ideal para: Ambiente acogedor
```
**Paleta:**
- Primary: `#ff6b35` (Naranja cálido)
- Secondary: `#f7931e` (Naranja dorado)
- Success: `#ffd23f` (Amarillo dorado)
- Warning: `#ffd23f` (Amarillo)
- Danger: `#d62828` (Rojo oscuro)

---

### 4. **Ocean** 🌊
```
Colores: Azul océano + Aqua
Estilo: Marino refrescante
Ideal para: Look fresco y limpio
```
**Paleta:**
- Primary: `#00d4ff` (Azul cielo)
- Secondary: `#48dbfb` (Azul claro)
- Success: `#1dd1a1` (Verde agua)
- Warning: `#feca57` (Amarillo suave)
- Danger: `#ee5a6f` (Rosa coral)

---

### 5. **Dracula** 🦇
```
Colores: Púrpura + Rosa pastel
Estilo: Elegante oscuro
Ideal para: Desarrolladores
```
**Paleta:**
- Primary: `#bd93f9` (Púrpura pastel)
- Secondary: `#ff79c6` (Rosa)
- Success: `#50fa7b` (Verde pastel)
- Warning: `#f1fa8c` (Amarillo pastel)
- Danger: `#ff5555` (Rojo pastel)

**Popular en editores de código.**

---

### 6. **Nord** ❄️
```
Colores: Azul hielo nórdico
Estilo: Minimalista frío
Ideal para: Estética nórdica
```
**Paleta:**
- Primary: `#88c0d0` (Azul hielo)
- Secondary: `#5e81ac` (Azul oscuro)
- Success: `#a3be8c` (Verde suave)
- Warning: `#ebcb8b` (Amarillo suave)
- Danger: `#bf616a` (Rojo suave)

---

### 7. **Tokyo Night** 🌃
```
Colores: Azul + Púrpura noche
Estilo: Noche de Tokio
Ideal para: Ambiente nocturno
```
**Paleta:**
- Primary: `#7aa2f7` (Azul brillante)
- Secondary: `#bb9af7` (Púrpura)
- Success: `#9ece6a` (Verde)
- Warning: `#e0af68` (Naranja suave)
- Danger: `#f7768e` (Rosa)

---

### 8. **Monokai** 🎨
```
Colores: Cyan + Verde lima
Estilo: IDE clásico
Ideal para: Programadores
```
**Paleta:**
- Primary: `#66d9ef` (Azul claro)
- Secondary: `#fd971f` (Naranja)
- Success: `#a6e22e` (Verde lima)
- Warning: `#e6db74` (Amarillo)
- Danger: `#f92672` (Rosa fucsia)

**Tema icónico de Sublime Text.**

---

### 9. **Gruvbox** 🏜️
```
Colores: Naranja + Beige retro
Estilo: Cálido vintage
Ideal para: Fans del retro
```
**Paleta:**
- Primary: `#fe8019` (Naranja)
- Secondary: `#d65d0e` (Naranja oscuro)
- Success: `#b8bb26` (Verde lima)
- Warning: `#fabd2f` (Amarillo)
- Danger: `#fb4934` (Rojo)

---

### 10. **Solarized Dark** ☀️
```
Colores: Azul + Cyan
Estilo: Elegante científico
Ideal para: Precisión visual
```
**Paleta:**
- Primary: `#268bd2` (Azul)
- Secondary: `#2aa198` (Cyan)
- Success: `#859900` (Verde oliva)
- Warning: `#b58900` (Amarillo oscuro)
- Danger: `#dc322f` (Rojo)

**Diseñado para reducir fatiga visual.**

---

### 11. **One Dark** 🌑
```
Colores: Azul claro + Cyan
Estilo: Moderno equilibrado
Ideal para: Uso prolongado
```
**Paleta:**
- Primary: `#61afef` (Azul claro)
- Secondary: `#56b6c2` (Cyan)
- Success: `#98c379` (Verde)
- Warning: `#e5c07b` (Amarillo)
- Danger: `#e06c75` (Rojo suave)

**Tema de Atom editor.**

---

### 12. **Synthwave 84** 🌆
```
Colores: Rosa + Verde neón
Estilo: Retro 80s
Ideal para: Nostalgia synthwave
```
**Paleta:**
- Primary: `#f92aad` (Rosa neón)
- Secondary: `#fe4450` (Rojo neón)
- Success: `#72f1b8` (Verde neón)
- Warning: `#fede5d` (Amarillo neón)
- Danger: `#fe4450` (Rojo neón)

**Inspirado en los 80s.**

---

### 13. **GitHub Dark** 🐙
```
Colores: Azul GitHub
Estilo: Profesional limpio
Ideal para: Desarrolladores
```
**Paleta:**
- Primary: `#58a6ff` (Azul GitHub)
- Secondary: `#1f6feb` (Azul oscuro)
- Success: `#3fb950` (Verde)
- Warning: `#d29922` (Amarillo)
- Danger: `#f85149` (Rojo)

---

### 14. **Material Dark** 📱
```
Colores: Azul Material Design
Estilo: Google Material
Ideal para: Estética moderna
```
**Paleta:**
- Primary: `#82aaff` (Azul material)
- Secondary: `#c792ea` (Púrpura)
- Success: `#c3e88d` (Verde claro)
- Warning: `#ffcb6b` (Amarillo)
- Danger: `#f07178` (Rojo suave)

---

### 15. **Ayu Dark** 🌙
```
Colores: Azul cielo minimalista
Estilo: Moderno limpio
Ideal para: Simplicidad
```
**Paleta:**
- Primary: `#59c2ff` (Azul cielo)
- Secondary: `#39bae6` (Azul claro)
- Success: `#aad94c` (Verde lima)
- Warning: `#ffb454` (Naranja)
- Danger: `#f07178` (Rosa)

---

## 🔄 Cambiar Tema

### **Desde la Interfaz:**
1. Menú principal → "Cambiar Tema"
2. Selecciona tu tema favorito
3. Clic en "Aplicar y Reiniciar"
4. ✨ Dashboard se reinicia automáticamente

### **Desde Código:**
Editar `data/theme_config.json`:
```json
{
  "selected_theme": "matrix"
}
```

---

## 🎨 Crear Tema Personalizado

### **Paso 1: Editar `config/themes.py`**

```python
THEMES = {
    # ... temas existentes ...
    
    "mi_tema": {
        "name": "Mi Tema Personalizado",
        "colors": {
            "primary": "#ff00ff",      # Color principal
            "secondary": "#00ffff",    # Color secundario
            "success": "#00ff00",      # Verde éxito
            "warning": "#ffff00",      # Amarillo advertencia
            "danger": "#ff0000",       # Rojo peligro
            "bg_dark": "#000000",      # Fondo oscuro
            "bg_medium": "#111111",    # Fondo medio
            "bg_light": "#222222",     # Fondo claro
            "text": "#ffffff",         # Texto
            "text_dim": "#aaaaaa",     # Texto tenue
            "border": "#ff00ff"        # Borde
        }
    }
}
```

### **Paso 2: Usar el Tema**

1. Reinicia el dashboard
2. "Cambiar Tema" → Aparecerá "Mi Tema Personalizado"
3. Selecciónalo y aplica

---

## 🎯 Guía de Colores

### **Colores Obligatorios:**
```python
"primary"    # Botones, sliders, elementos principales
"secondary"  # Títulos, elementos secundarios
"success"    # Indicadores positivos (<30% uso)
"warning"    # Indicadores medios (30-70% uso)
"danger"     # Indicadores altos (>70% uso)
"bg_dark"    # Fondo más oscuro
"bg_medium"  # Fondo medio
"bg_light"   # Fondo más claro
"text"       # Texto principal
"text_dim"   # Texto secundario/tenue
"border"     # Bordes de elementos
```

### **Dónde se Usa Cada Color:**

| Color | Uso |
|-------|-----|
| `primary` | Botones, sliders activos, bordes principales |
| `secondary` | Títulos de sección, hover de sliders/scrollbars |
| `success` | CPU/RAM <30%, mensajes de éxito |
| `warning` | CPU/RAM 30-70%, advertencias |
| `danger` | CPU/RAM >70%, errores, botón "Matar" |
| `bg_dark` | Fondo de cards, filas alternadas |
| `bg_medium` | Fondo principal de ventanas |
| `bg_light` | Fondo de sliders, elementos elevados |
| `text` | Texto principal |
| `text_dim` | Texto secundario (usuarios, paths) |
| `border` | Bordes de botones y elementos |

---

## 💡 Tips para Crear Temas

### **1. Contraste**
Asegura que `text` contraste bien con todos los fondos:
```python
# Bueno
"bg_dark": "#000000"
"text": "#ffffff"

# Malo (poco contraste)
"bg_dark": "#222222"
"text": "#333333"
```

### **2. Secondary Distintivo**
El color `secondary` debe ser diferente de los fondos:
```python
# ❌ Malo - secondary igual a bg_medium
"secondary": "#111111"
"bg_medium": "#111111"

# ✅ Bueno - secondary visible
"secondary": "#00ffff"
"bg_medium": "#111111"
```

### **3. Jerarquía de Fondos**
```python
bg_dark < bg_medium < bg_light
#000000   #111111     #222222
```

### **4. Paleta Armónica**
Usa una herramienta como:
- [Coolors.co](https://coolors.co)
- [Adobe Color](https://color.adobe.com)
- [Paletton](https://paletton.com)

---

## 🔍 Preview de Temas

Todos los temas han sido optimizados para:
- ✅ Alto contraste
- ✅ Legibilidad
- ✅ `secondary` distintivo
- ✅ Colores armónicos

**11 temas fueron corregidos** en v2.0 para tener `secondary` visible.

---

## 📊 Comparación de Temas

| Tema | Estilo | Colores Dominantes | Ideal Para |
|------|--------|-------------------|------------|
| Cyberpunk | Neón | Cyan + Verde | Original |
| Matrix | Película | Verde | Fans Matrix |
| Sunset | Cálido | Naranja + Púrpura | Acogedor |
| Ocean | Fresco | Azul + Aqua | Limpio |
| Dracula | Elegante | Púrpura + Rosa | Devs |
| Nord | Minimalista | Azul hielo | Nórdico |
| Tokyo Night | Nocturno | Azul + Púrpura | Noche |
| Monokai | IDE | Cyan + Verde | Código |
| Gruvbox | Retro | Naranja + Beige | Vintage |
| Solarized | Científico | Azul + Cyan | Precisión |
| One Dark | Moderno | Azul claro | Equilibrado |
| Synthwave | 80s | Rosa + Verde | Nostalgia |
| GitHub | Profesional | Azul GitHub | Devs |
| Material | Google | Azul material | Moderno |
| Ayu | Simple | Azul cielo | Minimalista |

---

## 🔄 Persistencia de Temas

El tema seleccionado se guarda en:
```
data/theme_config.json
```

**Se mantiene entre reinicios** del dashboard.

---

## 🆘 Troubleshooting

### **Tema no se aplica**
**Solución**: Usa "Aplicar y Reiniciar" (reinicia automáticamente)

### **Colores se ven mal**
**Causa**: Tema con contraste bajo  
**Solución**: Prueba otro tema o ajusta `text` y fondos

### **Secondary no se ve**
**Causa**: Color igual a fondo  
**Solución**: Ya corregido en v2.0. Actualiza.

---

**¡Personaliza tu dashboard!** 🎨✨
</file>

<file path="INSTALL_GUIDE.md">
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

**Nota**: En sistemas no-Raspberry Pi, el control de ventiladores PWM puede no funcionar. Todo lo demás funciona perfectamente.

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
- ✅ Dependencias del sistema (python3-pip, python3-tk, lm-sensors)
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
sudo apt install -y python3 python3-pip python3-tk lm-sensors

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

### **Error: No se ve la ventana**

**Causa**: Posición incorrecta.

**Solución**: Editar `config/settings.py` o crear `config/local_settings.py`:
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
speedtest        # CLI oficial de Ookla (NO speedtest-cli)
git              # Control de versiones
```

### **Dependencias Python:**
```
customtkinter    # UI moderna
psutil           # Info del sistema
Pillow           # Procesamiento de imágenes
```

---

## 🔐 Permisos

### **GPIO (para ventiladores):**

```bash
sudo usermod -a -G gpio,i2c,spi $USER
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

# 5. Ejecutar dashboard
python3 main.py
```

---

## 💡 Tips de Instalación

1. **Usa el script automático** si es tu primera vez
2. **Usa venv** si quieres mantener el sistema limpio
3. **No instales `speedtest-cli`** — usa siempre la CLI oficial de Ookla (`speedtest`)
4. **Detecta sensores** la primera vez con `sudo sensors-detect`
5. **Revisa los logs** si algo falla: `grep ERROR data/logs/dashboard.log`

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
</file>

<file path="REQUIREMENTS.md">
# 📦 Guía Rápida: requirements.txt

## 🎯 ¿Qué es?

Un archivo que lista todas las **dependencias Python** de tu proyecto para instalarlas automáticamente.

---

## 📝 Contenido del archivo

```txt
# Dependencias Python
customtkinter>=5.2.0
psutil>=5.9.0
matplotlib>=3.5.0
python-dotenv>=1.0.0
```

**Significado:**
- `customtkinter>=5.2.0` → Interfaz gráfica (versión 5.2.0 o superior)
- `psutil>=5.9.0` → Monitor de sistema (versión 5.9.0 o superior)
- `matplotlib>=3.5.0` → Gráficas históricas (versión 3.5.0 o superior)
- `python-dotenv>=1.0.0` → Variables de entorno desde `.env` (Homebridge, Telegram, Pi-hole)

---

## 🚀 Cómo usar

### Instalar dependencias:

```bash
# En sistemas modernos (Ubuntu 23.04+, Debian 12+)
pip3 install --break-system-packages -r requirements.txt

# En sistemas antiguos
pip3 install -r requirements.txt

# O con sudo (global)
sudo pip3 install -r requirements.txt
```

---

## 🔧 Operadores de versión

| Operador | Significado | Ejemplo |
|----------|-------------|---------|
| `>=` | Versión mínima | `psutil>=5.9.0` |
| `==` | Versión exacta | `psutil==5.9.5` |
| `<=` | Versión máxima | `psutil<=6.0.0` |
| `~=` | Compatible | `psutil~=5.9.0` (5.9.x) |

---

## ✅ Buenas prácticas

### ✅ Hacer:
- Usar versiones mínimas (`>=`) en lugar de exactas
- Comentar dependencias opcionales
- Mantener el archivo actualizado

### ❌ Evitar:
- No especificar versiones (puede romper)
- Versiones exactas innecesarias (muy restrictivo)
- Incluir TODO con `pip freeze` (archivo enorme)

---

## 🧪 Verificar instalación

```bash
# Ver qué tienes instalado
pip3 list

# Ver versión específica
pip3 show customtkinter

# Comprobar problemas
pip3 check
```

---

## 📊 Dependencias del Sistema

**NOTA:** requirements.txt solo lista dependencias **Python**. 

Las dependencias del **sistema** (como `lm-sensors` o `arp-scan`) se instalan con:

```bash
# Ubuntu/Debian/Raspberry Pi
sudo apt-get install lm-sensors usbutils udisks2 smartmontools arp-scan

# Fedora/RHEL
sudo dnf install lm-sensors usbutils udisks2 arp-scan
```

### Dependencias del sistema requeridas en v3.2:

| Paquete | Uso | Obligatorio |
|---------|-----|-------------|
| `lm-sensors` | Temperatura CPU | ✅ Sí |
| `usbutils` | Listar dispositivos USB | ✅ Sí |
| `udisks2` | Expulsión segura USB | ✅ Sí |
| `smartmontools` | Temperatura NVMe | ✅ Sí |
| `arp-scan` | Escáner de red local (v3.2) | ✅ Sí |
| `speedtest` (Ookla CLI) | Speedtest integrado | ⚙️ Opcional |

### Sudoers para arp-scan:

`arp-scan` necesita privilegios de root. Configura sudoers para ejecutarlo sin contraseña:

```bash
echo "usuario ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan" | sudo tee /etc/sudoers.d/arp-scan
```

Sustituye `usuario` por tu usuario del sistema (normalmente `pi` en Raspberry Pi OS).

---

## 🎯 Resumen

**¿Qué es?** → Lista de dependencias Python  
**¿Para qué?** → Instalar todo automáticamente  
**¿Cómo usar?** → `pip3 install --break-system-packages -r requirements.txt`  
**¿Dónde?** → Raíz del proyecto  

---

**Tip:** En sistemas modernos (Ubuntu 23.04+), usa `--break-system-packages` para evitar errores de PEP 668.
</file>

<file path="QUICKSTART.md">
# 🚀 Inicio Rápido - Dashboard v3.7

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

---

## 🎯 Menú Principal (26 botones)

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
│  Reiniciar       │  Salir            │
└──────────────────┴───────────────────┘
```

> Puedes ocultar botones que no uses con el **Gestor de Botones**.

---

## 🖥️ Las 24 Ventanas

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

---

## 🔧 Configuración Básica

### Ajustar posición en pantalla (`config/settings.py`):
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

**Dashboard v3.7** 🚀
</file>

<file path="README.md">
# 🖥️ Sistema de Monitoreo y Control - Dashboard v3.7

Sistema completo de monitoreo y control para Raspberry Pi con interfaz gráfica DSI, control de ventiladores PWM, temas personalizables, histórico de datos, gestión avanzada del sistema, integración con Homebridge, alertas externas por Telegram, escáner de red local, integración Pi-hole, gestor VPN, control de brillo, pantalla de resumen, LEDs RGB inteligentes, alertas de audio con voz TTS, cámara con OCR y SMART extendido de NVMe.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![Version](https://img.shields.io/badge/Version-3.7-orange.svg)]()

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

### 🖧 **Escáner de Red Local**
- **Escaneo con arp-scan**: Detecta todos los dispositivos activos en la red local
- **Información por dispositivo**: IP, MAC y fabricante (OUI lookup)
- **Auto-refresco cada 60s** en background sin bloquear la UI
- **Sudoers preconfigurado**: `usuario ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan`

### 🕳️ **Integración Pi-hole v6**
- **API v6 nativa**: autenticación por sesión (`POST /api/auth` → sid)
- **Estadísticas en tiempo real**: consultas totales, bloqueadas, porcentaje de bloqueo, clientes activos
- **Renovación automática de sesión** y logout limpio al parar
- **Badge en menú**: 🔴 si Pi-hole está offline

### 📲 **Alertas Externas por Telegram**
- **Sin dependencias nuevas**: usa `urllib` de la stdlib de Python
- **Métricas monitorizadas**: temperatura, CPU, RAM, disco y servicios fallidos
- **Anti-spam inteligente**: edge-trigger + sustain de 60s
- **Reseteo automático**: cuando la condición baja del umbral

### 🔔 **Historial de Alertas**
- **Registro persistente**: guarda en `data/alert_history.json` cada alerta enviada a Telegram
- **Máximo 100 entradas** (FIFO)
- **Ventana dedicada**: tarjetas con franja de color lateral (naranja=aviso, rojo=crítico)

### 🏠 **Integración Homebridge Extendida**
- **5 tipos de dispositivo**: switch/enchufe, luz regulable, termostato, sensor temperatura/humedad, persiana/estor
- **CTkSwitch táctil** (90×46px)
- **Tarjetas adaptativas** por tipo de dispositivo
- **Autenticación JWT** con renovación automática en 401
- **3 badges en el menú**: offline (🔴), encendidos (🟠), con fallo (🔴)

### ⚙️ **Monitor de Procesos**
- Lista en tiempo real: Top 20 procesos con CPU/RAM
- Búsqueda inteligente, filtros, terminar procesos con confirmación

### ⚙️ **Monitor de Servicios systemd**
- Gestión completa: Start/Stop/Restart, estado visual, autostart, logs en tiempo real
- Caché en background: sondeo cada 10s, `is-enabled` en llamada batch

### ⚙️ **Servicios Dashboard** *(v3.5/v3.6)*
- **ServiceRegistry**: registro centralizado de todos los servicios del dashboard
- **ServicesManagerWindow**: activar/desactivar servicios background desde la UI
- **Persistencia**: configuración guardada en `data/services.json`

### 🔧 **Gestor de Botones del Menú** *(v3.6.5)*
- **ButtonManagerWindow**: mostrar/ocultar botones del menú principal
- **Persistencia**: configuración guardada en `data/button_config.json`
- Ideal para simplificar el menú en cada máquina según sus capacidades

### 🕐 **Gestor de Crontab** *(v3.7)*
- **Ver, añadir, editar y eliminar** entradas del crontab
- **Selector de usuario**: `usuario` / `root`
- **Accesos rápidos** de programación: @reboot, cada hora, cada día, etc.
- **Preview legible** de la expresión cron

### 📊 **Histórico de Datos**
- Recolección automática cada 5 minutos en background (SQLite)
- 8 gráficas (CPU, RAM, Temperatura, Red, Disco, PWM) en 24h, 7d, 30d
- Estadísticas, detección de anomalías, exportación CSV

### 󱇰 **Monitor USB**
- Detección automática, separación inteligente, expulsión segura

###  **Monitor de Disco**
- Particiones, temperatura NVMe, velocidad I/O
- SMART extendido: horas de uso, ciclos, TB escritos/leídos, % vida útil

### 󱓞 **Lanzadores de Scripts**
- Terminal integrada, layout en grid, confirmación previa

### 󰆧 **Actualizaciones del Sistema**
- Verificación al arranque, caché 12h, terminal integrada

### 󰔎 **15 Temas Personalizables**
- Cambio con un clic, paletas completas, preview en vivo

### 📊 **Resumen del Sistema / Pantalla de Reposo**
- Vista unificada: CPU, RAM, Temperatura, Disco, Red y Servicios
- Fila Pi-hole, refresco cada 2s

### 💡 **Control de Brillo de Pantalla**
- Detección automática del método: `sysfs`, `wlr-randr` (Wayland) o `xrandr` (X11)
- Slider táctil, modo ahorro, encendido/apagado, persistencia

### 🔒 **Gestor de Conexiones VPN**
- Estado en tiempo real, badge en menú, conectar/desconectar con terminal en vivo
- Compatible con WireGuard y OpenVPN

### 💡 **Control LEDs RGB**
- 6 modos: auto, apagado, color fijo, secuencial, respiración, arcoíris
- Sin destellos, sliders RGB, preview en tiempo real

### 🔊 **Alertas de Audio**
- Voz TTS en español con `espeak-ng` + tono sintético por nivel
- 11 archivos .wav, lógica correcta por nivel y métrica

### 📷 **Cámara + Escáner OCR**
- Cámara OV5647 via `rpicam-still`, resoluciones hasta 2592×1944
- OCR con Tesseract local, preprocesado PIL, guarda `.txt` y `.md`

### 🌡️ **Hardware FNK0100K extendido**
- Temperatura del chasis, fan duty real, NVMe SMART extendido
- Arquitectura sin acoplamiento via `hardware_state.json`

---

## 🖥️ Soporte Multi-máquina

El dashboard soporta múltiples Raspberry Pi con configuraciones distintas sin tocar git.

### Config por máquina
`config/settings.py` al final carga opcionalmente:
```python
try:
    from config.local_settings import *
except ImportError:
    pass
```
`config/local_settings.py` está en `.gitignore` — cada máquina tiene el suyo.

### Pi 5 (pantalla DSI física + Wayland)
- Compositor: **labwc** sobre Wayland
- Acceso remoto: **wayvnc** (`wayvnc --output=DSI-2 0.0.0.0 5901`)
- Resolución DSI: 800×480 en posición 1124,1080
- Idle desactivado: `gsettings set org.gnome.desktop.session idle-delay 0`

### Pi 3B+ (sin pantalla física + X11)
- Display virtual `:1` con **Xvfb** (resolución configurable)
- Dashboard corre en `:1`, aislado del escritorio XFCE en `:0`
- Acceso remoto: x11vnc en puerto `5901` sobre `:1`
- XFCE/RealVNC sigue en `:0` puerto `5900` sin cambios
- `local_settings.py`: `DSI_X=0, DSI_Y=0, DSI_WIDTH=1024, DSI_HEIGHT=762`

---

## 📦 Instalación

### Requisitos del Sistema
- **Hardware**: Raspberry Pi 3/4/5
- **OS**: Raspberry Pi OS (Bullseye/Bookworm) o Kali Linux
- **Pantalla**: Touchscreen DSI 4,5" (800×480) o HDMI
- **Python**: 3.8 o superior

### ⚡ Instalación Recomendada

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

### 🛠️ Instalación Manual

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

# 5. Sudoers para arp-scan y smartctl
echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan" | sudo tee /etc/sudoers.d/arp-scan
echo "$(whoami) ALL=(ALL) NOPASSWD: /usr/bin/smartctl"  | sudo tee /etc/sudoers.d/smartctl

# 6. Hardware FNK0100K — cámara y OCR (opcional)
sudo apt install rpicam-apps tesseract-ocr tesseract-ocr-spa espeak-ng
pip install pytesseract --break-system-packages
sudo usermod -aG video $(whoami)

# 7. Generar archivos de audio (opcional)
python3 scripts/generate_sounds.py

# 8. Ejecutar
python3 main.py
```

### Alternativa con Entorno Virtual

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
```

---

## 🏠 Configuración de Homebridge

```env
HOMEBRIDGE_HOST=192.168.1.X
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña
```

> Activa el **Insecure Mode** en Homebridge para que la API permita acceder a los accesorios.

---

## 🕳️ Configuración de Pi-hole

```env
PIHOLE_HOST=192.168.1.X
PIHOLE_PORT=80
PIHOLE_PASSWORD=tu_contraseña
```

> Compatible exclusivamente con **Pi-hole v6**.

---

## 📲 Configuración de Alertas Telegram

```env
TELEGRAM_TOKEN=123456789:ABCdefGHI...
TELEGRAM_CHAT_ID=987654321
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

## 󰍜 Menú Principal (26 botones)

```
┌─────────────────────────────────────┐
│  Control         │  LEDs RGB         │
│  Ventiladores    │                   │
├──────────────────┼───────────────────┤
│  Monitor         │  Monitor          │
│  Placa           │  Red              │
├──────────────────┼───────────────────┤
│  Monitor         │  Monitor          │
│  USB             │  Disco            │
├──────────────────┼───────────────────┤
│  Lanzadores      │  Monitor          │
│                  │  Procesos         │
├──────────────────┼───────────────────┤
│  Monitor         │  Servicios        │
│  Servicios       │  Dashboard        │
├──────────────────┼───────────────────┤
│  Gestor          │  Gestor           │
│  Crontab         │  de Botones       │
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
│  📷 Cámara       │  Cambiar Tema     │
├──────────────────┼───────────────────┤
│  Reiniciar       │  Salir            │
└──────────────────┴───────────────────┘
```

### Las 24 Ventanas

1. **Control Ventiladores** - Configura modos y curvas PWM
2. **LEDs RGB** - Control LEDs RGB GPIO Board con 6 modos *(v3.4)*
3. **Monitor Placa** - CPU, RAM, temperatura + chasis + fan duty *(v3.4)*
4. **Monitor Red** - Tráfico, speedtest Ookla, interfaces e IPs
5. **Monitor USB** - Dispositivos y expulsión segura
6. **Monitor Disco** - Espacio, temperatura NVMe, I/O + SMART *(v3.4)*
7. **Lanzadores** - Scripts con terminal en vivo
8. **Monitor Procesos** - Gestión avanzada de procesos
9. **Monitor Servicios** - Control de servicios systemd
10. **Servicios Dashboard** - Activar/desactivar servicios background *(v3.5/v3.6)*
11. **Gestor Crontab** - Ver/añadir/editar/eliminar entradas cron *(v3.7)*
12. **Gestor de Botones** - Visibilidad de botones del menú *(v3.6.5)*
13. **Histórico Datos** - Visualización de métricas históricas con exportación CSV
14. **Actualizaciones** - Gestión de paquetes del sistema
15. **Homebridge** - Control de 5 tipos de dispositivos HomeKit
16. **Visor de Logs** - Visualización y exportación del log del dashboard
17. **🖧 Red Local** - Escáner arp-scan con IP, MAC y fabricante *(v3.2)*
18. **🕳 Pi-hole** - Estadísticas de bloqueo DNS en tiempo real *(v3.2)*
19. **🔒 Gestor VPN** - Estado en tiempo real + conectar/desconectar *(v3.3)*
20. **🔔 Historial Alertas** - Registro persistente de alertas Telegram *(v3.2)*
21. **💡 Brillo Pantalla** - Control de brillo DSI con modo ahorro *(v3.3)*
22. **📊 Resumen Sistema** - Vista unificada de todas las métricas *(v3.3)*
23. **📷 Cámara / Escáner OCR** - Captura + OCR con Tesseract *(v3.4)*
24. **Cambiar Tema** - Selecciona entre 15 temas

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
│   ├── settings.py                 # Constantes globales
│   ├── themes.py                   # 15 temas pre-configurados
│   └── local_settings.py           # Config por máquina (NO en git)
├── core/
│   ├── fan_controller.py
│   ├── fan_auto_service.py
│   ├── system_monitor.py
│   ├── network_monitor.py
│   ├── network_scanner.py
│   ├── disk_monitor.py
│   ├── process_monitor.py
│   ├── service_monitor.py
│   ├── service_registry.py         # Registro centralizado de servicios (v3.5)
│   ├── update_monitor.py
│   ├── homebridge_monitor.py
│   ├── pihole_monitor.py
│   ├── alert_service.py
│   ├── led_service.py
│   ├── hardware_monitor.py
│   ├── audio_alert_service.py
│   ├── display_service.py
│   ├── vpn_monitor.py
│   ├── data_logger.py
│   ├── data_analyzer.py
│   ├── data_collection_service.py
│   └── cleanup_service.py
├── ui/
│   ├── main_window.py
│   ├── styles.py                   # make_window_header(), make_futuristic_button(),
│   │                               # make_homebridge_switch(), make_entry(), StyleManager
│   ├── window_manager.py           # Gestión de visibilidad de botones
│   ├── widgets/
│   │   ├── graphs.py
│   │   └── dialogs.py              # custom_msgbox, confirm_dialog, terminal_dialog
│   └── windows/
│       ├── monitor.py, network.py, usb.py, disk.py
│       ├── process_window.py, service.py, history.py
│       ├── update.py, fan_control.py
│       ├── launchers.py, theme_selector.py
│       ├── homebridge.py
│       ├── log_viewer.py
│       ├── network_local.py
│       ├── pihole_window.py
│       ├── alert_history.py
│       ├── vpn_window.py
│       ├── display_window.py
│       ├── overview.py
│       ├── led_window.py
│       ├── camera_window.py
│       ├── services_manager_window.py  # Gestión servicios dashboard (v3.6)
│       ├── button_manager_window.py    # Visibilidad botones menú (v3.6.5)
│       ├── crontab_window.py           # Gestor crontab (v3.7)
│       └── __init__.py
├── utils/
│   ├── file_manager.py
│   ├── system_utils.py
│   └── logger.py
├── data/                            # Auto-generado al ejecutar
│   ├── fan_state.json, fan_curve.json, theme_config.json
│   ├── led_state.json
│   ├── hardware_state.json
│   ├── alert_history.json
│   ├── display_state.json
│   ├── services.json               # Config servicios activos/inactivos (v3.5)
│   ├── button_config.json          # Visibilidad botones menú (v3.6.5)
│   ├── history.db
│   ├── logs/dashboard.log
│   ├── photos/
│   ├── scans/
│   └── exports/
│       ├── csv/
│       ├── logs/
│       └── screenshots/
├── scripts/
│   ├── sounds/                     # 11 archivos .wav
│   └── generate_sounds.py
├── .env                             # Credenciales (NO en git)
├── .env.example
├── install_system.sh
├── install.sh
├── main.py
└── requirements.txt
```

---

## 🔧 Configuración

### `config/settings.py`

```python
DSI_WIDTH = 800
DSI_HEIGHT = 480
DSI_X = 0
DSI_Y = 0

LAUNCHERS = [
    {"label": "Montar NAS",   "script": str(SCRIPTS_DIR / "montarnas.sh")},
    {"label": "Conectar VPN", "script": str(SCRIPTS_DIR / "conectar_vpn.sh")},
]
```

### `config/local_settings.py` (por máquina, NO en git)

```python
# Ejemplo Pi 3B+ con Xvfb
DSI_X = 0
DSI_Y = 0
DSI_WIDTH = 1024
DSI_HEIGHT = 762
```

---

## 📋 Sistema de Logging

```bash
tail -f data/logs/dashboard.log
grep ERROR data/logs/dashboard.log
grep "$(date +%Y-%m-%d)" data/logs/dashboard.log
```

---

## 📈 Rendimiento

- **Uso CPU**: ~5-10% en idle
- **Uso RAM**: ~100-150 MB
- **Actualización UI**: 2 segundos — solo lectura de caché
- **Threads background**: 14
- **Log**: máx. 2MB con rotación automática

---

## 🔧 Troubleshooting

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto && sudo systemctl restart lm-sensors` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Ventiladores no responden | `sudo python3 main.py` |
| Speedtest falla | Instalar CLI oficial Ookla |
| USB no expulsa | `sudo apt install udisks2` |
| Homebridge no conecta | Verificar `.env` y que Insecure Mode esté activo |
| Red Local no escanea | `sudo apt install arp-scan` y configurar sudoers |
| Pi-hole no conecta | Verificar `.env`; solo compatible con v6 |
| VPN badge siempre rojo | Verificar que la interfaz (`tun0`/`wg0`) coincide en `vpn_monitor.py` |
| Brillo no disponible | Instalar `wlr-randr` si Wayland |
| No puedo escribir en entries (VNC) | Verificar que se usa `make_entry()` de `ui/styles.py` |
| Foco perdido tras inactividad (Wayland) | `gsettings set org.gnome.desktop.session idle-delay 0` |
| Dashboard no visible por VNC en Pi 5 | Usar `wayvnc --output=DSI-2 0.0.0.0 5901` |
| LEDs con destellos | Ver `FIX_LED_DESTELLOS.md` |
| Audio no suena | `aplay -l` → verificar dispositivo HDMI |
| Cámara no encontrada | `sudo apt install rpicam-apps` + `sudo usermod -aG video $(whoami)` |
| SMART muestra N/D | `sudo smartctl -A /dev/nvme0` + revisar sudoers |
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

| Métrica | v3.4 | v3.7 |
|---------|------|------|
| Versión | 3.4 | **3.7** |
| Archivos Python | 60 | **63** |
| Ventanas | 21 | **24** |
| Temas | 15 | 15 |
| Servicios background | 14 | 14 |
| Badges en menú | 12 | 12 |
| Documentos | 9 | **9** |

---

## Changelog

### **v3.7** - 2026-03-02 ⭐ ACTUAL
- ✅ **NUEVO**: Gestor Crontab — `CrontabWindow` con ver/añadir/editar/eliminar entradas, selector de usuario (usuario/root), accesos rápidos de programación, preview legible de expresión cron
- ✅ **FIX**: `grab_release()` garantizado al cerrar popups modales (`terminal_dialog`, `exit_application`) — elimina el bloqueo de foco en toda la app al cerrar diálogos
- ✅ **FIX**: `make_entry()` en `ui/styles.py` — fuerza foco al widget interno en VNC con `overrideredirect(True)`; usar siempre en lugar de `ctk.CTkEntry()` directamente
- ✅ **MEJORA**: Soporte dual-Pi sin tocar git — `config/local_settings.py` (en `.gitignore`) permite configuración independiente por máquina
- ✅ **MEJORA**: Pi 3B+ — pantalla virtual Xvfb en `:1` (1024×762), dashboard aislado del escritorio XFCE, acceso VNC en puerto `5901`
- ✅ **MEJORA**: Pi 5 Wayland — acceso remoto via `wayvnc --output=DSI-2`, fix idle `gsettings idle-delay 0`

### **v3.6.5** - 2026-02-XX
- ✅ **NUEVO**: Gestor de Botones — `ButtonManagerWindow` para mostrar/ocultar botones del menú principal con persistencia en `data/button_config.json`
- ✅ **NUEVO**: `WindowManager` en `ui/window_manager.py` — aplica configuración de visibilidad al arrancar

### **v3.6** - 2026-02-XX
- ✅ **NUEVO**: Servicios Dashboard — `ServicesManagerWindow` para activar/desactivar servicios background del dashboard desde la UI

### **v3.5** - 2026-02-XX
- ✅ **NUEVO**: `ServiceRegistry` — registro centralizado de todos los servicios del dashboard, con soporte para activar/desactivar y persistir configuración en `data/services.json`

### **v3.4** - 2026-02-27
- ✅ Control LEDs RGB, temperatura chasis, alertas audio, cámara OCR, SMART NVMe extendido

### **v3.3** - 2026-02-27
- ✅ Resumen Sistema, control brillo DSI, gestor VPN

### **v3.2** - 2026-02-27
- ✅ Escáner red local, Pi-hole v6, historial alertas

### **v3.1** - 2026-02-26
- ✅ Alertas Telegram, Homebridge extendido (5 tipos)

### **v3.0** - 2026-02-26
- ✅ Visor de Logs, exports organizados, fix grab_set FanControl

### v2.x
- Monitor completo, servicios systemd, histórico SQLite, 15 temas, badges, logging

### v1.0 - 2025-01
- Release inicial

---

## Licencia

MIT License

---

## Agradecimientos

CustomTkinter · psutil · matplotlib · Ookla Speedtest CLI · Homebridge · Pi-hole · Raspberry Pi Foundation
</file>

<file path="IDEAS_EXPANSION.md">
# 💡 IDEAS_EXPANSION.md
## Expansión y Roadmap — Sistema de Monitoreo v3.7

---

## ✅ Implementado

### v3.7 (actual) — Crontab + Fixes + Multi-Pi
- **Gestor Crontab** (`CrontabWindow`)
  - Ver, añadir, editar y eliminar entradas del crontab
  - Selector de usuario: usuario / root
  - Accesos rápidos de programación (@reboot, cada hora, cada día, etc.)
  - Preview legible de la expresión cron

- **Fix grab modal** (`dialogs.py` + `main_window.py`)
  - `grab_release()` garantizado al cerrar `terminal_dialog` y `exit_application`
  - Elimina el bloqueo de foco en toda la app al cerrar diálogos

- **`make_entry()`** (`ui/styles.py`)
  - Reemplaza `ctk.CTkEntry()` en ventanas con entries
  - Fuerza foco al widget interno con `focus_force()` al hacer clic
  - Soluciona escritura en VNC con `overrideredirect(True)`

- **Soporte dual-Pi** (`config/local_settings.py`)
  - Configuración independiente por máquina sin tocar git
  - Pi 3B+: Xvfb `:1`, resolución 1024×762, VNC puerto 5901
  - Pi 5: Wayland + labwc, wayvnc `--output=DSI-2`, idle-delay 0

### v3.6.5
- **Gestor de Botones** (`ButtonManagerWindow` + `WindowManager`)
  - Mostrar/ocultar botones del menú principal desde la UI
  - Persistencia en `data/button_config.json`

### v3.6
- **Servicios Dashboard** (`ServicesManagerWindow`)
  - Activar/desactivar servicios background del dashboard desde la UI
  - Persistencia en `data/services.json`

### v3.5
- **ServiceRegistry** (`core/service_registry.py`)
  - Registro centralizado de todos los servicios del dashboard
  - Base para `ServicesManagerWindow` y `ButtonManagerWindow`

### v3.4 — Hardware FNK0100K
- **LEDs RGB inteligentes** (`LedService` + `LedWindow`) — 6 modos, sin destellos
- **Temperatura chasis + Fan duty real** (`HardwareMonitor`) — via `hardware_state.json`
- **Alertas de audio** (`AudioAlertService`) — 11 .wav, TTS español, 4 métricas
- **Cámara OV5647 + Escáner OCR** (`CameraWindow`) — Tesseract local, `.txt` y `.md`
- **NVMe SMART extendido** — TBW, horas, ciclos, % vida útil

### v3.3
- **Resumen del Sistema** (`OverviewWindow`)
- **Control de Brillo DSI** (`DisplayService` + `DisplayWindow`)
- **Gestor VPN** (`VpnMonitor` + `VpnWindow`)

### v3.2
- **Escáner Red Local** (`NetworkScanner`) — arp-scan
- **Pi-hole v6** (`PiholeMonitor`) — API v6
- **Historial de Alertas** (`AlertHistoryWindow`)

### v3.1
- **Alertas Telegram** (`AlertService`)
- **Homebridge extendido** — 5 tipos de dispositivo

### v3.0
- Visor de Logs con filtros y exportación

### v2.x
- Control Ventiladores PWM, monitores completos, 15 temas, badges, logging, SQLite

---

## 🔄 Ideas en evaluación para v3.8+

### 🖥️ Información del Hardware
- Modelo de Pi, revisión, memoria total, versión del SO, kernel
- Ventana estática tipo "Acerca de este equipo"
- Sin dependencias nuevas — `vcgencmd`, `/proc/cpuinfo`, `uname`

### 🔒 Monitor SSH
- Leer `/var/log/auth.log` y mostrar intentos fallidos de acceso
- Badge con contador de intentos en las últimas 24h
- Lista con IP origen, usuario y timestamp de cada intento

### 📡 Monitor WiFi
- Intensidad de señal en dBm, calidad, SSID conectado, canal
- Gráfica histórica de señal
- Badge si la señal baja de umbral configurable

### 📝 Editor de Configuración
- Editar `config/settings.py`, `config/local_settings.py` y `.env` desde la UI
- Sin necesidad de SSH para cambios rápidos de configuración
- Solo las secciones relevantes para el usuario (posición pantalla, launchers, credenciales)

---

## 💭 Ideas futuras (backlog)

### API REST local
- Endpoint `/status` que devuelva el estado del sistema en JSON
- `http.server` de stdlib

### Backup automático de configuración
- Copiar `data/` a NAS o USB al detectar dispositivo montado

### Multi-pantalla / modo kiosk
- Detectar pantalla HDMI conectada y extender la UI

---

## 🗺️ Roadmap

```
v3.0  ✅ Visor Logs
v3.1  ✅ Telegram + Homebridge extendido
v3.2  ✅ Red Local + Pi-hole v6 + Historial Alertas
v3.3  ✅ Resumen Sistema + Brillo DSI + Gestor VPN
v3.4  ✅ LEDs RGB + Temp Chasis + Audio + Cámara OCR + SMART
v3.5  ✅ ServiceRegistry
v3.6  ✅ ServicesManagerWindow
v3.6.5 ✅ ButtonManagerWindow
v3.7  ✅ CrontabWindow + Fixes VNC/Wayland + Multi-Pi  ← ACTUAL
v3.8  🔄 Info Hardware + Monitor SSH + Monitor WiFi + Editor Config
v4.0  💭 API REST + Backup + Multi-pantalla?
```

---

## 📊 Cobertura por módulo (v3.7)

| Área | Cobertura | Notas |
|------|-----------|-------|
| Hardware CPU/RAM/Temp/Disco | ✅ Completa | SystemMonitor + DiskMonitor |
| NVMe SMART | ✅ Completa | TBW, horas, vida útil, ciclos |
| Red | ✅ Completa | NetworkMonitor + NetworkScanner |
| Procesos / Servicios systemd | ✅ Completa | ProcessMonitor + ServiceMonitor |
| Servicios Dashboard | ✅ Completa | ServiceRegistry + ServicesManagerWindow |
| Fans | ✅ Completa | FanController + FanAutoService |
| Crontab | ✅ Completa | CrontabWindow, usuario/root |
| Menú configurable | ✅ Completa | ButtonManagerWindow + WindowManager |
| Pantalla | ✅ Completa | DisplayService (brillo DSI) |
| VPN | ✅ Básica | VpnMonitor (estado + conectar/desconectar) |
| Homebridge / HomeKit | ✅ Avanzada | 5 tipos de dispositivo |
| Pi-hole | ✅ Completa | API v6, estadísticas, badge |
| Alertas Telegram | ✅ Completa | edge-trigger + historial JSON |
| Alertas Audio | ✅ Completa | 11 sonidos TTS español, 4 métricas |
| Histórico / Análisis | ✅ Completa | SQLite + matplotlib |
| LEDs RGB GPIO Board | ✅ Completa | 6 modos, sin destellos |
| Temperatura chasis | ✅ Completa | Via fase1.py + hardware_state.json |
| Fan duty real | ✅ Completa | Via fase1.py + hardware_state.json |
| Cámara OV5647 | ✅ Completa | rpicam-still + OCR Tesseract |
| Multi-Pi / local_settings | ✅ Completa | Pi 5 Wayland + Pi 3 Xvfb |
| Info Hardware | ❌ Pendiente | v3.8 
| Monitor SSH | ❌ Pendiente | v3.8 |
| Monitor WiFi | ❌ Pendiente | v3.8 |
| Editor Configuración | ❌ Pendiente | v3.8 |
</file>

<file path="INDEX.md">
# 📚 Índice de Documentación - System Dashboard v3.7

---

## 🚀 Documentos Esenciales

**[README.md](README.md)** ⭐ — Documentación completa v3.7. **Empieza aquí.**

**[QUICKSTART.md](QUICKSTART.md)** ⚡ — Instalación y ejecución en 5 minutos.

---

## 📖 Guías por tema

### 🎨 Personalización
**[THEMES_GUIDE.md](THEMES_GUIDE.md)** — 15 temas, crear personalizados.

### 🔧 Instalación
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — RPi OS, Kali, venv, script automático.

### 🏠 Homebridge
Configuración: ver sección en README.md.
5 tipos: `switch`, `light`, `thermostat`, `sensor`, `blind`.

### 🕳️ Pi-hole (v3.2)
Solo compatible con **Pi-hole v6**.
Añadir `PIHOLE_HOST`, `PIHOLE_PORT`, `PIHOLE_PASSWORD` al `.env`.

### 🖧 Red Local (v3.2)
Instalar: `sudo apt install arp-scan`.
Sudoers: `usuario ALL=(ALL) NOPASSWD: /usr/sbin/arp-scan`.

### 📲 Alertas Telegram
Configurar `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID` en `.env`.

### 🤝 Integración con fase1.py
**[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** — Compartir estado fans via JSON, OLED.

### 💡 Ideas y Expansión
**[IDEAS_EXPANSION.md](IDEAS_EXPANSION.md)** — Roadmap, backlog, cobertura por módulo.

### 🖥️ Multi-Pi (v3.7)
Crear `config/local_settings.py` (en `.gitignore`) con los valores de `DSI_X/Y/WIDTH/HEIGHT` para cada máquina.
- **Pi 5 Wayland**: `wayvnc --output=DSI-2 0.0.0.0 5901` + `gsettings set org.gnome.desktop.session idle-delay 0`
- **Pi 3B+ Xvfb**: display virtual `:1`, VNC puerto `5901`, resolución configurable

---

## 📋 Archivos de soporte

| Archivo | Propósito |
|---------|-----------|
| `requirements.txt` | Dependencias Python |
| `REQUIREMENTS.md` | Requisitos detallados con sistema |
| `.env` | Credenciales (NO en git) |
| `.env.example` | Plantilla |
| `config/settings.py` | Constantes globales |
| `config/local_settings.py` | Config por máquina (NO en git) |
| `config/themes.py` | 15 temas |
| `scripts/generate_sounds.py` | Genera los 11 audios de alerta |
| `scripts/sounds/` | Archivos .wav (tono + voz TTS español) |
| `data/fan_state.json` | fase1 lee — modo y PWM del ventilador |
| `data/led_state.json` | fase1 lee — modo y color de los LEDs |
| `data/hardware_state.json` | fase1 escribe — temp chasis + fan duty real |
| `data/services.json` | Servicios dashboard activos/inactivos |
| `data/button_config.json` | Visibilidad de botones del menú |
| `data/photos/` | Fotos capturadas con la cámara OV5647 |
| `data/scans/` | Escaneos OCR (.txt + .md) |

---

## 🗂️ Estructura de documentos v3.7

```
📚 Documentación/
├── README.md                         ⭐ Principal v3.7
├── QUICKSTART.md                     ⚡ Inicio rápido
├── INDEX.md                          📑 Este archivo
├── REQUIREMENTS.md                   📋 Requisitos
├── INSTALL_GUIDE.md                  🔧 Instalación
├── THEMES_GUIDE.md                   🎨 Temas
├── INTEGRATION_GUIDE.md              🤝 Integración fase1
├── IDEAS_EXPANSION.md                💡 Roadmap v3.8+
└── COMPATIBILIDAD.md                 🌐 Compatibilidad
```

---

## 🎯 Flujo de lectura recomendado

**Usuario nuevo:**
1. README.md → sección Características
2. QUICKSTART.md → instalar y ejecutar
3. Explorar las 24 ventanas 🎉

**Usuario avanzado / configurar integraciones:**
1. README.md completo
2. Sección Homebridge → `.env` + Insecure Mode
3. Sección Pi-hole → `.env` + compatibilidad v6
4. Sección Telegram → `.env` + `send_test()`
5. GUIA_GESTOR_VPN.md → scripts + interfaz
6. Sección Multi-Pi → `local_settings.py` + wayvnc / Xvfb

**Desarrollador / extender:**
1. README.md sección Arquitectura
2. `ui/styles.py` → `make_window_header()` y `make_entry()` para nuevas ventanas
3. `core/service_registry.py` → registrar nuevos servicios
4. IDEAS_EXPANSION.md → ver qué se puede añadir en v3.8

---

## 🔍 Buscar por problema

| Problema | Dónde mirar |
|----------|-------------|
| No arranca | QUICKSTART.md → Problemas Comunes |
| Brillo no funciona | GUIA_BRILLO_DSI.md → Paso 0 |
| VPN badge siempre rojo | GUIA_GESTOR_VPN.md → interfaz `tun0`/`wg0` |
| Pi-hole no conecta | README.md Troubleshooting (solo v6) |
| Red Local no escanea | README.md Troubleshooting (arp-scan + sudoers) |
| LEDs con destellos | FIX_LED_DESTELLOS.md |
| No puedo escribir en entries (VNC) | README.md → `make_entry()` en `ui/styles.py` |
| Foco perdido tras inactividad (Pi 5) | `gsettings set org.gnome.desktop.session idle-delay 0` |
| Dashboard no visible por VNC en Pi 5 | `wayvnc --output=DSI-2 0.0.0.0 5901` |
| Configuración distinta por máquina | `config/local_settings.py` (en `.gitignore`) |
| Homebridge no conecta | README.md Troubleshooting |
| Alertas Telegram no llegan | README.md sección Telegram / `.env` |
| SMART muestra N/D | Sudoers smartctl + `sudo smartctl -A /dev/nvme0` |
| Audio no suena | `aplay -l` → verificar dispositivo HDMI activo |
| Cámara no encuentra rpicam-still | `sudo apt install rpicam-apps` |
| Ver errores | `grep ERROR data/logs/dashboard.log` |

---

## 📊 Estadísticas del proyecto v3.7

| Métrica | v3.4 | v3.7 |
|---------|------|------|
| Versión | 3.4 | **3.7** |
| Archivos Python | 60 | **63** |
| Ventanas | 21 | **24** |
| Temas | 15 | 15 |
| Badges en menú | 12 | 12 |
| Servicios background | 14 | 14 |
| Documentos | 18 | 18 |

### Ventanas nuevas desde v3.4
- `ServicesManagerWindow` — Gestión servicios dashboard *(v3.6)*
- `ButtonManagerWindow` — Visibilidad botones menú *(v3.6.5)*
- `CrontabWindow` — Gestor de crontab *(v3.7)*

### Infraestructura nueva desde v3.4
- `ServiceRegistry` — registro centralizado *(v3.5)*
- `WindowManager` — gestión visibilidad botones *(v3.6.5)*
- `make_entry()` — entries compatibles con VNC/Wayland *(v3.7)*
- `local_settings.py` — config por máquina sin tocar git *(v3.7)*
</file>

</files>
