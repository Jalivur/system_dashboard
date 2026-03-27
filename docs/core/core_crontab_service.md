# `core.crontab_service`

> **Ruta**: `core/crontab_service.py`

Servicio de gestión de crontab.
Encapsula la lectura, escritura y parseo del crontab del sistema.

## Imports

```python
import subprocess
from utils.logger import get_logger
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `get_logger(__name__)` |
| `CRON_DESCRIPTIONS` | `{'* * * * *': 'Cada minuto', '*/5 * * * *': 'Cada 5 minutos', '*/10 * * * *': 'C...` |
| `QUICK_SCHEDULES` | `[('Cada minuto', '*', '*', '*', '*', '*'), ('Cada hora', '0', '*', '*', '*', '*'...` |

## Funciones

### `describe_cron(minute: str, hour: str, day: str, month: str, weekday: str) -> str`

Convierte una expresión cron a texto legible en español.

### `read_crontab(user: str) -> list[str]`

Lee las líneas del crontab del usuario indicado.

Args:
    user: nombre de usuario ("root" usa sudo, cualquier otro usa crontab -l)

Returns:
    Lista de líneas raw del crontab, o [] si no hay crontab o hay error.

### `write_crontab(user: str, lines: list[str]) -> tuple[bool, str]`

Escribe las líneas dadas como el nuevo crontab del usuario.

Args:
    user:  nombre de usuario
    lines: lista de líneas a escribir (sin \n final en cada una)

Returns:
    (True, mensaje_ok) o (False, mensaje_error)

### `parse_line(line: str) -> dict | None`

Parsea una línea de crontab a un diccionario.

Returns:
    dict con claves: special, minute, hour, day, month, weekday, command, raw
    None si la línea es comentario, vacía o malformada.

### `parse_crontab(lines: list[str]) -> list[dict]`

Parsea una lista de líneas raw y devuelve solo las entradas válidas.

Returns:
    Lista de dicts (una por entrada válida, sin comentarios ni vacíos).

### `build_line(minute: str, hour: str, day: str, month: str, weekday: str, command: str) -> str`

Construye una línea de crontab a partir de sus campos.

Si minute empieza por '@' se genera una entrada especial (@reboot, etc.).
