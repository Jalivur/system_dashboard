# `utils.logger`

> **Ruta**: `utils/logger.py`

Sistema de logging robusto para el dashboard
Funciona correctamente tanto desde terminal como desde auto-start

Ubicación: utils/logger.py

## Imports

```python
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
import os
from config.local_settings_io import update_params
```

## Funciones

### `get_logger(name: str) -> logging.Logger`

Obtiene logger para un módulo.

Uso:
    from utils.logger import get_logger
    logger = get_logger(__name__)

### `get_dashboard_logger() -> DashboardLogger`

Devuelve la instancia singleton de DashboardLogger para control en runtime.

### `log_startup_info()`

Log información de inicio del sistema.

## Clase `_ExactLevelFilter(logging.Filter)`

Deja pasar únicamente registros cuyo nivel sea exactamente el indicado.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_level` | `level` |

### Métodos públicos

#### `filter(self, record: logging.LogRecord) -> bool`

Filtra registros de log, permitiendo solo aquellos cuyo nivel coincide exactamente
con el nivel configurado.

Args:
    record (logging.LogRecord): Registro de log a evaluar.

Returns:
    bool: True si el nivel coincide, False en caso contrario.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, level: int)`

Inicializa el filtro con el nivel de log exacto especificado.

Args:
    level (int): Nivel de logging exacto (e.g., logging.INFO).

</details>

## Clase `DashboardLogger`

Logger centralizado para el dashboard.

### Métodos públicos

#### `set_file_level(self, level: int) -> None`

Cambia el nivel del handler de fichero y persiste.

#### `set_console_level(self, level: int, exact: bool = False) -> None`

Cambia el nivel del handler de consola y persiste.

#### `set_module_level(self, module: str, level: int) -> None`

Fija el nivel de un sub-logger concreto y persiste.
level=NOTSET restablece la herencia del padre.

#### `force_rollover(self) -> None`

Fuerza la rotación del fichero de log inmediatamente.

#### `get_status(self) -> dict`

Devuelve el estado actual de los handlers y módulos con nivel explícito.

#### `get_active_modules(self) -> list`

Lista de nombres cortos de todos los sub-loggers instanciados.

#### `get_logger(self, name: str) -> logging.Logger`

Obtiene un logger con prefijo 'Dashboard.' para el módulo especificado.

Args:
    name (str): Nombre del módulo (e.g., 'ui', 'services').

Returns:
    logging.Logger: Logger configurado para el módulo.

<details>
<summary>Métodos privados</summary>

#### `__new__(cls)`

Implementa el patrón Singleton para asegurar una única instancia del logger.

Returns:
    DashboardLogger: La instancia única del logger.

#### `_setup_logger(self)`

Configura el logger con rutas absolutas y rotación automática.

#### `_load_saved_config(self, project_root: Path) -> dict`

Lee log_file_level, log_console_level, log_console_exact y
log_module_levels desde local_settings.py sin importar el módulo
local_settings_io para evitar dependencias circulares en el arranque.

#### `_persist(self) -> None`

Guarda la configuración de logging en local_settings.py via
local_settings_io.update_params(). Importación local para evitar
dependencia circular en el arranque del logger.

</details>
