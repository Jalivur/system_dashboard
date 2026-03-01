"""
Ventana de gestión total de servicios background del Dashboard.

Permite parar y arrancar cada servicio de forma manual y completa.
Cuando un servicio está parado:
  - Su thread interno no corre
  - Sus métodos de acción devuelven sin hacer nada (ver parches en core/)
  - Las ventanas asociadas muestran aviso "Servicio detenido"
"""
import threading
import tkinter as tk
import customtkinter as ctk
from config.settings import (COLORS, FONT_FAMILY, FONT_SIZES,
                              DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y)
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from ui.widgets import confirm_dialog
from utils.logger import get_logger

logger = get_logger(__name__)

_REFRESH_MS = 1500


class ServicesManagerWindow(ctk.CTkToplevel):
    """Manager total de servicios del dashboard."""

    _DEFINITIONS = [
        ("system_monitor",
         "System Monitor", "🖥️",
         "CPU, RAM y temperatura dejarán de actualizarse en todas las ventanas."),
        ("disk_monitor",
         "Disk Monitor", " ",
         "Uso de disco, lectura y escritura, temperatura y smart dejaran de actualizarse."),
        ("hardware_monitor",
         "Hardware Monitor", "🌡️",
         "Temperatura del chasis y fan duty real dejarán de leerse."),
        ("network_monitor",                                          
         "Network Monitor", "🌐",
         "El tráfico de red dejará de monitorizarse y el speedtest quedará desactivado."),
        ("network_scanner",                                         
         "Network Scanner", "🌐",
         "Escaneo de red Local quedara desactivado."),
        ("process_monitor",
         "Process Monitor", "⚙️",
         "El estado de los Procesos activos no se actualizará."),
        ("service_monitor",
         "Service Monitor", "⚙️",
         "El estado de los servicios systemd no se actualizará."),
        ("alert_service",
         "Alert Service (Telegram)", "📲",
         "Las alertas por Telegram quedarán desactivadas."),
        ("audio_alert_service",
         "Audio Alert Service", "🔊",
         "Las alertas de audio quedarán desactivadas."),
        ("homebridge_monitor",
         "Homebridge Monitor", "🏠",
         "Homebridge dejará de sondearse y los controles quedarán bloqueados."),
        ("pihole_monitor",
         "Pi-hole Monitor", "🕳️",
         "Pi-hole dejará de sondearse. Los datos mostrados quedarán en cero."),
        ("vpn_monitor",
         "VPN Monitor", "🔒",
         "El estado de la VPN no se actualizará."),
        ("data_service",
         "Data Collection", "📊",
         "No se guardarán datos en el histórico mientras esté parado."),
        ("cleanup_service",
         "Cleanup Service", "🧹",
         "La limpieza automática de exports y BD quedará pausada."),
    ]

    def __init__(self, parent, **services):
        super().__init__(parent)
        self.title("Gestión de Servicios")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)
        self.lift()

        self._services: dict = {k: v for k, v in services.items() if v is not None}
        self._defs = [(k, lbl, emj, warn)
                      for k, lbl, emj, warn in self._DEFINITIONS
                      if k in self._services]
        self._rows: dict = {}
        self._busy: set  = set()

        self._create_ui()
        self._refresh_loop()
        logger.info("[ServicesManagerWindow] Ventana abierta")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _create_ui(self):

        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="GESTIÓN DE SERVICIOS", on_close=self.destroy)

        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(scroll_container, orientation="vertical",
                                     command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=inner, anchor="nw", width=DSI_WIDTH - 50)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Cabecera columnas
        hdr = ctk.CTkFrame(inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        hdr.pack(fill="x", padx=8, pady=(6, 4))
        hdr.grid_columnconfigure(1, weight=1)
        for col, text in enumerate(["", "Servicio", "Estado", ""]):
            ctk.CTkLabel(hdr, text=text,
                         font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                         text_color=COLORS['text_dim'],
                         ).grid(row=0, column=col, padx=(12, 4), pady=6, sticky="w")

        for key, label, emoji, warn in self._defs:
            self._create_row(inner, key, label, emoji, warn)

        # Botones globales
        footer = ctk.CTkFrame(inner, fg_color="transparent")
        footer.pack(fill="x", padx=8, pady=(8, 6))
        make_futuristic_button(footer, text="⏹  Parar todos",
                               command=self._stop_all,
                               width=14, height=6, font_size=13,
                               ).pack(side="left", padx=(0, 8))
        make_futuristic_button(footer, text="▶  Iniciar todos",
                               command=self._start_all,
                               width=14, height=6, font_size=13,
                               ).pack(side="left")

    def _create_row(self, parent, key, label, emoji, warn):
        row_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_dark'], corner_radius=8)
        row_frame.pack(fill="x", padx=8, pady=3)
        row_frame.grid_columnconfigure(1, weight=1)

        IND = 14
        ind_canvas = tk.Canvas(row_frame, width=IND, height=IND,
                               bg=COLORS['bg_dark'], highlightthickness=0, bd=0)
        ind_canvas.grid(row=0, column=0, padx=(12, 6), pady=14)
        oval = ind_canvas.create_oval(1, 1, IND - 1, IND - 1,
                                      fill=COLORS['text_dim'], outline="")

        ctk.CTkLabel(row_frame,
                     text=f"{emoji}  {label}",
                     font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
                     text_color=COLORS['text'], anchor="w",
                     ).grid(row=0, column=1, padx=(4, 8), pady=12, sticky="w")

        lbl_status = ctk.CTkLabel(row_frame, text="…",
                                  font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                                  text_color=COLORS['text_dim'],
                                  width=80, anchor="center")
        lbl_status.grid(row=0, column=2, padx=4, pady=12)

        btn = make_futuristic_button(row_frame, text="",
                                     command=lambda k=key, w=warn: self._toggle(k, w),
                                     width=12, height=6, font_size=13)
        btn.grid(row=0, column=3, padx=(4, 12), pady=8)

        self._rows[key] = {"canvas": ind_canvas, "oval": oval,
                           "lbl_status": lbl_status, "btn": btn}

    # ── Estado ────────────────────────────────────────────────────────────────

    def _is_running(self, key: str) -> bool:
        svc = self._services.get(key)
        if svc is None:
            return False
        if hasattr(svc, "is_running"):
            return svc.is_running()
        return getattr(svc, "_running", False)

    def _update_row(self, key: str):
        if key not in self._rows:
            return
        row  = self._rows[key]
        busy = key in self._busy
        if busy:
            row["lbl_status"].configure(text="…", text_color=COLORS['text_dim'])
            row["canvas"].itemconfigure(row["oval"], fill=COLORS['text_dim'])
            row["btn"].configure(state="disabled", text="…")
            return
        running = self._is_running(key)
        color   = COLORS['primary'] if running else COLORS['danger']
        row["canvas"].itemconfigure(row["oval"], fill=color)
        row["lbl_status"].configure(
            text="ACTIVO" if running else "PARADO", text_color=color)
        row["btn"].configure(
            state="normal",
            text="⏹ Parar"  if running else "▶ Iniciar",
            fg_color=COLORS['danger'] if running else COLORS['primary'])

    def _refresh_loop(self):
        if not self.winfo_exists():
            return
        for key in self._rows:
            self._update_row(key)
        self.after(_REFRESH_MS, self._refresh_loop)

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _toggle(self, key: str, warn: str):
        if key in self._busy:
            return
        running = self._is_running(key)
        action  = "parar" if running else "arrancar"
        msg     = f"¿Seguro que quieres {action} «{key}»?"
        if running and warn:
            msg += f"\n\n⚠️  {warn}"
        confirm_dialog(parent=self, text=msg,
                       on_confirm=lambda: self._execute(key, stop=running))

    def _execute(self, key: str, stop: bool):
        self._busy.add(key)
        self._update_row(key)

        def _run():
            svc = self._services[key]
            try:
                if stop:
                    logger.info("[ServicesManagerWindow] stop → %s", key)
                    svc.stop()
                else:
                    logger.info("[ServicesManagerWindow] start → %s", key)
                    svc.start()
            except Exception as e:
                logger.error("[ServicesManagerWindow] Error %s %s: %s",
                             "stop" if stop else "start", key, e)
            finally:
                self._busy.discard(key)
                if self.winfo_exists():
                    self.after(0, self._update_row, key)

        threading.Thread(target=_run, daemon=True,
                         name=f"SvcMgr-{key}").start()

    def _stop_all(self):
        keys = [k for k in self._rows if self._is_running(k)]
        if not keys:
            return
        names = "\n".join(f"  • {k}" for k in keys)
        confirm_dialog(
            parent=self,
            text=f"⚠️  Esto parará {len(keys)} servicios:\n\n{names}\n\n¿Continuar?",
            on_confirm=lambda: [self._execute(k, stop=True) for k in keys])

    def _start_all(self):
        keys = [k for k in self._rows if not self._is_running(k)]
        if not keys:
            return
        confirm_dialog(
            parent=self,
            text=f"¿Arrancar los {len(keys)} servicios parados?",
            on_confirm=lambda: [self._execute(k, stop=False) for k in keys])
