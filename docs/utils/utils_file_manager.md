# `utils.file_manager`

> **Ruta**: `utils/file_manager.py`

> **Cobertura de documentación**: 🟢 100% (8/8)

Gestión de archivos JSON para estado y configuración

---

## Tabla de contenidos

**Clase [`FileManager`](#clase-filemanager)**
  - [`write_state()`](#write_statedata-dictstr-any-none)
  - [`load_state()`](#load_state-dictstr-any)
  - [`load_curve()`](#load_curve-listdictstr-int)
  - [`save_curve()`](#save_curvepoints-listdictstr-int-none)

---

## Dependencias internas

- `config.settings`
- `utils.logger`

## Imports

```python
import json
import os
from typing import Dict, List, Any
from config.settings import STATE_FILE, CURVE_FILE
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `FileManager`

Gestor centralizado de archivos JSON.

Provee métodos estáticos para leer y escribir estados en formato JSON de manera segura.

### Métodos públicos

#### `write_state(data: Dict[str, Any]) -> None`

Escribe el estado de forma atómica usando un archivo temporal.

Args:
    data (Dict[str, Any]): Diccionario con los datos a guardar.

Raises:
    OSError: Si ocurre un error durante la escritura del estado.

Returns:
    None

#### `load_state() -> Dict[str, Any]`

Carga el estado guardado desde un archivo.

Args:
    Ninguno

Returns:
    Dict[str, Any]: Diccionario con el modo y el objetivo de PWM.

Raises:
    Ninguna excepción relevante, se manejan internamente.

#### `load_curve() -> List[Dict[str, int]]`

Carga la curva de ventiladores desde un archivo y devuelve una lista de puntos ordenados por temperatura.

Args:
    Ninguno

Returns:
    Lista de diccionarios con temperaturas (temp) y valores PWM (pwm) ordenados por temperatura.

Raises:
    Ninguna excepción específica, aunque puede registrar warnings si el archivo está malformado.

#### `save_curve(points: List[Dict[str, int]]) -> None`

Guarda la curva de ventiladores en un archivo.

Args:
    points: Lista de puntos con temperatura y PWM.

Raises:
    OSError: Si ocurre un error al escribir en el archivo.
