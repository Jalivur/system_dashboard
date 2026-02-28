This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: ui/**
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
ui/
  widgets/
    __init__.py
    dialogs.py
    graphs.py
  windows/
    __init__.py
    alert_history.py
    camera_window.py
    disk.py
    display_window.py
    fan_control.py
    history.py
    homebridge.py
    launchers.py
    led_window.py
    log_viewer.py
    monitor.py
    network_local.py
    network.py
    overview.py
    pihole_window.py
    process_window.py
    service.py
    services_manager_window.py
    theme_selector.py
    update.py
    usb.py
    vpn_window.py
  __init__.py
  main_window.py
  styles.py
```

# Files

## File: ui/widgets/graphs.py
```python
"""
Widgets para gráficas y visualización
"""
import customtkinter as ctk
from typing import List
from config.settings import GRAPH_WIDTH, GRAPH_HEIGHT


class GraphWidget:
    """Widget para gráficas de línea"""
    
    def __init__(self, parent, width: int = None, height: int = None):
        """
        Inicializa el widget de gráfica
        
        Args:
            parent: Widget padre
            width: Ancho del canvas
            height: Alto del canvas
        """
        self.width = width or GRAPH_WIDTH
        self.height = height or GRAPH_HEIGHT
        
        self.canvas = ctk.CTkCanvas(
            parent, 
            width=self.width, 
            height=self.height,
            bg="#111111", 
            highlightthickness=0
        )
        
        self.lines = []
        self._create_lines()
    
    def _create_lines(self) -> None:
        """Crea las líneas en el canvas"""
        self.lines = [
            self.canvas.create_line(0, 0, 0, 0, fill="#00ffff", width=2)
            for _ in range(self.width)
        ]
    
    def update(self, data: List[float], max_val: float, color: str = "#00ffff") -> None:
        """
        Actualiza la gráfica con nuevos datos
        
        Args:
            data: Lista de valores a graficar
            max_val: Valor máximo para normalización
            color: Color de las líneas
        """
        if not data or max_val <= 0:
            return
        
        n = len(data)
        if n < 2:
            return
        
        # Calcular puntos
        x_step = self.width / max(n - 1, 1)
        
        for i in range(min(n - 1, len(self.lines))):
            val1 = max(0, min(max_val, data[i]))
            val2 = max(0, min(max_val, data[i + 1]))
            
            y1 = self.height - (val1 / max_val) * self.height
            y2 = self.height - (val2 / max_val) * self.height
            
            x1 = i * x_step
            x2 = (i + 1) * x_step
            
            self.canvas.coords(self.lines[i], x1, y1, x2, y2)
            self.canvas.itemconfig(self.lines[i], fill=color)
    
    def recolor(self, color: str) -> None:
        """
        Cambia el color de todas las líneas
        
        Args:
            color: Nuevo color
        """
        for line in self.lines:
            self.canvas.itemconfig(line, fill=color)
    
    def pack(self, **kwargs):
        """Pack del canvas"""
        self.canvas.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid del canvas"""
        self.canvas.grid(**kwargs)


def update_graph_lines(canvas, lines: List, data: List[float], max_val: float) -> None:
    """
    Actualiza líneas de gráfica (función legacy para compatibilidad)
    
    Args:
        canvas: Canvas de tkinter
        lines: Lista de IDs de líneas
        data: Datos a graficar
        max_val: Valor máximo
    """
    if not data or max_val <= 0:
        return
    
    n = len(data)
    if n < 2:
        return
    
    width = canvas.winfo_width() or GRAPH_WIDTH
    height = canvas.winfo_height() or GRAPH_HEIGHT
    
    x_step = width / max(n - 1, 1)
    
    for i in range(min(n - 1, len(lines))):
        val1 = max(0, min(max_val, data[i]))
        val2 = max(0, min(max_val, data[i + 1]))
        
        y1 = height - (val1 / max_val) * height
        y2 = height - (val2 / max_val) * height
        
        x1 = i * x_step
        x2 = (i + 1) * x_step
        
        canvas.coords(lines[i], x1, y1, x2, y2)


def recolor_lines(canvas, lines: List, color: str) -> None:
    """
    Cambia el color de las líneas (función legacy)
    
    Args:
        canvas: Canvas de tkinter
        lines: Lista de IDs de líneas
        color: Nuevo color
    """
    for line in lines:
        canvas.itemconfig(line, fill=color)
```

## File: ui/windows/services_manager_window.py
```python
"""
Ventana de control manual de servicios del Dashboard.
Permite parar y arrancar cada servicio background de forma independiente.
"""
import threading
import tkinter as tk
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES,
                              DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import confirm_dialog
from utils.logger import get_logger

logger = get_logger(__name__)

# Intervalo de refresco de estados (ms)
_REFRESH_MS = 1500


class ServicesManagerWindow(ctk.CTkToplevel):
    """
    Ventana de gestión manual de servicios background del Dashboard.

    Muestra el estado (activo/parado) de cada servicio y permite
    pararlo o arrancarlo con un botón por fila.

    Recibe todos los servicios como kwargs — los que no se pasen
    simplemente no aparecen en la lista.
    """

    def __init__(self, parent, **services):
        super().__init__(parent)
        self.title("Gestión de Servicios")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        # ── Definición ordenada de servicios ──────────────────────────────────
        # (clave, etiqueta visible, emoji, advertencia si se para)
        _DEFINITIONS = [
            ("fan_service",         "Fan Auto Service",       "🌀",
             "El ventilador pasará a modo manual."),
            ("system_monitor",      "System Monitor",         "🖥️",
             "CPU, RAM y temperatura dejarán de actualizarse."),
            ("hardware_monitor",    "Hardware Monitor",       "🌡️",
             "Temperatura chasis y fan duty dejarán de leerse."),
            ("service_monitor",     "Service Monitor",        "⚙️",
             "El estado de servicios systemd no se actualizará."),
            ("alert_service",       "Alert Service",          "📲",
             "Las alertas Telegram quedarán desactivadas."),
            ("audio_alert_service", "Audio Alert Service",    "🔊",
             "Las alertas de audio quedarán desactivadas."),
            ("homebridge_monitor",  "Homebridge Monitor",     "🏠",
             "Homebridge no se sondeará."),
            ("pihole_monitor",      "Pi-hole Monitor",        "🕳️",
             "Pi-hole no se sondeará."),
            ("vpn_monitor",         "VPN Monitor",            "🔒",
             "El estado de VPN no se actualizará."),
            ("data_service",        "Data Collection",        "📊",
             "No se guardarán datos en el histórico."),
            ("cleanup_service",     "Cleanup Service",        "🧹",
             "La limpieza automática de archivos se pausará."),
            ("display_service",     "Display Service",        "💡",
             "El control de brillo quedará desactivado."),
            ("led_service",         "LED Service",            "💡",
             "Los LEDs RGB dejarán de controlarse."),
        ]

        # Solo mostrar los servicios que se han pasado
        self._services = {}   # clave → objeto servicio
        self._defs = []       # definiciones filtradas
        for key, label, emoji, warn in _DEFINITIONS:
            if key in services and services[key] is not None:
                self._services[key] = services[key]
                self._defs.append((key, label, emoji, warn))

        # Widgets por servicio: {key: {"indicator": canvas, "oval": id, "btn": CTkButton, "lbl_status": label}}
        self._rows: dict = {}
        self._busy: set = set()   # claves con operación en curso

        self._create_ui()
        self._refresh_loop()
        logger.info("[ServicesManagerWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="GESTIÓN DE SERVICIOS", on_close=self.destroy)

        # Scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw",
                             width=DSI_WIDTH - 50)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Cabecera de columnas
        hdr = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        hdr.pack(fill="x", padx=8, pady=(6, 2))
        hdr.grid_columnconfigure(0, minsize=14)   # indicador
        hdr.grid_columnconfigure(1, weight=1)      # nombre
        hdr.grid_columnconfigure(2, minsize=80)    # estado
        hdr.grid_columnconfigure(3, minsize=110)   # botón

        for col, text in enumerate(["", "Servicio", "Estado", ""]):
            ctk.CTkLabel(
                hdr, text=text,
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                text_color=COLORS['text_dim'],
            ).grid(row=0, column=col, padx=(10, 4), pady=6, sticky="w")

        # Filas de servicios
        for key, label, emoji, warn in self._defs:
            self._create_row(inner, key, label, emoji, warn)

    def _create_row(self, parent, key: str, label: str, emoji: str, warn: str):
        """Crea una fila para un servicio."""

        row_frame = ctk.CTkFrame(
            parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        row_frame.pack(fill="x", padx=8, pady=3)
        row_frame.grid_columnconfigure(1, weight=1)

        # ── Indicador circular de estado ──
        INDICATOR = 14
        indicator_canvas = tk.Canvas(
            row_frame, width=INDICATOR, height=INDICATOR,
            bg=COLORS['bg_dark'], highlightthickness=0, bd=0)
        indicator_canvas.grid(row=0, column=0, padx=(12, 6), pady=12)
        oval = indicator_canvas.create_oval(
            1, 1, INDICATOR - 1, INDICATOR - 1,
            fill=COLORS['text_dim'], outline="")

        # ── Nombre del servicio ──
        ctk.CTkLabel(
            row_frame,
            text=f"{emoji}  {label}",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['text'],
            anchor="w",
        ).grid(row=0, column=1, padx=(4, 8), pady=12, sticky="w")

        # ── Etiqueta de estado ──
        lbl_status = ctk.CTkLabel(
            row_frame,
            text="…",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['text_dim'],
            width=80, anchor="center",
        )
        lbl_status.grid(row=0, column=2, padx=4, pady=12)

        # ── Botón parar/arrancar ──
        btn = make_futuristic_button(
            row_frame,
            text="",
            command=lambda k=key, w=warn: self._toggle(k, w),
            width=12, height=7, font_size=13,
        )
        btn.grid(row=0, column=3, padx=(4, 12), pady=8)

        self._rows[key] = {
            "canvas":     indicator_canvas,
            "oval":       oval,
            "lbl_status": lbl_status,
            "btn":        btn,
        }

    # ── Lógica de estado ──────────────────────────────────────────────────────

    def _is_running(self, key: str) -> bool:
        """Lee el estado del servicio de forma segura."""
        svc = self._services.get(key)
        if svc is None:
            return False
        # display_service no tiene _running — siempre activo si existe
        if key == "display_service":
            return True
        if hasattr(svc, "is_running"):
            return svc.is_running()
        return getattr(svc, "_running", False)

    def _update_row(self, key: str):
        """Actualiza indicador, etiqueta y botón de una fila."""
        if key not in self._rows:
            return
        row = self._rows[key]
        busy = key in self._busy

        if busy:
            row["lbl_status"].configure(text="…", text_color=COLORS['text_dim'])
            row["canvas"].itemconfigure(row["oval"], fill=COLORS['text_dim'])
            row["btn"].configure(state="disabled", text="…")
            return

        running = self._is_running(key)

        # Indicador
        color = COLORS['primary'] if running else COLORS['danger']
        row["canvas"].itemconfigure(row["oval"], fill=color)

        # Etiqueta
        row["lbl_status"].configure(
            text="ACTIVO" if running else "PARADO",
            text_color=COLORS['primary'] if running else COLORS['danger'],
        )

        # Botón
        row["btn"].configure(
            state="normal",
            text="⏹ Parar" if running else "▶ Iniciar",
            fg_color=COLORS['danger'] if running else COLORS['primary'],
        )

        # display_service: no se puede parar desde aquí (solo se gestiona brillo)
        if key == "display_service":
            row["btn"].configure(state="disabled", text="—")

    def _refresh_loop(self):
        """Refresca todos los estados periódicamente."""
        if not self.winfo_exists():
            return
        for key in self._rows:
            self._update_row(key)
        self.after(_REFRESH_MS, self._refresh_loop)

    # ── Toggle parar / arrancar ───────────────────────────────────────────────

    def _toggle(self, key: str, warn: str):
        """Pide confirmación y ejecuta start/stop en un thread."""
        if key in self._busy:
            return

        svc = self._services.get(key)
        if svc is None:
            return

        running = self._is_running(key)
        action = "parar" if running else "arrancar"

        # Confirmación
        msg = f"¿Seguro que quieres {action} {key}?"
        if running and warn:
            msg += f"\n\n⚠️  {warn}"


        confirm_dialog(
            parent=self,
            text=msg,
            on_confirm=lambda: self._execute_toggle(key, running),
        )

    def _execute_toggle(self, key: str, was_running: bool):
        """Ejecuta stop/start en un thread para no bloquear la UI."""
        self._busy.add(key)
        self._update_row(key)

        def _run():
            svc = self._services[key]
            try:
                if was_running:
                    logger.info("[ServicesManagerWindow] Parando: %s", key)
                    svc.stop()
                else:
                    logger.info("[ServicesManagerWindow] Arrancando: %s", key)
                    svc.start()
            except Exception as e:
                logger.error("[ServicesManagerWindow] Error toggling %s: %s", key, e)
            finally:
                self._busy.discard(key)
                # Actualizar UI desde el hilo principal
                if self.winfo_exists():
                    self.after(0, self._update_row, key)

        threading.Thread(target=_run, daemon=True,
                         name=f"SvcToggle-{key}").start()
```

## File: ui/__init__.py
```python

```

## File: ui/widgets/__init__.py
```python
"""
Paquete de widgets personalizados
"""
from .graphs import GraphWidget, update_graph_lines, recolor_lines
from .dialogs import custom_msgbox, confirm_dialog, terminal_dialog

__all__ = ['GraphWidget', 'update_graph_lines', 'recolor_lines', 
           'custom_msgbox', 'confirm_dialog', 'terminal_dialog']
```

## File: ui/windows/alert_history.py
```python
"""
Ventana de historial de alertas disparadas por AlertService.
Lee data/alert_history.json y muestra las entradas con colores por nivel.
"""
import customtkinter as ctk
from datetime import datetime
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from ui.styles import make_window_header, make_futuristic_button, StyleManager
from ui.widgets import confirm_dialog
from utils.logger import get_logger

logger = get_logger(__name__)

# Colores por nivel (misma paleta que LogViewer)
LEVEL_COLORS = {
    "warn": "#FFA500",
    "crit": "#FF4444",
}

# Etiqueta legible por clave
KEY_LABELS = {
    "temp_warn":      "🌡️ Temperatura — aviso",
    "temp_crit":      "🌡️ Temperatura — crítico",
    "cpu_warn":       "🔥 CPU — aviso",
    "cpu_crit":       "🔥 CPU — crítico",
    "ram_warn":       "💾 RAM — aviso",
    "ram_crit":       "💾 RAM — crítico",
    "disk_warn":      "💿 Disco — aviso",
    "disk_crit":      "💿 Disco — crítico",
    "services_failed": "⚠️ Servicios caídos",
}


class AlertHistoryWindow(ctk.CTkToplevel):
    """Ventana de historial de alertas."""

    def __init__(self, parent, alert_service):
        super().__init__(parent)
        self.alert_service = alert_service

        self.title("Historial de Alertas")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._create_ui()
        self._load()
        logger.info("[AlertHistoryWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="HISTORIAL DE ALERTAS", on_close=self.destroy)

        # Área scrollable
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        self._list_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window(
            (0, 0), window=self._list_frame, anchor="nw", width=DSI_WIDTH - 50)
        self._list_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Barra inferior
        bar = ctk.CTkFrame(main, fg_color="transparent")
        bar.pack(fill="x", padx=5, pady=(0, 4))

        self._count_label = ctk.CTkLabel(
            bar, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'])
        self._count_label.pack(side="left", padx=8)

        make_futuristic_button(
            bar, text="↺ Actualizar", command=self._load,
            width=11, height=5, font_size=14
        ).pack(side="right", padx=4)

        make_futuristic_button(
            bar, text="🗑 Borrar todo", command=self._confirm_clear,
            width=12, height=5, font_size=14
        ).pack(side="right", padx=4)

    # ── Carga ─────────────────────────────────────────────────────────────────

    def _load(self):
        """Lee el historial y redibuja la lista."""
        for w in self._list_frame.winfo_children():
            w.destroy()

        history = self.alert_service.get_history()

        if not history:
            ctk.CTkLabel(
                self._list_frame,
                text="No hay alertas registradas.",
                text_color=COLORS['text_dim'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
            ).pack(pady=40)
            self._count_label.configure(text="0 alertas")
            return

        # Mostrar en orden inverso (más reciente primero)
        for entry in reversed(history):
            self._create_entry_card(entry)

        total = len(history)
        self._count_label.configure(text=f"{total} alerta{'s' if total != 1 else ''}")

    def _create_entry_card(self, entry: dict):
        """Crea una tarjeta para una entrada del historial."""
        level  = entry.get("level", "warn")
        key    = entry.get("key", "")
        color  = LEVEL_COLORS.get(level, COLORS['text'])
        label  = KEY_LABELS.get(key, key)
        value  = entry.get("value", 0)
        unit   = entry.get("unit", "")
        ts_str = entry.get("ts", "")

        card = ctk.CTkFrame(
            self._list_frame,
            fg_color=COLORS['bg_dark'],
            corner_radius=6,
        )
        card.pack(fill="x", padx=6, pady=3)

        # Franja de color a la izquierda
        ctk.CTkFrame(card, fg_color=color, width=4, corner_radius=0).pack(
            side="left", fill="y", padx=(0, 8))

        # Contenido
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="x", expand=True, pady=6)

        # Fila superior: etiqueta + valor
        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top, text=label,
            text_color=color,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=f"{value}{unit}",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="e",
        ).pack(side="right", padx=12)

        # Fila inferior: timestamp
        ctk.CTkLabel(
            content, text=ts_str,
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="w",
        ).pack(fill="x")

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _confirm_clear(self):
        confirm_dialog(
            parent=self,
            text="¿Borrar todo el historial de alertas?\n\nEsta acción no se puede deshacer.",
            title="🗑 Borrar Historial",
            on_confirm=self._clear,
        )

    def _clear(self):
        self.alert_service.clear_history()
        self._load()
```

## File: ui/windows/led_window.py
```python
"""
Ventana de control de LEDs RGB del GPIO Board.
Hardware: Freenove FNK0100K — 4 LEDs RGB (I2C 0x21, gestionados por fase1.py).
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from ui.styles import make_window_header, make_futuristic_button
from core.led_service import LED_MODES, LED_MODE_LABELS
from utils.logger import get_logger

logger = get_logger(__name__)


class LedWindow(ctk.CTkToplevel):
    """Ventana de control de LEDs RGB."""

    def __init__(self, parent, led_service):
        super().__init__(parent)
        self.led_service = led_service

        self.title("Control LEDs")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._r = ctk.IntVar(value=0)
        self._g = ctk.IntVar(value=255)
        self._b = ctk.IntVar(value=0)
        self._mode_var = ctk.StringVar(value="auto")

        self._create_ui()
        self._load_current_state()
        logger.info("[LedWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="CONTROL LEDs RGB", on_close=self.destroy)

        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        from ui.styles import StyleManager
        sb = ctk.CTkScrollbar(scroll_container, orientation="vertical", command=canvas.yview, width=30)
        sb.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(sb)
        canvas.configure(yscrollcommand=sb.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # ── Selector de modo ──
        mode_card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        mode_card.pack(fill="x", padx=10, pady=(6, 4))

        ctk.CTkLabel(mode_card, text="Modo de los LEDs",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(anchor="w", padx=14, pady=(10, 6))

        btn_row = ctk.CTkFrame(mode_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(0, 10))

        # 3 botones por fila
        self._mode_btns = {}
        for i, mode in enumerate(LED_MODES):
            label = LED_MODE_LABELS[mode]
            btn = make_futuristic_button(
                btn_row, text=label,
                command=lambda m=mode: self._set_mode(m),
                width=14, height=8, font_size=13
            )
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=4, sticky="nsew")
            self._mode_btns[mode] = btn
        for c in range(3):
            btn_row.grid_columnconfigure(c, weight=1)

        # ── Color RGB ──
        color_card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        color_card.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(color_card, text="Color (para modos: fijo, secuencial, respiración)",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(anchor="w", padx=14, pady=(10, 4))

        for label, var, color_accent in [
            ("R", self._r, "#FF4444"),
            ("G", self._g, "#44FF44"),
            ("B", self._b, "#4488FF"),
        ]:
            row = ctk.CTkFrame(color_card, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=2)

            ctk.CTkLabel(row, text=label, width=20,
                         font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
                         text_color=color_accent).pack(side="left")

            ctk.CTkSlider(
                row, from_=0, to=255, variable=var,
                command=lambda v, lbl=label: self._on_color_change(),
                width=500, height=28,
                progress_color=color_accent,
                button_color=color_accent,
                button_hover_color=COLORS['secondary'],
            ).pack(side="left", padx=8)

            val_lbl = ctk.CTkLabel(row, text="---", width=40,
                                   font=(FONT_FAMILY, FONT_SIZES['small']),
                                   text_color=COLORS['text'])
            val_lbl.pack(side="left")
            setattr(self, f"_{label.lower()}_lbl", val_lbl)

        # ── Preview color ──
        preview_row = ctk.CTkFrame(color_card, fg_color="transparent")
        preview_row.pack(pady=(6, 10))

        ctk.CTkLabel(preview_row, text="Preview:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 10))

        import tkinter as tk
        self._preview_canvas = tk.Canvas(preview_row, width=60, height=30,
                                         bg="#000000", highlightthickness=1,
                                         highlightbackground=COLORS['border'])
        self._preview_canvas.pack(side="left")
        self._preview_rect = self._preview_canvas.create_rectangle(0, 0, 60, 30, fill="#00ff00")

        make_futuristic_button(
            preview_row, text="✓ Aplicar color",
            command=self._apply_color,
            width=16, height=8, font_size=14
        ).pack(side="left", padx=10)

        # ── Colores rápidos ──
        quick_card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        quick_card.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(quick_card, text="Colores rápidos",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(anchor="w", padx=14, pady=(10, 6))

        presets = [
            ("🔴 Rojo",    255, 0,   0),
            ("🟢 Verde",   0,   255, 0),
            ("🔵 Azul",    0,   0,   255),
            ("🟡 Amarillo",255, 200, 0),
            ("🟣 Violeta", 180, 0,   255),
            ("⚪ Blanco",  255, 255, 255),
        ]
        qrow = ctk.CTkFrame(quick_card, fg_color="transparent")
        qrow.pack(fill="x", padx=10, pady=(0, 10))
        for i, (lbl, r, g, b) in enumerate(presets):
            make_futuristic_button(
                qrow, text=lbl,
                command=lambda r=r, g=g, b=b: self._quick_color(r, g, b),
                width=12, height=7, font_size=12
            ).grid(row=i // 3, column=i % 3, padx=5, pady=3, sticky="nsew")
        for c in range(3):
            qrow.grid_columnconfigure(c, weight=1)

        # ── Estado actual ──
        self._status_label = ctk.CTkLabel(inner, text="",
                                           font=(FONT_FAMILY, FONT_SIZES['small']),
                                           text_color=COLORS['text_dim'])
        self._status_label.pack(pady=6)

        self._update_preview()

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _set_mode(self, mode: str):
        r, g, b = self._r.get(), self._g.get(), self._b.get()
        self.led_service.set_mode(mode, r, g, b)
        self._mode_var.set(mode)
        self._highlight_mode_btn(mode)
        self._update_status()

    def _on_color_change(self):
        self._update_preview()

    def _apply_color(self):
        r, g, b = self._r.get(), self._g.get(), self._b.get()
        mode = self._mode_var.get()
        if mode in ("auto", "rainbow", "off"):
            mode = "static"
            self._mode_var.set(mode)
        self.led_service.set_mode(mode, r, g, b)
        self._highlight_mode_btn(mode)
        self._update_status()

    def _quick_color(self, r: int, g: int, b: int):
        self._r.set(r)
        self._g.set(g)
        self._b.set(b)
        self._update_preview()
        self._apply_color()

    def _update_preview(self):
        r, g, b = self._r.get(), self._g.get(), self._b.get()
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        self._preview_canvas.itemconfigure(self._preview_rect, fill=hex_color)
        if hasattr(self, "_r_lbl"):
            self._r_lbl.configure(text=str(r))
            self._g_lbl.configure(text=str(g))
            self._b_lbl.configure(text=str(b))

    def _highlight_mode_btn(self, active_mode: str):
        for mode, btn in self._mode_btns.items():
            if mode == active_mode:
                btn.configure(fg_color=COLORS['primary'], border_width=2,
                              border_color=COLORS['secondary'])
            else:
                btn.configure(fg_color=COLORS['bg_dark'], border_width=1,
                              border_color=COLORS['border'])

    def _update_status(self):
        state = self.led_service.get_state()
        mode  = state.get("mode", "auto")
        label = LED_MODE_LABELS.get(mode, mode)
        r, g, b = state.get("r", 0), state.get("g", 255), state.get("b", 0)
        if mode in ("auto", "rainbow", "off"):
            self._status_label.configure(text=f"Modo activo: {label}")
        else:
            self._status_label.configure(
                text=f"Modo activo: {label}  •  RGB({r},{g},{b})"
            )

    def _load_current_state(self):
        state = self.led_service.get_state()
        mode  = state.get("mode", "auto")
        self._mode_var.set(mode)
        self._r.set(state.get("r", 0))
        self._g.set(state.get("g", 255))
        self._b.set(state.get("b", 0))
        self._highlight_mode_btn(mode)
        self._update_status()
        self._update_preview()
```

## File: ui/windows/network_local.py
```python
"""
Ventana de panel de red local.
Muestra los dispositivos encontrados por arp-scan con IP, MAC, fabricante y hostname.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
)
from ui.styles import make_window_header, make_futuristic_button, StyleManager
from core.network_scanner import NetworkScanner
from utils.logger import get_logger

logger = get_logger(__name__)

# Refresco automático cada N segundos (0 = desactivado)
AUTO_REFRESH_S = 60


class NetworkLocalWindow(ctk.CTkToplevel):
    """Panel de dispositivos en la red local."""

    def __init__(self, parent):
        super().__init__(parent)
        self._scanner     = NetworkScanner()
        self._auto_job    = None
        self._poll_job    = None

        self.title("Panel de Red Local")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._create_ui()
        # Lanzar primer escaneo automáticamente
        self._start_scan()
        logger.info("[NetworkLocalWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main,
            title="RED LOCAL",
            on_close=self._on_close,
            status_text="Escaneando...",
        )

        # Área scrollable para la lista de dispositivos
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        self._device_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window(
            (0, 0), window=self._device_frame,
            anchor="nw", width=DSI_WIDTH - 50)
        self._device_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Barra inferior
        bar = ctk.CTkFrame(main, fg_color="transparent")
        bar.pack(fill="x", padx=5, pady=(0, 4))

        self._count_label = ctk.CTkLabel(
            bar, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'])
        self._count_label.pack(side="left", padx=8)

        self._scan_btn = make_futuristic_button(
            bar, text="⟳  Escanear", command=self._start_scan,
            width=12, height=5, font_size=14)
        self._scan_btn.pack(side="right", padx=4)

    # ── Escaneo ───────────────────────────────────────────────────────────────

    def _start_scan(self):
        """Lanza el escaneo y activa el polling de resultado."""
        if self._scanner.get_status() == "scanning":
            return
        self._scan_btn.configure(state="disabled", text="Escaneando...")
        self._header.status_label.configure(text="Escaneando red...")
        self._scanner.scan()
        self._poll_result()

    def _poll_result(self):
        """Comprueba cada 500ms si el escaneo terminó."""
        status = self._scanner.get_status()
        if status == "scanning":
            self._poll_job = self.after(500, self._poll_result)
            return
        # Escaneo terminado
        self._render()
        # Programar refresco automático
        if AUTO_REFRESH_S > 0:
            self._auto_job = self.after(AUTO_REFRESH_S * 1000, self._start_scan)

    def _render(self):
        """Redibuja la lista con los dispositivos encontrados."""
        status  = self._scanner.get_status()
        devices = self._scanner.get_devices()

        # Limpiar lista anterior
        for w in self._device_frame.winfo_children():
            w.destroy()

        if status == "error":
            error_msg = self._scanner.get_error()
            ctk.CTkLabel(
                self._device_frame,
                text=f"⚠ Error en el escaneo:\n{error_msg}",
                text_color=COLORS['danger'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                wraplength=DSI_WIDTH - 80,
                justify="left",
            ).pack(pady=30, padx=20)
            self._header.status_label.configure(text="Error")
            self._count_label.configure(text="")

        elif not devices:
            ctk.CTkLabel(
                self._device_frame,
                text="No se encontraron dispositivos.",
                text_color=COLORS['text_dim'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
            ).pack(pady=40)
            self._header.status_label.configure(text="0 dispositivos")
            self._count_label.configure(text="0 dispositivos")

        else:
            for device in devices:
                self._create_device_row(device)
            n = len(devices)
            age = self._scanner.get_last_scan_age()
            age_str = f" · hace {int(age)}s" if age is not None else ""
            self._header.status_label.configure(text=f"{n} dispositivos{age_str}")
            self._count_label.configure(
                text=f"{n} dispositivo{'s' if n != 1 else ''} en la red")

        self._scan_btn.configure(state="normal", text="⟳  Escanear")

    def _create_device_row(self, device: dict):
        """Fila de un dispositivo: IP | hostname | MAC | fabricante."""
        row = ctk.CTkFrame(
            self._device_frame,
            fg_color=COLORS['bg_dark'],
            corner_radius=6,
        )
        row.pack(fill="x", padx=6, pady=2)

        # Columna izquierda: IP + hostname
        left = ctk.CTkFrame(row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=10, pady=6)

        ctk.CTkLabel(
            left,
            text=device["ip"],
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="w",
        ).pack(fill="x")

        if device["hostname"]:
            ctk.CTkLabel(
                left,
                text=device["hostname"],
                text_color=COLORS['text_dim'],
                font=(FONT_FAMILY, FONT_SIZES['small']),
                anchor="w",
            ).pack(fill="x")

        # Columna derecha: fabricante + MAC
        right = ctk.CTkFrame(row, fg_color="transparent")
        right.pack(side="right", padx=10, pady=6)

        ctk.CTkLabel(
            right,
            text=device["vendor"],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="e",
            wraplength=200,
        ).pack(anchor="e")

        ctk.CTkLabel(
            right,
            text=device["mac"],
            text_color=COLORS['text_dim'],
            font=("Courier New", 12),
            anchor="e",
        ).pack(anchor="e")

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _on_close(self):
        if self._auto_job:
            self.after_cancel(self._auto_job)
        if self._poll_job:
            self.after_cancel(self._poll_job)
        logger.info("[NetworkLocalWindow] Ventana cerrada")
        self.destroy()
```

## File: ui/windows/pihole_window.py
```python
"""
Ventana de estadísticas de Pi-hole.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
)
from ui.styles import make_window_header, make_futuristic_button
from core.pihole_monitor import PiholeMonitor
from utils.logger import get_logger

logger = get_logger(__name__)

UPDATE_MS = 5000   # refresco visual de la ventana


class PiholeWindow(ctk.CTkToplevel):
    """Ventana de estadísticas de Pi-hole."""

    def __init__(self, parent, pihole_monitor: PiholeMonitor):
        super().__init__(parent)
        self.pihole = pihole_monitor
        self._update_job = None

        self.title("Pi-hole")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._create_ui()
        self._schedule_update()
        logger.info("[PiholeWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main, title="PI-HOLE",
            on_close=self._on_close,
            status_text="Cargando...",
        )

        # Grid 2×2 de tarjetas métricas
        grid = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        grid.pack(fill="both", expand=True, padx=5, pady=5)
        grid.grid_columnconfigure(0, weight=1, uniform="col")
        grid.grid_columnconfigure(1, weight=1, uniform="col")

        # Tarjetas: (título, clave_interna, unidad, color)
        cards_config = [
            ("QUERIES HOY",       "queries_today",   "",   COLORS['primary']),
            ("BLOQUEADAS HOY",    "blocked_today",   "",   COLORS['danger']),
            ("% BLOQUEADO",       "percent_blocked", "%",  COLORS['warning']),
            ("DOMINIOS EN LISTA", "domains_blocked", "",   COLORS['success']),
            ("CLIENTES ÚNICOS",   "unique_clients",  "",   COLORS['secondary']),
            ("ESTADO",            "status",          "",   COLORS['primary']),
        ]

        self._value_labels = {}

        for i, (title, key, unit, color) in enumerate(cards_config):
            row, col = divmod(i, 2)
            card = ctk.CTkFrame(grid, fg_color=COLORS['bg_dark'], corner_radius=8)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            ctk.CTkLabel(
                card, text=title,
                text_color=COLORS['text_dim'],
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                anchor="w",
            ).pack(anchor="w", padx=10, pady=(8, 2))

            val_lbl = ctk.CTkLabel(
                card, text="—",
                text_color=color,
                font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold"),
                anchor="w",
            )
            val_lbl.pack(anchor="w", padx=10, pady=(0, 10))
            self._value_labels[key] = (val_lbl, unit, color)

        # Botón forzar refresco
        bottom = ctk.CTkFrame(main, fg_color="transparent")
        bottom.pack(fill="x", pady=6, padx=10)
        make_futuristic_button(
            bottom, text="⟳  Actualizar",
            command=self._force_refresh,
            width=13, height=5,
        ).pack(side="left")

    # ── Actualización ─────────────────────────────────────────────────────────

    def _schedule_update(self):
        self._update_job = self.after(100, self._render)

    def _force_refresh(self):
        """Pide al monitor que sondee de inmediato (en background)."""
        import threading
        threading.Thread(
            target=self.pihole._fetch,
            daemon=True, name="PiholeForceRefresh"
        ).start()
        self._header.status_label.configure(text="Actualizando...")
        # Releer tras 2s para dar tiempo al fetch
        self.after(2000, self._render)

    def _render(self):
        """Actualiza los valores en pantalla con la caché del monitor."""
        if not self.winfo_exists():
            return

        stats = self.pihole.get_stats()

        if not stats.get("reachable", False):
            self._header.status_label.configure(text="⚠ Sin conexión")
        else:
            status_str = "✅ Activo" if stats.get("status") == "enabled" else "⏸ Pausado"
            pct = stats.get("percent_blocked", 0.0)
            self._header.status_label.configure(
                text=f"{status_str}  ·  {pct:.1f}% bloqueado")

        for key, (lbl, unit, color) in self._value_labels.items():
            value = stats.get(key, "—")
            if key == "status":
                if not stats.get("reachable"):
                    text       = "Sin conexión"
                    text_color = COLORS['danger']
                elif value == "enabled":
                    text       = "✅ Activo"
                    text_color = COLORS['success']
                else:
                    text       = "⏸ Pausado"
                    text_color = COLORS['warning']
                lbl.configure(text=text, text_color=text_color)
            elif key == "percent_blocked":
                lbl.configure(text=f"{value:.1f}{unit}")
            else:
                lbl.configure(
                    text=f"{value:,}{unit}".replace(",", ".") if isinstance(value, int) else str(value)
                )

        self._update_job = self.after(UPDATE_MS, self._render)

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _on_close(self):
        if self._update_job:
            self.after_cancel(self._update_job)
        logger.info("[PiholeWindow] Ventana cerrada")
        self.destroy()
```

## File: ui/windows/vpn_window.py
```python
"""
Ventana de gestión de conexiones VPN.
Muestra el estado en tiempo real y permite conectar/desconectar
usando los scripts del usuario.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR
)
from ui.styles import make_window_header, make_futuristic_button
from ui.widgets.dialogs import terminal_dialog
from utils.logger import get_logger

logger = get_logger(__name__)

# Rutas de los scripts (deben coincidir con los de LAUNCHERS en settings.py)
_SCRIPT_CONNECT    = str(SCRIPTS_DIR / "conectar_vpn.sh")
_SCRIPT_DISCONNECT = str(SCRIPTS_DIR / "desconectar_vpn.sh")

# Intervalo de refresco del estado en ms
_REFRESH_MS = 3000


class VpnWindow(ctk.CTkToplevel):
    """Ventana de gestión de VPN."""

    def __init__(self, parent, vpn_monitor):
        super().__init__(parent)
        self.vpn_monitor = vpn_monitor

        self.title("Gestor VPN")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._running = True
        self._widgets = {}

        self._create_ui()
        self._update()
        logger.info("[VpnWindow] Ventana abierta")

    def destroy(self):
        self._running = False
        super().destroy()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="GESTOR VPN", on_close=self.destroy)

        # ── Tarjeta de estado ──
        status_card = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=8)
        status_card.pack(fill="x", padx=10, pady=(8, 4))

        ctk.CTkLabel(
            status_card,
            text="Estado de la conexión",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(fill="x", padx=14, pady=(10, 4))

        # Indicador de estado grande
        indicator_row = ctk.CTkFrame(status_card, fg_color="transparent")
        indicator_row.pack(fill="x", padx=14, pady=(0, 6))

        self._widgets['status_dot'] = ctk.CTkLabel(
            indicator_row,
            text="●",
            font=(FONT_FAMILY, 36, "bold"),
            text_color=COLORS['text_dim'],
        )
        self._widgets['status_dot'].pack(side="left", padx=(0, 10))

        status_text_col = ctk.CTkFrame(indicator_row, fg_color="transparent")
        status_text_col.pack(side="left", fill="x", expand=True)

        self._widgets['status_text'] = ctk.CTkLabel(
            status_text_col,
            text="Comprobando...",
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold"),
            text_color=COLORS['text'],
            anchor="w",
        )
        self._widgets['status_text'].pack(fill="x")

        self._widgets['status_detail'] = ctk.CTkLabel(
            status_text_col,
            text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        )
        self._widgets['status_detail'].pack(fill="x")

        # ── Botones de acción ──
        action_card = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=8)
        action_card.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            action_card,
            text="Acciones",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(fill="x", padx=14, pady=(10, 6))

        btn_row = ctk.CTkFrame(action_card, fg_color="transparent")
        btn_row.pack(pady=(0, 12))

        make_futuristic_button(
            btn_row,
            text="🔒 Conectar VPN",
            command=self._connect,
            width=18, height=10, font_size=18,
        ).pack(side="left", padx=12)

        make_futuristic_button(
            btn_row,
            text="🔓 Desconectar",
            command=self._disconnect,
            width=18, height=10, font_size=18,
        ).pack(side="left", padx=12)

        # ── Info de interfaz ──
        info_card = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=8)
        info_card.pack(fill="x", padx=10, pady=4)

        info_inner = ctk.CTkFrame(info_card, fg_color="transparent")
        info_inner.pack(fill="x", padx=14, pady=10)

        for key, label in [("iface_label", "Interfaz"), ("ip_label", "IP VPN")]:
            col = ctk.CTkFrame(info_inner, fg_color="transparent")
            col.pack(side="left", expand=True)

            ctk.CTkLabel(
                col,
                text=label,
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
            ).pack()

            lbl = ctk.CTkLabel(
                col,
                text="--",
                font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
                text_color=COLORS['primary'],
            )
            lbl.pack()
            self._widgets[key] = lbl

        # ── Nota sobre scripts ──
        note_frame = ctk.CTkFrame(main, fg_color="transparent")
        note_frame.pack(fill="x", padx=14, pady=(4, 0))

        ctk.CTkLabel(
            note_frame,
            text=f"Scripts: conectar_vpn.sh / desconectar_vpn.sh",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(fill="x")

    # ── Actualización ─────────────────────────────────────────────────────────

    def _update(self):
        if not self._running:
            return
        try:
            status = self.vpn_monitor.get_status()
            connected = status['connected']
            ip        = status['ip']
            iface     = status['interface']

            if connected:
                self._widgets['status_dot'].configure(text_color="#00CC66")
                self._widgets['status_text'].configure(
                    text="CONECTADA", text_color="#00CC66")
                self._widgets['status_detail'].configure(text="VPN activa")
            else:
                self._widgets['status_dot'].configure(text_color=COLORS['danger'])
                self._widgets['status_text'].configure(
                    text="DESCONECTADA", text_color=COLORS['danger'])
                self._widgets['status_detail'].configure(text="Sin conexión VPN")

            self._widgets['iface_label'].configure(
                text=iface if connected else "--",
                text_color=COLORS['primary'] if connected else COLORS['text_dim']
            )
            self._widgets['ip_label'].configure(
                text=ip if ip else "--",
                text_color=COLORS['primary'] if ip else COLORS['text_dim']
            )
        except Exception as e:
            logger.error("[VpnWindow] Error en _update: %s", e)

        self.after(_REFRESH_MS, self._update)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _connect(self):
        """Ejecuta conectar_vpn.sh con terminal en vivo."""
        import os
        if not os.path.exists(_SCRIPT_CONNECT):
            from ui.widgets.dialogs import custom_msgbox
            custom_msgbox(
                self,
                f"Script no encontrado:\n{_SCRIPT_CONNECT}\n\n"
                "Crea el script en la carpeta scripts/",
                "Error"
            )
            return
        terminal_dialog(
            parent=self,
            script_path=_SCRIPT_CONNECT,
            title="🔒 CONECTANDO VPN...",
            on_close=self._on_action_done,
        )

    def _disconnect(self):
        """Ejecuta desconectar_vpn.sh con terminal en vivo."""
        import os
        if not os.path.exists(_SCRIPT_DISCONNECT):
            from ui.widgets.dialogs import custom_msgbox
            custom_msgbox(
                self,
                f"Script no encontrado:\n{_SCRIPT_DISCONNECT}\n\n"
                "Crea el script en la carpeta scripts/",
                "Error"
            )
            return
        terminal_dialog(
            parent=self,
            script_path=_SCRIPT_DISCONNECT,
            title="🔓 DESCONECTANDO VPN...",
            on_close=self._on_action_done,
        )

    def _on_action_done(self):
        """Fuerza sondeo inmediato tras conectar/desconectar."""
        self.vpn_monitor.force_poll()
        # Pequeño delay para que el sondeo tenga tiempo de completarse
        self.after(2000, self._update)
```

## File: ui/windows/camera_window.py
```python
"""
Ventana de cámara del FNK0100K con OCR integrado.
- Captura fotos con rpicam-still (OV5647, Bookworm)
- OCR con Tesseract (local, sin internet)
- Guarda resultado en .txt y .md

Requisitos:
    sudo apt install tesseract-ocr tesseract-ocr-spa rpicam-apps
    pip install pytesseract pillow --break-system-packages
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES,
                              DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
import subprocess
import threading
import os
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

_PHOTO_DIR  = Path(__file__).resolve().parent.parent.parent / "data" / "photos"
_SCAN_DIR   = Path(__file__).resolve().parent.parent.parent / "data" / "scans"
_MAX_PHOTOS = 20

# Ancho del inner scrollable (mismo que el resto del proyecto)
_INNER_W = DSI_WIDTH - 50


class CameraWindow(ctk.CTkToplevel):
    """Ventana de cámara con captura de fotos y escáner OCR."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Cámara / Escáner")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        _PHOTO_DIR.mkdir(parents=True, exist_ok=True)
        _SCAN_DIR.mkdir(parents=True, exist_ok=True)

        self._busy       = False
        self._active_tab = "photo"   # "photo" | "scan"

        # Canvas/inner referencias para poder cambiar de tab
        self._canvases = {}
        self._inners   = {}

        self._create_ui()
        self._refresh_photo_list()
        self._refresh_scan_list()

    # ── Estructura principal ──────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="CÁMARA / ESCÁNER OCR", on_close=self.destroy)

        # ── Selector de tab (botones) ──
        tab_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'], corner_radius=8)
        tab_bar.pack(fill="x", padx=5, pady=(0, 4))

        self._tab_photo_btn = make_futuristic_button(
            tab_bar, text="📷 Foto",
            command=lambda: self._switch_tab("photo"),
            width=14, height=7, font_size=14,
        )
        self._tab_photo_btn.pack(side="left", padx=8, pady=6)

        self._tab_scan_btn = make_futuristic_button(
            tab_bar, text="🔍 Escáner OCR",
            command=lambda: self._switch_tab("scan"),
            width=18, height=7, font_size=14,
        )
        self._tab_scan_btn.pack(side="left", padx=4, pady=6)

        # ── Contenedor de tabs ──
        self._tab_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        self._tab_container.pack(fill="both", expand=True)

        # Construir ambas tabs (solo una visible a la vez)
        self._photo_frame = self._build_scrollable_tab(self._tab_container)
        self._scan_frame  = self._build_scrollable_tab(self._tab_container)

        self._build_photo_content(self._inners["photo"])
        self._build_scan_content(self._inners["scan"])

        # Mostrar tab foto por defecto
        self._switch_tab("photo")

    def _build_scrollable_tab(self, parent) -> ctk.CTkFrame:
        """
        Crea un frame con el patrón estándar del proyecto:
        scroll_container → canvas + CTkScrollbar → inner frame
        """
        tab_name = "photo" if "photo" not in self._canvases else "scan"

        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])

        scroll_container = ctk.CTkFrame(frame, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30,
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=_INNER_W)
        inner.bind("<Configure>",
                   lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))

        self._canvases[tab_name] = canvas
        self._inners[tab_name]   = inner

        return frame

    def _switch_tab(self, tab: str):
        self._active_tab = tab

        # Mostrar/ocultar frames
        if tab == "photo":
            self._scan_frame.pack_forget()
            self._photo_frame.pack(fill="both", expand=True)
            self._tab_photo_btn.configure(
                fg_color=COLORS['primary'], border_width=2,
                border_color=COLORS['secondary'])
            self._tab_scan_btn.configure(
                fg_color=COLORS['bg_dark'], border_width=1,
                border_color=COLORS['border'])
        else:
            self._photo_frame.pack_forget()
            self._scan_frame.pack(fill="both", expand=True)
            self._tab_scan_btn.configure(
                fg_color=COLORS['primary'], border_width=2,
                border_color=COLORS['secondary'])
            self._tab_photo_btn.configure(
                fg_color=COLORS['bg_dark'], border_width=1,
                border_color=COLORS['border'])

    # ── Contenido tab FOTO ────────────────────────────────────────────────────

    def _build_photo_content(self, inner: ctk.CTkFrame):
        # Controles captura
        ctrl = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        ctrl.pack(fill="x", padx=10, pady=(6, 4))

        row = ctk.CTkFrame(ctrl, fg_color="transparent")
        row.pack(pady=10)

        self._photo_btn = make_futuristic_button(
            row, text="📷 Capturar",
            command=self._capture_photo,
            width=16, height=9, font_size=16,
        )
        self._photo_btn.pack(side="left", padx=10)

        ctk.CTkLabel(row, text="Resolución:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(16, 4))

        self._res_var = ctk.StringVar(value="1920x1080")
        ctk.CTkOptionMenu(
            row, variable=self._res_var,
            values=["640x480", "1296x972", "1920x1080", "2592x1944"],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            button_color=COLORS['primary'],
            width=140,
        ).pack(side="left")

        self._photo_status = ctk.CTkLabel(
            ctrl, text="Listo",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        )
        self._photo_status.pack(pady=(0, 8))

        # Cabecera lista fotos
        list_hdr = ctk.CTkFrame(inner, fg_color="transparent")
        list_hdr.pack(fill="x", padx=10, pady=(4, 2))

        ctk.CTkLabel(list_hdr, text=f"Fotos guardadas (máx. {_MAX_PHOTOS})",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left")

        make_futuristic_button(
            list_hdr, text="🗑 Borrar todas",
            command=self._delete_all_photos,
            width=12, height=6, font_size=11,
        ).pack(side="right")

        # Lista fotos con scroll propio
        self._photo_list_frame = self._build_inner_scroll(inner, height=300)

    # ── Contenido tab ESCÁNER ─────────────────────────────────────────────────

    def _build_scan_content(self, inner: ctk.CTkFrame):
        # Controles escáner
        ctrl = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        ctrl.pack(fill="x", padx=10, pady=(6, 4))

        row = ctk.CTkFrame(ctrl, fg_color="transparent")
        row.pack(pady=8)

        self._scan_btn = make_futuristic_button(
            row, text="🔍 Escanear documento",
            command=self._scan_document,
            width=22, height=9, font_size=16,
        )
        self._scan_btn.pack(side="left", padx=10)

        ctk.CTkLabel(row, text="Idioma:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(16, 4))

        self._lang_var = ctk.StringVar(value="spa")
        ctk.CTkOptionMenu(
            row, variable=self._lang_var,
            values=["spa", "eng", "spa+eng"],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            button_color=COLORS['primary'],
            width=110,
        ).pack(side="left")

        self._scan_status = ctk.CTkLabel(
            ctrl, text="Coloca el documento y pulsa Escanear",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        )
        self._scan_status.pack(pady=(0, 8))

        # Texto extraído
        txt_hdr = ctk.CTkFrame(inner, fg_color="transparent")
        txt_hdr.pack(fill="x", padx=10, pady=(4, 2))

        ctk.CTkLabel(txt_hdr, text="Texto extraído:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left")

        self._copy_btn = make_futuristic_button(
            txt_hdr, text="📋 Copiar",
            command=self._copy_text,
            width=10, height=5, font_size=11,
        )
        self._copy_btn.pack(side="right")
        self._copy_btn.configure(state="disabled")

        self._text_box = ctk.CTkTextbox(
            inner,
            fg_color=COLORS['bg_dark'],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            height=160,
            wrap="word",
        )
        self._text_box.pack(fill="x", padx=10, pady=4)
        self._text_box.configure(state="disabled")

        # Cabecera lista escaneos
        scan_hdr = ctk.CTkFrame(inner, fg_color="transparent")
        scan_hdr.pack(fill="x", padx=10, pady=(6, 2))

        ctk.CTkLabel(scan_hdr, text="Escaneos guardados:",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left")

        make_futuristic_button(
            scan_hdr, text="🗑 Borrar todos",
            command=self._delete_all_scans,
            width=12, height=6, font_size=11,
        ).pack(side="right")

        # Lista escaneos con scroll propio
        self._scan_list_frame = self._build_inner_scroll(inner, height=200)

    # ── Scroll interno para listas ────────────────────────────────────────────

    def _build_inner_scroll(self, parent: ctk.CTkFrame, height: int) -> ctk.CTkFrame:
        """
        Crea un scroll interno para una lista de items.
        Mismo patrón que el scroll principal: container → canvas + CTkScrollbar → inner.
        Devuelve el inner frame donde añadir los items.
        """
        container = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'],
                                 corner_radius=6, height=height)
        container.pack(fill="x", padx=10, pady=(0, 6))
        container.pack_propagate(False)   # respetar height fija

        canvas = ctk.CTkCanvas(
            container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            container,
            orientation="vertical",
            command=canvas.yview,
            width=30,
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw",
                             width=_INNER_W - 40)
        inner.bind("<Configure>",
                   lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))

        return inner

    # ── Captura de foto ───────────────────────────────────────────────────────

    def _capture_photo(self):
        if self._busy:
            return
        self._busy = True
        self._photo_btn.configure(state="disabled")
        self._photo_status.configure(text="⏳ Capturando...", text_color=COLORS['text'])
        threading.Thread(target=self._do_capture, daemon=True).start()

    def _do_capture(self):
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = _PHOTO_DIR / f"foto_{ts}.jpg"
        w, h     = self._res_var.get().split("x")
        ok, msg  = self._rpicam_capture(filename, w, h)
        if ok:
            self._cleanup_old_photos()
        self.after(0, self._capture_done, msg)

    def _capture_done(self, msg: str):
        self._busy = False
        self._photo_btn.configure(state="normal")
        color = COLORS['primary'] if msg.startswith("✅") else COLORS['danger']
        self._photo_status.configure(text=msg, text_color=color)
        self._refresh_photo_list()

    # ── Escáner OCR ───────────────────────────────────────────────────────────

    def _scan_document(self):
        if self._busy:
            return
        self._busy = True
        self._scan_btn.configure(state="disabled")
        self._scan_status.configure(text="⏳ Capturando imagen...",
                                    text_color=COLORS['text'])
        self._clear_textbox()
        threading.Thread(target=self._do_scan, daemon=True).start()

    def _do_scan(self):
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = _PHOTO_DIR / f"scan_src_{ts}.jpg"
        lang     = self._lang_var.get()

        ok, msg = self._rpicam_capture(img_path, "2592", "1944")
        if not ok:
            self.after(0, self._scan_done, msg, None)
            return

        self.after(0, lambda: self._scan_status.configure(
            text="⏳ Procesando imagen..."))
        proc_path = _PHOTO_DIR / f"scan_proc_{ts}.jpg"
        self._preprocess_image(img_path, proc_path)

        self.after(0, lambda: self._scan_status.configure(
            text="⏳ Extrayendo texto (OCR)..."))
        text, ocr_msg = self._run_ocr(proc_path, lang)

        if text:
            txt_path = _SCAN_DIR / f"scan_{ts}.txt"
            md_path  = _SCAN_DIR / f"scan_{ts}.md"
            self._save_txt(txt_path, text, ts)
            self._save_md(md_path, text, ts)

        for p in [img_path, proc_path]:
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass

        self.after(0, self._scan_done, ocr_msg, text)

    def _scan_done(self, msg: str, text):
        self._busy = False
        self._scan_btn.configure(state="normal")
        color = COLORS['primary'] if text else COLORS['danger']
        self._scan_status.configure(text=msg, text_color=color)
        if text:
            self._set_textbox(text)
            self._copy_btn.configure(state="normal")
        self._refresh_scan_list()

    # ── rpicam-still ─────────────────────────────────────────────────────────

    def _rpicam_capture(self, filename: Path, w: str, h: str):
        cmd = ["rpicam-still", "-o", str(filename),
               "--width", w, "--height", h,
               "--timeout", "2000", "--nopreview"]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=20)
            if r.returncode == 0 and filename.exists():
                return True, f"✅ Capturada: {filename.name}"
            err = r.stderr.decode().strip()[:80]
            return False, f"❌ Error cámara: {err or 'rpicam-still falló'}"
        except FileNotFoundError:
            return False, "❌ rpicam-still no encontrado"
        except subprocess.TimeoutExpired:
            return False, "❌ Timeout — ¿cámara conectada?"
        except Exception as e:
            return False, f"❌ {e}"

    # ── Preprocesado + OCR ────────────────────────────────────────────────────

    def _preprocess_image(self, src: Path, dst: Path):
        try:
            from PIL import Image, ImageFilter, ImageEnhance
            img = Image.open(src).convert("L")
            img = ImageEnhance.Contrast(img).enhance(2.0)
            img = img.filter(ImageFilter.SHARPEN)
            img.save(str(dst), "JPEG", quality=95)
        except Exception as e:
            logger.warning("[CameraWindow] Preprocesado falló: %s", e)
            import shutil
            shutil.copy(str(src), str(dst))

    def _run_ocr(self, img_path: Path, lang: str):
        try:
            import pytesseract
            from PIL import Image
            img  = Image.open(str(img_path))
            text = pytesseract.image_to_string(
                img, config=f"--oem 3 --psm 6 -l {lang}"
            ).strip()
            if not text:
                return None, "⚠️ No se detectó texto en la imagen"
            words = len(text.split())
            lines = len(text.splitlines())
            return text, f"✅ {lines} líneas / {words} palabras extraídas"
        except ImportError:
            return None, "❌ pytesseract no instalado: pip install pytesseract"
        except Exception as e:
            return None, f"❌ Error OCR: {e}"

    # ── Guardado ──────────────────────────────────────────────────────────────

    def _save_txt(self, path: Path, text: str, ts: str):
        try:
            path.write_text(
                f"Escaneo: {ts}\n{'─' * 40}\n\n{text}", encoding="utf-8"
            )
        except Exception as e:
            logger.error("[CameraWindow] Error TXT: %s", e)

    def _save_md(self, path: Path, text: str, ts: str):
        try:
            dt = datetime.strptime(ts, "%Y%m%d_%H%M%S").strftime("%d/%m/%Y %H:%M:%S")
            lines = [
                "# Escaneo OCR", "",
                f"**Fecha:** {dt}  ",
                f"**Idioma:** {self._lang_var.get()}  ",
                f"**Palabras:** {len(text.split())}",
                "", "---", "", "## Texto extraído", "",
            ]
            for line in text.splitlines():
                lines.append(line if line.strip() else "")
            path.write_text("\n".join(lines), encoding="utf-8")
        except Exception as e:
            logger.error("[CameraWindow] Error MD: %s", e)

    # ── TextBox helpers ───────────────────────────────────────────────────────

    def _set_textbox(self, text: str):
        self._text_box.configure(state="normal")
        self._text_box.delete("1.0", "end")
        self._text_box.insert("1.0", text)
        self._text_box.configure(state="disabled")

    def _clear_textbox(self):
        self._text_box.configure(state="normal")
        self._text_box.delete("1.0", "end")
        self._text_box.configure(state="disabled")
        self._copy_btn.configure(state="disabled")

    def _copy_text(self):
        self._text_box.configure(state="normal")
        text = self._text_box.get("1.0", "end").strip()
        self._text_box.configure(state="disabled")
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self._copy_btn.configure(text="✅ Copiado")
            self.after(2000, lambda: self._copy_btn.configure(text="📋 Copiar"))

    # ── Listas ────────────────────────────────────────────────────────────────

    def _refresh_photo_list(self):
        for w in self._photo_list_frame.winfo_children():
            w.destroy()
        photos = sorted(_PHOTO_DIR.glob("foto_*.jpg"), reverse=True)
        if not photos:
            ctk.CTkLabel(self._photo_list_frame,
                         text="No hay fotos guardadas",
                         text_color=COLORS['text_dim']).pack(pady=10)
            return
        for p in photos:
            self._list_row(self._photo_list_frame, f"📷 {p.name}",
                           p.stat().st_size // 1024,
                           on_delete=lambda ph=p: self._delete_one_photo(ph))

    def _refresh_scan_list(self):
        for w in self._scan_list_frame.winfo_children():
            w.destroy()
        txts = sorted(_SCAN_DIR.glob("scan_*.txt"), reverse=True)
        if not txts:
            ctk.CTkLabel(self._scan_list_frame,
                         text="No hay escaneos guardados",
                         text_color=COLORS['text_dim']).pack(pady=10)
            return
        for txt in txts:
            md = txt.with_suffix(".md")
            self._scan_row(self._scan_list_frame, txt, md)

    def _list_row(self, parent, label: str, size_kb: int, on_delete):
        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=6)
        row.pack(fill="x", pady=2, padx=4)
        ctk.CTkLabel(row, text=f"{label}  ({size_kb} KB)",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text'], anchor="w",
                     ).pack(side="left", padx=10, pady=6, expand=True, fill="x")
        make_futuristic_button(
            row, text="🗑",
            command=on_delete,
            width=4, height=5, font_size=13,
        ).pack(side="right", padx=6, pady=4)

    def _scan_row(self, parent, txt: Path, md: Path):
        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=6)
        row.pack(fill="x", pady=2, padx=4)
        size_kb = txt.stat().st_size // 1024
        ctk.CTkLabel(row,
                     text=f"📄 {txt.stem}  ({size_kb} KB)  [.txt + .md]",
                     font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text'], anchor="w",
                     ).pack(side="left", padx=10, pady=6, expand=True, fill="x")
        make_futuristic_button(
            row, text="🗑",
            command=lambda t=txt, m=md: self._delete_scan(t, m),
            width=4, height=5, font_size=13,
        ).pack(side="right", padx=2, pady=4)
        make_futuristic_button(
            row, text="📂",
            command=lambda t=txt: self._load_scan(t),
            width=4, height=5, font_size=13,
        ).pack(side="right", padx=2, pady=4)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _load_scan(self, txt_path: Path):
        try:
            text = txt_path.read_text(encoding="utf-8")
            self._set_textbox(text)
            self._copy_btn.configure(state="normal")
            self._switch_tab("scan")
        except Exception as e:
            logger.error("[CameraWindow] Error cargando: %s", e)

    def _delete_scan(self, txt: Path, md: Path):
        for p in [txt, md]:
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass
        self._refresh_scan_list()

    def _delete_one_photo(self, p: Path):
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass
        self._refresh_photo_list()

    def _delete_all_photos(self):
        for p in _PHOTO_DIR.glob("foto_*.jpg"):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass
        self._refresh_photo_list()

    def _delete_all_scans(self):
        for p in _SCAN_DIR.glob("scan_*"):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass
        self._refresh_scan_list()
        self._clear_textbox()

    def _cleanup_old_photos(self):
        photos = sorted(_PHOTO_DIR.glob("foto_*.jpg"))
        while len(photos) > _MAX_PHOTOS:
            photos[0].unlink(missing_ok=True)
            photos = photos[1:]
```

## File: ui/windows/display_window.py
```python
"""
Ventana de control de brillo de la pantalla.
Hardware: Freenove FNK0100K — Raspberry Pi 5.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger
from core.display_service import BRIGHTNESS_MIN, BRIGHTNESS_MAX

logger = get_logger(__name__)

QUICK_LEVELS = [
    ("🌑 10%",   10),
    ("🌒 30%",   30),
    ("🌓 60%",   60),
    ("🌕 100%", 100),
]


class DisplayWindow(ctk.CTkToplevel):
    """Ventana de control de brillo de pantalla."""

    def __init__(self, parent, display_service):
        super().__init__(parent)
        self.display_service = display_service

        self.title("Control de Pantalla")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._slider_var = ctk.IntVar(value=self.display_service.get_brightness())

        self._create_ui()
        self._refresh()
        logger.info("[DisplayWindow] Ventana abierta (método: %s)",
                    self.display_service.get_method())

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main, 
            title="CONTROL DE PANTALLA", 
            on_close=self.destroy,
            )
        # Area de scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        # Canvas para scroll
        canvas = ctk.CTkCanvas(
            scroll_container, 
            bg=COLORS['bg_medium'], 
            highlightthickness=0,
        )        
        canvas.pack(side="left", fill="both", expand=True)
        # Scrollable frame dentro del canvas
        scrollbar = ctk.CTkScrollbar(
            scroll_container, 
            orientation="vertical",
            command=canvas.yview,
            width=30,
            )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame que contiene el contenido real, dentro del canvas
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # ── Sin método disponible ──
        if not self.display_service.is_available():
            ctk.CTkLabel(
                inner,
                text=(
                    "⚠️ Brillo no disponible\n\n"
                    "No se encontró /sys/class/backlight/ ni wlr-randr.\n\n"
                    "Consulta GUIA_BRILLO_DSI.md → Paso 0\n"
                    "para diagnosticar tu sistema."
                ),
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                text_color=COLORS.get('warning', '#ffaa00'),
                justify="center",
            ).pack(expand=True)
            return

        # ── Info método activo ──
        method = self.display_service.get_method()
        ctk.CTkLabel(
            inner,
            text=f"Método activo: {method}",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(fill="x", padx=14, pady=(4, 0))

        # ── Tarjeta brillo actual + slider ──
        card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(6, 4))

        ctk.CTkLabel(
            card, text="Brillo",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(pady=(10, 0))

        self._brightness_label = ctk.CTkLabel(
            card, text="--",
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold"),
            text_color=COLORS['primary'],
        )
        self._brightness_label.pack()

        ctk.CTkSlider(
            card,
            from_=BRIGHTNESS_MIN, to=BRIGHTNESS_MAX,
            variable=self._slider_var,
            command=self._on_slider,
            width=680, height=36,
            button_length=40,
            progress_color=COLORS['primary'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['secondary'],
        ).pack(padx=20, pady=(4, 14))

        # ── Niveles rápidos ──
        quick = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        quick.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            quick, text="Niveles rápidos",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(pady=(8, 4))

        row = ctk.CTkFrame(quick, fg_color="transparent")
        row.pack(pady=(0, 10))
        for label, value in QUICK_LEVELS:
            make_futuristic_button(
                row, text=label,
                command=lambda v=value: self._set_quick(v),
                width=14, height=8, font_size=14,
            ).pack(side="left", padx=6)

        # ── ON / OFF ──
        toggle = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        toggle.pack(fill="x", padx=10, pady=4)

        tog_row = ctk.CTkFrame(toggle, fg_color="transparent")
        tog_row.pack(pady=10)

        make_futuristic_button(
            tog_row, text="🌕 Encender",
            command=self._screen_on,
            width=16, height=8, font_size=16,
        ).pack(side="left", padx=10)

        make_futuristic_button(
            tog_row, text="🌑 Apagar",
            command=self._screen_off,
            width=16, height=8, font_size=16,
        ).pack(side="left", padx=10)

        # ── Modo ahorro ──
        dim = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        dim.pack(fill="x", padx=10, pady=4)

        dim_row = ctk.CTkFrame(dim, fg_color="transparent")
        dim_row.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(
            dim_row,
            text="Dim automático  (2 min → 20%  |  4 min → apagado):",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(side="left", padx=(0, 10))

        self._dim_switch = ctk.CTkSwitch(
            dim_row, text="",
            command=self._toggle_dim,
            width=60, height=30,
            switch_width=60, switch_height=30,
            progress_color=COLORS['primary'],
        )
        self._dim_switch.pack(side="left") 

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_slider(self, value):
        self.display_service.set_brightness(int(value))
        self._refresh()

    def _set_quick(self, value):
        self.display_service.set_brightness(value)
        self._slider_var.set(value)
        self._refresh()

    def _screen_on(self):
        self.display_service.screen_on()
        self._refresh()

    def _screen_off(self):
        self.display_service.screen_off()
        self._refresh()

    def _toggle_dim(self):
        if self._dim_switch.get():
            self.display_service.enable_dim_on_idle()
        else:
            self.display_service.disable_dim_on_idle()

    def _refresh(self):
        if not self.display_service.is_available():
            return
        pct = self.display_service.get_brightness()
        self._brightness_label.configure(text=f"{pct}%")
        self._slider_var.set(pct)
```

## File: ui/windows/overview.py
```python
"""
Ventana de resumen general del sistema.
Muestra todas las métricas críticas en un solo vistazo.
Pensada para usarse como pantalla de reposo en la DSI.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
)
from ui.styles import make_window_header, make_futuristic_button
from utils.logger import get_logger

logger = get_logger(__name__)

# Intervalo de refresco en ms
_REFRESH_MS = 2000


class OverviewWindow(ctk.CTkToplevel):
    """Ventana de resumen — métricas críticas en un vistazo."""

    def __init__(self, parent, system_monitor, service_monitor,
                 pihole_monitor, network_monitor, disk_monitor):
        super().__init__(parent)
        self.system_monitor  = system_monitor
        self.service_monitor = service_monitor
        self.pihole_monitor  = pihole_monitor
        self.network_monitor = network_monitor
        self.disk_monitor    = disk_monitor

        self.title("Resumen del Sistema")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._widgets = {}   # clave -> CTkLabel de valor
        self._running = True

        self._create_ui()
        self._update()
        logger.info("[OverviewWindow] Ventana abierta")

    def destroy(self):
        self._running = False
        super().destroy()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="RESUMEN DEL SISTEMA", on_close=self.destroy)

        # Grid 2x3 de tarjetas
        grid = ctk.CTkFrame(main, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=5, pady=5)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        cards = [
            ("cpu",      "🔥 CPU",         "row=0,col=0"),
            ("ram",      "💾 RAM",         "row=0,col=1"),
            ("temp",     "🌡️ Temperatura", "row=1,col=0"),
            ("disk",     "💿 Disco",       "row=1,col=1"),
            ("net",      "🌐 Red",         "row=2,col=0"),
            ("services", "⚙️ Servicios",   "row=2,col=1"),
        ]

        for key, title, pos in cards:
            # Parsear posición
            parts = {p.split("=")[0]: int(p.split("=")[1]) for p in pos.split(",")}
            row, col = parts["row"], parts["col"]

            card = ctk.CTkFrame(
                grid,
                fg_color=COLORS['bg_dark'],
                corner_radius=8,
            )
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            grid.rowconfigure(row, weight=1)

            ctk.CTkLabel(
                card,
                text=title,
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
                anchor="w",
            ).pack(fill="x", padx=12, pady=(10, 2))

            val_label = ctk.CTkLabel(
                card,
                text="--",
                font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold"),
                text_color=COLORS['primary'],
                anchor="center",
            )
            val_label.pack(expand=True)
            self._widgets[key] = val_label

        # Fila extra: Pi-hole (ancho completo)
        pihole_card = ctk.CTkFrame(
            grid,
            fg_color=COLORS['bg_dark'],
            corner_radius=8,
        )
        pihole_card.grid(row=3, column=0, columnspan=2, padx=6, pady=6, sticky="nsew")
        grid.rowconfigure(3, weight=1)

        ctk.CTkLabel(
            pihole_card,
            text="🕳️ Pi-hole",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="w",
        ).pack(fill="x", padx=12, pady=(10, 2))

        pihole_inner = ctk.CTkFrame(pihole_card, fg_color="transparent")
        pihole_inner.pack(fill="x", padx=12, pady=(0, 10))

        for sub_key, sub_label in [
            ("pihole_blocked", "Bloqueadas"),
            ("pihole_pct",     "% Bloqueo"),
            ("pihole_total",   "Total"),
            ("pihole_status",  "Estado"),
        ]:
            col_frame = ctk.CTkFrame(pihole_inner, fg_color="transparent")
            col_frame.pack(side="left", expand=True)

            ctk.CTkLabel(
                col_frame,
                text=sub_label,
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
            ).pack()

            lbl = ctk.CTkLabel(
                col_frame,
                text="--",
                font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
                text_color=COLORS['primary'],
            )
            lbl.pack()
            self._widgets[sub_key] = lbl

    # ── Actualización ─────────────────────────────────────────────────────────

    def _update(self):
        if not self._running:
            return
        try:
            self._refresh_system()
            self._refresh_services()
            self._refresh_net()
            self._refresh_pihole()
        except Exception as e:
            logger.error("[OverviewWindow] Error en _update: %s", e)
        self.after(_REFRESH_MS, self._update)

    def _color_for(self, value, warn, crit):
        """Devuelve el color según umbrales."""
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS.get('warning', '#ffaa00')
        return COLORS['primary']

    def _refresh_system(self):
        stats = self.system_monitor.get_current_stats()

        cpu  = stats.get('cpu', 0)
        ram  = stats.get('ram', 0)
        temp = stats.get('temp', 0)
        disk = stats.get('disk_usage', 0)

        self._widgets['cpu'].configure(
            text=f"{cpu:.0f}%",
            text_color=self._color_for(cpu, 75, 90)
        )
        self._widgets['ram'].configure(
            text=f"{ram:.0f}%",
            text_color=self._color_for(ram, 75, 90)
        )
        self._widgets['temp'].configure(
            text=f"{temp:.0f}°C",
            text_color=self._color_for(temp, 60, 70)
        )
        self._widgets['disk'].configure(
            text=f"{disk:.0f}%",
            text_color=self._color_for(disk, 80, 90)
        )

    def _refresh_services(self):
        stats  = self.service_monitor.get_stats()
        failed = stats.get('failed', 0)
        total  = stats.get('total', 0)
        color  = COLORS['danger'] if failed > 0 else COLORS['primary']
        text   = f"{failed} caídos" if failed > 0 else f"{total} OK"
        self._widgets['services'].configure(text=text, text_color=color)

    def _refresh_net(self):
        try:
            stats = self.network_monitor.get_current_stats()
            dl = stats.get('download_mb', 0)
            ul = stats.get('upload_mb', 0)
            iface = stats.get('interface', '')
            self._widgets['net'].configure(
                text=f"↓{dl:.1f} ↑{ul:.1f}",
                text_color=COLORS['primary']
            )
        except Exception:
            self._widgets['net'].configure(text="--")

    def _refresh_pihole(self):
        try:
            stats = self.pihole_monitor.get_stats()
            if not stats:
                raise ValueError("sin datos")
            blocked = stats.get('blocked_today', 0)
            total   = stats.get('queries_today', 0)
            pct     = stats.get('percent_blocked', 0)
            status  = stats.get('status', 'desconocido').capitalize()
            self._widgets['pihole_blocked'].configure(text=f"{blocked:,}")
            self._widgets['pihole_pct'].configure(text=f"{pct:.1f}%")
            self._widgets['pihole_total'].configure(text=f"{total:,}")
            self._widgets['pihole_status'].configure(text=f"{status}")
        except Exception:
            for k in ('pihole_blocked', 'pihole_pct', 'pihole_total', 'pihole_status'):
                self._widgets[k].configure(text="--", text_color=COLORS['text_dim'])
```

## File: ui/windows/process_window.py
```python
"""
Ventana de monitor de procesos
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.process_monitor import ProcessMonitor


class ProcessWindow(ctk.CTkToplevel):
    """Ventana de monitor de procesos"""
    
    def __init__(self, parent, process_monitor: ProcessMonitor):
        super().__init__(parent)
        
        # Referencias
        self.process_monitor = process_monitor
        
        # Estado
        self.search_var = ctk.StringVar()
        self.filter_var = ctk.StringVar(value="all")
        self.process_labels = []  # Lista de labels de procesos
        self.update_paused = False  # Flag para pausar actualización
        self.update_job = None  # ID del trabajo de actualización
        
        # Configurar ventana
        self.title("Monitor de Procesos")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        # Crear interfaz
        self._create_ui()
        
        # Iniciar actualización
        self._update()
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="MONITOR DE PROCESOS",
            on_close=self.destroy,
        )

        # Stats en línea propia debajo del header
        stats_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'])
        stats_bar.pack(fill="x", padx=5, pady=(0, 4))
        self.stats_label = ctk.CTkLabel(
            stats_bar,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self.stats_label.pack(pady=4, padx=10, anchor="w")
        
        # Controles (búsqueda y filtros)
        self._create_controls(main)
        
        # Encabezados de columnas
        self._create_column_headers(main)
        
        # Área de scroll para procesos (con altura limitada)
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Limitar altura del canvas para que el botón cerrar sea visible
        max_height = DSI_HEIGHT - 300  # Dejar espacio para header, controles y botón
        
        # Canvas y scrollbar
        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=max_height  # Altura máxima
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno para procesos
        self.process_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self.process_frame, anchor="nw", width=DSI_WIDTH-50)
        self.process_frame.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Botón cerrar
        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=5, padx=10)
        
    
    
    def _create_controls(self, parent):
        """Crea controles de búsqueda y filtros"""
        controls = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        controls.pack(fill="x", padx=10, pady=5)
        
        # Búsqueda
        search_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        search_frame.pack(side="left", padx=10, pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="Buscar:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            width=200,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())
        
        # Filtros
        filter_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        filter_frame.pack(side="left", padx=20, pady=10)
        
        ctk.CTkLabel(
            filter_frame,
            text="Filtro:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))
        
        for filter_type, label in [("all", "Todos"), ("user", "Usuario"), ("system", "Sistema")]:
            rb = ctk.CTkRadioButton(
                filter_frame,
                text=label,
                variable=self.filter_var,
                value=filter_type,
                command=self._on_filter_change,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=5)
            from ui.styles import StyleManager
            StyleManager.style_radiobutton_ctk(rb)
    
    def _create_column_headers(self, parent):
        """Crea encabezados de columnas ordenables"""
        headers = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'])
        headers.pack(fill="x", padx=10, pady=(5, 0))
        
        # Configurar grid
        headers.grid_columnconfigure(0, weight=1, minsize=20)   # PID
        headers.grid_columnconfigure(1, weight=4, minsize=200)  # Nombre
        headers.grid_columnconfigure(2, weight=2, minsize=100)  # Usuario
        headers.grid_columnconfigure(3, weight=1, minsize=80)   # CPU
        headers.grid_columnconfigure(4, weight=1, minsize=80)   # RAM
        headers.grid_columnconfigure(5, weight=1, minsize=100)  # Acción
        
        # Crear headers
        columns = [
            ("PID", "pid"),
            ("Proceso", "name"),
            ("Usuario", "username"),
            ("CPU%", "cpu"),
            ("RAM%", "memory"),
            ("Acción", None)
        ]
        
        for i, (label, sort_key) in enumerate(columns):
            if sort_key:
                btn = ctk.CTkButton(
                    headers,
                    text=label,
                    command=lambda k=sort_key: self._on_sort_change(k),
                    fg_color=COLORS['bg_medium'],
                    hover_color=COLORS['bg_dark'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                    width=50,
                    height=30
                )
            else:
                btn = ctk.CTkLabel(
                    headers,
                    text=label,
                    text_color=COLORS['text'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
                )
            
            btn.grid(row=0, column=i, sticky="n", padx=2, pady=5)
    
    def _on_sort_change(self, column: str):
        """Cambia el orden de procesos"""
        # Pausar actualización automática temporalmente
        self.update_paused = True
        
        # Si ya estaba ordenado por esta columna, invertir
        if self.process_monitor.sort_by == column:
            self.process_monitor.sort_reverse = not self.process_monitor.sort_reverse
        else:
            self.process_monitor.set_sort(column, reverse=True)
        
        # Actualizar inmediatamente
        self._update_now()
        
        # Reanudar actualización después de 2 segundos
        self.after(2000, self._resume_updates)
    
    def _on_filter_change(self):
        """Cambia el filtro de procesos"""
        # Pausar actualización automática temporalmente
        self.update_paused = True
        
        self.process_monitor.set_filter(self.filter_var.get())
        
        # Actualizar inmediatamente
        self._update_now()
        
        # Reanudar actualización después de 2 segundos
        self.after(2000, self._resume_updates)
    
    def _update_now(self):
        """Actualiza inmediatamente sin programar siguiente"""
        if not self.winfo_exists():
            return
        
        # Cancelar actualización programada si existe
        if self.update_job:
            self.after_cancel(self.update_job)
            self.update_job = None
        
        # Actualizar estadísticas del sistema
        stats = self.process_monitor.get_system_stats()
        self.stats_label.configure(
            text=f"Procesos: {stats['total_processes']} | "
                 f"CPU: {stats['cpu_percent']:.1f}% | "
                 f"RAM: {stats['mem_used_gb']:.1f}/{stats['mem_total_gb']:.1f} GB ({stats['mem_percent']:.1f}%) | "
                 f"Uptime: {stats['uptime']}"
        )
        
        # Limpiar procesos anteriores
        for widget in self.process_frame.winfo_children():
            widget.destroy()
        self.process_labels = []
        
        # Obtener procesos
        search_query = self.search_var.get()
        if search_query:
            processes = self.process_monitor.search_processes(search_query)
        else:
            processes = self.process_monitor.get_processes(limit=20)
        
        # Mostrar procesos
        for i, proc in enumerate(processes):
            self._create_process_row(proc, i)
    
    def _resume_updates(self):
        """Reanuda las actualizaciones automáticas"""
        self.update_paused = False
    
    def _on_search_change(self):
        """Callback cuando cambia la búsqueda"""
        # Pausar actualización automática temporalmente
        self.update_paused = True
        
        # Cancelar timer anterior si existe
        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)
        
        # Actualizar después de 500ms (debounce)
        self._search_timer = self.after(500, self._do_search)
    
    def _do_search(self):
        """Ejecuta la búsqueda"""
        self._update_now()
        # Reanudar actualización después de 3 segundos
        self.after(3000, self._resume_updates)
    
    def _update(self):
        """Actualiza la lista de procesos"""
        if not self.winfo_exists():
            return
        
        # Si está pausada, reprogramar y salir
        if self.update_paused:
            self.update_job = self.after(UPDATE_MS * 2, self._update)
            return
        
        # Actualizar estadísticas del sistema
        stats = self.process_monitor.get_system_stats()
        self.stats_label.configure(
            text=f"Procesos: {stats['total_processes']} | "
                 f"CPU: {stats['cpu_percent']:.1f}% | "
                 f"RAM: {stats['mem_used_gb']:.1f}/{stats['mem_total_gb']:.1f} GB ({stats['mem_percent']:.1f}%) | "
                 f"Uptime: {stats['uptime']}"
        )
        
        # Limpiar procesos anteriores
        for widget in self.process_frame.winfo_children():
            widget.destroy()
        self.process_labels = []
        
        # Obtener procesos
        search_query = self.search_var.get()
        if search_query:
            processes = self.process_monitor.search_processes(search_query)
        else:
            processes = self.process_monitor.get_processes(limit=20)
        
        # Mostrar procesos
        for i, proc in enumerate(processes):
            self._create_process_row(proc, i)
        
        # Programar siguiente actualización
        self.update_job = self.after(UPDATE_MS * 2, self._update)  # Cada 4 segundos
    
    def _create_process_row(self, proc: dict, row: int):
        """Crea una fila para un proceso"""
        # Frame de la fila (sin altura fija, se adapta al contenido)
        bg_color = COLORS['bg_dark'] if row % 2 == 0 else COLORS['bg_medium']
        row_frame = ctk.CTkFrame(self.process_frame, fg_color=bg_color)
        row_frame.pack(fill="x", pady=2, padx=10)  # Más padding vertical
        
        # Configurar grid igual que headers
        row_frame.grid_columnconfigure(0, weight=1, minsize=70)
        row_frame.grid_columnconfigure(1, weight=3, minsize=300)
        row_frame.grid_columnconfigure(2, weight=2, minsize=100)
        row_frame.grid_columnconfigure(3, weight=1, minsize=80)
        row_frame.grid_columnconfigure(4, weight=1, minsize=80)
        row_frame.grid_columnconfigure(5, weight=1, minsize=100)
        
        # Colores según uso
        cpu_color = COLORS[self.process_monitor.get_process_color(proc['cpu'])]
        mem_color = COLORS[self.process_monitor.get_process_color(proc['memory'])]
        
        # PID
        ctk.CTkLabel(
            row_frame,
            text=str(proc['pid']),
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="center"
        ).grid(row=0, column=0, sticky="n", padx=5, pady=5)  # nw = arriba izquierda
        
        # Nombre (mostrar display_name que es más descriptivo)
        name_text = proc.get('display_name', proc['name'])
        name_label = ctk.CTkLabel(
            row_frame,
            text=name_text,  # Sin truncar
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=250,  # Ajustar texto en 350px de ancho
            justify="left",
            anchor="center"
        )
        name_label.grid(row=0, column=1, sticky="n", padx=5, pady=5)  # nw = arriba izquierda
        
        # Usuario
        ctk.CTkLabel(
            row_frame,
            text=proc['username'][:15],
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="center"
        ).grid(row=0, column=2, sticky="n", padx=5, pady=5)  # nw = arriba izquierda
        
        # CPU
        ctk.CTkLabel(
            row_frame,
            text=f"{proc['cpu']:.1f}%",
            text_color=cpu_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).grid(row=0, column=3, sticky="n", padx=5, pady=5)  # ne = arriba derecha
        
        # RAM
        ctk.CTkLabel(
            row_frame,
            text=f"{proc['memory']:.1f}%",
            text_color=mem_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).grid(row=0, column=4, sticky="n", padx=5, pady=5)  # ne = arriba derecha
        
        # Botón matar
        kill_btn = ctk.CTkButton(
            row_frame,
            text="Matar",
            command=lambda p=proc: self._kill_process(p),
            fg_color=COLORS['danger'],
            hover_color="#cc0000",
            width=70,
            height=25,
            font=(FONT_FAMILY, 9)
        )
        kill_btn.grid(row=0, column=5, padx=5, pady=5)  # centrado
    
    def _kill_process(self, proc: dict):
        """Mata un proceso con confirmación"""
        def do_kill():
            success, message = self.process_monitor.kill_process(proc['pid'])
            
            if success:
                title = "Proceso Terminado"
            else:
                title = "Error"
            
            custom_msgbox(self, message, title)
            self._update()  # Actualizar lista
        
        # Confirmar
        confirm_dialog(
            parent=self,
            text=f"¿Matar proceso '{proc['name']}'?\n\nPID: {proc['pid']}\nCPU: {proc['cpu']:.1f}%",
            title="⚠️ Confirmar",
            on_confirm=do_kill,
            on_cancel=None
        )
```

## File: ui/windows/service.py
```python
"""
Ventana de monitor de servicios systemd
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import confirm_dialog, custom_msgbox
from core.service_monitor import ServiceMonitor


class ServiceWindow(ctk.CTkToplevel):
    """Ventana de monitor de servicios"""

    def __init__(self, parent, service_monitor: ServiceMonitor):
        super().__init__(parent)

        # Referencias
        self.service_monitor = service_monitor

        # Estado
        self.search_var = ctk.StringVar()
        self.filter_var = ctk.StringVar(value="all")
        self.update_paused = False
        self.update_job = None

        # Configurar ventana
        self.title("Monitor de Servicios")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        # Crear interfaz
        self._create_ui()

        # Iniciar actualización
        self._update()

    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="MONITOR DE SERVICIOS",
            on_close=self.destroy,
        )

        # Stats en línea propia debajo del header
        stats_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'])
        stats_bar.pack(fill="x", padx=5, pady=(0, 4))
        self.stats_label = ctk.CTkLabel(
            stats_bar,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self.stats_label.pack(pady=4, padx=10, anchor="w")

        # Controles (búsqueda y filtros)
        self._create_controls(main)

        # Encabezados de columnas
        self._create_column_headers(main)

        # Área de scroll para servicios
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Limitar altura
        max_height = DSI_HEIGHT - 300

        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=max_height
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")


        StyleManager.style_scrollbar_ctk(scrollbar)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame interno para servicios
        self.service_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self.service_frame, anchor="nw", width=DSI_WIDTH-50)
        self.service_frame.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Botones inferiores
        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)

        refresh_btn = make_futuristic_button(
            bottom,
            text="Refrescar",
            command=self._force_update,
            width=15,
            height=6
        )
        refresh_btn.pack(side="left", padx=5)



    def _create_controls(self, parent):
        """Crea controles de búsqueda y filtros"""
        controls = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        controls.pack(fill="x", padx=10, pady=5)

        # Búsqueda
        search_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        search_frame.pack(side="left", padx=10, pady=10)

        ctk.CTkLabel(
            search_frame,
            text="Buscar:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))

        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            width=200,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda e: self._on_search_change())

        # Filtros
        filter_frame = ctk.CTkFrame(controls, fg_color=COLORS['bg_dark'])
        filter_frame.pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            filter_frame,
            text="Filtro:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 5))

        for filter_type, label in [("all", "Todos"), ("active", "Activos"), 
                                   ("inactive", "Inactivos"), ("failed", "Fallidos")]:
            rb = ctk.CTkRadioButton(
                filter_frame,
                text=label,
                variable=self.filter_var,
                value=filter_type,
                command=self._on_filter_change,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=5)
            StyleManager.style_radiobutton_ctk(rb)

    def _create_column_headers(self, parent):
        """Crea encabezados de columnas"""
        headers = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'])
        headers.pack(fill="x", padx=10, pady=(5, 0))

        headers.grid_columnconfigure(0, weight=2, minsize=150)  # Servicio
        headers.grid_columnconfigure(1, weight=1, minsize=100)  # Estado
        headers.grid_columnconfigure(2, weight=1, minsize=80)   # Autostart
        headers.grid_columnconfigure(3, weight=3, minsize=300)  # Acciones

        columns = [
            ("Servicio", "name"),
            ("Estado", "state"),
            ("Autostart", None),
            ("Acciones", None)
        ]

        for i, (label, sort_key) in enumerate(columns):
            if sort_key:
                btn = ctk.CTkButton(
                    headers,
                    text=label,
                    command=lambda k=sort_key: self._on_sort_change(k),
                    fg_color=COLORS['bg_medium'],
                    hover_color=COLORS['bg_dark'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                    height=30
                )
            else:
                btn = ctk.CTkLabel(
                    headers,
                    text=label,
                    text_color=COLORS['text'],
                    font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
                )

            btn.grid(row=0, column=i, sticky="ew", padx=2, pady=5)

    def _on_sort_change(self, column: str):
        """Cambia el orden"""
        self.update_paused = True

        if self.service_monitor.sort_by == column:
            self.service_monitor.sort_reverse = not self.service_monitor.sort_reverse
        else:
            self.service_monitor.set_sort(column, reverse=False)

        self._update_now()
        self.after(2000, self._resume_updates)

    def _on_filter_change(self):
        """Cambia el filtro"""
        self.update_paused = True
        self.service_monitor.set_filter(self.filter_var.get())
        self._update_now()
        self.after(2000, self._resume_updates)

    def _on_search_change(self):
        """Callback cuando cambia la búsqueda"""
        self.update_paused = True

        if hasattr(self, '_search_timer'):
            self.after_cancel(self._search_timer)

        self._search_timer = self.after(500, self._do_search)

    def _do_search(self):
        """Ejecuta la búsqueda"""
        self._update_now()
        self.after(3000, self._resume_updates)

    def _update(self):
        """Actualiza la lista de servicios"""
        if not self.winfo_exists():
            return

        if self.update_paused:
            self.update_job = self.after(UPDATE_MS * 5, self._update)  # 10 segundos
            return

        self._update_now()
        self.update_job = self.after(UPDATE_MS * 5, self._update)  # 10 segundos

    def _update_now(self):
        """Actualiza inmediatamente"""
        if not self.winfo_exists():
            return

        # Actualizar estadísticas
        stats = self.service_monitor.get_stats()
        self.stats_label.configure(
            text=f"Total: {stats['total']} | "
                 f"Activos: {stats['active']} | "
                 f"Inactivos: {stats['inactive']} | "
                 f"Fallidos: {stats['failed']} | "
                 f"Autostart: {stats['enabled']}"
        )

        # Limpiar servicios anteriores
        for widget in self.service_frame.winfo_children():
            widget.destroy()

        # Obtener servicios
        search_query = self.search_var.get()
        if search_query:
            services = self.service_monitor.search_services(search_query)
        else:
            services = self.service_monitor.get_services()

        # Limitar a top 30
        services = services[:30]

        # Mostrar servicios
        for i, service in enumerate(services):
            self._create_service_row(service, i)

    def _create_service_row(self, service: dict, row: int):
        """Crea una fila para un servicio"""
        bg_color = COLORS['bg_dark'] if row % 2 == 0 else COLORS['bg_medium']
        row_frame = ctk.CTkFrame(self.service_frame, fg_color=bg_color)
        row_frame.pack(fill="x", pady=2)

        row_frame.grid_columnconfigure(0, weight=2, minsize=150)
        row_frame.grid_columnconfigure(1, weight=1, minsize=100)
        row_frame.grid_columnconfigure(2, weight=1, minsize=80)
        row_frame.grid_columnconfigure(3, weight=3, minsize=300)

        # Icono y nombre
        state_icon = "🟢" if service['active'] == 'active' else "🔴"
        state_color = COLORS[self.service_monitor.get_state_color(service['active'])]

        name_label = ctk.CTkLabel(
            row_frame,
            text=f"{state_icon} {service['name']}",
            text_color=state_color,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        )
        name_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Estado
        ctk.CTkLabel(
            row_frame,
            text=service['active'],
            text_color=state_color,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Autostart
        autostart_text = "✓" if service['enabled'] else "✗"
        autostart_color = COLORS['success'] if service['enabled'] else COLORS['text_dim']
        ctk.CTkLabel(
            row_frame,
            text=autostart_text,
            text_color=autostart_color,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).grid(row=0, column=2, sticky="n", padx=5, pady=5)

        # Botones de acción
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=3, sticky="ew", padx=5, pady=3)

        # Start/Stop
        if service['active'] == 'active':
            stop_btn = ctk.CTkButton(
                actions_frame,
                text="⏸",
                command=lambda s=service: self._stop_service(s),
                fg_color=COLORS['warning'],
                hover_color=COLORS['danger'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 14)
            )
            stop_btn.pack(side="left", padx=2)
        else:
            start_btn = ctk.CTkButton(
                actions_frame,
                text="▶",
                command=lambda s=service: self._start_service(s),
                fg_color=COLORS['success'],
                hover_color="#00aa00",
                width=40,
                height=25,
                font=(FONT_FAMILY, 14)
            )
            start_btn.pack(side="left", padx=2)

        # Restart
        restart_btn = ctk.CTkButton(
            actions_frame,
            text="🔄",
            command=lambda s=service: self._restart_service(s),
            fg_color=COLORS['primary'],
            width=40,
            height=25,
            font=(FONT_FAMILY, 12)
        )
        restart_btn.pack(side="left", padx=2)

        # Logs
        logs_btn = ctk.CTkButton(
            actions_frame,
            text="👁",
            command=lambda s=service: self._view_logs(s),
            fg_color=COLORS['bg_light'],
            width=40,
            height=25,
            font=(FONT_FAMILY, 12)
        )
        logs_btn.pack(side="left", padx=2)

        # Enable/Disable
        if service['enabled']:
            disable_btn = ctk.CTkButton(
                actions_frame,
                text="⚙",
                command=lambda s=service: self._disable_service(s),
                fg_color=COLORS['text_dim'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 12)
            )
            disable_btn.pack(side="left", padx=2)
        else:
            enable_btn = ctk.CTkButton(
                actions_frame,
                text="⚙",
                command=lambda s=service: self._enable_service(s),
                fg_color=COLORS['secondary'],
                width=40,
                height=25,
                font=(FONT_FAMILY, 12)
            )
            enable_btn.pack(side="left", padx=2)

    def _start_service(self, service: dict):
        """Inicia un servicio"""
        def do_start():
            success, message = self.service_monitor.start_service(service['name'])
            custom_msgbox(self, message, "Iniciar Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Iniciar servicio '{service['name']}'?",
            title="⚠️ Confirmar",
            on_confirm=do_start,
            on_cancel=None
        )

    def _stop_service(self, service: dict):
        """Detiene un servicio"""
        def do_stop():
            success, message = self.service_monitor.stop_service(service['name'])
            custom_msgbox(self, message, "Detener Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Detener servicio '{service['name']}'?\n\n"
                 f"El servicio dejará de funcionar.",
            title="⚠️ Confirmar",
            on_confirm=do_stop,
            on_cancel=None
        )

    def _restart_service(self, service: dict):
        """Reinicia un servicio"""
        def do_restart():
            success, message = self.service_monitor.restart_service(service['name'])
            custom_msgbox(self, message, "Reiniciar Servicio")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Reiniciar servicio '{service['name']}'?",
            title="⚠️ Confirmar",
            on_confirm=do_restart,
            on_cancel=None
        )

    def _view_logs(self, service: dict):
        """Muestra logs de un servicio"""
        logs = self.service_monitor.get_logs(service['name'], lines=30)

        # Crear ventana de logs
        logs_window = ctk.CTkToplevel(self)
        logs_window.title(f"Logs: {service['name']}")
        logs_window.geometry("700x500")

        # Textbox con logs
        textbox = ctk.CTkTextbox(
            logs_window,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wrap="word"
        )
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("1.0", logs)
        textbox.configure(state="disabled")

        # Botón cerrar
        close_btn = make_futuristic_button(
            logs_window,
            text="Cerrar",
            command=logs_window.destroy,
            width=15,
            height=6
        )
        close_btn.pack(pady=10)

    def _enable_service(self, service: dict):
        """Habilita autostart"""
        def do_enable():
            success, message = self.service_monitor.enable_service(service['name'])
            custom_msgbox(self, message, "Habilitar Autostart")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Habilitar autostart para '{service['name']}'?\n\n"
                 f"El servicio se iniciará automáticamente al arrancar.",
            title="⚠️ Confirmar",
            on_confirm=do_enable,
            on_cancel=None
        )

    def _disable_service(self, service: dict):
        """Deshabilita autostart"""
        def do_disable():
            success, message = self.service_monitor.disable_service(service['name'])
            custom_msgbox(self, message, "Deshabilitar Autostart")
            if success:
                self._force_update()

        confirm_dialog(
            parent=self,
            text=f"¿Deshabilitar autostart para '{service['name']}'?\n\n"
                 f"El servicio NO se iniciará automáticamente al arrancar.",
            title="⚠️ Confirmar",
            on_confirm=do_disable,
            on_cancel=None
        )

    def _force_update(self):
        """Fuerza actualización inmediata"""
        self.update_paused = False
        self._update_now()

    def _resume_updates(self):
        """Reanuda actualizaciones"""
        self.update_paused = False
```

## File: ui/windows/theme_selector.py
```python
"""
Ventana de selección de temas
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from config.themes import get_available_themes, get_theme, save_selected_theme, load_selected_theme
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox, confirm_dialog
import sys
import os

class ThemeSelector(ctk.CTkToplevel):
    """Ventana de selección de temas"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configurar ventana
        self.title("Selector de Temas")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        # Tema actualmente seleccionado
        self.current_theme = load_selected_theme()
        self.selected_theme_var = ctk.StringVar(value=self.current_theme)
        
        # Crear interfaz
        self._create_ui()
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="SELECTOR DE TEMAS",
            on_close=self.destroy,
            status_text="Elige un tema y reinicia el dashboard para aplicarlo",
        )
        
        # Área de scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas y scrollbar
        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Crear tarjetas de temas
        self._create_theme_cards(inner)
        
        # Botones inferiores
        self._create_bottom_buttons(main)
    
    def _create_theme_cards(self, parent):
        """Crea las tarjetas de cada tema"""
        themes = get_available_themes()
        
        for theme_id, theme_name in themes:
            theme_data = get_theme(theme_id)
            colors = theme_data["colors"]
            
            # Frame de la tarjeta
            is_current = (theme_id == self.current_theme)
            border_color = COLORS['success'] if is_current else COLORS['primary']
            border_width = 3 if is_current else 2
            
            card = ctk.CTkFrame(
                parent,
                fg_color=COLORS['bg_dark'],
                border_width=border_width,
                border_color=border_color
            )
            card.pack(fill="x", pady=8, padx=10)
            
            # Radiobutton para seleccionar
            radio = ctk.CTkRadioButton(
                card,
                text=theme_name,
                variable=self.selected_theme_var,
                value=theme_id,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
                command=lambda: self._on_theme_change()
            )
            radio.pack(anchor="w", padx=15, pady=(10, 5))
            StyleManager.style_radiobutton_ctk(radio)
            
            # Indicador de tema actual
            if is_current:
                current_label = ctk.CTkLabel(
                    card,
                    text="✓ TEMA ACTUAL",
                    text_color=COLORS['success'],
                    font=(FONT_FAMILY, 10, "bold")
                )
                current_label.pack(anchor="w", padx=15, pady=(0, 5))
            
            # Frame de preview de colores
            preview_frame = ctk.CTkFrame(card, fg_color=COLORS['bg_medium'])
            preview_frame.pack(fill="x", padx=15, pady=(5, 10))
            
            # Mostrar colores principales
            color_samples = [
                ("Principal", colors['primary']),
                ("Secundario", colors['secondary']),
                ("Éxito", colors['success']),
                ("Advertencia", colors['warning']),
                ("Peligro", colors['danger']),
                ("Fondo oscuro", colors['bg_dark']),
                ("Fondo medio", colors['bg_medium']),
                ("Fondo claro", colors['bg_light']),
                ("Texto", colors['text']),
                ("Bordes", colors['border'])
            ]
            
            for i, (label, color) in enumerate(color_samples):
                color_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
                color_frame.grid(row=0, column=i, padx=5, pady=5)
                
                # Cuadrado de color
                color_box = ctk.CTkFrame(
                    color_frame,
                    width=40,
                    height=40,
                    fg_color=color,
                    border_width=1,
                    border_color=COLORS['text']
                )
                color_box.pack()
                color_box.pack_propagate(False)
                
                # Label
                color_label = ctk.CTkLabel(
                    color_frame,
                    text=label,
                    text_color=COLORS['text'],
                    font=(FONT_FAMILY, 9)
                )
                color_label.pack(pady=(2, 0))
    
    def _create_bottom_buttons(self, parent):
        """Crea los botones inferiores"""
        bottom = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)
        
        # Botón aplicar
        apply_btn = make_futuristic_button(
            bottom,
            text="Aplicar y Reiniciar",
            command=self._apply_theme,
            width=20,
            height=6
        )
        apply_btn.pack(side="right", padx=5)
    
    def _on_theme_change(self):
        """Callback cuando se selecciona un tema"""
        # Simplemente actualiza la variable, no aplica aún
        pass
    
    def _apply_theme(self):
        """Aplica el tema seleccionado y reinicia la aplicación"""
        selected = self.selected_theme_var.get()
        
        if selected == self.current_theme:
            custom_msgbox(
                self,
                "Este tema ya está activo.\nNo es necesario reiniciar.",
                "Tema Actual"
            )
            return
        
        # Guardar tema seleccionado
        save_selected_theme(selected)
        
        # Mostrar confirmación y reiniciar
        theme_name = get_theme(selected)["name"]
        

        
        def do_restart():
            """Reinicia la aplicación"""
            
            
            # Cerrar ventana de temas
            self.destroy()
            
            # Obtener el script principal
            python = sys.executable
            script = os.path.abspath(sys.argv[0])
            
            # Cerrar aplicación actual
            self.master.quit()
            self.master.destroy()
            
            # Reiniciar con os.execv (reemplaza el proceso actual)
            os.execv(python, [python, script] + sys.argv[1:])
        
        # Confirmar antes de reiniciar
        confirm_dialog(
            parent=self,
            text=f"Tema '{theme_name}' guardado.\n\n¿Reiniciar ahora para aplicar los cambios?",
            title="🔄 Aplicar Tema",
            on_confirm=do_restart,
            on_cancel=self.destroy
        )
```

## File: ui/windows/usb.py
```python
"""
Ventana de monitoreo de dispositivos USB
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class USBWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de dispositivos USB"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.system_utils = SystemUtils()
        self.device_widgets = []
        
        self.title("Monitor USB")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        self._create_ui()
        self._refresh_devices()
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="DISPOSITIVOS USB",
            on_close=self.destroy,
        )
        # Botón Actualizar
        refresh_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        refresh_bar.pack(fill="x", padx=10, pady=(0, 5))
        make_futuristic_button(
            refresh_bar,
            text="Actualizar",
            command=self._refresh_devices,
            width=15,
            height=5
        ).pack(side="right")
        
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=self.canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.devices_frame = ctk.CTkFrame(self.canvas, fg_color=COLORS['bg_medium'])
        self.canvas.create_window(
            (0, 0),
            window=self.devices_frame,
            anchor="nw",
            width=DSI_WIDTH-50
        )
        
        self.devices_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
    
    def _refresh_devices(self):
        """Refresca la lista de dispositivos USB"""
        for widget in self.device_widgets:
            widget.destroy()
        self.device_widgets.clear()
        
        storage_devices = self.system_utils.list_usb_storage_devices()
        other_devices = self.system_utils.list_usb_other_devices()
        
        logger.debug(f"[USBWindow] Dispositivos detectados: {len(storage_devices)} almacenamiento, {len(other_devices)} otros")
        
        if storage_devices:
            self._create_storage_section(storage_devices)
        
        if other_devices:
            self._create_other_devices_section(other_devices)
        
        if not storage_devices and not other_devices:
            no_devices = ctk.CTkLabel(
                self.devices_frame,
                text="No se detectaron dispositivos USB",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                justify="center"
            )
            no_devices.pack(pady=50)
            self.device_widgets.append(no_devices)
    
    def _create_storage_section(self, storage_devices: list):
        """Crea la sección de almacenamiento USB"""
        title = ctk.CTkLabel(
            self.devices_frame,
            text="ALMACENAMIENTO USB",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(10, 10), padx=10)
        self.device_widgets.append(title)
        
        for idx, device in enumerate(storage_devices):
            self._create_storage_device_widget(device, idx)
    
    def _create_storage_device_widget(self, device: dict, index: int):
        """Crea widget para un dispositivo de almacenamiento"""
        device_frame = ctk.CTkFrame(
            self.devices_frame,
            fg_color=COLORS['bg_dark'],
            border_width=2,
            border_color=COLORS['success']
        )
        device_frame.pack(fill="x", pady=5, padx=10)
        self.device_widgets.append(device_frame)
        
        name = device.get('name', 'USB Disk')
        size = device.get('size', '?')
        dev_type = device.get('type', 'disk')
        
        header = ctk.CTkLabel(
            device_frame,
            text=f"💾 {name} ({dev_type}) - {size}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        )
        header.pack(anchor="w", padx=10, pady=(10, 5))
        
        dev_path = device.get('dev', '?')
        info = ctk.CTkLabel(
            device_frame,
            text=f"Dispositivo: {dev_path}",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        info.pack(anchor="w", padx=10, pady=(0, 5))
        
        eject_btn = make_futuristic_button(
            device_frame,
            text="Expulsar",
            command=lambda d=device: self._eject_device(d),
            width=15,
            height=4
        )
        eject_btn.pack(anchor="w", padx=20, pady=(5, 10))
        
        children = device.get('children', [])
        if children:
            for child in children:
                self._create_partition_widget(device_frame, child)
    
    def _create_partition_widget(self, parent, partition: dict):
        """Crea widget para una partición"""
        name = partition.get('name', '?')
        mount = partition.get('mount')
        size = partition.get('size', '?')
        
        part_text = f"  └─ Partición: {name} ({size})"
        if mount:
            part_text += f" | 📁 Montado en: {mount}"
        else:
            part_text += " | No montado"
        
        part_label = ctk.CTkLabel(
            parent,
            text=part_text,
            text_color=COLORS['primary'] if mount else COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=DSI_WIDTH - 80,
            anchor="w",
            justify="left"
        )
        part_label.pack(anchor="w", padx=30, pady=2)
    
    def _create_other_devices_section(self, other_devices: list):
        """Crea la sección de otros dispositivos USB"""
        title = ctk.CTkLabel(
            self.devices_frame,
            text="OTROS DISPOSITIVOS USB",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
        )
        title.pack(anchor="w", pady=(20, 10), padx=10)
        self.device_widgets.append(title)
        
        for idx, device_line in enumerate(other_devices):
            self._create_other_device_widget(device_line, idx)
    
    def _create_other_device_widget(self, device_line: str, index: int):
        """Crea widget para otro dispositivo USB"""
        device_info = self._parse_lsusb_line(device_line)
        
        device_frame = ctk.CTkFrame(
            self.devices_frame,
            fg_color=COLORS['bg_dark'],
            border_width=1,
            border_color=COLORS['primary']
        )
        device_frame.pack(fill="x", pady=3, padx=10)
        self.device_widgets.append(device_frame)
        
        inner = ctk.CTkFrame(device_frame, fg_color=COLORS['bg_dark'])
        inner.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            inner,
            text=f"#{index + 1}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            width=30
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            inner,
            text=device_info['bus'],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            inner,
            text=device_info['description'],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            wraplength=DSI_WIDTH - 200,
            anchor="w",
            justify="left"
        ).pack(side="left", padx=5, fill="x", expand=True)
    
    def _parse_lsusb_line(self, line: str) -> dict:
        """Parsea una línea de lsusb"""
        parts = line.split()
        
        try:
            bus_idx = parts.index("Bus") + 1
            bus = f"Bus {parts[bus_idx]}"
            
            dev_idx = parts.index("Device") + 1
            device_num = parts[dev_idx].rstrip(':')
            bus += f" Dev {device_num}"
            
            id_idx = parts.index("ID") + 2
            description = " ".join(parts[id_idx:])
            
            if len(description) > 50:
                description = description[:47] + "..."
            
        except (ValueError, IndexError):
            bus = "Bus ?"
            description = line
        
        return {'bus': bus, 'description': description}
    
    def _eject_device(self, device: dict):
        """Expulsa un dispositivo USB"""
        device_name = device.get('name', 'dispositivo')
        
        logger.info(f"[USBWindow] Intentando expulsar: '{device_name}' ({device.get('dev', '?')})")
        
        success, message = self.system_utils.eject_usb_device(device)
        
        if success:
            logger.info(f"[USBWindow] Expulsión exitosa: '{device_name}'")
            custom_msgbox(
                self,
                f"✅ {device_name}\n\n{message}\n\nAhora puedes desconectar el dispositivo de forma segura.",
                "Expulsión Exitosa"
            )
            self._refresh_devices()
        else:
            logger.error(f"[USBWindow] Error expulsando '{device_name}': {message}")
            custom_msgbox(
                self,
                f"❌ Error al expulsar {device_name}:\n\n{message}",
                "Error"
            )
```

## File: ui/widgets/dialogs.py
```python
"""
Diálogos y ventanas modales personalizadas
"""
import customtkinter as ctk
from ui.styles import make_futuristic_button
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES
import subprocess
import threading


def custom_msgbox(parent, text: str, title: str = "Info") -> None:
    """
    Muestra un cuadro de mensaje personalizado
    
    Args:
        parent: Ventana padre
        text: Texto del mensaje
        title: Título del diálogo
    """
    popup = ctk.CTkToplevel(parent)
    popup.overrideredirect(True)
    
    # Contenedor
    frame = ctk.CTkFrame(popup)
    frame.pack(fill="both", expand=True)
    
    # Título
    title_lbl = ctk.CTkLabel(
        frame, 
        text=title,
        text_color=COLORS['primary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
    )
    title_lbl.pack(anchor="center", pady=(0, 10))
    
    # Texto
    text_lbl = ctk.CTkLabel(
        frame, 
        text=text,
        text_color=COLORS['text'],
        font=(FONT_FAMILY, FONT_SIZES['medium']),
        compound="left",
        wraplength=800
    )
    text_lbl.pack(anchor="center", pady=(0, 15))
    
    # Botón OK
    def _close_msgbox():
        try:
            popup.grab_release()
        except Exception:
            pass
        popup.destroy()

    btn = make_futuristic_button(
        frame, 
        text="OK",
        command=_close_msgbox,
        width=15, 
        height=6, 
        font_size=16
    )
    btn.pack()
    
    # Calcular tamaño
    popup.update_idletasks()
    
    w = popup.winfo_reqwidth()
    h = popup.winfo_reqheight()
    
    max_w = parent.winfo_screenwidth() - 40
    max_h = parent.winfo_screenheight() - 40
    
    w = min(w, max_w)
    h = min(h, max_h)
    
    # Centrar
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
    
    popup.geometry(f"{w}x{h}+{x}+{y}")
    
    popup.lift()
    popup.after(150, popup.focus_set)
    popup.grab_set()


def confirm_dialog(parent, text: str, title: str = "Confirmar", 
                   on_confirm=None, on_cancel=None) -> None:
    """
    Muestra un diálogo de confirmación
    
    Args:
        parent: Ventana padre
        text: Texto del mensaje
        title: Título del diálogo
        on_confirm: Callback al confirmar
        on_cancel: Callback al cancelar
    """
    popup = ctk.CTkToplevel(parent)
    popup.overrideredirect(True)
    
    frame = ctk.CTkFrame(popup)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Título
    title_lbl = ctk.CTkLabel(
        frame, 
        text=title,
        text_color=COLORS['primary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold")
    )
    title_lbl.pack(anchor="center", pady=(0, 10))
    
    # Texto
    text_lbl = ctk.CTkLabel(
        frame, 
        text=text,
        text_color=COLORS['text'],
        font=(FONT_FAMILY, FONT_SIZES['medium']),
        wraplength=600
    )
    text_lbl.pack(anchor="center", pady=(0, 20))
    
    # Botones
    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack()
    
    def _on_confirm():
        try:
            popup.grab_release()
        except Exception:
            pass
        popup.destroy()
        if on_confirm:
            on_confirm()
    
    def _on_cancel():
        try:
            popup.grab_release()
        except Exception:
            pass
        popup.destroy()
        if on_cancel:
            on_cancel()
    
    btn_confirm = make_futuristic_button(
        btn_frame,
        text="Confirmar",
        command=_on_confirm,
        width=15,
        height=8,
        font_size=16
    )
    btn_confirm.pack(side="left", padx=5)
    
    btn_cancel = make_futuristic_button(
        btn_frame,
        text="Cancelar",
        command=_on_cancel,
        width=20,
        height=10,
        font_size=16
    )
    btn_cancel.pack(side="left", padx=5)
    
    # Centrar
    popup.update_idletasks()
    w = popup.winfo_reqwidth()
    h = popup.winfo_reqheight()
    
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
    
    popup.geometry(f"{w}x{h}+{x}+{y}")
    
    popup.lift()
    popup.after(150, popup.focus_set)
    popup.grab_set()
def terminal_dialog(parent, script_path, title="Consola de Sistema", on_close=None):
    popup = ctk.CTkToplevel(parent)
    popup.overrideredirect(True)
    popup.configure(fg_color=COLORS['bg_dark'])
    
    # Tamaño para pantalla 800x480
    w, h = 720, 400
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (w // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")

    frame = ctk.CTkFrame(popup, fg_color=COLORS['bg_dark'], border_width=2, border_color=COLORS['primary'])
    frame.pack(fill="both", expand=True, padx=2, pady=2)

    ctk.CTkLabel(frame, text=title, font=(FONT_FAMILY, 18, "bold"), text_color=COLORS['secondary']).pack(pady=5)
    def _on_close():
        try:
            popup.grab_release()
        except Exception:
            pass
        popup.destroy()
        if on_close:
            on_close()
    console = ctk.CTkTextbox(frame, fg_color="black", text_color="#00FF00", font=("Courier New", 12))
    console.pack(fill="both", expand=True, padx=10, pady=5)

    btn_close = ctk.CTkButton(frame, text="Cerrar", command=_on_close, state="disabled")
    btn_close.pack(pady=10)

    def run_command():
        process = subprocess.Popen(["bash", script_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            popup.after(0, lambda l=line: console.insert("end", l))
            popup.after(0, lambda: console.see("end"))
        process.wait()
        popup.after(0, lambda: btn_close.configure(state="normal"))

    threading.Thread(target=run_command, daemon=True).start()
    popup.grab_set()
```

## File: ui/windows/network.py
```python
"""
Ventana de monitoreo de red
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS, NET_INTERFACE)
from ui.styles import StyleManager, make_futuristic_button, make_window_header
from ui.widgets import GraphWidget
from core.network_monitor import NetworkMonitor
from utils.system_utils import SystemUtils

_COL_W   = (DSI_WIDTH - 70) // 2
_GRAPH_H = 110


class NetworkWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de red"""

    def __init__(self, parent, network_monitor: NetworkMonitor):
        super().__init__(parent)
        self.network_monitor = network_monitor
        self.widgets = {}
        self.graphs  = {}
        self._interface_update_counter = 0

        self.title("Monitor de Red")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        self._create_ui()
        self._update()

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main, title="MONITOR DE RED", on_close=self.destroy,
            status_text="Detectando interfaz...")

        # Scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")

        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Grid 2 columnas dentro del inner scrollable
        grid = ctk.CTkFrame(inner, fg_color=COLORS['bg_medium'])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        # Fila 0: DESCARGA | SUBIDA  (con gráfica)
        self._create_traffic_cell(grid, 0, 0, "DESCARGA", "download")
        self._create_traffic_cell(grid, 0, 1, "SUBIDA",   "upload")

        # Fila 1: INTERFACES | SPEEDTEST  (informativas)
        self._create_interfaces_cell(grid, 1, 0)
        self._create_speedtest_cell(grid,  1, 1)

    # ── Celdas ───────────────────────────────────────────────────────────────

    def _create_traffic_cell(self, parent, row, col, title, key):
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        lbl = ctk.CTkLabel(cell, text=title, text_color=COLORS['primary'],
                           font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), anchor="w")
        lbl.pack(anchor="w", padx=8, pady=(6, 0))

        val = ctk.CTkLabel(cell, text="0.00 MB/s", text_color=COLORS['primary'],
                           font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"), anchor="e")
        val.pack(anchor="e", padx=8, pady=(0, 2))

        graph = GraphWidget(cell, width=_COL_W - 16, height=_GRAPH_H)
        graph.pack(padx=4, pady=(0, 6))

        self.widgets[f"{key}_label"] = lbl
        self.widgets[f"{key}_value"] = val
        self.graphs[key] = graph

    def _create_interfaces_cell(self, parent, row, col):
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        ctk.CTkLabel(cell, text="INTERFACES", text_color=COLORS['success'],
                     font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), anchor="w"
                     ).pack(anchor="w", padx=8, pady=(6, 4))

        self.interfaces_container = ctk.CTkFrame(cell, fg_color="transparent")
        self.interfaces_container.pack(fill="both", expand=True, padx=4, pady=(0, 6))
        self._update_interfaces()

    def _create_speedtest_cell(self, parent, row, col):
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        ctk.CTkLabel(cell, text="SPEEDTEST", text_color=COLORS['primary'],
                     font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), anchor="w"
                     ).pack(anchor="w", padx=8, pady=(6, 4))

        self.speedtest_result = ctk.CTkLabel(
            cell, text="Pulsa 'Test' para\ncomenzar",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            justify="left", wraplength=_COL_W - 20)
        self.speedtest_result.pack(anchor="w", padx=8, pady=(0, 4))

        self.speedtest_btn = make_futuristic_button(
            cell, text="Ejecutar Test", command=self._run_speedtest, width=15, height=5)
        self.speedtest_btn.pack(pady=(0, 8))

    # ── Interfaces ───────────────────────────────────────────────────────────

    def _update_interfaces(self):
        for w in self.interfaces_container.winfo_children():
            w.destroy()

        interfaces = SystemUtils.get_interfaces_ips()
        if not interfaces:
            ctk.CTkLabel(self.interfaces_container, text="Sin interfaces",
                         text_color=COLORS['warning'],
                         font=(FONT_FAMILY, FONT_SIZES['small'])).pack(pady=5)
            return

        for iface, ip in sorted(interfaces.items()):
            if iface.startswith('tun'):
                color, icon = COLORS['success'], "🔒"
            elif iface.startswith(('eth', 'enp')):
                color, icon = COLORS['primary'], "🌐"
            elif iface.startswith(('wlan', 'wlp')):
                color, icon = COLORS['warning'], "\uf0eb"
            else:
                color, icon = COLORS['text'], "•"

            ctk.CTkLabel(self.interfaces_container,
                         text=f"{icon} {iface}: {ip}",
                         text_color=color,
                         font=(FONT_FAMILY, FONT_SIZES['small']),
                         anchor="w", wraplength=_COL_W - 20
                         ).pack(anchor="w", pady=1, padx=4)

    # ── Speedtest ─────────────────────────────────────────────────────────────

    def _run_speedtest(self):
        result = self.network_monitor.get_speedtest_result()
        if result['status'] == 'running':
            return
        self.network_monitor.reset_speedtest()
        self.network_monitor.run_speedtest()
        self.speedtest_btn.configure(state="disabled")
        self.speedtest_result.configure(text="Ejecutando...", text_color=COLORS['warning'])

    def _update_speedtest(self):
        result = self.network_monitor.get_speedtest_result()
        status = result['status']
        if status == 'idle':
            self.speedtest_result.configure(
                text="Pulsa 'Test' para\ncomenzar", text_color=COLORS['text'])
            self.speedtest_btn.configure(state="normal")
        elif status == 'running':
            self.speedtest_result.configure(text="Ejecutando...", text_color=COLORS['warning'])
            self.speedtest_btn.configure(state="disabled")
        elif status == 'done':
            self.speedtest_result.configure(
                text=f"Ping: {result['ping']} ms\n↓ {result['download']:.1f} MB/s\n↑ {result['upload']:.1f} MB/s",
                text_color=COLORS['success'])
            self.speedtest_btn.configure(state="normal")
        elif status == 'timeout':
            self.speedtest_result.configure(text="Timeout", text_color=COLORS['danger'])
            self.speedtest_btn.configure(state="normal")
        elif status == 'error':
            self.speedtest_result.configure(
                text="Error al ejecutar\nel test", text_color=COLORS['danger'])
            self.speedtest_btn.configure(state="normal")

    # ── Update loop ───────────────────────────────────────────────────────────

    def _update(self):
        if not self.winfo_exists():
            return

        stats = self.network_monitor.get_current_stats(NET_INTERFACE)
        self.network_monitor.update_history(stats)
        self.network_monitor.update_dynamic_scale()
        history = self.network_monitor.get_history()

        self._header.status_label.configure(
            text=f"{stats['interface']}  ·  ↓{stats['download_mb']:.2f}  ↑{stats['upload_mb']:.2f} MB/s")

        dl_color = self.network_monitor.net_color(stats['download_mb'])
        self.widgets['download_label'].configure(text_color=dl_color)
        self.widgets['download_value'].configure(
            text=f"{stats['download_mb']:.2f} MB/s", text_color=dl_color)
        self.graphs['download'].update(history['download'], history['dynamic_max'], dl_color)

        ul_color = self.network_monitor.net_color(stats['upload_mb'])
        self.widgets['upload_label'].configure(text_color=ul_color)
        self.widgets['upload_value'].configure(
            text=f"{stats['upload_mb']:.2f} MB/s", text_color=ul_color)
        self.graphs['upload'].update(history['upload'], history['dynamic_max'], ul_color)

        self._update_speedtest()

        self._interface_update_counter += 1
        if self._interface_update_counter >= 5:
            self._update_interfaces()
            self._interface_update_counter = 0

        self.after(UPDATE_MS, self._update)
```

## File: ui/windows/homebridge.py
```python
"""
Ventana de control de dispositivos Homebridge
Muestra enchufes e interruptores y permite encenderlos / apagarlos
"""
import threading
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from ui.styles import StyleManager, make_futuristic_button, make_window_header, make_homebridge_switch
from ui.widgets import custom_msgbox
from core.homebridge_monitor import HomebridgeMonitor
from utils.logger import get_logger

logger = get_logger(__name__)

# Intervalo de refresco de la ventana (ms)
HB_UPDATE_MS = 5000


class HomebridgeWindow(ctk.CTkToplevel):
    """Ventana de control de dispositivos Homebridge."""

    def __init__(self, parent, homebridge_monitor: HomebridgeMonitor):
        super().__init__(parent)
        self.hb = homebridge_monitor
        self._accessories = []
        self._update_job = None
        self._busy = False  # evita peticiones simultáneas

        # Configurar ventana
        self.title("Homebridge")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        self._create_ui()
        self._schedule_update()
        logger.info("[HomebridgeWindow] Ventana abierta")

    # ── Interfaz ──────────────────────────────────────────────────────────────

    def _create_ui(self):
        """Construye la interfaz completa."""
        self.main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        self.main.pack(fill="both", expand=True, padx=5, pady=5)

        # ── Header unificado ──────────────────────────────────────────────────
        self._header = make_window_header(
            self.main,
            title="HOMEBRIDGE",
            on_close=self._on_close,
            status_text="Conectando...",
        )

        # ── Barra de estado ───────────────────────────────────────────────────
        status_bar = ctk.CTkFrame(self.main, fg_color=COLORS['bg_dark'])
        status_bar.pack(fill="x", padx=5, pady=(0, 4))
        self._status_label = ctk.CTkLabel(
            status_bar,
            text="",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            anchor="w",
        )
        self._status_label.pack(pady=4, padx=10, fill="x")

        # ── Área scrollable de dispositivos ───────────────────────────────────
        scroll_container = ctk.CTkFrame(self.main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        max_height = DSI_HEIGHT - 220
        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=max_height,
        )
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30,
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        self._device_frame = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window(
            (0, 0), window=self._device_frame, anchor="nw", width=DSI_WIDTH - 50
        )
        self._device_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        # ── Botón Refrescar ───────────────────────────────────────────────────
        bottom = ctk.CTkFrame(self.main, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=8, padx=10)

        make_futuristic_button(
            bottom,
            text="⟳  Refrescar",
            command=self._force_refresh,
            width=15,
            height=6,
        ).pack(side="left", padx=5)

    # ── Actualización ─────────────────────────────────────────────────────────

    def _schedule_update(self):
        """Programa la siguiente actualización."""
        self._update_job = self.after(100, self._fetch_and_render)

    def _force_refresh(self):
        """Fuerza un refresco inmediato."""
        if self._update_job:
            self.after_cancel(self._update_job)
        self._fetch_and_render()

    def _fetch_and_render(self):
        """Lanza la petición en background y actualiza la UI cuando termina."""
        if self._busy:
            return
        self._busy = True
        self._set_status("Actualizando...")

        def fetch():
            accessories = self.hb.get_accessories()
            self.after(0, lambda: self._render(accessories))

        threading.Thread(target=fetch, daemon=True, name="HB-Fetch").start()

    def _render(self, accessories):
        """Actualiza la lista de dispositivos en el hilo principal."""
        self._accessories = accessories
        self._busy = False

        # ── Header status ──────────────────────────────────────────────────────
        if self.hb.is_reachable():
            on_count = sum(1 for a in accessories if a["on"])
            total = len(accessories)
            header_status = f"{on_count}/{total} encendidos"
            self._set_status(
                f"{total} dispositivo{'s' if total != 1 else ''} encontrado{'s' if total != 1 else ''}"
            )
        else:
            header_status = "⚠ Sin conexión"
            self._set_status("No se pudo conectar con Homebridge — verifica host y credenciales")

        # Actualizar status del header
        try:
            self._header.status_label.configure(text=header_status)
        except Exception:
            pass

        # ── Redibujar grid 2 columnas ──────────────────────────────────────────
        for widget in self._device_frame.winfo_children():
            widget.destroy()

        if not accessories:
            msg = (
                "Sin conexión con Homebridge" if not self.hb.is_reachable()
                else "No se encontraron enchufes ni interruptores"
            )
            ctk.CTkLabel(
                self._device_frame,
                text=msg,
                text_color=COLORS.get('warning', '#ffaa00'),
                font=(FONT_FAMILY, FONT_SIZES['medium']),
            ).pack(pady=30)
        else:
            self._device_frame.grid_columnconfigure(0, weight=1, uniform="col")
            self._device_frame.grid_columnconfigure(1, weight=1, uniform="col")
            for idx, acc in enumerate(accessories):
                self._create_device_card(acc, idx // 2, idx % 2)

        # Programar siguiente actualización
        self._update_job = self.after(HB_UPDATE_MS, self._fetch_and_render)

    def _create_device_card(self, acc: dict, grid_row: int, grid_col: int):
        """Tarjeta adaptada al tipo de dispositivo."""
        dev_type = acc.get("type", "switch")
        is_fault = acc.get("fault", False)
        disabled = is_fault or acc.get("inactive", False)

        card = ctk.CTkFrame(
            self._device_frame,
            fg_color=COLORS['bg_dark'],
            corner_radius=8,
        )
        card.grid(row=grid_row, column=grid_col, sticky="nsew", padx=4, pady=4)

        if disabled:
            ctk.CTkLabel(
                card, text="⚠  FALLO",
                text_color=COLORS.get('danger', '#ff4444'),
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            ).pack(pady=(10, 0))
        else:
            ctk.CTkFrame(card, fg_color="transparent", height=10).pack()

        if dev_type in ("switch", "light"):
            self._card_switch(card, acc, disabled)
        elif dev_type == "thermostat":
            self._card_thermostat(card, acc, disabled)
        elif dev_type == "sensor":
            self._card_sensor(card, acc)
        elif dev_type == "blind":
            self._card_blind(card, acc, disabled)

    def _card_switch(self, card, acc, disabled):
        """Switch ON/OFF (enchufe, interruptor, luz básica)."""
    # ── Bloquear por nombre ──────────────────────────────
        blocked_names = ["Rpi5"]  # nombres a bloquear
        read_only = acc["displayName"] in blocked_names
        effective_disabled = disabled and not read_only  # mantén fallo/desactivado real

        def on_toggle(new_state, uid=acc["uniqueId"]):
            if read_only:
                # Solo mostrar mensaje o ignorar
                custom_msgbox(
                    parent=self, 
                    title="Aviso", 
                    text=f"El dispositivo '{acc['displayName']}' no puede ser manipulado.",
                )
                return
            self._toggle(uid, new_state)

        sw = make_homebridge_switch(
            card,
            text=acc["displayName"],
            command=on_toggle,
            is_on=acc["on"],
            disabled=disabled,
        )
        sw.pack(padx=16, pady=(8, 18))

    def _card_thermostat(self, card, acc, disabled):
        """Termostato: temperatura actual + botones +/- para objetivo."""
        ctk.CTkLabel(
            card,
            text=acc["displayName"],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
        ).pack(pady=(4, 0))

        ctk.CTkLabel(
            card,
            text=f"Actual: {acc['current_temp']:.1f}°C",
            text_color=COLORS.get('primary', '#00ffff'),
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
        ).pack()

        target_frame = ctk.CTkFrame(card, fg_color="transparent")
        target_frame.pack(pady=(4, 12))

        target_var = ctk.StringVar(value=f"{acc['target_temp']:.1f}°C")

        ctk.CTkLabel(
            target_frame, text="Objetivo:",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
        ).pack(side="left", padx=4)

        target_lbl = ctk.CTkLabel(
            target_frame, textvariable=target_var,
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
        )
        target_lbl.pack(side="left", padx=4)

        uid   = acc["uniqueId"]
        _temp = [acc["target_temp"]]  # mutable closure

        def change(delta):
            if disabled:
                return
            _temp[0] = round(_temp[0] + delta, 1)
            target_var.set(f"{_temp[0]:.1f}°C")
            threading.Thread(
                target=lambda: self.hb.set_target_temp(uid, _temp[0]),
                daemon=True, name="HB-SetTemp"
            ).start()

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=(0, 12))

        for label, delta in [("  −  ", -0.5), ("  +  ", +0.5)]:
            make_futuristic_button(
                btn_frame, text=label,
                command=lambda d=delta: change(d),
                width=8, height=5,
            ).pack(side="left", padx=4)

    def _card_sensor(self, card, acc):
        """Sensor de temperatura / humedad (solo lectura)."""
        ctk.CTkLabel(
            card,
            text=acc["displayName"],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
        ).pack(pady=(4, 0))

        if acc.get("temp") is not None:
            ctk.CTkLabel(
                card,
                text=f"🌡  {acc['temp']:.1f}°C",
                text_color=COLORS.get('primary', '#00ffff'),
                font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold"),
            ).pack(pady=4)

        if acc.get("humidity") is not None:
            ctk.CTkLabel(
                card,
                text=f"💧  {acc['humidity']:.0f}%",
                text_color=COLORS.get('secondary', '#aaaaff'),
                font=(FONT_FAMILY, FONT_SIZES['large']),
            ).pack(pady=(0, 12))

    def _card_blind(self, card, acc, disabled):
        """Persiana / estor con barra de posición."""
        ctk.CTkLabel(
            card,
            text=acc["displayName"],
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
        ).pack(pady=(4, 0))

        pos_var = ctk.IntVar(value=acc["position"])

        ctk.CTkLabel(
            card,
            text=f"Posición: {acc['position']}%",
            text_color=COLORS.get('primary', '#00ffff'),
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
        ).pack()

        # Barra visual (solo lectura — las persianas se controlan desde HomeKit)
        ctk.CTkProgressBar(
            card,
            variable=pos_var,
            progress_color=COLORS.get('primary', '#00ffff'),
            fg_color=COLORS['bg_light'],
            width=140, height=12,
        ).pack(pady=(4, 12))
    # ── Acciones ──────────────────────────────────────────────────────────────

    def _toggle(self, unique_id: str, turn_on: bool):
        """Envía el comando ON/OFF al dispositivo en background."""
        def send():
            ok = self.hb.toggle(unique_id, turn_on)
            if ok:
                # Refresca inmediatamente para reflejar el nuevo estado
                self.after(500, self._force_refresh)
            else:
                self.after(
                    0,
                    lambda: custom_msgbox(
                        self, "Error",
                        "No se pudo enviar el comando al dispositivo.\n"
                        "Verifica la conexión con Homebridge.",
                        tipo="error"
                    )
                )

        threading.Thread(target=send, daemon=True, name="HB-Toggle").start()

    def _set_status(self, text: str):
        """Actualiza la barra de estado inferior."""
        try:
            self._status_label.configure(text=text)
        except Exception:
            pass

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _on_close(self):
        """Cancela actualizaciones pendientes y cierra la ventana."""
        if self._update_job:
            self.after_cancel(self._update_job)
        logger.info("[HomebridgeWindow] Ventana cerrada")
        self.destroy()
```

## File: ui/windows/launchers.py
```python
"""
Ventana de lanzadores de scripts
"""
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, LAUNCHERS
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import confirm_dialog, terminal_dialog
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class LaunchersWindow(ctk.CTkToplevel):
    """Ventana de lanzadores de scripts del sistema"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.system_utils = SystemUtils()
        
        self.title("Lanzadores")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        
        self._create_ui()
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        make_window_header(
            main,
            title="LANZADORES",
            on_close=self.destroy,
        )
        
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        canvas = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        self._create_launcher_buttons(inner)
        
    
    def _create_launcher_buttons(self, parent):
        """Crea los botones de lanzadores en layout grid"""
        if not LAUNCHERS:
            no_launchers = ctk.CTkLabel(
                parent,
                text="No hay lanzadores configurados\n\nEdita config/settings.py para añadir scripts",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['medium']),
                justify="center"
            )
            no_launchers.pack(pady=50)
            return
        
        columns = 2
        
        for i, launcher in enumerate(LAUNCHERS):
            label = launcher.get("label", "Script")
            script_path = launcher.get("script", "")
            
            row = i // columns
            col = i % columns
            
            launcher_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
            launcher_frame.grid(row=row, column=col, sticky="nsew")
            
            btn = make_futuristic_button(
                launcher_frame,
                text=label,
                command=lambda s=script_path, l=label: self._run_script(s, l),
                width=40,
                height=15,
                font_size=FONT_SIZES['large']
            )
            btn.pack(pady=(10, 5), padx=10)
            
            path_label = ctk.CTkLabel(
                launcher_frame,
                text=script_path,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small']),
                wraplength=300
            )
            path_label.pack(pady=(0, 10), padx=10)
        
        for c in range(columns):
            parent.grid_columnconfigure(c, weight=1)
    
    def _run_script(self, script_path: str, label: str):
        """Ejecuta un script usando la terminal integrada tras confirmar"""

        def do_execute():
            logger.info(f"[LaunchersWindow] Ejecutando script: '{label}' → {script_path}")
            terminal_dialog(
                parent=self,
                script_path=script_path,
                title=f"EJECUTANDO: {label.upper()}"
            )

        confirm_dialog(
            parent=self,
            text=f"¿Deseas iniciar el proceso '{label}'?\n\nArchivo: {script_path}",
            title="⚠️ Lanzador de Sistema",
            on_confirm=do_execute
        )
```

## File: ui/windows/monitor.py
```python
"""
Ventana de monitoreo del sistema
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS,
                             CPU_WARN, CPU_CRIT, TEMP_WARN, TEMP_CRIT,
                             RAM_WARN, RAM_CRIT)
from ui.styles import StyleManager, make_window_header
from ui.widgets import GraphWidget
from core.system_monitor import SystemMonitor

_COL_W       = (DSI_WIDTH - 70) // 2
_GRAPH_H_TOP = 90
_GRAPH_H_BOT = 75


class MonitorWindow(ctk.CTkToplevel):
    """Ventana de monitoreo del sistema"""

    def __init__(self, parent, system_monitor: SystemMonitor, hardware_monitor=None):
        super().__init__(parent)
        self.system_monitor = system_monitor
        self.hardware_monitor = hardware_monitor
        self.widgets = {}
        self.graphs  = {}

        self.title("Monitor del Sistema")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        self._create_ui()
        self._update()

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main, title="MONITOR DEL SISTEMA", on_close=self.destroy)

        # Scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")

        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Grid 2 columnas dentro del inner scrollable
        grid = ctk.CTkFrame(inner, fg_color=COLORS['bg_medium'])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self._create_cell(grid, 0, 0, "CPU %",    "cpu",        "%",    _GRAPH_H_TOP)
        self._create_cell(grid, 0, 1, "RAM %",    "ram",        "%",    _GRAPH_H_TOP)
        self._create_cell(grid, 1, 0, "TEMP °C",  "temp",       "°C",   _GRAPH_H_TOP)
        self._create_cell(grid, 1, 1, "DISCO %",  "disk",       "%",    _GRAPH_H_TOP)
        self._create_cell(grid, 2, 0, "ESCRITURA","disk_write", "MB/s", _GRAPH_H_BOT)
        self._create_cell(grid, 2, 1, "LECTURA",  "disk_read",  "MB/s", _GRAPH_H_BOT)
    # ── Tarjeta temperatura chasis + fan duty real (FNK0100K) ──
        # Solo se crea si se pasó hardware_monitor (fase1 activo)
        if self.hardware_monitor:
            chassis_card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
            chassis_card.pack(fill="x", padx=5, pady=(0, 5))

            ctk.CTkLabel(
                chassis_card,
                text="🌡️ Hardware FNK0100K  (via fase1.py)",
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                text_color=COLORS['primary'],
                anchor="w",
            ).pack(anchor="w", padx=8, pady=(6, 4))

            hw_row = ctk.CTkFrame(chassis_card, fg_color="transparent")
            hw_row.pack(fill="x", padx=8, pady=(0, 10))
            hw_row.grid_columnconfigure(0, weight=1)
            hw_row.grid_columnconfigure(1, weight=1)
            hw_row.grid_columnconfigure(2, weight=1)

            for col_idx, (key, title, unit) in enumerate([
                ("chassis_temp", "Temp. chasis",  "°C"),
                ("fan0_pct",     "Fan 1 (real)",  "%"),
                ("fan1_pct",     "Fan 2 (real)",  "%"),
            ]):
                col_frame = ctk.CTkFrame(hw_row, fg_color="transparent")
                col_frame.grid(row=0, column=col_idx, padx=4, sticky="nsew")

                ctk.CTkLabel(
                    col_frame,
                    text=title,
                    font=(FONT_FAMILY, FONT_SIZES['small']),
                    text_color=COLORS['text_dim'],
                    anchor="center",
                ).pack()

                lbl = ctk.CTkLabel(
                    col_frame,
                    text=f"-- {unit}",
                    font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
                    text_color=COLORS['primary'],
                    anchor="center",
                )
                lbl.pack()

                # Guardar en self.widgets con el mismo patrón que el resto
                self.widgets[f"hw_{key}_value"] = (lbl, unit)
                
    def _create_cell(self, parent, row, col, title, key, unit, graph_h):
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        lbl = ctk.CTkLabel(cell, text=title, text_color=COLORS['primary'],
                           font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), anchor="w")
        lbl.pack(anchor="w", padx=8, pady=(6, 0))

        val = ctk.CTkLabel(cell, text=f"0.0 {unit}", text_color=COLORS['primary'],
                           font=(FONT_FAMILY, FONT_SIZES['large'], "bold"), anchor="e")
        val.pack(anchor="e", padx=8, pady=(0, 2))

        graph = GraphWidget(cell, width=_COL_W - 16, height=graph_h)
        graph.pack(padx=4, pady=(0, 6))

        self.widgets[f"{key}_label"] = lbl
        self.widgets[f"{key}_value"] = val
        self.graphs[key] = {'widget': graph, 'max_val': 100 if unit in ('%', '°C') else 50}

    def _update(self):
        if not self.winfo_exists():
            return

        stats   = self.system_monitor.get_current_stats()
        self.system_monitor.update_history(stats)
        history = self.system_monitor.get_history()

        self._update_metric('cpu',  stats['cpu'],        history['cpu'],   "%",   CPU_WARN,  CPU_CRIT)
        self._update_metric('ram',  stats['ram'],        history['ram'],   "%",   RAM_WARN,  RAM_CRIT)
        self._update_metric('temp', stats['temp'],       history['temp'],  "°C",  TEMP_WARN, TEMP_CRIT)
        self._update_metric('disk', stats['disk_usage'], history['disk'],  "%",   60,        80)
        self._update_io('disk_write', stats['disk_write_mb'], history['disk_write'])
        self._update_io('disk_read',  stats['disk_read_mb'],  history['disk_read'])

        self._header.status_label.configure(
            text=f"CPU {stats['cpu']:.0f}%  ·  RAM {stats['ram']:.0f}%  ·  {stats['temp']:.0f}°C")
        # ── Hardware FNK0100K (temperatura chasis + fan duty real) ──
        if self.hardware_monitor:
            if self.hardware_monitor.is_available():
                hw = self.hardware_monitor.get_stats()
                for key, warn, crit in [
                    ("chassis_temp", 35, 45),
                    ("fan0_pct",     80, 95),
                    ("fan1_pct",     80, 95),
                ]:
                    entry = self.widgets.get(f"hw_{key}_value")
                    if entry is None:
                        continue
                    lbl, unit = entry
                    val = hw.get(key)
                    if val is None:
                        lbl.configure(text=f"-- {unit}", text_color=COLORS['text_dim'])
                    else:
                        color = self.system_monitor.level_color(val, warn, crit)
                        lbl.configure(text=f"{val:.0f} {unit}", text_color=color)
            else:
                # fase1 no activo o datos obsoletos
                for key in ("chassis_temp", "fan0_pct", "fan1_pct"):
                    entry = self.widgets.get(f"hw_{key}_value")
                    if entry:
                        entry[0].configure(text="fase1 inactivo", text_color=COLORS['text_dim'])

        self.after(UPDATE_MS, self._update)


    def _update_metric(self, key, value, history, unit, warn, crit):
        color = self.system_monitor.level_color(value, warn, crit)
        self.widgets[f"{key}_value"].configure(text=f"{value:.1f} {unit}", text_color=color)
        self.widgets[f"{key}_label"].configure(text_color=color)
        g = self.graphs[key]
        g['widget'].update(history, g['max_val'], color)

    def _update_io(self, key, value, history):
        color = self.system_monitor.level_color(value, 10, 50)
        self.widgets[f"{key}_value"].configure(text=f"{value:.1f} MB/s", text_color=color)
        self.widgets[f"{key}_label"].configure(text_color=color)
        g = self.graphs[key]
        g['widget'].update(history, g['max_val'], color)
```

## File: ui/windows/update.py
```python
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, SCRIPTS_DIR
from ui.styles import make_futuristic_button
from ui.widgets.dialogs import terminal_dialog
from utils import SystemUtils


class UpdatesWindow(ctk.CTkToplevel):
    """Ventana de control de actualizaciones del sistema"""
    
    def __init__(self, parent, update_monitor):
        super().__init__(parent)
        self.system_utils = SystemUtils()
        self.monitor = update_monitor
        self._polling = False

        # Configuración de ventana (Estilo DSI)
        self.title("Actualizaciones del Sistema")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        
        self._create_ui()
        self._refresh_status(force=False)

    def _create_ui(self):
        # Frame Principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Icono
        self.status_icon = ctk.CTkLabel(main, text="󰚰", font=(FONT_FAMILY, 60))
        self.status_icon.pack(pady=(10, 5))
        
        # Labels
        self.status_label = ctk.CTkLabel(
            main, text="Verificando...", 
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold")
        )
        self.status_label.pack()
        
        self.info_label = ctk.CTkLabel(
            main, text="Estado de los paquetes",
            text_color=COLORS['text_dim'], font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        self.info_label.pack(pady=5)
        
        # Frame para botones
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=(10, 20))
        
        # 1. Botón Buscar (Manual)
        self.search_btn = make_futuristic_button(
            btn_frame, text="🔍 Buscar", 
            command=lambda: self._refresh_status(force=True), width=12
        )
        self.search_btn.pack(side="left", padx=5, expand=True)

        # 2. Botón Instalar
        self.update_btn = make_futuristic_button(
            btn_frame, text="󰚰 Instalar", 
            command=self._execute_update_script, width=12
        )
        self.update_btn.pack(side="left", padx=5, expand=True)
        self.update_btn.configure(state="disabled")
        
        # 3. Botón Cerrar
        close_btn = make_futuristic_button(
            btn_frame, text="Cerrar", 
            command=self.destroy, width=12
        )
        close_btn.pack(side="left", padx=5, expand=True)

    def _refresh_status(self, force=False):
        """Consulta el estado de actualizaciones"""
        if force:
            self._polling = False  # Cancelar polling si el usuario busca manualmente
            self.status_label.configure(text="Buscando...", text_color=COLORS['warning'])
            self.update_idletasks()

        res = self.monitor.check_updates(force=force)

        # Si el thread de arranque aún no ha terminado, mostrar estado de espera
        if res['status'] == "Unknown":
            self.status_label.configure(text="Comprobando...", text_color=COLORS['text_dim'])
            self.info_label.configure(text="Verificación inicial en curso")
            self.status_icon.configure(text_color=COLORS['text_dim'])
            self.update_btn.configure(state="disabled")
            # Reintentar cada 2 segundos hasta tener resultado real
            if not self._polling:
                self._polling = True
                self._poll_until_ready()
            return

        self._polling = False
        color = COLORS['success'] if res['pending'] == 0 else COLORS['warning']
        self.status_label.configure(text=res['status'], text_color=color)
        self.info_label.configure(text=res['message'])
        self.status_icon.configure(text_color=color)
        self.update_btn.configure(state="normal" if res['pending'] > 0 else "disabled")

    def _poll_until_ready(self):
        """Reintenta _refresh_status cada 2s mientras el resultado sea Unknown"""
        if not self._polling:
            return
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        res = self.monitor.check_updates(force=False)
        if res['status'] != "Unknown":
            self._refresh_status(force=False)
        else:
            self.after(2000, self._poll_until_ready)

    def _execute_update_script(self):
        """Lanza el script de terminal y refresca al terminar"""
        script_path = str(SCRIPTS_DIR / "update.sh")
        
        def al_terminar_actualizacion():
            self._refresh_status(force=True)
        
        terminal_dialog(
            self, 
            script_path, 
            "CONSOLA DE ACTUALIZACIÓN",
            on_close=al_terminar_actualizacion
        )
```

## File: ui/windows/disk.py
```python
"""
Ventana de monitoreo de disco
"""
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH,
                             DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS)
from ui.styles import StyleManager, make_window_header
from ui.widgets import GraphWidget
from core.disk_monitor import DiskMonitor

_COL_W   = (DSI_WIDTH - 70) // 2
_GRAPH_H = 95

# Cada cuántos ciclos de _update se refresca el SMART (es lento — smartctl tarda ~1s)
# UPDATE_MS suele ser 1000ms → cada 30 ciclos = cada 30 segundos
_SMART_EVERY = 30


class DiskWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de disco"""

    def __init__(self, parent, disk_monitor: DiskMonitor):
        super().__init__(parent)
        self.disk_monitor = disk_monitor
        self.widgets = {}
        self.graphs  = {}

        self._smart_tick = 0          # contador de ciclos para el SMART
        self._smart_cache = {}        # último resultado SMART

        self.title("Monitor de Disco")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        self._create_ui()
        self._update()

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main, title="MONITOR DE DISCO", on_close=self.destroy)

        # Scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")

        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # ── Grid 2 columnas — celdas originales con gráfica ──
        grid = ctk.CTkFrame(inner, fg_color=COLORS['bg_medium'])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self._create_cell(grid, 0, 0, "DISCO %",   "disk",       "%",    _GRAPH_H)
        self._create_cell(grid, 0, 1, "NVMe °C",   "nvme_temp",  "°C",   _GRAPH_H)
        self._create_cell(grid, 1, 0, "ESCRITURA", "disk_write", "MB/s", _GRAPH_H)
        self._create_cell(grid, 1, 1, "LECTURA",   "disk_read",  "MB/s", _GRAPH_H)

        # ── Tarjeta SMART NVMe (ancha, debajo del grid) ──
        smart_card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        smart_card.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkLabel(
            smart_card,
            text="💾 NVMe SMART",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(anchor="w", padx=8, pady=(6, 4))

        # Fila 1: Horas de uso / Ciclos de encendido / Apagados bruscos
        row1 = ctk.CTkFrame(smart_card, fg_color="transparent")
        row1.pack(fill="x", padx=8, pady=(0, 4))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)
        row1.grid_columnconfigure(2, weight=1)

        for col_idx, (key, title) in enumerate([
            ("power_on_hours", "Horas de uso"),
            ("power_cycles",   "Ciclos encendido"),
            ("unsafe_shutdowns", "Apagados bruscos"),
        ]):
            self._create_smart_col(row1, col_idx, key, title)

        # Separador
        ctk.CTkFrame(smart_card, fg_color=COLORS['border'], height=1).pack(
            fill="x", padx=8, pady=2)

        # Fila 2: TBW consumido / TB leídos / Vida útil consumida
        row2 = ctk.CTkFrame(smart_card, fg_color="transparent")
        row2.pack(fill="x", padx=8, pady=(4, 10))
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)
        row2.grid_columnconfigure(2, weight=1)

        for col_idx, (key, title) in enumerate([
            ("data_written_tb", "TB escritos"),
            ("data_read_tb",    "TB leídos"),
            ("percentage_used", "Vida útil usada"),
        ]):
            self._create_smart_col(row2, col_idx, key, title)

    def _create_cell(self, parent, row, col, title, key, unit, graph_h):
        """Celda original con gráfica — sin cambios."""
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        cell.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        lbl = ctk.CTkLabel(cell, text=title, text_color=COLORS['primary'],
                           font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), anchor="w")
        lbl.pack(anchor="w", padx=8, pady=(6, 0))

        val = ctk.CTkLabel(cell, text=f"0.0 {unit}", text_color=COLORS['primary'],
                           font=(FONT_FAMILY, FONT_SIZES['large'], "bold"), anchor="e")
        val.pack(anchor="e", padx=8, pady=(0, 2))

        graph = GraphWidget(cell, width=_COL_W - 16, height=graph_h)
        graph.pack(padx=4, pady=(0, 6))

        self.widgets[f"{key}_label"] = lbl
        self.widgets[f"{key}_value"] = val
        self.graphs[key] = {'widget': graph, 'max_val': 100 if unit in ('%', '°C') else 50}

    def _create_smart_col(self, parent, col_idx: int, key: str, title: str):
        """Columna de un campo SMART — sin gráfica."""
        col = ctk.CTkFrame(parent, fg_color="transparent")
        col.grid(row=0, column=col_idx, padx=4, sticky="nsew")

        ctk.CTkLabel(
            col, text=title,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
            anchor="center",
        ).pack()

        lbl = ctk.CTkLabel(
            col, text="--",
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
            text_color=COLORS['primary'],
            anchor="center",
        )
        lbl.pack()

        # Guardar referencia con prefijo smart_
        self.widgets[f"smart_{key}"] = lbl

    # ── Update ────────────────────────────────────────────────────────────────

    def _update(self):
        if not self.winfo_exists():
            return

        stats   = self.disk_monitor.get_current_stats()
        self.disk_monitor.update_history(stats)
        history = self.disk_monitor.get_history()

        # Métricas originales con gráfica
        self._update_metric('disk',       stats['disk_usage'],    history['disk_usage'], "%",    60, 80)
        self._update_metric('nvme_temp',  stats['nvme_temp'],     history['nvme_temp'],  "°C",   60, 70)
        self._update_io('disk_write',     stats['disk_write_mb'], history['disk_write'])
        self._update_io('disk_read',      stats['disk_read_mb'],  history['disk_read'])

        self._header.status_label.configure(
            text=f"Uso {stats['disk_usage']:.0f}%  ·  NVMe {stats['nvme_temp']:.0f}°C")

        # SMART — solo cada _SMART_EVERY ciclos (smartctl es lento)
        self._smart_tick += 1
        if self._smart_tick >= _SMART_EVERY:
            self._smart_tick = 0
            self._refresh_smart()

        self.after(UPDATE_MS, self._update)

    def _refresh_smart(self):
        """Llama a get_nvme_smart() y actualiza las etiquetas SMART."""
        smart = self.disk_monitor.get_nvme_smart()
        self._smart_cache = smart

        if not smart.get("available"):
            for key in ("power_on_hours", "power_cycles", "unsafe_shutdowns",
                        "data_written_tb", "data_read_tb", "percentage_used"):
                lbl = self.widgets.get(f"smart_{key}")
                if lbl:
                    lbl.configure(text="N/D", text_color=COLORS['text_dim'])
            return

        # Horas de uso
        self._set_smart("power_on_hours",
                        self._fmt_hours(smart.get("power_on_hours")),
                        warn=None)

        # Ciclos de encendido
        self._set_smart("power_cycles",
                        self._fmt_int(smart.get("power_cycles")),
                        warn=None)

        # Apagados bruscos — resaltar si hay muchos
        unsafe = smart.get("unsafe_shutdowns", 0) or 0
        self._set_smart("unsafe_shutdowns",
                        str(unsafe),
                        warn=unsafe > 10)

        # TB escritos
        self._set_smart("data_written_tb",
                        self._fmt_tb(smart.get("data_written_tb")),
                        warn=None)

        # TB leídos
        self._set_smart("data_read_tb",
                        self._fmt_tb(smart.get("data_read_tb")),
                        warn=None)

        # Vida útil consumida — color según nivel
        pct = smart.get("percentage_used")
        if pct is not None:
            if pct >= 90:
                color = COLORS['danger']
            elif pct >= 70:
                color = COLORS['warning']
            else:
                color = COLORS['primary']
            lbl = self.widgets.get("smart_percentage_used")
            if lbl:
                lbl.configure(text=f"{pct} %", text_color=color)
        else:
            self._set_smart("percentage_used", "--", warn=None)

    def _set_smart(self, key: str, text: str, warn):
        """Actualiza una etiqueta SMART con color según warn."""
        lbl = self.widgets.get(f"smart_{key}")
        if not lbl:
            return
        if warn is True:
            color = COLORS['warning']
        elif warn is False:
            color = COLORS['danger']
        else:
            color = COLORS['primary']
        lbl.configure(text=text, text_color=color)

    # ── Formateo ──────────────────────────────────────────────────────────────

    @staticmethod
    def _fmt_hours(hours) -> str:
        if hours is None:
            return "--"
        d = hours // 24
        h = hours % 24
        return f"{d}d {h}h"

    @staticmethod
    def _fmt_int(val) -> str:
        return "--" if val is None else str(val)

    @staticmethod
    def _fmt_tb(val) -> str:
        if val is None:
            return "--"
        if val < 1.0:
            return f"{val * 1024:.0f} GB"
        return f"{val:.2f} TB"

    # ── Métricas originales — sin cambios ────────────────────────────────────

    def _update_metric(self, key, value, history, unit, warn, crit):
        color = self.disk_monitor.level_color(value, warn, crit)
        self.widgets[f"{key}_value"].configure(text=f"{value:.1f} {unit}", text_color=color)
        self.widgets[f"{key}_label"].configure(text_color=color)
        g = self.graphs[key]
        g['widget'].update(history, g['max_val'], color)

    def _update_io(self, key, value, history):
        color = self.disk_monitor.level_color(value, 10, 50)
        self.widgets[f"{key}_value"].configure(text=f"{value:.1f} MB/s", text_color=color)
        self.widgets[f"{key}_label"].configure(text_color=color)
        g = self.graphs[key]
        g['widget'].update(history, g['max_val'], color)
```

## File: ui/windows/fan_control.py
```python
"""
Ventana de control de ventiladores
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, 
                             DSI_HEIGHT, DSI_X, DSI_Y)
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox
from core.fan_controller import FanController
from core.system_monitor import SystemMonitor
from utils.file_manager import FileManager


class FanControlWindow(ctk.CTkToplevel):
    """Ventana de control de ventiladores y curvas PWM"""
    
    def __init__(self, parent, fan_controller: FanController, 
                 system_monitor: SystemMonitor):
        super().__init__(parent)
        
        # Referencias
        self.fan_controller = fan_controller
        self.system_monitor = system_monitor
        self.file_manager = FileManager()
        
        # Variables de estado
        self.mode_var = tk.StringVar()
        self.manual_pwm_var = tk.IntVar(value=128)
        self.curve_vars = []

        # Variables para entries de nuevo punto (con placeholder)
        self._PLACEHOLDER_TEMP = "0-100"
        self._PLACEHOLDER_PWM  = "0-255"
        self.new_temp_var = tk.StringVar(value=self._PLACEHOLDER_TEMP)
        self.new_pwm_var  = tk.StringVar(value=self._PLACEHOLDER_PWM)
        
        # Cargar estado inicial
        self._load_initial_state()
        
        # Configurar ventana
        self.title("Control de Ventiladores")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.after(150, self.focus_set)
        self.lift()
        
        # Crear interfaz
        self._create_ui()
        
        # Iniciar bucle de actualización del slider/valor
        self._update_pwm_display()
    
    def _load_initial_state(self):
        """Carga el estado inicial desde archivo"""
        state = self.file_manager.load_state()
        self.mode_var.set(state.get("mode", "auto"))
        
        target = state.get("target_pwm")
        if target is not None:
            self.manual_pwm_var.set(target)
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Header unificado ──────────────────────────────────────────────────
        self._header = make_window_header(
            main,
            title="CONTROL DE VENTILADORES",
            on_close=self.destroy,
        )
        
        # Área de scroll
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Canvas y scrollbar
        canvas = ctk.CTkCanvas(
            scroll_container, 
            bg=COLORS['bg_medium'], 
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame interno
        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH-50)
        inner.bind("<Configure>", 
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Secciones
        self._create_mode_section(inner)
        self._create_manual_pwm_section(inner)
        self._create_curve_section(inner)
        self._create_bottom_buttons(main)
    
    def _create_mode_section(self, parent):
        """Crea la sección de selección de modo"""
        mode_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        mode_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(
            mode_frame,
            text="MODO DE OPERACIÓN",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        modes_container = ctk.CTkFrame(mode_frame, fg_color=COLORS['bg_medium'])
        modes_container.pack(fill="x", pady=5)
        
        modes = [
            ("Auto", "auto"),
            ("Silent", "silent"),
            ("Normal", "normal"),
            ("Performance", "performance"),
            ("Manual", "manual")
        ]
        
        for text, value in modes:
            rb = ctk.CTkRadioButton(
                modes_container,
                text=text,
                variable=self.mode_var,
                value=value,
                command=lambda v=value: self._on_mode_change(v),
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=8)
            StyleManager.style_radiobutton_ctk(rb)
    
    def _create_manual_pwm_section(self, parent):
        """Crea la sección de PWM manual"""
        manual_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        manual_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(
            manual_frame,
            text="PWM MANUAL (0-255)",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.pwm_value_label = ctk.CTkLabel(
            manual_frame,
            text=f"Valor: {self.manual_pwm_var.get()} ({int(self.manual_pwm_var.get()/255*100)}%)",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        self.pwm_value_label.pack(anchor="w", pady=(0, 10))
        
        slider = ctk.CTkSlider(
            manual_frame,
            from_=0,
            to=255,
            variable=self.manual_pwm_var,
            command=self._on_pwm_change,
            width=DSI_WIDTH - 100
        )
        slider.pack(fill="x", pady=5)
        StyleManager.style_slider_ctk(slider)
    
    def _create_curve_section(self, parent):
        """Crea la sección de curva temperatura-PWM"""
        curve_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        curve_frame.pack(fill="x", pady=5, padx=10)

        ctk.CTkLabel(
            curve_frame,
            text="CURVA TEMPERATURA-PWM",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        # Lista de puntos actuales
        self.points_frame = ctk.CTkFrame(curve_frame, fg_color=COLORS['bg_dark'])
        self.points_frame.pack(fill="x", pady=5, padx=5)
        self._refresh_curve_points()
        
        # Sección añadir punto con ENTRIES
        add_section = ctk.CTkFrame(curve_frame, fg_color=COLORS['bg_dark'])
        add_section.pack(fill="x", pady=5, padx=5)

        ctk.CTkLabel(
            add_section,
            text="AÑADIR NUEVO PUNTO",
            text_color=COLORS['success'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold")
        ).pack(anchor="w", padx=5, pady=5)

        # Fila con los dos entries en línea
        entries_row = ctk.CTkFrame(add_section, fg_color=COLORS['bg_dark'])
        entries_row.pack(fill="x", padx=5, pady=5)

        # — Temperatura —
        temp_col = ctk.CTkFrame(entries_row, fg_color=COLORS['bg_dark'])
        temp_col.pack(side="top", padx=(0, 20))

        ctk.CTkLabel(
            temp_col,
            text="Temperatura (°C)",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(anchor="n")

        self._entry_temp = ctk.CTkEntry(
            temp_col,
            textvariable=self.new_temp_var,
            width=120,
            height=36,
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text_dim'],      # color placeholder
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['primary']
        )
        self._entry_temp.pack(pady=4)
        self._entry_temp.bind("<FocusIn>",  lambda e: self._entry_focus_in(self._entry_temp, self.new_temp_var, self._PLACEHOLDER_TEMP))
        self._entry_temp.bind("<FocusOut>", lambda e: self._entry_focus_out(self._entry_temp, self.new_temp_var, self._PLACEHOLDER_TEMP))

        # — PWM —
        pwm_col = ctk.CTkFrame(entries_row, fg_color=COLORS['bg_dark'])
        pwm_col.pack(side="top", padx=(0, 20))

        ctk.CTkLabel(
            pwm_col,
            text="PWM (0-255)",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(anchor="n")

        self._entry_pwm = ctk.CTkEntry(
            pwm_col,
            textvariable=self.new_pwm_var,
            width=120,
            height=36,
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text_dim'],      # color placeholder
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['primary']
        )
        self._entry_pwm.pack(pady=4)
        self._entry_pwm.bind("<FocusIn>",  lambda e: self._entry_focus_in(self._entry_pwm, self.new_pwm_var, self._PLACEHOLDER_PWM))
        self._entry_pwm.bind("<FocusOut>", lambda e: self._entry_focus_out(self._entry_pwm, self.new_pwm_var, self._PLACEHOLDER_PWM))

        # Botón añadir
        make_futuristic_button(
            add_section,
            text="✓ Añadir Punto a la Curva",
            command=self._add_curve_point_from_entries,
            width=25,
            height=6,
            font_size=16
        ).pack(pady=10)

    # ── Helpers de placeholder ──────────────────────────────────────────────

    def _entry_focus_in(self, entry: ctk.CTkEntry, var: tk.StringVar, placeholder: str):
        """Borra el placeholder al enfocar y cambia color a texto normal"""
        if var.get() == placeholder:
            var.set("")
            entry.configure(text_color=COLORS['text'])

    def _entry_focus_out(self, entry: ctk.CTkEntry, var: tk.StringVar, placeholder: str):
        """Restaura el placeholder si el campo queda vacío"""
        if var.get().strip() == "":
            var.set(placeholder)
            entry.configure(text_color=COLORS['text_dim'])

    # ── Lógica de añadir punto ──────────────────────────────────────────────

    def _add_curve_point_from_entries(self):
        """Valida los entries y añade el punto a la curva"""
        temp_raw = self.new_temp_var.get().strip()
        pwm_raw  = self.new_pwm_var.get().strip()

        # Validar que no son placeholders ni vacíos
        if temp_raw in ("", self._PLACEHOLDER_TEMP) or pwm_raw in ("", self._PLACEHOLDER_PWM):
            custom_msgbox(self, "Introduce un valor en ambos campos.", "Error")
            return

        try:
            temp = int(temp_raw)
            pwm  = int(pwm_raw)
        except ValueError:
            custom_msgbox(self, "Los valores deben ser números enteros.", "Error")
            return

        if not (0 <= temp <= 100):
            custom_msgbox(self, "La temperatura debe estar entre 0 y 100 °C.", "Error")
            return
        if not (0 <= pwm <= 255):
            custom_msgbox(self, "El PWM debe estar entre 0 y 255.", "Error")
            return

        # Añadir punto
        self.fan_controller.add_curve_point(temp, pwm)

        # Resetear entries a placeholder
        self.new_temp_var.set(self._PLACEHOLDER_TEMP)
        self.new_pwm_var.set(self._PLACEHOLDER_PWM)
        self._entry_temp.configure(text_color=COLORS['text_dim'])
        self._entry_pwm.configure(text_color=COLORS['text_dim'])

        # Refrescar lista y confirmar
        self._refresh_curve_points()
        custom_msgbox(self, f"✓ Punto añadido:\n{temp}°C → PWM {pwm}", "Éxito")

    # ── Curva ───────────────────────────────────────────────────────────────

    def _refresh_curve_points(self):
        """Refresca la lista de puntos de la curva"""
        for widget in self.points_frame.winfo_children():
            widget.destroy()
        
        curve = self.file_manager.load_curve()
        
        if not curve:
            ctk.CTkLabel(
                self.points_frame,
                text="No hay puntos en la curva",
                text_color=COLORS['warning'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            ).pack(pady=10)
            return
        
        for point in curve:
            temp = point['temp']
            pwm  = point['pwm']
            
            point_frame = ctk.CTkFrame(self.points_frame, fg_color=COLORS['bg_medium'])
            point_frame.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(
                point_frame,
                text=f"{temp}°C → PWM {pwm}",
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            ).pack(side="left", padx=10)
            
            make_futuristic_button(
                point_frame,
                text="Eliminar",
                command=lambda t=temp: self._remove_curve_point(t),
                width=10,
                height=3,
                font_size=12
            ).pack(side="right", padx=5)

    def _remove_curve_point(self, temp: int):
        """Elimina un punto de la curva"""
        self.fan_controller.remove_curve_point(temp)
        self._refresh_curve_points()

    # ── Botones inferiores ──────────────────────────────────────────────────

    def _create_bottom_buttons(self, parent):
        """Crea los botones inferiores"""
        bottom = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        bottom.pack(fill="x", pady=10, padx=10)
        

        
        make_futuristic_button(
            bottom,
            text="Refrescar Curva",
            command=self._refresh_curve_points,
            width=15,
            height=6
        ).pack(side="left", padx=5)

    # ── Callbacks modo / PWM ────────────────────────────────────────────────

    def _on_mode_change(self, mode: str):
        """Callback cuando cambia el modo"""
        temp = self.system_monitor.get_current_stats()['temp']
        target_pwm = self.fan_controller.get_pwm_for_mode(
            mode=mode,
            temp=temp,
            manual_pwm=self.manual_pwm_var.get()
        )
        percent = int(target_pwm / 255 * 100)
        self.manual_pwm_var.set(target_pwm)
        self.pwm_value_label.configure(text=f"Valor: {target_pwm} ({percent}%)")
        self.file_manager.write_state({"mode": mode, "target_pwm": target_pwm})
    
    def _on_pwm_change(self, value):
        """Callback cuando cambia el PWM manual"""
        pwm = int(float(value))
        percent = int(pwm / 255 * 100)
        self.pwm_value_label.configure(text=f"Valor: {pwm} ({percent}%)")
        if self.mode_var.get() == "manual":
            self.file_manager.write_state({"mode": "manual", "target_pwm": pwm})
    
    def _update_pwm_display(self):
        """Actualiza el slider y valor para reflejar el PWM activo"""
        if not self.winfo_exists():
            return
        
        mode = self.mode_var.get()
        if mode != "manual":
            temp = self.system_monitor.get_current_stats()['temp']
            target_pwm = self.fan_controller.get_pwm_for_mode(
                mode=mode,
                temp=temp,
                manual_pwm=self.manual_pwm_var.get()
            )
            percent = int(target_pwm / 255 * 100)
            self.manual_pwm_var.set(target_pwm)
            self.pwm_value_label.configure(text=f"Valor: {target_pwm} ({percent}%)")
        
        self.after(2000, self._update_pwm_display)
```

## File: ui/windows/log_viewer.py
```python
"""
Ventana de visualización del log del dashboard
Permite filtrar por nivel, módulo, texto libre e intervalo de tiempo
y exportar el resultado filtrado a un archivo .log
"""
import re
import threading
from datetime import datetime, timedelta
from pathlib import Path

import customtkinter as ctk

from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, DATA_DIR, EXPORTS_LOG_DIR
)
from ui.styles import make_window_header, make_futuristic_button, StyleManager
from utils.logger import get_logger
from core.cleanup_service import CleanupService

logger = get_logger(__name__)

LOG_FILE = DATA_DIR / "logs" / "dashboard.log"
LOG_LEVELS = ["TODOS", "DEBUG", "INFO", "WARNING", "ERROR"]
LEVEL_COLORS = {
    "DEBUG":   "#888888",
    "INFO":    "#00BFFF",
    "WARNING": "#FFA500",
    "ERROR":   "#FF4444",
}

_PH_SEARCH = "buscar..."
_PH_MODULE = "módulo..."
_PH_DATE   = "YYYY-MM-DD"
_PH_TIME   = "HH:MM"

LOG_PATTERN = re.compile(
    r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+\[(\w+)\]\s+Dashboard(?:\.(\S+?))?:\s+(.*)$'
)


class LogViewerWindow(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Visor de Logs")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.lift()
        self.after(150, self.focus_set)

        self._all_lines = []
        self._modules   = []
        self._loading   = False

        self._level_var  = ctk.StringVar(value="TODOS")
        self._module_var = ctk.StringVar(value=_PH_MODULE)
        self._modules    = []  # lista completa de módulos disponibles
        self._search_var = ctk.StringVar(value=_PH_SEARCH)
        self._quick_var  = ctk.StringVar(value="1h")
        self._date_from  = ctk.StringVar(value=_PH_DATE)
        self._time_from  = ctk.StringVar(value=_PH_TIME)
        self._date_to    = ctk.StringVar(value=_PH_DATE)
        self._time_to    = ctk.StringVar(value=_PH_TIME)

        self._create_ui()
        self._load_log()

    # ── Placeholder helpers ──────────────────────────────────────────────────

    def _entry_focus_in(self, entry, var, placeholder):
        if var.get() == placeholder:
            var.set("")
            entry.configure(text_color=COLORS['text'])

    def _entry_focus_out(self, entry, var, placeholder):
        if var.get().strip() == "":
            var.set(placeholder)
            entry.configure(text_color=COLORS['text_dim'])

    def _entry_value(self, var, placeholder):
        v = var.get().strip()
        return "" if v == placeholder else v

    def _make_entry(self, parent, var, placeholder, width):
        e = ctk.CTkEntry(
            parent,
            textvariable=var,
            width=width,
            height=28,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['primary'],
            text_color=COLORS['text_dim'],
        )
        e.bind("<FocusIn>",  lambda ev: self._entry_focus_in(e, var, placeholder))
        e.bind("<FocusOut>", lambda ev: self._entry_focus_out(e, var, placeholder))
        return e

    # ── UI ───────────────────────────────────────────────────────────────────

    def _create_ui(self):
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)
        make_window_header(main, title="VISOR DE LOGS", on_close=self.destroy)
        self._create_filters(main)
        ctk.CTkFrame(main, fg_color=COLORS['border'], height=1,
                     corner_radius=0).pack(fill="x", padx=5, pady=(4, 0))
        self._create_results(main)
        self._create_bottom_bar(main)

    def _create_filters(self, parent):
        filters = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        filters.pack(fill="x", padx=5, pady=(4, 0))

        # Fila 1: Nivel · Módulo · Búsqueda
        row1 = ctk.CTkFrame(filters, fg_color="transparent")
        row1.pack(fill="x", padx=8, pady=(6, 2))

        ctk.CTkLabel(row1, text="Nivel:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        ctk.CTkOptionMenu(
            row1, variable=self._level_var, values=LOG_LEVELS, width=100,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'], button_color=COLORS['primary'],
            command=lambda _: self._apply_filters()
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(row1, text="Módulo:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        self._module_entry = self._make_entry(row1, self._module_var, _PH_MODULE, width=160)
        self._module_entry.bind("<Return>",     lambda e: self._apply_filters())
        self._module_entry.bind("<KeyRelease>", lambda e: self.after(300, self._apply_filters))
        self._module_entry.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(row1, text="Buscar:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        search_entry = self._make_entry(row1, self._search_var, _PH_SEARCH, width=140)
        search_entry.bind("<Return>",     lambda e: self._apply_filters())
        search_entry.bind("<KeyRelease>", lambda e: self.after(400, self._apply_filters))
        search_entry.pack(side="left")

        # Fila 2: Intervalo rápido | Intervalo manual
        row2 = ctk.CTkFrame(filters, fg_color="transparent")
        row2.pack(fill="x", padx=8, pady=(2, 6))

        ctk.CTkLabel(row2, text="Últimos:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        ctk.CTkOptionMenu(
            row2, variable=self._quick_var,
            values=["15min", "1h", "6h", "24h", "Todo"], width=80,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'], button_color=COLORS['primary'],
            command=self._on_quick_interval
        ).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(row2, text="│", text_color=COLORS['border'],
                     font=(FONT_FAMILY, FONT_SIZES['medium'])).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(row2, text="Desde:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        self._make_entry(row2, self._date_from, _PH_DATE, width=90).pack(side="left", padx=(0, 4))
        self._make_entry(row2, self._time_from, _PH_TIME, width=60).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(row2, text="Hasta:", font=(FONT_FAMILY, FONT_SIZES['small']),
                     text_color=COLORS['text_dim']).pack(side="left", padx=(0, 4))
        self._make_entry(row2, self._date_to, _PH_DATE, width=90).pack(side="left", padx=(0, 4))
        self._make_entry(row2, self._time_to, _PH_TIME, width=60).pack(side="left", padx=(0, 8))

        make_futuristic_button(
            row2, text="Aplicar", command=self._apply_filters,
            width=8, height=4, font_size=13
        ).pack(side="left")

    def _create_results(self, parent):
        result_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        result_frame.pack(fill="both", expand=True, padx=5, pady=4)

        self._textbox = ctk.CTkTextbox(
            result_frame,
            fg_color=COLORS['bg_dark'],
            text_color=COLORS['text'],
            font=("Courier New", 12),
            wrap="none",
            state="disabled",
        )
        self._textbox.pack(fill="both", expand=True, padx=4, pady=4)

        self._textbox._textbox.tag_config("DEBUG",   foreground=LEVEL_COLORS["DEBUG"])
        self._textbox._textbox.tag_config("INFO",    foreground=LEVEL_COLORS["INFO"])
        self._textbox._textbox.tag_config("WARNING", foreground=LEVEL_COLORS["WARNING"])
        self._textbox._textbox.tag_config("ERROR",   foreground=LEVEL_COLORS["ERROR"])

        try:
            children = self._textbox._textbox.master.children
            vsb = children.get('!ctkscrollbar')
            hsb = children.get('!ctkscrollbar2')
            if vsb:
                StyleManager.style_scrollbar_ctk(vsb)
                vsb.configure(width=22)
            if hsb:
                StyleManager.style_scrollbar_ctk(hsb)
                hsb.configure(height=22)
        except Exception:
            pass

    def _create_bottom_bar(self, parent):
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.pack(fill="x", padx=5, pady=(0, 4))

        self._count_label = ctk.CTkLabel(
            bar, text="0 entradas",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim']
        )
        self._count_label.pack(side="left", padx=8)

        make_futuristic_button(
            bar, text="↓ Exportar", command=self._export,
            width=10, height=5, font_size=14
        ).pack(side="right", padx=4)

        make_futuristic_button(
            bar, text="↺ Recargar", command=self._load_log,
            width=10, height=5, font_size=14
        ).pack(side="right", padx=4)

    # ── Carga ────────────────────────────────────────────────────────────────

    def _load_log(self):
        if self._loading:
            return
        self._loading = True
        self._set_text("Cargando log...", [])
        threading.Thread(target=self._read_log_thread, daemon=True).start()

    def _read_log_thread(self):
        lines = []
        try:
            rotated = Path(str(LOG_FILE) + ".1")
            if rotated.exists():
                with open(rotated, "r", encoding="utf-8", errors="replace") as f:
                    for raw in f:
                        p = self._parse_line(raw.rstrip())
                        if p:
                            lines.append(p)
            if LOG_FILE.exists():
                with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                    for raw in f:
                        p = self._parse_line(raw.rstrip())
                        if p:
                            lines.append(p)
        except Exception as e:
            logger.error(f"[LogViewerWindow] Error leyendo log: {e}")

        self._all_lines = lines
        self._loading = False
        modules = sorted(set(l["module"] for l in lines))
        self.after(0, lambda: self._update_modules(modules))
        self.after(0, self._apply_filters)

    def _parse_line(self, raw):
        m = LOG_PATTERN.match(raw)
        if not m:
            return None
        ts_str, level, module, message = m.groups()
        if not module:
            module = "general"
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
        return {"ts": ts, "ts_str": ts_str, "level": level,
                "module": module, "message": message, "raw": raw}

    def _update_modules(self, modules):
        self._modules = modules  # guardar lista para filtrado parcial

    # ── Filtrado ─────────────────────────────────────────────────────────────

    def _on_quick_interval(self, value):
        now = datetime.now()
        deltas = {"15min": timedelta(minutes=15), "1h": timedelta(hours=1),
                  "6h": timedelta(hours=6), "24h": timedelta(hours=24)}
        if value == "Todo":
            for var, ph in [(self._date_from, _PH_DATE), (self._time_from, _PH_TIME),
                            (self._date_to,   _PH_DATE), (self._time_to,   _PH_TIME)]:
                var.set(ph)
        else:
            since = now - deltas[value]
            self._date_from.set(since.strftime("%Y-%m-%d"))
            self._time_from.set(since.strftime("%H:%M"))
            self._date_to.set(now.strftime("%Y-%m-%d"))
            self._time_to.set(now.strftime("%H:%M"))
        self._apply_filters()

    def _apply_filters(self):
        level  = self._level_var.get()
        module = self._entry_value(self._module_var, _PH_MODULE).lower()
        search = self._entry_value(self._search_var, _PH_SEARCH).lower()
        dt_from = self._parse_datetime(
            self._entry_value(self._date_from, _PH_DATE),
            self._entry_value(self._time_from, _PH_TIME), False)
        dt_to = self._parse_datetime(
            self._entry_value(self._date_to, _PH_DATE),
            self._entry_value(self._time_to, _PH_TIME), True)

        result = []
        for line in self._all_lines:
            if level  != "TODOS" and line["level"]  != level:  continue
            if module and module not in line["module"].lower():   continue
            if search and search not in line["raw"].lower():   continue
            if dt_from and line["ts"] < dt_from:               continue
            if dt_to   and line["ts"] > dt_to:                 continue
            result.append(line)

        self._set_text(None, result)
        self._count_label.configure(text=f"{len(result)} entradas")

    def _parse_datetime(self, date_str, time_str, is_end):
        if not date_str:
            return None
        if not time_str:
            time_str = "23:59" if is_end else "00:00"
        try:
            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            return None

    # ── Renderizado ──────────────────────────────────────────────────────────

    def _set_text(self, loading_msg, lines):
        self._textbox.configure(state="normal")
        self._textbox._textbox.delete("1.0", "end")
        if loading_msg:
            self._textbox._textbox.insert("end", loading_msg)
        else:
            for line in lines:
                lvl = line["level"]
                tag = lvl if lvl in LEVEL_COLORS else "INFO"
                self._textbox._textbox.insert(
                    "end",
                    f"{line['ts_str']} [{lvl}] {line['module']}: {line['message']}\n",
                    tag
                )
            self._textbox._textbox.see("end")
        self._textbox.configure(state="disabled")

    # ── Exportar ─────────────────────────────────────────────────────────────

    def _export(self):
        level  = self._level_var.get()
        module = self._entry_value(self._module_var, _PH_MODULE).lower()
        search = self._entry_value(self._search_var, _PH_SEARCH).lower()
        dt_from = self._parse_datetime(
            self._entry_value(self._date_from, _PH_DATE),
            self._entry_value(self._time_from, _PH_TIME), False)
        dt_to = self._parse_datetime(
            self._entry_value(self._date_to, _PH_DATE),
            self._entry_value(self._time_to, _PH_TIME), True)

        result = []
        for line in self._all_lines:
            if level  != "TODOS" and line["level"]  != level:  continue
            if module and module not in line["module"].lower():   continue
            if search and search not in line["raw"].lower():   continue
            if dt_from and line["ts"] < dt_from:               continue
            if dt_to   and line["ts"] > dt_to:                 continue
            result.append(line["raw"])

        from ui.widgets.dialogs import custom_msgbox
        if not result:
            custom_msgbox(self, "No hay entradas que exportar.", "Exportar")
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = EXPORTS_LOG_DIR / f"log_export_{ts}.log"
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                f.write("\n".join(result))
            custom_msgbox(self, f"Exportado en:\n{export_path}", "Exportar")
            logger.info(f"[LogViewerWindow] Log exportado: {export_path}")
            try:
                CleanupService().clean_log_exports()
            except Exception as e:
                logger.warning(f"[LogViewerWindow] No se pudo limpiar exports: {e}")
        except OSError as e:
            custom_msgbox(self, f"Error al exportar:\n{e}", "Error")
            logger.error(f"[LogViewerWindow] Error exportando: {e}")
```

## File: ui/styles.py
```python
"""
Estilos y temas para la interfaz
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES


class StyleManager:
    """Gestor centralizado de estilos"""
    
    @staticmethod
    def style_radiobutton_tk(rb: tk.Radiobutton, 
                            fg: str = None, 
                            bg: str = None, 
                            hover_fg: str = None) -> None:
        """
        Aplica estilo a radiobutton de tkinter
        
        Args:
            rb: Widget radiobutton
            fg: Color de texto
            bg: Color de fondo
            hover_fg: Color al pasar el mouse
        """
        fg = fg or COLORS['primary']
        bg = bg or COLORS['bg_dark']
        hover_fg = hover_fg or COLORS['success']
        
        rb.config(
            fg=fg, 
            bg=bg, 
            selectcolor=bg, 
            activeforeground=fg, 
            activebackground=bg,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"), 
            indicatoron=True
        )
        
        def on_enter(e): 
            rb.config(fg=hover_fg)
        
        def on_leave(e): 
            rb.config(fg=fg)
        
        rb.bind("<Enter>", on_enter)
        rb.bind("<Leave>", on_leave)
    
    @staticmethod
    def style_radiobutton_ctk(rb: ctk.CTkRadioButton, radiobutton_width: int = 25, radiobutton_height: int = 25) -> None:
        """
        Aplica estilo a radiobutton de customtkinter
        
        Args:
            rb: Widget radiobutton
        """
        rb.configure(
            radiobutton_width=radiobutton_width,
            radiobutton_height=radiobutton_height,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            fg_color=COLORS['primary'],
        )
    
    @staticmethod
    def style_slider(slider: tk.Scale, color: str = None) -> None:
        """
        Aplica estilo a slider de tkinter
        
        Args:
            slider: Widget slider
            color: Color personalizado
        """
        color = color or COLORS['primary']
        slider.config(
            troughcolor=COLORS['secondary'], 
            sliderrelief="flat", 
            bd=0,
            highlightthickness=0, 
            fg=color, 
            bg=COLORS['bg_dark'], 
            activebackground=color
        )
    
    @staticmethod
    def style_slider_ctk(slider: ctk.CTkSlider, color: str = None) -> None:
        """
        Aplica estilo a slider de customtkinter
        
        Args:
            slider: Widget slider
            color: Color personalizado
        """
        color = color or COLORS['primary']  # ✓ Usar tema
        slider.configure(
            fg_color=COLORS['bg_light'],
            progress_color=color,
            button_color=color,
            button_hover_color=COLORS['secondary'],
            height=30
        )
    
    @staticmethod
    def style_scrollbar(sb: tk.Scrollbar, color: str = None) -> None:
        """
        Aplica estilo a scrollbar de tkinter
        
        Args:
            sb: Widget scrollbar
            color: Color personalizado
        """
        color = color or COLORS['bg_dark']
        sb.config(
            troughcolor=COLORS['secondary'], 
            bg=color, 
            activebackground=color,
            highlightthickness=0, 
            relief="flat"
        )
    
    @staticmethod
    def style_scrollbar_ctk(sb: ctk.CTkScrollbar, color: str = None) -> None:
        """
        Aplica estilo a scrollbar de customtkinter
        
        Args:
            sb: Widget scrollbar
            color: Color personalizado
        """
        color = color or COLORS['primary']  # ✓ Usar tema
        sb.configure(
            bg_color=COLORS['bg_medium'],
            button_color=color,
            button_hover_color=COLORS['secondary']
        )
    
    @staticmethod
    def style_ctk_scrollbar(scrollable_frame: ctk.CTkScrollableFrame, 
                           color: str = None) -> None:
        """
        Aplica estilo a scrollable frame de customtkinter
        
        Args:
            scrollable_frame: Widget scrollable frame
            color: Color personalizado
        """
        color = color or COLORS['primary']  # ✓ Usar tema
        scrollable_frame.configure(
            scrollbar_fg_color=COLORS['bg_medium'],
            scrollbar_button_color=color,
            scrollbar_button_hover_color=COLORS['secondary']
        )


def make_futuristic_button(parent, text: str, command=None, 
                          width: int = None, height: int = None, 
                          font_size: int = None, state: str = "normal") -> ctk.CTkButton:
    """
    Crea un botón con estilo futurista
    
    Args:
        parent: Widget padre
        text: Texto del botón
        command: Función a ejecutar al hacer clic
        width: Ancho en unidades
        height: Alto en unidades
        font_size: Tamaño de fuente
        
    Returns:
        Widget CTkButton configurado
    """
    width = width or 20
    height = height or 10
    font_size = font_size or FONT_SIZES['large']
    
    btn = ctk.CTkButton(
        parent, 
        text=text, 
        command=command,
        fg_color=COLORS['bg_dark'], 
        hover_color=COLORS['bg_light'],
        border_width=3, 
        border_color=COLORS['border'],
        width=width * 8, 
        height=height * 8,
        font=(FONT_FAMILY, font_size, "bold"), 
        corner_radius=10,
        state=state
    )
    
    def on_enter(e): 
        btn.configure(fg_color=COLORS['bg_light'])
    
    def on_leave(e): 
        btn.configure(fg_color=COLORS['bg_dark'])
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn


def make_window_header(parent, title: str, on_close, status_text: str = None) -> ctk.CTkFrame:
    """
    Crea una barra de cabecera unificada para ventanas de monitoreo.

    Layout (altura fija 48px):
    ┌─────────────────────────────────────────────────────────┐
    │  ● TÍTULO DE VENTANA      status_text opcional   [✕]   │
    └─────────────────────────────────────────────────────────┘

    El indicador ● usa COLORS['secondary'] para identificar
    visualmente que es una ventana hija del dashboard.

    Args:
        parent:      Widget padre (normalmente el frame main de la ventana).
        title:       Texto del título en mayúsculas (ej. "MONITOR DEL SISTEMA").
        on_close:    Callable ejecutado al pulsar el botón ✕.
        status_text: Texto informativo opcional a la derecha del título
                     (ej. "CPU 12% · RAM 45% · 52°C"). Si es None no se muestra.

    Returns:
        CTkFrame de cabecera ya empaquetado con pack(fill="x").
        Guarda referencia al label de estado en frame.status_label
        para que la ventana pueda actualizarlo dinámicamente.
    """
    # ── Contenedor ───────────────────────────────────────────────────────────
    header = ctk.CTkFrame(
        parent,
        fg_color=COLORS['bg_dark'],
        height=56,
        corner_radius=8,
    )
    header.pack(fill="x", padx=5, pady=(5, 0))
    header.pack_propagate(False)  # Altura fija

    # Separador inferior (línea decorativa)
    separator = ctk.CTkFrame(
        parent,
        fg_color=COLORS['border'],
        height=1,
        corner_radius=0,
    )
    separator.pack(fill="x", padx=5, pady=(0, 4))

    # ── Indicador de color (pastilla izquierda) ───────────────────────────
    dot = ctk.CTkLabel(
        header,
        text="●",
        text_color=COLORS['secondary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
        width=28,
    )
    dot.pack(side="left", padx=(10, 2))

    # ── Título ────────────────────────────────────────────────────────────
    title_lbl = ctk.CTkLabel(
        header,
        text=title,
        text_color=COLORS['secondary'],
        font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
        anchor="w",
    )
    title_lbl.pack(side="left", padx=(0, 10))

    # ── Botón cerrar (derecha) ────────────────────────────────────────────
    close_btn = ctk.CTkButton(
        header,
        text="✕",
        command=on_close,
        width=52,
        height=42,
        fg_color=COLORS['bg_medium'],
        hover_color=COLORS['danger'],
        border_width=3,
        border_color=COLORS['border'],
        font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
        corner_radius=6,
    )
    close_btn.pack(side="right", padx=(0, 8))

    # ── Status label (derecha del título, izquierda del botón) ───────────
    status_lbl = ctk.CTkLabel(
        header,
        text=status_text or "",
        text_color=COLORS['text_dim'],
        font=(FONT_FAMILY, FONT_SIZES['small']),
        anchor="e",
    )
    status_lbl.pack(side="right", padx=(0, 12), expand=True, fill="x")

    # Referencia pública para actualizaciones dinámicas
    header.status_label = status_lbl

    return header


def make_homebridge_switch(
    parent,
    text: str,
    command=None,
    is_on: bool = False,
    disabled: bool = False,
) -> ctk.CTkSwitch:
    """
    Crea un CTkSwitch estilado para el control de accesorios Homebridge.

    Layout dentro de la tarjeta de dispositivo:
    ┌─────────────────────────────────────────┐
    │   NOMBRE DEL DISPOSITIVO   [══ ●]       │
    └─────────────────────────────────────────┘

    El switch usa los colores del tema activo:
    - ON  → COLORS['success']  (verde por defecto)
    - OFF → COLORS['bg_light'] (gris oscuro)
    - Deshabilitado (fallo/inactivo) → COLORS['danger'] fijo, no interactivo

    Args:
        parent:   Widget padre (normalmente la tarjeta CTkFrame).
        text:     Etiqueta del switch (nombre del dispositivo).
        command:  Callable ejecutado al cambiar el estado.
                  Recibe el nuevo valor como booleano (True=ON, False=OFF).
        is_on:    Estado inicial del switch.
        disabled: Si True, el switch se muestra bloqueado en rojo (fallo/inactivo).

    Returns:
        CTkSwitch configurado y listo para empaquetar.
    """
    color_on   = COLORS.get('success', '#00ff88')
    color_off  = COLORS.get('bg_light', '#333333')
    color_fault = COLORS.get('danger', '#ff4444')

    if disabled:
        # Fallo o inactivo: switch bloqueado, color de aviso
        sw = ctk.CTkSwitch(
            parent,
            text=text,
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
            text_color=COLORS.get('text_dim', '#888888'),
            progress_color=color_fault,
            button_color=color_fault,
            button_hover_color=color_fault,
            fg_color=color_off,
            switch_width=90,
            switch_height=46,
            state="disabled",
        )
        # Fijar visualmente en OFF aunque haya fallo
        sw.deselect()
    else:
        def _on_toggle():
            # El switch ya cambió internamente; leemos su valor
            if command:
                command(bool(sw.get()))

        sw = ctk.CTkSwitch(
            parent,
            text=text,
            command=_on_toggle,
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
            text_color=COLORS['text'],
            progress_color=color_on,
            button_color=COLORS['secondary'],
            button_hover_color=COLORS['primary'],
            fg_color=color_off,
            switch_width=90,
            switch_height=46,
        )
        # Establecer estado inicial
        if is_on:
            sw.select()
        else:
            sw.deselect()

    return sw
```

## File: ui/windows/history.py
```python
"""
Ventana de histórico de datos
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, DATA_DIR, EXPORTS_CSV_DIR, EXPORTS_SCR_DIR
from ui.styles import make_futuristic_button, StyleManager, make_window_header
from ui.widgets import custom_msgbox , confirm_dialog
from core.data_analyzer import DataAnalyzer
from core.data_logger import DataLogger
from core.cleanup_service import CleanupService
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from utils.logger import get_logger
import os

logger = get_logger(__name__)

_DATE_FMT = "%Y-%m-%d %H:%M"


class HistoryWindow(ctk.CTkToplevel):
    """Ventana de visualización de histórico"""

    def __init__(self, parent, cleanup_service: CleanupService):
        super().__init__(parent)

        # Referencias
        self.analyzer         = DataAnalyzer()
        self.logger           = DataLogger()
        self.cleanup_service  = cleanup_service

        # Estado de periodo
        self.period_var = ctk.StringVar(value="24h")
        self.period_start = ctk.StringVar(value="YYYY-MM-DD HH:MM")
        self.period_end   = ctk.StringVar(value="YYYY-MM-DD HH:MM")

        # Estado de rango personalizado
        self._using_custom_range = False
        self._custom_start: datetime = None
        self._custom_end:   datetime = None

        # Configurar ventana
        self.title("Histórico de Datos")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)

        # Crear interfaz
        self._create_ui()

        # Cargar datos iniciales
        self._update_data()

    # ─────────────────────────────────────────────
    # Construcción de la UI
    # ─────────────────────────────────────────────

    def _create_ui(self):
        self._main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        self._main.pack(fill="both", expand=True, padx=5, pady=5) 
        # ── Header unificado ──────────────────────────────────────────────────
        self._header = make_window_header(
            self._main,
            title="HISTÓRICO DE DATOS",
            on_close=self.destroy,
        )
        # Barra de herramientas en línea propia debajo del header
        self.toolbar_container = ctk.CTkFrame(self._main, fg_color=COLORS["bg_dark"])
        self.toolbar_container.pack(fill="x", padx=5, pady=(0, 4))
        self.toolbar_container.pack_configure(anchor="center")
        self._create_period_controls(self._main)
        self._create_range_panel(self._main)   # fila oculta de OptionMenus

        scroll_container = ctk.CTkFrame(self._main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas_tk = ctk.CTkCanvas(
            scroll_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0,
            height=DSI_HEIGHT - 300
        )
        canvas_tk.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container,
            orientation="vertical",
            command=canvas_tk.yview,
            width=30
        )
        scrollbar.pack(side="right", fill="y")

        StyleManager.style_scrollbar_ctk(scrollbar)

        canvas_tk.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas_tk, fg_color=COLORS['bg_medium'])
        canvas_tk.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>",
                   lambda e: canvas_tk.configure(scrollregion=canvas_tk.bbox("all")))

        self._create_graphs_area(inner)
        self._create_stats_area(inner)
        self._create_buttons(self._main)


    def _create_period_controls(self, parent):
        """Fila 1: radio buttons 24h/7d/30d + botón para abrir/cerrar el panel de rango."""
        self._controls_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        self._controls_frame.pack(fill="x", padx=10, pady=(5, 0))

        ctk.CTkLabel(
            self._controls_frame,
            text="Periodo:",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        ).pack(side="left", padx=10)

        for period, label in [("24h", "24 horas"), ("7d", "7 días"), ("30d", "30 días")]:
            rb = ctk.CTkRadioButton(
                self._controls_frame,
                text=label,
                variable=self.period_var,
                value=period,
                command=self._on_period_radio,
                text_color=COLORS['text'],
                font=(FONT_FAMILY, FONT_SIZES['small'])
            )
            rb.pack(side="left", padx=10)
            StyleManager.style_radiobutton_ctk(rb)

        # Botón toggle del panel de rango
        self._toggle_btn = make_futuristic_button(
            self._controls_frame,
            text="󰙹 Rango",
            command=self._toggle_range_panel,
            height=6,
            width=13
        )
        self._toggle_btn.pack(side="right", padx=10)

    def _create_range_panel(self, parent):
        """
        Fila 2 (oculta por defecto): selectores día/mes/año/hora/min
        para inicio y fin del rango. Sin teclado — todo por OptionMenu.
        """
        self._range_panel = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        # No se hace pack aquí → empieza oculto
        ctk.CTkLabel(
            self._range_panel,
            text="desde:",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(10, 2))

        self.date_start = ctk.CTkEntry(
            self._range_panel,
            textvariable=self.period_start,
            text_color=COLORS['text_dim'],
            width=300,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        # Limpiar al hacer foco si tiene el texto de ejemplo
        self.date_start.bind("<FocusIn>",  lambda e: self._entry_focus_in(self.date_start, self.period_start))
        self.date_start.bind("<FocusOut>", lambda e: self._entry_focus_out(self.date_start, self.period_start))
        self.date_start.pack(side="left", padx=(0, 4))
                # Entradas de fecha en la fila de controles (derecha)
        ctk.CTkLabel(
            self._range_panel,
            text="hasta:",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small'])
        ).pack(side="left", padx=(0, 2))

        self.date_end = ctk.CTkEntry(
            self._range_panel,
            textvariable=self.period_end,
            text_color=COLORS['text_dim'],
            width=300,
            font=(FONT_FAMILY, FONT_SIZES['small'])
        )
        self.date_end.bind("<FocusIn>",  lambda e: self._entry_focus_in(self.date_end, self.period_end))
        self.date_end.bind("<FocusOut>", lambda e: self._entry_focus_out(self.date_end, self.period_end))
        self.date_end.pack(side="left", padx=(0, 4))


        # ── BOTÓN APLICAR ─────────────────────────────────────────
        self._apply_btn = make_futuristic_button(
            self._controls_frame,
            text="✓Aplicar",
            command=self._apply_custom_range,
            height=6,
            width=12,
            state="disabled"  # solo se habilita al abrir el panel, para evitar confusión
        )
        self._apply_btn.pack(side="right", padx=(10, 5))

    def _create_graphs_area(self, parent):
        graphs_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        graphs_frame.pack(fill="both", expand=True, padx=(0, 10), pady=(0, 10))

        self.fig = Figure(figsize=(9, 20), facecolor=COLORS['bg_medium'])
        self.fig.set_tight_layout(True)

        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=0)

        # Toolbar invisible — sus métodos se invocan desde botones propios
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.pack_forget()

        # Sub-frame centrado dentro de la barra de herramientas
        _btn_row = ctk.CTkFrame(self.toolbar_container, fg_color="transparent")
        _btn_row.pack(expand=True)

        for text, cmd, w in [
            ("🏠 Inicio",  self.toolbar.home,          12),
            ("🔍 Zoom",    self.toolbar.zoom,           12),
            ("🖐️ Mover",  self.toolbar.pan,            12),
            (" Guardar",  self._export_figure_image,   12),
        ]:
            make_futuristic_button(
                _btn_row, text=text, command=cmd, height=6, width=w
            ).pack(side="left", padx=5, pady=4)

        self.canvas.mpl_connect('button_press_event',   self._on_click)
        self.canvas.mpl_connect('button_release_event', self._on_release)
        self.canvas.mpl_connect('motion_notify_event',  self._on_motion)

    def _create_stats_area(self, parent):
        stats_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'])
        stats_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            stats_frame,
            text="Estadísticas:",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold")
        ).pack(pady=(10, 5))

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Cargando...",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['small']),
            justify="left"
        )
        self.stats_label.pack(pady=(0, 10), padx=20)

    def _create_buttons(self, parent):
        buttons = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'])
        buttons.pack(fill="x", pady=10, padx=10)

        for text, cmd, side, w in [
            ("Actualizar",       self._update_data,    "left",  18),
            ("Exportar CSV",     self._export_csv,     "left",  18),
            ("Limpiar Antiguos", self._clean_old_data, "left",  18),
        ]:
            make_futuristic_button(
                buttons, text=text, command=cmd, width=w, height=6
            ).pack(side=side, padx=5)

    # ─────────────────────────────────────────────
    # Control del panel de rango
    # ─────────────────────────────────────────────

    def _toggle_range_panel(self):
        """Muestra u oculta la fila de OptionMenus de rango personalizado."""
        if self._range_panel.winfo_ismapped():
            self._range_panel.pack_forget()
            self._toggle_btn.configure(text="󰙹 Rango")
            self._apply_btn.configure(state="disabled")
        else:
            # Insertar después del frame de controles de periodo
            self._range_panel.pack(
                fill="x", padx=10, pady=(10, 5),
                after=self._controls_frame
            )
            self._toggle_btn.configure(text="✕ Cerrar")
            self._apply_btn.configure(state="normal")


    # ─────────────────────────────────────────────
    # Lógica de actualización
    # ─────────────────────────────────────────────

    _PLACEHOLDER = "YYYY-MM-DD HH:MM"

    def _entry_focus_in(self, entry: ctk.CTkEntry, var: ctk.StringVar):
        """Al enfocar: si tiene el texto de ejemplo, lo borra y pone color normal."""
        if var.get() == self._PLACEHOLDER:
            var.set("")
            entry.configure(text_color=COLORS['text'])

    def _entry_focus_out(self, entry: ctk.CTkEntry, var: ctk.StringVar):
        """Al perder foco: si quedó vacío, restaura el texto de ejemplo en gris."""
        if var.get().strip() == "":
            var.set(self._PLACEHOLDER)
            entry.configure(text_color=COLORS['text_dim'])

    def _on_period_radio(self):
        """Al pulsar radio button fijo: desactiva modo custom y actualiza."""
        self._using_custom_range = False
        self._update_data()

    def _apply_custom_range(self):
        """Lee los OptionMenus y aplica el rango sin necesidad de teclado."""
        _PH = self._PLACEHOLDER
        start_dt_text = self.period_start.get().strip()
        end_dt_text   = self.period_end.get().strip()
        if start_dt_text == _PH: start_dt_text = ""
        if end_dt_text   == _PH: end_dt_text   = ""
        try:
            start_dt = datetime.strptime(start_dt_text, _DATE_FMT)
        except ValueError as e:
            custom_msgbox(self, f"Fecha de inicio inválida:\n{e}", "❌ Error")
            return

        try:
            end_dt = datetime.strptime(end_dt_text, _DATE_FMT)
        except ValueError as e:
            custom_msgbox(self, f"Fecha de fin inválida:\n{e}", "❌ Error")
            return

        if end_dt <= start_dt:
            custom_msgbox(self, "La fecha de fin debe ser\nposterior a la de inicio.", "⚠️ Rango inválido")
            return

        if (end_dt - start_dt).days > 90:
            custom_msgbox(self, "El rango no puede superar 90 días.", "⚠️ Rango demasiado amplio")
            return

        self._using_custom_range = True
        self._custom_start = start_dt
        self._custom_end   = end_dt

        logger.info(
            f"[HistoryWindow] Rango aplicado: "
            f"{start_dt.strftime('%Y-%m-%d %H:%M')} → {end_dt.strftime('%Y-%m-%d %H:%M')}"
        )
        self._update_data()

    def _update_data(self):
        """Actualiza estadísticas y gráficas según el modo activo."""
        if self._using_custom_range:
            start = self._custom_start
            end   = self._custom_end
            stats = self.analyzer.get_stats_between(start, end)
            rango_label = f"{start.strftime('%Y-%m-%d %H:%M')} → {end.strftime('%Y-%m-%d %H:%M')}"
            hours = None  # no se usa en modo custom
        else:
            period = self.period_var.get()
            hours  = {"24h": 24, "7d": 24 * 7, "30d": 24 * 30}[period]
            stats  = self.analyzer.get_stats(hours)
            rango_label = period

        total_records = self.logger.get_metrics_count()
        db_size       = self.logger.get_db_size_mb()

        stats_text = (
            f"• CPU promedio: {stats.get('cpu_avg', 0):.1f}%  "
            f"(min: {stats.get('cpu_min', 0):.1f}%, max: {stats.get('cpu_max', 0):.1f}%)\n"
            f"• RAM promedio: {stats.get('ram_avg', 0):.1f}%  "
            f"(min: {stats.get('ram_min', 0):.1f}%, max: {stats.get('ram_max', 0):.1f}%)\n"
            f"• Temp promedio: {stats.get('temp_avg', 0):.1f}°C  "
            f"(min: {stats.get('temp_min', 0):.1f}°C, max: {stats.get('temp_max', 0):.1f}°C)\n"
            f"• Red Down: {stats.get('down_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('down_min', 0):.2f}, max: {stats.get('down_max', 0):.2f})\n"
            f"• Red Up: {stats.get('up_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('up_min', 0):.2f}, max: {stats.get('up_max', 0):.2f})\n"
            f"• Disk Read: {stats.get('disk_read_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('disk_read_min', 0):.2f}, max: {stats.get('disk_read_max', 0):.2f})\n"
            f"• Disk Write: {stats.get('disk_write_avg', 0):.2f} MB/s  "
            f"(min: {stats.get('disk_write_min', 0):.2f}, max: {stats.get('disk_write_max', 0):.2f})\n"
            f"• PWM promedio: {stats.get('pwm_avg', 0):.0f}  "
            f"(min: {stats.get('pwm_min', 0):.0f}, max: {stats.get('pwm_max', 0):.0f})\n"
            f"• Actualizaciones disponibles promedio: {stats.get('updates_available_avg', 0):.2f}\n"
            f"• Actualizaciones disponibles (min: {stats.get('updates_available_min', 0)})\n"
            f"• Actualizaciones disponibles (max: {stats.get('updates_available_max', 0)})\n"
            f"• Muestras: {stats.get('total_samples', 0)} en {rango_label}\n"
            f"• Total registros: {total_records}  |  DB: {db_size:.2f} MB"
        )
        self.stats_label.configure(text=stats_text)

        if self._using_custom_range:
            self._update_graphs_between(self._custom_start, self._custom_end)
        else:
            self._update_graphs(hours)

    # ─────────────────────────────────────────────
    # Gráficas
    # ─────────────────────────────────────────────

    _METRICS = [
        ('cpu_percent',     'CPU %',           'primary'),
        ('ram_percent',     'RAM %',           'secondary'),
        ('temperature',     'Temp °C',         'danger'),
        ('net_download_mb', 'Red Down MB/s',   'primary'),
        ('net_upload_mb',   'Red Up MB/s',     'secondary'),
        ('disk_read_mb',    'Disk Read MB/s',  'primary'),
        ('disk_write_mb',   'Disk Write MB/s', 'secondary'),
        ('fan_pwm',         'PWM',             'warning'),
    ]

    def _update_graphs(self, hours: int):
        self.fig.clear()
        axes = [self.fig.add_subplot(8, 1, i) for i in range(1, 9)]
        for (metric, ylabel, color_key), ax in zip(self._METRICS, axes):
            ts, vals = self.analyzer.get_graph_data(metric, hours)
            self._draw_metric(ax, ts, vals, ylabel, COLORS[color_key])
        self.fig.tight_layout()
        self.canvas.draw()

    def _update_graphs_between(self, start: datetime, end: datetime):
        self.fig.clear()
        axes = [self.fig.add_subplot(8, 1, i) for i in range(1, 9)]
        for (metric, ylabel, color_key), ax in zip(self._METRICS, axes):
            ts, vals = self.analyzer.get_graph_data_between(metric, start, end)
            self._draw_metric(ax, ts, vals, ylabel, COLORS[color_key])
        self.fig.tight_layout()
        self.canvas.draw()

    def _draw_metric(self, ax, timestamps, values, ylabel: str, color: str):
        ax.set_facecolor(COLORS['bg_dark'])
        ax.tick_params(colors=COLORS['text'])
        ax.set_ylabel(ylabel, color=COLORS['text'])
        ax.set_xlabel('Tiempo', color=COLORS['text'])
        ax.grid(True, alpha=0.2)
        if timestamps:
            ax.plot(timestamps, values, color=color, linewidth=1.5)

    # ─────────────────────────────────────────────
    # Exportación
    # ─────────────────────────────────────────────

    def _export_csv(self):
        if self._using_custom_range:
            start = self._custom_start
            end   = self._custom_end
            label = f"custom_{start.strftime('%Y%m%d%H%M')}_{end.strftime('%Y%m%d%H%M')}"
            path  = str(EXPORTS_CSV_DIR / f"history_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            try:
                self.analyzer.export_to_csv_between(path, start, end)
                custom_msgbox(self, f"Datos exportados a:\n{path}", "✅ Exportado")
                try:
                    CleanupService().clean_csv()
                except Exception as ce:
                    logger.warning(f"[HistoryWindow] No se pudo limpiar CSV: {ce}")
            except Exception as e:
                custom_msgbox(self, f"Error al exportar:\n{e}", "❌ Error")
        else:
            period = self.period_var.get()
            hours  = {"24h": 24, "7d": 24 * 7, "30d": 24 * 30}[period]
            path   = str(EXPORTS_CSV_DIR / f"history_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            try:
                self.analyzer.export_to_csv(path, hours)
                custom_msgbox(self, f"Datos exportados a:\n{path}", "✅ Exportado")
                try:
                    CleanupService().clean_csv()
                except Exception as ce:
                    logger.warning(f"[HistoryWindow] No se pudo limpiar CSV: {ce}")
            except Exception as e:
                custom_msgbox(self, f"Error al exportar:\n{e}", "❌ Error")

    def _clean_old_data(self):
        """Fuerza un ciclo de limpieza completo a través de CleanupService."""
        status = self.cleanup_service.get_status()

        def do_clean():
            try:
                result = self.cleanup_service.force_cleanup()
                msg = (
                    f"Limpieza completada:\n\n"
                    f"• CSV eliminados: {result['deleted_csv']}\n"
                    f"• PNG eliminados: {result['deleted_png']}\n"
                    f"• BD limpiada: {'Sí' if result['db_ok'] else 'No'}"
                )
                custom_msgbox(self, msg, "✅ Limpiado")
                logger.info(f"[HistoryWindow] Limpieza manual completada: {result}")
                self._update_data()
            except Exception as e:
                logger.error(f"[HistoryWindow] Error en limpieza manual: {e}")
                custom_msgbox(self, f"Error al limpiar:\n{e}", "❌ Error")

        confirm_dialog(
            parent=self,
            text=(
                f"¿Forzar limpieza ahora?\n\n"
                f"• CSV actuales: {status['csv_count']} (límite: {status['max_csv']})\n"
                f"• PNG actuales: {status['png_count']} (límite: {status['max_png']})\n"
                f"• BD: registros >'{status['db_days']}' días\n\n"
                f"Esto liberará espacio en disco."
            ),
            title="⚠️ Confirmar Limpieza",
            on_confirm=do_clean,
            on_cancel=None
        )

    def _export_figure_image(self):
        
        try:
            save_dir = str(EXPORTS_SCR_DIR)
            os.makedirs(save_dir, exist_ok=True)
            filepath = os.path.join(
                save_dir,
                f"graficas_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.png"
            )
            self.fig.savefig(
                filepath, dpi=150,
                facecolor=self.fig.get_facecolor(),
                bbox_inches='tight'
            )
            logger.info(f"[HistoryWindow] Figura guardada: {filepath}")
            custom_msgbox(self, f"Imagen guardada en:\n\n{filepath}", "✅ Captura Guardada")
            try:
                CleanupService().clean_png()
            except Exception as ce:
                logger.warning(f"[HistoryWindow] No se pudo limpiar PNG: {ce}")
        except Exception as e:
            logger.error(f"[HistoryWindow] Error guardando imagen: {e}")
            custom_msgbox(self, f"Error al guardar la imagen: {e}", "❌ Error")

    # ─────────────────────────────────────────────
    # Eventos matplotlib
    # ─────────────────────────────────────────────

    def _on_click(self, event):
        if event.inaxes:
            logger.debug(f"Click en gráfica: x={event.xdata}, y={event.ydata}")

    def _on_release(self, event):
        pass

    def _on_motion(self, event):
        pass
```

## File: ui/windows/__init__.py
```python
"""
Paquete de ventanas secundarias
"""
from .fan_control import FanControlWindow
from .monitor import MonitorWindow
from .network import NetworkWindow
from .usb import USBWindow
from .launchers import LaunchersWindow
from .disk import DiskWindow
from .process_window import ProcessWindow
from .service import ServiceWindow
from .update import UpdatesWindow
from .history import HistoryWindow
from .theme_selector import ThemeSelector
from .homebridge import HomebridgeWindow
from .network_local import NetworkLocalWindow
from .pihole_window import PiholeWindow
from .alert_history import AlertHistoryWindow
from .display_window import DisplayWindow
from .vpn_window import VpnWindow
from .overview import OverviewWindow
from .led_window import LedWindow
from .camera_window import CameraWindow
from .services_manager_window import ServicesManagerWindow

__all__ = [
    'FanControlWindow',
    'MonitorWindow', 
    'NetworkWindow',
    'USBWindow',
    'LaunchersWindow',
    'DiskWindow',
    'ProcessWindow',
    'ServiceWindow',
    'UpdatesWindow',
    'HistoryWindow',
    'ThemeSelector',
    'HomebridgeWindow',
    'NetworkLocalWindow',
    'PiholeWindow',
    'AlertHistoryWindow',
    'DisplayWindow',
    'VpnWindow',
    'OverviewWindow',
    'LedWindow',
    'CameraWindow',
    'ServicesManagerWindow',
    
]
```

## File: ui/main_window.py
```python
"""
Ventana principal del sistema de monitoreo
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_X, DSI_Y, SCRIPTS_DIR
from ui.styles import StyleManager, make_futuristic_button
from ui.windows import (FanControlWindow, MonitorWindow, NetworkWindow, USBWindow, ProcessWindow, ServiceWindow, 
                        HistoryWindow, LaunchersWindow, ThemeSelector, DiskWindow, UpdatesWindow, HomebridgeWindow, 
                        NetworkLocalWindow, PiholeWindow, AlertHistoryWindow, DisplayWindow, VpnWindow, OverviewWindow,
                        LedWindow, CameraWindow, ServicesManagerWindow)
from ui.windows.log_viewer import LogViewerWindow
from ui.widgets import confirm_dialog, terminal_dialog
from utils.system_utils import SystemUtils
from utils.logger import get_logger
import sys
import os
from datetime import datetime
import psutil  # uptime badge
logger = get_logger(__name__)


class MainWindow:
    """Ventana principal del dashboard"""
    
    def __init__(self, root, system_monitor, fan_controller, 
                 fan_service, data_service, network_monitor,
                 disk_monitor, process_monitor, service_monitor, update_monitor, 
                 cleanup_service, homebridge_monitor, network_scanner, pihole_monitor, 
                 alert_service, display_service, vpn_monitor, led_service, hardware_monitor,
                 audio_alert_service,
                 update_interval=2000):
        self.root = root
        self.system_monitor = system_monitor
        self.fan_controller = fan_controller
        self.fan_service = fan_service
        self.data_service = data_service
        self.network_monitor = network_monitor
        self.disk_monitor = disk_monitor
        self.process_monitor = process_monitor
        self.service_monitor = service_monitor
        self.update_monitor = update_monitor
        self.cleanup_service = cleanup_service
        self.homebridge_monitor = homebridge_monitor
        self.network_scanner = network_scanner
        self.pihole_monitor = pihole_monitor
        self.alert_service = alert_service
        self.display_service = display_service
        self.vpn_monitor = vpn_monitor
        self.led_service = led_service
        self.hardware_monitor = hardware_monitor
        self.audio_alert_service = audio_alert_service
        
        self.update_interval = update_interval
        self.system_utils = SystemUtils()
        
        # Referencias a badges (canvas item ids)
        self._badges = {}  # key -> (canvas, oval_id, text_id)

        # Referencias a botones del menú para feedback visual
        self._menu_btns = {}  # label_key -> CTkButton

        # Referencias a ventanas secundarias
        self.fan_window = None
        self.monitor_window = None
        self.network_window = None
        self.usb_window = None
        self.launchers_window = None
        self.disk_window = None
        self.process_window = None
        self.service_window = None
        self.history_window = None
        self.update_window = None
        self.theme_window = None
        self.homebridge_window = None
        self.log_viewer_window = None
        self.network_local_window = None
        self.pihole_window = None
        self.alert_history_window = None
        self.display_window = None
        self.vpn_window = None
        self.overview_window = None
        self.led_window = None
        self.camera_window = None
        self.services_manager_window = None

        self._uptime_tick = 0  # uptime badge: contador para actualizar cada ~60s

        logger.info(f"[MainWindow] Dashboard iniciado en {self.system_utils.get_hostname()}")

        self._create_ui()
        self._start_update_loop()
    
    def _create_ui(self):
        """Crea la interfaz principal"""
        main_frame = ctk.CTkFrame(self.root, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ── Barra de cabecera: hostname (izq) + título (centro) + reloj (der) ──
        header_bar = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'], height=56)
        header_bar.pack(fill="x", padx=5, pady=(5, 0))
        header_bar.pack_propagate(False)

        hostname = self.system_utils.get_hostname()
        ctk.CTkLabel(
            header_bar,
            text=f"  {hostname}",
            text_color=COLORS['primary'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="w",
        ).pack(side="left", padx=12)

        ctk.CTkLabel(
            header_bar,
            text="SISTEMA DE MONITOREO",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['large'], "bold"),
            anchor="center",
        ).pack(side="left", expand=True)

        self._uptime_label = ctk.CTkLabel(  # uptime badge
            header_bar,
            text="⏱ --",
            text_color=COLORS['text_dim'],
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            anchor="e",
        )
        self._uptime_label.pack(side="right", padx=(0, 4))  # izq del reloj

        self._clock_label = ctk.CTkLabel(
            header_bar,
            text="00:00:00",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            anchor="e",
        )
        self._clock_label.pack(side="right", padx=12)

        # Separador
        ctk.CTkFrame(main_frame, fg_color=COLORS['border'], height=1, corner_radius=0).pack(fill="x", padx=5, pady=(0, 4))
        
        menu_container = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_medium'])
        menu_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.menu_canvas = ctk.CTkCanvas(
            menu_container,
            bg=COLORS['bg_medium'],
            highlightthickness=0
        )
        self.menu_canvas.pack(side="left", fill="both", expand=True)
        
        menu_scrollbar = ctk.CTkScrollbar(
            menu_container,
            orientation="vertical",
            command=self.menu_canvas.yview,
            width=30
        )
        menu_scrollbar.pack(side="right", fill="y")
        

        StyleManager.style_scrollbar_ctk(menu_scrollbar)
        
        self.menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
        
        self.menu_inner = ctk.CTkFrame(self.menu_canvas, fg_color=COLORS['bg_medium'])
        self.menu_canvas.create_window(
            (0, 0),
            window=self.menu_inner,
            anchor="nw",
            width=DSI_WIDTH - 50
        )
        
        self.menu_inner.bind(
            "<Configure>",
            lambda e: self.menu_canvas.configure(
                scrollregion=self.menu_canvas.bbox("all")
            )
        )
        
        self._create_menu_buttons()
    
    def _create_menu_buttons(self):
        """Crea los botones del menú principal"""
        buttons_config = [
            ("󰈐  Control Ventiladores", self.open_fan_control,     ["temp_fan"]),
            ("󰟖  LEDs RGB",      self.open_led_window,    []),
            ("󰚗  Monitor Placa",         self.open_monitor_window,  ["temp_monitor", "cpu", "ram"]),
            ("  Monitor Red",               self.open_network_window,  []),
            ("󱇰 Monitor USB",            self.open_usb_window,      []),
            ("  Monitor Disco",             self.open_disk_window,     ["disk"]),
            ("󱓞  Lanzadores",            self.open_launchers,       []),
            ("⚙️ Monitor Procesos",     self.open_process_window,  []),
            ("⚙️ Monitor Servicios",    self.open_service_window,  ["services"]),
            ("⚙️  Servicios Dashboard", self.open_services_manager, []),
            ("󱘿  Histórico Datos",       self.open_history_window,  []),
            ("󰆧  Actualizaciones",       self.open_update_window,   ["updates"]),
            ("󰟐  Homebridge",        self.open_homebridge,     ["hb_offline", "hb_on", "hb_fault"]),
            ("󰷐  Visor de Logs",        self.open_log_viewer,      []),
            ("🖧  Red Local",   self.open_network_local,   []),
            ("🕳  Pi-hole",   self.open_pihole,   ["pihole_offline"]),
            ("🔒  Gestor VPN", self.open_vpn_window, ["vpn_offline"]),
            ("  Historial Alertas",  self.open_alert_history,   []),
            ("󰃟  Brillo Pantalla", self.open_display_window, []),
            ("📊  Resumen Sistema", self.open_overview, []),
            ("📷  Cámara",        self.open_camera_window, []),
            ("󰔎  Cambiar Tema",          self.open_theme_selector,  []),
            ("  Reiniciar",                 self.restart_application,  []),
            ("󰿅  Salir",                 self.exit_application,     []),
        ]
        
        columns = 2
        
        for i, (text, command, badge_keys) in enumerate(buttons_config):
            row = i // columns
            col = i % columns
            
            btn = make_futuristic_button(
                self.menu_inner,
                text,
                command=command,
                font_size=FONT_SIZES['large'],
                width=30,
                height=15
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Guardar referencia para feedback visual
            self._menu_btns[text] = btn

            # Múltiples badges por botón, colocados de derecha a izquierda
            for j, key in enumerate(badge_keys):
                self._create_badge(btn, key, offset_index=j)
        
        for c in range(columns):
            self.menu_inner.grid_columnconfigure(c, weight=1)

    # ── Badges ────────────────────────────────────────────────────────────────

    # ── Feedback visual de botones ───────────────────────────────────────────

    def _btn_active(self, text_key):
        """Oscurece el botón mientras su ventana está abierta"""
        btn = self._menu_btns.get(text_key)
        if btn:
            try:
                btn.configure(fg_color=COLORS['bg_light'], border_color=COLORS['primary'], border_width=2)
            except Exception:
                pass

    def _btn_idle(self, text_key):
        """Restaura el botón a su estado normal"""
        btn = self._menu_btns.get(text_key)
        if btn:
            try:
                btn.configure(fg_color=COLORS['bg_dark'], border_color=COLORS['border'], border_width=1)
            except Exception:
                pass

    def _create_badge(self, btn, key, offset_index=0):
        """Crea un badge circular en la esquina superior-derecha del botón.
        offset_index separa horizontalmente múltiples badges en el mismo botón."""
        BADGE_SIZE = 36
        x_offset = -6 - offset_index * (BADGE_SIZE + 4)
        badge_canvas = tk.Canvas(
            btn,
            width=BADGE_SIZE,
            height=BADGE_SIZE,
            bg=COLORS['bg_dark'],
            highlightthickness=0,
            bd=0
        )
        badge_canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)

        oval = badge_canvas.create_oval(
            1, 1, BADGE_SIZE - 1, BADGE_SIZE - 1,
            fill=COLORS['danger'],
            outline=""
        )
        txt = badge_canvas.create_text(
            BADGE_SIZE // 2, BADGE_SIZE // 2,
            text="0",
            fill="white",
            font=(FONT_FAMILY, 13, "bold")
        )

        self._badges[key] = (badge_canvas, oval, txt, x_offset)
        badge_canvas.place_forget()

    # Umbrales de temperatura
    _TEMP_WARN = 60   # °C — badge naranja
    _TEMP_CRIT = 70   # °C — badge rojo

    # Umbrales CPU / RAM (%)
    _CPU_WARN  = 75
    _CPU_CRIT  = 90
    _RAM_WARN  = 75
    _RAM_CRIT  = 90

    # Umbrales disco (%)
    _DISK_WARN = 80
    _DISK_CRIT = 90

    def _update_badge(self, key, value, color=None):
        """Actualiza el valor y visibilidad de un badge."""
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        if value > 0:
            display = str(value) if value < 100 else "99+"
            canvas.itemconfigure(txt, text=display)
            if color is None:
                color = COLORS['danger'] if key == "services" else COLORS.get('warning', '#ffaa00')
            canvas.itemconfigure(oval, fill=color)
            txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
            canvas.itemconfigure(txt, fill=txt_color)
            canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)
        else:
            canvas.place_forget()
    
    # ── Apertura de ventanas ──────────────────────────────────────────────────

    def open_fan_control(self):
        """Abre la ventana de control de ventiladores"""
        if self.fan_window is None or not self.fan_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Control Ventiladores")
            self._btn_active("󰈐  Control Ventiladores")
            self.fan_window = FanControlWindow(self.root, self.fan_controller, self.system_monitor)
            self.fan_window.bind("<Destroy>", lambda e: self._btn_idle("󰈐  Control Ventiladores"))
        else:
            self.fan_window.lift()
    
    def open_monitor_window(self):
        """Abre la ventana de monitoreo del sistema"""
        if self.monitor_window is None or not self.monitor_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Placa")
            self._btn_active("󰚗  Monitor Placa")
            self.monitor_window = MonitorWindow(self.root, self.system_monitor, self.hardware_monitor)
            self.monitor_window.bind("<Destroy>", lambda e: self._btn_idle("󰚗  Monitor Placa"))
        else:
            self.monitor_window.lift()
    
    def open_network_window(self):
        """Abre la ventana de monitoreo de red"""
        if self.network_window is None or not self.network_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Red")
            self._btn_active("  Monitor Red")
            self.network_window = NetworkWindow(self.root, self.network_monitor)
            self.network_window.bind("<Destroy>", lambda e: self._btn_idle("  Monitor Red"))
        else:
            self.network_window.lift()
    
    def open_usb_window(self):
        """Abre la ventana de monitoreo USB"""
        if self.usb_window is None or not self.usb_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor USB")
            self._btn_active("󱇰 Monitor USB")
            self.usb_window = USBWindow(self.root)
            self.usb_window.bind("<Destroy>", lambda e: self._btn_idle("󱇰 Monitor USB"))
        else:
            self.usb_window.lift()
    
    def open_process_window(self):
        """Abre el monitor de procesos"""
        if self.process_window is None or not self.process_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Procesos")
            self._btn_active("⚙️ Monitor Procesos")
            self.process_window = ProcessWindow(self.root, self.process_monitor)
            self.process_window.bind("<Destroy>", lambda e: self._btn_idle("⚙️ Monitor Procesos"))
        else:
            self.process_window.lift()
    
    def open_service_window(self):
        """Abre el monitor de servicios"""
        if self.service_window is None or not self.service_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Servicios")
            self._btn_active("⚙️ Monitor Servicios")
            self.service_window = ServiceWindow(self.root, self.service_monitor)
            self.service_window.bind("<Destroy>", lambda e: self._btn_idle("⚙️ Monitor Servicios"))
        else:
            self.service_window.lift()
    
    def open_history_window(self):
        """Abre la ventana de histórico"""
        if self.history_window is None or not self.history_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Histórico Datos")
            self._btn_active("󱘿  Histórico Datos")
            self.history_window = HistoryWindow(self.root, self.cleanup_service)
            self.history_window.bind("<Destroy>", lambda e: self._btn_idle("󱘿  Histórico Datos"))
        else:
            self.history_window.lift()
    
    def open_launchers(self):
        """Abre la ventana de lanzadores"""
        if self.launchers_window is None or not self.launchers_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Lanzadores")
            self._btn_active("󱓞  Lanzadores")
            self.launchers_window = LaunchersWindow(self.root)
            self.launchers_window.bind("<Destroy>", lambda e: self._btn_idle("󱓞  Lanzadores"))
        else:
            self.launchers_window.lift()
    
    def open_theme_selector(self):
        """Abre el selector de temas"""
        if self.theme_window is None or not self.theme_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Cambiar Tema")
            self._btn_active("󰔎  Cambiar Tema")
            self.theme_window = ThemeSelector(self.root)
            self.theme_window.bind("<Destroy>", lambda e: self._btn_idle("󰔎  Cambiar Tema"))
        else:
            self.theme_window.lift()
    
    def open_disk_window(self):
        """Abre la ventana de monitor de disco"""
        if self.disk_window is None or not self.disk_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Monitor Disco")
            self._btn_active("  Monitor Disco")
            self.disk_window = DiskWindow(self.root, self.disk_monitor)
            self.disk_window.bind("<Destroy>", lambda e: self._btn_idle("  Monitor Disco"))
        else:
            self.disk_window.lift()
    
    def open_update_window(self):
        """Abre la ventana de actualizaciones"""
        if self.update_window is None or not self.update_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Actualizaciones")
            self._btn_active("󰆧  Actualizaciones")
            self.update_window = UpdatesWindow(self.root, self.update_monitor)
            self.update_window.bind("<Destroy>", lambda e: self._btn_idle("󰆧  Actualizaciones"))
        else:
            self.update_window.lift()
    
    def open_homebridge(self):
        """Abre la ventana de control de Homebridge"""
        if self.homebridge_window is None or not self.homebridge_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Homebridge")
            self._btn_active("󰟐  Homebridge")
            self.homebridge_window = HomebridgeWindow(self.root, self.homebridge_monitor)
            self.homebridge_window.bind("<Destroy>", lambda e: self._btn_idle("󰟐  Homebridge"))
        else:
            self.homebridge_window.lift()

    def open_log_viewer(self):
        """Abre el visor de logs del dashboard"""
        if self.log_viewer_window is None or not self.log_viewer_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Visor de Logs")
            self._btn_active("󰷐  Visor de Logs")
            self.log_viewer_window = LogViewerWindow(self.root)
            self.log_viewer_window.bind("<Destroy>", lambda e: self._btn_idle("󰷐  Visor de Logs"))
        else:
            self.log_viewer_window.lift()
    
    def open_network_local(self):
        """Abre el panel de red local."""
        if self.network_local_window is None or not self.network_local_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Red Local")
            self._btn_active("🖧  Red Local")
            self.network_local_window = NetworkLocalWindow(self.root)
            self.network_local_window.bind(
                "<Destroy>", lambda e: self._btn_idle("🖧  Red Local"))
        else:
            self.network_local_window.lift()
    def open_pihole(self):
        """Abre la ventana de Pi-hole."""
        if self.pihole_window is None or not self.pihole_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Pi-hole")
            self._btn_active("🕳  Pi-hole")
            self.pihole_window = PiholeWindow(self.root, self.pihole_monitor)
            self.pihole_window.bind("<Destroy>", lambda e: self._btn_idle("🕳  Pi-hole"))
        else:
            self.pihole_window.lift()
    
    def open_alert_history(self):
        """Abre el historial de alertas."""
        if self.alert_history_window is None or not self.alert_history_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Historial Alertas")
            self._btn_active("  Historial Alertas")
            self.alert_history_window = AlertHistoryWindow(self.root, self.alert_service)
            self.alert_history_window.bind(
                "<Destroy>", lambda e: self._btn_idle("  Historial Alertas"))
        else:
            self.alert_history_window.lift()
            
            
            
    def open_display_window(self):
        """Abre la ventana de control de brillo y apagado de pantalla."""
        if self.display_window is None or not self.display_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Brillo Pantalla")
            self._btn_active("󰃟  Brillo Pantalla")
            self.display_window = DisplayWindow(self.root, self.display_service)
            self.display_window.bind(
                "<Destroy>", lambda e: self._btn_idle("󰃟  Brillo Pantalla"))
        else:
            self.display_window.lift()
            
    def open_vpn_window(self):
        """Abre el gestor de VPN."""
        if self.vpn_window is None or not self.vpn_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Gestor VPN")
            self._btn_active("🔒  Gestor VPN")
            self.vpn_window = VpnWindow(self.root, self.vpn_monitor)
            self.vpn_window.bind(
                "<Destroy>", lambda e: self._btn_idle("🔒  Gestor VPN"))
        else:
            self.vpn_window.lift()
            
    def open_overview(self):
        """Abre la ventana de resumen del sistema."""
        if self.overview_window is None or not self.overview_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Resumen Sistema")
            self._btn_active("📊  Resumen Sistema")
            self.overview_window = OverviewWindow(
                self.root,
                system_monitor=self.system_monitor,
                service_monitor=self.service_monitor,
                pihole_monitor=self.pihole_monitor,
                network_monitor=self.network_monitor,
                disk_monitor=self.disk_monitor,
            )
            self.overview_window.bind(
                "<Destroy>", lambda e: self._btn_idle("📊  Resumen Sistema"))
        else:
            self.overview_window.lift()
            
    def open_led_window(self):
        """Abre la ventana de control de LEDs RGB."""
        if self.led_window is None or not self.led_window.winfo_exists():
            self._btn_active("󰟖  LEDs RGB")
            self.led_window = LedWindow(self.root, self.led_service)
            self.led_window.bind("<Destroy>", lambda e: self._btn_idle("󰟖  LEDs RGB"))
        else:
            self.led_window.lift()
    
    def open_camera_window(self):
        """Abre la ventana de cámara."""
        if self.camera_window is None or not self.camera_window.winfo_exists():
            self._btn_active("📷  Cámara")
            self.camera_window = CameraWindow(self.root)
            self.camera_window.bind("<Destroy>", lambda e: self._btn_idle("📷  Cámara"))
        else:
            self.camera_window.lift()

    def open_services_manager(self):
        """Abre la ventana de gestión de servicios del dashboard."""
        if self.services_manager_window is None or not self.services_manager_window.winfo_exists():
            logger.debug("[MainWindow] Abriendo: Servicios Dashboard")
            self._btn_active("⚙️  Servicios Dashboard")
            self.services_manager_window = ServicesManagerWindow(
                self.root,
                fan_service          = self.fan_service,
                system_monitor       = self.system_monitor,
                hardware_monitor     = self.hardware_monitor,
                service_monitor      = self.service_monitor,
                alert_service        = self.alert_service,
                audio_alert_service  = self.audio_alert_service,
                homebridge_monitor   = self.homebridge_monitor,
                pihole_monitor       = self.pihole_monitor,
                vpn_monitor          = self.vpn_monitor,
                data_service         = self.data_service,
                cleanup_service      = self.cleanup_service,
                display_service      = self.display_service,
                led_service          = self.led_service,
            )
            self.services_manager_window.bind(
                "<Destroy>", lambda e: self._btn_idle("⚙️  Servicios Dashboard"))
        else:
            self.services_manager_window.lift()

    

    
    # ── Salir / Reiniciar ─────────────────────────────────────────────────────

    def exit_application(self):
        """Cierra la aplicación con opciones de salida o apagado"""
        selection_window = ctk.CTkToplevel(self.root)
        selection_window.title("Opciones de Salida")
        selection_window.configure(fg_color=COLORS['bg_medium'])
        selection_window.geometry("450x280")
        selection_window.resizable(False, False)
        selection_window.overrideredirect(True)
        
        selection_window.update_idletasks()
        x = DSI_X + (450 // 2) - 40
        y = DSI_Y + (280 // 2) - 40
        selection_window.geometry(f"450x280+{x}+{y}")
        
        selection_window.transient(self.root)
        selection_window.after(150, selection_window.focus_set)
        selection_window.grab_set()
        
        main_frame = ctk.CTkFrame(selection_window, fg_color=COLORS['bg_medium'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="⚠️ ¿Qué deseas hacer?",
            text_color=COLORS['secondary'],
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold")
        )
        title_label.pack(pady=(10, 10))
        
        selection_var = ctk.StringVar(value="exit")
        
        options_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'])
        options_frame.pack(fill="x", pady=5, padx=20)
        
        exit_radio = ctk.CTkRadioButton(
            options_frame,
            text="  Salir de la aplicación",
            variable=selection_var,
            value="exit",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium']),
        )
        exit_radio.pack(anchor="w", padx=20, pady=12)
        
        shutdown_radio = ctk.CTkRadioButton(
            options_frame,
            text="󰐥  Apagar el sistema",
            variable=selection_var,
            value="shutdown",
            text_color=COLORS['text'],
            font=(FONT_FAMILY, FONT_SIZES['medium'])
        )
        shutdown_radio.pack(anchor="w", padx=20, pady=12)
        

        StyleManager.style_radiobutton_ctk(exit_radio, radiobutton_width=30, radiobutton_height=30)
        StyleManager.style_radiobutton_ctk(shutdown_radio, radiobutton_width=30, radiobutton_height=30)
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(side="bottom", fill="x", pady=(5, 10))
        
        def on_confirm():
            selected = selection_var.get()
            selection_window.destroy()
            
            if selected == "exit":
                def do_exit():
                    logger.info("[MainWindow] Cerrando dashboard por solicitud del usuario")
                    self.root.quit()
                    self.root.destroy()
                
                confirm_dialog(
                    parent=self.root,
                    text="¿Confirmar salir de la aplicación?",
                    title=" Confirmar Salida",
                    on_confirm=do_exit,
                    on_cancel=None
                )
            
            else:  # shutdown
                def do_shutdown():
                    logger.info("[MainWindow] Iniciando apagado del sistema")
                    shutdown_script = str(SCRIPTS_DIR / "apagado.sh")
                    terminal_dialog(
                        parent=self.root,
                        script_path=shutdown_script,
                        title="󰐥  APAGANDO SISTEMA..."
                    )
                
                confirm_dialog(
                    parent=self.root,
                    text="⚠️ ¿Confirmar APAGAR el sistema?\n\nEsta acción apagará completamente el equipo.",
                    title=" Confirmar Apagado",
                    on_confirm=do_shutdown,
                    on_cancel=None
                )
        
        def on_cancel():
            logger.debug("[MainWindow] Diálogo de salida cancelado")
            selection_window.destroy()
        
        cancel_btn = make_futuristic_button(
            buttons_frame,
            text="Cancelar",
            command=on_cancel,
            width=20,
            height=10
        )
        cancel_btn.pack(side="right", padx=5)
        
        confirm_btn = make_futuristic_button(
            buttons_frame,
            text="Continuar",
            command=on_confirm,
            width=15,
            height=8
        )
        confirm_btn.pack(side="right", padx=5)
        
        selection_window.bind("<Escape>", lambda e: on_cancel())
    
    def restart_application(self):
        """Reinicia la aplicación"""
        def do_restart():

            logger.info("[MainWindow] Reiniciando dashboard")
            self.root.quit()
            self.root.destroy()
            os.execv(sys.executable, [sys.executable, os.path.abspath(sys.argv[0])] + sys.argv[1:])
        
        confirm_dialog(
            parent=self.root,
            text="¿Reiniciar el dashboard?\n\nSe aplicarán los cambios realizados.",
            title=" Reiniciar Dashboard",
            on_confirm=do_restart,
            on_cancel=None
        )
    
    # ── Loop de actualización ─────────────────────────────────────────────────

    def _tick_clock(self):
        """Actualiza el reloj cada segundo y el uptime cada minuto."""
        self._clock_label.configure(text=datetime.now().strftime("%H:%M:%S"))

        # Uptime badge: recalcular cada 60 ticks (~60s) y en el primero
        self._uptime_tick += 1
        if self._uptime_tick == 1 or self._uptime_tick >= 60:
            self._uptime_tick = 1
            try:
                import time as _time
                uptime_s = _time.time() - psutil.boot_time()
                days    = int(uptime_s // 86400)
                hours   = int((uptime_s % 86400) // 3600)
                minutes = int((uptime_s % 3600) // 60)
                uptime_str = f"⏱ {days}d {hours}h" if days > 0 else f"⏱ {hours}h {minutes}m"
                self._uptime_label.configure(text=uptime_str)
            except Exception:
                pass

        self.root.after(1000, self._tick_clock)

    def _start_update_loop(self):
        """Inicia el bucle de actualización"""
        self._tick_clock()
        self._update()
    
    def _update(self):
        """Actualiza los badges del menú. Solo lee cachés — nunca bloquea la UI."""
        try:
            pending = self.update_monitor.cached_result.get('pending', 0)
            self._update_badge("updates", pending)

            # Homebridge — lectura desde memoria, sin HTTP
            self._update_badge("hb_offline", self.homebridge_monitor.get_offline_count())
            self._update_badge(
                "hb_on",
                self.homebridge_monitor.get_on_count(),
                color=COLORS.get('warning', '#ffaa00'),
            )
            self._update_badge("hb_fault", self.homebridge_monitor.get_fault_count())
            self._update_badge("pihole_offline", self.pihole_monitor.get_offline_count())
            self._update_badge("vpn_offline", self.vpn_monitor.get_offline_count())

        except Exception:
            pass

        try:
            # get_stats() ahora es lectura de caché — no lanza systemctl
            stats  = self.service_monitor.get_stats()
            failed = stats.get('failed', 0)
            self._update_badge("services", failed)
        except Exception:
            pass

        try:
            # get_current_stats() ahora es lectura de caché — no llama psutil
            sys_stats = self.system_monitor.get_current_stats()

            # Temperatura
            temp = sys_stats['temp']
            if temp >= self._TEMP_CRIT:
                temp_color = COLORS['danger']
                show_temp  = True
            elif temp >= self._TEMP_WARN:
                temp_color = COLORS.get('warning', '#ffaa00')
                show_temp  = True
            else:
                show_temp = False

            if show_temp:
                self._update_badge_temp("temp_fan",     int(temp), temp_color)
                self._update_badge_temp("temp_monitor", int(temp), temp_color)
            else:
                self._update_badge("temp_fan",     0)
                self._update_badge("temp_monitor", 0)

            # CPU
            cpu = sys_stats['cpu']
            if cpu >= self._CPU_CRIT:
                self._update_badge("cpu", int(cpu), COLORS['danger'])
            elif cpu >= self._CPU_WARN:
                self._update_badge("cpu", int(cpu), COLORS.get('warning', '#ffaa00'))
            else:
                self._update_badge("cpu", 0)

            # RAM
            ram = sys_stats['ram']
            if ram >= self._RAM_CRIT:
                self._update_badge("ram", int(ram), COLORS['danger'])
            elif ram >= self._RAM_WARN:
                self._update_badge("ram", int(ram), COLORS.get('warning', '#ffaa00'))
            else:
                self._update_badge("ram", 0)

            # Disco
            disk = sys_stats['disk_usage']
            if disk >= self._DISK_CRIT:
                self._update_badge("disk", int(disk), COLORS['danger'])
            elif disk >= self._DISK_WARN:
                self._update_badge("disk", int(disk), COLORS.get('warning', '#ffaa00'))
            else:
                self._update_badge("disk", 0)

        except Exception:
            pass

        self.root.after(self.update_interval, self._update)


    def _update_badge_temp(self, key, temp, color):
        """Muestra la temperatura en el badge con el color indicado."""
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        canvas.itemconfigure(txt, text=f"{temp}°")
        canvas.itemconfigure(oval, fill=color)
        txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
        canvas.itemconfigure(txt, fill=txt_color)
        canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)
```
