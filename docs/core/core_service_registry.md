# `core.service_registry`

> **Ruta**: `core/service_registry.py`

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

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_config_path` | `os.path.abspath(config_path or _CONFIG_PATH)` |
| `_config` | `{'services': dict(_DEFAULT_CONFIG['services']), 'ui': dict(_DEFAULT_CONFIG['ui'])}` |

### Métodos públicos

#### `save_config(self)`

Persiste la configuración actual (_config) al JSON.
No lee el estado live de los servicios — guarda lo que se haya
establecido explícitamente via set_service_enabled().

#### `set_service_enabled(self, key: str, enabled: bool) -> None`

Marca un servicio como habilitado/deshabilitado en la config y persiste.

#### `register(self, key: str, instance) -> None`

Registra un servicio. Solo lo almacena, no lo para ni arranca.

#### `apply_config(self) -> None`

Para todos los servicios configurados como False en services.json.

#### `get(self, key: str)`

Devuelve la instancia de un servicio por clave.

#### `get_all(self) -> dict`

Devuelve todos los servicios registrados.

#### `service_enabled(self, key: str) -> bool`

True si el servicio está configurado para arrancar.

#### `ui_enabled(self, key: str) -> bool`

True si el botón de UI está habilitado en la configuración.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, config_path: str = None)`

Inicializa el registro de servicios.

Args:
    config_path: Ruta opcional al archivo services.json

#### `_load_config(self)`

Carga services.json. Si no existe lo crea con valores por defecto.

</details>
