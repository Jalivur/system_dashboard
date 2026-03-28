# `config.themes`

> **Ruta**: `config/themes.py`

> **Cobertura de documentación**: 🟢 100% (7/7)

Sistema de temas personalizados

---

## Tabla de contenidos

**Funciones**
- [`get_theme()`](#funcion-get_theme)
- [`get_available_themes()`](#funcion-get_available_themes)
- [`get_theme_colors()`](#funcion-get_theme_colors)
- [`get_theme_preview()`](#funcion-get_theme_preview)
- [`create_custom_theme()`](#funcion-create_custom_theme)
- [`save_selected_theme()`](#funcion-save_selected_theme)
- [`load_selected_theme()`](#funcion-load_selected_theme)

---

## Imports

```python
import json
import os
from pathlib import Path
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `THEMES` | `{'cyberpunk': {'name': 'Cyberpunk (Original)', 'colors': {'primary': '#00ffff', ...` |
| `DEFAULT_THEME` | `'cyberpunk'` |
| `THEME_CONFIG_FILE` | `Path(__file__).parent.parent / 'data' / 'theme_config.json'` |

## Funciones

### `get_theme(theme_name: str) -> dict`

Recuperación de un tema mediante su nombre.

Args:
    theme_name (str): Nombre del tema a recuperar.

Returns:
    dict: Diccionario con los colores asociados al tema.

Raises:
    KeyError: Si el tema por defecto no está configurado.

### `get_available_themes() -> list`

Obtiene una lista de temas disponibles.

Returns:
    list: Lista de tuplas que contienen el identificador y el nombre descriptivo de cada tema.

### `get_theme_colors(theme_name: str) -> dict`

Recupera los colores asociados a un tema específico.

Args:
    theme_name (str): Nombre del tema del que obtener los colores.

Returns:
    dict: Diccionario que contiene los colores del tema.

Raises:
    Exception: Si el tema no existe o no tiene colores definidos.

### `get_theme_preview() -> str`

Obtiene una vista previa en texto de todos los temas disponibles.

Returns:
    str: Cadena con la lista de temas y sus colores principales.

Raises:
    None

### `create_custom_theme(name: str, colors: dict) -> dict`

Crea un tema personalizado con un nombre descriptivo y colores específicos.

Args:
    name (str): Nombre descriptivo del tema.
    colors (dict): Diccionario con los colores personalizados.

Returns:
    dict: Diccionario del tema creado.

Raises:
    ValueError: Si falta algún color requerido en el tema personalizado.

### `save_selected_theme(theme_name: str)`

Guarda el tema seleccionado en un archivo de configuración.

Args:
    theme_name (str): Nombre del tema a guardar.

Returns:
    None

Raises:
    None

### `load_selected_theme() -> str`

Carga el tema seleccionado desde archivo de configuración.

Args:
    Ninguno

Returns:
    str: Nombre del tema seleccionado o el tema predeterminado.

Raises:
    Ninguna excepción relevante, se maneja internamente.
