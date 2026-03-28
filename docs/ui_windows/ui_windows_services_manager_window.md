# `ui.windows.services_manager_window`

> **Ruta**: `ui/windows/services_manager_window.py`

> **Cobertura de documentación**: 🟢 100% (14/14)

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

---

## Tabla de contenidos

**Clase [`ServicesManagerWindow`](#clase-servicesmanagerwindow)**

---

## Dependencias internas

- `config.settings`
- `ui.styles`
- `ui.widgets`
- `utils.logger`

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

Ventana de gestión total de servicios del dashboard.

Args:
    None

Returns:
    None

Raises:
    None

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
crea la interfaz de usuario y prepara el entorno.

Args:
    parent: Ventana padre (CTkToplevel).
    registry: ServiceRegistry con todos los servicios disponibles.

Raises:
    Ninguna excepción específica.

#### `_create_ui(self)`

Crea la interfaz de usuario completa de la ventana de gestión de servicios.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_create_row(self, parent, key, label, emoji, warn)`

Crea una fila UI para un servicio específico.

Incluye indicador circular de estado, nombre con emoji y label de status.

Args:
    parent: Frame contenedor.
    key: ID del servicio.
    label: Nombre legible del servicio.
    emoji: Icono Nerd Font asociado al servicio.
    warn: Advertencia al parar el servicio.

Returns:
    None

Raises:
    None

#### `_is_running(self, key: str) -> bool`

Consulta si un servicio está ejecutándose.

Args:
    key (str): ID del servicio.

Returns:
    bool: True si el servicio está corriendo.

Raises:
    None

#### `_update_row(self, key: str)`

Actualiza el estado visual de la fila de un servicio según su estado de ejecución.

    Args:
        key (str): ID del servicio.

    Returns:
        None

    Raises:
        None

#### `_refresh_loop(self)`

Establece un bucle infinito que refresca el contenido de la ventana cada 1.5 segundos.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

#### `_toggle(self, key: str, warn: str)`

Manejador del botón toggle de un servicio.

Muestra diálogo de confirmación con warning si es necesario,
luego ejecuta la acción en thread separado.

Args:
    key (str): ID del servicio.
    warn (str): Texto de advertencia (si aplica).

Raises:
    Ninguna excepción específica.

#### `_execute(self, key: str, stop: bool)`

Ejecuta la acción de inicio o detención de un servicio en un hilo daemon.

Maneja el estado de ocupado durante la operación, loguea acciones, captura errores y actualiza la UI después de la ejecución.

Args:
    key (str): ID del servicio.
    stop (bool): True para detener, False para iniciar.

Raises:
    Exception: Si ocurre un error durante la ejecución de la acción.

#### `_stop_all(self)`

Para todos los servicios en ejecución después de confirmar con el usuario.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_start_all(self)`

Inicia todos los servicios parados tras confirmar.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_save_defaults(self)`

Persiste el estado actual de servicios como configuración de arranque en services.json.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
