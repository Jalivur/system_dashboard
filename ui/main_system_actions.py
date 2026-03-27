"""
Acciones de sistema del dashboard: salir y reiniciar.

Separado de MainWindow para mantener main_window.py enfocado en UI.
Las funciones reciben el root y los dialogos necesarios como parametros
— sin acoplamiento a MainWindow mas alla de lo imprescindible.

Uso en MainWindow:
    from ui.main_system_actions import exit_application, restart_application

    # En _create_ui footer:
    make_futuristic_button(..., command=lambda: exit_application(self.root, self._update_loop))
    make_futuristic_button(..., command=lambda: restart_application(self.root, self._update_loop))
"""
import sys
import os
import customtkinter as ctk
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_X, DSI_Y, SCRIPTS_DIR, Icons
from ui.styles import StyleManager, make_futuristic_button
from ui.widgets import confirm_dialog, terminal_dialog
from utils.logger import get_logger

logger = get_logger(__name__)


def exit_application(root, update_loop=None) -> None:
    """
    Muestra el dialogo de opciones de salida (salir / apagar sistema).

    Args:
        root:        ventana Tk raiz del dashboard
        update_loop: instancia de UpdateLoop (se detiene antes de destroy)
    """
    selection_window = ctk.CTkToplevel(root)
    selection_window.title("Opciones de Salida")
    selection_window.configure(fg_color=COLORS['bg_medium'])
    selection_window.geometry("450x280")
    selection_window.resizable(False, False)
    selection_window.overrideredirect(True)
    selection_window.update_idletasks()
    x = DSI_X + (450 // 2) - 40
    y = DSI_Y + (280 // 2) - 40
    selection_window.geometry(f"450x280+{x}+{y}")
    selection_window.transient(root)
    selection_window.after(150, selection_window.focus_set)

    main_frame = ctk.CTkFrame(selection_window, fg_color=COLORS['bg_medium'])
    main_frame.pack(fill="both", expand=True, padx=20, pady=5)

    ctk.CTkLabel(
        main_frame,
        text=f"{Icons.WARNING} ¿Qué deseas hacer?",
        text_color=COLORS['secondary'],
        font=(FONT_FAMILY, FONT_SIZES['xlarge'], "bold"),
    ).pack(pady=(10, 10))

    selection_var = ctk.StringVar(master=root, value="exit")
    options_frame = ctk.CTkFrame(main_frame, fg_color=COLORS['bg_dark'])
    options_frame.pack(fill="x", pady=5, padx=20)

    exit_radio = ctk.CTkRadioButton(
        options_frame, text="  Salir de la aplicación",
        variable=selection_var, value="exit",
        text_color=COLORS['text'], font=(FONT_FAMILY, FONT_SIZES['medium']))
    exit_radio.pack(anchor="w", padx=20, pady=12)

    shutdown_radio = ctk.CTkRadioButton(
        options_frame, text=f"{Icons.POWER_OFF}  Apagar el sistema",
        variable=selection_var, value="shutdown",
        text_color=COLORS['text'], font=(FONT_FAMILY, FONT_SIZES['medium']))
    shutdown_radio.pack(anchor="w", padx=20, pady=12)

    StyleManager.style_radiobutton_ctk(exit_radio,     radiobutton_width=30, radiobutton_height=30)
    StyleManager.style_radiobutton_ctk(shutdown_radio, radiobutton_width=30, radiobutton_height=30)

    buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    buttons_frame.pack(side="bottom", fill="x", pady=(5, 10))

    def on_confirm():
        """
        Maneja confirmación de selección de salida/apagado
        """
        selected = selection_var.get()
        selection_window.grab_release()
        selection_window.destroy()
        if selected == "exit":
            def do_exit():
                """
                Confirma y cierra la aplicación
                """
                logger.info("[SystemActions] Cerrando dashboard por solicitud del usuario")
                # Detener el UpdateLoop antes de destruir — evita after() huérfanos
                if update_loop is not None:
                    update_loop.stop()
                root.quit()
                root.destroy()
            confirm_dialog(
                parent=root,
                text="¿Confirmar salir de la aplicación?",
                title=" Confirmar Salida",
                on_confirm=do_exit, on_cancel=None)
        else:
            def do_shutdown():
                """
                Confirma y ejecuta apagado del sistema
                """
                logger.info("[SystemActions] Iniciando apagado del sistema")
                terminal_dialog(
                    parent=root,
                    script_path=str(SCRIPTS_DIR / "apagado.sh"),
                    title=f"{Icons.POWER_OFF}  APAGANDO SISTEMA...")
            confirm_dialog(
                parent=root,
                text=(f"{Icons.WARNING} ¿Confirmar APAGAR el sistema?\n\n"
                      "Esta acción apagará completamente el equipo."),
                title=" Confirmar Apagado",
                on_confirm=do_shutdown, on_cancel=None)

    def on_cancel():
        """
        Cancela el diálogo de salida
        """
        logger.debug("[SystemActions] Dialogo de salida cancelado")
        selection_window.grab_release()
        selection_window.destroy()

    make_futuristic_button(
        buttons_frame, text="Cancelar", command=on_cancel,
        width=20, height=10).pack(side="right", padx=5)
    make_futuristic_button(
        buttons_frame, text="Continuar", command=on_confirm,
        width=15, height=8).pack(side="right", padx=5)

    selection_window.bind("<Escape>", lambda e: on_cancel())


def restart_application(root, update_loop=None) -> None:
    """
    Muestra confirmacion y reinicia el proceso del dashboard via os.execv.

    Args:
        root:        ventana Tk raiz del dashboard
        update_loop: instancia de UpdateLoop (se detiene antes de destroy)
    """
    def do_restart():
        """
        Reinicia la aplicación via os.execv
        """
        logger.info("[SystemActions] Reiniciando dashboard")
        # Detener el UpdateLoop antes de destruir — evita after() huérfanos
        if update_loop is not None:
            update_loop.stop()
        root.quit()
        root.destroy()
        os.execv(sys.executable,
                 [sys.executable, os.path.abspath(sys.argv[0])] + sys.argv[1:])

    confirm_dialog(
        parent=root,
        text="¿Reiniciar el dashboard?\n\nSe aplicarán los cambios realizados.",
        title=f"{Icons.REINICIAR} Reiniciar Dashboard",
        on_confirm=do_restart, on_cancel=None)
