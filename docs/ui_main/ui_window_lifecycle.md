# `ui.window_lifecycle`

> **Ruta**: `ui/window_lifecycle.py`

> **Cobertura de documentación**: 🟢 100% (7/7)

Gestor del ciclo de vida de las ventanas hijas del dashboard.

Encapsula el patron repetido en MainWindow:
  - Comprobar si la ventana existe (winfo_exists)
  - Crearla via factory si no existe, o hacer lift si ya esta abierta
  - Gestionar _btn_active / _btn_idle al abrir y al cerrar

Uso en MainWindow:
    self._wlm = WindowLifecycleManager(
        on_btn_active=self._btn_active,
        on_btn_idle=self._btn_idle,
    )
    self._wlm.register("fan_control", BL.FAN_CONTROL,
        factory=lambda: FanControlWindow(self.root, self.fan_controller, ...),
        badge_keys=["temp_fan"],
    )
    # En _build_buttons_meta:
    BL.FAN_CONTROL: (lambda: self._wlm.open("fan_control"), ["temp_fan"])

    # Para ButtonManagerWindow (necesita la instancia):
    self._wlm.open("button_manager")
    instance = self._wlm.get("button_manager")

---

## Tabla de contenidos

**Clase [`WindowLifecycleManager`](#clase-windowlifecyclemanager)**
  - [`register()`](#registerself-key-str-label-str-factory-badge_keys-none-none)
  - [`open()`](#openself-key-str-none)
  - [`get()`](#getself-key-str)
  - [`is_open()`](#is_openself-key-str-bool)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `WindowLifecycleManager`

Gestiona el ciclo de vida de ventanas hijas, permitiendo su creación, activación y cierre.

Args:
    on_btn_active : función a llamar cuando un botón de ventana se activa
    on_btn_idle   : función a llamar cuando un botón de ventana se inactiva

Raises:
    No se documentan excepciones en esta clase.

Returns:
    No se documenta retorno en esta clase.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_on_active` | `on_btn_active` |
| `_on_idle` | `on_btn_idle` |
| `_registry` | `{}` |

### Métodos públicos

#### `register(self, key: str, label: str, factory, badge_keys = None) -> None`

Registra una ventana hija con su información asociada.

Args:
    key (str): Identificador único de la ventana.
    label (str): Etiqueta o constante asociada al botón de la ventana.
    factory (callable): Función que crea una instancia de CTkToplevel.
    badge_keys (list[str], opcional): Lista de claves de badge. Por defecto es None.

Returns:
    None

Raises:
    Ninguna excepción específica.

#### `open(self, key: str) -> None`

Abre la ventana registrada bajo la clave proporcionada.

Args:
    key (str): La clave de la ventana a abrir.

Returns:
    None

Raises:
    None

#### `get(self, key: str)`

Recupera la instancia activa de una ventana registrada.

Args:
    key (str): La clave de registro de la ventana.

Returns:
    La instancia activa de la ventana, o None si no existe o no está activa.

#### `is_open(self, key: str) -> bool`

Indica si una ventana específica está actualmente abierta.

Args:
    key (str): Identificador de la ventana.

Returns:
    bool: True si la ventana está abierta, False en caso contrario.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, on_btn_active, on_btn_idle)`

Inicializa el administrador del ciclo de vida de la ventana.

Args:
    on_btn_active (callable): Función que se llama cuando un botón está activo, recibe una etiqueta como parámetro.
    on_btn_idle (callable): Función que se llama cuando un botón está inactivo, recibe una etiqueta como parámetro.

#### `_on_close(self, key: str, label: str) -> None`

Limpia la instancia y el botón asociado cuando una ventana es cerrada.

Args:
    key (str): Clave de registro de la ventana.
    label (str): Etiqueta de la ventana.

Returns:
    None

Raises:
    None

</details>
