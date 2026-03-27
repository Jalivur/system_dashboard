# `ui.widgets.graphs`

> **Ruta**: `ui/widgets/graphs.py`

Widgets para gráficas y visualización

## Imports

```python
import customtkinter as ctk
from typing import List
from config.settings import GRAPH_WIDTH, GRAPH_HEIGHT
```

## Funciones

### `update_graph_lines(canvas, lines: List, data: List[float], max_val: float) -> None`

Actualiza líneas de gráfica (función legacy para compatibilidad)

Args:
    canvas: Canvas de tkinter
    lines: Lista de IDs de líneas
    data: Datos a graficar
    max_val: Valor máximo

### `recolor_lines(canvas, lines: List, color: str) -> None`

Cambia el color de las líneas (función legacy)

Args:
    canvas: Canvas de tkinter
    lines: Lista de IDs de líneas
    color: Nuevo color

## Clase `GraphWidget`

Widget para gráficas de línea

### Atributos públicos

| Atributo | Valor inicial |
|----------|---------------|
| `width` | `width or GRAPH_WIDTH` |
| `height` | `height or GRAPH_HEIGHT` |
| `canvas` | `ctk.CTkCanvas(parent, width=self.width, height=self.height, bg='#111111', highlightthickness=0)` |
| `lines` | `[]` |

### Métodos públicos

#### `update(self, data: List[float], max_val: float, color: str = '#00ffff') -> None`

Actualiza la gráfica con nuevos datos

Args:
    data: Lista de valores a graficar
    max_val: Valor máximo para normalización
    color: Color de las líneas

#### `recolor(self, color: str) -> None`

Cambia el color de todas las líneas

Args:
    color: Nuevo color

#### `pack(self, **kwargs)`

Pack del canvas

#### `grid(self, **kwargs)`

Grid del canvas

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, width: int = None, height: int = None)`

Inicializa el widget de gráfica

Args:
    parent: Widget padre
    width: Ancho del canvas
    height: Alto del canvas

#### `_create_lines(self) -> None`

Crea las líneas en el canvas

</details>
