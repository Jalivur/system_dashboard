"""
Gestor del ciclo de vida de las ventanas hijas del dashboard.

Encapsula el patron repetido en MainWindow:
  - Comprobar si la ventana existe (winfo_exists)
  - Crearla via factory si no existe, o hacer lift si ya esta abierta
  - Gestionar _btn_active / _btn_idle al abrir y al cerrar

Uso en MainWindow:
    self._wlm = WindowLifecycleManager(
        on_btn_active=self._btn_active,
        on_btn_idle=self._btn_idle,
    )
    self._wlm.register("fan_control", BL.FAN_CONTROL,
        factory=lambda: FanControlWindow(self.root, self.fan_controller, ...),
        badge_keys=["temp_fan"],
    )
    # En _build_buttons_meta:
    BL.FAN_CONTROL: (lambda: self._wlm.open("fan_control"), ["temp_fan"])

    # Para ButtonManagerWindow (necesita la instancia):
    self._wlm.open("button_manager")
    instance = self._wlm.get("button_manager")
"""
from utils.logger import get_logger

logger = get_logger(__name__)


class WindowLifecycleManager:
    """
    Gestiona el ciclo de vida de ventanas hijas, permitiendo su creación, activación y cierre.

    Args:
        on_btn_active : función a llamar cuando un botón de ventana se activa
        on_btn_idle   : función a llamar cuando un botón de ventana se inactiva

    Raises:
        No se documentan excepciones en esta clase.

    Returns:
        No se documenta retorno en esta clase.
    """

    def __init__(self, on_btn_active, on_btn_idle):
        """
        Inicializa el administrador del ciclo de vida de la ventana.

        Args:
            on_btn_active (callable): Función que se llama cuando un botón está activo, recibe una etiqueta como parámetro.
            on_btn_idle (callable): Función que se llama cuando un botón está inactivo, recibe una etiqueta como parámetro.
        """
        self._on_active  = on_btn_active
        self._on_idle    = on_btn_idle
        self._registry   = {}   # key → {label, factory, badge_keys, instance}

    # ── Registro ──────────────────────────────────────────────────────────────

    def register(self, key: str, label: str, factory, badge_keys=None) -> None:
        """
        Registra una ventana hija con su información asociada.

        Args:
            key (str): Identificador único de la ventana.
            label (str): Etiqueta o constante asociada al botón de la ventana.
            factory (callable): Función que crea una instancia de CTkToplevel.
            badge_keys (list[str], opcional): Lista de claves de badge. Por defecto es None.

        Returns:
            None

        Raises:
            Ninguna excepción específica.
        """
        self._registry[key] = {
            "label":      label,
            "factory":    factory,
            "badge_keys": badge_keys or [],
            "instance":   None,
        }

    # ── Apertura ──────────────────────────────────────────────────────────────

    def open(self, key: str) -> None:
        """
        Abre la ventana registrada bajo la clave proporcionada.

        Args:
            key (str): La clave de la ventana a abrir.

        Returns:
            None

        Raises:
            None
        """
        entry = self._registry.get(key)
        if entry is None:
            logger.error("[WindowLifecycleManager] Clave no registrada: '%s'", key)
            return

        instance = entry["instance"]
        if instance is not None and instance.winfo_exists():
            instance.lift()
            return

        logger.debug("[WindowLifecycleManager] Abriendo: %s", key)
        label = entry["label"]
        self._on_active(label)

        win = entry["factory"]()
        entry["instance"] = win

        win.bind("<Destroy>", lambda e, k=key, l=label: self._on_close(k, l))

    # ── Consulta ──────────────────────────────────────────────────────────────

    def get(self, key: str):
        """
        Recupera la instancia activa de una ventana registrada.

        Args:
            key (str): La clave de registro de la ventana.

        Returns:
            La instancia activa de la ventana, o None si no existe o no está activa.
        """
        entry = self._registry.get(key)
        if entry is None:
            return None
        instance = entry["instance"]
        if instance is not None and instance.winfo_exists():
            return instance
        return None

    def is_open(self, key: str) -> bool:
        """
        Indica si una ventana específica está actualmente abierta.

        Args:
            key (str): Identificador de la ventana.

        Returns:
            bool: True si la ventana está abierta, False en caso contrario.
        """
        return self.get(key) is not None

    # ── Callbacks internos ────────────────────────────────────────────────────

    def _on_close(self, key: str, label: str) -> None:
        """
        Limpia la instancia y el botón asociado cuando una ventana es cerrada.

        Args:
            key (str): Clave de registro de la ventana.
            label (str): Etiqueta de la ventana.

        Returns:
            None

        Raises:
            None
        """
        entry = self._registry.get(key)
        if entry is not None:
            entry["instance"] = None
        self._on_idle(label)
