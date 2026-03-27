# `ui.window_lifecycle`

> **Ruta**: `ui/window_lifecycle.py`

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

## Imports

```python
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `WindowLifecycleManager`

Gestiona el ciclo de vida (crear / levantar / cerrar) de las ventanas hijas.

Cada ventana se registra con:
  - key        : identificador interno (str)
  - label      : constante BL.* usada para _btn_active/_btn_idle
  - factory    : callable sin argumentos que devuelve la instancia de la ventana
  - badge_keys : lista de claves de badge asociadas (informativo, no gestionado aqui)

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_on_active` | `on_btn_active` |
| `_on_idle` | `on_btn_idle` |
| `_registry` | `{}` |

### Métodos públicos

#### `register(self, key: str, label: str, factory, badge_keys = None) -> None`

Registra una ventana hija.

Args:
    key        : identificador unico (ej. "fan_control")
    label      : constante BL.* del boton asociado
    factory    : callable() → instancia CTkToplevel
    badge_keys : lista de claves de badge (opcional, solo informativo)

#### `open(self, key: str) -> None`

Abre la ventana registrada bajo key.
Si ya existe la levanta al frente; si no, la crea via factory.

#### `get(self, key: str)`

Devuelve la instancia activa de la ventana, o None si no existe.

#### `is_open(self, key: str) -> bool`

True si la ventana esta actualmente abierta.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, on_btn_active, on_btn_idle)`

Args:
    on_btn_active : callable(label) — resalta el boton en el menu
    on_btn_idle   : callable(label) — restaura el boton al estado normal

#### `_on_close(self, key: str, label: str) -> None`

Llamado cuando la ventana es destruida — limpia instancia y boton.

</details>
