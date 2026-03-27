# `config.themes`

> **Ruta**: `config/themes.py`

Sistema de temas personalizados

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

Obtiene un tema por su nombre

Args:
    theme_name: Nombre del tema

Returns:
    Diccionario con los colores del tema

### `get_available_themes() -> list`

Obtiene lista de temas disponibles

Returns:
    Lista de tuplas (id, nombre_descriptivo)

### `get_theme_colors(theme_name: str) -> dict`

Obtiene los colores de un tema

Args:
    theme_name: Nombre del tema

Returns:
    Diccionario de colores

### `get_theme_preview() -> str`

Genera un texto con preview de todos los temas

Returns:
    String con la lista de temas y sus colores principales

### `create_custom_theme(name: str, colors: dict) -> dict`

Crea un tema personalizado

Args:
    name: Nombre descriptivo del tema
    colors: Diccionario con los colores personalizados

Returns:
    Diccionario del tema creado

### `save_selected_theme(theme_name: str)`

Guarda el tema seleccionado en archivo

Args:
    theme_name: Nombre del tema a guardar

### `load_selected_theme() -> str`

Carga el tema seleccionado desde archivo

Returns:
    Nombre del tema seleccionado o DEFAULT_THEME
