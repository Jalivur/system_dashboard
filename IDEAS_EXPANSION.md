# 💡 Ideas de Expansión - Dashboard v2.8

---

## ✅ Implementado

### **1. Monitor de Procesos en Tiempo Real**
**Implementado en v2.0**
- ✅ Lista en tiempo real (Top 20) con PID, comando, usuario, CPU%, RAM%
- ✅ Búsqueda por nombre o comando
- ✅ Filtros: Todos / Usuario / Sistema
- ✅ Ordenar por PID, Nombre, CPU%, RAM%
- ✅ Matar procesos con confirmación
- ✅ Colores dinámicos según uso
- ✅ Pausa inteligente durante interacciones
- ✅ Estadísticas: procesos totales, CPU, RAM, uptime

---

### **2. Monitor de Servicios systemd**
**Implementado en v2.5**
- ✅ Lista completa de servicios systemd
- ✅ Estados: active, inactive, failed con iconos
- ✅ Start/Stop/Restart con confirmación
- ✅ Ver logs en tiempo real (últimas 50 líneas)
- ✅ Enable/Disable autostart
- ✅ Búsqueda y filtros (Todos / Activos / Inactivos / Fallidos)
- ✅ Estadísticas: total, activos, fallidos, enabled

---

### **3. Histórico de Datos**
**Implementado en v2.5 — ampliado en v2.5.1**
- ✅ Base de datos SQLite (~5MB/10k registros)
- ✅ Recolección automática cada 5 minutos en background
- ✅ Métricas guardadas: CPU, RAM, Temp, Disco I/O, Red, PWM, actualizaciones
- ✅ **8 gráficas**: CPU, RAM, Temperatura, Red Download, Red Upload, Disk Read, Disk Write, PWM
- ✅ Periodos: 24h, 7d, 30d
- ✅ Estadísticas completas: promedios, mínimos, máximos de todas las métricas
- ✅ Detección de anomalías automática
- ✅ Exportación a CSV
- ✅ Exportación de gráficas como imagen PNG
- ✅ Limpieza de datos antiguos configurable
- ✅ **Zoom, pan y navegación** sobre las gráficas (toolbar matplotlib)
- ✅ Registro de eventos críticos en BD separada

---

### **4. Sistema de Temas**
**Implementado en v2.0**
- ✅ 15 temas pre-configurados
- ✅ Cambio con un clic y reinicio automático
- ✅ Preview visual antes de aplicar
- ✅ Persistencia entre reinicios
- ✅ Todos los componentes usan colores del tema (sliders, scrollbars, radiobuttons)

---

### **5. Reinicio y Apagado**
**Implementado en v2.5**
- ✅ Botón Reiniciar con confirmación (aplica cambios de código)
- ✅ Botón Salir con opción de apagar el sistema
- ✅ Terminal de apagado (visualiza apagado.sh en vivo)

---

### **6. Actualizaciones del Sistema**
**Implementado en v2.5.1**
- ✅ Verificación al arranque en background (no bloquea la UI)
- ✅ Sistema de caché 12h (no repite apt update innecesariamente)
- ✅ Ventana dedicada con estado visual
- ✅ Instalación con terminal integrada en vivo
- ✅ Botón Buscar para forzar comprobación manual
- ✅ Refresco automático del estado tras instalar

---

### **7. Sistema de Logging Completo**
**Implementado en v2.5.1**
- ✅ Cobertura 100% en módulos core y UI
- ✅ Niveles diferenciados: DEBUG, INFO, WARNING, ERROR
- ✅ Rotación automática 2MB con backup
- ✅ Archivo fijo `data/logs/dashboard.log`

---

### **8. Lanzadores de Scripts**
**Implementado desde v1.0 — mejorado en v2.5.1**
- ✅ Scripts personalizados configurables en `settings.py`
- ✅ Terminal integrada que muestra el output en vivo
- ✅ Confirmación previa a ejecución
- ✅ Layout en grid configurable

---

### **9. Servicio de Limpieza Automática**
**Implementado en v2.6**
- ✅ `CleanupService` en `core/` — singleton, daemon thread
- ✅ Limpieza automática de CSV exportados (máx. 10)
- ✅ Limpieza automática de PNG exportados (máx. 10)
- ✅ Limpieza periódica de BD SQLite (registros >30 días, cada 24h)
- ✅ `force_cleanup()` para limpieza manual desde la UI
- ✅ Inyección de dependencias en `HistoryWindow`
- ✅ Botón "Limpiar Antiguos" delega en el servicio
- ✅ Red de seguridad por tamaño en `DataLogger` (>5MB → limpia a 7 días)

---

### ~~**10. Notificaciones Visuales en el Menú**~~ ✅ Implementado en v2.6
**Implementado en v2.6**
- ✅ Badge en "Actualizaciones" con paquetes pendientes (naranja)
- ✅ Badge en "Monitor Servicios" con servicios fallidos (rojo)
- ✅ Badge en "Control Ventiladores" y "Monitor Placa" con temperatura (naranja >60°C, rojo >70°C)
- ✅ Badge en "Monitor Placa" con CPU (naranja >75%, rojo >90%)
- ✅ Badge en "Monitor Placa" con RAM (naranja >75%, rojo >90%)
- ✅ Badge en "Monitor Disco" con uso de disco (naranja >80%, rojo >90%)
- ✅ Texto dinámico en badge (valor real: temperatura en °C, porcentaje)
- ✅ Color de texto adaptativo (negro sobre amarillo, blanco sobre rojo)

---

### ~~**11. Header Unificado con Status Dinámico**~~ ✅ Implementado en v2.7
**Implementado en v2.7**
- ✅ `make_window_header()` centralizado en `ui/styles.py`
- ✅ Header en todas las ventanas: título + status + botón ✕ táctil
- ✅ Botón ✕ de 52×42px, optimizado para uso táctil en pantalla DSI 4,5"
- ✅ Status dinámico en Monitor Placa: CPU%, RAM%, temperatura en tiempo real
- ✅ Status dinámico en Monitor Disco: espacio disponible + temperatura NVMe
- ✅ Status dinámico en Monitor Red: interfaz activa + velocidades de red
- ✅ Speedtest migrado a CLI oficial de Ookla (`--format=json`, MB/s reales)

---

### ~~**12. Integración Homebridge**~~ ✅ Implementado en v2.8
**Implementado en v2.8**
- ✅ `HomebridgeMonitor` en `core/` — singleton, daemon thread, sondeo cada 30s
- ✅ Autenticación JWT con renovación automática en 401
- ✅ Lectura desde caché en memoria para badges (sin peticiones HTTP adicionales)
- ✅ `toggle()` fuerza sondeo inmediato tras el comando
- ✅ Ventana `HomebridgeWindow` con grid de 2 columnas estilo Lanzadores
- ✅ Indicador ● color por dispositivo (on/off), ⚠ rojo si `StatusFault=1`
- ✅ Soporte para accesorios con característica HomeKit `On` (enchufes e interruptores)
- ✅ 3 badges en el botón "Homebridge" del menú:
  - `hb_offline` 🔴 — Homebridge sin conexión
  - `hb_on` 🟠 — N enchufes encendidos
  - `hb_fault` 🔴 — N dispositivos con StatusFault=1
- ✅ `_reachable = None` al arrancar → badges no aparecen hasta primera consulta real
- ✅ Configuración por `.env` — credenciales fuera del código
- ✅ Dependencia `python-dotenv>=1.0.0` con fallback manual si no está instalada

---

## 🔄 En Evaluación

### **Monitor de Contenedores Docker**
**Prioridad**: Alta si usas Docker en la Pi  
**Complejidad**: Media

- Start/Stop/Restart contenedores
- Ver logs en tiempo real
- Estadísticas de uso por contenedor (CPU, RAM)
- Ver puertos expuestos
- Similar a `docker ps` y `docker stats` pero visual

---

### **Soporte Homebridge extendido**
**Prioridad**: Media  
**Complejidad**: Baja-Media

- Termostatos (característica `CurrentTemperature`, `TargetTemperature`)
- Sensores de temperatura/humedad (solo lectura)
- Persianas y estores (característica `CurrentPosition`)
- Luces con brillo (`Brightness`)

---

### **Alertas Externas**
**Prioridad**: Baja  
**Complejidad**: Media

- Notificaciones por Telegram o webhook
- Alertas por temperatura alta sostenida, CPU, disco lleno, servicios caídos
- Configurable por umbral y duración

---

### **Monitor de GPU**
**Prioridad**: Muy baja (Raspberry Pi sin GPU dedicada)  
**Complejidad**: Media

---

## 🚀 Ideas Futuras (Backlog)

**Automatización**: cron visual, profiles de ventiladores por hora, auto-reinicio de servicios caídos

**Red avanzada**: monitor de dispositivos en red (nmap), Pi-hole stats, VPN panel

**Backup**: programar backups, estado con progreso, sincronización cloud

**Seguridad**: intentos de login fallidos, logs de seguridad, firewall status

**API REST**: endpoints para métricas, histórico y control de servicios

---

## 🎯 Roadmap

### **v2.5.1** ✅ — 2026-02-20
- ✅ Logging completo en todos los módulos
- ✅ Ventana Actualizaciones con caché y terminal
- ✅ 8 gráficas en Histórico (Red, Disco, PWM añadidas)
- ✅ Zoom y navegación en gráficas
- ✅ Fix bug atexit en DataCollectionService

### **v2.6** ✅ — 2026-02-22
- ✅ Badges de notificación visual en menú principal (6 badges, 5 botones)
- ✅ CleanupService — limpieza automática background de CSV, PNG y BD
- ✅ Fan control: entries con placeholder en lugar de sliders
- ✅ Inyección de dependencias profesional (CleanupService → HistoryWindow)

### **v2.7** ✅ — 2026-02-23
- ✅ Header unificado `make_window_header()` en todas las ventanas
- ✅ Status dinámico en tiempo real en el header
- ✅ Botón ✕ táctil 52×42px para pantalla DSI
- ✅ Speedtest migrado a CLI oficial de Ookla (JSON, MB/s reales)

### **v2.8** ✅ ACTUAL — 2026-02-23
- ✅ Integración Homebridge completa
- ✅ HomebridgeMonitor con JWT, sondeo 30s, caché en memoria
- ✅ HomebridgeWindow con toggle táctil en grid 2 columnas
- ✅ 3 badges Homebridge en menú principal
- ✅ Configuración por .env (credenciales seguras)

### **v3.0** (Futuro)
- [ ] Alertas externas (Telegram/webhook)
- [ ] API REST básica
- [ ] Monitor Docker (si aplica)
- [ ] Soporte Homebridge extendido (termostatos, sensores, persianas)

---

## 📈 Cobertura actual

| Área | Estado |
|------|--------|
| Monitoreo básico (CPU, RAM, Temp, Disco, Red) | ✅ 100% |
| Control avanzado (Ventiladores, Procesos, Servicios) | ✅ 100% |
| Histórico y análisis | ✅ 100% |
| Actualizaciones del sistema | ✅ 100% |
| Logging y observabilidad | ✅ 100% |
| Notificaciones visuales internas | ✅ 100% |
| UI unificada y táctil | ✅ 100% |
| Integración Homebridge (enchufes/interruptores) | ✅ 100% |
| Homebridge extendido (termostatos, sensores) | ⏳ 0% |
| Alertas externas | ⏳ 0% |
| Docker | ⏳ 0% |
| Automatización | ⏳ 0% |

---

**Versión actual**: v2.8 — **Última actualización**: 2026-02-23
