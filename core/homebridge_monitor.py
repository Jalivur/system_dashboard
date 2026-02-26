"""
Monitor de Homebridge
Integración con la API REST de homebridge-config-ui-x
Credenciales cargadas desde .env (nunca hardcodeadas)

Incluye sondeo ligero en background cada 30s para mantener
los badges del menú actualizados sin necesidad de abrir la ventana.
"""
import json
import os
import threading
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Carga de .env ─────────────────────────────────────────────────────────────
def _load_env():
    """
    Carga variables de .env sin dependencias externas.
    Si python-dotenv está disponible lo usa; si no, parsea el archivo a mano.
    """
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        logger.warning("[HomebridgeMonitor] No se encontró .env en %s", env_path)
        return

    try:
        from dotenv import load_dotenv
        load_dotenv(env_path, override=False)
        logger.debug("[HomebridgeMonitor] .env cargado con python-dotenv")
    except ImportError:
        logger.debug("[HomebridgeMonitor] python-dotenv no instalado, usando parser manual")
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value

_load_env()

# ── Configuración leída del entorno ───────────────────────────────────────────
HOMEBRIDGE_HOST  = os.environ.get("HOMEBRIDGE_HOST", "")
HOMEBRIDGE_PORT  = int(os.environ.get("HOMEBRIDGE_PORT", "8581"))
HOMEBRIDGE_USER  = os.environ.get("HOMEBRIDGE_USER", "")
HOMEBRIDGE_PASS  = os.environ.get("HOMEBRIDGE_PASS", "")

HOMEBRIDGE_URL   = f"http://{HOMEBRIDGE_HOST}:{HOMEBRIDGE_PORT}"
REQUEST_TIMEOUT  = 5   # segundos por petición HTTP
POLL_INTERVAL_S  = 30  # segundos entre sondeos en background


class HomebridgeMonitor:
    """
    Monitor y controlador de dispositivos Homebridge.

    - Sondeo ligero en background cada 30s (1 petición HTTP ~1KB).
    - La ventana lee self._accessories desde memoria sin petición extra.
    - Los badges del menú siempre reflejan el estado real.
    - toggle() fuerza un sondeo inmediato tras el comando.
    """

    def __init__(self):
        self._token: Optional[str]      = None
        self._token_lock                = threading.Lock()
        self._accessories: List[Dict]   = []
        self._accessories_lock          = threading.Lock()
        self._reachable: Optional[bool] = None  # None = aún no consultado

        # Control del thread de background
        self._running  = False
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None

        if not HOMEBRIDGE_HOST or not HOMEBRIDGE_USER:
            logger.error(
                "[HomebridgeMonitor] Faltan variables en .env: "
                "HOMEBRIDGE_HOST=%r, HOMEBRIDGE_USER=%r",
                HOMEBRIDGE_HOST, HOMEBRIDGE_USER,
            )
        else:
            logger.info(
                "[HomebridgeMonitor] Inicializado — %s:%s (usuario: %s)",
                HOMEBRIDGE_HOST, HOMEBRIDGE_PORT, HOMEBRIDGE_USER,
            )

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Arranca el sondeo en background.
        Llamar desde main.py justo después de instanciar.
        """
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._poll_loop,
            daemon=True,
            name="HomebridgePoll",
        )
        self._thread.start()
        logger.info(
            "[HomebridgeMonitor] Sondeo iniciado (cada %ds)", POLL_INTERVAL_S
        )

    def stop(self) -> None:
        """
        Detiene el sondeo limpiamente.
        Llamar en cleanup() de main.py.
        """
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=REQUEST_TIMEOUT + 1)
        logger.info("[HomebridgeMonitor] Sondeo detenido")

    def _poll_loop(self) -> None:
        """
        Bucle de background. Primera consulta inmediata al arrancar
        para poblar los badges lo antes posible.
        """
        while self._running:
            try:
                self.get_accessories()
            except Exception as e:
                logger.error("[HomebridgeMonitor] Error en poll_loop: %s", e)

            # Espera interrumpible: stop() lo despierta al instante
            self._stop_evt.wait(timeout=POLL_INTERVAL_S)
            if self._stop_evt.is_set():
                break

    # ── Autenticación ─────────────────────────────────────────────────────────

    def _authenticate(self) -> bool:
        """Obtiene un token JWT. Devuelve True si tiene éxito."""
        if not HOMEBRIDGE_HOST:
            logger.error("[HomebridgeMonitor] HOMEBRIDGE_HOST no configurado en .env")
            return False

        payload = json.dumps({
            "username": HOMEBRIDGE_USER,
            "password": HOMEBRIDGE_PASS,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{HOMEBRIDGE_URL}/api/auth/login",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                data = json.loads(resp.read().decode())
                token = data.get("access_token")
                if token:
                    with self._token_lock:
                        self._token = token
                    logger.info("[HomebridgeMonitor] Autenticación correcta")
                    return True
                logger.warning("[HomebridgeMonitor] Respuesta sin token: %s", data)
                return False
        except Exception as e:
            logger.error("[HomebridgeMonitor] Error de autenticación: %s", e)
            return False

    def _get_token(self) -> Optional[str]:
        """Devuelve el token actual; si no existe intenta autenticar."""
        with self._token_lock:
            token = self._token
        if token:
            return token
        if self._authenticate():
            with self._token_lock:
                return self._token
        return None

    def _request(self, method: str, path: str, body: Optional[Dict] = None) -> Optional[Dict]:
        """
        Petición autenticada. Si el token caduca (401) lo renueva una vez.
        """
        for attempt in range(2):
            token = self._get_token()
            if not token:
                return None

            payload = json.dumps(body).encode() if body else None
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            req = urllib.request.Request(
                f"{HOMEBRIDGE_URL}{path}",
                data=payload,
                headers=headers,
                method=method,
            )
            try:
                with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                    content = resp.read().decode()
                    return json.loads(content) if content else {}
            except urllib.error.HTTPError as e:
                if e.code == 401 and attempt == 0:
                    logger.warning("[HomebridgeMonitor] Token caducado, renovando...")
                    with self._token_lock:
                        self._token = None
                    continue
                logger.error("[HomebridgeMonitor] HTTP %s en %s: %s", e.code, path, e)
                return None
            except Exception as e:
                logger.error("[HomebridgeMonitor] Error en petición %s %s: %s", method, path, e)
                return None
        return None

    # ── Accesorios ────────────────────────────────────────────────────────────

    def get_accessories(self) -> List[Dict]:
        """
        Consulta Homebridge y actualiza self._accessories.
        Ahora reconoce 5 tipos de dispositivo:
          switch      — característica On (enchufe / interruptor)
          thermostat  — CurrentTemperature + TargetTemperature
          sensor      — CurrentTemperature o CurrentRelativeHumidity (solo lectura)
          blind       — CurrentPosition (persiana / estor)
          light       — On + Brightness (luz regulable)
        """
        data = self._request("GET", "/api/accessories")
        if data is None:
            self._reachable = False
            logger.warning("[HomebridgeMonitor] Sin conexión con Homebridge")
            return []

        self._reachable = True
        accesorios = data if isinstance(data, list) else data.get("accessories", [])

        devices = []
        for acc in accesorios:
            values = acc.get("values", {})
            name   = acc.get("serviceName", acc.get("name", "Desconocido"))
            uid    = acc.get("uniqueId", "")
            fault  = int(values.get("StatusFault",  0)) == 1
            active = int(values.get("StatusActive", 1)) == 1
            base   = {
                "uniqueId":    uid,
                "displayName": name,
                "fault":       fault,
                "inactive":    not active,
                "room":        acc.get("humanType", ""),
            }

            if "Brightness" in values and "On" in values:
                # Luz regulable
                devices.append({**base,
                    "type":       "light",
                    "on":         bool(values["On"]),
                    "brightness": int(values.get("Brightness", 0)),
                })
            elif "On" in values:
                # Enchufe / interruptor
                devices.append({**base,
                    "type": "switch",
                    "on":   bool(values["On"]),
                })
            elif "TargetTemperature" in values:
                # Termostato
                devices.append({**base,
                    "type":        "thermostat",
                    "current_temp": float(values.get("CurrentTemperature", 0)),
                    "target_temp":  float(values.get("TargetTemperature",  20)),
                })
            elif "CurrentPosition" in values:
                # Persiana / estor
                devices.append({**base,
                    "type":     "blind",
                    "position": int(values.get("CurrentPosition", 0)),
                })
            elif "CurrentTemperature" in values or "CurrentRelativeHumidity" in values:
                # Sensor de temperatura / humedad
                devices.append({**base,
                    "type":     "sensor",
                    "temp":     float(values.get("CurrentTemperature", 0))
                                if "CurrentTemperature" in values else None,
                    "humidity": float(values.get("CurrentRelativeHumidity", 0))
                                if "CurrentRelativeHumidity" in values else None,
                })

        with self._accessories_lock:
            self._accessories = devices

        logger.debug(
            "[HomebridgeMonitor] Sondeo OK — %d dispositivos (%s)",
            len(devices),
            ", ".join(
                f"{t}:{sum(1 for d in devices if d['type']==t)}"
                for t in ('switch','light','thermostat','sensor','blind')
                if any(d['type']==t for d in devices)
            ),
        )
        return devices

    def get_accessories_cached(self) -> List[Dict]:
        """
        Devuelve la lista en memoria sin hacer ninguna petición HTTP.
        Usar desde la ventana para el refresco visual inmediato.
        """
        with self._accessories_lock:
            return list(self._accessories)

    def toggle(self, unique_id: str, turn_on: bool) -> bool:
        """
        Cambia el estado On/Off de un accesorio.
        Tras el comando lanza un sondeo inmediato para que los badges
        reflejen el cambio sin esperar los 30s del ciclo normal.
        """
        body   = {"characteristicType": "On", "value": turn_on}
        result = self._request("PUT", f"/api/accessories/{unique_id}", body)
        if result is not None:
            logger.info(
                "[HomebridgeMonitor] %s → %s",
                unique_id, "ON" if turn_on else "OFF",
            )
            # Sondeo inmediato para actualizar badges al instante
            threading.Thread(
                target=self.get_accessories,
                daemon=True,
                name="HB-PostToggle",
            ).start()
            return True
        logger.error("[HomebridgeMonitor] Fallo al togglear %s", unique_id)
        return False

    # ── Métodos de badge (lectura desde memoria, sin HTTP) ────────────────────

    def is_reachable(self) -> bool:
        """True si la última consulta fue exitosa."""
        return bool(self._reachable)

    def get_offline_count(self) -> int:
        """1 si Homebridge no respondió en la última consulta. 0 en cualquier otro caso."""
        if self._reachable is None:
            return 0  # sin consultar aún — no mostrar badge al arrancar
        return 0 if self._reachable else 1

    def get_on_count(self) -> int:
        """Número de enchufes encendidos. Badge naranja en el menú."""
        if self._reachable is None:
            return 0
        with self._accessories_lock:
            return sum(1 for a in self._accessories if a.get("on", False))

    def get_fault_count(self) -> int:
        """Número de dispositivos con StatusFault=1. Badge rojo en el menú."""
        if self._reachable is None:
            return 0
        with self._accessories_lock:
            return sum(1 for a in self._accessories if a.get("fault", False))
        
    def set_brightness(self, unique_id: str, brightness: int) -> bool:
        """Establece el brillo de una luz (0–100)."""
        brightness = max(0, min(100, brightness))
        result = self._request(
            "PUT", f"/api/accessories/{unique_id}",
            {"characteristicType": "Brightness", "value": brightness}
        )
        if result is not None:
            logger.info("[HomebridgeMonitor] Brillo %s → %d%%", unique_id, brightness)
            threading.Thread(target=self.get_accessories, daemon=True,
                             name="HB-PostBrightness").start()
            return True
        return False

    def set_target_temp(self, unique_id: str, temp: float) -> bool:
        """Establece la temperatura objetivo de un termostato."""
        result = self._request(
            "PUT", f"/api/accessories/{unique_id}",
            {"characteristicType": "TargetTemperature", "value": temp}
        )
        if result is not None:
            logger.info("[HomebridgeMonitor] Termostato %s → %.1f°C", unique_id, temp)
            threading.Thread(target=self.get_accessories, daemon=True,
                             name="HB-PostTemp").start()
            return True
        return False