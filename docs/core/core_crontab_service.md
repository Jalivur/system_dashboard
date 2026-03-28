# `core.crontab_service`

> **Ruta**: `core/crontab_service.py`

> **Cobertura de documentación**: 🟢 100% (6/6)

Servicio de gestión de crontab.
Encapsula la lectura, escritura y parseo del crontab del sistema.

---

## Tabla de contenidos

**Funciones**
- [`describe_cron()`](#funcion-describe_cron)
- [`read_crontab()`](#funcion-read_crontab)
- [`write_crontab()`](#funcion-write_crontab)
- [`parse_line()`](#funcion-parse_line)
- [`parse_crontab()`](#funcion-parse_crontab)
- [`build_line()`](#funcion-build_line)

---

## Dependencias internas

- `utils.logger`

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

Args:
    minute (str): Minuto de la expresión cron.
    hour (str): Hora de la expresión cron.
    day (str): Día del mes de la expresión cron.
    month (str): Mes de la expresión cron.
    weekday (str): Día de la semana de la expresión cron.

Returns:
    str: Descripción legible de la expresión cron.

Raises:
    Ninguna excepción relevante.

### `read_crontab(user: str) -> list[str]`

Lee las líneas del crontab del usuario indicado.

Args:
    user: nombre de usuario. Utiliza "root" para leer el crontab de root mediante sudo.

Returns:
    Lista de líneas raw del crontab. Si no hay crontab o hay error, devuelve una lista vacía.

Raises:
    Exception: si ocurre un error al leer el crontab.

### `write_crontab(user: str, lines: list[str]) -> tuple[bool, str]`

Escribe las líneas dadas como el nuevo crontab del usuario especificado.

Args:
    user: nombre de usuario cuyo crontab se actualizará
    lines: lista de líneas a escribir en el crontab

Returns:
    Tupla con un booleano indicando éxito y un mensaje descriptivo

Raises:
    Excepción en caso de error al escribir el crontab

### `parse_line(line: str) -> dict | None`

Parsea una línea de crontab a un diccionario.

Args:
    line (str): La línea de crontab a parsear.

Returns:
    dict | None: Un diccionario con la información de la línea de crontab o None si la línea es inválida.

Raises:
    No se lanzan excepciones explícitas, pero puede retornar None si la línea es vacía, comentario o malformada.

### `parse_crontab(lines: list[str]) -> list[dict]`

Parsea una lista de líneas crontab y devuelve las entradas válidas.

Args:
    lines: Lista de líneas crontab en formato raw.

Returns:
    Lista de dicts, cada uno representando una entrada crontab válida.

Raises:
    None

### `build_line(minute: str, hour: str, day: str, month: str, weekday: str, command: str) -> str`

Construye una línea de crontab a partir de sus campos.

Args:
    minute (str): Minuto de la línea de crontab.
    hour (str): Hora de la línea de crontab.
    day (str): Día del mes de la línea de crontab.
    month (str): Mes de la línea de crontab.
    weekday (str): Día de la semana de la línea de crontab.
    command (str): Comando a ejecutar.

Returns:
    str: La línea de crontab construida.
