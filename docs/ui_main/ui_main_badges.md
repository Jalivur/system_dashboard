# `ui.main_badges`

> **Ruta**: `ui/main_badges.py`

Gestor de badges del menu principal.

Los badges son indicadores visuales circulares superpuestos sobre los botones
del menu que muestran contadores (servicios caidos, actualizaciones pendientes)
o valores de temperatura/CPU/RAM/disco.

Uso en MainWindow:
    self._badge_mgr = BadgeManager(menu_btns=self._menu_btns)
    self._badge_mgr.create(btn, key="updates", offset_index=0)
    self._badge_mgr.update("updates", value=3)
    self._badge_mgr.update_temp("temp_fan", temp=72, color="#ff4444")

## Imports

```python
import tkinter as tk
from config.settings import COLORS, FONT_FAMILY, Icons
```

## Clase `BadgeManager`

Crea y actualiza los badges de notificacion sobre los botones del menu.

Cada badge es un Canvas circular flotante (place) anclado a la esquina
superior derecha del boton padre. Multiples badges en un mismo boton se
desplazan horizontalmente via offset_index.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_menu_btns` | `menu_btns` |

### Métodos públicos

#### `create(self, btn, key: str, offset_index: int = 0) -> None`

Crea un badge sobre btn y lo registra bajo key.
Si ya existia un badge con esa key lo sobreescribe.

Args:
    btn:          CTkButton padre
    key:          clave interna (ej. "updates", "temp_fan")
    offset_index: desplazamiento horizontal (0 = mas a la derecha)

#### `update(self, key: str, value: int, color: str = None) -> None`

Muestra u oculta el badge segun value.

Args:
    key:   clave del badge
    value: si > 0 muestra el badge; si == 0 lo oculta
    color: color de fondo opcional; si None usa danger o warning segun key

#### `update_temp(self, key: str, temp: int, color: str) -> None`

Muestra el badge con valor de temperatura.

Args:
    key:   clave del badge
    temp:  valor entero de temperatura
    color: color de fondo

#### `hide(self, key: str) -> None`

Oculta el badge sin cambiar su valor.

Args:
    key: Clave del badge a ocultar

<details>
<summary>Métodos privados</summary>

#### `__init__(self, menu_btns: dict)`

Args:
    menu_btns: referencia al dict {label → CTkButton} de MainWindow.
               Se usa para recuperar el widget padre al recrear badges
               tras un cambio de pestana.

#### `__contains__(self, key: str) -> bool`

Verifica si existe badge con la clave dada.

Args:
    key: Clave a verificar

Returns:
    True si existe el badge

</details>
