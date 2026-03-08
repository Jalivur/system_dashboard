# 📡 Guía de uso del EventBus

## Problema que resuelve

Los servicios se ejecutan en **threads secundarios** y no pueden acceder a widgets de Tkinter desde threads que no sean el principal. Esto causa:

```
RuntimeError: main thread is not in main loop
```

## ✅ Solución: EventBus thread-safe

El EventBus permite que los servicios **publiquen eventos** desde threads secundarios sin acceder a widgets. La UI se suscribe a estos eventos y actualiza widgets en el thread principal.

---

## 📝 Patrones de uso

### 1️⃣ Servicios: Publicar eventos

```python
from core.event_bus import get_event_bus

class MiServicio:
    def actualizar_status(self, status):
        # Cambio en datos → publica evento
        get_event_bus().publish("miservicio.status_changed", {
            "status": status,
            "timestamp": datetime.now()
        })
```

**Importante:** `publish()` es **thread-safe**, puede llamarse desde cualquier thread incluyendo el servicio.

---

### 2️⃣ UI: Suscribirse a eventos

```python
from core.event_bus import get_event_bus

class MiPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.status_label = ctk.CTkLabel(self, text="--")
        self.status_label.pack()
        
        # Suscribirse al evento
        bus = get_event_bus()
        bus.subscribe("miservicio.status_changed", self.on_status_changed)
    
    def on_status_changed(self, data):
        # Este callback se ejecuta en el thread principal 
        # (dentro del loop de eventos)
        status = data.get("status")
        self.status_label.configure(text=status)
```

**Nota:** El callback se ejecuta en el thread principal durante `UpdateLoop`, no es necesario usar `.after()`.

---

## 🎯 Casos de uso comunes

### Case 1: Servicio monitorea y publica cambios

```python
class SensorMonitor:
    def _monitor_loop(self):
        while self.running:
            temp = self._read_temperature()
            if temp > self.last_temp:
                # Publica cambio
                get_event_bus().publish("sensor.temperature_changed", {
                    "temp": temp,
                    "unit": "C"
                })
                self.last_temp = temp
            time.sleep(1)
```

### Case 2: UI actualiza labels

```python
def on_temperature_changed(data):
    temp = data.get("temp")
    self.temp_label.configure(text=f"{temp:0.1f}°C")

get_event_bus().subscribe("sensor.temperature_changed", on_temperature_changed)
```

### Case 3: Eventos con acciones en UI

```python
# Desde servicio
get_event_bus().publish("system.alert", {
    "level": "critical",
    "message": "CPU muy alta"
})

# En UI
def on_system_alert(data):
    level = data.get("level")
    msg = data.get("message")
    
    if level == "critical":
        show_error_dialog(msg)
    elif level == "warning":
        show_warning_banner(msg)

get_event_bus().subscribe("system.alert", on_system_alert)
```

---

## 🚨 Errores comunes a evitar

### ❌ MALO: Acceder a widgets desde servicio

```python
# ❌ NO HAGAS ESTO
class MiServicio:
    def __init__(self, ui_label):
        self.label = ui_label  # ¡Referencia a widget!
    
    def actualizar(self):
        self.label.configure(text="nuevo")  # ❌ RuntimeError!
```

### ✅ BUENO: Publicar al EventBus

```python
# ✅ HAZ ESTO
class MiServicio:
    def actualizar(self, dato):
        get_event_bus().publish("miservicio.datos_actualizados", {"dato": dato})

# En UI
def on_datos(data):
    self.label.configure(text=data.get("dato"))

get_event_bus().subscribe("miservicio.datos_actualizados", on_datos)
```

---

## 🔧 API del EventBus

### `publish(event_name: str, data: Any = None)`
- Publica un evento (thread-safe)
- `data` es un dict con los datos
- Puede llamarse desde cualquier thread

```python
get_event_bus().publish("evento.cambio", {"valor": 42})
```

### `subscribe(event_name: str, callback: Callable)`
- Suscribirse a un evento
- Callback recibe `data` como parámetro
- Debe ejecutarse en UI thread

```python
get_event_bus().subscribe("evento.cambio", mi_callback)
# Ahora whenever se publica "evento.cambio", mi_callback se ejecuta
```

### `unsubscribe(event_name: str, callback: Callable)`
- Dejar de escuchar un evento

```python
get_event_bus().unsubscribe("evento.cambio", mi_callback)
```

### `process_events()`
- Procesa todos los eventos pendientes
- **YA SE LLAMA AUTOMÁTICAMENTE** desde `UpdateLoop`
- No necesitas llamarla manualmente

---

## 📋 Convención de nombres de eventos

Usa notación `namespace.evento`:

```
system.cpu_changed
system.ram_changed
system.temperature_changed
system.alert

network.connection_lost
network.speed_changed

service.started
service.stopped
service.failed

ui.modal_opened
ui.modal_closed
```

---

## 🧼 Limpieza de suscriptores

**Importante:** Si necesitas dejar de escuchar un evento (ej, al cerrar una ventana), debes desuscribirse:

```python
class MiVentana(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        bus = get_event_bus()
        
        # Suscribirse
        bus.subscribe("sistema.estado", self.on_estado)
        
        # Al cerrar ventana, desuscribirse
        def on_destroy():
            bus.unsubscribe("sistema.estado", self.on_estado)
        
        self.protocol("WM_DELETE_WINDOW", on_destroy)
    
    def on_estado(self, data):
        self.label.configure(text=data.get("estado"))
```

---

## 🎯 Resumen

| **Problema** | **Solución** |
|---|---|
| Servicio necesita actualizar UI | → Publica evento con `get_event_bus().publish()` |
| UI necesita enterarse de cambios | → Se suscribe con `get_event_bus().subscribe()` |
| Thread secundario accediendo a Tkinter | → ¡Usa EventBus, no accedas directamente! |
| Ventana se destruye durante actualización | → EventBus maneja esto de forma segura |

---

## 📚 Arquitectura

```
┌─────────────────────┐
│  Servicios (threads)│
└──────────┬──────────┘
           │
        publish   ← thread-safe queue
           │
      [EventBus]  ← singleton
           │
        subscribe
           │
┌──────────▼──────────────┐
│  UI MainWindow          │
│  ├─ UpdateLoop          │
│  │  └─ process_events() │ ← ejecuta en thread principal
│  └─ Panel, Labels, etc  │
└─────────────────────────┘
```

Los eventos se procesan **una sola vez por ciclo de actualización de UI**, garantizando seguridad thread-safe.
