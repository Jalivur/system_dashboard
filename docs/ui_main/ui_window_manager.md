# `ui.window_manager`

> **Ruta**: `ui/window_manager.py`

> **Cobertura de documentación**: 🟢 100% (8/8)

Gestor centralizado de ventanas y botones del menu principal.

---

## Tabla de contenidos

**Clase [`WindowManager`](#clase-windowmanager)**
  - [`set_rerender_callback()`](#set_rerender_callbackself-cb-none)
  - [`apply_config()`](#apply_configself-none)
  - [`show()`](#showself-key-str-none)
  - [`hide()`](#hideself-key-str-none)
  - [`is_enabled()`](#is_enabledself-key-str-bool)

---

## Dependencias internas

- `config.button_labels`
- `utils.logger`

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

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_registry` | `registry` |
| `_menu_btns` | `menu_btns` |
| `_columns` | `2` |
| `_rerender_cb` | `None` |

### Métodos públicos

#### `set_rerender_callback(self, cb) -> None`

Establece el callback para re-renderizar las pestañas al cambiar el estado de ui_enabled.

Args:
    cb (Callable): La función callback a ejecutar para re-renderizar las pestañas.

Returns:
    None

Raises:
    None

#### `apply_config(self) -> None`

Aplica la configuración de la interfaz de usuario y ejecuta un re-renderizado.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

#### `show(self, key: str) -> None`

Habilita la visualización de una ventana específica en la interfaz de usuario.

Args:
    key (str): Identificador de la ventana (por ejemplo, 'fan_control').

Returns:
    None

Raises:
    None

#### `hide(self, key: str) -> None`

Oculta un botón o ventana específica en la interfaz de usuario.

Args:
    key (str): ID de la ventana a ocultar (e.g., 'fan_control').

Returns:
    None

Raises:
    None

#### `is_enabled(self, key: str) -> bool`

Consulta si una ventana o botón está habilitado en la configuración de la interfaz de usuario.

Args:
    key (str): ID de la ventana.

Returns:
    bool: Estado de habilitación de la ventana o botón.

Raises:
    None

<details>
<summary>Métodos privados</summary>

#### `__init__(self, registry, menu_btns: dict)`

Inicializa el gestor de ventanas y botones con un registro de servicios.

Args:
    registry (ServiceRegistry): Registro central de servicios y monitores.
    menu_btns (dict): Diccionario de botones de las pestañas principales.

Returns:
    None

Raises:
    None

#### `_rerender(self) -> None`

Re-renderiza la ventana llamando al callback registrado.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
