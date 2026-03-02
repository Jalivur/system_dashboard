"""
Controlador de ventiladores
"""
from typing import List, Dict
from utils.file_manager import FileManager
from utils.logger import get_logger

logger = get_logger(__name__)


class FanController:
    """Controlador para gestión de ventiladores"""
    
    def __init__(self):
        self.file_manager = FileManager()
        self._running = True  # stateless — siempre activo

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False
    
    def compute_pwm_from_curve(self, temp: float) -> int:
        """
        Calcula el PWM basado en la curva y la temperatura

        Args:
            temp: Temperatura actual en °C

        Returns:
            Valor PWM (0-255)
        """
        curve = self.file_manager.load_curve()
        
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
        Obtiene el PWM según el modo seleccionado

        Args:
            mode: Modo de operación (auto, manual, silent, normal, performance)
            temp: Temperatura actual
            manual_pwm: Valor PWM manual si mode='manual'

        Returns:
            Valor PWM calculado (0-255)
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
            logger.warning(f"[FanController] Modo desconocido '{mode}', usando curva auto")
            return self.compute_pwm_from_curve(temp)
    
    def update_fan_state(self, mode: str, temp: float, current_target: int = None,
                         manual_pwm: int = 128) -> Dict:
        """
        Actualiza el estado del ventilador

        Args:
            mode: Modo actual
            temp: Temperatura actual
            current_target: PWM objetivo actual
            manual_pwm: PWM manual configurado

        Returns:
            Diccionario con el nuevo estado
        """
        desired = self.get_pwm_for_mode(mode, temp, manual_pwm)
        desired = max(0, min(255, int(desired)))
        
        if desired != current_target:
            new_state = {"mode": mode, "target_pwm": desired}
            self.file_manager.write_state(new_state)
            logger.debug(f"[FanController] PWM actualizado: {current_target} → {desired} (modo={mode}, temp={temp:.1f}°C)")
            return new_state
        
        return {"mode": mode, "target_pwm": current_target}
    
    def add_curve_point(self, temp: int, pwm: int) -> List[Dict]:
        """
        Añade un punto a la curva

        Args:
            temp: Temperatura en °C
            pwm: Valor PWM (0-255)

        Returns:
            Curva actualizada
        """
        curve = self.file_manager.load_curve()
        pwm = max(0, min(255, pwm))
        
        found = False
        for point in curve:
            if point["temp"] == temp:
                logger.debug(f"[FanController] Punto actualizado en curva: {temp}°C → PWM {point['pwm']} → {pwm}")
                point["pwm"] = pwm
                found = True
                break
        
        if not found:
            logger.debug(f"[FanController] Nuevo punto añadido a curva: {temp}°C → PWM {pwm}")
            curve.append({"temp": temp, "pwm": pwm})
        
        curve = sorted(curve, key=lambda x: x["temp"])
        self.file_manager.save_curve(curve)
        
        return curve
    
    def remove_curve_point(self, temp: int) -> List[Dict]:
        """
        Elimina un punto de la curva

        Args:
            temp: Temperatura del punto a eliminar

        Returns:
            Curva actualizada
        """
        curve = self.file_manager.load_curve()
        original_len = len(curve)
        curve = [p for p in curve if p["temp"] != temp]
        
        if len(curve) < original_len:
            logger.debug(f"[FanController] Punto eliminado de curva: {temp}°C")
        else:
            logger.warning(f"[FanController] remove_curve_point: no se encontró punto en {temp}°C")
        
        if not curve:
            curve = [{"temp": 40, "pwm": 100}]
            logger.warning("[FanController] Curva quedó vacía, restaurado punto por defecto")
        
        self.file_manager.save_curve(curve)
        return curve
