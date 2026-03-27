# `ui.windows.service_watchdog`

> **Ruta**: `ui/windows/service_watchdog.py`

Ventana Service Watchdog - monitor críticos + config inline

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, Icons
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.service_monitor import ServiceMonitor
from core.service_watchdog import ServiceWatchdog
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `ServiceWatchdogWindow(ctk.CTkToplevel)`

Ventana Service Watchdog systemd

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_service_monitor` | `service_monitor` |
| `_watchdog` | `watchdog` |
| `_search_var` | `ctk.StringVar(master=self)` |
| `_filter_var` | `ctk.StringVar(master=self, value='critical')` |
| `_critical_entry` | `ctk.StringVar(master=self)` |
| `_critical_list_label` | `None` |
| `_update_paused` | `False` |
| `_update_job` | `None` |
| `_umbral_debounce_id` | `None` |
| `_interval_debounce_id` | `None` |
| `_umbral_var` | `ctk.StringVar(master=self, value=str(_stats['threshold']))` |
| `_interval_var` | `ctk.StringVar(master=self, value=str(_stats['interval']))` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, service_monitor: ServiceMonitor, watchdog: ServiceWatchdog)`

Inicializador de la ventana Service Watchdog para monitoreo systemd.

Configura:
- Dependencias: ServiceMonitor, ServiceWatchdog
- Variables de estado/UI (search, filter, criticals, pause, debounces)
- Geometría DSI fullscreen no-resizable
- Llama _create_ui() y inicia _update() loop
- Log apertura

Args:
    parent: Ventana padre (CTk).
    service_monitor (ServiceMonitor): Instancia para queries servicios/logs.
    watchdog (ServiceWatchdog): Instancia para config/stats críticos.

#### `_create_ui(self)`

Crea la interfaz de usuario principal de la ventana Service Watchdog.

Construye todos los componentes visuales incluyendo:
- Header de ventana con título y botón cerrar
- Barra de estadísticas (críticos, restarts, umbral, estado)
- Panel de configuración (umbral, intervalo, botones APLIAR/Refrescar)
- Controles de búsqueda y filtro
- Encabezados de tabla
- Canvas scrollable para la tabla de servicios

Inicializa la geometría y estilos según configuración global (DSI).

#### `_create_controls(self, parent)`

Crea los controles interactivos superiores para filtrado y gestión.

Componentes:
- Campo de búsqueda con debounce para servicios por nombre
- Radio buttons para filtro (solo críticos / todos)
- Entry para añadir nuevo servicio crítico + botón AÑADIR
- Botón GUARDAR lista críticos

Args:
    parent: Frame contenedor principal.

#### `_create_column_headers(self, parent)`

Crea la fila de encabezados para la tabla scrollable de servicios.

Columnas: Servicio | Estado | Fallos | Actions (reiniciar/ver logs)
Usa grid con pesos para responsividad.

Args:
    parent: Frame contenedor de headers.

#### `_debounce_umbral_update(self)`

Maneja el debounce para cambios en el campo de umbral de fallos críticos.

Cancela cualquier timer previo y programa _on_umbral_change después de 400ms
de inactividad en el entry, evitando múltiples llamadas durante tipificación rápida.

#### `_on_umbral_change(self, val)`

Valida y aplica cambios al umbral de fallos consecutivos críticos.

Convierte entrada a entero, clamp entre 1-10, actualiza StringVar y label visual.

Args:
    val (str): Valor crudo del entry field.

#### `_debounce_interval_update(self)`

Maneja el debounce para cambios en el campo de intervalo de monitoreo.

Cancela timer previo y programa _on_interval_change tras 400ms de inactividad.

#### `_on_interval_change(self, val)`

Valida y aplica cambios al intervalo de chequeo periódico del watchdog.

Convierte a entero, clamp 30-300s, actualiza StringVar y label.

Args:
    val (str): Valor del entry field.

#### `_apply_config(self)`

Aplica configuración actual de umbral e intervalo al ServiceWatchdog.

Valida rangos finales, llama set_threshold/set_interval, confirma con msgbox.
Maneja ValueError mostrando mensaje de error.

#### `_debounced_search(self)`

Implementa búsqueda en tiempo real con debounce para nombres de servicios.

Cancela búsqueda previa y agenda _update_now tras 400ms sin teclas,
optimizando rendimiento durante tipificación.

#### `_on_filter(self)`

Responde a cambio de filtro de servicios (críticos/todos).

Pausa actualizaciones por 1.5s para evitar flicker durante transición,
llamando _resume_updates.

#### `_resume_updates(self)`

Reanuda el ciclo de actualizaciones periódicas tras pausa temporal.

Usado después de cambios de filtro para estabilizar UI.

#### `_force_update(self)`

Fuerza actualización inmediata de datos y UI.

Despausa updates si estaban detenidos y llama _update_now directamente.
Usado por botón Refrescar.

#### `_update(self)`

Loop principal de actualización periódica de la UI.

Verifica existencia ventana, respeta pausa, llama _update_now,
reprograna cada UPDATE_MS*2 (2000ms típicamente).

#### `_update_now(self)`

Actualización inmediata y completa de estadísticas y tabla de servicios.

- Actualiza label stats desde watchdog.get_stats()
- Limpia y reconstruye tabla con servicios filtrados (search + filter)
- Max 25 filas, alterna colores filas, iconos estado, badges fallos/restarts
- Botones por fila: restart (confirm), logs (modal)

#### `_do_restart(self, name)`

Inicia reinicio seguro de servicio con confirmación del usuario.

Crea closure action() que llama ServiceMonitor.restart_service,
muestra msgbox resultado, refresca UI.
Usa confirm_dialog con ícono warning.

Args:
    name (str): Nombre exacto del servicio systemd (ej. 'nginx').

#### `_show_logs(self, name)`

Muestra logs recientes del servicio en modal.

Obtiene 30 líneas via ServiceMonitor.get_logs, trunca a 800 chars,
fallback "Sin logs" si vacío.

Args:
    name (str): Nombre del servicio.

#### `_add_critical(self)`

Añade servicio ingresado a lista de monitoreo crítico.

Valida no vacío/no duplicado via ServiceWatchdog.add_critical_service,
actualiza label lista, refresca tabla, confirma.

#### `_save_criticals(self)`

Persiste la lista actual de servicios críticos en watchdog.

Obtiene servicios desde stats['services'], llama set_critical_services,
confirma con msgbox.

#### `_update_critical_label(self)`

Actualiza label textual con lista actual de servicios críticos.

Formato "Críticos: service1, service2..." o ignora si label None.

</details>
