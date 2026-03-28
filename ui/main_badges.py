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
    Administrador de badges de notificación para botones del menú.

    Args:
        menu_btns (dict): Diccionario de botones del menú {etiqueta → CTkButton}.

    Nota: Utiliza este diccionario para obtener el widget padre y recrear los badges 
          después de un cambio de pestaña.
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
        Inicializa el administrador de insignias con una referencia a los botones del menú.

        Args:
            menu_btns (dict): Diccionario de botones del menú donde cada clave es una etiqueta y cada valor es un CTkButton.

        """
        self._menu_btns = menu_btns
        self._badges: dict = {}   # key → (canvas, oval, txt, x_offset)

    # ── Creación ──────────────────────────────────────────────────────────────

    def create(self, btn, key: str, offset_index: int = 0) -> None:
        """
        Crea un badge sobre un botón y lo registra bajo una clave específica.

        Args:
            btn: CTkButton padre sobre el que se creará el badge.
            key (str): Clave interna para registrar el badge (ej. "updates", "temp_fan").
            offset_index (int): Desplazamiento horizontal del badge (0 = más a la derecha). Por defecto es 0.

        Returns:
            None

        Raises:
            None
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
        Actualiza la visualización de un badge según su valor.

        Args:
            key (str): Clave del badge a actualizar.
            value (int): Valor del badge; mayor que 0 lo muestra, igual a 0 lo oculta.
            color (str, opcional): Color de fondo del badge; si no se proporciona, se usa danger o warning según la clave.

        Returns:
            None

        Raises:
            Ninguna excepción específica.
        """
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        try:
            if not canvas.winfo_exists():
                return
        except Exception:
            return
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
        Actualiza el valor de temperatura de un badge existente.

        Args:
            key (str): Clave del badge a actualizar.
            temp (int): Nuevo valor de temperatura.
            color (str): Color de fondo del badge.

        Returns:
            None

        Raises:
            None
        """
        if key not in self._badges:
            return
        canvas, oval, txt, x_offset = self._badges[key]
        try:
            if not canvas.winfo_exists():
                return
        except Exception:
            return
        canvas.itemconfigure(txt, text=f"{temp}{Icons.DEGREE}")
        canvas.itemconfigure(oval, fill=color)
        txt_color = "black" if color == COLORS.get('warning', '#ffaa00') else "white"
        canvas.itemconfigure(txt, fill=txt_color)
        canvas.place(relx=1.0, rely=0.0, anchor="ne", x=x_offset, y=6)

    def hide(self, key: str) -> None:
        """
        Oculta el badge asociado a la clave dada sin modificar su valor.

        Args:
            key (str): Clave del badge a ocultar.

        Returns:
            None

        Raises:
            None
        """
        if key not in self._badges:
            return
        canvas = self._badges[key][0]
        try:
            if not canvas.winfo_exists():
                return
        except Exception:
            return
        canvas.place_forget()

    def __contains__(self, key: str) -> bool:
        """
        Determina si existe un badge con la clave dada.

        Args:
            key (str): Clave a verificar

        Returns:
            bool: True si existe el badge, False en caso contrario
        """
        return key in self._badges
