# `core.alert_service`

> **Ruta**: `core/alert_service.py`

> **Cobertura de documentación**: 🟢 100% (16/16)

Servicio de alertas externas por Telegram.
Sin dependencias nuevas — usa urllib de la stdlib.

Lógica anti-spam: cada alerta debe mantenerse activa durante
ALERT_SUSTAIN_S segundos antes de enviarse, y no se repite
hasta que baje del umbral y vuelva a subir (edge-trigger).

---

## Tabla de contenidos

**Clase [`AlertService`](#clase-alertservice)**
  - [`start()`](#startself-none)
  - [`stop()`](#stopself-none)
  - [`is_running()`](#is_runningself-bool)
  - [`get_history()`](#get_historyself-list)
  - [`clear_history()`](#clear_historyself-none)
  - [`send_test()`](#send_testself-bool)

---

## Dependencias internas

- `utils.logger`

## Imports

```python
import threading
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Optional
import os
from dotenv import load_dotenv
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `ALERT_SUSTAIN_S` | `60` |
| `CHECK_INTERVAL` | `15` |
| `THRESHOLDS` | `{'temp': {'warn': 60, 'crit': 70}, 'cpu': {'warn': 85, 'crit': 95}, 'ram': {'war...` |
| `MAX_HISTORY_ENTRIES` | `100` |

<details>
<summary>Funciones privadas</summary>

### `_load_telegram_config() -> tuple`

Carga la configuración de Telegram desde el archivo .env o las variables de entorno.

Args: 
    None

Returns: 
    tuple: Una tupla con el token y el ID de chat de Telegram.

Raises: 
    None

</details>

## Clase `AlertService`

Servicio de alertas que monitoriza métricas y envía notificaciones a Telegram.

Args:
    system_monitor: Monitor de métricas del sistema como CPU, temperatura, RAM y disco.
    service_monitor: Monitor de servicios para detectar fallas.

Raises:
    Ninguna excepción relevante.

Nota: Si no se configuran token y chat_id de Telegram, las alertas se desactivan.

### Atributos privados

| Atributo | Valor inicial |
|----------|---------------|
| `_system_monitor` | `system_monitor` |
| `_service_monitor` | `service_monitor` |
| `_lock` | `threading.Lock()` |
| `_running` | `False` |
| `_stop_evt` | `threading.Event()` |

### Métodos públicos

#### `start(self) -> None`

Inicia el servicio de monitoreo de alertas en segundo plano.

Args:
    None

Returns:
    None

Raises:
    None

#### `stop(self) -> None`

Detiene el servicio de alertas de manera segura.

Args:
    None

Returns:
    None

Raises:
    None

#### `is_running(self) -> bool`

Indica si el servicio de alertas está actualmente en ejecución.

Args:
    None

Returns:
    bool: Estado de ejecución del servicio.

Raises:
    None

#### `get_history(self) -> list`

Obtiene el historial de alertas enviadas desde el archivo de datos.

Args:
    None

Returns:
    list[dict]: Entradas con información de alertas, incluyendo timestamp, clave, nivel, valor, unidad y mensaje, ordenadas por recencia.

Raises:
    None

#### `clear_history(self) -> None`

Borra el historial de alertas.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Exception: Si ocurre un error al borrar el historial.

#### `send_test(self) -> bool`

Envía un mensaje de prueba para verificar la configuración.

Args:
    No requiere parámetros.

Returns:
    bool: True si el mensaje se envía correctamente.

Raises:
    No lanza excepciones explícitas.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, system_monitor, service_monitor)`

Inicializa el servicio de alertas con los monitores del sistema y de servicios.

Args:
    system_monitor: Monitor de métricas del sistema como CPU, temperatura, RAM y disco.
    service_monitor: Monitor de servicios para detectar fallas.

Returns:
    None

Raises:
    None

#### `_loop(self) -> None`

Ejecuta el bucle principal del servicio de alertas.

Args:
    None

Returns:
    None

Raises:
    Exception: Si ocurre un error durante la ejecución del bucle.

#### `_check_metrics(self) -> None`

Verifica los valores actuales de temperatura, CPU, RAM y disco contra los umbrales configurados.

Args:
    No aplica, utiliza atributos de instancia.

Returns:
    None

Raises:
    No se lanzan excepciones explícitas.

#### `_check_services(self) -> None`

Verifica el estado de los servicios y dispara una alerta si hay servicios con estado FAILED.

Args: 
    None

Returns: 
    None

Raises: 
    None

#### `_trigger(self, key: str, message: str, value: float = 0.0, unit: str = '', level: str = '') -> None`

Activa una alerta con retardo anti-spam.

Args:
    key (str): Identificador único de la alerta.
    message (str): Mensaje de la alerta.
    value (float): Valor asociado a la alerta (opcional).
    unit (str): Unidad del valor (opcional).
    level (str): Nivel de la alerta (opcional).

Returns:
    None

Raises:
    None

#### `_reset(self, key: str) -> None`

Resetea el estado de una alerta marcándola como condición resuelta.

Args:
    key (str): La clave de la alerta a resetear.

Returns:
    None

Raises:
    None

#### `_save_to_history(self, key: str, message: str, value: float, unit: str, level: str) -> None`

Guarda una alerta disparada en el historial de registros.

Args:
    key (str): Clave identificativa de la alerta.
    message (str): Mensaje descriptivo de la alerta.
    value (float): Valor numérico asociado a la alerta.
    unit (str): Unidad de medida del valor.
    level (str): Nivel de gravedad de la alerta.

Returns:
    None

Raises:
    Exception: Si ocurre un error durante el guardado del historial.

#### `_send(self, text: str) -> bool`

Envía un mensaje Markdown a Telegram.

Args:
    text (str): El texto del mensaje a enviar.

Returns:
    bool: True si el mensaje se envía con éxito, False en caso contrario.

Raises:
    Exception: Si ocurre un error durante el envío del mensaje.

</details>
