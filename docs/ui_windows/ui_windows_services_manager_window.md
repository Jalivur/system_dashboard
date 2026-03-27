# `ui.windows.services_manager_window`

> **Ruta**: `ui/windows/services_manager_window.py`

Ventana de gestión total de servicios background del Dashboard.

Permite parar y arrancar cada servicio de forma manual y completa.
Cuando un servicio está parado:
  - Su thread interno no corre
  - Sus métodos de acción devuelven sin hacer nada (ver parches en core/)
  - Las ventanas asociadas muestran aviso "Servicio detenido"

Recibe el ServiceRegistry completo — muestra todos los servicios registrados
que aparezcan en _DEFINITIONS.

El botón "Guardar predeterminado" persiste el estado actual al services.json
para que en el próximo arranque los servicios parados no se inicien.

## Imports

```python
import threading
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import confirm_dialog
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `ServicesManagerWindow(ctk.CTkToplevel)`

Manager total de servicios del dashboard.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_registry` | `registry` |
| `_services` | `registry.get_all()` |
| `_defs` | `[(k, lbl, emj, warn) for k, lbl, emj, warn in self._DEFINITIONS if k in self._services]` |

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, registry)`

Inicializa la ventana de gestión de servicios.

Configura la ventana toplevel, filtra servicios disponibles del registry,
crea la interfaz de usuario y inicia el bucle de refresco automático.

Args:
    parent: Ventana padre (CTkToplevel).
    registry: ServiceRegistry con todos los servicios disponibles.

#### `_create_ui(self)`

Crea la interfaz de usuario completa.

Incluye header de ventana, contenedor desplazable con filas de servicios,
y botones globales para acciones masivas (parar/iniciar todos, guardar).

#### `_create_row(self, parent, key, label, emoji, warn)`

Crea una fila UI para un servicio específico.

Incluye indicador circular de estado, nombre con emoji, label de status,
y botón toggle.

Args:
    parent: Frame contenedor.
    key: ID del servicio (str).
    label: Nombre legible.
    emoji: Icono Nerd Font.
    warn: Advertencia al parar (si aplica).

#### `_is_running(self, key: str) -> bool`

Consulta si un servicio está ejecutándose.

Args:
    key: ID del servicio.

Returns:
    bool: True si está corriendo según el registry.

#### `_update_row(self, key: str)`

Actualiza el estado visual de la fila de un servicio.

Cambia colores, textos y estado del botón según si está corriendo o busy.

Args:
    key: ID del servicio.

#### `_refresh_loop(self)`

Bucle infinito de refresco cada 1.5 segundos.

Actualiza todas las filas consultando estados reales.
Se auto-para si la ventana se destruye.

#### `_toggle(self, key: str, warn: str)`

Manejador del botón toggle de un servicio.

Muestra diálogo de confirmación (con warning si parar),
luego ejecuta la acción en thread separado.

Args:
    key: ID del servicio.
    warn: Texto de advertencia (si aplica).

#### `_execute(self, key: str, stop: bool)`

Ejecuta start o stop en thread daemon.

Maneja estado busy durante operación, loguea acciones,
captura errores y actualiza UI post-ejecución.

Args:
    key: ID del servicio.
    stop: True para parar, False para iniciar.

#### `_stop_all(self)`

Para todos los servicios corriendo tras confirmar.

Lista servicios activos, muestra diálogo multi-item,
ejecuta _execute(stop=True) en todos.

#### `_start_all(self)`

Inicia todos los servicios parados tras confirmar.

Lista servicios inactivos, muestra diálogo simple,
ejecuta _execute(stop=False) en todos.

#### `_save_defaults(self)`

Persiste el estado actual al services.json como configuración de arranque.
Llama set_service_enabled() por cada servicio según su estado en la UI —
no depende de que save_config() lea _running directamente.

</details>
