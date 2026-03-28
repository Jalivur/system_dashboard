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
    """
    Gestor centralizado de archivos JSON.

    Provee métodos estáticos para leer y escribir estados en formato JSON de manera segura.
    """


    class FileManager:
        """
        Encapsula la lógica para manejar archivos de estado de forma segura y eficiente.
        """


        @staticmethod
        def write_state(data: dict) -> None:
            """
            Escribe el estado de forma atómica usando archivo temporal.

            Args:
                data (dict): Diccionario con los datos a guardar.

            Raises:
                OSError: Si ocurre un error al escribir el archivo.
            """


        @staticmethod
        def load_state() -> dict:
            """
            Carga el estado guardado.

            Returns:
                dict: Diccionario con el estado guardado, incluyendo modo y objetivo PWM.

            Nota:
                Si no existe un estado guardado, se devuelve un estado por defecto.
            """
    
    @staticmethod
    def write_state(data: Dict[str, Any]) -> None:
        """
        Escribe el estado de forma atómica usando un archivo temporal.

        Args:
            data (Dict[str, Any]): Diccionario con los datos a guardar.

        Raises:
            OSError: Si ocurre un error durante la escritura del estado.

        Returns:
            None
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
        Carga el estado guardado desde un archivo.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con el modo y el objetivo de PWM.

        Raises:
            Ninguna excepción relevante, se manejan internamente.
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
        Carga la curva de ventiladores desde un archivo y devuelve una lista de puntos ordenados por temperatura.

        Args:
            Ninguno

        Returns:
            Lista de diccionarios con temperaturas (temp) y valores PWM (pwm) ordenados por temperatura.

        Raises:
            Ninguna excepción específica, aunque puede registrar warnings si el archivo está malformado.
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
        Guarda la curva de ventiladores en un archivo.

        Args:
            points: Lista de puntos con temperatura y PWM.

        Raises:
            OSError: Si ocurre un error al escribir en el archivo.
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
