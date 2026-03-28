"""
Ventana de panel de red local.
Muestra los dispositivos encontrados por arp-scan con IP, MAC, fabricante y hostname.
"""
import customtkinter as ctk
from config.settings import (
    COLORS, FONT_FAMILY, FONT_SIZES,
    DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y
, Icons)
from ui.styles import make_window_header, make_futuristic_button, StyleManager
from utils.logger import get_logger

logger = get_logger(__name__)

# Refresco automático cada N segundos (0 = desactivado)
AUTO_REFRESH_S = 60


class NetworkLocalWindow(ctk.CTkToplevel):
    """
    Ventana emergente que muestra dispositivos detectados en la red local.

    Args:
        parent: Ventana principal padre de esta ventana.
        network_scanner: Instancia del escáner de red externa para obtener dispositivos.

    Raises:
        None

    Returns:
        None
    """

    def __init__(self, parent, network_scanner):  # ── MODIFICADO: recibe scanner ──
        """
        Inicializa y configura la ventana emergente del panel de red local.

        Esta ventana muestra dispositivos detectados en la red mediante arp-scan,
        mostrando IP, MAC, fabricante y hostname.

        Args:
            parent: Ventana principal (CTkToplevel) padre de esta ventana.
            network_scanner: Instancia del escáner de red externa para obtener dispositivos.

        """
        super().__init__(parent)
        self._scanner     = network_scanner  # ── MODIFICADO: usa el scanner externo ──
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
        """
        Construye toda la interfaz de usuario de la ventana.

        Crea los componentes visuales principales, incluyendo el encabezado con título y 
        controles de ventana, un área scrollable para la lista de dispositivos y un 
        frame inferior con funcionalidades adicionales.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
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
        """
        Inicia el proceso de escaneo de la red y activa la verificación periódica de resultados.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        # ── guard: servicio detenido ──────────────────────────────────────────
        if not self._scanner.is_running():
            StyleManager.show_service_stopped_banner(self._device_frame, "Escáner de Red")
            self._header.status_label.configure(text="Servicio detenido")
            self._scan_btn.configure(state="disabled")
            return

        # ── si estaba con banner, limpiar y reactivar botón ──────────────────
        self._scan_btn.configure(state="normal", text="⟳  Escanear")

        if self._scanner.get_status() == "scanning":
            return
        self._scan_btn.configure(state="disabled", text="Escaneando...")
        self._header.status_label.configure(text="Escaneando red...")
        self._scanner.scan()
        self._poll_result()

    def _poll_result(self):
        """
        Verifica periódicamente el estado del escaneo y actualiza la interfaz gráfica accordingly.

        Args: 
            None

        Returns: 
            None

        Raises: 
            None
        """
        # Si el servicio se paró durante el escaneo, mostrar banner
        if not self._scanner.is_running():
            self._start_scan()  # redirige al banner
            return

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
        """
        Redibuja la lista con los dispositivos encontrados en la red local.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        status  = self._scanner.get_status()
        devices = self._scanner.get_devices()

        # Limpiar lista anterior
        for w in self._device_frame.winfo_children():
            w.destroy()

        if status == "error":
            error_msg = self._scanner.get_error()
            ctk.CTkLabel(
                self._device_frame,
                text=f"{Icons.WARNING} Error en el escaneo:\n{error_msg}",
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
        """
        Crea una fila que representa un dispositivo en la interfaz gráfica.

        Args:
            device (dict): Diccionario que contiene la información del dispositivo, incluyendo 'ip', 'hostname' y 'MAC' (aunque este último no se utiliza en este método).

        Returns:
            None

        Raises:
            None
        """
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
        """
        Gestiona el cierre ordenado de la ventana.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        if self._auto_job:
            self.after_cancel(self._auto_job)
        if self._poll_job:
            self.after_cancel(self._poll_job)
        logger.info("[NetworkLocalWindow] Ventana cerrada")
        self.destroy()
