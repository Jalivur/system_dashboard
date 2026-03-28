# `core.service_registry`

> **Ruta**: `core/service_registry.py`

> **Cobertura de documentación**: 🟢 100% (11/11)

Registro centralizado de servicios del Dashboard.

Gestiona el ciclo de vida de todos los servicios según configuración JSON.
Servicios y visibilidad de botones son configuraciones INDEPENDIENTES:
  - "services": controla si el servicio arranca al inicio
  - "ui":       controla si el botón aparece en el menú (WindowManager)

Uso en main.py:
    registry = ServiceRegistry()
    registry.register("system_monitor", SystemMonitor())
    ...
    registry.apply_config()              # para los que estén en False en services.json
    registry.set_service_enabled(k, v)   # marca habilitado/deshabilitado y persiste
    registry.save_config()               # persiste _config al JSON (sin leer estado live)

---

## Tabla de contenidos

**Clase [`ServiceRegistry`](#clase-serviceregistry)**
  - [`save_config()`](#save_configself)
  - [`set_service_enabled()`](#set_service_enabledself-key-str-enabled-bool-none)
  - [`register()`](#registerself-key-str-instance-none)
  - [`apply_config()`](#apply_configself-none)
  - [`get()`](#getself-key-str)
  - [`get_all()`](#get_allself-dict)
  - [`service_enabled()`](#service_enabledself-key-str-bool)
  - [`ui_enabled()`](#ui_enabledself-key-str-bool)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import json
import os
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |

## Clase `ServiceRegistry`

Registro centralizado de servicios del dashboard.

Args:
    config_path: Ruta opcional al archivo services.json

Returns:
    None

Raises:
    None

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_config_path` | `os.path.abspath(config_path or _CONFIG_PATH)` |
| `_config` | `{'services': dict(_DEFAULT_CONFIG['services']), 'ui': dict(_DEFAULT_CONFIG['ui'])}` |

### Métodos públicos

#### `save_config(self)`

Persiste la configuración actual al archivo JSON.

Args:
    None

Returns:
    None

Raises:
    Exception: Si ocurre un error al guardar la configuración.

Nota: No lee el estado live de los servicios, guarda lo que se haya establecido 
      explícitamente.

#### `set_service_enabled(self, key: str, enabled: bool) -> None`

Establece si un servicio está habilitado o deshabilitado en la configuración.

Args:
    key (str): La clave del servicio a actualizar.
    enabled (bool): El nuevo estado de habilitación del servicio.

Returns:
    None

Raises:
    None

#### `register(self, key: str, instance) -> None`

Registra un servicio en el registro de servicios.

Args:
    key (str): La clave única para identificar el servicio.
    instance: La instancia del servicio a registrar.

Returns:
    None

Raises:
    None

#### `apply_config(self) -> None`

Aplica la configuración de servicios, deteniendo aquellos que estén configurados como deshabilitados en services.json.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Exception: Si ocurre un error al detener un servicio.

#### `get(self, key: str)`

Recuperar la instancia de un servicio registrada por su clave.

Args:
    key (str): Clave del servicio a recuperar.

Returns:
    La instancia del servicio asociada a la clave, o None si no existe.

#### `get_all(self) -> dict`

Devuelve un diccionario con todos los servicios registrados.

Args:
    Ninguno

Returns:
    dict: Un diccionario con todos los servicios registrados.

Raises:
    Ninguno

#### `service_enabled(self, key: str) -> bool`

Determina si un servicio específico está configurado para arrancar.

Args:
    key (str): Clave del servicio a verificar.

Returns:
    bool: True si el servicio está configurado para arrancar, False en caso contrario.

#### `ui_enabled(self, key: str) -> bool`

Determina si un elemento de la interfaz de usuario está habilitado según la configuración.

Args:
    key (str): La clave de configuración para verificar.

Returns:
    bool: True si el elemento de la interfaz de usuario está habilitado, False en caso contrario.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, config_path: str = None)`

Inicializa el registro de servicios.

Args:
    config_path (str): Ruta opcional al archivo de configuración services.json.

#### `_load_config(self)`

Carga la configuración desde services.json y la inicializa con valores por defecto si no existe.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

</details>
