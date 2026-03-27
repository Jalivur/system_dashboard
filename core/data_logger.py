"""
Sistema de logging de datos históricos
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict
from utils import DashboardLogger


class DataLogger:
    """Registra datos del sistema en base de datos SQLite"""

    def __init__(self, db_path: str = "data/history.db"):
        """
        Inicializa DataLogger con BD SQLite.

        Args:
            db_path (str): Ruta BD (default data/history.db).

        Crea tablas, chequea rotación automática.
        """
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._db_path = db_path
        self._init_database()
        self._dashboard_logger = DashboardLogger()
        self.check_and_rotate_db(max_mb=5.0)


    def _init_database(self):
        """
        Crea tablas metrics/events si no existen + índice timestamp.

        Tabla metrics: Histórico sistema cada UPDATE_MS.
        Tabla events: Alertas/log eventos.
        """
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    cpu_percent REAL,
                    ram_percent REAL,
                    ram_used_gb REAL,
                    temperature REAL,
                    disk_used_percent REAL,
                    disk_read_mb REAL,
                    disk_write_mb REAL,
                    net_download_mb REAL,
                    net_upload_mb REAL,
                    fan_pwm INTEGER,
                    fan_mode TEXT,
                    updates_available INTEGER,
                    uptime_s INTEGER
                )
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON metrics(timestamp)
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    event_type TEXT,
                    severity TEXT,
                    message TEXT,
                    data JSON
                )
            ''')

            conn.commit()

    def log_metrics(self, metrics: Dict):
        """
        Guarda un conjunto de métricas.
        La timestamp se genera con datetime.now() para usar la hora local del sistema,
        evitando el desfase UTC que produce DEFAULT CURRENT_TIMESTAMP de SQLite.
        """
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()

            # Hora local explícita — SQLite CURRENT_TIMESTAMP siempre es UTC
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('''
                INSERT INTO metrics (
                    timestamp,
                    cpu_percent, ram_percent, ram_used_gb, temperature,
                    disk_used_percent, disk_read_mb, disk_write_mb,
                    net_download_mb, net_upload_mb, fan_pwm, fan_mode, updates_available,
                    uptime_s
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                now,
                metrics.get('cpu_percent'),
                metrics.get('ram_percent'),
                metrics.get('ram_used_gb'),
                metrics.get('temperature'),
                metrics.get('disk_used_percent'),
                metrics.get('disk_read_mb'),
                metrics.get('disk_write_mb'),
                metrics.get('net_download_mb'),
                metrics.get('net_upload_mb'),
                metrics.get('fan_pwm'),
                metrics.get('fan_mode'),
                metrics.get('updates_available'),
                metrics.get('uptime_s')
            ))

            conn.commit()

    def log_event(self, event_type: str, severity: str, message: str, data: Dict = None):
        """
        Registra evento (alerta/log) en tabla events.

        Args:
            event_type (str): e.g. 'service_restart'
            severity (str): 'info', 'warning', 'error'
            message (str): Descripción
            data (Dict, optional): Datos extra JSON.

        Timestamp local automática.
        """
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('''
                INSERT INTO events (timestamp, event_type, severity, message, data)
                VALUES (?, ?, ?, ?, ?)
            ''', (now, event_type, severity, message, json.dumps(data) if data else None))

            conn.commit()


    def get_metrics_count(self) -> int:
        """
        Cuenta total registros en tabla metrics.

        Returns:
            int: Número de entradas históricas.
        """
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM metrics')
            count = cursor.fetchone()[0]

        return count

    def get_db_size_mb(self) -> float:
        """
        Retorna tamaño archivo history.db en MB.

        Returns:
            float: Tamaño MB o 0 si no existe.
        """
        db_file = Path(self._db_path)
        if db_file.exists():
            return db_file.stat().st_size / (1024 * 1024)
        return 0.0

    def clean_old_data(self, days: int = 30):
        """
        Borra métricas/events > days antiguos + VACUUM optimizar.

        Args:
            days (int): Retener últimos N días (default 30).
        """
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.cursor()

            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute('DELETE FROM metrics WHERE timestamp < ?', (cutoff,))
            cursor.execute('DELETE FROM events  WHERE timestamp < ?', (cutoff,))

            conn.commit()
            cursor.execute('VACUUM')


    def check_and_rotate_db(self, max_mb: float = 5.0):
        """
        Chequea tamaño DB > max_mb y auto-limpia si necesario.

        Args:
            max_mb (float): Límite tamaño MB (default 5).
        """
        log = self._dashboard_logger.get_logger(__name__)
        log.info("[DataLogger] Verificando tamaño BD... %.2F MB", self.get_db_size_mb())
        if self.get_db_size_mb() > max_mb:
            log.warning("[DataLogger] BD supera %.1f MB. Limpiando...", max_mb)
            self.clean_old_data(days=30)
            log.info("[DataLogger] Limpieza completada. Nuevo tamaño: %.2f MB", self.get_db_size_mb())
