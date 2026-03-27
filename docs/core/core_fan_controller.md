# `core.fan_controller`

> **Ruta**: `core/fan_controller.py`

Controlador de ventiladores

## Imports

```python
from typing import List, Dict
from utils.file_manager import FileManager
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `FanController`

Controlador stateless para cálculo PWM según modo/curva de temperatura.
Lee/escribe fan_state.json y fan_curve.json via FileManager.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_file_manager` | `FileManager()` |
| `_running` | `True` |

### Métodos públicos

#### `start(self) -> None`

Activa controlador (stateless, siempre activo).

#### `stop(self) -> None`

Desactiva controlador (stateless, efecto mínimo).

#### `is_running(self) -> bool`

Verifica si el servicio está corriendo.

#### `compute_pwm_from_curve(self, temp: float) -> int`

Calcula el PWM basado en la curva y la temperatura

Args:
    temp: Temperatura actual en °C

Returns:
    Valor PWM (0-255)

#### `get_pwm_for_mode(self, mode: str, temp: float, manual_pwm: int = 128) -> int`

Obtiene el PWM según el modo seleccionado

Args:
    mode: Modo de operación (auto, manual, silent, normal, performance)
    temp: Temperatura actual
    manual_pwm: Valor PWM manual si mode='manual'

Returns:
    Valor PWM calculado (0-255)

#### `update_fan_state(self, mode: str, temp: float, current_target: int = None, manual_pwm: int = 128) -> Dict`

Actualiza el estado del ventilador

Args:
    mode: Modo actual
    temp: Temperatura actual
    current_target: PWM objetivo actual
    manual_pwm: PWM manual configurado

Returns:
    Diccionario con el nuevo estado

#### `add_curve_point(self, temp: int, pwm: int) -> List[Dict]`

Añade un punto a la curva

Args:
    temp: Temperatura en °C
    pwm: Valor PWM (0-255)

Returns:
    Curva actualizada

#### `remove_curve_point(self, temp: int) -> List[Dict]`

Elimina un punto de la curva

Args:
    temp: Temperatura del punto a eliminar

Returns:
    Curva actualizada

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa controlador stateless (sin estado interno).
FileManager para JSON state/curva.

</details>
