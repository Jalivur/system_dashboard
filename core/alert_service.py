"""
Servicio de alertas externas por Telegram.
Sin dependencias nuevas — usa urllib de la stdlib.

Lógica anti-spam: cada alerta debe mantenerse activa durante
ALERT_SUSTAIN_S segundos antes de enviarse, y no se repite
hasta que baje del umbral y vuelva a subir (edge-trigger).
"""
import threading
import time
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Optional
import os
from dotenv import load_dotenv
from utils.logger import get_logger

logger = get_logger(__name__)

# Tiempo que la condición debe mantenerse antes de enviar (segundos)
ALERT_SUSTAIN_S = 60

# Intervalo de comprobación (segundos)
CHECK_INTERVAL  = 15

# Umbrales (se pueden sobrescribir en settings.py si se prefiere)
THRESHOLDS = {
    'temp':  {'warn': 60, 'crit': 70},
    'cpu':   {'warn': 85, 'crit': 95},
    'ram':   {'warn': 85, 'crit': 95},
    'disk':  {'warn': 85, 'crit': 95},
}


def _load_telegram_config() -> tuple:
    """Lee TOKEN y CHAT_ID desde .env / os.environ."""
    
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        try:
            load_dotenv(env_path, override=False)
        except ImportError:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    k, _, v = line.partition('=')
                    k = k.strip()
                    if k not in os.environ:
                        os.environ[k] = v.strip().strip('"').strip("'")
    token   = os.environ.get('TELEGRAM_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    return token, chat_id


class AlertService:
    """
    Servicio background que monitoriza métricas y envía alertas a Telegram.

    Instanciar en main.py y pasar system_monitor / service_monitor.
    Llamar a start() y stop() igual que el resto de servicios.
    """

    def __init__(self, system_monitor, service_monitor):
        self.system_monitor  = system_monitor
        self.service_monitor = service_monitor

        self._token, self._chat_id = _load_telegram_config()

        if not self._token or not self._chat_id:
            logger.warning(
                "[AlertService] TELEGRAM_TOKEN o TELEGRAM_CHAT_ID no configurados — "
                "alertas desactivadas"
            )

        # Estado interno para anti-spam
        # key -> {'first_seen': timestamp, 'sent': bool}
        self._state: Dict[str, dict] = {}
        self._lock   = threading.Lock()

        self._running  = False
        self._stop_evt = threading.Event()
        self._thread: Optional[threading.Thread] = None

    # ── Ciclo de vida ─────────────────────────────────────────────────────────

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._stop_evt.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="AlertService"
        )
        self._thread.start()
        logger.info("[AlertService] Servicio iniciado (cada %ds)", CHECK_INTERVAL)

    def stop(self) -> None:
        self._running = False
        self._stop_evt.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        logger.info("[AlertService] Servicio detenido")

    # ── Bucle principal ───────────────────────────────────────────────────────

    def _loop(self) -> None:
        while self._running:
            try:
                self._check_metrics()
                self._check_services()
            except Exception as e:
                logger.error("[AlertService] Error en _loop: %s", e)
            self._stop_evt.wait(timeout=CHECK_INTERVAL)
            if self._stop_evt.is_set():
                break

    def _check_metrics(self) -> None:
        stats = self.system_monitor.get_current_stats()
        checks = [
            ('temp', stats.get('temp',        0), '°C',  '🌡️ Temperatura'),
            ('cpu',  stats.get('cpu',          0), '%',   '🔥 CPU'),
            ('ram',  stats.get('ram',          0), '%',   '💾 RAM'),
            ('disk', stats.get('disk_usage',   0), '%',   '💿 Disco'),
        ]
        for key, value, unit, label in checks:
            thr  = THRESHOLDS[key]
            if value >= thr['crit']:
                level, emoji = 'crit', '🔴'
            elif value >= thr['warn']:
                level, emoji = 'warn', '🟠'
            else:
                level = None

            alert_key = f"{key}_{level}" if level else None
            if level:
                msg = (
                    f"{emoji} *Dashboard — {label} alta*\n"
                    f"Valor actual: *{value:.1f}{unit}*\n"
                    f"Umbral {'crítico' if level=='crit' else 'de aviso'}: "
                    f"{thr[level]}{unit}"
                )
                self._trigger(alert_key, msg)
            else:
                # Condición resuelta — resetear para permitir futura alerta
                for suffix in ('warn', 'crit'):
                    self._reset(f"{key}_{suffix}")

    def _check_services(self) -> None:
        stats = self.service_monitor.get_stats()
        failed = stats.get('failed', 0)
        key = 'services_failed'
        if failed > 0:
            msg = (
                f"⚠️ *Dashboard — Servicios caídos*\n"
                f"Hay *{failed}* servicio{'s' if failed > 1 else ''} en estado FAILED.\n"
                f"Abre Monitor Servicios para más detalles."
            )
            self._trigger(key, msg)
        else:
            self._reset(key)

    # ── Lógica anti-spam (edge-trigger + sustain) ─────────────────────────────

    def _trigger(self, key: str, message: str) -> None:
        """
        Activa una alerta con retardo anti-spam.
        Solo envía si la condición lleva ALERT_SUSTAIN_S segundos activa
        y no se ha enviado ya para este 'flanco'.
        """
        now = time.time()
        with self._lock:
            entry = self._state.get(key)
            if entry is None:
                self._state[key] = {'first_seen': now, 'sent': False}
                return
            if entry['sent']:
                return
            if now - entry['first_seen'] >= ALERT_SUSTAIN_S:
                entry['sent'] = True
        # Enviar fuera del lock
        self._send(message)

    def _reset(self, key: str) -> None:
        """Resetea el estado de una alerta (condición resuelta)."""
        with self._lock:
            self._state.pop(key, None)

    # ── Envío a Telegram ──────────────────────────────────────────────────────

    def _send(self, text: str) -> bool:
        """Envía un mensaje Markdown a Telegram. Devuelve True si tiene éxito."""
        if not self._token or not self._chat_id:
            return False
        url     = f"https://api.telegram.org/bot{self._token}/sendMessage"
        payload = json.dumps({
            "chat_id":    self._chat_id,
            "text":       text,
            "parse_mode": "Markdown",
        }).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                result = json.loads(resp.read())
                if result.get("ok"):
                    logger.info("[AlertService] Mensaje enviado a Telegram")
                    return True
            logger.warning("[AlertService] Respuesta inesperada de Telegram: %s", result)
            return False
        except Exception as e:
            logger.error("[AlertService] Error enviando a Telegram: %s", e)
            return False

    def send_test(self) -> bool:
        """Envía un mensaje de prueba. Útil para verificar la configuración."""
        return self._send(
            "✅ *Dashboard — Test de alertas*\n"
            "La conexión con Telegram funciona correctamente."
        )