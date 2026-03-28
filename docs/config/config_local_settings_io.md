# `config.local_settings_io`

> **Ruta**: `config/local_settings_io.py`

> **Cobertura de documentación**: 🟢 100% (7/7)

config/local_settings_io.py

Lectura y escritura de config/local_settings.py de forma segura y sin
conflictos entre módulos que necesitan persistir claves distintas.

Formato del fichero:
  - Sección "# ── Parámetros" — variables sueltas (DSI_X, CPU_WARN, WEATHER_*)
  - Sección "# ── Iconos"     — asignaciones Icons.ATTR = "\Uxxxxxxxx"

Cualquier módulo que necesite leer o escribir local_settings.py debe
importar este módulo y usar read() / write_params() / write_icons().
Nunca escribir directamente el fichero desde fuera de este módulo.

---

## Tabla de contenidos

**Funciones**
- [`read()`](#funcion-read)
- [`write()`](#funcion-write)
- [`update_params()`](#funcion-update_params)
- [`write_params()`](#funcion-write_params)
- [`write_icons()`](#funcion-write_icons)
- [`update_icons()`](#funcion-update_icons)
- [`get_param()`](#funcion-get_param)

---

## Imports

```python
import os
import re
import logging
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `logger` | `logging.getLogger(__name__)` |

## Funciones

### `read() -> tuple`

Lee el contenido de local_settings.py y devuelve los parámetros y overrides de iconos.

Args:
    Ninguno

Returns:
    tuple: (param_overrides, icon_overrides) donde param_overrides es un diccionario de variables sueltas y icon_overrides es un diccionario de overrides de iconos.

Raises:
    Ninguno

### `write(param_overrides: dict, icon_overrides: dict) -> None`

Escribe el contenido completo de local_settings.py con parámetros e iconos sobrescritos.

Args:
    param_overrides (dict): Diccionario de parámetros a sobrescribir.
    icon_overrides (dict): Diccionario de iconos a sobrescribir.

Returns:
    None

Raises:
    Ninguna excepción específica.

### `update_params(new_params: dict) -> None`

Actualiza los parámetros existentes con nuevos valores de manera segura.

Args:
    new_params: Diccionario con los nuevos parámetros a aplicar.

Returns:
    None

Raises:
    None

### `write_params(param_overrides: dict) -> None`

Sobreescribe parámetros en un archivo preservando los iconos existentes.

Args:
    param_overrides: Diccionario con parámetros a sobreescribir.

Returns:
    None

Raises:
    None

### `write_icons(icon_overrides: dict) -> None`

Sobreescribe los iconos de los parámetros existentes con los valores proporcionados.

Args:
    icon_overrides (dict): Diccionario con los iconos a sobreescribir.

Returns:
    None

Raises:
    None

### `update_icons(new_icons: dict) -> None`

Actualiza los iconos existentes con nuevos iconos proporcionados.

Args:
    new_icons: Un diccionario con los nuevos iconos que se van a agregar.

Returns:
    None

Raises:
    None

### `get_param(key: str, default = None)`

Recuperar el valor de un parámetro específico desde la configuración de local_settings.py.

Args:
    key (str): Clave del parámetro a recuperar.
    default: Valor predeterminado a retornar si el parámetro no existe.

Returns:
    Valor del parámetro si existe, o el valor predeterminado si no existe.
