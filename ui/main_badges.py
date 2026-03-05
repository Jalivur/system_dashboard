"""
Gestor de badges del menu principal.

Los badges son indicadores visuales circulares superpuestos sobre los botones
del menu que muestran contadores (servicios caidos, actualizaciones pendientes)
o valores de temperatura/CPU/RAM/disco.

Uso en MainWindow:
    self._badge_mgr = BadgeManager(menu_btns=self._menu_btns)
    self._badge_mgr.create(btn, key="updates", offset_index=0)
    self._badge_mgr.update("updates", value=3)
    self._badge_mgr.update_temp("temp_fan", temp=72, color="#ff4444")
"""
import tkinter as tk
from config.settings import COLORS, FONT_FAMILY, Icons


class BadgeManager:
    """
    Crea y actualiza los badges de notificacion sobre los botones del menu.

    Cada badge es un Canvas circular flotante (place) anclado a la esquina
    superior derecha del boton padre. Multiples badges en un mismo boton se
    desplazan horizontalmente via offset_index.
    """

    _BADGE_SIZE = 36

    # Umbrales para badges de sistema
    TEMP_WARN = 60
    TEMP_CRIT = 70
    CPU_WARN  = 75
    CPU_CRIT  = 90
    RAM_WARN  = 75
    RAM_CRIT  = 90
    DISK_WARN = 80
    DISK_CRIT = 90

    def __init__(self, menu_btns: dict):
        """
        Args:
            menu_btns: referencia al dict {label → CTkButton} de MainWindow.
                       Se usa para recuperar el widget padre al recrear badges
                       tras un cambio de pestana.
        """
        self._menu_btns = menu_btns
        self._badges: dict = {}   # key → (canvas, oval, txt, x_offset)

    # ── Creación ──────────────────────────────────────────────────────────────

    def create(self, btn, key: str, offset_index: int = 0) -> None:
        """
        Crea un badge sobre btn y lo registra bajo key.
        Si ya existia un badge con esa key lo sobreescribe.

        Args:
            btn:          CTkButton padre
            key:          clave interna (ej. "updates", "temp_fan")
            offset_index: desplazamiento horizontal (0 = mas a la derecha)
        """
        size     = self._BADGE_SIZE
        x_offset = -6 - offset_index * (size + 4)

        canvas = tk.Canvas(
            btn, width=size, height=size,
            bg=COLORS['bg_dark'], highlightthickness=0, bd=0)
        canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)

        oval = canvas.create_oval(
            1, 1, size - 1, size - 1,
            fill=COLORS['danger'], outline="")
        txt = canvas.create_text(
            size // 2, size // 2,
            text="0", fill="white",
            font=(FONT_FAMILY, 13, "bold"))

        self._badges[key] = (canvas, oval, txt, x_offset)
        canvas.place_forget()

    # ── Actualización ─────────────────────────────────────────────────────────

    def update(self, key: str, value: int, color: str = None) -> None:
        """
        Muestra u oculta el badge segun value.

        Args:
            key:   clave del badge
            value: si > 0 muestra el badge; si == 0 lo oculta
            color: color de fondo opcional; si None usa danger o warning segun key
        """
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        if value > 0:
            display = str(value) if value < 100 else "99+"
            canvas.itemconfigure(txt, text=display)
            if color is None:
                color = (COLORS['danger']
                         if key == "services"
                         else COLORS.get('warning', '#ffaa00'))
            canvas.itemconfigure(oval, fill=color)
            txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
            canvas.itemconfigure(txt, fill=txt_color)
            canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)
        else:
            canvas.place_forget()

    def update_temp(self, key: str, temp: int, color: str) -> None:
        """
        Muestra el badge con valor de temperatura.

        Args:
            key:   clave del badge
            temp:  valor entero de temperatura
            color: color de fondo
        """
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        canvas.itemconfigure(txt, text=f"{temp}{Icons.DEGREE}")
        canvas.itemconfigure(oval, fill=color)
        txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
        canvas.itemconfigure(txt, fill=txt_color)
        canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)

    def hide(self, key: str) -> None:
        """Oculta el badge sin cambiar su valor."""
        if key not in self._badges:
            return
        canvas = self._badges[key][0]
        canvas.place_forget()

    def __contains__(self, key: str) -> bool:
        return key in self._badges
