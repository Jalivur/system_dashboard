# `core.i2c_monitor`

> **Ruta**: `core/i2c_monitor.py`

> **Cobertura de documentación**: 🟢 100% (9/9)

core/i2c_monitor.py

Escaner I2C de solo lectura usando smbus2.
Detecta dispositivos en todos los buses /dev/i2c-* disponibles.

Arquitectura:
  - Thread daemon que escanea cada INTERVAL_SECONDS
  - get_stats() devuelve cache — nunca bloquea la UI
  - SOLO LECTURA: usa read_byte() para detectar ACK, nunca escribe
  - smbus2 es opcional — si no está instalado devuelve error descriptivo

---

## Tabla de contenidos

**Clase [`I2CMonitor`](#clase-i2cmonitor)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`get_stats()`](#get_statsself-dict)
  - [`scan_now()`](#scan_nowself-none)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import threading
import os
from utils.logger import get_logger
import smbus2
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `INTERVAL_SECONDS` | `30` |

## Clase `I2CMonitor`

Monitoriza el bus I2C mediante escaneo periódico y almacena en caché los resultados.
No realiza escrituras en el bus, solo lectura.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_lock` | `threading.Lock()` |
| `_stats` | `{}` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |
| `_thread` | `None` |

### Métodos públicos

#### `start(self) -> None`

Inicia el hilo daemon de escaneo periódico de monitoreo I2C.

Args:
    None

Returns:
    None

Raises:
    None

#### `stop(self) -> None`

Detiene el monitor de I2C y limpia la caché de estadísticas.

Args:
    None

Returns:
    None

Raises:
    None

#### `is_running(self) -> bool`

Indica si el monitor de I2C está actualmente en ejecución.

Returns:
    bool: True si el monitor está escaneando, False en caso contrario.

#### `get_stats(self) -> dict`

Retorna estadísticas thread-safe del último escaneo.

Args:
    Ninguno

Returns:
    dict: Diccionario con estadísticas, incluyendo 'error', 'buses' y 'total'.

Raises:
    Ninguno

#### `scan_now(self) -> None`

Fuerza un escaneo inmediato del bus I2C en un hilo daemon separado.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

<details>
<summary>Métodos privados</summary>

#### `__init__(self)`

Inicializa el monitor I2C con mecanismos de bloqueo y estado vacío.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_loop(self) -> None`

Ejecuta un bucle en un hilo daemon que realiza un escaneo inicial y luego 
se repite a intervalos regulares hasta ser detenido.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_scan(self) -> None`

Realiza un escaneo interno de buses I2C disponibles y cachea los resultados de manera thread-safe.

Args: 
    Ninguno

Returns: 
    Ninguno

Raises: 
    Ninguno

Nota: En caso de error, se actualiza el estado con un mensaje de error y una lista vacía de buses.

</details>
