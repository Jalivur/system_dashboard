# `ui.widgets.graphs`

> **Ruta**: `ui/widgets/graphs.py`

> **Cobertura de documentación**: 🟢 100% (9/9)

Widgets para gráficas y visualización

---

## Tabla de contenidos

**Funciones**
- [`update_graph_lines()`](#funcion-update_graph_lines)
- [`recolor_lines()`](#funcion-recolor_lines)

**Clase [`GraphWidget`](#clase-graphwidget)**
  - [`update()`](#updateself-data-listfloat-max_val-float-color-str-00ffff-none)
  - [`recolor()`](#recolorself-color-str-none)
  - [`pack()`](#packself-kwargs)
  - [`grid()`](#gridself-kwargs)

---

## Dependencias internas

- `config.settings`

## Imports

```python
import customtkinter as ctk
from typing import List
from config.settings import GRAPH_WIDTH, GRAPH_HEIGHT
```

## Funciones

### `update_graph_lines(canvas, lines: List, data: List[float], max_val: float) -> None`

Actualiza las líneas de una gráfica en un canvas de tkinter con nuevos datos.

Args:
    canvas: El canvas de tkinter donde se dibuja la gráfica.
    lines: Lista de IDs de líneas a actualizar.
    data: Lista de valores flotantes representando los datos a graficar.
    max_val: El valor máximo utilizado para escalar los datos.

Returns:
    None

Raises:
    Ninguna excepción específica.

### `recolor_lines(canvas, lines: List, color: str) -> None`

Cambia el color de las líneas especificadas en un canvas de tkinter.

Args:
    canvas: El canvas de tkinter donde se encuentran las líneas.
    lines: Lista de IDs de líneas a recolar.
    color: El nuevo color para las líneas.

Returns:
    None

Raises:
    Ninguna excepción específica.

## Clase `GraphWidget`

Widget para gráficas de línea.

Args:
    parent: Widget padre.
    width (int): Ancho del canvas. Por defecto None.
    height (int): Alto del canvas. Por defecto None.

Nota: Utiliza valores por defecto de ancho y alto si no se proporcionan.

### Atributos públicos

| Atributo | Valor inicial |
|----------|---------------|
| `width` | `width or GRAPH_WIDTH` |
| `height` | `height or GRAPH_HEIGHT` |
| `canvas` | `ctk.CTkCanvas(parent, width=self.width, height=self.height, bg='#111111', highlightthickness=0)` |
| `lines` | `[]` |

### Métodos públicos

#### `update(self, data: List[float], max_val: float, color: str = '#00ffff') -> None`

Actualiza la gráfica con nuevos datos.

Args:
    data (List[float]): Lista de valores a graficar.
    max_val (float): Valor máximo para normalización.
    color (str, opcional): Color de las líneas. Por defecto '#00ffff'.

Returns:
    None

Raises:
    Ninguna excepción relevante.

#### `recolor(self, color: str) -> None`

Cambia el color de todas las líneas del gráfico.

Args:
    color (str): Nuevo color para las líneas.

Returns:
    None

Raises:
    None

#### `pack(self, **kwargs)`

Coloca el canvas en la ventana y ajusta su tamaño según sea necesario.

Args:
    **kwargs: Argumentos adicionales para el método pack del widget.

Returns:
    None

Raises:
    Ninguna excepción específica.

#### `grid(self, **kwargs)`

Configura la rejilla del lienzo del widget gráfico.

Args:
    **kwargs: Parámetros adicionales para configurar la rejilla.

Returns:
    None

Raises:
    Ninguna excepción específica.

<details>
<summary>Métodos privados</summary>

#### `__init__(self, parent, width: int = None, height: int = None)`

Inicializa el widget de gráfica con un lienzo personalizable.

Args:
    parent: El widget padre que contendrá la gráfica.
    width: El ancho del lienzo en píxeles. Por defecto, None.
    height: El alto del lienzo en píxeles. Por defecto, None.

Returns:
    None

Raises:
    None

#### `_create_lines(self) -> None`

Crea las líneas en el canvas.

Args:
    Ninguno

Returns:
    Ninguno

Raises:
    Ninguno

</details>
