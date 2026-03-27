# `ui.window_manager`

> **Ruta**: `ui/window_manager.py`

Gestor centralizado de ventanas y botones del menu principal.

## Imports

```python
import config.button_labels as BL
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `WindowManager`

Gestor centralizado de visibilidad de ventanas y botones del menú principal.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_registry` | `registry` |
| `_menu_btns` | `menu_btns` |
| `_columns` | `2` |
| `_rerender_cb` | `None` |

### Métodos públicos

#### `set_rerender_callback(self, cb) -> None`

Establece callback para re-render pestañas al cambiar ui_enabled.

Args:
    cb (Callable): Función MainWindow._switch_tab activa.

#### `apply_config(self) -> None`

Aplica configuración UI y ejecuta re-render.

#### `show(self, key: str) -> None`

Habilita botón/ventana en services.json['ui'][key] = true + re-render.

Args:
    key (str): ID ventana (e.g., 'fan_control').

#### `hide(self, key: str) -> None`

Oculta botón/ventana services.json['ui'][key] = false + re-render.

Args:
    key (str): ID ventana (e.g., 'fan_control').

#### `is_enabled(self, key: str) -> bool`

Consulta si ventana/botón está habilitado en config UI.

Args:
    key (str): ID ventana.

Returns:
    bool: services.json['ui'][key].

<details>
<summary>Métodos privados</summary>

#### `__init__(self, registry, menu_btns: dict)`

Inicializa gestor ventanas/botones con registry servicios.

Args:
    registry (ServiceRegistry): Central servicios/monitors.
    menu_btns (dict): Botones pestañas principales.

#### `_rerender(self) -> None`

Llama callback re-render pestañas (MainWindow._switch_tab).

</details>
