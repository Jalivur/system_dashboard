"""
Ventana de información estática del hardware.
Muestra datos del sistema que no cambian en runtime:
modelo de CPU, núcleos, RAM total, kernel, arquitectura,
hostname y uptime (este último se refresca cada 60s).

No requiere core service propio — los datos estáticos se leen
una sola vez al abrir la ventana via psutil/platform/subprocess.
El uptime se lee del caché de SystemMonitor.
"""
import platform
import subprocess
import psutil
import threading
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons)
from ui.styles import StyleManager, make_window_header
from utils.logger import get_logger

logger = get_logger(__name__)

_UPTIME_EVERY = 60


def _read_cpu_model() -> str:
    """Lee el modelo de CPU desde /proc/cpuinfo."""
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Model name") or line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("Model") or line.startswith("Hardware"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return platform.processor() or "Desconocido"


def _read_pi_model() -> str:
    """Lee el modelo de Raspberry Pi desde /proc/device-tree/model."""
    try:
        with open("/proc/device-tree/model", "r") as f:
            return f.read().strip().rstrip("\x00")
    except Exception:
        return ""


def _read_os() -> str:
    """Devuelve el nombre del SO."""
    try:
        result = subprocess.run(
            ["lsb_release", "-ds"],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            return result.stdout.strip().strip('"')
    except Exception:
        pass
    return platform.system()


def _gather_static_info() -> dict:
    """Recopila toda la información estática del hardware."""
    vm          = psutil.virtual_memory()
    ram_gb      = vm.total / (1024 ** 3)
    cpu_count   = psutil.cpu_count(logical=False) or 1
    cpu_threads = psutil.cpu_count(logical=True) or cpu_count
    freq        = psutil.cpu_freq()
    freq_str    = f"{freq.max / 1000:.2f} GHz" if freq else "N/D"

    return {
        "pi_model":    _read_pi_model(),
        "cpu_model":   _read_cpu_model(),
        "cpu_cores":   cpu_count,
        "cpu_threads": cpu_threads,
        "cpu_freq":    freq_str,
        "ram_total":   f"{ram_gb:.1f} GB",
        "kernel":      platform.release(),
        "arch":        platform.machine(),
        "os":          _read_os(),
        "hostname":    platform.node(),
    }


class HardwareInfoWindow(ctk.CTkToplevel):
    """Ventana de información del hardware — datos estáticos + uptime dinámico."""

    def __init__(self, parent, system_monitor):
        """Inicializa la ventana de información del hardware.

        Args:
            parent: Ventana padre (CTkToplevel).
            system_monitor: Instancia para obtener uptime dinámico.
        """
        super().__init__(parent)
        self._system_monitor = system_monitor

        self.title("Información del Hardware")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._uptime_tick  = 0
        self._uptime_label = None
        
        self._info = {}
        self._create_ui()

        threading.Thread(
            target=self._load_info,
            daemon=True,
            name="HWInfoLoad"
        ).start()
        logger.info("[HardwareInfoWindow] Ventana abierta")
        
    def _load_info(self) -> None:
        """Carga info estática en background y rellena la UI."""
        info = _gather_static_info()
        if self.winfo_exists():
            self.after(0, lambda: self._populate_info(info))
    
    def _populate_info(self, info: dict) -> None:
        """Rellena la UI con los datos ya cargados (main thread)."""
        if not self.winfo_exists():
            return
        self._info = info
        # Limpiar skeleton
        for w in self._inner.winfo_children():
            w.destroy()
        # Reconstruir con datos reales
        self._build_content(self._inner)
        self._uptime_tick = 0
        self._tick_uptime()
    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):
        """Crea la estructura de la interfaz de usuario principal con scroll y placeholder de carga."""
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="INFORMACIÓN DEL HARDWARE", on_close=self.destroy)

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

        self._inner = inner    # guarda referencia para _populate_info
        self._show_loading(inner)
    def _show_loading(self, parent) -> None:
        """Muestra texto de carga mientras _gather_static_info trabaja."""
        ctk.CTkLabel(
            parent,
            text="Cargando información del hardware...",
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text_dim'],
        ).pack(pady=40)
    
    def _build_content(self, inner):
        """Construye secciones de contenido con datos reales del hardware (Sistema, CPU, RAM, Uptime).

        Args:
            inner: Frame contenedor para los widgets de secciones.
        """
        info = self._info

        # ── Tarjeta: Placa / Sistema ──────────────────────────────────────────
        if info["pi_model"]:
            self._section(inner, "" + Icons.TAB_HARDWARE + "️  Placa", [
                ("Modelo",       info["pi_model"]),
                ("Hostname",     info["hostname"]),
                ("SO",           info["os"]),
                ("Arquitectura", info["arch"]),
                ("Kernel",       info["kernel"]),
            ])
        else:
            self._section(inner, "" + Icons.TAB_HARDWARE + "️  Sistema", [
                ("Hostname",     info["hostname"]),
                ("SO",           info["os"]),
                ("Arquitectura", info["arch"]),
                ("Kernel",       info["kernel"]),
            ])

        # ── Tarjeta: Procesador ───────────────────────────────────────────────
        self._section(inner, "" + Icons.FIRE + "  Procesador", [
            ("Modelo",           info["cpu_model"]),
            ("Núcleos físicos",  str(info["cpu_cores"])),
            ("Hilos (lógicos)",  str(info["cpu_threads"])),
            ("Frecuencia máx.",  info["cpu_freq"]),
        ])

        # ── Tarjeta: Memoria ──────────────────────────────────────────────────
        self._section(inner, f"{Icons.RAM}  Memoria RAM", [
            ("Total instalada", info["ram_total"]),
        ])

        # ── Tarjeta: Uptime (dinámica) ────────────────────────────────────────
        uptime_card = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        uptime_card.pack(fill="x", padx=10, pady=(0, 6))

        ctk.CTkLabel(
            uptime_card,
            text="" + Icons.UPTIME + "️  Uptime",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(anchor="w", padx=14, pady=(10, 4))

        self._uptime_label = ctk.CTkLabel(
            uptime_card,
            text="--",
            font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold"),
            text_color=COLORS['secondary'],
            anchor="center",
        )
        self._uptime_label.pack(pady=(0, 14))

    # ── Helper de sección ─────────────────────────────────────────────────────

    def _section(self, parent, title: str, rows: list):
        """Crea una tarjeta de sección con filas etiqueta-valor."""
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(0, 6))

        ctk.CTkLabel(
            card,
            text=title,
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(anchor="w", padx=14, pady=(10, 6))

        ctk.CTkFrame(card, fg_color=COLORS['border'], height=1,
                     corner_radius=0).pack(fill="x", padx=14, pady=(0, 6))

        for label, value in rows:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=3)

            ctk.CTkLabel(
                row,
                text=label,
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'],
                anchor="w",
                width=160,
            ).pack(side="left")

            ctk.CTkLabel(
                row,
                text=value,
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                text_color=COLORS['text'],
                anchor="w",
                wraplength=DSI_WIDTH - 230,
            ).pack(side="left", padx=(8, 0))

        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

    # ── Uptime dinámico ───────────────────────────────────────────────────────

    def _tick_uptime(self):
        """Refresca el uptime cada _UPTIME_EVERY segundos."""
        if not self.winfo_exists():
            return
        self._uptime_tick += 1
        if self._uptime_tick == 1 or self._uptime_tick >= _UPTIME_EVERY:
            self._uptime_tick = 1
            try:
                uptime_str = self._system_monitor.get_current_stats().get(
                    "uptime_str", "--")
                uptime_str = uptime_str.lstrip("" + Icons.UPTIME + " ").strip()
                if self._uptime_label:
                    self._uptime_label.configure(text=uptime_str)
            except Exception:
                pass
        self.after(1000, self._tick_uptime)
