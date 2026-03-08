"""
Diálogos y ventanas modales personalizadas
"""
import customtkinter as ctk
from ui.styles import make_futuristic_button
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES
import subprocess
import threading
from core.event_bus import get_event_bus


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

    console = ctk.CTkTextbox(frame, fg_color="black", text_color="#00FF00", font=("Courier New", 12))
    console.pack(fill="both", expand=True, padx=10, pady=5)

    btn_close = ctk.CTkButton(frame, text="Cerrar", state="disabled")
    btn_close.pack(pady=10)

    thread_active = threading.Event()
    thread_active.set()

    # ── Suscriptores EventBus ─────────────────────────────────────────────────

    def handle_terminal_line(data):
        try:
            c    = data.get("console")
            line = data.get("line")
            if c and line:
                c.insert("end", line)
                c.see("end")
        except Exception:
            pass

    def handle_terminal_done(data):
        try:
            btn = data.get("btn")
            if btn:
                btn.configure(state="normal")
        except Exception:
            pass

    def handle_terminal_error(data):
        try:
            error = data.get("error")
            console.insert("end", f"\n❌ Error: {error}\n")
            console.see("end")
            btn_close.configure(state="normal")
        except Exception:
            pass

    bus = get_event_bus()
    bus.subscribe("terminal.line",  handle_terminal_line)
    bus.subscribe("terminal.done",  handle_terminal_done)
    bus.subscribe("terminal.error", handle_terminal_error)

    # ── Cierre explícito — limpia suscriptores ANTES de destruir el popup ────

    def _on_close():
        # 1. Desuscribir primero — ningún evento llegará tras este punto
        bus.unsubscribe("terminal.line",  handle_terminal_line)
        bus.unsubscribe("terminal.done",  handle_terminal_done)
        bus.unsubscribe("terminal.error", handle_terminal_error)
        # 2. Esperar a que el thread del script termine (máx 2 s)
        thread_active.wait(timeout=2.0)
        # 3. Destruir popup
        try:
            popup.grab_release()
        except Exception:
            pass
        try:
            popup.destroy()
        except Exception:
            pass
        if on_close:
            on_close()

    btn_close.configure(command=_on_close)
    popup.protocol("WM_DELETE_WINDOW", _on_close)
    # Nota: NO se usa <Destroy> para limpiar — es poco fiable en CTkToplevel

    # ── Thread del script ─────────────────────────────────────────────────────

    def run_command():
        try:
            process = subprocess.Popen(
                ["bash", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for line in process.stdout:
                bus.publish("terminal.line", {"console": console, "line": line})
            process.wait()
            bus.publish("terminal.done", {"btn": btn_close})
        except Exception as e:
            bus.publish("terminal.error", {"error": str(e)})
        finally:
            thread_active.clear()

    threading.Thread(target=run_command, daemon=True).start()
    popup.grab_set()
