# `utils.logger`

> **Ruta**: `utils/logger.py`

> **Cobertura de documentación**: 🟢 100% (18/18)

Sistema de logging robusto para el dashboard
Funciona correctamente tanto desde terminal como desde auto-start

Ubicación: utils/logger.py

---

## Tabla de contenidos

**Funciones**
- [`get_logger()`](#funcion-get_logger)
- [`get_dashboard_logger()`](#funcion-get_dashboard_logger)
- [`log_startup_info()`](#funcion-log_startup_info)

**Clase [`_ExactLevelFilter`](#clase-_exactlevelfilter)**
  - [`filter()`](#filterself-record-logginglogrecord-bool)

**Clase [`DashboardLogger`](#clase-dashboardlogger)**
  - [`set_file_level()`](#set_file_levelself-level-int-none)
  - [`set_console_level()`](#set_console_levelself-level-int-exact-bool-false-none)
  - [`set_module_level()`](#set_module_levelself-module-str-level-int-none)
  - [`force_rollover()`](#force_rolloverself-none)
  - [`get_status()`](#get_statusself-dict)
  - [`get_active_modules()`](#get_active_modulesself-list)
  - [`get_logger()`](#get_loggerself-name-str-logginglogger)

---

## Dependencias internas

- `config.local_settings_io`

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

Obtiene un logger para un módulo específico.

Args:
    name (str): Nombre del módulo que solicita el logger.

Returns:
    logging.Logger: Instancia de logger configurada para el módulo.

Raises:
    None

### `get_dashboard_logger() -> DashboardLogger`

Devuelve la instancia singleton de DashboardLogger para control en runtime.

Args:
    Ninguno

Returns:
    DashboardLogger: La instancia singleton de DashboardLogger.

Raises:
    Ninguno

### `log_startup_info()`

Registra información de inicio del sistema en el registro de eventos.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

## Clase `_ExactLevelFilter(logging.Filter)`

Filtra registros de log permitiendo solo aquellos con un nivel de log exacto.

Args:
    level (int): Nivel de logging exacto (e.g., logging.INFO).

Returns:
    bool: True si el nivel coincide, False en caso contrario.

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_level` | `level` |

### Métodos públicos

#### `filter(self, record: logging.LogRecord) -> bool`

Filtra registros de log según su nivel exacto.

Args:
    record (logging.LogRecord): Registro de log a evaluar.

Returns:
    bool: True si el nivel coincide, False en caso contrario.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, level: int)`

Inicializa el filtro con el nivel de log exacto especificado.

Args:
    level (int): Nivel de logging exacto.

</details>

## Clase `DashboardLogger`

Clase que implementa un logger centralizado para el dashboard siguiendo el patrón Singleton.

Args:
    Ninguno

Returns:
    DashboardLogger: La instancia única del logger.

Raises:
    Ninguna excepción explícita.

Notas:
    La instancia única se crea automáticamente al invocar la clase.

### Métodos públicos

#### `set_file_level(self, level: int) -> None`

Establece el nivel de registro para el handler de fichero y persiste los cambios.

Args:
    level (int): El nuevo nivel de registro.

Returns:
    None

Raises:
    None

#### `set_console_level(self, level: int, exact: bool = False) -> None`

Establece el nivel de registro de la consola y persiste la configuración.

Args:
    level (int): El nuevo nivel de registro.
    exact (bool): Si True, solo se mostrarán mensajes con el nivel exacto. Por defecto es False.

Returns:
    None

Raises:
    None

#### `set_module_level(self, module: str, level: int) -> None`

Establece el nivel de registro para un módulo específico en el sistema de registro.

Args:
    module (str): Nombre del módulo para el que se establece el nivel de registro.
    level (int): Nivel de registro que se asigna al módulo.

Returns:
    None

Raises:
    None

#### `force_rollover(self) -> None`

Fuerza la rotación inmediata del fichero de log.

Args:
    None

Returns:
    None

Raises:
    None

#### `get_status(self) -> dict`

Devuelve el estado actual de los handlers y módulos con nivel explícito.

Args:
    Ninguno

Returns:
    dict: Diccionario con el estado de los handlers y módulos, incluyendo niveles de registro.

Raises:
    Ninguno

#### `get_active_modules(self) -> list`

Obtiene una lista de nombres cortos de todos los sub-loggers activos instanciados en el dashboard.

Args:
    Ninguno

Returns:
    list: Lista ordenada de nombres cortos de sub-loggers activos.

Raises:
    Ninguno

#### `get_logger(self, name: str) -> logging.Logger`

Obtiene un logger con prefijo 'Dashboard.' para el módulo especificado.

Args:
    name (str): Nombre del módulo (e.g., 'ui', 'services').

Returns:
    logging.Logger: Logger configurado para el módulo.

<details>
<summary>Métodos privados</summary>

#### `__new__(cls)`

Crea una nueva instancia del logger, aplicando el patrón Singleton para garantizar una única instancia.

Args:
    cls: La clase DashboardLogger.

Returns:
    DashboardLogger: La instancia única del logger.

Raises:
    None

#### `_setup_logger(self)`

Configura el logger con rutas absolutas y rotación automática.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

#### `_load_saved_config(self, project_root: Path) -> dict`

Carga la configuración guardada de niveles de registro desde el archivo local_settings.py.

Args:
    project_root: Ruta raíz del proyecto.

Returns:
    Un diccionario con la configuración guardada de niveles de registro.

Raises:
    Ninguna excepción es propagada explícitamente, aunque puede ocurrir una excepción genérica durante la ejecución.

#### `_persist(self) -> None`

Guarda la configuración actual de logging en el archivo local_settings.py.

Args: Ninguno

Returns: None

Raises: Exception - Si ocurre un error al persistir la configuración, se registra una advertencia.

</details>
