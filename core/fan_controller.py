"""
Controlador de ventiladores
"""
from typing import List, Dict
from utils.file_manager import FileManager
from utils.logger import get_logger

logger = get_logger(__name__)


class FanController:
    """
    Controlador stateless para ventiladores que calcula PWM según modo y curva de temperatura.

    Args: Ninguno

    Returns: Ninguno

    Raises: Ninguno
    """

    
    def __init__(self):
        """
        Inicializa el controlador del ventilador sin estado interno.

        Args:
            Ninguno

        Returns:
            Ninguno

        Raises:
            Ninguno
        """
        self._file_manager = FileManager()
        self._running = True  # stateless — siempre activo


    def start(self) -> None:
        """
        Activa el controlador del ventilador.

        Args: 
            Ninguno

        Returns: 
            Ninguno

        Raises: 
            Ninguno
        """
        self._running = True


    def stop(self) -> None:
        """
        Detiene el controlador del ventilador.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self._running = False

        
    def is_running(self) -> bool:
        """
        Verifica si el servicio de control de ventiladores está en ejecución.

        Args:
            None

        Returns:
            bool: True si el servicio está corriendo, False de lo contrario.

        Raises:
            None
        """
        return self._running
    
    def compute_pwm_from_curve(self, temp: float) -> int:
        """
        Calcula el valor PWM interpolando la temperatura en la curva cargada.

        Args:
            temp: Temperatura actual en °C.

        Returns:
            Valor PWM (0-255) correspondiente a la temperatura.

        Raises:
            ValueError: Si la curva tiene menos de dos puntos.
        """
        curve = self._file_manager.load_curve()
        
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
        Obtiene el valor PWM según el modo de operación y la temperatura actual.

        Args:
            mode (str): Modo de operación (auto, manual, silent, normal, performance)
            temp (float): Temperatura actual
            manual_pwm (int): Valor PWM manual si mode='manual' (por defecto 128)

        Returns:
            int: Valor PWM calculado (0-255)

        Raises:
            Ninguna excepción específica, se registra un warning en caso de modo desconocido.
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
            logger.warning("[FanController] Modo desconocido '%s', usando curva auto", mode)
            return self.compute_pwm_from_curve(temp)
    
    def update_fan_state(self, mode: str, temp: float, current_target: int = None,
                         manual_pwm: int = 128) -> Dict:
        """
        Actualiza el estado del ventilador según el modo y la temperatura actuales.

        Args:
            mode (str): Modo de operación ('auto', 'manual', 'full', 'off').
            temp (float): Temperatura actual en grados Celsius.
            current_target (int): PWM objetivo actual. None si no hay estado previo.
            manual_pwm (int): Valor PWM para modo manual (0-255).

        Returns:
            Dict: Estado actualizado con claves 'mode' y 'target_pwm'.

        Raises:
            ValueError: Si el modo no es válido.
        """
        desired = self.get_pwm_for_mode(mode, temp, manual_pwm)
        desired = max(0, min(255, int(desired)))
        
        if desired != current_target:
            new_state = {"mode": mode, "target_pwm": desired}
            self._file_manager.write_state(new_state)
            logger.debug("[FanController] PWM actualizado: %d → %d (modo=%s, temp=%.1f°C)", current_target, desired, mode, temp)
            return new_state
        
        return {"mode": mode, "target_pwm": current_target}
    
    def add_curve_point(self, temp: int, pwm: int) -> List[Dict]:
        """
        Añade o actualiza un punto en la curva temperatura-PWM.

        Args:
            temp (int): Temperatura en °C del punto a añadir/actualizar.
            pwm (int): Ciclo de trabajo PWM (0-255) asociado.

        Returns:
            List[Dict]: Curva ordenada tras la modificación.

        Raises:
            None
        """
        curve = self._file_manager.load_curve()
        pwm = max(0, min(255, pwm))
        
        found = False
        for point in curve:
            if point["temp"] == temp:
                logger.debug("[FanController] Punto actualizado en curva: %d°C → PWM %d → %d", temp, point['pwm'], pwm)
                point["pwm"] = pwm
                found = True
                break
        
        if not found:
            logger.debug("[FanController] Nuevo punto añadido a curva: %d°C → PWM %d", temp, pwm)
            curve.append({"temp": temp, "pwm": pwm})
        
        curve = sorted(curve, key=lambda x: x["temp"])
        self._file_manager.save_curve(curve)
        
        return curve
    
    def remove_curve_point(self, temp: int) -> List[Dict]:
        """
        Elimina el punto de la curva que coincide con la temperatura indicada.

        Args:
            temp (int): Temperatura en °C del punto a eliminar.

        Returns:
            List[Dict]: Curva actualizada tras la eliminación.

        Raises:
            Ninguna excepción relevante.

        Nota: Si la curva queda vacía, se añade automáticamente un punto por defecto.
        """
        curve = self._file_manager.load_curve()
        original_len = len(curve)
        curve = [p for p in curve if p["temp"] != temp]
        
        if len(curve) < original_len:
            logger.debug("[FanController] Punto eliminado de curva: %d°C", temp)
        else:
            logger.warning("[FanController] remove_curve_point: no se encontró punto en %d°C", temp)
        
        if not curve:
            curve = [{"temp": 40, "pwm": 100}]
            logger.warning("[FanController] Curva quedó vacía, restaurado punto por defecto")
        
        self._file_manager.save_curve(curve)
        return curve
