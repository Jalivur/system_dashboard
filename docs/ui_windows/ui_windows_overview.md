# `ui.windows.overview`

> **Ruta**: `ui/windows/overview.py`

Ventana de resumen general del sistema.
Muestra todas las métricas críticas en un solo vistazo.
Pensada para usarse como pantalla de reposo en la DSI.

## Imports

```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, CPU_WARN, CPU_CRIT, RAM_WARN, RAM_CRIT, TEMP_WARN, TEMP_CRIT, Icons
from ui.styles import StyleManager, make_window_header
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `OverviewWindow(ctk.CTkToplevel)`

Ventana de resumen — métricas críticas en un vistazo.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_monitor` | `system_monitor` |
| `_service_monitor` | `service_monitor` |
| `_pihole_monitor` | `pihole_monitor` |
| `_network_monitor` | `network_monitor` |
| `_disk_monitor` | `disk_monitor` |
| `_widgets` | `{}` |
| `_running` | `True` |

### Métodos públicos

#### `destroy(self)`

Destructor seguro: detiene loop _update y llama super().destroy().

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, system_monitor, service_monitor, pihole_monitor, network_monitor, disk_monitor)`

Inicializador principal de OverviewWindow.

Configura ventana DSI sin bordes en posición fija, almacena referencias
a 5 monitores, inicializa widgets/running, crea UI y lanza update loop.

Args:
    parent: Ventana padre.
    system_monitor: Monitor sistema (CPU/RAM/temp).
    service_monitor: Monitor servicios.
    pihole_monitor: Monitor Pi-hole.
    network_monitor: Monitor red.
    disk_monitor: Monitor disco.

#### `_create_ui(self)`

Construye la interfaz completa del dashboard de resumen.

Estructura:
- Frame principal con header draggable.
- Canvas con scrollbar para contenido.
- Grid 2 columnas x 3 filas para tarjetas (CPU, RAM, Temp, Disco, Red, Servicios).
- Fila completa para Pi-hole con 4 sub-métricas.
- Registra todos los labels de valores en self._widgets para actualizaciones.

#### `_update(self)`

Loop principal de actualización automática de todo el dashboard.

Llama refresh de cada sección cada 2000ms. Maneja errores silenciosamente
registrando en logger. Se auto-programa recursivamente con after().

#### `_color_for(self, value, warn, crit)`

Sistema de colores semáforo para métricas basado en umbrales.

Args:
    value (float): Valor numérico de la métrica.
    warn (float): Límite naranja (advertencia).
    crit (float): Límite rojo (crítico).

Returns:
    str: Clave de color ('danger', 'warning' o 'primary') de COLORS.

#### `_refresh_system(self)`

Actualiza tarjetas de sistema desde monitores respectivos.

CPU/RAM/Temp: De SystemMonitor con color por umbrales config.
Disco: De DiskMonitor (umbral hardcode 80/90%).
Muestra '-- (parado)' si monitor detenido.

#### `_refresh_services(self)`

Actualiza tarjeta servicios: fallidos vs total, con color rojo si hay fallos.

Formato: 'X caídos' (rojo) o 'N OK' (verde).

#### `_refresh_net(self)`

Actualiza velocidades red ↓MB/s ↑MB/s desde NetworkMonitor.

Formato: ↓X.X ↑Y.Y (azul primary).
Maneja excepciones mostrando '--'.

#### `_refresh_pihole(self)`

Actualiza 4 métricas Pi-hole: bloqueadas hoy, % bloqueo, total queries, estado.

Formato con separadores miles. Maneja sin datos o errores.

</details>
