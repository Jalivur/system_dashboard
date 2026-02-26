# 💡 Ideas de Expansión - Dashboard v3.1

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
- ✅ 3 badges en el botón "Homebridge" del menú
- ✅ `_reachable = None` al arrancar → badges no aparecen hasta primera consulta real
- ✅ Configuración por `.env` — credenciales fuera del código
- ✅ Dependencia `python-dotenv>=1.0.0` con fallback manual si no está instalada

---

### ~~**13. Optimización de Rendimiento — UI sin bloqueos**~~ ✅ Implementado en v2.9
**Implementado en v2.9**
- ✅ `SystemMonitor` con thread de background (cada 2s) — `get_current_stats()` devuelve caché sin llamar psutil
- ✅ `ServiceMonitor` con thread de background (cada 10s) — `get_services()` / `get_stats()` devuelven caché
- ✅ `is-enabled` obtenido en una sola llamada batch (`systemctl is-enabled u1 u2 ...`) en lugar de N subprocesses
- ✅ `refresh_now()` fuerza refresco inmediato tras start/stop/restart/enable/disable
- ✅ `_update()` de `MainWindow` solo lee cachés — hilo de Tkinter completamente libre de syscalls bloqueantes
- ✅ Todos los servicios background registran inicio y parada en el log (`FanAutoService` incluido)
- ✅ `make_homebridge_switch()` en `ui/styles.py` — CTkSwitch (90×46px) estilado con colores del tema

---

### ~~**14. Control Homebridge con Switches Táctiles**~~ ✅ Implementado en v2.9
**Implementado en v2.9**
- ✅ `CTkSwitch` en lugar de botones ON/OFF — más intuitivo y adaptado al uso táctil
- ✅ Tamaño 90×46px óptimo para operar con el dedo en pantalla DSI de 4,5"
- ✅ Estado disabled en rojo para dispositivos con fallo (no interactivo)
- ✅ Colores del tema activo: success (ON), bg_light (OFF), danger (fallo)
- ✅ Nombre del dispositivo integrado como etiqueta del switch

---

### ~~**15. Visor de Logs**~~ ✅ Implementado en v3.0
**Implementado en v3.0**
- ✅ Ventana `LogViewerWindow` con filtros por nivel (DEBUG/INFO/WARNING/ERROR), módulo, texto libre e intervalo de fechas/horas
- ✅ Selector rápido: 15min, 1h, 6h, 24h o rango manual con date/time entries
- ✅ Colores por nivel: gris (DEBUG), azul (INFO), naranja (WARNING), rojo (ERROR)
- ✅ Exportación del resultado filtrado a `data/exports/logs/`
- ✅ Recarga manual — lee también el archivo rotado `.log.1`
- ✅ Scrollbar táctil (22px) integrado con `StyleManager.style_scrollbar_ctk`

---

### ~~**16. Exports organizados y limpieza al exportar**~~ ✅ Implementado en v3.0
**Implementado en v3.0**
- ✅ Carpetas `data/exports/{csv,logs,screenshots}` creadas automáticamente al arrancar (`settings.py`)
- ✅ `CleanupService` gestiona también `log_export_*.log` (máx. 10) — `DEFAULT_MAX_LOG`, `clean_log_exports()`
- ✅ Limpieza automática al exportar CSV, PNG y logs — no solo en el ciclo de 24h
- ✅ `get_status()` y `force_cleanup()` actualizados con `log_count` y `deleted_log`

---

### ~~**17. Fix grab_set en FanControlWindow**~~ ✅ Implementado en v3.0
**Implementado en v3.0**
- ✅ Eliminado `grab_set()` en `FanControlWindow` que bloqueaba el teclado en todas las ventanas al cerrarse
- ✅ El bug afectaba a entries en `history.py`, `service.py`, `process_window.py` y `log_viewer.py`

---

### ~~**18. Alertas Externas por Telegram**~~ ✅ Implementado en v3.1
**Implementado en v3.1**
- ✅ `AlertService` en `core/` — singleton, daemon thread, comprobación cada 15s
- ✅ Sin dependencias nuevas — usa `urllib` de la stdlib
- ✅ Métricas monitorizadas: temperatura, CPU, RAM, disco (umbrales warn + crit independientes) y servicios fallidos
- ✅ Anti-spam: edge-trigger + sustain de 60s (condición debe mantenerse antes de enviar)
- ✅ Reseteo automático cuando la condición baja del umbral (permite nuevo flanco)
- ✅ `send_test()` para verificar configuración sin esperar una alerta real
- ✅ Configurable por `.env`: `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID`
- ✅ Si las variables no están configuradas, el servicio arranca pero no envía (warning en log)
- ✅ Integrado en `main.py` con `start()`/`stop()` y `atexit` igual que el resto de servicios

---

### ~~**19. Homebridge Extendido**~~ ✅ Implementado en v3.1
**Implementado en v3.1**
- ✅ `HomebridgeMonitor` reconoce ahora 5 tipos de dispositivo:
  - `switch` — característica `On` (enchufe / interruptor)
  - `light` — `On` + `Brightness` (luz regulable)
  - `thermostat` — `CurrentTemperature` + `TargetTemperature`
  - `sensor` — `CurrentTemperature` y/o `CurrentRelativeHumidity` (solo lectura)
  - `blind` — `CurrentPosition` (persiana / estor)
- ✅ `set_brightness(unique_id, brightness)` — control de brillo 0–100%
- ✅ `set_target_temp(unique_id, temp)` — control de temperatura objetivo en termostatos
- ✅ Tarjetas adaptativas en `HomebridgeWindow._create_device_card()` según `acc["type"]`
- ✅ Termostato: temperatura actual + botones +/− 0.5°C con closure mutable
- ✅ Sensor: lectura de temp y/o humedad con íconos 🌡 💧
- ✅ Persiana: barra `CTkProgressBar` mostrando posición actual (control en HomeKit)

---

### ~~**20. UI Diálogo Salir**~~ ✅ Implementado en v3.1
**Implementado en v3.1**
- ✅ Radiobuttons táctiles 30×30px en el diálogo de salir (`radiobutton_width=30, radiobutton_height=30`)
- ✅ Botones ajustados a referencia estándar: Continuar `width=15, height=8`, Cancelar `width=20, height=10`
- ✅ `buttons_frame` con `side="bottom"` para evitar hueco inferior en el layout

---

## 🔄 Planificado v3.2

### ~~**Historial de Alertas**~~ — Guía disponible: `GUIA_HISTORIAL_ALERTAS.md`
**Complejidad**: 🟢 Baja — 2-3h  
**Archivos**: `core/alert_service.py` (modificar), `ui/windows/alert_history.py` (nuevo)

- Persistencia en `data/alert_history.json` (máx. 100 entradas)
- Ventana nueva "Historial Alertas" con tarjetas por alerta: timestamp, métrica, nivel, valor
- Colores por nivel: naranja (warn), rojo (crit)
- Botón "Borrar todo" con confirmación
- Solo guarda alertas enviadas con éxito a Telegram (o siempre si se prefiere)

---

### ~~**Panel de Red Local (arp-scan)**~~ — Guía disponible: `GUIA_PANEL_RED_PIHOLE.md`
**Complejidad**: 🟡 Media — 3h  
**Archivos**: `core/network_scanner.py` (nuevo), `ui/windows/network_local.py` (nuevo)

- Escaneo con `sudo arp-scan --localnet` en thread background
- Lista de dispositivos: IP, MAC, fabricante, hostname resuelto
- Refresco manual + automático cada 60s
- Prerequisito: añadir `arp-scan` a sudoers para ejecución sin contraseña

---

### ~~**Pi-hole Stats**~~ — Guía disponible: `GUIA_PANEL_RED_PIHOLE.md`
**Complejidad**: 🟡 Media — 2-3h  
**Archivos**: `core/pihole_monitor.py` (nuevo), `ui/windows/pihole_window.py` (nuevo)

- `PiholeMonitor` — 9º servicio background, sondeo cada 60s, API Pi-hole v5
- Métricas: queries hoy, bloqueadas, % bloqueado, dominios en lista, clientes únicos, estado
- Configurable por `.env`: `PIHOLE_HOST`, `PIHOLE_PORT`, `PIHOLE_TOKEN`
- Badge `pihole_offline` en el menú si Pi-hole no responde
- Nota: requiere Pi-hole v5 (api.php); v6 tiene API diferente

---

## 🚀 Ideas Futuras (Backlog)

**Automatización**: cron visual, perfiles de ventiladores por hora, auto-reinicio servicios caídos

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

### **v2.7** ✅ — 2026-02-23
- ✅ Header unificado `make_window_header()` en todas las ventanas
- ✅ Status dinámico en tiempo real en el header
- ✅ Botón ✕ táctil 52×42px para pantalla DSI
- ✅ Speedtest migrado a CLI oficial de Ookla (JSON, MB/s reales)

### **v2.8** ✅ — 2026-02-23
- ✅ Integración Homebridge completa
- ✅ HomebridgeMonitor con JWT, sondeo 30s, caché en memoria
- ✅ HomebridgeWindow con toggle táctil en grid 2 columnas
- ✅ 3 badges Homebridge en menú principal

### **v2.9** ✅ — 2026-02-24
- ✅ SystemMonitor y ServiceMonitor con caché en background thread
- ✅ ServiceMonitor: is-enabled batch, sondeo 10s, refresh_now() tras acciones
- ✅ HomebridgeWindow: CTkSwitch táctil 90×46px en lugar de botones
- ✅ make_homebridge_switch() en ui/styles.py
- ✅ Logging completo en todos los servicios background (FanAutoService incluido)

### **v3.0** ✅ — 2026-02-26
- ✅ Visor de Logs con filtros avanzados y exportación
- ✅ Exports organizados en data/exports/{csv,logs,screenshots}
- ✅ Limpieza automática al exportar (CSV, PNG, logs)
- ✅ Fix grab_set en FanControlWindow — entries funcionan en todas las ventanas

### **v3.1** ✅ ACTUAL — 2026-02-26
- ✅ Alertas externas por Telegram (AlertService, anti-spam, 5 métricas)
- ✅ Homebridge extendido (5 tipos: switch, light, thermostat, sensor, blind)
- ✅ UI diálogo salir mejorada (radiobuttons 30×30, botones ajustados)

### **v3.2** (Próxima)
- [ ] Historial de alertas (ventana + persistencia JSON)
- [ ] Panel de red local (arp-scan, lista dispositivos)
- [ ] Pi-hole stats (monitor background, ventana métricas, badge)

### **v3.3** (Futuro)
- [ ] Automatización (cron visual, perfiles ventiladores, auto-reinicio)
- [ ] API REST básica

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
| Integración Homebridge (5 tipos) | ✅ 100% |
| Visor de logs con filtros y exportación | ✅ 100% |
| Exports organizados y limpieza automática | ✅ 100% |
| Alertas externas Telegram | ✅ 100% |
| Historial de alertas | 📋 Guía lista |
| Panel de red local (arp-scan) | 📋 Guía lista |
| Pi-hole stats | 📋 Guía lista |
| Automatización | ⏳ 0% |
| API REST | ⏳ 0% |

---

**Versión actual**: v3.1 — **Próxima**: v3.2 — **Última actualización**: 2026-02-26
