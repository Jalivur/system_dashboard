# Service Watchdog Window

**Ubicación**: `ui/windows/service_watchdog.py`

## ✨ Características

- **Monitor de servicios críticos systemd** con umbral configurable de fallos consecutivos
- **Lista dinámica**: Servicios críticos vs todos, búsqueda en vivo
- **Acciones por servicio**: Reinicio (confirmación), logs recientes
- **Estadísticas globales**: Críticos activos, restarts hoy, estado del watchdog
- **Gestión críticos**: Añadir/guardar lista persistente

## ⚙️ Configuración Inline (mejoras v4.1+)

| Parámetro | Rango | Actualización |
|-----------|-------|--------------|
| **Umbral** | 1-10 | Entry texto + debounce 400ms + clamp |
| **Intervalo** | 30-300s | Entry texto + debounce 400ms + clamp |

**Mejoras implementadas:**
- Sliders reemplazados por **CTkEntry** para precisión exacta
- **Validación debounced** (400ms): typing fuera rango (ej. 400) no interfiere, clamp tras pausa
- **Label en vivo** sincronizado con valor validado
- **Apply button** con error handling: `ValueError` → msgbox

## 🔧 Uso

1. **Filtrar**: Radio "Críticos" / "Todos"
2. **Buscar**: Entry en vivo (debounced 400ms)
3. **Config**: Editar umbral/intervalo → **APLICAR**
4. **Añadir crítico**: Entry → AÑADIR → Guardar
5. **Acciones**: 🔄 Reiniciar, 👁️ Logs

## 📊 Dependencias

- `core/service_monitor.py` — `ServiceMonitor.get_services()`, `restart_service()`, `get_logs()`
- `core/service_watchdog.py` — `ServiceWatchdog` (threshold/interval, críticos, stats)

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| Lista vacía | Verificar servicios systemd: `systemctl list-units --type=service` |
| Críticos no persisten | Pulsar **Guardar** tras añadir |
| Valores inválidos | Clamp automático en Apply (Umbral 1-10, Intervalo 30-300) |
| Update pausado | Radio filter → espera 1.5s auto-resume |

**Actualizado**: v4.2 (2024) — Text entries + debounce para precisión.
