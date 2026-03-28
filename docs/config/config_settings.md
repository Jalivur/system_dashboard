# `config.settings`

> **Ruta**: `config/settings.py`

> **Cobertura de documentación**: 🟢 100% (2/2)

Configuración centralizada del sistema de monitoreo

---

## Tabla de contenidos

**Clase [`Icons`](#clase-icons)**

**Clase [`UI`](#clase-ui)**

---

## Dependencias internas

- `config.local_settings`
- `config.themes`

## Imports

```python
from pathlib import Path
from config.themes import load_selected_theme, get_theme_colors
from config.local_settings import *
```

## Constantes / Variables de módulo

| Nombre | Valor |
|--------|-------|
| `PROJECT_ROOT` | `Path(__file__).parent.parent` |
| `DATA_DIR` | `PROJECT_ROOT / 'data'` |
| `SCRIPTS_DIR` | `PROJECT_ROOT / 'scripts'` |
| `EXPORTS_DIR` | `DATA_DIR / 'exports'` |
| `EXPORTS_CSV_DIR` | `EXPORTS_DIR / 'csv'` |
| `EXPORTS_LOG_DIR` | `EXPORTS_DIR / 'logs'` |
| `EXPORTS_SCR_DIR` | `EXPORTS_DIR / 'screenshots'` |
| `STATE_FILE` | `DATA_DIR / 'fan_state.json'` |
| `CURVE_FILE` | `DATA_DIR / 'fan_curve.json'` |
| `DSI_WIDTH` | `800` |
| `DSI_HEIGHT` | `480` |
| `DSI_X` | `1124` |
| `DSI_Y` | `1080` |
| `UPDATE_MS` | `2000` |
| `HISTORY` | `60` |
| `GRAPH_WIDTH` | `800` |
| `GRAPH_HEIGHT` | `20` |
| `CPU_WARN` | `60` |
| `CPU_CRIT` | `85` |
| `TEMP_WARN` | `60` |
| `TEMP_CRIT` | `75` |
| `RAM_WARN` | `65` |
| `RAM_CRIT` | `85` |
| `NET_WARN` | `2.0` |
| `NET_CRIT` | `6.0` |
| `SERVICE_WATCHDOG_CRITICAL` | `[]` |
| `SERVICE_WATCHDOG_INTERVAL` | `60` |
| `SERVICE_WATCHDOG_THRESHOLD` | `3` |
| `NET_INTERFACE` | `None` |
| `NET_MAX_MB` | `10.0` |

## Clase `Icons`

Iconos Nerd Font y emoji usados en la UI, definidos como escape Unicode.

Args: Ninguno

Returns: Ninguno

Raises: Ninguno

Nota: Clase que almacena iconos como literales Unicode para evitar corrupción al editar.
      Todos los literales de icono deben vivir en esta clase.

## Clase `UI`

Configuración visual del menú principal.

Args:
    Ninguno

Attributes:
    MENU_COLUMNS (int): Número de columnas del grid de botones.
    MENU_TABS (list): Definición de pestañas, cada una contiene clave, icono, label y lista de claves de etiquetas de botones.

Returns:
    Ninguno

Raises:
    Ninguno
