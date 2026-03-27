# `core.alert_service`

> **Ruta**: `core/alert_service.py`

Servicio de alertas externas por Telegram.
Sin dependencias nuevas — usa urllib de la stdlib.

Lógica anti-spam: cada alerta debe mantenerse activa durante
ALERT_SUSTAIN_S segundos antes de enviarse, y no se repite
hasta que baje del umbral y vuelva a subir (edge-trigger).

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

Lee TOKEN y CHAT_ID desde .env / os.environ.

</details>

## Clase `AlertService`

Servicio background que monitoriza métricas y envía alertas a Telegram.

Instanciar en main.py y pasar system_monitor / service_monitor.
Llamar a start() y stop() igual que el resto de servicios.

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

Inicia el thread daemon de monitoreo alertas.

Pollea cada CHECK_INTERVAL segs métricas/servicios.

#### `stop(self) -> None`

Detiene el thread de alertas limpiamente.

Join timeout 5s, log.

#### `is_running(self) -> bool`

Estado activo del servicio.

#### `get_history(self) -> list`

Historial alertas enviadas desde JSON data/alert_history.json.

Returns:
    list[dict]: Entradas ts/key/level/value/unit/message, reciente último.

#### `clear_history(self) -> None`

Borra el historial de alertas.

#### `send_test(self) -> bool`

Envía un mensaje de prueba. Útil para verificar la configuración.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, system_monitor, service_monitor)`

Inicializa AlertService con monitors.

Args:
    system_monitor: Para métricas CPU/TEMP/RAM/DISK.
    service_monitor: Para servicios FAILED.

#### `_loop(self) -> None`

Bucle principal thread daemon.

Check métricas/servicios cada CHECK_INTERVAL s.

#### `_check_metrics(self) -> None`

Chequea TEMP/CPU/RAM/DISK vs THRESHOLDS, trigger si warn/crit.

#### `_check_services(self) -> None`

Chequea servicios FAILED, trigger si >0.

#### `_trigger(self, key: str, message: str, value: float = 0.0, unit: str = '', level: str = '') -> None`

Activa una alerta con retardo anti-spam.
Solo envía si la condición lleva ALERT_SUSTAIN_S segundos activa
y no se ha enviado ya para este 'flanco'.

#### `_reset(self, key: str) -> None`

Resetea el estado de una alerta (condición resuelta).

#### `_save_to_history(self, key: str, message: str, value: float, unit: str, level: str) -> None`

Guarda la alerta disparada en el historial JSON (máx. MAX_HISTORY_ENTRIES).

#### `_send(self, text: str) -> bool`

Envía un mensaje Markdown a Telegram. Devuelve True si tiene éxito.

</details>
