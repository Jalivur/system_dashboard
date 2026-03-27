"""
Ventana de monitor de sesiones SSH.
Muestra sesiones activas (who) e historial de conexiones (last).
Se refresca automáticamente cada 30 segundos via SSHMonitor.
Los widgets se crean una sola vez — solo se actualizan los valores.
"""
import re
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger

logger = get_logger(__name__)

_REFRESH_MS = 30_000


# ── Helpers de formato ────────────────────────────────────────────────────────

def _fmt_tty(raw: str) -> str:
    """pts/0 → Sesión 1 · tty1 → Consola local"""
    if not raw:
        return ""
    if raw.startswith("pts/"):
        try:
            n = int(raw.split("/")[1]) + 1
            return f"Sesión {n}"
        except (IndexError, ValueError):
            return raw
    if raw.startswith("tty"):
        return "Consola local"
    return raw


def _fmt_ip(raw: str) -> str:
    """192.168.x.x → 192.168.x.x (local) · vacío → Consola local"""
    if not raw:
        return "Consola local"
    if raw.startswith("192.168.") or raw.startswith("10.") or raw.startswith("172."):
        return f"{raw}  (red local)"
    return raw


def _fmt_time_active(date: str, time: str) -> str:
    """2026-03-04 10:22 → Conectado desde las 10:22"""
    if not time:
        return ""
    if date:
        return f"Conectado desde las {time}  ({date})"
    return f"Conectado desde las {time}"


def _fmt_time_history(raw: str) -> str:
    """
    Transforma la cadena de time_info del historial en algo legible.
    Ejemplos de entrada:
        'Tue Mar  4 10:22   still logged in'
        'Mon Mar  3 21:10 - 21:45  (00:35)'
        'Mon Mar  3 09:00 - crash'
        'Mon Mar  3 09:00 - down'
    """
    if not raw:
        return ""

    raw = raw.strip()

    # Detectar sesión activa
    if "still logged in" in raw:
        # Extraer hora de inicio
        m = re.search(r'(\d{2}:\d{2})', raw)
        hora = m.group(1) if m else ""
        return f"Activa desde las {hora}" if hora else "Activa"

    # Detectar cierre por crash o apagado
    if "crash" in raw:
        m = re.search(r'(\d{2}:\d{2})', raw)
        hora = m.group(1) if m else ""
        return f"Cortada por crash  ({hora})" if hora else "Cortada por crash"
    if "down" in raw:
        m = re.search(r'(\d{2}:\d{2})', raw)
        hora = m.group(1) if m else ""
        return f"Cortada por apagado  ({hora})" if hora else "Cortada por apagado"

    # Formato normal: hora_inicio - hora_fin  (duración)
    # Extraer duración entre paréntesis
    m_dur = re.search(r'\((\d{2}:\d{2})\)', raw)
    dur = m_dur.group(1) if m_dur else None

    # Extraer horas de inicio y fin
    horas = re.findall(r'(\d{2}:\d{2})', raw)

    if len(horas) >= 2:
        inicio, fin = horas[0], horas[1]
        if dur:
            h, m2 = dur.split(":")
            if h == "00":
                dur_str = f"{int(m2)} min"
            else:
                dur_str = f"{int(h)}h {int(m2)}min"
            return f"{inicio} → {fin}  ({dur_str})"
        return f"{inicio} → {fin}"
    elif len(horas) == 1:
        return f"Desde las {horas[0]}"

    return raw


# ── Ventana ───────────────────────────────────────────────────────────────────

class SSHWindow(ctk.CTkToplevel):
    """Ventana de monitor de sesiones SSH."""

    def __init__(self, parent, ssh_monitor):
        """Inicializa la ventana de monitor SSH.

        Args:
            parent: Ventana padre (CTkToplevel).
            ssh_monitor: Instancia de SSHMonitor para obtener estadísticas en tiempo real.
        """
        super().__init__(parent)
        self._ssh_monitor = ssh_monitor

        self.title("Monitor SSH")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._refresh_job = None

        # Referencias a widgets que se actualizan sin recrearse
        self._session_rows:  list = []
        self._history_rows:  list = []
        self._session_badge: ctk.CTkLabel = None
        self._session_empty: ctk.CTkLabel = None
        self._history_empty: ctk.CTkLabel = None

        self._create_ui()
        self.after(100, self._update)
        logger.info("[SSHWindow] Ventana abierta")

    # ── Construcción UI (una sola vez) ────────────────────────────────────────

    def _create_ui(self):
        """Crea toda la interfaz de usuario una sola vez al inicializar la ventana.

        Incluye header, scrollable canvas, tarjetas de sesiones e historial,
        y barra de controles con botón de actualización manual.
        """
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])

        main.pack(fill="both", expand=True, padx=5, pady=5)

        self._header = make_window_header(
            main, title="MONITOR SSH",
            on_close=self._on_close,
            status_text="Cargando...",
        )

        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=5, pady=5)

        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        sb = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        sb.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(sb)
        canvas.configure(yscrollcommand=sb.set)

        self._inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window(
            (0, 0), window=self._inner,
            anchor="nw", width=DSI_WIDTH - 50)
        self._inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self._build_sessions_card()
        self._build_history_card()

        bar = ctk.CTkFrame(main, fg_color="transparent")
        bar.pack(fill="x", padx=5, pady=(0, 4))

        self._update_label = ctk.CTkLabel(
            bar, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'])
        self._update_label.pack(side="left", padx=8)

        make_futuristic_button(
            bar, text="↺ Actualizar", command=self._force_refresh,
            width=12, height=5, font_size=14
        ).pack(side="right", padx=4)

    def _build_sessions_card(self):
        """Crea la tarjeta de sesiones activas con filas fijas (máximo 10)."""
        MAX_SESSIONS = 10

        card = ctk.CTkFrame(self._inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(6, 4))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            hdr,
            text="SESIONES ACTIVAS",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(side="left")

        self._session_badge = ctk.CTkLabel(
            hdr, text="Ninguna",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['text_dim'],
            anchor="e")
        self._session_badge.pack(side="right", padx=4)

        ctk.CTkFrame(
            card, fg_color=COLORS['border'], height=1, corner_radius=0
        ).pack(fill="x", padx=14, pady=(0, 4))

        self._session_empty = ctk.CTkLabel(
            card,
            text="No hay sesiones SSH abiertas",
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text_dim'])
        self._session_empty.pack(pady=(4, 10))
        self._session_empty.pack_forget()

        for _ in range(MAX_SESSIONS):
            row = ctk.CTkFrame(card, fg_color=COLORS['bg_medium'], corner_radius=6)

            left = ctk.CTkFrame(row, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            lbl_user = ctk.CTkLabel(
                left, text="",
                font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
                text_color=COLORS['primary'], anchor="w")
            lbl_user.pack(fill="x")

            lbl_tty = ctk.CTkLabel(
                left, text="",
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'], anchor="w")
            lbl_tty.pack(fill="x")

            right = ctk.CTkFrame(row, fg_color="transparent")
            right.pack(side="right", padx=10, pady=8)

            lbl_ip = ctk.CTkLabel(
                right, text="",
                font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
                text_color=COLORS['primary'], anchor="e")
            lbl_ip.pack(anchor="e")

            lbl_time = ctk.CTkLabel(
                right, text="",
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'], anchor="e")
            lbl_time.pack(anchor="e")

            self._session_rows.append({
                "row": row, "user": lbl_user,
                "tty": lbl_tty, "ip": lbl_ip, "time": lbl_time,
            })

        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

    def _build_history_card(self):
        """Crea la tarjeta de historial con filas fijas (50 entradas)."""
        MAX_HISTORY = 50

        card = ctk.CTkFrame(self._inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        card.pack(fill="x", padx=10, pady=(4, 6))

        ctk.CTkLabel(
            card,
            text="HISTORIAL DE CONEXIONES",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
            anchor="w",
        ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkFrame(
            card, fg_color=COLORS['border'], height=1, corner_radius=0
        ).pack(fill="x", padx=14, pady=(0, 4))

        self._history_empty = ctk.CTkLabel(
            card,
            text="Sin historial disponible",
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text_dim'])
        self._history_empty.pack(pady=(4, 10))
        self._history_empty.pack_forget()

        for i in range(MAX_HISTORY):
            bg = COLORS['bg_medium'] if i % 2 == 0 else COLORS['bg_dark']
            row = ctk.CTkFrame(card, fg_color=bg, corner_radius=4)

            left = ctk.CTkFrame(row, fg_color="transparent")
            left.pack(side="left", padx=10, pady=6)

            lbl_user = ctk.CTkLabel(
                left, text="",
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                text_color=COLORS['text'], anchor="w", width=100)
            lbl_user.pack(side="left")

            lbl_tty = ctk.CTkLabel(
                left, text="",
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'], anchor="w", width=90)
            lbl_tty.pack(side="left", padx=(8, 0))

            lbl_ip = ctk.CTkLabel(
                left, text="",
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['primary'], anchor="w", width=160)
            lbl_ip.pack(side="left", padx=(8, 0))

            lbl_time = ctk.CTkLabel(
                row, text="",
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=COLORS['text_dim'], anchor="e", wraplength=200)
            lbl_time.pack(side="right", padx=10, pady=6)

            self._history_rows.append({
                "row": row, "user": lbl_user,
                "tty": lbl_tty, "ip": lbl_ip, "time": lbl_time,
            })

        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

    # ── Actualización de valores (sin recrear widgets) ─────────────────────────

    def _update(self):
        """Actualiza los datos visuales de sesiones activas e historial de conexiones.

        Obtiene estadísticas del SSHMonitor, refresca widgets sin recrearlos,
        maneja estado parado del monitor, y programa la próxima actualización
        cada 30 segundos.

        Returns:
            None
        """
        if not self.winfo_exists():

            return
        if not self._ssh_monitor.is_running():
            StyleManager.show_service_stopped_banner(self._inner, "SSH Monitor")
            return
        stats    = self._ssh_monitor.get_stats()
        sessions = stats["sessions"]
        history  = stats["history"]
        ts       = stats["last_update"]

        self._refresh_sessions(sessions)
        self._refresh_history(history)

        n = len(sessions)
        self._header.status_label.configure(
            text=f"{n} sesión{'es' if n != 1 else ''} activa{'s' if n != 1 else ''}")
        self._update_label.configure(
            text=f"Actualizado: {ts}" if ts else "")

        self._refresh_job = self.after(_REFRESH_MS, self._update)

    def _refresh_sessions(self, sessions: list):
        """Refresca la visualización de las sesiones SSH activas actuales.

        Muestra hasta 10 filas; oculta filas extras y mensaje 'Ninguna' si vacío.
        Actualiza badges de conteo y colores de estado.

        Args:
            sessions: Lista de dicts con claves 'user', 'tty', 'ip' (opcional),
                      'date' (opcional), 'time'.
        """
        n = len(sessions)


        if n == 0:
            self._session_badge.configure(
                text="Ninguna", text_color=COLORS['text_dim'])
            self._session_empty.pack(pady=(4, 10))
        else:
            self._session_badge.configure(
                text=f"{n} activa{'s' if n != 1 else ''}",
                text_color=COLORS['danger'])
            self._session_empty.pack_forget()

        for i, widgets in enumerate(self._session_rows):
            if i < n:
                s = sessions[i]
                widgets["user"].configure(text=s["user"])
                widgets["tty"].configure(text=_fmt_tty(s["tty"]))
                widgets["ip"].configure(text=_fmt_ip(s.get("ip", "")))
                widgets["time"].configure(
                    text=_fmt_time_active(s.get("date", ""), s.get("time", "")))
                widgets["row"].pack(fill="x", padx=10, pady=3)
            else:
                widgets["row"].pack_forget()

    def _refresh_history(self, history: list):
        """Refresca la visualización del historial reciente de conexiones SSH.

        Muestra hasta 50 entradas con colores alternos; oculta extras si vacío.

        Args:
            history: Lista de dicts con claves 'user', 'tty', 'ip' (opcional),
                     'time_info' (cadena con detalles de tiempo).
        """
        n = len(history)

        if n == 0:
            self._history_empty.pack(pady=(4, 10))
        else:
            self._history_empty.pack_forget()

        for i, widgets in enumerate(self._history_rows):
            if i < n:
                e = history[i]
                widgets["user"].configure(text=e["user"])
                widgets["tty"].configure(text=_fmt_tty(e["tty"]))
                widgets["ip"].configure(text=_fmt_ip(e.get("ip", "")))
                widgets["time"].configure(text=_fmt_time_history(e.get("time_info", "")))
                widgets["row"].pack(fill="x", padx=10, pady=1)
            else:
                widgets["row"].pack_forget()

    def _force_refresh(self):
        """Fuerza una actualización inmediata de todos los datos SSH.

        Cancela el job automático pendiente y llama a _update directamente.
        """
        if self._refresh_job:

            self.after_cancel(self._refresh_job)
        self._update()

    # ── Cierre ────────────────────────────────────────────────────────────────

    def _on_close(self):
        """Limpia recursos y cierra la ventana de forma segura.

        Cancela jobs de refresco pendientes y registra cierre en logger.
        """
        if self._refresh_job:

            self.after_cancel(self._refresh_job)
        logger.info("[SSHWindow] Ventana cerrada")
        self.destroy()
