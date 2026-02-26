This file is a merged representation of a subset of the codebase, containing files not matching ignore patterns, combined into a single document by Repomix.

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
- Files matching these patterns are excluded: /home/jalivur/Documents/system_dashboard/fix_timestamps.py, /home/jalivur/Documents/system_dashboard/test_logging.py, /home/jalivur/Documents/system_dashboard/integration_fase1.py
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
config/
  __init__.py
  settings.py
  themes.py
core/
  __init__.py
  alert_service.py
  cleanup_service.py
  data_analyzer.py
  data_collection_service.py
  data_logger.py
  disk_monitor.py
  fan_auto_service.py
  fan_controller.py
  homebridge_monitor.py
  network_monitor.py
  network_scanner.py
  pihole_monitor.py
  process_monitor.py
  service_monitor.py
  system_monitor.py
  update_monitor.py
ui/
  widgets/
    __init__.py
    dialogs.py
    graphs.py
  windows/
    __init__.py
    alert_history.py
    disk.py
    fan_control.py
    history.py
    homebridge.py
    launchers.py
    log_viewer.py
    monitor.py
    network_local.py
    network.py
    pihole_window.py
    process_window.py
    service.py
    theme_selector.py
    update.py
    usb.py
  __init__.py
  main_window.py
  styles.py
utils/
  __init__.py
  file_manager.py
  logger.py
  system_utils.py
.gitignore
COMPATIBILIDAD.md
create_desktop_launcher.sh
IDEAS_EXPANSION.md
INDEX.md
INSTALL_GUIDE.md
install_system.sh
install.sh
INTEGRATION_GUIDE.md
main.py
migratelogger.sh
QUICKSTART.md
README.md
REQUIREMENTS.md
requirements.txt
setup.py
THEMES_GUIDE.md
```

# Files

## File: core/network_scanner.py
````python
"""
Escáner de red local usando arp-scan.
Requiere: sudo arp-scan (disponible en Kali por defecto)

Ejecuta arp-scan en un thread de background para no bloquear la UI.
"""
import subprocess
import threading
import socket
import re
import time
from typing import List, Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Timeout para arp-scan (segundos)
ARP_TIMEOUT = 15

# Regex para parsear líneas de arp-scan:
# Regex actualizado — fabricante con paréntesis opcional
_ARP_LINE = re.compile(
    r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\t([\da-fA-F:]{17})\t(.*)$'
)

class NetworkScanner:
    """
    Escáner de red local con arp-scan.

    Uso:
        scanner = NetworkScanner()
        scanner.scan()                    # lanza en background
        devices = scanner.get_devices()   # lee caché (no bloquea)
        status  = scanner.get_status()    # 'idle' | 'scanning' | 'done' | 'error'
    """

    def __init__(self):
        self._devices: List[Dict] = []
        self._status  = "idle"     # idle | scanning | done | error
        self._error   = ""
        self._last_scan: Optional[float] = None
        self._lock    = threading.Lock()

    # ── API pública ───────────────────────────────────────────────────────────

    def scan(self) -> None:
        """Lanza el escaneo en background. Si ya hay uno en curso, no hace nada."""
        with self._lock:
            if self._status == "scanning":
                return
            self._status = "scanning"
        threading.Thread(target=self._do_scan, daemon=True, name="ARPScan").start()
        logger.info("[NetworkScanner] Escaneo iniciado")

    def get_devices(self) -> List[Dict]:
        """Devuelve la lista de dispositivos del último escaneo (caché)."""
        with self._lock:
            return list(self._devices)

    def get_status(self) -> str:
        """Estado actual: 'idle' | 'scanning' | 'done' | 'error'."""
        with self._lock:
            return self._status

    def get_error(self) -> str:
        """Mensaje de error si status == 'error'."""
        with self._lock:
            return self._error

    def get_last_scan_age(self) -> Optional[float]:
        """Segundos desde el último escaneo completado. None si nunca se ha escaneado."""
        with self._lock:
            if self._last_scan is None:
                return None
            return time.time() - self._last_scan

    # ── Escaneo ───────────────────────────────────────────────────────────────

    def _do_scan(self) -> None:
        """Ejecuta arp-scan y parsea el resultado."""
        try:
            result = subprocess.run(
                [
                    "sudo", "arp-scan", "--localnet",
                    "--ouifile=/usr/share/arp-scan/ieee-oui.txt",
                    "--macfile=/etc/arp-scan/mac-vendor.txt",
                ],
                capture_output=True,
                text=True,
                timeout=ARP_TIMEOUT,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"arp-scan salió con código {result.returncode}: {result.stderr.strip()}"
                )
            devices = self._parse_output(result.stdout)
            with self._lock:
                self._devices    = devices
                self._status     = "done"
                self._last_scan  = time.time()
                self._error      = ""
            logger.info("[NetworkScanner] Escaneo completado — %d dispositivos", len(devices))

        except subprocess.TimeoutExpired:
            with self._lock:
                self._status = "error"
                self._error  = f"Timeout ({ARP_TIMEOUT}s) — red puede ser grande"
            logger.warning("[NetworkScanner] Timeout en arp-scan")

        except FileNotFoundError:
            with self._lock:
                self._status = "error"
                self._error  = "arp-scan no encontrado — instalar con: sudo apt install arp-scan"
            logger.error("[NetworkScanner] arp-scan no instalado")

        except Exception as e:
            with self._lock:
                self._status = "error"
                self._error  = str(e)
            logger.error("[NetworkScanner] Error en escaneo: %s", e)

    def _parse_output(self, output: str) -> list:
        devices = []
        for line in output.splitlines():
            line = line.strip()
            # Ignorar líneas de cabecera, pie y vacías
            if not line:
                continue
            if line.startswith(('Interface:', 'Starting', 'WARNING', 'Ending')):
                continue
            if 'packets' in line or 'hosts' in line:
                continue

            m = _ARP_LINE.match(line)
            if not m:
                continue

            ip     = m.group(1)
            mac    = m.group(2).upper()
            vendor = m.group(3).strip().strip('()')  # quita los paréntesis de (Unknown)
            vendor = vendor if vendor and vendor.lower() != 'unknown' else ""

            hostname = self._resolve_hostname(ip)
            devices.append({
                "ip":       ip,
                "mac":      mac,
                "vendor":   vendor,
                "hostname": hostname,
            })

        devices.sort(key=lambda d: tuple(int(x) for x in d["ip"].split(".")))
        return devices

    @staticmethod
    def _resolve_hostname(ip: str) -> str:
        """Intenta resolver el hostname de una IP. Devuelve '' si falla."""
        try:
            return socket.gethostbyaddr(ip)[0]
        except Exception:
            return ""
````

## File: core/pihole_monitor.py
````python
"""
Monitor de Pi-hole v6.
Sondea la API REST de Pi-hole v6 cada POLL_INTERVAL_S segundos.
Credenciales leídas desde .env: PIHOLE_HOST, PIHOLE_PORT, PIHOLE_PASSWORD.

Sin dependencias nuevas — usa urllib de la stdlib.
"""
import json
import os
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Carga de .env ─────────────────────────────────────────────────────────────
def _load_env():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=False)
    except ImportError:
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value

_load_env()

PIHOLE_HOST     = os.environ.get("PIHOLE_HOST",     "")
PIHOLE_PORT     = int(os.environ.get("PIHOLE_PORT", "80"))
PIHOLE_PASSWORD = os.environ.get("PIHOLE_PASSWORD", "")

POLL_INTERVAL_S  = 60
REQUEST_TIMEOUT  = 5
SESSION_VALIDITY = 1800  # segundos — renovar antes de que expire

_EMPTY_STATS: Dict = {
    "status":          "unknown",
    "queries_today":   0,
    "blocked_today":   0,
    "percent_blocked": 0.0,
    "domains_blocked": 0,
    "unique_clients":  0,
    "reachable":       False,
}


class PiholeMonitor:
    """
    Monitor de Pi-hole v6 con sondeo en background.
    Autenticación por sesión (sid) con renovación automática antes de expirar.
    """

    def __init__(self):
        self._stats: Dict       = dict(_EMPTY_STATS)
        self._sid: Optional[str] = None
        self._sid_obtained: Optional[float] = None  # timestamp de cuando se obtuvo
        self._stats_lock        = threading.Lock()
        self._sid_lock          = threading.Lock()
        self._running           = False
        self._stop_evt          = threading.Event()
        self._thread: Optional[threading.Thread] = None

        if not PIHOLE_HOST:
            logger.warning(
                "[PiholeMonitor] PIHOLE_HOST no configurado en .env — monitor desactivado"
            )
        else:
            logger.info(
                "[PiholeMonitor] Inicializado — http://%s:%d (v6)", PIHOLE_HOST, PIHOLE_PORT
            )

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        if self._running or not PIHOLE_HOST:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, daemon=True, name="PiholePoll")
        self._thread.start()
        logger.info("[PiholeMonitor] Sondeo iniciado (cada %ds)", POLL_INTERVAL_S)

    def stop(self) -> None:
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=REQUEST_TIMEOUT + 1)
        self._logout()
        logger.info("[PiholeMonitor] Sondeo detenido")

    def _poll_loop(self) -> None:
        while self._running:
            try:
                self._fetch()
            except Exception as e:
                logger.error("[PiholeMonitor] Error en poll_loop: %s", e)
            self._stop_evt.wait(timeout=POLL_INTERVAL_S)
            if self._stop_evt.is_set():
                break

    # ── Autenticación ─────────────────────────────────────────────────────────

    def _authenticate(self) -> bool:
        """Obtiene un sid de sesión. Devuelve True si tiene éxito."""
        if not PIHOLE_PASSWORD:
            # Sin contraseña — Pi-hole puede permitir acceso anónimo
            logger.debug("[PiholeMonitor] Sin contraseña configurada — intentando sin auth")
            return True

        payload = json.dumps({"password": PIHOLE_PASSWORD}).encode("utf-8")
        req = urllib.request.Request(
            f"http://{PIHOLE_HOST}:{PIHOLE_PORT}/api/auth",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                sid = data.get("session", {}).get("sid")
                if sid:
                    with self._sid_lock:
                        self._sid         = sid
                        self._sid_obtained = time.time()
                    logger.info("[PiholeMonitor] Autenticación correcta (sid obtenido)")
                    return True
                logger.warning("[PiholeMonitor] Respuesta sin sid: %s", data)
                return False
        except Exception as e:
            logger.error("[PiholeMonitor] Error de autenticación: %s", e)
            return False

    def _sid_valid(self) -> bool:
        """True si el sid existe y no ha expirado (con margen de 60s)."""
        with self._sid_lock:
            if not self._sid or self._sid_obtained is None:
                return False
            return (time.time() - self._sid_obtained) < (SESSION_VALIDITY - 60)

    def _get_sid(self) -> Optional[str]:
        """Devuelve el sid válido, autenticando si es necesario."""
        if not self._sid_valid():
            if not self._authenticate():
                return None
        with self._sid_lock:
            return self._sid

    def _logout(self) -> None:
        """Cierra la sesión en Pi-hole al parar el monitor."""
        with self._sid_lock:
            sid = self._sid
            self._sid = None
        if not sid:
            return
        try:
            req = urllib.request.Request(
                f"http://{PIHOLE_HOST}:{PIHOLE_PORT}/api/auth",
                headers={"sid": sid},
                method="DELETE",
            )
            urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT)
            logger.debug("[PiholeMonitor] Sesión cerrada correctamente")
        except Exception:
            pass

    # ── Fetch ─────────────────────────────────────────────────────────────────

    def _fetch(self) -> None:
        """Llama a la API v6 de Pi-hole y actualiza la caché."""
        try:
            sid = self._get_sid()
            headers = {"sid": sid} if sid else {}

            req = urllib.request.Request(
                f"http://{PIHOLE_HOST}:{PIHOLE_PORT}/api/stats/summary",
                headers=headers,
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            # Estructura de respuesta v6:
            # {"queries": {"total": X, "blocked": X, "percent_blocked": X, ...},
            #  "clients": {"active": X, ...},
            #  "gravity": {"domains_being_blocked": X}}
            queries  = data.get("queries",  {})
            clients  = data.get("clients",  {})
            gravity  = data.get("gravity",  {})

            stats = {
                "status":          "enabled",  # si llegamos aquí, está activo
                "queries_today":   int(queries.get("total",            0)),
                "blocked_today":   int(queries.get("blocked",          0)),
                "percent_blocked": float(queries.get("percent_blocked", 0.0)),
                "domains_blocked": int(gravity.get("domains_being_blocked", 0)),
                "unique_clients":  int(clients.get("active",           0)),
                "reachable":       True,
            }
            with self._stats_lock:
                self._stats = stats
            logger.debug(
                "[PiholeMonitor] OK — %d queries, %.1f%% bloqueado",
                stats["queries_today"], stats["percent_blocked"]
            )

        except urllib.error.HTTPError as e:
            if e.code == 401:
                # Sesión expirada — forzar reautenticación en el próximo ciclo
                logger.warning("[PiholeMonitor] Sesión expirada (401) — renovando")
                with self._sid_lock:
                    self._sid = None
            else:
                logger.warning("[PiholeMonitor] HTTP %d en /api/stats/summary", e.code)
            with self._stats_lock:
                self._stats = {**_EMPTY_STATS, "reachable": False}

        except Exception as e:
            with self._stats_lock:
                self._stats = {**_EMPTY_STATS, "reachable": False}
            logger.warning("[PiholeMonitor] Sin conexión con Pi-hole: %s", e)

    # ── API pública ───────────────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        """Devuelve las estadísticas en caché. Sin petición HTTP."""
        with self._stats_lock:
            return dict(self._stats)

    def is_reachable(self) -> bool:
        with self._stats_lock:
            return self._stats.get("reachable", False)

    def is_enabled(self) -> bool:
        with self._stats_lock:
            return self._stats.get("status") == "enabled"

    def get_offline_count(self) -> int:
        """Para badge: 1 si Pi-hole no responde, 0 si ok."""
        with self._stats_lock:
            if not self._stats.get("reachable", False) and PIHOLE_HOST:
                return 1
        return 0
````

## File: ui/widgets/graphs.py
````python
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
````

## File: ui/windows/alert_history.py
````python
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
````

## File: ui/windows/network_local.py
````python
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
````

## File: ui/windows/pihole_window.py
````python
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
````

## File: ui/__init__.py
````python

````

## File: .gitignore
````
# ============================================
# System Dashboard - .gitignore
# ============================================
# 
# Excluye archivos temporales, compilados, 
# datos personales y configuraciones locales
#
# ============================================

# ============================================
# Python
# ============================================

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Virtual Environments
venv/
env/
ENV/
env.bak/
venv.bak/
.venv/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/


# ============================================
# IDEs y Editores
# ============================================

# VSCode
.vscode/
*.code-workspace

# PyCharm
.idea/
*.iml
*.iws

# Sublime Text
*.sublime-project
*.sublime-workspace

# Vim
*.swp
*.swo
*~
.*.sw[op]

# Emacs
*~
\#*\#
.\#*

# Nano
*.save
*.swp


# ============================================
# Sistema Operativo
# ============================================

# macOS
.DS_Store
.AppleDouble
.LSOverride
Icon
._*
.DocumentRevisions-V100
.fseventsd
.Spotlight-V100
.TemporaryItems
.Trashes
.VolumeIcon.icns
.com.apple.timemachine.donotpresent

# Windows
Thumbs.db
Thumbs.db:encryptable
ehthumbs.db
ehthumbs_vista.db
*.stackdump
[Dd]esktop.ini
$RECYCLE.BIN/
*.cab
*.msi
*.msix
*.msm
*.msp
*.lnk

# Linux
.directory
.Trash-*
.nfs*


# ============================================
# Archivos del Proyecto
# ============================================

# Datos persistentes y estado
data/
!data/.gitkeep
*.json
!requirements.json
!package.json
fan_state.json
fan_curve.json
theme_config.json

# Logs
*.log
logs/
*.log.*

# Archivos temporales
*.tmp
*.temp
*.bak
*.backup
*~
.~*

# Scripts personales del usuario
scripts/
!scripts/.gitkeep
!scripts/README.md

# Configuración local
.env
.env.local
.env.*.local
config.local.py
settings.local.py


# ============================================
# Documentación y Builds
# ============================================

# Sphinx documentation
docs/_build/
docs/_static/
docs/_templates/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py


# ============================================
# Específico del Dashboard
# ============================================

# Capturas de pantalla de desarrollo
screenshots/
*.png
*.jpg
*.jpeg
!docs/images/
!assets/images/

# Archivos de calibración de hardware
calibration/
*.calibration

# Datos de sensores históricos
sensor_data/
historical_data/

# Backups automáticos
backups/
*.backup

# Testing local
test_output/
test_results/


# ============================================
# Dependencias y Builds
# ============================================

# Node modules (si usas Node para algo)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
package-lock.json
yarn.lock

# Compiled files
*.pyc
*.pyo
*.pyd


# ============================================
# Git
# ============================================

# Parches
*.patch
*.diff

# Merge files
*.orig


# ============================================
# Archivos Sensibles
# ============================================

# API Keys y Secretos
secrets.py
secrets.json
.secrets
api_keys.txt
credentials.json

# SSH Keys
*.pem
*.key
id_rsa
id_rsa.pub

# Certificados
*.crt
*.cer
*.p12


# ============================================
# Base de Datos
# ============================================

# SQLite
*.db
*.sqlite
*.sqlite3
*.db-journal


# ============================================
# Compresión y Empaquetado
# ============================================

# Archives
*.zip
*.tar
*.tar.gz
*.tgz
*.rar
*.7z
*.bz2
*.gz
*.xz

# Pero MANTENER releases
!releases/*.zip
!dist/*.tar.gz


# ============================================
# Excepciones (Archivos a INCLUIR)
# ============================================

# Mantener estructura de directorios vacíos
!**/.gitkeep

# Mantener ejemplos y templates
!examples/
!templates/

# Mantener archivos de configuración base
!config/settings.py
!config/themes.py

# Mantener documentación
!*.md
!docs/

# Mantener requirements
!requirements.txt
!requirements-dev.txt


# ============================================
# Testing y CI/CD
# ============================================

# pytest
.pytest_cache/
.coverage

# tox
.tox/

# Coverage reports
htmlcov/

# GitHub Actions
.github/workflows/*.log


# ============================================
# Varios
# ============================================

# Thumbnails
*.thumb

# Profile data
*.prof

# Session data
.session

# PID files
*.pid


# ============================================
# NOTAS IMPORTANTES
# ============================================
#
# - Este .gitignore está diseñado para:
#   * Excluir archivos temporales y compilados
#   * Proteger datos sensibles (API keys, passwords)
#   * Mantener limpio el repositorio
#   * Permitir configuración local sin conflictos
#
# - Los datos en data/ NO se suben (configuraciones locales)
# - Los scripts en scripts/ NO se suben (personalizados)
# - Los logs NO se suben
#
# - Para INCLUIR algo que está ignorado:
#   git add -f archivo.txt
#
# ============================================
````

## File: COMPATIBILIDAD.md
````markdown
# 🌐 Compatibilidad Multiplataforma - Resumen

## 🎯 ¿En qué sistemas funciona?

### ✅ Funciona al 100% (TODO)
- **Raspberry Pi OS** (Raspbian)
- **Kali Linux** (en Raspberry Pi)

### ✅ Funciona al ~85% (sin control de ventiladores)
- **Ubuntu** (20.04, 22.04, 23.04+)
- **Debian** (11, 12+)
- **Linux Mint**
- **Fedora, CentOS, RHEL**
- **Arch Linux, Manjaro**

---

## 📊 Tabla de Compatibilidad

| Componente | Raspberry Pi | Otros Linux | Notas |
|------------|--------------|-------------|-------|
| **Interfaz gráfica** | ✅ | ✅ | 100% compatible |
| **Monitor sistema** | ✅ | ✅ | CPU, RAM, Temp, Disco |
| **Monitor red** | ✅ | ✅ | Download, Upload, Speedtest |
| **Monitor USB** | ✅ | ✅ | Con dependencias |
| **Lanzadores** | ✅ | ✅ | Scripts bash |
| **Temas** | ✅ | ✅ | 15 temas |
| **Control ventiladores** | ✅ | ❌ | Solo con GPIO |

---

## 🔧 Dependencias por Sistema

### Ubuntu/Debian/Raspberry Pi:
```bash
sudo apt-get install lm-sensors usbutils udisks2
pip3 install --break-system-packages customtkinter psutil
```

### Fedora/RHEL:
```bash
sudo dnf install lm-sensors usbutils udisks2
pip3 install customtkinter psutil
```

### Arch Linux:
```bash
sudo pacman -S lm-sensors usbutils udisks2
pip3 install customtkinter psutil
```

---

## ⚠️ Limitación: Control de Ventiladores

El control de ventiladores PWM **SOLO funciona en Raspberry Pi** porque requiere:
- GPIO pins
- Hardware específico
- Librería de control GPIO

**En otros sistemas Linux:** El botón de ventiladores no funcionará, pero el resto del dashboard (85%) funciona perfectamente.

---

## 💡 Uso Recomendado

- **Raspberry Pi:** Usa TODO al 100%
- **Ubuntu/Debian Desktop:** Monitor de sistema completo (sin ventiladores)
- **Servidores:** Requiere X11 para la interfaz gráfica
- **Kali Linux (RPi):** Funciona al 100% igual que Raspbian

---

## 🚀 Verificación Rápida

```bash
# Verificar Python
python3 --version  # Debe ser 3.8+

# Verificar temperatura
sensors  # o vcgencmd measure_temp

# Verificar USB
lsusb
lsblk
```

---

**Conclusión:** El dashboard funciona en cualquier Linux con interfaz gráfica. Solo el control de ventiladores es específico de Raspberry Pi con GPIO.
````

## File: create_desktop_launcher.sh
````bash
#!/bin/bash

# Script para crear lanzador de escritorio
# Para Sistema de Monitoreo

CURRENT_DIR=$(pwd)
DESKTOP_FILE="$HOME/.local/share/applications/system-dashboard.desktop"
ICON_FILE="$CURRENT_DIR/dashboard_icon.png"

echo "Creando lanzador de escritorio..."

# Crear directorio si no existe
mkdir -p "$HOME/.local/share/applications"

# Crear archivo .desktop
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=System Dashboard
Comment=Monitor del sistema con control de ventiladores
Exec=python3 $CURRENT_DIR/main.py
Path=$CURRENT_DIR
Icon=utilities-system-monitor
Terminal=false
Categories=System;Monitor;
Keywords=monitor;cpu;ram;temperature;fan;
StartupNotify=false
EOF

echo "✓ Lanzador creado en: $DESKTOP_FILE"
echo ""
echo "Ahora puedes:"
echo "  1. Buscar 'System Dashboard' en el menú de aplicaciones"
echo "  2. O ejecutar directamente: python3 main.py"
echo ""

# Preguntar si quiere autostart
read -p "¿Quieres que inicie automáticamente al encender? (s/n): " autostart
if [[ "$autostart" == "s" || "$autostart" == "S" ]]; then
    AUTOSTART_DIR="$HOME/.config/autostart"
    mkdir -p "$AUTOSTART_DIR"
    cp "$DESKTOP_FILE" "$AUTOSTART_DIR/"
    echo "✓ Configurado para iniciar automáticamente"
fi

echo ""
echo "¡Listo! 🎉"
````

## File: INSTALL_GUIDE.md
````markdown
# 🔧 Guía de Instalación Completa

Guía detallada para instalar el Dashboard en cualquier sistema Linux.

---

## 🎯 Sistemas Soportados

### ✅ **Soporte Completo (100%)**
- Raspberry Pi OS (Bullseye, Bookworm)
- Kali Linux (en Raspberry Pi)

### ✅ **Soporte Parcial (~85%)**
- Ubuntu (20.04, 22.04, 23.04+, 24.04)
- Debian (11, 12+)
- Linux Mint
- Fedora / CentOS / RHEL
- Arch Linux / Manjaro

**Nota**: En sistemas no-Raspberry Pi, el control de ventiladores PWM puede no funcionar. Todo lo demás funciona perfectamente.

---

## ⚡ Método 1: Instalación Automática (Recomendado)

### **Script de Instalación**

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard

# 2. Dar permisos y ejecutar
chmod +x install.sh
./install.sh

# 3. Ejecutar
python3 main.py
```

**El script instalará automáticamente:**
- ✅ Dependencias del sistema (python3-pip, python3-tk, lm-sensors)
- ✅ Dependencias Python (customtkinter, psutil, Pillow)
- ✅ Speedtest-cli (opcional)
- ✅ Configurará sensores

---

## 🛠️ Método 2: Instalación Manual con Entorno Virtual

### **Paso 1: Instalar Dependencias del Sistema**

```bash
# Actualizar repositorios
sudo apt update

# Instalar herramientas básicas
sudo apt install -y python3 python3-pip python3-venv python3-tk git

# Instalar lm-sensors para temperatura
sudo apt install -y lm-sensors

# Opcional: Speedtest
sudo apt install -y speedtest-cli

# Detectar sensores (primera vez)
sudo sensors-detect --auto
```

### **Paso 2: Clonar Repositorio**

```bash
cd ~
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
```

### **Paso 3: Crear Entorno Virtual**

```bash
# Crear venv
python3 -m venv venv

# Activar venv
source venv/bin/activate

# Tu prompt debería cambiar a: (venv) user@host:~$
```

### **Paso 4: Instalar Dependencias Python**

```bash
# Dentro del venv
pip install --upgrade pip
pip install -r requirements.txt
```

### **Paso 5: Ejecutar**

```bash
# Asegurarte que el venv está activo
source venv/bin/activate

# Ejecutar
python3 main.py
```

### **Paso 6: Crear Launcher (Opcional)**

```bash
# Para ejecutar sin activar venv manualmente
chmod +x create_desktop_launcher.sh
./create_desktop_launcher.sh
```

---

## 🚀 Método 3: Instalación Sin Entorno Virtual

**⚠️ Advertencia**: En Ubuntu 23.04+ y Debian 12+ necesitarás usar `--break-system-packages` o el script automático.

### **Opción A: Usar Script Automático** ⭐

```bash
cd system-dashboard
sudo ./install_system.sh
```

### **Opción B: Manual**

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install -y python3 python3-pip python3-tk lm-sensors speedtest-cli

# Instalar dependencias Python (método según tu sistema)
```

#### **En sistemas antiguos (Ubuntu 22.04, Debian 11):**
```bash
pip install -r requirements.txt
```

#### **En sistemas modernos (Ubuntu 23.04+, Debian 12+):**
```bash
pip install -r requirements.txt --break-system-packages
```

**O usar pipx:**
```bash
sudo apt install pipx
pipx install customtkinter
pipx install psutil
pipx install Pillow
```

### **Ejecutar**

```bash
python3 main.py
```

---

## 🐛 Solución de Problemas

### **Error: externally-managed-environment**

**Síntoma:**
```
error: externally-managed-environment
```

**Causa**: Sistema moderno (Ubuntu 23.04+, Debian 12+) que protege paquetes del sistema.

**Soluciones:**

1. **Opción 1: Usar venv** (Recomendado)
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Opción 2: Usar --break-system-packages**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```

3. **Opción 3: Usar pipx**
   ```bash
   sudo apt install pipx
   pipx install customtkinter psutil Pillow
   ```

---

### **Error: ModuleNotFoundError: No module named 'customtkinter'**

**Causa**: Dependencias no instaladas.

**Solución:**
```bash
# Si usas venv
source venv/bin/activate
pip install customtkinter

# Si no usas venv
pip install customtkinter --break-system-packages
```

---

### **Error: No se detecta temperatura**

**Síntoma:**
```
Temp: N/A
```

**Solución:**
```bash
# Detectar sensores
sudo sensors-detect --auto

# Reiniciar servicio
sudo systemctl restart lm-sensors

# Verificar que funciona
sensors
# Debería mostrar: coretemp-isa-0000, etc.
```

**Si aún no funciona:**
```bash
# Cargar módulos manualmente
sudo modprobe coretemp
```

---

### **Error: Ventiladores no responden**

**Causa**: Pin GPIO incorrecto o sin permisos.

**Solución:**

1. **Verificar pin:**
   ```bash
   gpio readall
   # Verificar que PWM_PIN=18 corresponde a un pin PWM
   ```

2. **Probar con sudo** (temporal):
   ```bash
   sudo python3 main.py
   ```

3. **Añadir usuario a grupo gpio** (permanente):
   ```bash
   sudo usermod -a -G gpio $USER
   # Cerrar sesión y volver a entrar
   ```

---

### **Error: ImportError: libGL.so.1**

**Causa**: Falta librería OpenGL.

**Solución:**
```bash
sudo apt install -y libgl1-mesa-glx
```

---

### **Error: Speedtest no funciona**

**Causa**: speedtest-cli no instalado.

**Solución:**
```bash
sudo apt install speedtest-cli

# Verificar
speedtest-cli --version
```

---

### **Error: No se ve la ventana**

**Causa**: Posición incorrecta.

**Solución**: Editar `config/settings.py`:
```python
DSI_X = 0  # Cambiar según tu pantalla
DSI_Y = 0
DSI_WIDTH = 800   # Ajustar a tu resolución
DSI_HEIGHT = 480
```

---

## 📦 Dependencias Completas

### **Dependencias del Sistema:**
```bash
python3          # >= 3.8
python3-pip      # Gestor de paquetes
python3-venv     # Entornos virtuales (opcional)
python3-tk       # Tkinter
lm-sensors       # Lectura de sensores
speedtest-cli    # Tests de velocidad (opcional)
git              # Control de versiones
```

### **Dependencias Python:**
```
customtkinter==5.2.0    # UI moderna
psutil==5.9.5           # Info del sistema
Pillow==10.0.0          # Procesamiento de imágenes
```

---

## 🔐 Permisos

### **GPIO (para ventiladores):**

```bash
# Añadir usuario a grupos necesarios
sudo usermod -a -G gpio,i2c,spi $USER

# Cerrar sesión y volver a entrar
```

### **Ejecutar sin sudo:**

El dashboard debería funcionar sin sudo, excepto:
- Control de ventiladores (requiere acceso GPIO)
- Algunos scripts en Lanzadores

---

## 🚀 Autoarranque (Opcional)

### **Método 1: systemd**

```bash
# Crear servicio
sudo nano /etc/systemd/system/dashboard.service
```

Contenido:
```ini
[Unit]
Description=System Dashboard
After=graphical.target

[Service]
Type=simple
User=tu-usuario
WorkingDirectory=/home/tu-usuario/system-dashboard
ExecStart=/home/tu-usuario/system-dashboard/venv/bin/python3 main.py
Restart=on-failure

[Install]
WantedBy=graphical.target
```

Activar:
```bash
sudo systemctl enable dashboard.service
sudo systemctl start dashboard.service
```

---

### **Método 2: autostart**

```bash
# Crear archivo autostart
mkdir -p ~/.config/autostart
nano ~/.config/autostart/dashboard.desktop
```

Contenido:
```ini
[Desktop Entry]
Type=Application
Name=System Dashboard
Exec=/home/tu-usuario/system-dashboard/venv/bin/python3 /home/tu-usuario/system-dashboard/main.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

---

## 🧪 Verificación de Instalación

### **Test completo:**

```bash
# 1. Verificar Python
python3 --version  # Debe ser >= 3.8

# 2. Verificar módulos
python3 -c "import customtkinter; print('CustomTkinter OK')"
python3 -c "import psutil; print('psutil OK')"
python3 -c "import PIL; print('Pillow OK')"

# 3. Verificar sensores
sensors  # Debe mostrar temperaturas

# 4. Verificar speedtest
speedtest-cli --version

# 5. Ejecutar dashboard
python3 main.py
```

---

## 💡 Tips de Instalación

1. **Usa el script automático** si es tu primera vez
2. **Usa venv** si quieres mantener el sistema limpio
3. **No uses sudo** para instalar paquetes Python (usa venv)
4. **Detecta sensores** la primera vez con `sudo sensors-detect`
5. **Revisa los logs** si algo falla: `journalctl -xe`

---

## 📊 Tiempos de Instalación

| Método | Tiempo | Dificultad |
|--------|--------|------------|
| Script automático | ~5 min | ⭐ Fácil |
| Manual con venv | ~10 min | ⭐⭐ Media |
| Manual sin venv | ~8 min | ⭐⭐ Media |

---

## 🆘 Ayuda Adicional

**¿Problemas con la instalación?**

1. Revisa esta guía completa
2. Verifica [QUICKSTART.md](QUICKSTART.md) para problemas comunes
3. Revisa [README.md](README.md) sección Troubleshooting
4. Abre un Issue en GitHub con:
   - Sistema operativo y versión
   - Versión de Python
   - Mensaje de error completo
   - Comando que ejecutaste

---

**¡Instalación completa!** 🎉
````

## File: install_system.sh
````bash
#!/bin/bash

# Script de instalación DIRECTA en el sistema (sin venv)
# Para Sistema de Monitoreo

echo "==================================="
echo "System Dashboard - Instalación"
echo "Instalación DIRECTA en el sistema"
echo "==================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"

# Instalar dependencias del sistema
echo ""
echo "Instalando dependencias del sistema..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-tk lm-sensors

# Opcional: speedtest
read -p "¿Instalar speedtest-cli? (s/n): " install_speedtest
if [[ "$install_speedtest" == "s" || "$install_speedtest" == "S" ]]; then
    sudo apt-get install -y speedtest-cli
fi

# Instalar dependencias Python DIRECTAMENTE en el sistema
echo ""
echo "Instalando dependencias de Python en el sistema..."

# Usar --break-system-packages para sistemas modernos
echo "Usando --break-system-packages (necesario en Ubuntu 23.04+/Debian 12+)..."
sudo pip3 install --break-system-packages customtkinter psutil

# Alternativa: Si lo anterior falla, instalar para el usuario
if [ $? -ne 0 ]; then
    echo "Instalación con sudo falló, intentando instalación de usuario..."
    pip3 install --user --break-system-packages customtkinter psutil
fi

# Configurar sensors (opcional)
echo ""
read -p "¿Configurar sensors para lectura de temperatura? (s/n): " config_sensors
if [[ "$config_sensors" == "s" || "$config_sensors" == "S" ]]; then
    echo "Configurando sensors..."
    sudo sensors-detect --auto
fi

echo ""
echo "==================================="
echo "✓ Instalación completada"
echo "==================================="
echo ""
echo "Para ejecutar el dashboard:"
echo "  python3 main.py"
echo ""
echo "O crear un lanzador de escritorio (recomendado):"
echo "  ./create_desktop_launcher.sh"
echo ""
````

## File: install.sh
````bash
#!/bin/bash

# Script de instalación rápida para System Dashboard

echo "==================================="
echo "System Dashboard - Instalación"
echo "==================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.8+"
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"

# Crear entorno virtual
echo ""
echo "Creando entorno virtual..."
python3 -m venv venv

# Activar entorno
source venv/bin/activate

# Actualizar pip
echo ""
echo "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo ""
echo "Instalando dependencias de Python..."
pip install -r requirements.txt

echo ""
echo "==================================="
echo "✓ Instalación completada"
echo "==================================="
echo ""
echo "Para ejecutar el dashboard:"
echo "  1. Activa el entorno: source venv/bin/activate"
echo "  2. Ejecuta: python main.py"
echo ""
echo "Notas:"
echo "  - Asegúrate de tener lm-sensors instalado: sudo apt-get install lm-sensors"
echo "  - Para speedtest: sudo apt-get install speedtest-cli"
echo "  - Configura tus scripts en config/settings.py"
echo ""
````

## File: INTEGRATION_GUIDE.md
````markdown
# 🔗 Guía de Integración con fase1.py

Esta guía explica cómo integrar tu aplicación OLED (`fase1.py`) con el Dashboard para que ambos funcionen juntos.

---

## 🎯 ¿Cómo Funciona la Integración?

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  DASHBOARD (system_dashboard)                          │
│  - Interfaz gráfica                                    │
│  - Control de ventiladores                             │
│  - Guarda estado en: data/fan_state.json              │
│                                                         │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Escribe fan_state.json
                   │ {"mode": "auto", "target_pwm": 128}
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  ARCHIVO COMPARTIDO                                     │
│  📄 data/fan_state.json                                │
│  {"mode": "auto", "target_pwm": 128}                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Lee fan_state.json
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  OLED MONITOR (fase1.py / integration_fase1.py)       │
│  - Muestra CPU, RAM, Temp en OLED                     │
│  - Controla LEDs RGB                                   │
│  - Aplica PWM de ventiladores                         │
│  - Lee estado desde: data/fan_state.json              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Pasos de Integración

### 1️⃣ Instalar el Dashboard

```bash
# Descargar y extraer system_dashboard
cd ~
unzip system_dashboard_WITH_THEMES.zip
cd system_dashboard

# Instalar dependencias
sudo ./install_system.sh
```

### 2️⃣ Configurar Ruta en fase1.py

Edita tu `fase1.py` (o usa el nuevo `integration_fase1.py`):

```python
# En la línea ~13, cambia:
STATE_FILE = "/home/jalivur/system_dashboard/data/fan_state.json"

# Ajusta la ruta donde hayas puesto el proyecto
```

### 3️⃣ Ejecutar Ambos Programas

**Terminal 1** - Dashboard:
```bash
cd ~/system_dashboard
python3 main.py
```

**Terminal 2** - OLED Monitor:
```bash
cd /ruta/a/tu/fase1
python3 integration_fase1.py
# O tu fase1.py modificado
```

---

## 🔄 Flujo de Datos

### Cuando Cambias el Modo en el Dashboard:

1. **Usuario** hace clic en "Control Ventiladores"
2. **Dashboard** cambia el modo a "Manual" y PWM a 200
3. **Dashboard** guarda en `data/fan_state.json`:
   ```json
   {
     "mode": "manual",
     "target_pwm": 200
   }
   ```
4. **fase1.py** lee el archivo cada 1 segundo
5. **fase1.py** aplica PWM=200 a los ventiladores
6. **OLED** muestra "Fan1:78% Fan2:78%" (200/255 = 78%)

### Sincronización:

- ✅ Dashboard escribe cada vez que cambias algo
- ✅ fase1 lee cada 1 segundo
- ✅ PWM se aplica inmediatamente si cambia
- ✅ Sin conflictos (escritura atómica con .tmp)

---

## ⚙️ Modos Disponibles

El Dashboard soporta 5 modos:

| Modo | PWM | Descripción |
|------|-----|-------------|
| **Auto** | Dinámico | Basado en curva temperatura-PWM |
| **Manual** | Usuario | Tú eliges el valor (0-255) |
| **Silent** | 77 | Silencioso (30%) |
| **Normal** | 128 | Normal (50%) |
| **Performance** | 255 | Máximo (100%) |

El archivo `fan_state.json` siempre tiene `target_pwm` calculado, independientemente del modo.

---

## 🛠️ Configuración Avanzada

### Opción 1: Usar Rutas Relativas (Recomendado)

Modifica `integration_fase1.py`:

```python
import os
from pathlib import Path

# Ruta relativa al home del usuario
HOME = Path.home()
STATE_FILE = HOME / "system_dashboard" / "data" / "fan_state.json"
```

### Opción 2: Variable de Entorno

```bash
# En ~/.bashrc o ~/.profile
export DASHBOARD_DATA="/home/jalivur/system_dashboard/data"

# En fase1.py
STATE_FILE = os.environ.get("DASHBOARD_DATA", "/home/jalivur/system_dashboard/data") + "/fan_state.json"
```

### Opción 3: Enlace Simbólico

```bash
# Crear enlace en ubicación fija
ln -s ~/system_dashboard/data/fan_state.json /tmp/fan_state.json

# En fase1.py
STATE_FILE = "/tmp/fan_state.json"
```

---

## 🚀 Autostart de Ambos Programas

### Método 1: systemd (Recomendado)

**Dashboard:**
```bash
# Crear servicio
sudo nano /etc/systemd/system/dashboard.service
```

```ini
[Unit]
Description=System Dashboard
After=graphical.target

[Service]
Type=simple
User=jalivur
WorkingDirectory=/home/jalivur/system_dashboard
Environment="DISPLAY=:0"
ExecStart=/usr/bin/python3 /home/jalivur/system_dashboard/main.py
Restart=always

[Install]
WantedBy=graphical.target
```

**OLED Monitor:**
```bash
sudo nano /etc/systemd/system/oled-monitor.service
```

```ini
[Unit]
Description=OLED Monitor
After=network.target

[Service]
Type=simple
User=jalivur
WorkingDirectory=/home/jalivur/proyectopantallas
ExecStart=/usr/bin/python3 /home/jalivur/proyectopantallas/integration_fase1.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Activar:**
```bash
sudo systemctl enable dashboard.service
sudo systemctl enable oled-monitor.service

sudo systemctl start dashboard.service
sudo systemctl start oled-monitor.service

# Ver logs
sudo journalctl -u dashboard.service -f
sudo journalctl -u oled-monitor.service -f
```

### Método 2: Crontab @reboot

```bash
crontab -e
```

Añadir:
```cron
@reboot sleep 30 && DISPLAY=:0 /usr/bin/python3 /home/jalivur/system_dashboard/main.py &
@reboot sleep 10 && /usr/bin/python3 /home/jalivur/proyectopantallas/integration_fase1.py &
```

---

## 🐛 Solución de Problemas

### El OLED no muestra cambios de ventilador

**Verificar que el archivo existe:**
```bash
ls -la ~/system_dashboard/data/fan_state.json
```

**Ver contenido:**
```bash
cat ~/system_dashboard/data/fan_state.json
# Debe mostrar: {"mode": "...", "target_pwm": ...}
```

**Ver logs de fase1:**
```bash
# Añadir debug al inicio
python3 integration_fase1.py
# Verás: "Estado leído: modo=auto, PWM=128"
```

### El PWM no cambia

**Verificar permisos:**
```bash
chmod 644 ~/system_dashboard/data/fan_state.json
```

**Verificar que fase1 lee el archivo:**
```python
# Añadir en el código de fase1:
if state:
    print(f"DEBUG: Estado leído = {state}")
```

### Los dos programas pelean por los ventiladores

**Esto NO debería pasar** porque:
- Dashboard solo ESCRIBE el estado
- fase1 solo LEE el estado
- fase1 es quien aplica el PWM físicamente

Si pasa:
1. Cierra el Dashboard
2. Solo ejecuta fase1
3. Verifica que funciona
4. Vuelve a abrir Dashboard

---

## 💡 Tips y Trucos

### Ver Estado en Tiempo Real

```bash
# Terminal dedicado
watch -n 1 cat ~/system_dashboard/data/fan_state.json
```

### Script de Debug

```bash
#!/bin/bash
# debug_integration.sh

echo "=== Estado del Dashboard ==="
cat ~/system_dashboard/data/fan_state.json | python3 -m json.tool

echo ""
echo "=== Procesos corriendo ==="
ps aux | grep -E "main.py|fase1.py|integration_fase1.py"

echo ""
echo "=== Temperatura actual ==="
vcgencmd measure_temp
```

### Notificaciones de Cambio

Añade a `integration_fase1.py`:

```python
last_mode = None

# En el bucle:
if state and state.get("mode") != last_mode:
    new_mode = state.get("mode")
    print(f"🔔 Modo cambiado: {last_mode} → {new_mode}")
    # Opcionalmente, mostrar en OLED temporalmente
    last_mode = new_mode
```

---

## 📊 Monitoreo

### Ver Logs en Tiempo Real

```bash
# Dashboard
tail -f ~/system_dashboard/dashboard.log

# OLED Monitor
tail -f ~/proyectopantallas/oled_monitor.log
```

### Crear Logs

Añade al inicio de `integration_fase1.py`:

```python
import logging

logging.basicConfig(
    filename='/home/jalivur/proyectopantallas/oled_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# En el bucle:
if state:
    logging.info(f"PWM aplicado: {fan_pwm}, Modo: {state.get('mode')}")
```

---

## ✅ Checklist de Integración

- [ ] Dashboard instalado y funcionando
- [ ] Archivo `fan_state.json` se crea al cambiar modo
- [ ] Ruta correcta configurada en fase1.py
- [ ] fase1.py lee el archivo correctamente
- [ ] PWM se aplica a los ventiladores físicos
- [ ] OLED muestra el porcentaje correcto
- [ ] Ambos programas arrancan al inicio (opcional)
- [ ] Logs configurados (opcional)

---

## 🎯 Resultado Final

Una vez integrado correctamente:

✅ Cambias modo en Dashboard → Ventiladores responden inmediatamente
✅ OLED muestra estado actual de ventiladores
✅ LEDs cambian color según temperatura
✅ Todo funciona sin conflictos
✅ Puedes cerrar Dashboard, fase1 sigue funcionando
✅ Puedes cerrar fase1, Dashboard sigue guardando estado

---

## 📞 ¿Problemas?

Si tienes problemas con la integración:

1. Verifica rutas con `ls -la`
2. Verifica contenido con `cat`
3. Añade `print()` para debug
4. Ejecuta manualmente primero (no autostart)
5. Revisa logs de systemd si usas servicios

---

**¡Disfruta de tu sistema integrado!** 🎉
````

## File: migratelogger.sh
````bash
# Script: migrate_to_logging.sh
#!/bin/bash

# Reemplazar prints por logging
find . -name "*.py" -type f -exec sed -i 's/print(f"\[/logger.info("/g' {} \;
find . -name "*.py" -type f -exec sed -i 's/print("Error/logger.error("/g' {} \;
````

## File: REQUIREMENTS.md
````markdown
# 📦 Guía Rápida: requirements.txt

## 🎯 ¿Qué es?

Un archivo que lista todas las **dependencias Python** de tu proyecto para instalarlas automáticamente.

---

## 📝 Contenido del archivo

```txt
# Dependencias Python
customtkinter>=5.2.0
psutil>=5.9.0
```

**Significado:**
- `customtkinter>=5.2.0` → Interfaz gráfica (versión 5.2.0 o superior)
- `psutil>=5.9.0` → Monitor de sistema (versión 5.9.0 o superior)

---

## 🚀 Cómo usar

### Instalar dependencias:

```bash
# En sistemas modernos (Ubuntu 23.04+, Debian 12+)
pip3 install --break-system-packages -r requirements.txt

# En sistemas antiguos
pip3 install -r requirements.txt

# O con sudo (global)
sudo pip3 install -r requirements.txt
```

---

## 🔧 Operadores de versión

| Operador | Significado | Ejemplo |
|----------|-------------|---------|
| `>=` | Versión mínima | `psutil>=5.9.0` |
| `==` | Versión exacta | `psutil==5.9.5` |
| `<=` | Versión máxima | `psutil<=6.0.0` |
| `~=` | Compatible | `psutil~=5.9.0` (5.9.x) |

---

## ✅ Buenas prácticas

### ✅ Hacer:
- Usar versiones mínimas (`>=`) en lugar de exactas
- Comentar dependencias opcionales
- Mantener el archivo actualizado

### ❌ Evitar:
- No especificar versiones (puede romper)
- Versiones exactas innecesarias (muy restrictivo)
- Incluir TODO con `pip freeze` (archivo enorme)

---

## 🧪 Verificar instalación

```bash
# Ver qué tienes instalado
pip3 list

# Ver versión específica
pip3 show customtkinter

# Comprobar problemas
pip3 check
```

---

## 📊 Dependencias del Sistema

**NOTA:** requirements.txt solo lista dependencias **Python**. 

Las dependencias del **sistema** (como `lm-sensors`) se instalan con:

```bash
# Ubuntu/Debian/Raspberry Pi
sudo apt-get install lm-sensors usbutils udisks2

# Fedora/RHEL
sudo dnf install lm-sensors usbutils udisks2
```

---

## 🎯 Resumen

**¿Qué es?** → Lista de dependencias Python  
**¿Para qué?** → Instalar todo automáticamente  
**¿Cómo usar?** → `pip3 install -r requirements.txt`  
**¿Dónde?** → Raíz del proyecto  

---

**Tip:** En sistemas modernos (Ubuntu 23.04+), usa `--break-system-packages` para evitar errores de PEP 668.
````

## File: setup.py
````python
"""
Setup script para System Dashboard
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="system-dashboard",
    version="1.0.0",
    author="Tu Nombre",
    author_email="tu@email.com",
    description="Sistema profesional de monitoreo del sistema con control de ventiladores",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tuusuario/system-dashboard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "system-dashboard=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
    },
)
````

## File: config/__init__.py
````python
"""
Paquete de configuración
"""
from .settings import (
    # Rutas
    PROJECT_ROOT,
    DATA_DIR,
    SCRIPTS_DIR,
    STATE_FILE,
    CURVE_FILE,
    # Pantalla
    DSI_WIDTH,
    DSI_HEIGHT,
    DSI_X,
    DSI_Y,
    # Actualización y gráficas
    UPDATE_MS,
    HISTORY,
    GRAPH_WIDTH,
    GRAPH_HEIGHT,
    # Umbrales
    CPU_WARN,
    CPU_CRIT,
    TEMP_WARN,
    TEMP_CRIT,
    RAM_WARN,
    RAM_CRIT,
    # Red
    NET_WARN,
    NET_CRIT,
    NET_INTERFACE,
    NET_MAX_MB,
    NET_MIN_SCALE,
    NET_MAX_SCALE,
    NET_IDLE_THRESHOLD,
    NET_IDLE_RESET_TIME,
    # Lanzadores
    LAUNCHERS,
    # Tema y estilos
    SELECTED_THEME,
    COLORS,
    FONT_FAMILY,
    FONT_SIZES,
)
````

## File: core/alert_service.py
````python
"""
Servicio de alertas externas por Telegram.
Sin dependencias nuevas — usa urllib de la stdlib.

Lógica anti-spam: cada alerta debe mantenerse activa durante
ALERT_SUSTAIN_S segundos antes de enviarse, y no se repite
hasta que baje del umbral y vuelva a subir (edge-trigger).
"""
import threading
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Optional
import os
from dotenv import load_dotenv
from utils.logger import get_logger

logger = get_logger(__name__)

# Tiempo que la condición debe mantenerse antes de enviar (segundos)
ALERT_SUSTAIN_S = 60

# Intervalo de comprobación (segundos)
CHECK_INTERVAL  = 15

# Umbrales (se pueden sobrescribir en settings.py si se prefiere)
THRESHOLDS = {
    'temp':  {'warn': 60, 'crit': 70},
    'cpu':   {'warn': 85, 'crit': 95},
    'ram':   {'warn': 85, 'crit': 95},
    'disk':  {'warn': 85, 'crit': 95},
}
# Constante: máximo de entradas en el historial
MAX_HISTORY_ENTRIES = 100
# Archivo JSON para persistir el historial de alertas enviadas
_HISTORY_FILE = Path(__file__).resolve().parent.parent / "data" / "alert_history.json"

def _load_telegram_config() -> tuple:
    """Lee TOKEN y CHAT_ID desde .env / os.environ."""
    
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        try:
            load_dotenv(env_path, override=False)
        except ImportError:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, _, v = line.partition('=')
                    k = k.strip()
                    if k not in os.environ:
                        os.environ[k] = v.strip().strip('"').strip("'")
    token   = os.environ.get('TELEGRAM_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    return token, chat_id


class AlertService:
    """
    Servicio background que monitoriza métricas y envía alertas a Telegram.

    Instanciar en main.py y pasar system_monitor / service_monitor.
    Llamar a start() y stop() igual que el resto de servicios.
    """

    def __init__(self, system_monitor, service_monitor):
        self.system_monitor  = system_monitor
        self.service_monitor = service_monitor

        self._token, self._chat_id = _load_telegram_config()

        if not self._token or not self._chat_id:
            logger.warning(
                "[AlertService] TELEGRAM_TOKEN o TELEGRAM_CHAT_ID no configurados — "
                "alertas desactivadas"
            )

        # Estado interno para anti-spam
        # key -> {'first_seen': timestamp, 'sent': bool}
        self._state: Dict[str, dict] = {}
        self._lock   = threading.Lock()

        self._running  = False
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="AlertService"
        )
        self._thread.start()
        logger.info("[AlertService] Servicio iniciado (cada %ds)", CHECK_INTERVAL)

    def stop(self) -> None:
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("[AlertService] Servicio detenido")

    # ── Bucle principal ───────────────────────────────────────────────────────

    def _loop(self) -> None:
        while self._running:
            try:
                self._check_metrics()
                self._check_services()
            except Exception as e:
                logger.error("[AlertService] Error en _loop: %s", e)
            self._stop_evt.wait(timeout=CHECK_INTERVAL)
            if self._stop_evt.is_set():
                break

    def _check_metrics(self) -> None:
        stats = self.system_monitor.get_current_stats()
        checks = [
            ('temp', stats.get('temp',       0), '°C', '🌡️ Temperatura'),
            ('cpu',  stats.get('cpu',         0), '%',  '🔥 CPU'),
            ('ram',  stats.get('ram',         0), '%',  '💾 RAM'),
            ('disk', stats.get('disk_usage',  0), '%',  '💿 Disco'),
        ]
        for key, value, unit, label in checks:
            thr = THRESHOLDS[key]
            if value >= thr['crit']:
                level, emoji = 'crit', '🔴'
            elif value >= thr['warn']:
                level, emoji = 'warn', '🟠'
            else:
                level = None

            if level:
                msg = (
                    f"{emoji} *Dashboard — {label} alta*\n"
                    f"Valor actual: *{value:.1f}{unit}*\n"
                    f"Umbral {'crítico' if level=='crit' else 'de aviso'}: "
                    f"{thr[level]}{unit}"
                )
                self._trigger(f"{key}_{level}", msg, value=value, unit=unit, level=level)
            else:
                for suffix in ('warn', 'crit'):
                    self._reset(f"{key}_{suffix}")

    def _check_services(self) -> None:
        stats  = self.service_monitor.get_stats()
        failed = stats.get('failed', 0)
        key    = 'services_failed'
        if failed > 0:
            msg = (
                f"⚠️ *Dashboard — Servicios caídos*\n"
                f"Hay *{failed}* servicio{'s' if failed > 1 else ''} en estado FAILED.\n"
                f"Abre Monitor Servicios para más detalles."
            )
            self._trigger(key, msg, value=float(failed), unit=" servicios", level="crit")
        else:
            self._reset(key)

    # ── Lógica anti-spam (edge-trigger + sustain) ─────────────────────────────
    def _trigger(self, key: str, message: str, value: float = 0.0,
                unit: str = "", level: str = "") -> None:
        """
        Activa una alerta con retardo anti-spam.
        Solo envía si la condición lleva ALERT_SUSTAIN_S segundos activa
        y no se ha enviado ya para este 'flanco'.
        """
        now = time.time()
        with self._lock:
            entry = self._state.get(key)
            if entry is None:
                self._state[key] = {'first_seen': now, 'sent': False}
                return
            if entry['sent']:
                return
            if now - entry['first_seen'] >= ALERT_SUSTAIN_S:
                entry['sent'] = True
        # Enviar fuera del lock
        if self._send(message):
            self._save_to_history(key, message, value, unit, level)

    def _reset(self, key: str) -> None:
        """Resetea el estado de una alerta (condición resuelta)."""
        with self._lock:
            self._state.pop(key, None)
            
    def _save_to_history(self, key: str, message: str, value: float, unit: str, level: str) -> None:
        """Guarda la alerta disparada en el historial JSON (máx. MAX_HISTORY_ENTRIES)."""
        entry = {
            "ts":      time.strftime("%Y-%m-%d %H:%M:%S"),
            "key":     key,
            "level":   level,       # 'warn' o 'crit'
            "value":   round(value, 1),
            "unit":    unit,
            "message": message.replace("*", "").replace("\n", " "),  # limpiar markdown
        }
        try:
            _HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            history = []
            if _HISTORY_FILE.exists():
                with open(_HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            history.append(entry)
            # Mantener solo las últimas MAX_HISTORY_ENTRIES
            history = history[-MAX_HISTORY_ENTRIES:]
            with open(_HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("[AlertService] Error guardando historial: %s", e)

    def get_history(self) -> list:
        """Devuelve el historial completo (más reciente al final)."""
        try:
            if _HISTORY_FILE.exists():
                with open(_HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def clear_history(self) -> None:
        """Borra el historial de alertas."""
        try:
            if _HISTORY_FILE.exists():
                _HISTORY_FILE.unlink()
            logger.info("[AlertService] Historial de alertas borrado")
        except Exception as e:
            logger.error("[AlertService] Error borrando historial: %s", e)

    # ── Envío a Telegram ──────────────────────────────────────────────────────

    def _send(self, text: str) -> bool:
        """Envía un mensaje Markdown a Telegram. Devuelve True si tiene éxito."""
        if not self._token or not self._chat_id:
            return False
        url     = f"https://api.telegram.org/bot{self._token}/sendMessage"
        payload = json.dumps({
            "chat_id":    self._chat_id,
            "text":       text,
            "parse_mode": "Markdown",
        }).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                result = json.loads(resp.read())
                if result.get("ok"):
                    logger.info("[AlertService] Mensaje enviado a Telegram")
                    return True
            logger.warning("[AlertService] Respuesta inesperada de Telegram: %s", result)
            return False
        except Exception as e:
            logger.error("[AlertService] Error enviando a Telegram: %s", e)
            return False

    def send_test(self) -> bool:
        """Envía un mensaje de prueba. Útil para verificar la configuración."""
        return self._send(
            "✅ *Dashboard — Test de alertas*\n"
            "La conexión con Telegram funciona correctamente."
        )
````

## File: core/disk_monitor.py
````python
"""
Monitor de disco
"""
from collections import deque
from typing import Dict
from config.settings import HISTORY, UPDATE_MS, COLORS
from utils.system_utils import SystemUtils
import psutil


class DiskMonitor:
    """Monitor de disco con historial"""
    
    def __init__(self):
        self.system_utils = SystemUtils()
        
        # Historiales (reutilizamos lo del SystemMonitor)
        self.usage_hist = deque(maxlen=HISTORY)
        self.read_hist = deque(maxlen=HISTORY)
        self.write_hist = deque(maxlen=HISTORY)
        self.nvme_temp_hist = deque(maxlen=HISTORY)  # NUEVO
        
        # Para calcular velocidad de I/O
        self.last_disk_io = psutil.disk_io_counters()
    
    def get_current_stats(self) -> Dict:
        """
        Obtiene estadísticas actuales del disco
        
        Returns:
            Diccionario con todas las métricas
        """
        # Uso de disco (%)
        disk_usage = psutil.disk_usage('/').percent
        
        # I/O (calcular velocidad)
        disk_io = psutil.disk_io_counters()
        read_bytes = max(0, disk_io.read_bytes - self.last_disk_io.read_bytes)
        write_bytes = max(0, disk_io.write_bytes - self.last_disk_io.write_bytes)
        self.last_disk_io = disk_io
        
        # Convertir a MB/s

        seconds = UPDATE_MS / 1000.0
        read_mb = (read_bytes / (1024 * 1024)) / seconds
        write_mb = (write_bytes / (1024 * 1024)) / seconds
        
        # Temperatura NVMe (NUEVO)
        nvme_temp = self.system_utils.get_nvme_temp()
        
        return {
            'disk_usage': disk_usage,
            'disk_read_mb': read_mb,
            'disk_write_mb': write_mb,
            'nvme_temp': nvme_temp  # NUEVO
        }
    
    def update_history(self, stats: Dict) -> None:
        """
        Actualiza historiales con estadísticas actuales
        
        Args:
            stats: Diccionario con estadísticas
        """
        self.usage_hist.append(stats['disk_usage'])
        self.read_hist.append(stats['disk_read_mb'])
        self.write_hist.append(stats['disk_write_mb'])
        self.nvme_temp_hist.append(stats['nvme_temp'])  # NUEVO
    
    def get_history(self) -> Dict:
        """
        Obtiene todos los historiales
        
        Returns:
            Diccionario con historiales
        """
        return {
            'disk_usage': list(self.usage_hist),
            'disk_read': list(self.read_hist),
            'disk_write': list(self.write_hist),
            'nvme_temp': list(self.nvme_temp_hist)  # NUEVO
        }
    
    @staticmethod
    def level_color(value: float, warn: float, crit: float) -> str:
        """
        Determina color según nivel
        
        Args:
            value: Valor actual
            warn: Umbral de advertencia
            crit: Umbral crítico
            
        Returns:
            Color en formato hex
        """
        
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS['warning']
        else:
            return COLORS['primary']
````

## File: core/fan_controller.py
````python
"""
Controlador de ventiladores
"""
from typing import List, Dict
from utils.file_manager import FileManager
from utils.logger import get_logger

logger = get_logger(__name__)


class FanController:
    """Controlador para gestión de ventiladores"""
    
    def __init__(self):
        self.file_manager = FileManager()
    
    def compute_pwm_from_curve(self, temp: float) -> int:
        """
        Calcula el PWM basado en la curva y la temperatura

        Args:
            temp: Temperatura actual en °C

        Returns:
            Valor PWM (0-255)
        """
        curve = self.file_manager.load_curve()
        
        if not curve:
            logger.warning("[FanController] compute_pwm_from_curve: curva vacía, retornando PWM 0")
            return 0
        
        if temp <= curve[0]["temp"]:
            return int(curve[0]["pwm"])
        
        if temp >= curve[-1]["temp"]:
            return int(curve[-1]["pwm"])
        
        for i in range(len(curve) - 1):
            t1, pwm1 = curve[i]["temp"], curve[i]["pwm"]
            t2, pwm2 = curve[i + 1]["temp"], curve[i + 1]["pwm"]
            
            if t1 <= temp <= t2:
                ratio = (temp - t1) / (t2 - t1)
                pwm = pwm1 + ratio * (pwm2 - pwm1)
                return int(pwm)
        
        return int(curve[-1]["pwm"])
    
    def get_pwm_for_mode(self, mode: str, temp: float, manual_pwm: int = 128) -> int:
        """
        Obtiene el PWM según el modo seleccionado

        Args:
            mode: Modo de operación (auto, manual, silent, normal, performance)
            temp: Temperatura actual
            manual_pwm: Valor PWM manual si mode='manual'

        Returns:
            Valor PWM calculado (0-255)
        """
        if mode == "manual":
            return max(0, min(255, manual_pwm))
        elif mode == "auto":
            return self.compute_pwm_from_curve(temp)
        elif mode == "silent":
            return 77
        elif mode == "normal":
            return 128
        elif mode == "performance":
            return 255
        else:
            logger.warning(f"[FanController] Modo desconocido '{mode}', usando curva auto")
            return self.compute_pwm_from_curve(temp)
    
    def update_fan_state(self, mode: str, temp: float, current_target: int = None,
                         manual_pwm: int = 128) -> Dict:
        """
        Actualiza el estado del ventilador

        Args:
            mode: Modo actual
            temp: Temperatura actual
            current_target: PWM objetivo actual
            manual_pwm: PWM manual configurado

        Returns:
            Diccionario con el nuevo estado
        """
        desired = self.get_pwm_for_mode(mode, temp, manual_pwm)
        desired = max(0, min(255, int(desired)))
        
        if desired != current_target:
            new_state = {"mode": mode, "target_pwm": desired}
            self.file_manager.write_state(new_state)
            logger.debug(f"[FanController] PWM actualizado: {current_target} → {desired} (modo={mode}, temp={temp:.1f}°C)")
            return new_state
        
        return {"mode": mode, "target_pwm": current_target}
    
    def add_curve_point(self, temp: int, pwm: int) -> List[Dict]:
        """
        Añade un punto a la curva

        Args:
            temp: Temperatura en °C
            pwm: Valor PWM (0-255)

        Returns:
            Curva actualizada
        """
        curve = self.file_manager.load_curve()
        pwm = max(0, min(255, pwm))
        
        found = False
        for point in curve:
            if point["temp"] == temp:
                logger.debug(f"[FanController] Punto actualizado en curva: {temp}°C → PWM {point['pwm']} → {pwm}")
                point["pwm"] = pwm
                found = True
                break
        
        if not found:
            logger.debug(f"[FanController] Nuevo punto añadido a curva: {temp}°C → PWM {pwm}")
            curve.append({"temp": temp, "pwm": pwm})
        
        curve = sorted(curve, key=lambda x: x["temp"])
        self.file_manager.save_curve(curve)
        
        return curve
    
    def remove_curve_point(self, temp: int) -> List[Dict]:
        """
        Elimina un punto de la curva

        Args:
            temp: Temperatura del punto a eliminar

        Returns:
            Curva actualizada
        """
        curve = self.file_manager.load_curve()
        original_len = len(curve)
        curve = [p for p in curve if p["temp"] != temp]
        
        if len(curve) < original_len:
            logger.debug(f"[FanController] Punto eliminado de curva: {temp}°C")
        else:
            logger.warning(f"[FanController] remove_curve_point: no se encontró punto en {temp}°C")
        
        if not curve:
            curve = [{"temp": 40, "pwm": 100}]
            logger.warning("[FanController] Curva quedó vacía, restaurado punto por defecto")
        
        self.file_manager.save_curve(curve)
        return curve
````

## File: core/homebridge_monitor.py
````python
"""
Monitor de Homebridge
Integración con la API REST de homebridge-config-ui-x
Credenciales cargadas desde .env (nunca hardcodeadas)

Incluye sondeo ligero en background cada 30s para mantener
los badges del menú actualizados sin necesidad de abrir la ventana.
"""
import json
import os
import threading
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Carga de .env ─────────────────────────────────────────────────────────────
def _load_env():
    """
    Carga variables de .env sin dependencias externas.
    Si python-dotenv está disponible lo usa; si no, parsea el archivo a mano.
    """
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        logger.warning("[HomebridgeMonitor] No se encontró .env en %s", env_path)
        return

    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=False)
        logger.debug("[HomebridgeMonitor] .env cargado con python-dotenv")
    except ImportError:
        logger.debug("[HomebridgeMonitor] python-dotenv no instalado, usando parser manual")
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value

_load_env()

# ── Configuración leída del entorno ───────────────────────────────────────────
HOMEBRIDGE_HOST  = os.environ.get("HOMEBRIDGE_HOST", "")
HOMEBRIDGE_PORT  = int(os.environ.get("HOMEBRIDGE_PORT", "8581"))
HOMEBRIDGE_USER  = os.environ.get("HOMEBRIDGE_USER", "")
HOMEBRIDGE_PASS  = os.environ.get("HOMEBRIDGE_PASS", "")

HOMEBRIDGE_URL   = f"http://{HOMEBRIDGE_HOST}:{HOMEBRIDGE_PORT}"
REQUEST_TIMEOUT  = 5   # segundos por petición HTTP
POLL_INTERVAL_S  = 30  # segundos entre sondeos en background


class HomebridgeMonitor:
    """
    Monitor y controlador de dispositivos Homebridge.

    - Sondeo ligero en background cada 30s (1 petición HTTP ~1KB).
    - La ventana lee self._accessories desde memoria sin petición extra.
    - Los badges del menú siempre reflejan el estado real.
    - toggle() fuerza un sondeo inmediato tras el comando.
    """

    def __init__(self):
        self._token: Optional[str]      = None
        self._token_lock                = threading.Lock()
        self._accessories: List[Dict]   = []
        self._accessories_lock          = threading.Lock()
        self._reachable: Optional[bool] = None  # None = aún no consultado

        # Control del thread de background
        self._running  = False
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None

        if not HOMEBRIDGE_HOST or not HOMEBRIDGE_USER:
            logger.error(
                "[HomebridgeMonitor] Faltan variables en .env: "
                "HOMEBRIDGE_HOST=%r, HOMEBRIDGE_USER=%r",
                HOMEBRIDGE_HOST, HOMEBRIDGE_USER,
            )
        else:
            logger.info(
                "[HomebridgeMonitor] Inicializado — %s:%s (usuario: %s)",
                HOMEBRIDGE_HOST, HOMEBRIDGE_PORT, HOMEBRIDGE_USER,
            )

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Arranca el sondeo en background.
        Llamar desde main.py justo después de instanciar.
        """
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
            name="HomebridgePoll",
        )
        self._thread.start()
        logger.info(
            "[HomebridgeMonitor] Sondeo iniciado (cada %ds)", POLL_INTERVAL_S
        )

    def stop(self) -> None:
        """
        Detiene el sondeo limpiamente.
        Llamar en cleanup() de main.py.
        """
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=REQUEST_TIMEOUT + 1)
        logger.info("[HomebridgeMonitor] Sondeo detenido")

    def _poll_loop(self) -> None:
        """
        Bucle de background. Primera consulta inmediata al arrancar
        para poblar los badges lo antes posible.
        """
        while self._running:
            try:
                self.get_accessories()
            except Exception as e:
                logger.error("[HomebridgeMonitor] Error en poll_loop: %s", e)

            # Espera interrumpible: stop() lo despierta al instante
            self._stop_evt.wait(timeout=POLL_INTERVAL_S)
            if self._stop_evt.is_set():
                break

    # ── Autenticación ─────────────────────────────────────────────────────────

    def _authenticate(self) -> bool:
        """Obtiene un token JWT. Devuelve True si tiene éxito."""
        if not HOMEBRIDGE_HOST:
            logger.error("[HomebridgeMonitor] HOMEBRIDGE_HOST no configurado en .env")
            return False

        payload = json.dumps({
            "username": HOMEBRIDGE_USER,
            "password": HOMEBRIDGE_PASS,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{HOMEBRIDGE_URL}/api/auth/login",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode())
                token = data.get("access_token")
                if token:
                    with self._token_lock:
                        self._token = token
                    logger.info("[HomebridgeMonitor] Autenticación correcta")
                    return True
                logger.warning("[HomebridgeMonitor] Respuesta sin token: %s", data)
                return False
        except Exception as e:
            logger.error("[HomebridgeMonitor] Error de autenticación: %s", e)
            return False

    def _get_token(self) -> Optional[str]:
        """Devuelve el token actual; si no existe intenta autenticar."""
        with self._token_lock:
            token = self._token
        if token:
            return token
        if self._authenticate():
            with self._token_lock:
                return self._token
        return None

    def _request(self, method: str, path: str, body: Optional[Dict] = None) -> Optional[Dict]:
        """
        Petición autenticada. Si el token caduca (401) lo renueva una vez.
        """
        for attempt in range(2):
            token = self._get_token()
            if not token:
                return None

            payload = json.dumps(body).encode() if body else None
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            req = urllib.request.Request(
                f"{HOMEBRIDGE_URL}{path}",
                data=payload,
                headers=headers,
                method=method,
            )
            try:
                with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                    content = resp.read().decode()
                    return json.loads(content) if content else {}
            except urllib.error.HTTPError as e:
                if e.code == 401 and attempt == 0:
                    logger.warning("[HomebridgeMonitor] Token caducado, renovando...")
                    with self._token_lock:
                        self._token = None
                    continue
                logger.error("[HomebridgeMonitor] HTTP %s en %s: %s", e.code, path, e)
                return None
            except Exception as e:
                logger.error("[HomebridgeMonitor] Error en petición %s %s: %s", method, path, e)
                return None
        return None

    # ── Accesorios ────────────────────────────────────────────────────────────

    def get_accessories(self) -> List[Dict]:
        """
        Consulta Homebridge y actualiza self._accessories.
        Ahora reconoce 5 tipos de dispositivo:
          switch      — característica On (enchufe / interruptor)
          thermostat  — CurrentTemperature + TargetTemperature
          sensor      — CurrentTemperature o CurrentRelativeHumidity (solo lectura)
          blind       — CurrentPosition (persiana / estor)
          light       — On + Brightness (luz regulable)
        """
        data = self._request("GET", "/api/accessories")
        if data is None:
            self._reachable = False
            logger.warning("[HomebridgeMonitor] Sin conexión con Homebridge")
            return []

        self._reachable = True
        accesorios = data if isinstance(data, list) else data.get("accessories", [])

        devices = []
        for acc in accesorios:
            values = acc.get("values", {})
            name   = acc.get("serviceName", acc.get("name", "Desconocido"))
            uid    = acc.get("uniqueId", "")
            fault  = int(values.get("StatusFault",  0)) == 1
            active = int(values.get("StatusActive", 1)) == 1
            base   = {
                "uniqueId":    uid,
                "displayName": name,
                "fault":       fault,
                "inactive":    not active,
                "room":        acc.get("humanType", ""),
            }

            if "Brightness" in values and "On" in values:
                # Luz regulable
                devices.append({**base,
                    "type":       "light",
                    "on":         bool(values["On"]),
                    "brightness": int(values.get("Brightness", 0)),
                })
            elif "On" in values:
                # Enchufe / interruptor
                devices.append({**base,
                    "type": "switch",
                    "on":   bool(values["On"]),
                })
            elif "TargetTemperature" in values:
                # Termostato
                devices.append({**base,
                    "type":        "thermostat",
                    "current_temp": float(values.get("CurrentTemperature", 0)),
                    "target_temp":  float(values.get("TargetTemperature",  20)),
                })
            elif "CurrentPosition" in values:
                # Persiana / estor
                devices.append({**base,
                    "type":     "blind",
                    "position": int(values.get("CurrentPosition", 0)),
                })
            elif "CurrentTemperature" in values or "CurrentRelativeHumidity" in values:
                # Sensor de temperatura / humedad
                devices.append({**base,
                    "type":     "sensor",
                    "temp":     float(values.get("CurrentTemperature", 0))
                                if "CurrentTemperature" in values else None,
                    "humidity": float(values.get("CurrentRelativeHumidity", 0))
                                if "CurrentRelativeHumidity" in values else None,
                })

        with self._accessories_lock:
            self._accessories = devices

        logger.debug(
            "[HomebridgeMonitor] Sondeo OK — %d dispositivos (%s)",
            len(devices),
            ", ".join(
                f"{t}:{sum(1 for d in devices if d['type']==t)}"
                for t in ('switch','light','thermostat','sensor','blind')
                if any(d['type']==t for d in devices)
            ),
        )
        return devices

    def get_accessories_cached(self) -> List[Dict]:
        """
        Devuelve la lista en memoria sin hacer ninguna petición HTTP.
        Usar desde la ventana para el refresco visual inmediato.
        """
        with self._accessories_lock:
            return list(self._accessories)

    def toggle(self, unique_id: str, turn_on: bool) -> bool:
        """
        Cambia el estado On/Off de un accesorio.
        Tras el comando lanza un sondeo inmediato para que los badges
        reflejen el cambio sin esperar los 30s del ciclo normal.
        """
        body   = {"characteristicType": "On", "value": turn_on}
        result = self._request("PUT", f"/api/accessories/{unique_id}", body)
        if result is not None:
            logger.info(
                "[HomebridgeMonitor] %s → %s",
                unique_id, "ON" if turn_on else "OFF",
            )
            # Sondeo inmediato para actualizar badges al instante
            threading.Thread(
                target=self.get_accessories,
                daemon=True,
                name="HB-PostToggle",
            ).start()
            return True
        logger.error("[HomebridgeMonitor] Fallo al togglear %s", unique_id)
        return False

    # ── Métodos de badge (lectura desde memoria, sin HTTP) ────────────────────

    def is_reachable(self) -> bool:
        """True si la última consulta fue exitosa."""
        return bool(self._reachable)

    def get_offline_count(self) -> int:
        """1 si Homebridge no respondió en la última consulta. 0 en cualquier otro caso."""
        if self._reachable is None:
            return 0  # sin consultar aún — no mostrar badge al arrancar
        return 0 if self._reachable else 1

    def get_on_count(self) -> int:
        """Número de enchufes encendidos. Badge naranja en el menú."""
        if self._reachable is None:
            return 0
        with self._accessories_lock:
            return sum(1 for a in self._accessories if a.get("on", False))

    def get_fault_count(self) -> int:
        """Número de dispositivos con StatusFault=1. Badge rojo en el menú."""
        if self._reachable is None:
            return 0
        with self._accessories_lock:
            return sum(1 for a in self._accessories if a.get("fault", False))
        
    def set_brightness(self, unique_id: str, brightness: int) -> bool:
        """Establece el brillo de una luz (0–100)."""
        brightness = max(0, min(100, brightness))
        result = self._request(
            "PUT", f"/api/accessories/{unique_id}",
            {"characteristicType": "Brightness", "value": brightness}
        )
        if result is not None:
            logger.info("[HomebridgeMonitor] Brillo %s → %d%%", unique_id, brightness)
            threading.Thread(target=self.get_accessories, daemon=True,
                             name="HB-PostBrightness").start()
            return True
        return False

    def set_target_temp(self, unique_id: str, temp: float) -> bool:
        """Establece la temperatura objetivo de un termostato."""
        result = self._request(
            "PUT", f"/api/accessories/{unique_id}",
            {"characteristicType": "TargetTemperature", "value": temp}
        )
        if result is not None:
            logger.info("[HomebridgeMonitor] Termostato %s → %.1f°C", unique_id, temp)
            threading.Thread(target=self.get_accessories, daemon=True,
                             name="HB-PostTemp").start()
            return True
        return False
````

## File: ui/widgets/__init__.py
````python
"""
Paquete de widgets personalizados
"""
from .graphs import GraphWidget, update_graph_lines, recolor_lines
from .dialogs import custom_msgbox, confirm_dialog, terminal_dialog

__all__ = ['GraphWidget', 'update_graph_lines', 'recolor_lines', 
           'custom_msgbox', 'confirm_dialog', 'terminal_dialog']
````

## File: utils/logger.py
````python
"""
Sistema de logging robusto para el dashboard
Funciona correctamente tanto desde terminal como desde auto-start

Ubicación: utils/logger.py
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler
import os


class DashboardLogger:
    """Logger centralizado para el dashboard"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Configura el logger con rutas absolutas y rotación automática"""
        
        # 1. Obtener directorio del proyecto de forma absoluta
        if hasattr(sys, '_MEIPASS'):
            # Si está empaquetado con PyInstaller
            project_root = Path(sys._MEIPASS)
        else:
            # utils/logger.py -> utils/ -> project_root/
            project_root = Path(__file__).parent.parent.resolve()
        
        # 2. Crear directorio de logs
        log_dir = project_root / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. Nombre fijo para que la rotación funcione
        # (Si el nombre cambia cada día, el sistema no puede detectar el tamaño del archivo previo)
        log_file = log_dir / "dashboard.log"
        
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 4. Configurar RotatingFileHandler
        # maxBytes: 2MB (2 * 1024 * 1024)
        # backupCount: 1 (mantiene el archivo actual y uno de respaldo .log.1)
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=2*1024*1024, 
            backupCount=1,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # 5. Handler para consola (solo si hay terminal)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)
        
        # 6. Configurar root logger
        self.logger = logging.getLogger('Dashboard')
        self.logger.setLevel(logging.DEBUG)
        
        # Evitar duplicar handlers si se instancia varias veces
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            
            try:
                if sys.stdout and sys.stdout.isatty():
                    self.logger.addHandler(console_handler)
            except:
                pass
        
        # Log de confirmación
        self.logger.info("=" * 60)
        self.logger.info(f"Logger inicializado - Archivo: {log_file}")
        self.logger.info(f"Límite de tamaño: 2MB con rotación activa")
        self.logger.info("=" * 60)

    def get_logger(self, name: str):
        """Obtiene un sub-logger para un módulo específico (ej: Dashboard.Database)"""
        return logging.getLogger(f'Dashboard.{name}')


# Singleton global
_dashboard_logger = None

def get_logger(name: str):
    """
    Obtiene logger para un módulo
    
    Uso:
        from utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Mensaje")
        logger.warning("Advertencia")
        logger.error("Error")
        logger.debug("Debug")
    
    Args:
        name: Nombre del módulo (usa __name__)
        
    Returns:
        Logger configurado
    """
    global _dashboard_logger
    if _dashboard_logger is None:
        _dashboard_logger = DashboardLogger()
    return _dashboard_logger.get_logger(name)


def log_startup_info():
    """Log información de inicio del sistema"""
    logger = get_logger('startup')
    
    # Información del entorno
    logger.info(f"Python: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"CWD: {os.getcwd()}")
    logger.info(f"User: {os.getenv('USER', 'unknown')}")
    logger.info(f"HOME: {os.getenv('HOME', 'unknown')}")
    
    # Variables de entorno relevantes
    display = os.getenv('DISPLAY', 'not set')
    logger.info(f"DISPLAY: {display}")
    
    if display == 'not set':
        logger.warning("DISPLAY no configurado - posible problema de GUI")
````

## File: THEMES_GUIDE.md
````markdown
# 🎨 Guía de Temas - System Dashboard

El dashboard incluye **15 temas profesionales** pre-configurados y la capacidad de crear temas personalizados.

---

## 🌈 Temas Disponibles

### 1. **Cyberpunk** (Original) ⚡
```
Colores: Cyan neón + Verde oscuro
Estilo: Futurista, neón brillante
Ideal para: Look cyberpunk clásico
```
**Paleta:**
- Primary: `#00ffff` (Cyan brillante)
- Secondary: `#14611E` (Verde oscuro)
- Success: `#1ae313` (Verde neón)
- Warning: `#ffaa00` (Naranja)
- Danger: `#ff3333` (Rojo)

---

### 2. **Matrix** 💚
```
Colores: Verde Matrix brillante
Estilo: Película Matrix
Ideal para: Fans de Matrix
```
**Paleta:**
- Primary: `#00ff00` (Verde Matrix)
- Secondary: `#0aff0a` (Verde brillante)
- Success: `#00ff00` (Verde puro)
- Warning: `#ccff00` (Verde-amarillo lima)
- Danger: `#ff0000` (Rojo)

**✨ Colores optimizados** para alto contraste.

---

### 3. **Sunset** 🌅
```
Colores: Naranja cálido + Púrpura
Estilo: Atardecer cálido
Ideal para: Ambiente acogedor
```
**Paleta:**
- Primary: `#ff6b35` (Naranja cálido)
- Secondary: `#f7931e` (Naranja dorado)
- Success: `#ffd23f` (Amarillo dorado)
- Warning: `#ffd23f` (Amarillo)
- Danger: `#d62828` (Rojo oscuro)

---

### 4. **Ocean** 🌊
```
Colores: Azul océano + Aqua
Estilo: Marino refrescante
Ideal para: Look fresco y limpio
```
**Paleta:**
- Primary: `#00d4ff` (Azul cielo)
- Secondary: `#48dbfb` (Azul claro)
- Success: `#1dd1a1` (Verde agua)
- Warning: `#feca57` (Amarillo suave)
- Danger: `#ee5a6f` (Rosa coral)

---

### 5. **Dracula** 🦇
```
Colores: Púrpura + Rosa pastel
Estilo: Elegante oscuro
Ideal para: Desarrolladores
```
**Paleta:**
- Primary: `#bd93f9` (Púrpura pastel)
- Secondary: `#ff79c6` (Rosa)
- Success: `#50fa7b` (Verde pastel)
- Warning: `#f1fa8c` (Amarillo pastel)
- Danger: `#ff5555` (Rojo pastel)

**Popular en editores de código.**

---

### 6. **Nord** ❄️
```
Colores: Azul hielo nórdico
Estilo: Minimalista frío
Ideal para: Estética nórdica
```
**Paleta:**
- Primary: `#88c0d0` (Azul hielo)
- Secondary: `#5e81ac` (Azul oscuro)
- Success: `#a3be8c` (Verde suave)
- Warning: `#ebcb8b` (Amarillo suave)
- Danger: `#bf616a` (Rojo suave)

---

### 7. **Tokyo Night** 🌃
```
Colores: Azul + Púrpura noche
Estilo: Noche de Tokio
Ideal para: Ambiente nocturno
```
**Paleta:**
- Primary: `#7aa2f7` (Azul brillante)
- Secondary: `#bb9af7` (Púrpura)
- Success: `#9ece6a` (Verde)
- Warning: `#e0af68` (Naranja suave)
- Danger: `#f7768e` (Rosa)

---

### 8. **Monokai** 🎨
```
Colores: Cyan + Verde lima
Estilo: IDE clásico
Ideal para: Programadores
```
**Paleta:**
- Primary: `#66d9ef` (Azul claro)
- Secondary: `#fd971f` (Naranja)
- Success: `#a6e22e` (Verde lima)
- Warning: `#e6db74` (Amarillo)
- Danger: `#f92672` (Rosa fucsia)

**Tema icónico de Sublime Text.**

---

### 9. **Gruvbox** 🏜️
```
Colores: Naranja + Beige retro
Estilo: Cálido vintage
Ideal para: Fans del retro
```
**Paleta:**
- Primary: `#fe8019` (Naranja)
- Secondary: `#d65d0e` (Naranja oscuro)
- Success: `#b8bb26` (Verde lima)
- Warning: `#fabd2f` (Amarillo)
- Danger: `#fb4934` (Rojo)

---

### 10. **Solarized Dark** ☀️
```
Colores: Azul + Cyan
Estilo: Elegante científico
Ideal para: Precisión visual
```
**Paleta:**
- Primary: `#268bd2` (Azul)
- Secondary: `#2aa198` (Cyan)
- Success: `#859900` (Verde oliva)
- Warning: `#b58900` (Amarillo oscuro)
- Danger: `#dc322f` (Rojo)

**Diseñado para reducir fatiga visual.**

---

### 11. **One Dark** 🌑
```
Colores: Azul claro + Cyan
Estilo: Moderno equilibrado
Ideal para: Uso prolongado
```
**Paleta:**
- Primary: `#61afef` (Azul claro)
- Secondary: `#56b6c2` (Cyan)
- Success: `#98c379` (Verde)
- Warning: `#e5c07b` (Amarillo)
- Danger: `#e06c75` (Rojo suave)

**Tema de Atom editor.**

---

### 12. **Synthwave 84** 🌆
```
Colores: Rosa + Verde neón
Estilo: Retro 80s
Ideal para: Nostalgia synthwave
```
**Paleta:**
- Primary: `#f92aad` (Rosa neón)
- Secondary: `#fe4450` (Rojo neón)
- Success: `#72f1b8` (Verde neón)
- Warning: `#fede5d` (Amarillo neón)
- Danger: `#fe4450` (Rojo neón)

**Inspirado en los 80s.**

---

### 13. **GitHub Dark** 🐙
```
Colores: Azul GitHub
Estilo: Profesional limpio
Ideal para: Desarrolladores
```
**Paleta:**
- Primary: `#58a6ff` (Azul GitHub)
- Secondary: `#1f6feb` (Azul oscuro)
- Success: `#3fb950` (Verde)
- Warning: `#d29922` (Amarillo)
- Danger: `#f85149` (Rojo)

---

### 14. **Material Dark** 📱
```
Colores: Azul Material Design
Estilo: Google Material
Ideal para: Estética moderna
```
**Paleta:**
- Primary: `#82aaff` (Azul material)
- Secondary: `#c792ea` (Púrpura)
- Success: `#c3e88d` (Verde claro)
- Warning: `#ffcb6b` (Amarillo)
- Danger: `#f07178` (Rojo suave)

---

### 15. **Ayu Dark** 🌙
```
Colores: Azul cielo minimalista
Estilo: Moderno limpio
Ideal para: Simplicidad
```
**Paleta:**
- Primary: `#59c2ff` (Azul cielo)
- Secondary: `#39bae6` (Azul claro)
- Success: `#aad94c` (Verde lima)
- Warning: `#ffb454` (Naranja)
- Danger: `#f07178` (Rosa)

---

## 🔄 Cambiar Tema

### **Desde la Interfaz:**
1. Menú principal → "Cambiar Tema"
2. Selecciona tu tema favorito
3. Clic en "Aplicar y Reiniciar"
4. ✨ Dashboard se reinicia automáticamente

### **Desde Código:**
Editar `data/theme_config.json`:
```json
{
  "selected_theme": "matrix"
}
```

---

## 🎨 Crear Tema Personalizado

### **Paso 1: Editar `config/themes.py`**

```python
THEMES = {
    # ... temas existentes ...
    
    "mi_tema": {
        "name": "Mi Tema Personalizado",
        "colors": {
            "primary": "#ff00ff",      # Color principal
            "secondary": "#00ffff",    # Color secundario
            "success": "#00ff00",      # Verde éxito
            "warning": "#ffff00",      # Amarillo advertencia
            "danger": "#ff0000",       # Rojo peligro
            "bg_dark": "#000000",      # Fondo oscuro
            "bg_medium": "#111111",    # Fondo medio
            "bg_light": "#222222",     # Fondo claro
            "text": "#ffffff",         # Texto
            "text_dim": "#aaaaaa",     # Texto tenue
            "border": "#ff00ff"        # Borde
        }
    }
}
```

### **Paso 2: Usar el Tema**

1. Reinicia el dashboard
2. "Cambiar Tema" → Aparecerá "Mi Tema Personalizado"
3. Selecciónalo y aplica

---

## 🎯 Guía de Colores

### **Colores Obligatorios:**
```python
"primary"    # Botones, sliders, elementos principales
"secondary"  # Títulos, elementos secundarios
"success"    # Indicadores positivos (<30% uso)
"warning"    # Indicadores medios (30-70% uso)
"danger"     # Indicadores altos (>70% uso)
"bg_dark"    # Fondo más oscuro
"bg_medium"  # Fondo medio
"bg_light"   # Fondo más claro
"text"       # Texto principal
"text_dim"   # Texto secundario/tenue
"border"     # Bordes de elementos
```

### **Dónde se Usa Cada Color:**

| Color | Uso |
|-------|-----|
| `primary` | Botones, sliders activos, bordes principales |
| `secondary` | Títulos de sección, hover de sliders/scrollbars |
| `success` | CPU/RAM <30%, mensajes de éxito |
| `warning` | CPU/RAM 30-70%, advertencias |
| `danger` | CPU/RAM >70%, errores, botón "Matar" |
| `bg_dark` | Fondo de cards, filas alternadas |
| `bg_medium` | Fondo principal de ventanas |
| `bg_light` | Fondo de sliders, elementos elevados |
| `text` | Texto principal |
| `text_dim` | Texto secundario (usuarios, paths) |
| `border` | Bordes de botones y elementos |

---

## 💡 Tips para Crear Temas

### **1. Contraste**
Asegura que `text` contraste bien con todos los fondos:
```python
# Bueno
"bg_dark": "#000000"
"text": "#ffffff"

# Malo (poco contraste)
"bg_dark": "#222222"
"text": "#333333"
```

### **2. Secondary Distintivo**
El color `secondary` debe ser diferente de los fondos:
```python
# ❌ Malo - secondary igual a bg_medium
"secondary": "#111111"
"bg_medium": "#111111"

# ✅ Bueno - secondary visible
"secondary": "#00ffff"
"bg_medium": "#111111"
```

### **3. Jerarquía de Fondos**
```python
bg_dark < bg_medium < bg_light
#000000   #111111     #222222
```

### **4. Paleta Armónica**
Usa una herramienta como:
- [Coolors.co](https://coolors.co)
- [Adobe Color](https://color.adobe.com)
- [Paletton](https://paletton.com)

---

## 🔍 Preview de Temas

Todos los temas han sido optimizados para:
- ✅ Alto contraste
- ✅ Legibilidad
- ✅ `secondary` distintivo
- ✅ Colores armónicos

**11 temas fueron corregidos** en v2.0 para tener `secondary` visible.

---

## 📊 Comparación de Temas

| Tema | Estilo | Colores Dominantes | Ideal Para |
|------|--------|-------------------|------------|
| Cyberpunk | Neón | Cyan + Verde | Original |
| Matrix | Película | Verde | Fans Matrix |
| Sunset | Cálido | Naranja + Púrpura | Acogedor |
| Ocean | Fresco | Azul + Aqua | Limpio |
| Dracula | Elegante | Púrpura + Rosa | Devs |
| Nord | Minimalista | Azul hielo | Nórdico |
| Tokyo Night | Nocturno | Azul + Púrpura | Noche |
| Monokai | IDE | Cyan + Verde | Código |
| Gruvbox | Retro | Naranja + Beige | Vintage |
| Solarized | Científico | Azul + Cyan | Precisión |
| One Dark | Moderno | Azul claro | Equilibrado |
| Synthwave | 80s | Rosa + Verde | Nostalgia |
| GitHub | Profesional | Azul GitHub | Devs |
| Material | Google | Azul material | Moderno |
| Ayu | Simple | Azul cielo | Minimalista |

---

## 🔄 Persistencia de Temas

El tema seleccionado se guarda en:
```
data/theme_config.json
```

**Se mantiene entre reinicios** del dashboard.

---

## 🆘 Troubleshooting

### **Tema no se aplica**
**Solución**: Usa "Aplicar y Reiniciar" (reinicia automáticamente)

### **Colores se ven mal**
**Causa**: Tema con contraste bajo  
**Solución**: Prueba otro tema o ajusta `text` y fondos

### **Secondary no se ve**
**Causa**: Color igual a fondo  
**Solución**: Ya corregido en v2.0. Actualiza.

---

**¡Personaliza tu dashboard!** 🎨✨
````

## File: config/themes.py
````python
"""
Sistema de temas personalizados
"""
import json
import os
from pathlib import Path
# ========================================
# TEMAS DISPONIBLES
# ========================================

THEMES = {
    "cyberpunk": {
        "name": "Cyberpunk (Original)",
        "colors": {
            "primary": "#00ffff",      # Cyan brillante
            "secondary": "#14611E",    # Verde oscuro ✓ OK
            "success": "#1ae313",      # Verde neón
            "warning": "#ffaa00",      # Naranja
            "danger": "#ff3333",       # Rojo
            "bg_dark": "#111111",      # Negro profundo
            "bg_medium": "#212121",    # Gris muy oscuro
            "bg_light": "#222222",     # Gris oscuro
            "text": "#ffffff",         # Blanco
            "text_dim": "#aaaaaa",     # Gris claro
            "border": "#00ffff"        # Cyan
        }
    },
    
    "matrix": {
        "name": "Matrix",
        "colors": {
            "primary": "#00ff00",      # Verde Matrix brillante
            "secondary": "#00ff88",    # Verde-cyan (bien diferente)
            "success": "#33ff33",      # Verde claro
            "warning": "#ffff00",      # Amarillo puro (muy diferente)
            "danger": "#ff0000",       # Rojo
            "bg_dark": "#000000",      # Negro puro
            "bg_medium": "#001a00",    # Negro verdoso sutil
            "bg_light": "#003300",     # Verde muy oscuro
            "text": "#00ff00",         # Verde brillante
            "text_dim": "#009900",     # Verde medio oscuro
            "border": "#00ff00"        # Verde brillante
        }
    },
    
    "sunset": {
        "name": "Sunset (Atardecer)",
        "colors": {
            "primary": "#ff6b35",      # Naranja cálido
            "secondary": "#f7931e",    # Naranja dorado ✓ CORREGIDO
            "success": "#ffd23f",      # Amarillo dorado
            "warning": "#ffd23f",      # Amarillo dorado
            "danger": "#d62828",       # Rojo oscuro
            "bg_dark": "#1a1423",      # Púrpura muy oscuro
            "bg_medium": "#2d1b3d",    # Púrpura oscuro
            "bg_light": "#3e2a47",     # Púrpura medio
            "text": "#f8f0e3",         # Beige claro
            "text_dim": "#c4b5a0",     # Beige oscuro
            "border": "#ff6b35"        # Naranja
        }
    },
    
    "ocean": {
        "name": "Ocean (Océano)",
        "colors": {
            "primary": "#00d4ff",      # Azul cielo
            "secondary": "#48dbfb",    # Azul claro ✓ CORREGIDO
            "success": "#1dd1a1",      # Verde agua
            "warning": "#feca57",      # Amarillo suave
            "danger": "#ee5a6f",       # Rosa coral
            "bg_dark": "#0c2233",      # Azul muy oscuro
            "bg_medium": "#163447",    # Azul oscuro
            "bg_light": "#1e4a5f",     # Azul medio
            "text": "#e0f7ff",         # Azul muy claro
            "text_dim": "#8899aa",     # Azul grisáceo
            "border": "#00d4ff"        # Azul cielo
        }
    },
    
    "dracula": {
        "name": "Dracula",
        "colors": {
            "primary": "#bd93f9",      # Púrpura pastel
            "secondary": "#ff79c6",    # Rosa ✓ CORREGIDO
            "success": "#50fa7b",      # Verde pastel
            "warning": "#f1fa8c",      # Amarillo pastel
            "danger": "#ff5555",       # Rojo pastel
            "bg_dark": "#1e1f29",      # Azul muy oscuro
            "bg_medium": "#282a36",    # Gris azulado
            "bg_light": "#44475a",     # Gris medio
            "text": "#f8f8f2",         # Blanco suave
            "text_dim": "#6272a4",     # Azul grisáceo
            "border": "#bd93f9"        # Púrpura
        }
    },
    
    "nord": {
        "name": "Nord (Nórdico)",
        "colors": {
            "primary": "#88c0d0",      # Azul hielo
            "secondary": "#5e81ac",    # Azul oscuro ✓ CORREGIDO
            "success": "#a3be8c",      # Verde suave
            "warning": "#ebcb8b",      # Amarillo suave
            "danger": "#bf616a",       # Rojo suave
            "bg_dark": "#1e2229",      # Negro azulado
            "bg_medium": "#2e3440",    # Gris polar
            "bg_light": "#3b4252",     # Gris claro
            "text": "#eceff4",         # Blanco nieve
            "text_dim": "#8899aa",     # Gris azulado
            "border": "#88c0d0"        # Azul hielo
        }
    },
    
    "tokyo_night": {
        "name": "Tokyo Night",
        "colors": {
            "primary": "#7aa2f7",      # Azul brillante
            "secondary": "#bb9af7",    # Púrpura ✓ CORREGIDO
            "success": "#9ece6a",      # Verde
            "warning": "#e0af68",      # Naranja suave
            "danger": "#f7768e",       # Rosa
            "bg_dark": "#16161e",      # Negro azulado
            "bg_medium": "#1a1b26",    # Azul noche
            "bg_light": "#24283b",     # Azul oscuro
            "text": "#c0caf5",         # Azul claro
            "text_dim": "#565f89",     # Azul oscuro
            "border": "#7aa2f7"        # Azul
        }
    },
    
    "monokai": {
        "name": "Monokai",
        "colors": {
            "primary": "#66d9ef",      # Azul claro
            "secondary": "#fd971f",    # Naranja ✓ CORREGIDO
            "success": "#a6e22e",      # Verde lima
            "warning": "#e6db74",      # Amarillo
            "danger": "#f92672",       # Rosa fucsia
            "bg_dark": "#1e1f1c",      # Negro verdoso
            "bg_medium": "#272822",    # Verde muy oscuro
            "bg_light": "#3e3d32",     # Verde grisáceo
            "text": "#f8f8f2",         # Blanco suave
            "text_dim": "#75715e",     # Gris verdoso
            "border": "#66d9ef"        # Azul claro
        }
    },
    
    "gruvbox": {
        "name": "Gruvbox",
        "colors": {
            "primary": "#fe8019",      # Naranja
            "secondary": "#d65d0e",    # Naranja oscuro ✓ CORREGIDO
            "success": "#b8bb26",      # Verde lima
            "warning": "#fabd2f",      # Amarillo
            "danger": "#fb4934",       # Rojo
            "bg_dark": "#1d2021",      # Negro marrón
            "bg_medium": "#282828",    # Gris oscuro
            "bg_light": "#3c3836",     # Gris medio
            "text": "#ebdbb2",         # Beige claro
            "text_dim": "#a89984",     # Beige oscuro
            "border": "#fe8019"        # Naranja
        }
    },
    
    "solarized_dark": {
        "name": "Solarized Dark",
        "colors": {
            "primary": "#268bd2",      # Azul
            "secondary": "#2aa198",    # Cyan ✓ CORREGIDO
            "success": "#859900",      # Verde oliva
            "warning": "#b58900",      # Amarillo oscuro
            "danger": "#dc322f",       # Rojo
            "bg_dark": "#002b36",      # Azul noche
            "bg_medium": "#073642",    # Azul oscuro
            "bg_light": "#586e75",     # Gris azulado
            "text": "#fdf6e3",         # Beige muy claro
            "text_dim": "#839496",     # Gris azulado
            "border": "#268bd2"        # Azul
        }
    },
    
    "one_dark": {
        "name": "One Dark",
        "colors": {
            "primary": "#61afef",      # Azul claro
            "secondary": "#56b6c2",    # Cyan ✓ CORREGIDO
            "success": "#98c379",      # Verde
            "warning": "#e5c07b",      # Amarillo
            "danger": "#e06c75",       # Rojo suave
            "bg_dark": "#1e2127",      # Negro azulado
            "bg_medium": "#282c34",    # Gris oscuro
            "bg_light": "#3e4451",     # Gris medio
            "text": "#abb2bf",         # Gris claro
            "text_dim": "#5c6370",     # Gris oscuro
            "border": "#61afef"        # Azul
        }
    },
    
    "synthwave": {
        "name": "Synthwave 84",
        "colors": {
            "primary": "#f92aad",      # Rosa neón
            "secondary": "#fe4450",    # Rojo neón ✓ CORREGIDO
            "success": "#72f1b8",      # Verde neón
            "warning": "#fede5d",      # Amarillo neón
            "danger": "#fe4450",       # Rojo neón
            "bg_dark": "#0e0b16",      # Negro púrpura
            "bg_medium": "#241734",    # Púrpura oscuro
            "bg_light": "#2d1b3d",     # Púrpura medio
            "text": "#ffffff",         # Blanco
            "text_dim": "#ff7edb",     # Rosa claro
            "border": "#f92aad"        # Rosa neón
        }
    },
    
    "github_dark": {
        "name": "GitHub Dark",
        "colors": {
            "primary": "#58a6ff",      # Azul GitHub
            "secondary": "#1f6feb",    # Azul oscuro ✓ CORREGIDO
            "success": "#3fb950",      # Verde
            "warning": "#d29922",      # Amarillo
            "danger": "#f85149",       # Rojo
            "bg_dark": "#0d1117",      # Negro
            "bg_medium": "#161b22",    # Gris muy oscuro
            "bg_light": "#21262d",     # Gris oscuro
            "text": "#c9d1d9",         # Gris claro
            "text_dim": "#8b949e",     # Gris medio
            "border": "#58a6ff"        # Azul
        }
    },
    
    "material": {
        "name": "Material Dark",
        "colors": {
            "primary": "#82aaff",      # Azul material
            "secondary": "#c792ea",    # Púrpura ✓ CORREGIDO
            "success": "#c3e88d",      # Verde claro
            "warning": "#ffcb6b",      # Amarillo
            "danger": "#f07178",       # Rojo suave
            "bg_dark": "#0f111a",      # Negro azulado
            "bg_medium": "#1e2029",    # Gris oscuro
            "bg_light": "#292d3e",     # Gris azulado
            "text": "#eeffff",         # Blanco azulado
            "text_dim": "#546e7a",     # Gris azulado
            "border": "#82aaff"        # Azul
        }
    },
    
    "ayu_dark": {
        "name": "Ayu Dark",
        "colors": {
            "primary": "#59c2ff",      # Azul cielo
            "secondary": "#39bae6",    # Azul claro ✓ CORREGIDO
            "success": "#aad94c",      # Verde lima
            "warning": "#ffb454",      # Naranja
            "danger": "#f07178",       # Rosa
            "bg_dark": "#0a0e14",      # Negro azulado
            "bg_medium": "#0d1017",    # Negro
            "bg_light": "#1c2128",     # Gris muy oscuro
            "text": "#b3b1ad",         # Gris claro
            "text_dim": "#626a73",     # Gris oscuro
            "border": "#59c2ff"        # Azul
        }
    }
}

# Tema por defecto
DEFAULT_THEME = "cyberpunk"

# ========================================
# FUNCIONES DE GESTIÓN DE TEMAS
# ========================================

def get_theme(theme_name: str) -> dict:
    """
    Obtiene un tema por su nombre
    
    Args:
        theme_name: Nombre del tema
        
    Returns:
        Diccionario con los colores del tema
    """
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])


def get_available_themes() -> list:
    """
    Obtiene lista de temas disponibles
    
    Returns:
        Lista de tuplas (id, nombre_descriptivo)
    """
    return [(key, theme["name"]) for key, theme in THEMES.items()]


def get_theme_colors(theme_name: str) -> dict:
    """
    Obtiene los colores de un tema
    
    Args:
        theme_name: Nombre del tema
        
    Returns:
        Diccionario de colores
    """
    theme = get_theme(theme_name)
    return theme["colors"]


# ========================================
# PREVIEW DE TEMAS (Para mostrar al usuario)
# ========================================

def get_theme_preview() -> str:
    """
    Genera un texto con preview de todos los temas
    
    Returns:
        String con la lista de temas y sus colores principales
    """
    preview = "TEMAS DISPONIBLES:\n\n"
    
    for theme_id, theme_data in THEMES.items():
        colors = theme_data["colors"]
        preview += f"• {theme_data['name']} ({theme_id})\n"
        preview += f"  Color principal: {colors['primary']}\n"
        preview += f"  Fondo: {colors['bg_dark']}\n"
        preview += f"  Texto: {colors['text']}\n\n"
    
    return preview


# ========================================
# CREAR TEMA PERSONALIZADO
# ========================================

def create_custom_theme(name: str, colors: dict) -> dict:
    """
    Crea un tema personalizado
    
    Args:
        name: Nombre descriptivo del tema
        colors: Diccionario con los colores personalizados
        
    Returns:
        Diccionario del tema creado
    """
    # Validar que tenga todos los colores necesarios
    required_keys = ["primary", "secondary", "success", "warning", "danger",
                     "bg_dark", "bg_medium", "bg_light", "text", "border"]
    
    for key in required_keys:
        if key not in colors:
            raise ValueError(f"Falta el color '{key}' en el tema personalizado")
    
    return {
        "name": name,
        "colors": colors
    }


# ========================================
# GUARDAR/CARGAR TEMA SELECCIONADO
# ========================================


THEME_CONFIG_FILE = Path(__file__).parent.parent / "data" / "theme_config.json"


def save_selected_theme(theme_name: str):
    """
    Guarda el tema seleccionado en archivo
    
    Args:
        theme_name: Nombre del tema a guardar
    """
    # Asegurar que el directorio existe
    THEME_CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    config = {"selected_theme": theme_name}
    
    tmp_file = str(THEME_CONFIG_FILE) + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(config, f, indent=2)
    os.replace(tmp_file, THEME_CONFIG_FILE)


def load_selected_theme() -> str:
    """
    Carga el tema seleccionado desde archivo
    
    Returns:
        Nombre del tema seleccionado o DEFAULT_THEME
    """
    try:
        with open(THEME_CONFIG_FILE) as f:
            config = json.load(f)
            theme = config.get("selected_theme", DEFAULT_THEME)
            
            # Verificar que el tema existe
            if theme in THEMES:
                return theme
            else:
                return DEFAULT_THEME
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_THEME
````

## File: core/cleanup_service.py
````python
"""
Servicio de limpieza automática de archivos exportados y datos antiguos
"""
import os
import glob
import threading
import time
from typing import Optional
from config.settings import DATA_DIR, EXPORTS_CSV_DIR, EXPORTS_LOG_DIR, EXPORTS_SCR_DIR
from utils.logger import get_logger

logger = get_logger(__name__)


class CleanupService:
    """
    Servicio background que limpia periódicamente archivos exportados
    y datos antiguos de la base de datos.

    Características:
    - Singleton: Solo una instancia en toda la aplicación
    - Thread-safe: Seguro para concurrencia
    - Daemon: Se cierra automáticamente con el programa
    - Configurable: límites de archivos y antigüedad ajustables
    """

    _instance: Optional['CleanupService'] = None
    _lock = threading.Lock()

    # ── Configuración por defecto ─────────────────────────────────────────────
    DEFAULT_MAX_CSV        = 10      # Máx. archivos CSV a conservar
    DEFAULT_MAX_PNG        = 10      # Máx. archivos PNG a conservar
    DEFAULT_MAX_LOG        = 10      # Máx. archivos log exportados a conservar
    DEFAULT_DB_DAYS        = 30      # Días de datos a conservar en BD
    DEFAULT_INTERVAL_HOURS = 24      # Cada cuántas horas limpiar

    def __new__(cls, *args, **kwargs):
        """Singleton: solo una instancia"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        data_logger=None,
        max_csv: int = DEFAULT_MAX_CSV,
        max_png: int = DEFAULT_MAX_PNG,
        max_log: int = DEFAULT_MAX_LOG,
        db_days: int = DEFAULT_DB_DAYS,
        interval_hours: float = DEFAULT_INTERVAL_HOURS,
    ):
        """
        Inicializa el servicio (solo la primera vez).

        Args:
            data_logger:     Instancia de DataLogger para limpiar la BD.
                             Si es None, solo se limpian archivos.
            max_csv:         Número máximo de CSV exportados a conservar.
            max_png:         Número máximo de PNG exportados a conservar.
            db_days:         Días de histórico a conservar en la BD.
            interval_hours:  Horas entre ejecuciones del ciclo de limpieza.
        """
        if hasattr(self, '_initialized'):
            return

        self.data_logger    = data_logger
        self.max_csv        = max_csv
        self.max_png        = max_png
        self.max_log        = max_log
        self.db_days        = db_days
        self.interval_hours = interval_hours

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._initialized = True

        logger.info(
            f"[CleanupService] Configurado — "
            f"CSV: {max_csv}, PNG: {max_png}, LOG: {max_log}, "
            f"BD: {db_days}d, intervalo: {interval_hours}h"
        )

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self):
        """Inicia el servicio en segundo plano."""
        if self._running:
            logger.info("[CleanupService] Ya está corriendo")
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="CleanupService"
        )
        self._thread.start()
        logger.info("[CleanupService] Servicio iniciado")

    def stop(self):
        """Detiene el servicio."""
        if not self._running:
            return
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[CleanupService] Servicio detenido")

    def _run(self):
        """Bucle principal: limpia al arrancar y luego cada interval_hours."""
        # Primera limpieza inmediata al arrancar
        self._cleanup_cycle()

        interval_seconds = self.interval_hours * 3600
        elapsed = 0.0
        while self._running:
            time.sleep(0.5)
            elapsed += 0.5
            if elapsed >= interval_seconds:
                self._cleanup_cycle()
                elapsed = 0.0

    # ── Lógica de limpieza ────────────────────────────────────────────────────

    def _cleanup_cycle(self):
        """Ejecuta un ciclo completo de limpieza."""
        logger.info("[CleanupService] Iniciando ciclo de limpieza")
        self.clean_csv()
        self.clean_png()
        self.clean_log_exports()
        if self.data_logger:
            self.clean_db()
        logger.info("[CleanupService] Ciclo de limpieza completado")

    def clean_csv(self, max_files: int = None) -> int:
        """
        Elimina los CSV exportados más antiguos que superen el límite.

        Args:
            max_files: Límite a aplicar. Si es None usa self.max_csv.

        Returns:
            Número de archivos eliminados.
        """
        limit = max_files if max_files is not None else self.max_csv
        pattern = os.path.join(str(EXPORTS_CSV_DIR), "history_*.csv")
        return self._trim_files(pattern, limit, "CSV")

    def clean_png(self, max_files: int = None) -> int:
        """
        Elimina los PNG exportados más antiguos que superen el límite.

        Args:
            max_files: Límite a aplicar. Si es None usa self.max_png.

        Returns:
            Número de archivos eliminados.
        """
        limit = max_files if max_files is not None else self.max_png
        pattern = os.path.join(str(EXPORTS_SCR_DIR), "*.png")
        return self._trim_files(pattern, limit, "PNG")


    def clean_log_exports(self, max_files: int = None) -> int:
        """
        Elimina los archivos de exportación de logs más antiguos que superen el límite.

        Args:
            max_files: Límite a aplicar. Si es None usa self.max_log.

        Returns:
            Número de archivos eliminados.
        """
        limit = max_files if max_files is not None else self.max_log
        pattern = os.path.join(str(EXPORTS_LOG_DIR), "log_export_*.log")
        return self._trim_files(pattern, limit, "LOG_EXPORT")

    def clean_db(self, days: int = None) -> bool:
        """
        Elimina registros de la BD más antiguos que 'days' días.

        Args:
            days: Antigüedad máxima. Si es None usa self.db_days.

        Returns:
            True si la limpieza fue exitosa.
        """
        if not self.data_logger:
            logger.warning("[CleanupService] No hay data_logger configurado")
            return False

        d = days if days is not None else self.db_days
        try:
            self.data_logger.clean_old_data(days=d)
            logger.info(f"[CleanupService] BD limpiada — registros >'{d}' días eliminados")
            return True
        except Exception as e:
            logger.error(f"[CleanupService] Error limpiando BD: {e}")
            return False

    def _trim_files(self, pattern: str, max_files: int, label: str) -> int:
        """
        Elimina los archivos más antiguos que superen max_files.

        Args:
            pattern:   Patrón glob de los archivos a gestionar.
            max_files: Número máximo a conservar.
            label:     Etiqueta para el log.

        Returns:
            Número de archivos eliminados.
        """
        try:
            files = sorted(glob.glob(pattern), key=os.path.getmtime)
            to_delete = files[:-max_files] if len(files) > max_files else []
            for f in to_delete:
                try:
                    os.remove(f)
                    logger.info(f"[CleanupService] {label} eliminado: {os.path.basename(f)}")
                except Exception as e:
                    logger.warning(f"[CleanupService] No se pudo eliminar {f}: {e}")
            if to_delete:
                logger.info(
                    f"[CleanupService] {label}: {len(to_delete)} eliminados, "
                    f"{len(files) - len(to_delete)} conservados"
                )
            return len(to_delete)
        except Exception as e:
            logger.error(f"[CleanupService] Error en _trim_files ({label}): {e}")
            return 0

    # ── Información y estado ──────────────────────────────────────────────────

    def get_status(self) -> dict:
        """
        Devuelve el estado actual del servicio.

        Returns:
            Diccionario con configuración y estado del hilo.
        """
        csv_files = glob.glob(os.path.join(str(EXPORTS_CSV_DIR), "history_*.csv"))
        png_files = glob.glob(os.path.join(str(EXPORTS_SCR_DIR), "*.png"))
        log_files = glob.glob(os.path.join(str(EXPORTS_LOG_DIR), "log_export_*.log"))
        return {
            'running':        self._running,
            'thread_alive':   self._thread.is_alive() if self._thread else False,
            'interval_hours': self.interval_hours,
            'max_csv':        self.max_csv,
            'max_png':        self.max_png,
            'max_log':        self.max_log,
            'db_days':        self.db_days,
            'csv_count':      len(csv_files),
            'png_count':      len(png_files),
            'log_count':      len(log_files),
        }

    def force_cleanup(self) -> dict:
        """
        Fuerza un ciclo de limpieza inmediato desde fuera del hilo.
        Útil para llamadas manuales desde la UI.

        Returns:
            Diccionario con el número de archivos eliminados y resultado de BD.
        """
        logger.info("[CleanupService] Limpieza forzada manualmente")
        deleted_csv = self.clean_csv()
        deleted_png = self.clean_png()
        deleted_log = self.clean_log_exports()
        db_ok = self.clean_db() if self.data_logger else False
        logger.info(
            f"[CleanupService] Limpieza manual completada — "
            f"CSV: {deleted_csv}, PNG: {deleted_png}, LOG: {deleted_log}, BD: {db_ok}"
        )
        return {'deleted_csv': deleted_csv, 'deleted_png': deleted_png, 'deleted_log': deleted_log, 'db_ok': db_ok}

    def is_running(self) -> bool:
        """Verifica si el servicio está corriendo."""
        return self._running
````

## File: core/service_monitor.py
````python
"""
Monitor de servicios systemd
"""
import subprocess
import threading
from typing import List, Dict, Optional
from utils import DashboardLogger


# Intervalo de actualización del caché de servicios (segundos).
# Los servicios cambian raramente — 10s es más que suficiente para el badge
# y no sobrecarga la Pi con systemctl cada 2s.
SERVICES_POLL_INTERVAL = 10


class ServiceMonitor:
    """
    Monitor de servicios systemd con caché en background.

    El método get_services() en versiones anteriores lanzaba systemctl
    en el hilo de UI cada 2s, bloqueando Tkinter. Ahora:
    - Un thread de background sondea systemctl cada 10s.
    - get_services() y get_stats() devuelven el caché sin bloquear.
    - La ventana ServiceWindow puede forzar un refresco con refresh_now().
    """

    def __init__(self):
        self.sort_by     = "name"   # name | state
        self.sort_reverse = False
        self.filter_type  = "all"   # all | active | inactive | failed
        self.dashboard_logger = DashboardLogger()
        self._logger = self.dashboard_logger.get_logger(__name__)

        # Caché thread-safe
        self._lock: threading.Lock = threading.Lock()
        self._cached_services: List[Dict] = []
        self._cached_stats: Dict = {
            'total': 0, 'active': 0, 'inactive': 0, 'failed': 0, 'enabled': 0
        }

        # Control del thread
        self._running  = False
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self.start()

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """Arranca el sondeo en background (llamado automáticamente en __init__)."""
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
            name="ServiceMonitorPoll",
        )
        self._thread.start()
        self._logger.info(
            "[ServiceMonitor] Sondeo iniciado (cada %ds)", SERVICES_POLL_INTERVAL
        )

    def stop(self) -> None:
        """Detiene el sondeo limpiamente."""
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=6)
        self._logger.info("[ServiceMonitor] Sondeo detenido")

    def _poll_loop(self) -> None:
        """Bucle de background: sondea systemctl y actualiza el caché."""
        self._do_poll()  # primera lectura inmediata
        while self._running:
            self._stop_evt.wait(timeout=SERVICES_POLL_INTERVAL)
            if self._stop_evt.is_set():
                break
            self._do_poll()

    def refresh_now(self) -> None:
        """
        Fuerza un refresco inmediato del caché en background.
        Llamar desde ServiceWindow tras start/stop/restart/enable/disable.
        """
        threading.Thread(
            target=self._do_poll,
            daemon=True,
            name="ServiceMonitor-ForceRefresh",
        ).start()

    # ── Sondeo ────────────────────────────────────────────────────────────────

    def _do_poll(self) -> None:
        """
        Ejecuta systemctl en background y actualiza el caché.
        Obtiene todos los servicios Y su estado enabled en dos llamadas,
        evitando el antipatrón de N subprocesses (uno por servicio).
        """
        try:
            services = self._fetch_services()
            stats    = self._compute_stats(services)

            with self._lock:
                self._cached_services = services
                self._cached_stats    = stats

        except Exception as e:
            self._logger.error("[ServiceMonitor] Error en _do_poll: %s", e)

    def _fetch_services(self) -> List[Dict]:
        """
        Obtiene la lista de servicios con una sola llamada a systemctl
        y enriquece con el estado enabled en una segunda llamada batch.
        """
        # ── 1. Listar unidades ─────────────────────────────────────────────
        result = subprocess.run(
            ["systemctl", "list-units", "--type=service", "--all", "--no-pager"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if result.returncode != 0:
            return []

        services = []
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if (not line.strip()
                    or line.startswith('UNIT')
                    or line.startswith('●')
                    or 'loaded units listed' in line):
                continue

            parts = line.split()
            if len(parts) < 4:
                continue

            unit = parts[0]
            if not unit.endswith('.service'):
                continue

            load        = parts[1]
            active      = parts[2]
            sub         = parts[3]
            description = ' '.join(parts[4:]) if len(parts) > 4 else ''
            name        = unit.replace('.service', '')

            services.append({
                'name':        name,
                'unit':        unit,
                'load':        load,
                'active':      active,
                'sub':         sub,
                'description': description,
                'enabled':     False,   # se rellena en el paso 2
            })

        if not services:
            return []

        # ── 2. Estado enabled — una sola llamada para todos ────────────────
        enabled_set = self._fetch_enabled_batch([s['unit'] for s in services])
        for s in services:
            s['enabled'] = s['unit'] in enabled_set

        # ── 3. Ordenar ─────────────────────────────────────────────────────
        if self.sort_by == "name":
            services.sort(key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
        elif self.sort_by == "state":
            order = {'active': 0, 'inactive': 1, 'failed': 2}
            services.sort(
                key=lambda x: order.get(x['active'], 3),
                reverse=self.sort_reverse,
            )

        return services

    def _fetch_enabled_batch(self, units: List[str]) -> set:
        """
        Obtiene el estado enabled de todos los servicios en UNA sola
        llamada a systemctl, en lugar de N llamadas separadas.
        Devuelve un set con los nombres de unidades que están enabled.
        """
        try:
            result = subprocess.run(
                ["systemctl", "is-enabled", "--"] + units,
                capture_output=True,
                text=True,
                timeout=8,
            )
            # La salida tiene una línea por unidad, en el mismo orden
            lines = result.stdout.strip().split('\n')
            enabled = set()
            for unit, state in zip(units, lines):
                if state.strip() == "enabled":
                    enabled.add(unit)
            return enabled
        except Exception as e:
            self._logger.warning("[ServiceMonitor] Error en is-enabled batch: %s", e)
            return set()

    def _compute_stats(self, services: List[Dict]) -> Dict:
        """Calcula las estadísticas a partir de la lista de servicios."""
        return {
            'total':    len(services),
            'active':   sum(1 for s in services if s['active'] == 'active'),
            'inactive': sum(1 for s in services if s['active'] == 'inactive'),
            'failed':   sum(1 for s in services if s['active'] == 'failed'),
            'enabled':  sum(1 for s in services if s['enabled']),
        }

    # ── API pública (lee del caché, no bloquea) ───────────────────────────────

    def get_services(self) -> List[Dict]:
        """
        Devuelve la lista de servicios del caché aplicando filtro actual.
        No lanza ningún subprocess — nunca bloquea el hilo de UI.
        """
        with self._lock:
            services = list(self._cached_services)

        # Aplicar filtro en memoria
        if self.filter_type != "all":
            services = [s for s in services if s['active'] == self.filter_type]

        return services

    def get_stats(self) -> Dict:
        """
        Devuelve las estadísticas del caché.
        No lanza ningún subprocess — nunca bloquea el hilo de UI.
        """
        with self._lock:
            return dict(self._cached_stats)

    def search_services(self, query: str) -> List[Dict]:
        """Busca servicios por nombre o descripción (en el caché)."""
        query = query.lower()
        with self._lock:
            all_services = list(self._cached_services)
        return [
            s for s in all_services
            if query in s['name'].lower() or query in s['description'].lower()
        ]

    # ── Control de servicios (subprocesses bloqueantes, solo bajo demanda) ────

    def start_service(self, name: str) -> tuple:
        """Inicia un servicio y fuerza refresco del caché."""
        ok, msg = self._run_systemctl("start", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def stop_service(self, name: str) -> tuple:
        """Detiene un servicio y fuerza refresco del caché."""
        ok, msg = self._run_systemctl("stop", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def restart_service(self, name: str) -> tuple:
        """Reinicia un servicio y fuerza refresco del caché."""
        ok, msg = self._run_systemctl("restart", name)
        if ok:
            self.refresh_now()
        return ok, msg

    def enable_service(self, name: str) -> tuple:
        """Habilita autostart y fuerza refresco del caché."""
        ok, msg = self._run_systemctl("enable", name, sudo=False)
        if ok:
            self.refresh_now()
        return ok, msg

    def disable_service(self, name: str) -> tuple:
        """Deshabilita autostart y fuerza refresco del caché."""
        ok, msg = self._run_systemctl("disable", name, sudo=False)
        if ok:
            self.refresh_now()
        return ok, msg

    def _run_systemctl(self, action: str, name: str, sudo: bool = True) -> tuple:
        """Ejecuta un comando systemctl. Uso interno."""
        cmd = (["sudo"] if sudo else []) + ["systemctl", action, f"{name}.service"]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                self._logger.info("[ServiceMonitor] %s '%s' OK", action, name)
                return True, f"Servicio '{name}' {action} correctamente"
            self._logger.error(
                "[ServiceMonitor] Error en %s '%s': %s", action, name, result.stderr
            )
            return False, f"Error: {result.stderr}"
        except Exception as e:
            self._logger.error("[ServiceMonitor] Error en %s '%s': %s", action, name, e)
            return False, f"Error: {str(e)}"

    def get_logs(self, name: str, lines: int = 50) -> str:
        """Obtiene logs de un servicio vía journalctl."""
        try:
            result = subprocess.run(
                ["journalctl", "-u", f"{name}.service", "-n", str(lines), "--no-pager"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout
            return f"Error obteniendo logs: {result.stderr}"
        except Exception as e:
            return f"Error: {str(e)}"

    # ── Configuración de vista ────────────────────────────────────────────────

    def set_sort(self, column: str, reverse: bool = False) -> None:
        self.sort_by     = column
        self.sort_reverse = reverse

    def set_filter(self, filter_type: str) -> None:
        self.filter_type = filter_type

    def get_state_color(self, state: str) -> str:
        if state == "active":
            return "success"
        elif state == "failed":
            return "danger"
        return "text_dim"
````

## File: core/update_monitor.py
````python
"""
Monitor de actualizaciones del sistema
"""
import subprocess
import time
from typing import Dict
from utils.logger import get_logger

logger = get_logger(__name__)


class UpdateMonitor:
    """Lógica para verificar actualizaciones del sistema con caché"""

    def __init__(self):
        # Inicializar con tiempo actual para que la caché sea válida desde el inicio
        # Solo ejecuta apt update real cuando: arranque (main.py) o usuario pulsa "Buscar"
        self.last_check_time = time.time()
        self.cached_result = {"pending": 0, "status": "Unknown", "message": "No comprobado"}
        self.check_interval = 43200  # 12 horas en segundos

    def check_updates(self, force=False) -> Dict:
        """
        Verifica actualizaciones pendientes con sistema de caché.

        Args:
            force: Si True, ignora el caché y ejecuta apt update real

        Returns:
            Diccionario con pending, status y message
        """
        current_time = time.time()

        # Devolver caché si no ha pasado el intervalo y no se fuerza
        if not force and (current_time - self.last_check_time) < self.check_interval:
            logger.debug("[UpdateMonitor] Devolviendo resultado en caché")
            return self.cached_result

        try:
            logger.info("[UpdateMonitor] Ejecutando búsqueda real de actualizaciones (apt update)...")

            result = subprocess.run(
                ["sudo", "apt", "update"],
                capture_output=True,
                timeout=20
            )
            if result.returncode != 0:
                logger.warning(f"[UpdateMonitor] apt update retornó código {result.returncode}")

            cmd = "apt-get -s upgrade | grep '^Inst ' | wc -l"
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            count = int(output) if output else 0

            if count > 0:
                logger.info(f"[UpdateMonitor] {count} paquetes pendientes de actualización")
            else:
                logger.debug("[UpdateMonitor] Sistema al día, sin actualizaciones pendientes")

            self.cached_result = {
                "pending": count,
                "status": "Ready" if count > 0 else "Updated",
                "message": f"{count} paquetes pendientes" if count > 0 else "Sistema al día"
            }
            self.last_check_time = current_time
            return self.cached_result

        except subprocess.TimeoutExpired:
            logger.error("[UpdateMonitor] check_updates: timeout ejecutando apt update (>20s)")
            return {"pending": 0, "status": "Error", "message": "Timeout ejecutando apt update"}
        except FileNotFoundError:
            logger.error("[UpdateMonitor] check_updates: apt no encontrado en el sistema")
            return {"pending": 0, "status": "Error", "message": "apt no encontrado"}
        except ValueError as e:
            logger.error(f"[UpdateMonitor] check_updates: error parseando resultado: {e}")
            return {"pending": 0, "status": "Error", "message": str(e)}
        except Exception as e:
            logger.error(f"[UpdateMonitor] check_updates: error inesperado: {e}")
            return {"pending": 0, "status": "Error", "message": str(e)}
````

## File: ui/windows/homebridge.py
````python
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
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        # ── Header unificado ──────────────────────────────────────────────────
        self._header = make_window_header(
            main,
            title="HOMEBRIDGE",
            on_close=self._on_close,
            status_text="Conectando...",
        )

        # ── Barra de estado ───────────────────────────────────────────────────
        status_bar = ctk.CTkFrame(main, fg_color=COLORS['bg_dark'])
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
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
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
        bottom = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
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
        def on_toggle(new_state, uid=acc["uniqueId"]):
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
````

## File: ui/windows/service.py
````python
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
````

## File: ui/windows/usb.py
````python
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
````

## File: utils/__init__.py
````python
"""
Paquete de utilidades
"""
from .file_manager import FileManager
from .system_utils import SystemUtils
from .logger import DashboardLogger

__all__ = ['FileManager', 'SystemUtils', 'DashboardLogger']
````

## File: utils/file_manager.py
````python
"""
Gestión de archivos JSON para estado y configuración
"""
import json
import os
from typing import Dict, List, Any
from config.settings import STATE_FILE, CURVE_FILE
from utils.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """Gestor centralizado de archivos JSON"""
    
    @staticmethod
    def write_state(data: Dict[str, Any]) -> None:
        """
        Escribe el estado de forma atómica usando archivo temporal
        
        Args:
            data: Diccionario con los datos a guardar
        """
        tmp = str(STATE_FILE) + ".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, STATE_FILE)
        except OSError as e:
            logger.error(f"[FileManager] write_state: error escribiendo estado: {e}")
            raise
    
    @staticmethod
    def load_state() -> Dict[str, Any]:
        """
        Carga el estado guardado
        
        Returns:
            Diccionario con mode y target_pwm
        """
        default_state = {"mode": "auto", "target_pwm": None}
        
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logger.warning("[FileManager] load_state: contenido inválido, usando estado por defecto")
                    return default_state
                return {
                    "mode": data.get("mode", "auto"),
                    "target_pwm": data.get("target_pwm")
                }
        except FileNotFoundError:
            logger.debug(f"[FileManager] load_state: {STATE_FILE} no existe, usando estado por defecto")
            return default_state
        except json.JSONDecodeError as e:
            logger.error(f"[FileManager] load_state: JSON corrupto en {STATE_FILE}: {e} — usando estado por defecto")
            return default_state
    
    @staticmethod
    def load_curve() -> List[Dict[str, int]]:
        """
        Carga la curva de ventiladores
        
        Returns:
            Lista de puntos ordenados por temperatura
        """
        default_curve = [
            {"temp": 40, "pwm": 100},
            {"temp": 50, "pwm": 100},
            {"temp": 60, "pwm": 100},
            {"temp": 70, "pwm": 63},
            {"temp": 80, "pwm": 81}
        ]
        
        try:
            with open(CURVE_FILE) as f:
                data = json.load(f)
                pts = data.get("points", [])
                
                if not isinstance(pts, list):
                    logger.warning("[FileManager] load_curve: 'points' no es una lista, usando curva por defecto")
                    return default_curve
                
                sanitized = []
                for p in pts:
                    try:
                        temp = int(p.get("temp", 0))
                    except (ValueError, TypeError):
                        temp = 0
                    
                    try:
                        pwm = int(p.get("pwm", 0))
                    except (ValueError, TypeError):
                        pwm = 0
                    
                    pwm = max(0, min(255, pwm))
                    sanitized.append({"temp": temp, "pwm": pwm})
                
                if not sanitized:
                    logger.warning("[FileManager] load_curve: curva vacía tras sanear, usando curva por defecto")
                    return default_curve
                
                return sorted(sanitized, key=lambda x: x["temp"])
                
        except FileNotFoundError:
            logger.debug(f"[FileManager] load_curve: {CURVE_FILE} no existe, usando curva por defecto")
            return default_curve
        except json.JSONDecodeError as e:
            logger.error(f"[FileManager] load_curve: JSON corrupto en {CURVE_FILE}: {e} — usando curva por defecto")
            return default_curve
    
    @staticmethod
    def save_curve(points: List[Dict[str, int]]) -> None:
        """
        Guarda la curva de ventiladores
        
        Args:
            points: Lista de puntos {temp, pwm}
        """
        data = {"points": points}
        tmp = str(CURVE_FILE) + ".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, CURVE_FILE)
            logger.info(f"[FileManager] save_curve: curva guardada ({len(points)} puntos)")
        except OSError as e:
            logger.error(f"[FileManager] save_curve: error guardando curva: {e}")
            raise
````

## File: core/process_monitor.py
````python
"""
Monitor de procesos del sistema
"""
import psutil
from typing import List, Dict
from datetime import datetime
from utils import DashboardLogger


class ProcessMonitor:
    """Monitor de procesos en tiempo real"""
    
    def __init__(self):
        """Inicializa el monitor de procesos"""
        self.sort_by = "cpu"  # cpu, memory, name, pid
        self.sort_reverse = True
        self.filter_type = "all"  # all, user, system
        self.dashboard_logger = DashboardLogger()
    
    def get_processes(self, limit: int = 20) -> List[Dict]:
        """
        Obtiene lista de procesos con su información
        
        Args:
            limit: Número máximo de procesos a retornar
            
        Returns:
            Lista de diccionarios con información de procesos
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'cmdline', 'exe']):
            try:
                pinfo = proc.info
                
                # Aplicar filtro
                if self.filter_type == "user":
                    # Solo procesos del usuario actual
                    if pinfo['username'] != psutil.Process().username():
                        continue
                elif self.filter_type == "system":
                    # Solo procesos del sistema (root, etc)
                    if pinfo['username'] == psutil.Process().username():
                        continue
                
                # Obtener descripción más detallada
                cmdline = pinfo['cmdline']
                exe = pinfo['exe']
                name = pinfo['name'] or 'N/A'
                
                # Crear descripción mejor
                if cmdline:
                    # Si hay cmdline, usar el primer argumento como descripción
                    display_name = ' '.join(cmdline[:2])  # Primeros 2 argumentos
                elif exe:
                    # Si no hay cmdline pero hay exe, usar el path
                    display_name = exe
                else:
                    display_name = name
                
                processes.append({
                    'pid': pinfo['pid'],
                    'name': name,
                    'display_name': display_name,  # Nueva columna descriptiva
                    'username': pinfo['username'] or 'N/A',
                    'cpu': pinfo['cpu_percent'] or 0.0,
                    'memory': pinfo['memory_percent'] or 0.0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Ordenar según criterio
        if self.sort_by == "cpu":
            processes.sort(key=lambda x: x['cpu'], reverse=self.sort_reverse)
        elif self.sort_by == "memory":
            processes.sort(key=lambda x: x['memory'], reverse=self.sort_reverse)
        elif self.sort_by == "name":
            processes.sort(key=lambda x: x['name'].lower(), reverse=self.sort_reverse)
        elif self.sort_by == "pid":
            processes.sort(key=lambda x: x['pid'], reverse=self.sort_reverse)
        
        return processes[:limit]
    
    def search_processes(self, query: str) -> List[Dict]:
        """
        Busca procesos por nombre o descripción
        
        Args:
            query: Texto a buscar en nombre de proceso
            
        Returns:
            Lista de procesos que coinciden
        """
        query = query.lower()
        all_processes = self.get_processes(limit=1000)  # Obtener todos
        
        return [p for p in all_processes 
                if query in p['name'].lower() or query in p.get('display_name', '').lower()]
    



    def kill_process(self, pid: int) -> tuple[bool, str]:
        """
        Mata un proceso por su PID
        
        Args:
            pid: ID del proceso
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            proc = psutil.Process(pid)
            name = proc.name()

            # Obtener display_name igual que en get_processes
            try:
                cmdline = proc.cmdline()
                display_name = ' '.join(cmdline[:2]) if cmdline else name
            except (psutil.AccessDenied, psutil.ZombieProcess):
                display_name = name

            proc.terminate()  # Intenta cerrar limpiamente
            
            # Esperar un poco
            proc.wait(timeout=3)
            self.dashboard_logger.get_logger(__name__).info(f"[ProcessMonitor] Proceso '{display_name}' (PID {pid}) terminado correctamente")
            return True, f"Proceso '{display_name}' (PID {pid}) terminado correctamente"
        except psutil.NoSuchProcess:
            self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Proceso con PID {pid} no existe")
            return False, f"Proceso con PID {pid} no existe"
        except psutil.AccessDenied:
            self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Sin permisos para terminar proceso {pid}")
            return False, f"Sin permisos para terminar proceso {pid}"
        except psutil.TimeoutExpired:
            # Si no se cierra, forzar
            try:
                proc.kill()
                self.dashboard_logger.get_logger(__name__).info(f"[ProcessMonitor] Proceso '{display_name}' (PID {pid}) forzado a cerrar")
                return True, f"Proceso '{display_name}' (PID {pid}) forzado a cerrar"
            except Exception as e:
                self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Error forzando cierre del proceso '{display_name}' (PID {pid}): {e}")
                return False, f"Error: {str(e)}"
        except Exception as e:
            self.dashboard_logger.get_logger(__name__).error(f"[ProcessMonitor] Error terminando proceso '{display_name}' (PID {pid}): {e}")
            return False, f"Error: {str(e)}"
    def get_system_stats(self) -> Dict:
        """
        Obtiene estadísticas generales del sistema
        
        Returns:
            Diccionario con estadísticas
        """
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # RAM
        mem = psutil.virtual_memory()
        mem_used_gb = mem.used / (1024**3)
        mem_total_gb = mem.total / (1024**3)
        mem_percent = mem.percent
        
        # Procesos
        total_processes = len(psutil.pids())
        
        # Uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = self._format_uptime(uptime.total_seconds())
        
        return {
            'cpu_percent': cpu_percent,
            'mem_used_gb': mem_used_gb,
            'mem_total_gb': mem_total_gb,
            'mem_percent': mem_percent,
            'total_processes': total_processes,
            'uptime': uptime_str
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """
        Formatea uptime en formato legible
        
        Args:
            seconds: Segundos de uptime
            
        Returns:
            String formateado
        """
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def set_sort(self, column: str, reverse: bool = True):
        """
        Configura el orden de procesos
        
        Args:
            column: Columna por la que ordenar (cpu, memory, name, pid)
            reverse: Si ordenar de mayor a menor
        """
        self.sort_by = column
        self.sort_reverse = reverse
    
    def set_filter(self, filter_type: str):
        """
        Configura el filtro de procesos
        
        Args:
            filter_type: Tipo de filtro (all, user, system)
        """
        self.filter_type = filter_type
    
    def get_process_color(self, value: float) -> str:
        """
        Obtiene color según porcentaje de uso
        
        Args:
            value: Porcentaje (0-100)
            
        Returns:
            Nombre del color en COLORS
        """
        if value >= 70:
            return "danger"
        elif value >= 30:
            return "warning"
        else:
            return "success"
````

## File: core/system_monitor.py
````python
"""
Monitor del sistema
"""
import threading
import psutil
from collections import deque
from typing import Dict, Optional
from config.settings import HISTORY, UPDATE_MS, COLORS
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class SystemMonitor:
    """
    Monitor centralizado de recursos del sistema.

    Las métricas se actualizan en un thread de background cada UPDATE_MS ms.
    La UI siempre lee del caché (get_current_stats / get_cached_stats),
    nunca bloquea el hilo principal de Tkinter.
    """

    def __init__(self):
        self.system_utils = SystemUtils()

        self.cpu_hist        = deque(maxlen=HISTORY)
        self.ram_hist        = deque(maxlen=HISTORY)
        self.temp_hist       = deque(maxlen=HISTORY)
        self.disk_hist       = deque(maxlen=HISTORY)
        self.disk_write_hist = deque(maxlen=HISTORY)
        self.disk_read_hist  = deque(maxlen=HISTORY)

        self._cache_lock = threading.Lock()
        self._cached: Dict = {
            'cpu': 0.0, 'ram': 0.0, 'ram_used': 0,
            'temp': 0.0, 'disk_usage': 0.0,
            'disk_read_mb': 0.0, 'disk_write_mb': 0.0,
        }

        self._last_disk_io = psutil.disk_io_counters()
        self._running      = False
        self._stop_evt     = threading.Event()
        self._thread       = None
        self._interval_s   = max(UPDATE_MS / 1000.0, 1.0)

        self.start()

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True, name="SystemMonitorPoll")
        self._thread.start()
        logger.info("[SystemMonitor] Sondeo iniciado (cada %.1fs)", self._interval_s)

    def stop(self) -> None:
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        logger.info("[SystemMonitor] Sondeo detenido")

    def _poll_loop(self) -> None:
        self._do_poll()
        while self._running:
            self._stop_evt.wait(timeout=self._interval_s)
            if self._stop_evt.is_set():
                break
            self._do_poll()

    def _do_poll(self) -> None:
        try:
            cpu      = psutil.cpu_percent()
            vm       = psutil.virtual_memory()
            temp     = self.system_utils.get_cpu_temp()
            disk_pct = psutil.disk_usage('/').percent

            disk_io      = psutil.disk_io_counters()
            disk_read_b  = max(0, disk_io.read_bytes  - self._last_disk_io.read_bytes)
            disk_write_b = max(0, disk_io.write_bytes - self._last_disk_io.write_bytes)
            self._last_disk_io = disk_io

            stats = {
                'cpu':           cpu,
                'ram':           vm.percent,
                'ram_used':      vm.used,
                'temp':          temp,
                'disk_usage':    disk_pct,
                'disk_read_mb':  (disk_read_b  / (1024 * 1024)) / self._interval_s,
                'disk_write_mb': (disk_write_b / (1024 * 1024)) / self._interval_s,
            }

            with self._cache_lock:
                self._cached = stats

            self.update_history(stats)

        except Exception as e:
            logger.error("[SystemMonitor] Error en _do_poll: %s", e)

    def get_current_stats(self) -> Dict:
        with self._cache_lock:
            return dict(self._cached)

    get_cached_stats = get_current_stats

    def update_history(self, stats: Dict) -> None:
        self.cpu_hist.append(stats['cpu'])
        self.ram_hist.append(stats['ram'])
        self.temp_hist.append(stats['temp'])
        self.disk_hist.append(stats['disk_usage'])
        self.disk_read_hist.append(stats['disk_read_mb'])
        self.disk_write_hist.append(stats['disk_write_mb'])

    def get_history(self) -> Dict:
        return {
            'cpu':        list(self.cpu_hist),
            'ram':        list(self.ram_hist),
            'temp':       list(self.temp_hist),
            'disk':       list(self.disk_hist),
            'disk_read':  list(self.disk_read_hist),
            'disk_write': list(self.disk_write_hist),
        }

    @staticmethod
    def level_color(value: float, warn: float, crit: float) -> str:
        if value >= crit:
            return COLORS['danger']
        elif value >= warn:
            return COLORS['warning']
        return COLORS['primary']
````

## File: ui/windows/monitor.py
````python
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

    def __init__(self, parent, system_monitor: SystemMonitor):
        super().__init__(parent)
        self.system_monitor = system_monitor
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
````

## File: ui/windows/process_window.py
````python
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
````

## File: ui/windows/theme_selector.py
````python
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
````

## File: ui/windows/update.py
````python
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
````

## File: utils/system_utils.py
````python
"""
Utilidades para obtener información del sistema
"""
import re
import socket
import psutil
import subprocess
import glob
from typing import Tuple, Dict, Optional, Any
from collections import namedtuple
from config.settings import UPDATE_MS
import json
from utils.logger import get_logger

logger = get_logger(__name__)


class SystemUtils:
    """Utilidades para interactuar con el sistema"""
    
    # Variable de clase para mantener estado de red entre llamadas
    _last_net_io = {}
    
    @staticmethod
    def get_cpu_temp() -> float:
        """
        Obtiene la temperatura de la CPU
        
        Returns:
            Temperatura en grados Celsius
        """
        # Método 1: vcgencmd (Raspberry Pi - método oficial)
        try:
            out = subprocess.check_output(
                ["vcgencmd", "measure_temp"],
                universal_newlines=True,
                timeout=2
            )
            temp_str = out.replace("temp=", "").replace("'C", "").strip()
            return float(temp_str)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        except ValueError as e:
            logger.warning(f"[SystemUtils] get_cpu_temp: formato inesperado de vcgencmd: {e}")
        
        # Método 2: sensors (Linux genérico)
        try:
            out = subprocess.check_output(["sensors"], universal_newlines=True, timeout=2)
            for line in out.split('\n'):
                if 'Package id 0:' in line or 'Tdie:' in line or 'CPU:' in line:
                    m = re.search(r'[\+\-](\d+\.\d+).C', line)
                    if m:
                        return float(m.group(1))
                        
            for line in out.split('\n'):
                if 'temp' in line.lower():
                    m = re.search(r'[\+\-](\d+\.\d+).C', line)
                    if m:
                        return float(m.group(1))
        except subprocess.TimeoutExpired:
            logger.warning("[SystemUtils] get_cpu_temp: timeout leyendo sensors")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Método 3: Fallback - leer de thermal_zone
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                val = f.read().strip()
                return float(val) / 1000.0
        except FileNotFoundError:
            logger.warning("[SystemUtils] get_cpu_temp: no se encontró thermal_zone0, retornando 0.0")
        except ValueError as e:
            logger.error(f"[SystemUtils] get_cpu_temp: error leyendo thermal_zone0: {e}")
        
        return 0.0
    
    @staticmethod
    def get_hostname() -> str:
        """
        Obtiene el nombre del host
        
        Returns:
            Nombre del host o "unknown"
        """
        try:
            return socket.gethostname()
        except Exception as e:
            logger.warning(f"[SystemUtils] get_hostname: {e}")
            return "unknown"
    
    @staticmethod
    def get_net_io(interface: Optional[str] = None) -> Tuple[str, Any]:
        """
        Obtiene estadísticas de red con auto-detección de interfaz activa
        
        Args:
            interface: Nombre de la interfaz o None para auto-detección
            
        Returns:
            Tupla (nombre_interfaz, estadísticas)
        """
        if not SystemUtils._last_net_io:
            SystemUtils._last_net_io = psutil.net_io_counters(pernic=True)
        
        stats = psutil.net_io_counters(pernic=True)
        
        if interface and interface in stats:
            SystemUtils._last_net_io = stats
            return interface, stats[interface]
        
        best_name = None
        best_speed = -1
        
        for name in stats:
            if name not in SystemUtils._last_net_io:
                continue
            
            curr = stats[name]
            prev = SystemUtils._last_net_io[name]
            
            speed = (
                (curr.bytes_recv - prev.bytes_recv) +
                (curr.bytes_sent - prev.bytes_sent)
            )
            
            if speed < 0 or speed > 500 * 1024 * 1024:
                continue
            
            if speed > best_speed:
                best_speed = speed
                best_name = name
        
        SystemUtils._last_net_io = stats
        
        if best_name:
            return best_name, stats[best_name]
        
        for iface, s in stats.items():
            if iface.startswith(('eth', 'enp', 'wlan', 'wlp', 'tun')):
                if s.bytes_sent > 0 or s.bytes_recv > 0:
                    return iface, s
        
        if stats:
            first = list(stats.items())[0]
            return first[0], first[1]
        
        EmptyStats = namedtuple('EmptyStats', 
            ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv',
             'errin', 'errout', 'dropin', 'dropout'])
        return "none", EmptyStats(0, 0, 0, 0, 0, 0, 0, 0)
    
    @staticmethod
    def safe_net_speed(current: Any, previous: Optional[Any]) -> Tuple[float, float]:
        """
        Calcula velocidad de red de forma segura
        
        Args:
            current: Estadísticas actuales
            previous: Estadísticas anteriores
            
        Returns:
            Tupla (download_mb, upload_mb)
        """
        if previous is None:
            return 0.0, 0.0
        
        try:
            dl_bytes = max(0, current.bytes_recv - previous.bytes_recv)
            ul_bytes = max(0, current.bytes_sent - previous.bytes_sent)
            
            seconds = UPDATE_MS / 1000.0
            
            dl_mb = (dl_bytes / (1024 * 1024)) / seconds
            ul_mb = (ul_bytes / (1024 * 1024)) / seconds
            
            return dl_mb, ul_mb
        except (AttributeError, TypeError) as e:
            logger.warning(f"[SystemUtils] safe_net_speed: error calculando velocidad de red: {e}")
            return 0.0, 0.0
    
    @staticmethod
    def list_usb_storage_devices() -> list:
        """
        Lista dispositivos USB de almacenamiento (discos)
        
        Returns:
            Lista de diccionarios con información de almacenamiento USB
        """
        storage_devices = []
        
        try:
            result = subprocess.run(
                ['lsblk', '-o', 'NAME,MODEL,TRAN,MOUNTPOINT,SIZE,TYPE', '-J'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                for block in data.get('blockdevices', []):
                    if block.get('tran') == 'usb':
                        dev = {
                            'name': block.get('model', 'USB Disk').strip(),
                            'type': block.get('type', 'disk'),
                            'mount': block.get('mountpoint'),
                            'dev': '/dev/' + block.get('name', ''),
                            'size': block.get('size', ''),
                            'children': []
                        }
                        
                        for child in block.get('children', []):
                            child_dev = {
                                'name': child.get('name', ''),
                                'type': child.get('type', 'part'),
                                'mount': child.get('mountpoint'),
                                'dev': '/dev/' + child.get('name', ''),
                                'size': child.get('size', '')
                            }
                            dev['children'].append(child_dev)
                        
                        storage_devices.append(dev)
            else:
                logger.warning(f"[SystemUtils] list_usb_storage_devices: lsblk retornó código {result.returncode}")
        
        except subprocess.TimeoutExpired:
            logger.error("[SystemUtils] list_usb_storage_devices: timeout ejecutando lsblk")
        except FileNotFoundError:
            logger.error("[SystemUtils] list_usb_storage_devices: lsblk no encontrado")
        except json.JSONDecodeError as e:
            logger.error(f"[SystemUtils] list_usb_storage_devices: error parseando JSON de lsblk: {e}")
        
        return storage_devices
    
    @staticmethod
    def list_usb_other_devices() -> list:
        """
        Lista otros dispositivos USB (no almacenamiento)
        
        Returns:
            Lista de strings con información de dispositivos USB
        """
        try:
            result = subprocess.run(
                ['lsusb'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                devices = [line for line in result.stdout.strip().split('\n') if line]
                return devices
            else:
                logger.warning(f"[SystemUtils] list_usb_other_devices: lsusb retornó código {result.returncode}")
            
        except subprocess.TimeoutExpired:
            logger.error("[SystemUtils] list_usb_other_devices: timeout ejecutando lsusb")
        except FileNotFoundError:
            logger.error("[SystemUtils] list_usb_other_devices: lsusb no encontrado")
        
        return []
    
    @staticmethod
    def list_usb_devices() -> list:
        """
        Lista TODOS los dispositivos USB (mantener para compatibilidad)
        
        Returns:
            Lista de strings con lsusb
        """
        return SystemUtils.list_usb_other_devices()
    
    @staticmethod
    def eject_usb_device(device: dict) -> Tuple[bool, str]:
        """
        Expulsa un dispositivo USB de forma segura
        
        Args:
            device: Diccionario con información del dispositivo
                   (debe tener 'children' con particiones)
        
        Returns:
            Tupla (success: bool, message: str)
        """
        device_name = device.get('name', 'desconocido')
        
        try:
            unmounted = []
            for partition in device.get('children', []):
                if partition.get('mount'):
                    result = subprocess.run(
                        ['udisksctl', 'unmount', '-b', partition['dev']],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        unmounted.append(partition['name'])
                        logger.info(f"[SystemUtils] Partición {partition['name']} desmontada correctamente")
                    else:
                        logger.error(f"[SystemUtils] Error desmontando {partition['name']}: {result.stderr}")
                        return (False, f"Error desmontando {partition['name']}: {result.stderr}")
            
            if unmounted:
                logger.info(f"[SystemUtils] Dispositivo '{device_name}' expulsado: {', '.join(unmounted)}")
                return (True, f"Desmontado correctamente: {', '.join(unmounted)}")
            else:
                logger.info(f"[SystemUtils] Dispositivo '{device_name}': no había particiones montadas")
                return (True, "No había particiones montadas")
        
        except subprocess.TimeoutExpired:
            logger.error(f"[SystemUtils] eject_usb_device: timeout desmontando '{device_name}'")
            return (False, "Timeout al desmontar el dispositivo")
        except FileNotFoundError:
            logger.error("[SystemUtils] eject_usb_device: udisksctl no encontrado")
            return (False, "udisksctl no encontrado. Instala: sudo apt-get install udisks2")
        except Exception as e:
            logger.error(f"[SystemUtils] eject_usb_device: error inesperado con '{device_name}': {e}")
            return (False, f"Error: {str(e)}")
    
    @staticmethod
    def run_script(script_path: str) -> Tuple[bool, str]:
        """
        Ejecuta un script de sistema
        
        Args:
            script_path: Ruta al script
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            result = subprocess.run(
                ["bash", script_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"[SystemUtils] Script ejecutado correctamente: {script_path}")
                return True, "Script ejecutado exitosamente"
            else:
                logger.error(f"[SystemUtils] Script falló ({script_path}): {result.stderr}")
                return False, f"Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            logger.error(f"[SystemUtils] run_script: timeout ejecutando {script_path}")
            return False, "Timeout: El script tardó demasiado"
        except FileNotFoundError:
            logger.error(f"[SystemUtils] run_script: script no encontrado: {script_path}")
            return False, f"Script no encontrado: {script_path}"
        except Exception as e:
            logger.error(f"[SystemUtils] run_script: error inesperado ({script_path}): {e}")
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def get_interfaces_ips() -> Dict[str, str]:
        """
        Obtiene las IPs de todas las interfaces de red
        
        Returns:
            Diccionario {interfaz: IP}
        """
        result = {}
        try:
            addrs = psutil.net_if_addrs()
            for iface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family == socket.AF_INET:
                        result[iface] = addr.address
                        break
        except Exception as e:
            logger.warning(f"[SystemUtils] get_interfaces_ips: {e}")
        
        return result
    
    @staticmethod
    def get_nvme_temp() -> float:
        """
        Obtiene la temperatura del disco NVMe
        
        Returns:
            Temperatura en °C o 0.0 si no se puede leer
        """
        # Método 1: smartctl
        try:
            result = subprocess.run(
                ["sudo", "smartctl", "-a", "/dev/nvme0"],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Temperature:' in line or 'Temperature Sensor' in line:
                        match = re.search(r'(\d+)\s*Celsius', line)
                        if match:
                            return float(match.group(1))
            else:
                logger.debug(f"[SystemUtils] get_nvme_temp: smartctl retornó código {result.returncode}")
        except subprocess.TimeoutExpired:
            logger.warning("[SystemUtils] get_nvme_temp: timeout ejecutando smartctl")
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # Método 2: sysfs
        try:
            temp_files = [
                "/sys/class/hwmon/hwmon*/temp1_input",
                "/sys/block/nvme0n1/device/hwmon/hwmon*/temp1_input"
            ]
            
            for pattern in temp_files:
                for temp_file in glob.glob(pattern):
                    with open(temp_file, 'r') as f:
                        temp_millis = int(f.read().strip())
                        return temp_millis / 1000.0
        except FileNotFoundError:
            logger.debug("[SystemUtils] get_nvme_temp: archivos sysfs no encontrados")
        except ValueError as e:
            logger.warning(f"[SystemUtils] get_nvme_temp: error leyendo sysfs: {e}")
        except PermissionError:
            logger.warning("[SystemUtils] get_nvme_temp: sin permisos para leer sysfs")
        
        return 0.0
````

## File: requirements.txt
````
# ============================================
# System Dashboard - Python Dependencies
# ============================================
#
# Instalación rápida (recomendada):
#   sudo ./install_system.sh
#
# O manualmente:
#   pip3 install --break-system-packages -r requirements.txt
#
# Versión mínima de Python: 3.8+
# ============================================

# === Dependencias Obligatorias ===

# Interfaz gráfica moderna con tema oscuro
customtkinter>=5.2.0

# Monitor del sistema (CPU, RAM, Disco, Red, Procesos)
psutil>=5.9.0

# Gráficas históricas (ventana Histórico Datos)
matplotlib>=3.5.0

# Variables de entorno desde .env (credenciales Homebridge)
python-dotenv>=1.0.0


# ============================================
# NOTA: Dependencias del Sistema (NO Python)
# ============================================
#
# El script install_system.sh las instala automáticamente.
# O manualmente con apt-get:
#
#   sudo apt-get install lm-sensors usbutils udisks2 smartmontools
#
# Descripción:
#   - lm-sensors:     Lectura de temperatura CPU (sensors)
#   - usbutils:       Comando lsusb (listar USB)
#   - udisks2:        Expulsar dispositivos USB de forma segura
#   - util-linux:     Comando lsblk (suele venir instalado)
#   - smartmontools:  Temperatura NVMe (smartctl)
#
# Opcional para speedtest (CLI oficial de Ookla, NO speedtest-cli de pip):
#   curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
#   sudo apt-get install speedtest
#
# ============================================
````

## File: core/data_logger.py
````python
"""
Sistema de logging de datos históricos
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict
from utils import DashboardLogger


class DataLogger:
    """Registra datos del sistema en base de datos SQLite"""

    def __init__(self, db_path: str = "data/history.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_database()
        self.dashboard_logger = DashboardLogger()
        self.check_and_rotate_db(max_mb=5.0)

    def _init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                cpu_percent REAL,
                ram_percent REAL,
                ram_used_gb REAL,
                temperature REAL,
                disk_used_percent REAL,
                disk_read_mb REAL,
                disk_write_mb REAL,
                net_download_mb REAL,
                net_upload_mb REAL,
                fan_pwm INTEGER,
                fan_mode TEXT,
                updates_available INTEGER
            )
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON metrics(timestamp)
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                event_type TEXT,
                severity TEXT,
                message TEXT,
                data JSON
            )
        ''')

        conn.commit()
        conn.close()

    def log_metrics(self, metrics: Dict):
        """
        Guarda un conjunto de métricas.
        La timestamp se genera con datetime.now() para usar la hora local del sistema,
        evitando el desfase UTC que produce DEFAULT CURRENT_TIMESTAMP de SQLite.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Hora local explícita — SQLite CURRENT_TIMESTAMP siempre es UTC
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO metrics (
                timestamp,
                cpu_percent, ram_percent, ram_used_gb, temperature,
                disk_used_percent, disk_read_mb, disk_write_mb,
                net_download_mb, net_upload_mb, fan_pwm, fan_mode, updates_available
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            now,
            metrics.get('cpu_percent'),
            metrics.get('ram_percent'),
            metrics.get('ram_used_gb'),
            metrics.get('temperature'),
            metrics.get('disk_used_percent'),
            metrics.get('disk_read_mb'),
            metrics.get('disk_write_mb'),
            metrics.get('net_download_mb'),
            metrics.get('net_upload_mb'),
            metrics.get('fan_pwm'),
            metrics.get('fan_mode'),
            metrics.get('updates_available'),
        ))

        conn.commit()
        conn.close()

    def log_event(self, event_type: str, severity: str, message: str, data: Dict = None):
        """Registra un evento con hora local."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO events (timestamp, event_type, severity, message, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (now, event_type, severity, message, json.dumps(data) if data else None))

        conn.commit()
        conn.close()

    def get_metrics_count(self) -> int:
        """Obtiene el número total de registros"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM metrics')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_db_size_mb(self) -> float:
        """Obtiene el tamaño de la base de datos en MB"""
        db_file = Path(self.db_path)
        if db_file.exists():
            return db_file.stat().st_size / (1024 * 1024)
        return 0.0

    def clean_old_data(self, days: int = 7):
        """Elimina datos más antiguos de X días"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('DELETE FROM metrics WHERE timestamp < ?', (cutoff,))
        cursor.execute('DELETE FROM events  WHERE timestamp < ?', (cutoff,))

        conn.commit()
        cursor.execute('VACUUM')
        conn.close()

    def check_and_rotate_db(self, max_mb: float = 5.0):
        """Si la DB supera el tamaño máximo, elimina datos antiguos"""
        log = self.dashboard_logger.get_logger(__name__)
        log.info(f"[DataLogger] Verificando tamaño BD... {self.get_db_size_mb():.2f} MB")
        if self.get_db_size_mb() > max_mb:
            log.warning(f"[DataLogger] BD supera {max_mb} MB. Limpiando...")
            self.clean_old_data(days=7)
            log.info(f"[DataLogger] Limpieza completada. Nuevo tamaño: {self.get_db_size_mb():.2f} MB")
````

## File: core/fan_auto_service.py
````python
"""
Servicio en segundo plano para modo AUTO de ventiladores
"""
import threading
import time
from typing import Optional
from core.fan_controller import FanController
from core.system_monitor import SystemMonitor
from utils import FileManager
from utils.logger import get_logger


logger = get_logger(__name__)


class FanAutoService:
    """
    Servicio que actualiza automáticamente el PWM en modo AUTO
    Se ejecuta en segundo plano independiente de la UI
    
    Características:
    - Singleton: Solo una instancia en toda la aplicación
    - Thread-safe: Seguro para concurrencia
    - Daemon: Se cierra automáticamente con el programa
    - Independiente de UI: Funciona con o sin ventanas abiertas
    """
    
    _instance: Optional['FanAutoService'] = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton: solo una instancia"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, fan_controller: FanController, 
                 system_monitor: SystemMonitor):
        """
        Inicializa el servicio (solo la primera vez)
        
        Args:
            fan_controller: Instancia del controlador de ventiladores
            system_monitor: Instancia del monitor del sistema
        """
        # Solo inicializar una vez (patrón singleton)
        if hasattr(self, '_initialized'):
            return
        
        self.fan_controller = fan_controller
        self.system_monitor = system_monitor
        self.file_manager = FileManager()
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._update_interval = 2.0  # segundos
        self._initialized = True
        self.start_cycle = True
    def start(self):
        """Inicia el servicio en segundo plano"""
        if self._running:
            logger.info("[FanAutoService] ya está corriendo")
            return
        
        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,  # Se cierra con el programa
            name="FanAutoService"
        )
        self._thread.start()
        logger.info("[FanAutoService] Servicio iniciado")
    
    def stop(self):
        """Detiene el servicio"""
        if not self._running:
            logger.warning("[FanAutoService] no está corriendo")
            return
        
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("[FanAutoService] Servicio detenido")

    
    def _run(self):
        """Bucle principal del servicio (ejecuta en thread separado)"""
        while self._running:
            try:
                self._update_auto_mode()
            except Exception as e:
                logger.error(f"[FanAutoService] Error en actualización automática: {e}")
            
            # Dormir en intervalos pequeños para poder detener rápido
            for _ in range(int(self._update_interval * 10)):
                if not self._running:
                    break
                time.sleep(0.1)
    
    def _update_auto_mode(self):
        """Actualiza el PWM si está en modo auto"""
        
        try:
            state = self.file_manager.load_state()
        except Exception as e:
            logger.error(f"[FanAutoService] Error cargando estado: {e}")
            return
        
        # Solo actuar si está en modo auto
        if state.get("mode") != "auto":
            
            if self.start_cycle:
                logger.info("[FanAutoService] Modo no es auto, esperando para iniciar actualizaciones automáticas...")
                self.start_cycle = False
            return
        
        try:
            # Obtener temperatura actual
            stats = self.system_monitor.get_current_stats()
            temp = stats.get('temp', 50)
            
            # Calcular PWM según curva
            target_pwm = self.fan_controller.get_pwm_for_mode(
                mode="auto",
                temp=temp,
                manual_pwm=128  # No importa en auto
            )
            
            # Solo guardar si cambió (evitar writes innecesarios)
            current_pwm = state.get("target_pwm")
            if target_pwm != current_pwm:
                self.file_manager.write_state({
                    "mode": "auto",
                    "target_pwm": target_pwm
                })
        
        except Exception as e:
            logger.error(f"[FanAutoService] Error calculando o guardando PWM: {e}")
    
    def set_update_interval(self, seconds: float):
        """
        Cambia el intervalo de actualización
        
        Args:
            seconds: Segundos entre actualizaciones (mínimo 1.0)
        """
        self._update_interval = max(1.0, seconds)
    
    def is_running(self) -> bool:
        """
        Verifica si el servicio está corriendo
        
        Returns:
            True si está activo, False si no
        """
        logger.debug(f"[FanAutoService] is_running: {self._running}")
        return self._running
    
    def get_status(self) -> dict:
        """
        Obtiene el estado del servicio
        
        Returns:
            Diccionario con información del servicio
        """
        return {
            'running': self._running,
            'interval': self._update_interval,
            'thread_alive': self._thread.is_alive() if self._thread else False
        }
````

## File: core/network_monitor.py
````python
"""
Monitor de red
"""
import json
import threading
import subprocess
from collections import deque
from typing import Dict, Optional
from config.settings import (HISTORY, NET_MIN_SCALE, NET_MAX_SCALE, 
                             NET_IDLE_THRESHOLD, NET_IDLE_RESET_TIME, NET_MAX_MB, COLORS, NET_WARN, NET_CRIT)
from utils.system_utils import SystemUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class NetworkMonitor:
    """Monitor de red con gestión de estadísticas y speedtest"""
    
    def __init__(self):
        self.system_utils = SystemUtils()
        
        # Historiales
        self.download_hist = deque(maxlen=HISTORY)
        self.upload_hist = deque(maxlen=HISTORY)
        
        # Estado
        self.last_net_io = {}
        self.last_used_iface = None
        self.dynamic_max = NET_MAX_MB
        self.idle_counter = 0
        
        # Speedtest
        self.speedtest_result = {
            "status": "idle",
            "ping": 0,
            "download": 0.0,
            "upload": 0.0
        }
    
    def get_current_stats(self, interface: Optional[str] = None) -> Dict:
        """
        Obtiene estadísticas actuales de red
        
        Args:
            interface: Interfaz de red específica o None para auto-detección
            
        Returns:
            Diccionario con estadísticas de red
        """
        iface, stats = self.system_utils.get_net_io(interface)
        
        prev = self.last_net_io.get(iface)
        dl, ul = self.system_utils.safe_net_speed(stats, prev)
        
        self.last_net_io[iface] = stats
        self.last_used_iface = iface
        
        return {
            'interface': iface,
            'download_mb': dl,
            'upload_mb': ul
        }
    
    def update_history(self, stats: Dict) -> None:
        """
        Actualiza historiales de red
        
        Args:
            stats: Estadísticas actuales
        """
        self.download_hist.append(stats['download_mb'])
        self.upload_hist.append(stats['upload_mb'])
    
    def adaptive_scale(self, current_max: float, recent_data: list) -> float:
        """
        Ajusta dinámicamente la escala del gráfico
        
        Args:
            current_max: Máximo actual
            recent_data: Datos recientes
            
        Returns:
            Nuevo máximo escalado
        """
        if not recent_data:
            return current_max
        
        peak = max(recent_data) if recent_data else 0
        
        if peak < NET_IDLE_THRESHOLD:
            self.idle_counter += 1
            if self.idle_counter >= NET_IDLE_RESET_TIME:
                self.idle_counter = 0
                return NET_MAX_MB
        else:
            self.idle_counter = 0
        
        if peak > current_max * 0.8:
            new_max = peak * 1.2
        elif peak < current_max * 0.3:
            new_max = max(peak * 1.5, NET_MIN_SCALE)
        else:
            new_max = current_max
        
        return max(NET_MIN_SCALE, min(NET_MAX_SCALE, new_max))
    
    def update_dynamic_scale(self) -> None:
        """Actualiza la escala dinámica basada en el historial"""
        all_data = list(self.download_hist) + list(self.upload_hist)
        self.dynamic_max = self.adaptive_scale(self.dynamic_max, all_data)
    
    def get_history(self) -> Dict:
        """
        Obtiene historiales de red
        
        Returns:
            Diccionario con historiales
        """
        return {
            'download': list(self.download_hist),
            'upload': list(self.upload_hist),
            'dynamic_max': self.dynamic_max
        }
    
    def run_speedtest(self) -> None:
        """Ejecuta speedtest (Ookla CLI) en un thread separado"""
        def _run():
            logger.info("[NetworkMonitor] Iniciando speedtest...")
            self.speedtest_result["status"] = "running"
            try:
                result = subprocess.run(
                    ["speedtest", "--format=json", "--accept-license", "--accept-gdpr"],
                    capture_output=True,
                    text=True,
                    timeout=90
                )

                if result.returncode == 0:
                    data = json.loads(result.stdout)

                    # El nuevo CLI devuelve bytes/s → convertir a MB/s
                    ping     = data["ping"]["latency"]
                    download = data["download"]["bandwidth"] / 1_000_000
                    upload   = data["upload"]["bandwidth"]   / 1_000_000

                    self.speedtest_result.update({
                        "status":   "done",
                        "ping":     round(ping, 1),
                        "download": round(download, 2),
                        "upload":   round(upload, 2),
                    })
                    logger.info(
                        f"[NetworkMonitor] Speedtest completado — "
                        f"Ping: {ping:.1f}ms, ↓{download:.2f} MB/s, ↑{upload:.2f} MB/s"
                    )
                else:
                    logger.error(
                        f"[NetworkMonitor] speedtest retornó código {result.returncode}: {result.stderr}"
                    )
                    self.speedtest_result["status"] = "error"

            except subprocess.TimeoutExpired:
                logger.warning("[NetworkMonitor] Speedtest timeout (>90s)")
                self.speedtest_result["status"] = "timeout"
            except FileNotFoundError:
                logger.error(
                    "[NetworkMonitor] speedtest no encontrado. "
                    "Instala el CLI oficial de Ookla: https://www.speedtest.net/apps/cli"
                )
                self.speedtest_result["status"] = "error"
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"[NetworkMonitor] Error parseando resultado de speedtest: {e}")
                self.speedtest_result["status"] = "error"
            except Exception as e:
                logger.error(f"[NetworkMonitor] Error inesperado en speedtest: {e}")
                self.speedtest_result["status"] = "error"

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
    
    def get_speedtest_result(self) -> Dict:
        """
        Obtiene el resultado del speedtest
        
        Returns:
            Diccionario con resultados
        """
        return self.speedtest_result.copy()
    
    def reset_speedtest(self) -> None:
        """Resetea el estado del speedtest"""
        self.speedtest_result = {
            "status": "idle",
            "ping": 0,
            "download": 0.0,
            "upload": 0.0
        }
    
    @staticmethod
    def net_color(value: float) -> str:
        """
        Determina el color según el tráfico de red
        
        Args:
            value: Velocidad en MB/s
            
        Returns:
            Color en formato hex
        """
        if value >= NET_CRIT:
            return COLORS['danger']
        elif value >= NET_WARN:
            return COLORS['warning']
        else:
            return COLORS['primary']
````

## File: ui/widgets/dialogs.py
````python
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
````

## File: ui/windows/disk.py
````python
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


class DiskWindow(ctk.CTkToplevel):
    """Ventana de monitoreo de disco"""

    def __init__(self, parent, disk_monitor: DiskMonitor):
        super().__init__(parent)
        self.disk_monitor = disk_monitor
        self.widgets = {}
        self.graphs  = {}

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

        # Grid 2 columnas dentro del inner scrollable
        grid = ctk.CTkFrame(inner, fg_color=COLORS['bg_medium'])
        grid.pack(fill="x")
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        self._create_cell(grid, 0, 0, "DISCO %",  "disk",       "%",    _GRAPH_H)
        self._create_cell(grid, 0, 1, "NVMe °C",  "nvme_temp",  "°C",   _GRAPH_H)
        self._create_cell(grid, 1, 0, "ESCRITURA","disk_write", "MB/s", _GRAPH_H)
        self._create_cell(grid, 1, 1, "LECTURA",  "disk_read",  "MB/s", _GRAPH_H)

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

        stats   = self.disk_monitor.get_current_stats()
        self.disk_monitor.update_history(stats)
        history = self.disk_monitor.get_history()

        self._update_metric('disk',      stats['disk_usage'],   history['disk_usage'], "%",   60, 80)
        self._update_metric('nvme_temp', stats['nvme_temp'],    history['nvme_temp'],  "°C",  60, 70)
        self._update_io('disk_write',    stats['disk_write_mb'], history['disk_write'])
        self._update_io('disk_read',     stats['disk_read_mb'],  history['disk_read'])

        self._header.status_label.configure(
            text=f"Uso {stats['disk_usage']:.0f}%  ·  NVMe {stats['nvme_temp']:.0f}°C")

        self.after(UPDATE_MS, self._update)

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
````

## File: ui/windows/log_viewer.py
````python
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
````

## File: config/settings.py
````python
"""
Configuración centralizada del sistema de monitoreo
"""
from pathlib import Path
from config.themes import load_selected_theme, get_theme_colors
# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Subdirectorios de exportación
EXPORTS_DIR      = DATA_DIR / "exports"
EXPORTS_CSV_DIR  = EXPORTS_DIR / "csv"
EXPORTS_LOG_DIR  = EXPORTS_DIR / "logs"
EXPORTS_SCR_DIR  = EXPORTS_DIR / "screenshots"

# Asegurar que los directorios existan
DATA_DIR.mkdir(exist_ok=True)
SCRIPTS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
EXPORTS_CSV_DIR.mkdir(exist_ok=True)
EXPORTS_LOG_DIR.mkdir(exist_ok=True)
EXPORTS_SCR_DIR.mkdir(exist_ok=True)

# Archivos de estado
STATE_FILE = DATA_DIR / "fan_state.json"
CURVE_FILE = DATA_DIR / "fan_curve.json"

# Configuración de pantalla DSI
DSI_WIDTH = 800
DSI_HEIGHT = 480
DSI_X = 1124
DSI_Y = 1080

# Configuración de actualización
UPDATE_MS = 2000
HISTORY = 60
GRAPH_WIDTH = 800
GRAPH_HEIGHT = 20

# Umbrales de advertencia y críticos
CPU_WARN = 60
CPU_CRIT = 85
TEMP_WARN = 60
TEMP_CRIT = 75
RAM_WARN = 65
RAM_CRIT = 85

# Configuración de red
NET_WARN = 2.0  # MB/s
NET_CRIT = 6.0
NET_INTERFACE = None  # None = auto | "eth0" | "wlan0"
NET_MAX_MB = 10.0
NET_MIN_SCALE = 0.5
NET_MAX_SCALE = 200.0
NET_IDLE_THRESHOLD = 0.2
NET_IDLE_RESET_TIME = 15  # segundos

# Lanzadores de scripts
LAUNCHERS = [
    {
        "label": "󰣳 󰌘 Montar NAS",
        "script": str(SCRIPTS_DIR / "montarnas.sh")
    },
    {
        "label": "󰣳 󰌙 Desmontar NAS",
        "script": str(SCRIPTS_DIR / "desmontarnas.sh")
    },
    {
        "label": "󰚰  Update System",
        "script": str(SCRIPTS_DIR / "update.sh")
    },
    {
        "label": "󰌘  Conectar VPN",
        "script": str(SCRIPTS_DIR / "conectar_vpn.sh")
    },
    {
        "label": "󰌙  Desconectar VPN",
        "script": str(SCRIPTS_DIR / "desconectar_vpn.sh")
    },
    {
        "label": "󱓞  Iniciar fase1",
        "script": str(SCRIPTS_DIR / "fase1.sh")
    },
    {
        "label": "󰅙  Shutdown",
        "script": str(SCRIPTS_DIR / "apagado.sh")
    }
]

# ========================================
# SISTEMA DE TEMAS
# ========================================

# Importar sistema de temas


# Cargar tema seleccionado
SELECTED_THEME = load_selected_theme()

# Obtener colores del tema
COLORS = get_theme_colors(SELECTED_THEME)

# Fuente
FONT_FAMILY = "FiraMono Nerd Font"
FONT_SIZES = {
    "small": 14,
    "medium": 18,
    "large": 20,
    "xlarge": 24,
    "xxlarge": 30
}
````

## File: ui/windows/network.py
````python
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
````

## File: core/data_analyzer.py
````python
"""
Análisis de datos históricos
"""
import sqlite3
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from config.settings import DATA_DIR
from utils.logger import get_logger

logger = get_logger(__name__)

_FMT = "%Y-%m-%d %H:%M:%S"


def _fmt(dt: datetime) -> str:
    """Convierte datetime a string sin microsegundos, formato que usa la BD."""
    return dt.strftime(_FMT)


class DataAnalyzer:
    """Analiza datos históricos de la base de datos"""

    def __init__(self, db_path: str = f"{DATA_DIR}/history.db"):
        self.db_path = db_path

    # ─────────────────────────────────────────────
    # Métodos basados en horas
    # ─────────────────────────────────────────────

    def get_data_range(self, hours: int = 24) -> List[Dict]:
        """Obtiene datos de las últimas X horas"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cutoff = _fmt(datetime.now() - timedelta(hours=hours))

            cursor.execute('''
                SELECT * FROM metrics
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
            ''', (cutoff,))

            rows = cursor.fetchall()
            conn.close()

            logger.debug(f"[DataAnalyzer] get_data_range: {len(rows)} registros (últimas {hours}h)")
            return [dict(row) for row in rows]

        except sqlite3.OperationalError as e:
            logger.error(f"[DataAnalyzer] get_data_range: error BD: {e}")
            return []
        except Exception as e:
            logger.error(f"[DataAnalyzer] get_data_range: error inesperado: {e}")
            return []

    def get_stats(self, hours: int = 24) -> Dict:
        """Obtiene estadísticas de las últimas X horas"""
        now = datetime.now()
        start = now - timedelta(hours=hours)
        return self._get_stats_between(start, now)

    def get_graph_data(self, metric: str, hours: int = 24) -> Tuple[List, List]:
        """Obtiene datos para gráficas (últimas X horas)"""
        try:
            data = self.get_data_range(hours)
            return self._extract_metric(data, metric)
        except Exception as e:
            logger.error(f"[DataAnalyzer] get_graph_data '{metric}': {e}")
            return [], []

    def export_to_csv(self, output_path: str, hours: int = 24):
        """Exporta datos a CSV (últimas X horas)"""
        data = self.get_data_range(hours)
        self._write_csv(output_path, data)

    # ─────────────────────────────────────────────
    # Métodos basados en rango personalizado
    # ─────────────────────────────────────────────

    def get_data_range_between(self, start: datetime, end: datetime) -> List[Dict]:
        """Obtiene datos entre dos fechas exactas"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM metrics
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp ASC
            ''', (_fmt(start), _fmt(end)))

            rows = cursor.fetchall()
            conn.close()

            logger.debug(
                f"[DataAnalyzer] get_data_range_between: {len(rows)} registros "
                f"({_fmt(start)} → {_fmt(end)})"
            )
            return [dict(row) for row in rows]

        except sqlite3.OperationalError as e:
            logger.error(f"[DataAnalyzer] get_data_range_between: error BD: {e}")
            return []
        except Exception as e:
            logger.error(f"[DataAnalyzer] get_data_range_between: error inesperado: {e}")
            return []

    def get_stats_between(self, start: datetime, end: datetime) -> Dict:
        """Obtiene estadísticas entre dos fechas exactas"""
        return self._get_stats_between(start, end)

    def get_graph_data_between(self, metric: str, start: datetime, end: datetime) -> Tuple[List, List]:
        """Obtiene datos para gráficas entre dos fechas exactas"""
        try:
            data = self.get_data_range_between(start, end)
            return self._extract_metric(data, metric)
        except Exception as e:
            logger.error(f"[DataAnalyzer] get_graph_data_between '{metric}': {e}")
            return [], []

    def export_to_csv_between(self, output_path: str, start: datetime, end: datetime):
        """Exporta datos a CSV entre dos fechas exactas"""
        data = self.get_data_range_between(start, end)
        self._write_csv(output_path, data)

    # ─────────────────────────────────────────────
    # Detección de anomalías
    # ─────────────────────────────────────────────

    def detect_anomalies(self, hours: int = 24) -> List[Dict]:
        """Detecta anomalías en los datos"""
        anomalies = []
        stats = self.get_stats(hours)

        if not stats:
            return anomalies

        if stats.get('cpu_avg', 0) > 80:
            anomalies.append({'type': 'cpu_high', 'severity': 'warning',
                               'message': f"CPU promedio alta: {stats['cpu_avg']:.1f}%"})
            logger.warning(f"[DataAnalyzer] CPU promedio {stats['cpu_avg']:.1f}%")

        if stats.get('temp_max', 0) > 80:
            anomalies.append({'type': 'temp_high', 'severity': 'critical',
                               'message': f"Temperatura máxima: {stats['temp_max']:.1f}°C"})
            logger.warning(f"[DataAnalyzer] Temperatura máxima {stats['temp_max']:.1f}°C")

        if stats.get('ram_avg', 0) > 85:
            anomalies.append({'type': 'ram_high', 'severity': 'warning',
                               'message': f"RAM promedio alta: {stats['ram_avg']:.1f}%"})
            logger.warning(f"[DataAnalyzer] RAM promedio {stats['ram_avg']:.1f}%")

        return anomalies

    # ─────────────────────────────────────────────
    # Métodos privados
    # ─────────────────────────────────────────────

    def _get_stats_between(self, start: datetime, end: datetime) -> Dict:
        """Lógica común de estadísticas para cualquier rango start→end."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    AVG(cpu_percent), MAX(cpu_percent), MIN(cpu_percent),
                    AVG(ram_percent), MAX(ram_percent), MIN(ram_percent),
                    AVG(temperature), MAX(temperature), MIN(temperature),
                    AVG(net_download_mb), MAX(net_download_mb), MIN(net_download_mb),
                    AVG(net_upload_mb), MAX(net_upload_mb), MIN(net_upload_mb),
                    AVG(disk_read_mb), MAX(disk_read_mb), MIN(disk_read_mb),
                    AVG(disk_write_mb), MAX(disk_write_mb), MIN(disk_write_mb),
                    AVG(fan_pwm), MAX(fan_pwm), MIN(fan_pwm),
                    MAX(updates_available), MIN(updates_available), AVG(updates_available),
                    COUNT(*)
                FROM metrics
                WHERE timestamp >= ? AND timestamp <= ?
            ''', (_fmt(start), _fmt(end)))

            row = cursor.fetchone()
            conn.close()

            if row and row[27]:
                logger.debug(f"[DataAnalyzer] _get_stats_between: {row[27]} muestras")
                return {
                    'cpu_avg':   round(row[0],  1) if row[0]  else 0,
                    'cpu_max':   round(row[1],  1) if row[1]  else 0,
                    'cpu_min':   round(row[2],  1) if row[2]  else 0,
                    'ram_avg':   round(row[3],  1) if row[3]  else 0,
                    'ram_max':   round(row[4],  1) if row[4]  else 0,
                    'ram_min':   round(row[5],  1) if row[5]  else 0,
                    'temp_avg':  round(row[6],  1) if row[6]  else 0,
                    'temp_max':  round(row[7],  1) if row[7]  else 0,
                    'temp_min':  round(row[8],  1) if row[8]  else 0,
                    'down_avg':  round(row[9],  2) if row[9]  else 0,
                    'down_max':  round(row[10], 2) if row[10] else 0,
                    'down_min':  round(row[11], 2) if row[11] else 0,
                    'up_avg':    round(row[12], 2) if row[12] else 0,
                    'up_max':    round(row[13], 2) if row[13] else 0,
                    'up_min':    round(row[14], 2) if row[14] else 0,
                    'disk_read_avg':   round(row[15], 2) if row[15] else 0,
                    'disk_read_max':   round(row[16], 2) if row[16] else 0,
                    'disk_read_min':   round(row[17], 2) if row[17] else 0,
                    'disk_write_avg':  round(row[18], 2) if row[18] else 0,
                    'disk_write_max':  round(row[19], 2) if row[19] else 0,
                    'disk_write_min':  round(row[20], 2) if row[20] else 0,
                    'pwm_avg':   round(row[21], 0) if row[21] else 0,
                    'pwm_max':   round(row[22], 0) if row[22] else 0,
                    'pwm_min':   round(row[23], 0) if row[23] else 0,
                    'updates_available_max': row[24] if row[24] else 0,
                    'updates_available_min': row[25] if row[25] else 0,
                    'updates_available_avg': row[26] if row[26] else 0,
                    'total_samples': row[27],
                }

            logger.debug("[DataAnalyzer] _get_stats_between: sin datos en el rango")
            return {}

        except sqlite3.OperationalError as e:
            logger.error(f"[DataAnalyzer] _get_stats_between: error BD: {e}")
            return {}
        except Exception as e:
            logger.error(f"[DataAnalyzer] _get_stats_between: error inesperado: {e}")
            return {}

    def _extract_metric(self, data: List[Dict], metric: str) -> Tuple[List, List]:
        """Extrae timestamps y valores de una métrica."""
        timestamps, values = [], []
        for entry in data:
            try:
                ts = datetime.strptime(entry['timestamp'], _FMT)
            except ValueError:
                # Por si algún registro antiguo tiene microsegundos
                ts = datetime.fromisoformat(entry['timestamp'])
            timestamps.append(ts)
            values.append(entry.get(metric) or 0)
        return timestamps, values

    def _write_csv(self, output_path: str, data: List[Dict]):
        """Escribe una lista de registros a CSV."""
        try:
            if not data:
                logger.warning("[DataAnalyzer] _write_csv: sin datos para exportar")
                return
            with open(output_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            logger.info(f"[DataAnalyzer] _write_csv: {len(data)} registros → {output_path}")
        except OSError as e:
            logger.error(f"[DataAnalyzer] _write_csv: error escribiendo {output_path}: {e}")
        except Exception as e:
            logger.error(f"[DataAnalyzer] _write_csv: error inesperado: {e}")
````

## File: core/data_collection_service.py
````python
"""
Servicio de recolección automática de datos
"""
import threading
import time
from datetime import datetime
from core.data_logger import DataLogger
from utils.file_manager import FileManager

from utils.logger import get_logger

logger = get_logger(__name__)


class DataCollectionService:
    """Servicio que recolecta métricas cada X minutos"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Implementa singleton thread-safe"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, system_monitor, fan_controller, network_monitor,
                 disk_monitor, update_monitor, interval_minutes: int = 5):
        # Evitar re-inicialización del singleton
        if hasattr(self, '_initialized'):
            return

        self.system_monitor = system_monitor
        self.fan_controller = FileManager()
        self.network_monitor = network_monitor
        self.disk_monitor = disk_monitor
        self.update_monitor = update_monitor
        self.interval_minutes = interval_minutes

        self.logger = DataLogger()
        self.running = False
        self.thread = None


        self._initialized = True

        # ELIMINADO: atexit.register(self.stop)
        # El registro del cleanup se hace en main.py junto con fan_service.stop()
        # para evitar que se dispare durante os.execv() en el reinicio

    def start(self):
        """Inicia el servicio de recolección"""
        if self.running:
            logger.info("[DataCollection] Servicio ya está corriendo")
            return

        self.running = True
        self.thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.thread.start()
        logger.info(f"[DataCollection] Servicio iniciado (cada {self.interval_minutes} min)")

    def stop(self):
        """Detiene el servicio"""
        if not self.running:
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("[DataCollection] Servicio detenido")

    def _collection_loop(self):
        """Bucle principal de recolección"""
        while self.running:
            try:
                self._collect_and_save()
            except Exception as e:
                logger.error(f"[DataCollection] Error en recolección: {e}")
            time.sleep(self.interval_minutes * 60)

    def _collect_and_save(self):
        """Recolecta métricas y las guarda"""
        system_stats = self.system_monitor.get_current_stats()
        network_stats = self.network_monitor.get_current_stats()
        disk_stats = self.disk_monitor.get_current_stats()
        update_stats = self.update_monitor.check_updates()
        fan_state = self.fan_controller.load_state()

        metrics = {
            'cpu_percent': system_stats.get('cpu', 0),
            'ram_percent': system_stats.get('ram', 0),
            'ram_used_gb': "{:.2f}".format(system_stats.get('ram_used', 0) / (1024 ** 3)),
            'temperature': system_stats.get('temp', 0),
            'disk_used_percent': disk_stats.get('disk_usage', 0),
            'disk_read_mb': "{:.2f}".format(disk_stats.get('disk_read_mb', 0)),
            'disk_write_mb': "{:.2f}".format(disk_stats.get('disk_write_mb', 0)),
            'net_download_mb': "{:.2f}".format(network_stats.get('download_mb', 0)),
            'net_upload_mb': "{:.2f}".format(network_stats.get('upload_mb', 0)),
            'fan_pwm': fan_state.get('target_pwm', 0),
            'fan_mode': fan_state.get('mode', 'unknown'),
            'updates_available': update_stats.get('pending', 0),
        }

        self.logger.log_metrics(metrics)

        if metrics['temperature'] > 80:
            self.logger.log_event(
                'temp_high', 'critical',
                f"Temperatura alta detectada: {metrics['temperature']:.1f}°C",
                {'temperature': metrics['temperature']}
            )

        if metrics['cpu_percent'] > 90:
            self.logger.log_event(
                'cpu_high', 'warning',
                f"CPU alta detectada: {metrics['cpu_percent']:.1f}%",
                {'cpu': metrics['cpu_percent']}
            )

        logger.info(f"[DataCollection] Métricas guardadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def force_collection(self):
        """Fuerza una recolección inmediata (útil para testing)"""
        self._collect_and_save()
````

## File: ui/windows/launchers.py
````python
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
````

## File: ui/styles.py
````python
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
````

## File: ui/windows/fan_control.py
````python
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
````

## File: QUICKSTART.md
````markdown
# 🚀 Inicio Rápido - Dashboard v3.1

---

## ⚡ Instalación (2 Comandos)

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

El script instala automáticamente las dependencias del sistema y Python, la CLI oficial de Ookla para speedtest, y pregunta si quieres configurar sensores de temperatura.

---

## 🔁 Alternativa con Entorno Virtual

Si prefieres aislar las dependencias:

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
```

> Recuerda activar el entorno (`source venv/bin/activate`) cada vez que quieras ejecutar el dashboard.

---

## 📋 Requisitos Mínimos

- ✅ Raspberry Pi 3/4/5
- ✅ Raspberry Pi OS (cualquier versión)
- ✅ Python 3.8+
- ✅ Conexión a internet (para instalación)

---

## 🎯 Menú Principal (15 botones)

```
┌───────────────────────────────────┐
│  Control        │  Monitor         │
│  Ventiladores   │  Placa           │
├─────────────────┼──────────────────┤
│  Monitor        │  Monitor         │
│  Red            │  USB             │
├─────────────────┼──────────────────┤
│  Monitor        │  Lanzadores      │
│  Disco          │                  │
├─────────────────┼──────────────────┤
│  Monitor        │  Monitor         │
│  Procesos       │  Servicios       │
├─────────────────┼──────────────────┤
│  Histórico      │  Actualizaciones │
│  Datos          │                  │
├─────────────────┼──────────────────┤
│  Homebridge     │  Visor de Logs   │
├─────────────────┼──────────────────┤
│  Cambiar Tema   │  Reiniciar       │
├─────────────────┼──────────────────┤
│  Salir          │                  │
└─────────────────┴──────────────────┘
```

---

## 🖥️ Las 15 Ventanas

**1. Monitor Placa** — CPU, RAM y temperatura en tiempo real (status en header)

**2. Monitor Red** — Download/Upload en vivo, speedtest Ookla, lista de IPs (status en header)

**3. Monitor USB** — Dispositivos conectados, expulsión segura

**4. Monitor Disco** — Espacio, temperatura NVMe, velocidad I/O (status en header)

**5. Monitor Procesos** — Top 20 procesos, búsqueda, matar procesos

**6. Monitor Servicios** — Start/Stop/Restart systemd, ver logs

**7. Histórico Datos** — 8 gráficas CPU/RAM/Temp/Red/Disco/PWM en 24h, 7d, 30d, exportar CSV

**8. Control Ventiladores** — Modo Auto/Manual/Silent/Normal/Performance, curvas PWM

**9. Lanzadores** — Scripts personalizados con terminal en vivo

**10. Actualizaciones** — Estado de paquetes, instalar con terminal integrada

**11. Homebridge** — Control de **5 tipos de dispositivos HomeKit**: switches/enchufes, luces con brillo, termostatos, sensores temperatura/humedad, persianas

**12. Visor de Logs** — Filtros por nivel, módulo, texto e intervalo de tiempo; exportación a `data/exports/logs/`

**13. Cambiar Tema** — 15 temas (Cyberpunk, Matrix, Dracula, Nord...)

**14. Reiniciar** — Reinicia el dashboard aplicando cambios de código

**15. Salir** — Salir de la app o apagar el sistema

> **Todas las ventanas** incluyen header unificado con título, status en tiempo real y botón ✕ táctil (52×42px) optimizado para pantalla DSI.

> **Exports organizados** en `data/exports/{csv,logs,screenshots}` — carpetas creadas automáticamente, máx. 10 archivos por tipo.

---

## 🔧 Configuración Básica

### Ajustar posición en pantalla DSI (`config/settings.py`):
```python
DSI_X = 0     # Posición horizontal
DSI_Y = 0     # Posición vertical
```

### Añadir scripts en Lanzadores:
```python
LAUNCHERS = [
    {"label": "Mi Script", "script": str(SCRIPTS_DIR / "mi_script.sh")},
]
```

---

## 🏠 Configurar Homebridge

Crea el archivo `.env` en la raíz del proyecto (cópialo desde `.env.example`):

```env
HOMEBRIDGE_HOST=192.168.1.X    # IP de la Pi con Homebridge
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña
```

> **Importante**: Activa el **Insecure Mode** en Homebridge (`homebridge-config-ui-x → Configuración → Homebridge`). Sin él, la API no permite acceder a los accesorios.

La ventana Homebridge muestra los accesorios en grid de 2 columnas con tarjetas adaptativas según el tipo:

- **Switch / Enchufe / Luz básica**: CTkSwitch táctil (90×46px)
- **Luz regulable**: switch ON/OFF con control de brillo
- **Termostato**: temperatura actual + botones +/− 0.5°C para temperatura objetivo
- **Sensor**: temperatura y/o humedad en modo solo lectura
- **Persiana / Estor**: posición actual (%) con barra visual

Si un dispositivo tiene `StatusFault=1` aparece ⚠ FALLO en rojo y el switch queda bloqueado.

---

## 📲 Configurar Alertas Telegram

Añade al mismo archivo `.env`:

```env
TELEGRAM_TOKEN=123456789:ABCdefGHI...   # Token del bot (@BotFather)
TELEGRAM_CHAT_ID=987654321              # ID del chat o canal destino
```

Las alertas se envían cuando temperatura, CPU, RAM o disco superan los umbrales durante 60 segundos sostenidos (anti-spam). También avisa si hay servicios en estado FAILED.

> Si no configuras estas variables, el dashboard funciona igual — las alertas simplemente no se envían.

---

## 📋 Ver Logs del Sistema

```bash
# En tiempo real
tail -f data/logs/dashboard.log

# Solo errores
grep ERROR data/logs/dashboard.log
```

---

## ❓ Problemas Comunes

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Speedtest falla | Instalar CLI Ookla: `sudo apt install speedtest` |
| USB no expulsa | `sudo apt install udisks2` |
| Homebridge no conecta | Revisar `.env` y activar Insecure Mode en Homebridge |
| Badge hb_offline siempre rojo | Comprobar conectividad entre Pis y `HOMEBRIDGE_HOST` |
| Servicios tardan en aparecer | Normal — ServiceMonitor sondea systemctl cada 10s al arrancar |
| No puedo escribir en los entries | Asegúrate de usar v3.0+ — el bug de `grab_set` está corregido |
| Alertas Telegram no llegan | Verificar `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` en `.env` |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 🆕 Novedades v3.1

✅ **Alertas Telegram** — `AlertService` con anti-spam (edge-trigger + sustain 60s), monitoriza temp/CPU/RAM/disco y servicios  
✅ **Homebridge extendido** — 5 tipos de dispositivo: switch, luz regulable, termostato, sensor, persiana  
✅ **UI diálogo salir** — radiobuttons táctiles 30×30px, botones ajustados, layout corregido  

### v3.0 (referencia)
✅ **Visor de Logs** — Filtros por nivel, módulo, texto e intervalo; exportación incluida  
✅ **Exports organizados** — `data/exports/{csv,logs,screenshots}` creadas automáticamente  
✅ **Limpieza al exportar** — CleanupService actúa también al guardar, no solo cada 24h  
✅ **Fix entries** — Eliminado `grab_set()` en FanControl que bloqueaba el teclado  

### v2.9 (referencia)
✅ **Switches táctiles Homebridge** — CTkSwitch de 90×46px, optimizado para el dedo en DSI  
✅ **Sin bloqueos en UI** — SystemMonitor y ServiceMonitor con caché en background thread  
✅ **ServiceMonitor optimizado** — is-enabled en llamada batch, sondeo cada 10s  
✅ **Logging completo** — Todos los servicios registran inicio y parada  

---

## 📚 Más Información

**[README.md](README.md)** — Documentación completa  
**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)** — Instalación detallada  
**[INDEX.md](INDEX.md)** — Índice de toda la documentación

---

**Dashboard v3.1** 🚀🏠📲✨
````

## File: ui/windows/__init__.py
````python
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
    
]
````

## File: INDEX.md
````markdown
# 📚 Índice de Documentación - System Dashboard v3.1

Guía completa de toda la documentación del proyecto actualizada.

---

## 🚀 Documentos Esenciales

### **Para Empezar:**
1. **[README.md](README.md)** ⭐  
   Documentación completa del proyecto v3.1. **Empieza aquí.**

2. **[QUICKSTART.md](QUICKSTART.md)** ⚡  
   Instalación y ejecución en 5 minutos.

---

## 📖 Guías por Tema

### 🎨 **Personalización**

**[THEMES_GUIDE.md](THEMES_GUIDE.md)**  
- Lista completa de 15 temas
- Cómo crear temas personalizados
- Paletas de colores de cada tema
- Cambiar tema desde código

---

### 🔧 **Instalación**

**[INSTALL_GUIDE.md](INSTALL_GUIDE.md)**  
- Instalación en Raspberry Pi OS
- Instalación en Kali Linux
- Instalación en otros Linux
- Solución de problemas comunes
- Métodos: venv, sin venv, script automático

---

### ⚙️ **Características Avanzadas**

**[PROCESS_MONITOR_GUIDE.md](PROCESS_MONITOR_GUIDE.md)**  
- Monitor de procesos completo
- Búsqueda y filtrado
- Terminación de procesos
- Personalización de columnas

**[SERVICE_MONITOR_GUIDE.md](SERVICE_MONITOR_GUIDE.md)**  
- Monitor de servicios systemd
- Start/Stop/Restart servicios
- Enable/Disable autostart
- Ver logs en tiempo real
- Implementación paso a paso

**[HISTORICO_DATOS_GUIDE.md](HISTORICO_DATOS_GUIDE.md)**  
- Sistema de histórico completo
- Base de datos SQLite
- Visualización con matplotlib
- Recolección automática
- Exportación CSV
- Implementación paso a paso

**[FAN_CONTROL_GUIDE.md](FAN_CONTROL_GUIDE.md)** (si existe)  
- Configuración de ventiladores PWM
- Crear curvas personalizadas
- Modos de operación
- Servicio background

**[NETWORK_GUIDE.md](NETWORK_GUIDE.md)** (si existe)  
- Monitor de tráfico de red
- Speedtest integrado (CLI oficial Ookla)
- Auto-detección de interfaz
- Lista de IPs

---

### 🏠 **Homebridge**

**Configuración rápida** — Ver sección en [QUICKSTART.md](QUICKSTART.md) y [README.md](README.md):
- Crear `.env` con IP, puerto, usuario y contraseña
- Activar Insecure Mode en Homebridge
- Verificar conectividad entre Pis

**5 tipos de dispositivo soportados**:
- `switch` — enchufe / interruptor (CTkSwitch táctil 90×46px)
- `light` — luz regulable (ON/OFF + brillo)
- `thermostat` — termostato (temp actual + botones +/− objetivo)
- `sensor` — sensor temperatura/humedad (solo lectura)
- `blind` — persiana / estor (posición %, control en HomeKit)

**Arquitectura**:
- `core/homebridge_monitor.py` — Sondeo 30s, JWT, caché en memoria, 5 tipos, `set_brightness()`, `set_target_temp()`
- `core/system_monitor.py` — Caché en background thread (cada 2s)
- `core/service_monitor.py` — Caché en background thread (cada 10s), is-enabled batch
- `ui/windows/homebridge.py` — Tarjetas adaptativas por tipo de dispositivo
- `ui/styles.py` — `make_homebridge_switch()` para switch/light
- Badges `hb_offline`, `hb_on`, `hb_fault` en `ui/main_window.py`

---

### 📲 **Alertas Telegram**

**Configuración rápida** — Ver sección en [QUICKSTART.md](QUICKSTART.md) y [README.md](README.md):
- Añadir `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` al `.env`
- Verificar con `alert_service.send_test()`

**Arquitectura**:
- `core/alert_service.py` — 8º servicio background, urllib stdlib, anti-spam edge-trigger + sustain 60s
- Métricas: temperatura, CPU, RAM, disco (warn + crit) y servicios fallidos
- Sin dependencias nuevas — usa `urllib` de la stdlib de Python

---

### 🏗️ **Arquitectura**

**[ARCHITECTURE.md](ARCHITECTURE.md)** (si existe)  
- Estructura del proyecto
- Patrones de diseño
- Flujo de datos
- Cómo extender funcionalidad

---

### 🤝 **Integración**

**[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)**  
- Integrar con fase1.py (OLED)
- Compartir estado de ventiladores
- API de archivos JSON
- Sincronización entre procesos

---

### 💡 **Ideas y Expansión**

**[IDEAS_EXPANSION.md](IDEAS_EXPANSION.md)**  
- ✅ Funcionalidades implementadas (hasta v3.1 inclusive)
- 🔄 En evaluación (Docker, Automatización)
- 💭 Ideas futuras (API REST, Red avanzada, Backup)
- Roadmap v3.1 y v3.2

---

## 📋 Archivos de Soporte

### **Configuración:**
- `requirements.txt` - Dependencias Python
- `.env` - Credenciales Homebridge + Telegram (NO en git)
- `.env.example` - Plantilla de configuración
- `install.sh` - Script de instalación automática
- `config/settings.py` - Configuración global
- `config/themes.py` - Definición de 15 temas

### **Scripts:**
- `main.py` - Punto de entrada
- `scripts/` - Scripts personalizados

### **Compatibilidad:**
- `COMPATIBILIDAD.md` - Sistemas soportados
- `REQUIREMENTS.md` - Requisitos detallados

---

## 🗂️ Estructura de Documentos v3.1

```
📚 Documentación/
├── README.md                    ⭐ Documento principal v3.1
├── QUICKSTART.md                ⚡ Inicio rápido
├── INDEX.md                     📑 Este archivo
├── INSTALL_GUIDE.md             🔧 Instalación
├── THEMES_GUIDE.md              🎨 Guía de temas
├── PROCESS_MONITOR_GUIDE.md     ⚙️ Monitor de procesos
├── SERVICE_MONITOR_GUIDE.md     🔧 Monitor de servicios
├── HISTORICO_DATOS_GUIDE.md     📊 Histórico de datos
├── INTEGRATION_GUIDE.md         🤝 Integración
├── IDEAS_EXPANSION.md           💡 Ideas futuras
├── COMPATIBILIDAD.md            🌐 Compatibilidad
└── REQUIREMENTS.md              📋 Requisitos
```

---

## 🎯 Flujo de Lectura Recomendado

### **Usuario Nuevo:**
1. README.md - Leer sección "Características"
2. QUICKSTART.md - Instalar y ejecutar
3. THEMES_GUIDE.md - Personalizar colores
4. Explorar las 15 ventanas del dashboard 🎉

### **Usuario Avanzado:**
1. README.md completo
2. PROCESS_MONITOR_GUIDE.md - Gestión avanzada
3. SERVICE_MONITOR_GUIDE.md - Control de servicios
4. HISTORICO_DATOS_GUIDE.md - Análisis de datos
5. QUICKSTART.md sección Homebridge - Control de accesorios HomeKit
6. QUICKSTART.md sección Telegram - Alertas externas

### **Desarrollador:**
1. ARCHITECTURE.md - Estructura del proyecto
2. README.md sección "Arquitectura"
3. `ui/styles.py` → `make_window_header()` para añadir nuevas ventanas
4. Código fuente en `core/` y `ui/`
5. IDEAS_EXPANSION.md - Ver qué se puede añadir

---

## 🔍 Buscar por Tema

### **¿Cómo hacer X?**
- **Cambiar tema** → THEMES_GUIDE.md
- **Instalar** → QUICKSTART.md o INSTALL_GUIDE.md
- **Ver procesos** → PROCESS_MONITOR_GUIDE.md
- **Gestionar servicios** → SERVICE_MONITOR_GUIDE.md
- **Ver histórico** → HISTORICO_DATOS_GUIDE.md
- **Configurar ventiladores** → FAN_CONTROL_GUIDE.md
- **Integrar con OLED** → INTEGRATION_GUIDE.md
- **Configurar Homebridge** → QUICKSTART.md sección Homebridge
- **Configurar alertas Telegram** → QUICKSTART.md sección Telegram / README.md
- **Ver logs del dashboard** → Botón "Visor de Logs" en el menú principal
- **Añadir nueva ventana con header** → `ui/styles.py` → `make_window_header()`
- **Añadir funciones** → ARCHITECTURE.md + IDEAS_EXPANSION.md

### **¿Tengo un problema?**
- **No arranca** → QUICKSTART.md sección "Problemas Comunes"
- **Ventiladores no funcionan** → FAN_CONTROL_GUIDE.md
- **Temperatura no se lee** → INSTALL_GUIDE.md
- **Speedtest falla** → README.md sección "Instalación Manual" (CLI Ookla)
- **Base de datos crece** → HISTORICO_DATOS_GUIDE.md
- **Servicios no se gestionan** → SERVICE_MONITOR_GUIDE.md
- **Homebridge no conecta** → QUICKSTART.md sección Homebridge / README.md Troubleshooting
- **Alertas Telegram no llegan** → README.md sección Telegram / verificar `.env`
- **Otro problema** → README.md sección "Troubleshooting"

---

## 📊 Estadísticas del Proyecto v3.1

- **Archivos Python**: 45
- **Ventanas**: 15 ventanas funcionales
- **Temas**: 15 temas pre-configurados
- **Documentos**: 12 guías
- **Servicios background**: 8 (FanAuto + SystemMonitor + ServiceMonitor + DataCollection + Cleanup + Homebridge + AlertService + main)
- **Badges en menú**: 9
- **Exports organizados**: 3 carpetas (csv, logs, screenshots) — máx. 10 por tipo
- **Tipos Homebridge**: 5 (switch, light, thermostat, sensor, blind)

---

## 🆕 Novedades en v3.1

### **Funcionalidades Nuevas:**
- ✅ **Alertas Telegram** — `AlertService` con anti-spam (edge-trigger + sustain 60s), monitoriza temp/CPU/RAM/disco y servicios fallidos, sin dependencias nuevas
- ✅ **Homebridge extendido** — 5 tipos de dispositivo: switch, luz regulable, termostato, sensor temperatura/humedad, persiana/estor
- ✅ **UI diálogo salir** — radiobuttons táctiles 30×30px, botones ajustados, layout corregido

---

## 📊 Evolución de la Documentación

| Versión | Documentos | Características |
|---------|------------|-----------------|
| **v1.0** | 8 | Básico |
| **v2.0** | 10 | + Procesos, Temas |
| **v2.5** | 12 | + Servicios, Histórico |
| **v2.6** | 12 | + Badges, CleanupService |
| **v2.7** | 12 | + Header unificado, Speedtest Ookla |
| **v2.8** | 12 | + Homebridge, 9 badges |
| **v2.9** | 14 | + Switches táctiles, caché background |
| **v3.0** | 15 | + Visor Logs, exports organizados, fix entries |
| **v3.1** | 15 | + Alertas Telegram, Homebridge extendido ⭐ |

---

## 📧 Ayuda Adicional

**¿No encuentras lo que buscas?**

1. Busca en README.md (Ctrl+F)
2. Revisa los ejemplos en las guías
3. Abre un Issue en GitHub
4. Revisa el código fuente (está comentado)

---

## 🔗 Enlaces Rápidos

| Tema | Documento |
|------|-----------|
| **Inicio Rápido** | [QUICKSTART.md](QUICKSTART.md) |
| **Características** | [README.md#características](README.md#características-principales) |
| **Instalación** | [INSTALL_GUIDE.md](INSTALL_GUIDE.md) |
| **Temas** | [THEMES_GUIDE.md](THEMES_GUIDE.md) |
| **Procesos** | [PROCESS_MONITOR_GUIDE.md](PROCESS_MONITOR_GUIDE.md) |
| **Servicios** | [SERVICE_MONITOR_GUIDE.md](SERVICE_MONITOR_GUIDE.md) |
| **Histórico** | [HISTORICO_DATOS_GUIDE.md](HISTORICO_DATOS_GUIDE.md) |
| **Homebridge** | [QUICKSTART.md#homebridge](QUICKSTART.md#-configurar-homebridge) |
| **Telegram** | [QUICKSTART.md#telegram](QUICKSTART.md#-configurar-alertas-telegram) |
| **Troubleshooting** | [README.md#troubleshooting](README.md#troubleshooting) |
| **Ideas Futuras** | [IDEAS_EXPANSION.md](IDEAS_EXPANSION.md) |

---

**¡Toda la información que necesitas está aquí!** 📚✨
````

## File: core/__init__.py
````python
"""
Paquete core con lógica de negocio
"""
from .fan_controller import FanController
from .system_monitor import SystemMonitor
from .network_monitor import NetworkMonitor
from .fan_auto_service import FanAutoService
from .disk_monitor import DiskMonitor
from .process_monitor import ProcessMonitor
from .service_monitor import ServiceMonitor
from .update_monitor import UpdateMonitor
from .cleanup_service import CleanupService
from .homebridge_monitor import HomebridgeMonitor  
from .alert_service import AlertService
from .network_scanner import NetworkScanner
from .pihole_monitor import PiholeMonitor        

__all__ = [
    'FanController',
    'SystemMonitor',
    'NetworkMonitor',
    'FanAutoService',
    'DiskMonitor',
    'ProcessMonitor',
    'ServiceMonitor',
    'UpdateMonitor',
    'CleanupService',
    'HomebridgeMonitor',                                 
    'AlertService',
    'NetworkScanner',
    'PiholeMonitor',
]
````

## File: IDEAS_EXPANSION.md
````markdown
# 💡 Ideas de Expansión - Dashboard v3.1

---

## ✅ Implementado

### **1. Monitor de Procesos en Tiempo Real**
**Implementado en v2.0**
- ✅ Lista en tiempo real (Top 20) con PID, comando, usuario, CPU%, RAM%
- ✅ Búsqueda por nombre o comando
- ✅ Filtros: Todos / Usuario / Sistema
- ✅ Ordenar por PID, Nombre, CPU%, RAM%
- ✅ Matar procesos con confirmación
- ✅ Colores dinámicos según uso
- ✅ Pausa inteligente durante interacciones
- ✅ Estadísticas: procesos totales, CPU, RAM, uptime

---

### **2. Monitor de Servicios systemd**
**Implementado en v2.5**
- ✅ Lista completa de servicios systemd
- ✅ Estados: active, inactive, failed con iconos
- ✅ Start/Stop/Restart con confirmación
- ✅ Ver logs en tiempo real (últimas 50 líneas)
- ✅ Enable/Disable autostart
- ✅ Búsqueda y filtros (Todos / Activos / Inactivos / Fallidos)
- ✅ Estadísticas: total, activos, fallidos, enabled

---

### **3. Histórico de Datos**
**Implementado en v2.5 — ampliado en v2.5.1**
- ✅ Base de datos SQLite (~5MB/10k registros)
- ✅ Recolección automática cada 5 minutos en background
- ✅ Métricas guardadas: CPU, RAM, Temp, Disco I/O, Red, PWM, actualizaciones
- ✅ **8 gráficas**: CPU, RAM, Temperatura, Red Download, Red Upload, Disk Read, Disk Write, PWM
- ✅ Periodos: 24h, 7d, 30d
- ✅ Estadísticas completas: promedios, mínimos, máximos de todas las métricas
- ✅ Detección de anomalías automática
- ✅ Exportación a CSV
- ✅ Exportación de gráficas como imagen PNG
- ✅ Limpieza de datos antiguos configurable
- ✅ **Zoom, pan y navegación** sobre las gráficas (toolbar matplotlib)
- ✅ Registro de eventos críticos en BD separada

---

### **4. Sistema de Temas**
**Implementado en v2.0**
- ✅ 15 temas pre-configurados
- ✅ Cambio con un clic y reinicio automático
- ✅ Preview visual antes de aplicar
- ✅ Persistencia entre reinicios
- ✅ Todos los componentes usan colores del tema (sliders, scrollbars, radiobuttons)

---

### **5. Reinicio y Apagado**
**Implementado en v2.5**
- ✅ Botón Reiniciar con confirmación (aplica cambios de código)
- ✅ Botón Salir con opción de apagar el sistema
- ✅ Terminal de apagado (visualiza apagado.sh en vivo)

---

### **6. Actualizaciones del Sistema**
**Implementado en v2.5.1**
- ✅ Verificación al arranque en background (no bloquea la UI)
- ✅ Sistema de caché 12h (no repite apt update innecesariamente)
- ✅ Ventana dedicada con estado visual
- ✅ Instalación con terminal integrada en vivo
- ✅ Botón Buscar para forzar comprobación manual
- ✅ Refresco automático del estado tras instalar

---

### **7. Sistema de Logging Completo**
**Implementado en v2.5.1**
- ✅ Cobertura 100% en módulos core y UI
- ✅ Niveles diferenciados: DEBUG, INFO, WARNING, ERROR
- ✅ Rotación automática 2MB con backup
- ✅ Archivo fijo `data/logs/dashboard.log`

---

### **8. Lanzadores de Scripts**
**Implementado desde v1.0 — mejorado en v2.5.1**
- ✅ Scripts personalizados configurables en `settings.py`
- ✅ Terminal integrada que muestra el output en vivo
- ✅ Confirmación previa a ejecución
- ✅ Layout en grid configurable

---

### **9. Servicio de Limpieza Automática**
**Implementado en v2.6**
- ✅ `CleanupService` en `core/` — singleton, daemon thread
- ✅ Limpieza automática de CSV exportados (máx. 10)
- ✅ Limpieza automática de PNG exportados (máx. 10)
- ✅ Limpieza periódica de BD SQLite (registros >30 días, cada 24h)
- ✅ `force_cleanup()` para limpieza manual desde la UI
- ✅ Inyección de dependencias en `HistoryWindow`
- ✅ Botón "Limpiar Antiguos" delega en el servicio
- ✅ Red de seguridad por tamaño en `DataLogger` (>5MB → limpia a 7 días)

---

### ~~**10. Notificaciones Visuales en el Menú**~~ ✅ Implementado en v2.6
**Implementado en v2.6**
- ✅ Badge en "Actualizaciones" con paquetes pendientes (naranja)
- ✅ Badge en "Monitor Servicios" con servicios fallidos (rojo)
- ✅ Badge en "Control Ventiladores" y "Monitor Placa" con temperatura (naranja >60°C, rojo >70°C)
- ✅ Badge en "Monitor Placa" con CPU (naranja >75%, rojo >90%)
- ✅ Badge en "Monitor Placa" con RAM (naranja >75%, rojo >90%)
- ✅ Badge en "Monitor Disco" con uso de disco (naranja >80%, rojo >90%)
- ✅ Texto dinámico en badge (valor real: temperatura en °C, porcentaje)
- ✅ Color de texto adaptativo (negro sobre amarillo, blanco sobre rojo)

---

### ~~**11. Header Unificado con Status Dinámico**~~ ✅ Implementado en v2.7
**Implementado en v2.7**
- ✅ `make_window_header()` centralizado en `ui/styles.py`
- ✅ Header en todas las ventanas: título + status + botón ✕ táctil
- ✅ Botón ✕ de 52×42px, optimizado para uso táctil en pantalla DSI 4,5"
- ✅ Status dinámico en Monitor Placa: CPU%, RAM%, temperatura en tiempo real
- ✅ Status dinámico en Monitor Disco: espacio disponible + temperatura NVMe
- ✅ Status dinámico en Monitor Red: interfaz activa + velocidades de red
- ✅ Speedtest migrado a CLI oficial de Ookla (`--format=json`, MB/s reales)

---

### ~~**12. Integración Homebridge**~~ ✅ Implementado en v2.8
**Implementado en v2.8**
- ✅ `HomebridgeMonitor` en `core/` — singleton, daemon thread, sondeo cada 30s
- ✅ Autenticación JWT con renovación automática en 401
- ✅ Lectura desde caché en memoria para badges (sin peticiones HTTP adicionales)
- ✅ `toggle()` fuerza sondeo inmediato tras el comando
- ✅ Ventana `HomebridgeWindow` con grid de 2 columnas estilo Lanzadores
- ✅ Indicador ● color por dispositivo (on/off), ⚠ rojo si `StatusFault=1`
- ✅ Soporte para accesorios con característica HomeKit `On` (enchufes e interruptores)
- ✅ 3 badges en el botón "Homebridge" del menú
- ✅ `_reachable = None` al arrancar → badges no aparecen hasta primera consulta real
- ✅ Configuración por `.env` — credenciales fuera del código
- ✅ Dependencia `python-dotenv>=1.0.0` con fallback manual si no está instalada

---

### ~~**13. Optimización de Rendimiento — UI sin bloqueos**~~ ✅ Implementado en v2.9
**Implementado en v2.9**
- ✅ `SystemMonitor` con thread de background (cada 2s) — `get_current_stats()` devuelve caché sin llamar psutil
- ✅ `ServiceMonitor` con thread de background (cada 10s) — `get_services()` / `get_stats()` devuelven caché
- ✅ `is-enabled` obtenido en una sola llamada batch (`systemctl is-enabled u1 u2 ...`) en lugar de N subprocesses
- ✅ `refresh_now()` fuerza refresco inmediato tras start/stop/restart/enable/disable
- ✅ `_update()` de `MainWindow` solo lee cachés — hilo de Tkinter completamente libre de syscalls bloqueantes
- ✅ Todos los servicios background registran inicio y parada en el log (`FanAutoService` incluido)
- ✅ `make_homebridge_switch()` en `ui/styles.py` — CTkSwitch (90×46px) estilado con colores del tema

---

### ~~**14. Control Homebridge con Switches Táctiles**~~ ✅ Implementado en v2.9
**Implementado en v2.9**
- ✅ `CTkSwitch` en lugar de botones ON/OFF — más intuitivo y adaptado al uso táctil
- ✅ Tamaño 90×46px óptimo para operar con el dedo en pantalla DSI de 4,5"
- ✅ Estado disabled en rojo para dispositivos con fallo (no interactivo)
- ✅ Colores del tema activo: success (ON), bg_light (OFF), danger (fallo)
- ✅ Nombre del dispositivo integrado como etiqueta del switch

---

### ~~**15. Visor de Logs**~~ ✅ Implementado en v3.0
**Implementado en v3.0**
- ✅ Ventana `LogViewerWindow` con filtros por nivel (DEBUG/INFO/WARNING/ERROR), módulo, texto libre e intervalo de fechas/horas
- ✅ Selector rápido: 15min, 1h, 6h, 24h o rango manual con date/time entries
- ✅ Colores por nivel: gris (DEBUG), azul (INFO), naranja (WARNING), rojo (ERROR)
- ✅ Exportación del resultado filtrado a `data/exports/logs/`
- ✅ Recarga manual — lee también el archivo rotado `.log.1`
- ✅ Scrollbar táctil (22px) integrado con `StyleManager.style_scrollbar_ctk`

---

### ~~**16. Exports organizados y limpieza al exportar**~~ ✅ Implementado en v3.0
**Implementado en v3.0**
- ✅ Carpetas `data/exports/{csv,logs,screenshots}` creadas automáticamente al arrancar (`settings.py`)
- ✅ `CleanupService` gestiona también `log_export_*.log` (máx. 10) — `DEFAULT_MAX_LOG`, `clean_log_exports()`
- ✅ Limpieza automática al exportar CSV, PNG y logs — no solo en el ciclo de 24h
- ✅ `get_status()` y `force_cleanup()` actualizados con `log_count` y `deleted_log`

---

### ~~**17. Fix grab_set en FanControlWindow**~~ ✅ Implementado en v3.0
**Implementado en v3.0**
- ✅ Eliminado `grab_set()` en `FanControlWindow` que bloqueaba el teclado en todas las ventanas al cerrarse
- ✅ El bug afectaba a entries en `history.py`, `service.py`, `process_window.py` y `log_viewer.py`

---

### ~~**18. Alertas Externas por Telegram**~~ ✅ Implementado en v3.1
**Implementado en v3.1**
- ✅ `AlertService` en `core/` — singleton, daemon thread, comprobación cada 15s
- ✅ Sin dependencias nuevas — usa `urllib` de la stdlib
- ✅ Métricas monitorizadas: temperatura, CPU, RAM, disco (umbrales warn + crit independientes) y servicios fallidos
- ✅ Anti-spam: edge-trigger + sustain de 60s (condición debe mantenerse antes de enviar)
- ✅ Reseteo automático cuando la condición baja del umbral (permite nuevo flanco)
- ✅ `send_test()` para verificar configuración sin esperar una alerta real
- ✅ Configurable por `.env`: `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID`
- ✅ Si las variables no están configuradas, el servicio arranca pero no envía (warning en log)
- ✅ Integrado en `main.py` con `start()`/`stop()` y `atexit` igual que el resto de servicios

---

### ~~**19. Homebridge Extendido**~~ ✅ Implementado en v3.1
**Implementado en v3.1**
- ✅ `HomebridgeMonitor` reconoce ahora 5 tipos de dispositivo:
  - `switch` — característica `On` (enchufe / interruptor)
  - `light` — `On` + `Brightness` (luz regulable)
  - `thermostat` — `CurrentTemperature` + `TargetTemperature`
  - `sensor` — `CurrentTemperature` y/o `CurrentRelativeHumidity` (solo lectura)
  - `blind` — `CurrentPosition` (persiana / estor)
- ✅ `set_brightness(unique_id, brightness)` — control de brillo 0–100%
- ✅ `set_target_temp(unique_id, temp)` — control de temperatura objetivo en termostatos
- ✅ Tarjetas adaptativas en `HomebridgeWindow._create_device_card()` según `acc["type"]`
- ✅ Termostato: temperatura actual + botones +/− 0.5°C con closure mutable
- ✅ Sensor: lectura de temp y/o humedad con íconos 🌡 💧
- ✅ Persiana: barra `CTkProgressBar` mostrando posición actual (control en HomeKit)

---

### ~~**20. UI Diálogo Salir**~~ ✅ Implementado en v3.1
**Implementado en v3.1**
- ✅ Radiobuttons táctiles 30×30px en el diálogo de salir (`radiobutton_width=30, radiobutton_height=30`)
- ✅ Botones ajustados a referencia estándar: Continuar `width=15, height=8`, Cancelar `width=20, height=10`
- ✅ `buttons_frame` con `side="bottom"` para evitar hueco inferior en el layout

---

## 🔄 Planificado v3.2

### ~~**Historial de Alertas**~~ — Guía disponible: `GUIA_HISTORIAL_ALERTAS.md`
**Complejidad**: 🟢 Baja — 2-3h  
**Archivos**: `core/alert_service.py` (modificar), `ui/windows/alert_history.py` (nuevo)

- Persistencia en `data/alert_history.json` (máx. 100 entradas)
- Ventana nueva "Historial Alertas" con tarjetas por alerta: timestamp, métrica, nivel, valor
- Colores por nivel: naranja (warn), rojo (crit)
- Botón "Borrar todo" con confirmación
- Solo guarda alertas enviadas con éxito a Telegram (o siempre si se prefiere)

---

### ~~**Panel de Red Local (arp-scan)**~~ — Guía disponible: `GUIA_PANEL_RED_PIHOLE.md`
**Complejidad**: 🟡 Media — 3h  
**Archivos**: `core/network_scanner.py` (nuevo), `ui/windows/network_local.py` (nuevo)

- Escaneo con `sudo arp-scan --localnet` en thread background
- Lista de dispositivos: IP, MAC, fabricante, hostname resuelto
- Refresco manual + automático cada 60s
- Prerequisito: añadir `arp-scan` a sudoers para ejecución sin contraseña

---

### ~~**Pi-hole Stats**~~ — Guía disponible: `GUIA_PANEL_RED_PIHOLE.md`
**Complejidad**: 🟡 Media — 2-3h  
**Archivos**: `core/pihole_monitor.py` (nuevo), `ui/windows/pihole_window.py` (nuevo)

- `PiholeMonitor` — 9º servicio background, sondeo cada 60s, API Pi-hole v5
- Métricas: queries hoy, bloqueadas, % bloqueado, dominios en lista, clientes únicos, estado
- Configurable por `.env`: `PIHOLE_HOST`, `PIHOLE_PORT`, `PIHOLE_TOKEN`
- Badge `pihole_offline` en el menú si Pi-hole no responde
- Nota: requiere Pi-hole v5 (api.php); v6 tiene API diferente

---

## 🚀 Ideas Futuras (Backlog)

**Automatización**: cron visual, perfiles de ventiladores por hora, auto-reinicio servicios caídos

**Backup**: programar backups, estado con progreso, sincronización cloud

**Seguridad**: intentos de login fallidos, logs de seguridad, firewall status

**API REST**: endpoints para métricas, histórico y control de servicios

---

## 🎯 Roadmap

### **v2.5.1** ✅ — 2026-02-20
- ✅ Logging completo en todos los módulos
- ✅ Ventana Actualizaciones con caché y terminal
- ✅ 8 gráficas en Histórico (Red, Disco, PWM añadidas)
- ✅ Zoom y navegación en gráficas
- ✅ Fix bug atexit en DataCollectionService

### **v2.6** ✅ — 2026-02-22
- ✅ Badges de notificación visual en menú principal (6 badges, 5 botones)
- ✅ CleanupService — limpieza automática background de CSV, PNG y BD
- ✅ Fan control: entries con placeholder en lugar de sliders

### **v2.7** ✅ — 2026-02-23
- ✅ Header unificado `make_window_header()` en todas las ventanas
- ✅ Status dinámico en tiempo real en el header
- ✅ Botón ✕ táctil 52×42px para pantalla DSI
- ✅ Speedtest migrado a CLI oficial de Ookla (JSON, MB/s reales)

### **v2.8** ✅ — 2026-02-23
- ✅ Integración Homebridge completa
- ✅ HomebridgeMonitor con JWT, sondeo 30s, caché en memoria
- ✅ HomebridgeWindow con toggle táctil en grid 2 columnas
- ✅ 3 badges Homebridge en menú principal

### **v2.9** ✅ — 2026-02-24
- ✅ SystemMonitor y ServiceMonitor con caché en background thread
- ✅ ServiceMonitor: is-enabled batch, sondeo 10s, refresh_now() tras acciones
- ✅ HomebridgeWindow: CTkSwitch táctil 90×46px en lugar de botones
- ✅ make_homebridge_switch() en ui/styles.py
- ✅ Logging completo en todos los servicios background (FanAutoService incluido)

### **v3.0** ✅ — 2026-02-26
- ✅ Visor de Logs con filtros avanzados y exportación
- ✅ Exports organizados en data/exports/{csv,logs,screenshots}
- ✅ Limpieza automática al exportar (CSV, PNG, logs)
- ✅ Fix grab_set en FanControlWindow — entries funcionan en todas las ventanas

### **v3.1** ✅ ACTUAL — 2026-02-26
- ✅ Alertas externas por Telegram (AlertService, anti-spam, 5 métricas)
- ✅ Homebridge extendido (5 tipos: switch, light, thermostat, sensor, blind)
- ✅ UI diálogo salir mejorada (radiobuttons 30×30, botones ajustados)

### **v3.2** (Próxima)
- [ ] Historial de alertas (ventana + persistencia JSON)
- [ ] Panel de red local (arp-scan, lista dispositivos)
- [ ] Pi-hole stats (monitor background, ventana métricas, badge)

### **v3.3** (Futuro)
- [ ] Automatización (cron visual, perfiles ventiladores, auto-reinicio)
- [ ] API REST básica

---

## 📈 Cobertura actual

| Área | Estado |
|------|--------|
| Monitoreo básico (CPU, RAM, Temp, Disco, Red) | ✅ 100% |
| Control avanzado (Ventiladores, Procesos, Servicios) | ✅ 100% |
| Histórico y análisis | ✅ 100% |
| Actualizaciones del sistema | ✅ 100% |
| Logging y observabilidad | ✅ 100% |
| Notificaciones visuales internas | ✅ 100% |
| UI unificada y táctil | ✅ 100% |
| Integración Homebridge (5 tipos) | ✅ 100% |
| Visor de logs con filtros y exportación | ✅ 100% |
| Exports organizados y limpieza automática | ✅ 100% |
| Alertas externas Telegram | ✅ 100% |
| Historial de alertas | 📋 Guía lista |
| Panel de red local (arp-scan) | 📋 Guía lista |
| Pi-hole stats | 📋 Guía lista |
| Automatización | ⏳ 0% |
| API REST | ⏳ 0% |

---

**Versión actual**: v3.1 — **Próxima**: v3.2 — **Última actualización**: 2026-02-26
````

## File: ui/windows/history.py
````python
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
````

## File: README.md
````markdown
# 🖥️ Sistema de Monitoreo y Control - Dashboard v3.1

Sistema completo de monitoreo y control para Raspberry Pi con interfaz gráfica DSI, control de ventiladores PWM, temas personalizables, histórico de datos, gestión avanzada del sistema, integración con Homebridge y alertas externas por Telegram.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![Version](https://img.shields.io/badge/Version-3.1-orange.svg)]()

---

## ✨ Características Principales

### 🖥️ **Monitoreo Completo del Sistema**
- **CPU**: Uso en tiempo real, frecuencia, gráficas históricas
- **RAM**: Memoria usada/total, porcentaje, visualización dinámica
- **Temperatura**: Monitoreo de CPU con alertas por color
- **Disco**: Espacio usado/disponible, temperatura NVMe, I/O en tiempo real

### 🪟 **UI Unificada con Header Táctil**
- **Header en todas las ventanas**: título + status dinámico + botón ✕ (52×42px táctil)
- **Status en tiempo real** en el header: CPU/RAM/Temp (Monitor Placa), Disco/NVMe (Monitor Disco), interfaz/velocidades (Monitor Red)
- **Botón ✕ táctil** optimizado para pantalla DSI de 4,5" sin teclado
- Función `make_window_header()` centralizada en `ui/styles.py`

### 🌡️ **Control Inteligente de Ventiladores**
- **5 Modos**: Auto (curva), Manual, Silent (30%), Normal (50%), Performance (100%)
- **Curvas personalizables**: Define hasta 8 puntos temperatura-PWM
- **Servicio background**: Funciona incluso con ventana cerrada
- **Visualización en vivo**: Gráfica de curva activa y PWM actual

### 🌐 **Monitor de Red Avanzado**
- **Tráfico en tiempo real**: Download/Upload con gráficas
- **Auto-detección**: Interfaz activa (eth0, wlan0, tun0)
- **Lista de IPs**: Todas las interfaces con iconos por tipo
- **Speedtest integrado**: CLI oficial de Ookla (JSON nativo, resultados en MB/s reales)
- **Status en header**: interfaz activa + velocidades actuales

### 🏠 **Integración Homebridge Extendida**
- **5 tipos de dispositivo**: switch/enchufe, luz regulable (brillo), termostato, sensor temperatura/humedad, persiana/estor
- **CTkSwitch táctil** (90×46px): Toggle grande optimizado para uso con el dedo en pantalla DSI
- **Tarjetas adaptativas**: Cada tipo muestra su propia interfaz de control
  - **Luces**: switch ON/OFF igual que enchufes
  - **Termostatos**: temperatura actual + botones +/− 0.5°C para temperatura objetivo
  - **Sensores**: temperatura y/o humedad en modo solo lectura
  - **Persianas**: posición actual (%) con barra visual (control desde HomeKit)
- **Indicador visual**: switch verde ON / gris OFF, ⚠ rojo bloqueado si `StatusFault=1`
- **Sondeo ligero en background**: Cada 30 segundos sin bloquear la UI
- **Autenticación JWT** con renovación automática en 401
- **3 badges en el menú**: offline (🔴), dispositivos encendidos (🟠), dispositivos con fallo (🔴)
- **Configuración por `.env`**: IP, puerto, usuario y contraseña de Homebridge
- Requiere **Insecure Mode** activado en Homebridge para acceder a accesorios

### 📲 **Alertas Externas por Telegram**
- **Sin dependencias nuevas**: usa `urllib` de la stdlib de Python
- **Métricas monitorizadas**: temperatura, CPU, RAM, disco y servicios fallidos
- **Umbrales configurables**: warn y crit independientes por métrica
- **Anti-spam inteligente**: edge-trigger + sustain de 60s (condición debe mantenerse antes de enviar)
- **Reseteo automático**: cuando la condición baja del umbral, permite una nueva alerta en el siguiente flanco
- **Configurable por `.env`**: `TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID`
- **Mensaje de prueba**: `alert_service.send_test()` para verificar la configuración
- **8º servicio background**: integrado en `main.py` con `start()`/`stop()` igual que el resto

### ⚙️ **Monitor de Procesos**
- **Lista en tiempo real**: Top 20 procesos con CPU/RAM
- **Búsqueda inteligente**: Por nombre o comando completo
- **Filtros**: Todos / Usuario / Sistema
- **Terminar procesos**: Con confirmación y feedback

### ⚙️ **Monitor de Servicios systemd**
- **Gestión completa**: Start/Stop/Restart servicios
- **Estado visual**: active, inactive, failed con iconos
- **Autostart**: Enable/Disable con confirmación
- **Logs en tiempo real**: Ver últimas 50 líneas
- **Caché en background**: Sondeo cada 10s sin bloquear la UI; `is-enabled` en llamada batch

### 📊 **Histórico de Datos**
- **Recolección automática**: Cada 5 minutos en background
- **Base de datos SQLite**: Ligera y eficiente
- **Visualización gráfica**: 8 gráficas (CPU, RAM, Temperatura, Red Download, Red Upload, Disk Read, Disk Write, PWM)
- **Periodos**: 24 horas, 7 días, 30 días
- **Estadísticas**: Promedios, mínimos, máximos
- **Detección de anomalías**: Alertas automáticas
- **Exportación CSV**: Para análisis externo

### 󱇰 **Monitor USB**
- **Detección automática**: Dispositivos conectados
- **Separación inteligente**: Mouse/teclado vs almacenamiento
- **Expulsión segura**: Unmount + eject con confirmación

###  **Monitor de Disco**
- **Particiones**: Uso de espacio de todas las unidades
- **Temperatura NVMe**: Monitoreo térmico del SSD (smartctl/sysfs)
- **Velocidad I/O**: Lectura/escritura en MB/s
- **Status en header**: espacio disponible + temperatura NVMe en tiempo real

### 󱓞 **Lanzadores de Scripts**
- **Terminal integrada**: Visualiza la ejecución en tiempo real
- **Layout en grid**: Organización visual en columnas
- **Confirmación previa**: Diálogo antes de ejecutar

### 󰆧 **Actualizaciones del Sistema**
- **Verificación al arranque**: En background sin bloquear la UI
- **Sistema de caché 12h**: No repite `apt update` innecesariamente
- **Terminal integrada**: Instala viendo el output en vivo
- **Botón Buscar**: Fuerza comprobación manual

### 󰆧 **15 Temas Personalizables**
- **Cambio con un clic**: Reinicio automático
- **Paletas completas**: Cyberpunk, Matrix, Dracula, Nord, Tokyo Night, etc.
- **Preview en vivo**: Ve los colores antes de aplicar

### /󰿅 **Reinicio y Apagado**
- **Botón Reiniciar**: Reinicia el dashboard aplicando cambios de código
- **Botón Salir**: Salir de la app o apagar el sistema con radiobuttons táctiles (30×30px)
- **Terminal de apagado**: Visualiza `apagado.sh` en tiempo real
- **Con confirmación**: Evita acciones accidentales

### 📋 **Visor de Logs**
- **Filtros avanzados**: Por nivel (DEBUG/INFO/WARNING/ERROR), módulo, texto libre e intervalo de fechas/horas
- **Colores por nivel**: gris / azul / naranja / rojo
- **Selector rápido**: 15min, 1h, 6h, 24h o rango manual
- **Exportación**: Guarda el resultado filtrado en `data/exports/logs/`
- **Recarga manual**: Lee también el archivo rotado `.log.1`

### 🔔 **Badges de Notificación Visual**
- **9 badges** en el menú principal con alertas en tiempo real
- **Temperatura**: naranja >60°C, rojo >70°C (Control Ventiladores + Monitor Placa)
- **CPU y RAM**: naranja >75%, rojo >90% (Monitor Placa)
- **Disco**: naranja >80%, rojo >90% (Monitor Disco)
- **Servicios fallidos**: rojo con contador (Monitor Servicios)
- **Actualizaciones pendientes**: naranja con contador (Actualizaciones)
- **Homebridge offline**: rojo si sin conexión
- **Dispositivos encendidos**: naranja con contador
- **Dispositivos con fallo**: rojo si `StatusFault=1`

### 🧹 **Limpieza Automática**
- **CleanupService**: servicio background singleton
- Limpia CSV exportados (máx. 10), PNG exportados (máx. 10), logs exportados (máx. 10)
- Limpieza automática también al exportar — no solo en el ciclo de 24h
- Limpia BD SQLite: registros >30 días cada 24h
- Red de seguridad: si BD supera 5MB limpia a 7 días al arrancar
- Botón "Limpiar Antiguos" fuerza limpieza manual completa

### 📋 **Sistema de Logging Completo**
- **Cobertura total**: Todos los módulos core y UI incluyendo todos los servicios background
- **Niveles diferenciados**: DEBUG, INFO, WARNING, ERROR
- **Rotación automática**: 2MB máximo con backup
- **Ubicación**: `data/logs/dashboard.log`
- **Todos los servicios** registran inicio y parada en el log

---

## 📦 Instalación

###  **Requisitos del Sistema**
- **Hardware**: Raspberry Pi 3/4/5
- **OS**: Raspberry Pi OS (Bullseye/Bookworm) o Kali Linux
- **Pantalla**: Touchscreen DSI 4,5" (800x480) o HDMI
- **Python**: 3.8 o superior

### ⚡ **Instalación Recomendada**

Usa el script de instalación directa (sin entorno virtual):

```bash
git clone https://github.com/tu-usuario/system-dashboard.git
cd system-dashboard
chmod +x install_system.sh
sudo ./install_system.sh
python3 main.py
```

El script `install_system.sh` instala automáticamente:
- Dependencias del sistema (`lm-sensors`, `usbutils`, `udisks2`)
- Dependencias Python con `--break-system-packages`
- CLI oficial de Ookla para speedtest
- Ofrece configurar sensores de temperatura

### 🛠️ **Instalación Manual**

Si prefieres instalar paso a paso:

```bash
# 1. Dependencias del sistema
sudo apt-get update
sudo apt-get install -y lm-sensors usbutils udisks2 smartmontools

# 2. CLI oficial de Ookla (speedtest)
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest

# 3. Detectar sensores
sudo sensors-detect --auto

# 4. Dependencias Python
pip3 install --break-system-packages -r requirements.txt

# 5. Ejecutar
python3 main.py
```

###  **Alternativa con Entorno Virtual**

Si prefieres aislar las dependencias Python:

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python3 main.py
```

> **Nota**: Con venv necesitas activar el entorno (`source venv/bin/activate`) cada vez antes de ejecutar.

---

## 🏠 Configuración de Homebridge

La integración con Homebridge requiere un archivo `.env` en la raíz del proyecto:

```env
HOMEBRIDGE_HOST=192.168.1.X    # IP de la Raspberry Pi con Homebridge
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña
```

> **Importante**: Activa el **Insecure Mode** en Homebridge (`homebridge-config-ui-x → Configuración → Homebridge`) para que la API permita acceder y controlar los accesorios.

El archivo `.env` está en `.gitignore` y nunca se sube al repositorio.

La ventana Homebridge muestra los accesorios en un grid de 2 columnas con tarjetas adaptativas según el tipo de dispositivo.

---

## 📲 Configuración de Alertas Telegram

Añade al archivo `.env` existente:

```env
TELEGRAM_TOKEN=123456789:ABCdefGHI...   # Token del bot (@BotFather)
TELEGRAM_CHAT_ID=987654321              # ID del chat o canal destino
```

> Si `TELEGRAM_TOKEN` o `TELEGRAM_CHAT_ID` no están configurados, `AlertService` arranca igualmente pero registra un warning y no envía nada.

Para verificar la configuración desde Python:

```python
alert_service.send_test()
```

### Umbrales por defecto

| Métrica  | Aviso (🟠) | Crítico (🔴) |
|----------|-----------|------------|
| Temperatura | 60°C | 70°C |
| CPU | 85% | 95% |
| RAM | 85% | 95% |
| Disco | 85% | 95% |
| Servicios | — | cualquier FAILED |

---

## 󰍜 Menú Principal (15 botones)

```
┌─────────────────────────────────────┐
│  Control         │  Monitor          │
│  Ventiladores    │  Placa            │
├──────────────────┼───────────────────┤
│  Monitor         │  Monitor          │
│  Red             │  USB              │
├──────────────────┼───────────────────┤
│  Monitor         │  Lanzadores       │
│  Disco           │                   │
├──────────────────┼───────────────────┤
│  Monitor         │  Monitor          │
│  Procesos        │  Servicios        │
├──────────────────┼───────────────────┤
│  Histórico       │  Actualizaciones  │
│  Datos           │                   │
├──────────────────┼───────────────────┤
│  Homebridge      │  Visor de Logs    │
├──────────────────┼───────────────────┤
│  Cambiar Tema    │  Reiniciar        │
├──────────────────┼───────────────────┤
│  Salir           │                   │
└──────────────────┴───────────────────┘
```

### **Las 15 Ventanas:**

1. **Control Ventiladores** - Configura modos y curvas PWM
2. **Monitor Placa** - CPU, RAM, temperatura en tiempo real (status en header)
3. **Monitor Red** - Tráfico, speedtest Ookla, interfaces e IPs (status en header)
4. **Monitor USB** - Dispositivos y expulsión segura
5. **Monitor Disco** - Espacio, temperatura NVMe, I/O (status en header)
6. **Lanzadores** - Ejecuta scripts con terminal en vivo
7. **Monitor Procesos** - Gestión avanzada de procesos
8. **Monitor Servicios** - Control de servicios systemd
9. **Histórico Datos** - Visualización de métricas históricas con exportación CSV
10. **Actualizaciones** - Gestión de paquetes del sistema
11. **Homebridge** - Control de 5 tipos de dispositivos HomeKit
12. **Visor de Logs** - Visualización y exportación del log del dashboard
13. **Cambiar Tema** - Selecciona entre 15 temas
14. **Reiniciar** - Reinicia el dashboard
15. **Salir** - Cierra la app o apaga el sistema

---

## 󰔎 Temas Disponibles

| Tema | Colores | Estilo |
|------|---------|--------|
| **Cyberpunk** | Cyan + Verde | Original neón |
| **Matrix** | Verde brillante | Película Matrix |
| **Sunset** | Naranja + Púrpura | Atardecer cálido |
| **Ocean** | Azul + Aqua | Océano refrescante |
| **Dracula** | Púrpura + Rosa | Elegante oscuro |
| **Nord** | Azul hielo | Minimalista nórdico |
| **Tokyo Night** | Azul + Púrpura | Noche de Tokio |
| **Monokai** | Cyan + Verde | IDE clásico |
| **Gruvbox** | Naranja + Beige | Retro cálido |
| **Solarized** | Azul + Cyan | Científico |
| **One Dark** | Azul claro | Atom editor |
| **Synthwave** | Rosa + Verde | Neón 80s |
| **GitHub Dark** | Azul GitHub | Profesional |
| **Material** | Azul material | Google Design |
| **Ayu Dark** | Azul cielo | Minimalista |

---

## 📊 Arquitectura del Proyecto

```
system_dashboard/
├── config/
│   ├── settings.py                 # Constantes globales, LAUNCHERS y rutas de exports
│   └── themes.py                   # 15 temas pre-configurados
├── core/
│   ├── fan_controller.py           # Control PWM y curvas
│   ├── fan_auto_service.py         # Servicio background ventiladores
│   ├── system_monitor.py           # CPU, RAM, temp — caché en background thread
│   ├── network_monitor.py          # Red, speedtest Ookla CLI, interfaces
│   ├── disk_monitor.py             # Disco, NVMe, I/O
│   ├── process_monitor.py          # Gestión de procesos
│   ├── service_monitor.py          # Servicios systemd — caché 10s, batch is-enabled
│   ├── update_monitor.py           # Actualizaciones con caché 12h
│   ├── homebridge_monitor.py       # Integración Homebridge (JWT, sondeo 30s, 5 tipos)
│   ├── alert_service.py            # Alertas Telegram (urllib, anti-spam, 5 métricas)
│   ├── data_logger.py              # SQLite logging
│   ├── data_analyzer.py            # Análisis histórico
│   ├── data_collection_service.py  # Recolección automática (singleton)
│   ├── cleanup_service.py          # Limpieza automática background (singleton)
│   └── __init__.py
├── ui/
│   ├── main_window.py              # Ventana principal (15 botones + badges)
│   ├── styles.py                   # make_window_header(), make_futuristic_button(),
│   │                               # make_homebridge_switch(), StyleManager
│   ├── widgets/
│   │   ├── graphs.py               # Gráficas personalizadas
│   │   └── dialogs.py              # custom_msgbox, confirm_dialog, terminal_dialog
│   └── windows/
│       ├── monitor.py, network.py, usb.py, disk.py
│       ├── process_window.py, service.py, history.py
│       ├── update.py, fan_control.py
│       ├── launchers.py, theme_selector.py
│       ├── homebridge.py           # 5 tarjetas adaptativas por tipo de dispositivo
│       ├── log_viewer.py           # Visor de logs con filtros y exportación
│       └── __init__.py
├── utils/
│   ├── file_manager.py             # Gestión de JSON (escritura atómica)
│   ├── system_utils.py             # Utilidades del sistema
│   └── logger.py                   # DashboardLogger (rotación 2MB)
├── data/                            # Auto-generado al ejecutar
│   ├── fan_state.json, fan_curve.json, theme_config.json
│   ├── history.db                  # SQLite histórico
│   ├── logs/dashboard.log          # Log del sistema
│   └── exports/                    # Archivos exportados (máx. 10 por tipo)
│       ├── csv/                    # Exportaciones CSV del histórico
│       ├── logs/                   # Exportaciones del visor de logs
│       └── screenshots/            # Capturas de gráficas
├── scripts/                         # Scripts personalizados del usuario
├── .env                             # Credenciales Homebridge + Telegram (NO en git)
├── .env.example                     # Plantilla de configuración
├── install_system.sh               # Instalación directa (recomendada)
├── install.sh                      # Instalación con venv (alternativa)
├── main.py
└── requirements.txt
```

---

##  Configuración

### **`config/settings.py`**

```python
# Posición en pantalla DSI
DSI_WIDTH = 800
DSI_HEIGHT = 480
DSI_X = 0
DSI_Y = 0

# Scripts personalizados en Lanzadores
LAUNCHERS = [
    {"label": "Montar NAS",   "script": str(SCRIPTS_DIR / "montarnas.sh")},
    {"label": "Conectar VPN", "script": str(SCRIPTS_DIR / "conectar_vpn.sh")},
    # Añade tus scripts aquí
]
```

### **`.env` (Homebridge + Telegram)**

```env
HOMEBRIDGE_HOST=192.168.1.X
HOMEBRIDGE_PORT=8581
HOMEBRIDGE_USER=admin
HOMEBRIDGE_PASS=tu_contraseña

TELEGRAM_TOKEN=123456789:ABCdefGHI...
TELEGRAM_CHAT_ID=987654321
```

---

## 📋 Sistema de Logging

```bash
# Ver logs en tiempo real
tail -f data/logs/dashboard.log

# Solo errores
grep ERROR data/logs/dashboard.log

# Eventos de hoy
grep "$(date +%Y-%m-%d)" data/logs/dashboard.log
```

**Niveles:** `DEBUG` (operaciones normales) · `INFO` (eventos importantes) · `WARNING` (degradación) · `ERROR` (fallos)

Todos los servicios background registran su inicio y parada. Al arrancar verás entradas como:
```
[SystemMonitor]     Sondeo iniciado (cada 2.0s)
[ServiceMonitor]    Sondeo iniciado (cada 10s)
[HomebridgeMonitor] Sondeo iniciado (cada 30s)
[FanAutoService]    Servicio iniciado
[DataCollection]    Servicio iniciado (cada 5 min)
[CleanupService]    Servicio iniciado
[AlertService]      Servicio iniciado (cada 15s)
```

---

## 📈 Rendimiento

- **Uso CPU**: ~5-10% en idle
- **Uso RAM**: ~100-150 MB
- **Base de datos**: ~5 MB por 10,000 registros
- **Actualización UI**: 2 segundos (configurable en `UPDATE_MS`) — solo lectura de caché, sin syscalls bloqueantes
- **Threads background**: 8 (FanAuto + SystemMonitor + ServiceMonitor + DataCollection + Cleanup + Homebridge + AlertService + main)
- **Log**: máx. 2MB con rotación automática

---

##  Troubleshooting

| Problema | Solución |
|----------|----------|
| No arranca | `pip3 install --break-system-packages -r requirements.txt` |
| Temperatura 0 | `sudo sensors-detect --auto && sudo systemctl restart lm-sensors` |
| NVMe temp 0 | `sudo apt install smartmontools` |
| Ventiladores no responden | `sudo python3 main.py` |
| Speedtest falla | Instalar CLI oficial Ookla: ver sección Instalación Manual |
| USB no expulsa | `sudo apt install udisks2` |
| Homebridge no conecta | Verificar IP/puerto en `.env` y que Insecure Mode esté activo |
| Badge hb_offline siempre rojo | Comprobar `HOMEBRIDGE_HOST` en `.env` y red entre Pis |
| Servicios tardan en aparecer | Normal — ServiceMonitor sondea systemctl cada 10s al arrancar |
| No puedo escribir en los entries | Asegúrate de usar v3.0+ — el bug de `grab_set` está corregido |
| Alertas Telegram no llegan | Verificar `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` en `.env`; ejecutar `send_test()` |
| Ver qué falla | `grep ERROR data/logs/dashboard.log` |

---

## 📚 Documentación

- [QUICKSTART.md](QUICKSTART.md) — Inicio rápido
- [INSTALL_GUIDE.md](INSTALL_GUIDE.md) — Instalación detallada
- [THEMES_GUIDE.md](THEMES_GUIDE.md) — Guía de temas
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) — Integración con OLED
- [INDEX.md](INDEX.md) — Índice completo

---

## 📊 Estadísticas del Proyecto

| Métrica | Valor |
|---------|-------|
| Versión | 3.1 |
| Archivos Python | 45 |
| Ventanas | 15 |
| Temas | 15 |
| Servicios background | 8 (FanAuto + SystemMonitor + ServiceMonitor + DataCollection + Cleanup + Homebridge + AlertService + main) |
| Badges en menú | 9 |
| Cobertura logging | 100% módulos core y UI |
| Exports organizados | 3 carpetas (csv, logs, screenshots) — máx. 10 por tipo |
| Tipos Homebridge | 5 (switch, light, thermostat, sensor, blind) |

---

## Changelog

### **v3.1** - 2026-02-26 ⭐ ACTUAL
- ✅ **NUEVO**: Alertas externas por Telegram — `AlertService` con anti-spam (edge-trigger + sustain 60s), umbrales para temp/CPU/RAM/disco y servicios, sin dependencias nuevas (urllib stdlib)
- ✅ **NUEVO**: Homebridge extendido — soporte para 5 tipos de dispositivo: switch, luz regulable, termostato, sensor temperatura/humedad, persiana
- ✅ **NUEVO**: `set_brightness()` y `set_target_temp()` en `HomebridgeMonitor`
- ✅ **NUEVO**: Tarjetas adaptativas en `HomebridgeWindow` según tipo de dispositivo
- ✅ **MEJORA**: Diálogo salir — radiobuttons táctiles (30×30px), botones ajustados, layout corregido

### **v3.0** - 2026-02-26
- ✅ **NUEVO**: Visor de Logs — ventana con filtros por nivel, módulo, texto libre e intervalo de fechas/horas
- ✅ **NUEVO**: Exportación de logs filtrados a `data/exports/logs/`
- ✅ **NUEVO**: Carpetas organizadas para exports — `data/exports/{csv,logs,screenshots}` (creadas automáticamente al arrancar)
- ✅ **MEJORA**: Limpieza automática al exportar — no solo en el ciclo de 24h o al pulsar manualmente
- ✅ **MEJORA**: `CleanupService` gestiona ahora también logs exportados (máx. 10)
- ✅ **FIX**: Eliminado `grab_set()` en `FanControlWindow` que bloqueaba el teclado en todas las ventanas al cerrarse

### **v2.9** - 2026-02-24
- ✅ **MEJORA**: `SystemMonitor` — caché en background thread (cada 2s); la UI nunca llama psutil directamente
- ✅ **MEJORA**: `ServiceMonitor` — caché en background thread (cada 10s); `is-enabled` en llamada batch en lugar de N subprocesses
- ✅ **MEJORA**: `_update()` de `MainWindow` solo lee cachés — hilo de UI completamente libre de syscalls bloqueantes
- ✅ **MEJORA**: `HomebridgeWindow` usa `CTkSwitch` (90×46px) en lugar de botones ON/OFF — más intuitivo y táctil
- ✅ **MEJORA**: `make_homebridge_switch()` añadida a `ui/styles.py` con soporte de estado disabled (fallo)
- ✅ **MEJORA**: Todos los servicios background registran inicio y parada en el log (`FanAutoService` incluido)

### **v2.8** - 2026-02-23
- ✅ **NUEVO**: Integración Homebridge — ventana de control de accesorios HomeKit (enchufes e interruptores)
- ✅ **NUEVO**: `HomebridgeMonitor` en `core/` — sondeo ligero cada 30s, autenticación JWT con renovación automática
- ✅ **NUEVO**: 3 badges Homebridge en menú principal (`hb_offline` 🔴, `hb_on` 🟠, `hb_fault` 🔴)
- ✅ **NUEVO**: Toggle táctil por dispositivo con indicador ● color y ⚠ en StatusFault
- ✅ **NUEVO**: Configuración por `.env` (credenciales fuera del código)

### **v2.7** - 2026-02-23
- ✅ **NUEVO**: Header unificado `make_window_header()` en todas las ventanas (título + status + botón ✕ táctil 52×42px)
- ✅ **NUEVO**: Status dinámico en tiempo real en el header (CPU/RAM/Temp, Disco/NVMe, interfaz/velocidades)
- ✅ **MEJORA**: Speedtest migrado a CLI oficial de Ookla (`--format=json`), resultados en MB/s reales
- ✅ **MEJORA**: Botón ✕ táctil optimizado para pantalla DSI sin teclado

### **v2.6** - 2026-02-22
- ✅ **NUEVO**: 6 badges de notificación visual en menú principal
- ✅ **NUEVO**: `CleanupService` — limpieza automática background de CSV, PNG y BD
- ✅ **NUEVO**: Fan control con entries en lugar de sliders

### v2.5.1 - 2026-02-19
- Logging completo, Ventana Actualizaciones, Fix atexit DataCollectionService

### v2.5 - 2026-02-17
- Monitor Servicios systemd, Historico SQLite, Boton Reiniciar

### v2.0 - 2026-02-16
- Monitor Procesos, 15 temas, fix Speedtest

### v1.0 - 2025-01
- Release inicial

---

## Licencia

MIT License

---

## Agradecimientos

CustomTkinter - psutil - matplotlib - Ookla Speedtest CLI - Homebridge - Raspberry Pi Foundation

---

Dashboard v3.1: Profesional, Unificado, Táctil, Auto-mantenido, conectado a HomeKit, con Alertas Telegram y sin bloqueos en UI
````

## File: main.py
````python
#!/usr/bin/env python3
"""
Sistema de Monitoreo y Control
Punto de entrada principal
"""
import sys
import os
import atexit
import threading
import customtkinter as ctk
from config import DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, UPDATE_MS
from core import (SystemMonitor, FanController, NetworkMonitor, FanAutoService, DiskMonitor, ProcessMonitor, 
                  ServiceMonitor, UpdateMonitor, CleanupService, HomebridgeMonitor, AlertService, NetworkScanner,
                  PiholeMonitor)
from core.data_collection_service import DataCollectionService
from core.data_logger import DataLogger
from ui.main_window import MainWindow
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Función principal"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    
    root = ctk.CTk()
    root.title("Sistema de Monitoreo")
    
    root.withdraw()
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.configure(bg="#111111")
    root.update_idletasks()
    root.overrideredirect(True)
    root.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
    root.update_idletasks()
    root.deiconify()
    """root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))"""
    
    # Inicializar monitores
    system_monitor = SystemMonitor()
    fan_controller = FanController()
    network_monitor = NetworkMonitor()
    disk_monitor = DiskMonitor()
    process_monitor = ProcessMonitor()
    service_monitor = ServiceMonitor()
    update_monitor = UpdateMonitor()
    homebridge_monitor = HomebridgeMonitor()
    homebridge_monitor.start()
    network_scanner = NetworkScanner()
    pihole_monitor = PiholeMonitor()
    pihole_monitor.start()

    # Comprobación inicial de actualizaciones en background
    # No bloquea el arranque y llena el caché para toda la sesión
    threading.Thread(
        target=lambda: update_monitor.check_updates(force=True),
        daemon=True,
        name="UpdateCheck-Startup"
    ).start()

    # Iniciar servicio de recolección de datos
    data_service = DataCollectionService(
        system_monitor=system_monitor,
        fan_controller=fan_controller,
        network_monitor=network_monitor,
        disk_monitor=disk_monitor,
        update_monitor=update_monitor,
        interval_minutes=5
    )
    data_service.start()
    
    # Iniciar servicio de alertas
    alert_service = AlertService(
    system_monitor=system_monitor,
    service_monitor=service_monitor,
    )
    alert_service.start()
    
    # Iniciar servicio de limpieza automática
    cleanup_service = CleanupService(
        data_logger=DataLogger(),
        max_csv=10,
        max_png=10,
        db_days=90,
        interval_hours=24,
    )
    cleanup_service.start()

    # Iniciar servicio de ventiladores AUTO
    fan_service = FanAutoService(fan_controller, system_monitor)
    fan_service.start()
    
    # Cleanup centralizado — ambos servicios aquí, ninguno en atexit interno
    def cleanup():
        """Limpieza al cerrar la aplicación"""
        fan_service.stop()
        data_service.stop()
        cleanup_service.stop()
        homebridge_monitor.stop()
        system_monitor.stop()
        service_monitor.stop()
        alert_service.stop()
        pihole_monitor.stop()
    
    atexit.register(cleanup)
    
    # Crear interfaz
    app = MainWindow(
        root,
        system_monitor=system_monitor,
        fan_controller=fan_controller,
        network_monitor=network_monitor,
        disk_monitor=disk_monitor,
        update_interval=UPDATE_MS,
        process_monitor=process_monitor,
        service_monitor=service_monitor,
        update_monitor=update_monitor,
        cleanup_service=cleanup_service,
        homebridge_monitor=homebridge_monitor,
        network_scanner=network_scanner,
        pihole_monitor=pihole_monitor,
        alert_service=alert_service,
    )

    try:
        root.mainloop()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
````

## File: ui/main_window.py
````python
"""
Ventana principal del sistema de monitoreo
"""
import tkinter as tk
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_X, DSI_Y, SCRIPTS_DIR
from ui.styles import StyleManager, make_futuristic_button
from ui.windows import (FanControlWindow, MonitorWindow, NetworkWindow, USBWindow, ProcessWindow, ServiceWindow, 
                        HistoryWindow, LaunchersWindow, ThemeSelector, DiskWindow, UpdatesWindow, HomebridgeWindow, 
                        NetworkLocalWindow, PiholeWindow, AlertHistoryWindow)
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
    
    def __init__(self, root, system_monitor, fan_controller, network_monitor,
                 disk_monitor, process_monitor, service_monitor, update_monitor, cleanup_service, homebridge_monitor, network_scanner, pihole_monitor, alert_service,
                 update_interval=2000):
        self.root = root
        self.system_monitor = system_monitor
        self.fan_controller = fan_controller
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
            ("󰚗  Monitor Placa",         self.open_monitor_window,  ["temp_monitor", "cpu", "ram"]),
            ("  Monitor Red",               self.open_network_window,  []),
            ("󱇰 Monitor USB",            self.open_usb_window,      []),
            ("  Monitor Disco",             self.open_disk_window,     ["disk"]),
            ("󱓞  Lanzadores",            self.open_launchers,       []),
            ("⚙️ Monitor Procesos",     self.open_process_window,  []),
            ("⚙️ Monitor Servicios",    self.open_service_window,  ["services"]),
            ("󱘿  Histórico Datos",       self.open_history_window,  []),
            ("󰆧  Actualizaciones",       self.open_update_window,   ["updates"]),
            ("󰟐  Homebridge",        self.open_homebridge,     ["hb_offline", "hb_on", "hb_fault"]),
            ("󰷐  Visor de Logs",        self.open_log_viewer,      []),
            ("🖧  Red Local",   self.open_network_local,   []),
            ("🕳  Pi-hole",   self.open_pihole,   ["pihole_offline"]),
            ("  Historial Alertas",  self.open_alert_history,   []),
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
            self.monitor_window = MonitorWindow(self.root, self.system_monitor)
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
````
