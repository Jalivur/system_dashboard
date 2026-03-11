"""
Análisis de datos históricos
"""
import sqlite3
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from config.settings import DATA_DIR
from utils.logger import get_logger

logger = get_logger(__name__)

_FMT = "%Y-%m-%d %H:%M:%S"


def _fmt(dt: datetime) -> str:
    """Convierte datetime a string sin microsegundos, formato que usa la BD."""
    return dt.strftime(_FMT)


class DataAnalyzer:
    """Analiza datos históricos de la base de datos"""

    def __init__(self, db_path: str = f"{DATA_DIR}/history.db"):
        self._db_path = db_path

    # ─────────────────────────────────────────────
    # Métodos basados en horas
    # ─────────────────────────────────────────────

    def get_data_range(self, hours: int = 24) -> List[Dict]:
        """Obtiene datos de las últimas X horas"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cutoff = _fmt(datetime.now() - timedelta(hours=hours))

                cursor.execute('''
                    SELECT * FROM metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp ASC
                ''', (cutoff,))

                rows = cursor.fetchall()
            logger.debug("[DataAnalyzer] get_data_range: %d registros (últimas %dh)", len(rows), hours)
            return [dict(row) for row in rows]

        except sqlite3.OperationalError as e:
            logger.error("[DataAnalyzer] get_data_range: error BD: %s", e)
            return []
        except Exception as e:
            logger.error("[DataAnalyzer] get_data_range: error inesperado: %s", e)
            return []

    def get_stats(self, hours: int = 24) -> Dict:
        """Obtiene estadísticas de las últimas X horas"""
        now = datetime.now()
        start = now - timedelta(hours=hours)
        return self._get_stats_between(start, now)

    def get_graph_data(self, metric: str, hours: int = 24) -> Tuple[List, List]:
        """Obtiene datos para gráficas (últimas X horas)"""
        try:
            data = self.get_data_range(hours)
            return self._extract_metric(data, metric)
        except Exception as e:
            logger.error("[DataAnalyzer] get_graph_data %s: %s", metric, e)
            return [], []

    def export_to_csv(self, output_path: str, hours: int = 24):
        """Exporta datos a CSV (últimas X horas)"""
        data = self.get_data_range(hours)
        self._write_csv(output_path, data)

    # ─────────────────────────────────────────────
    # Métodos basados en rango personalizado
    # ─────────────────────────────────────────────

    def get_data_range_between(self, start: datetime, end: datetime) -> List[Dict]:
        """Obtiene datos entre dos fechas exactas"""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT * FROM metrics
                    WHERE timestamp >= ? AND timestamp <= ?
                    ORDER BY timestamp ASC
                ''', (_fmt(start), _fmt(end)))

                rows = cursor.fetchall()
            logger.debug(
                "[DataAnalyzer] get_data_range_between: %d registros (%s → %s)", len(rows), start, end)
            return [dict(row) for row in rows]

        except sqlite3.OperationalError as e:
            logger.error("[DataAnalyzer] get_data_range_between: error BD: %s", e)
            return []
        except Exception as e:
            logger.error("[DataAnalyzer] get_data_range_between: error inesperado: %s", e)
            return []

    def get_stats_between(self, start: datetime, end: datetime) -> Dict:
        """Obtiene estadísticas entre dos fechas exactas"""
        return self._get_stats_between(start, end)

    def get_graph_data_between(self, metric: str, start: datetime, end: datetime) -> Tuple[List, List]:
        """Obtiene datos para gráficas entre dos fechas exactas"""
        try:
            data = self.get_data_range_between(start, end)
            return self._extract_metric(data, metric)
        except Exception as e:
            logger.error("[DataAnalyzer] get_graph_data_between '%s': %s", metric, e)
            return [], []

    def export_to_csv_between(self, output_path: str, start: datetime, end: datetime):
        """Exporta datos a CSV entre dos fechas exactas"""
        data = self.get_data_range_between(start, end)
        self._write_csv(output_path, data)

    # ─────────────────────────────────────────────
    # Detección de anomalías
    # ─────────────────────────────────────────────

    def detect_anomalies(self, hours: int = 24) -> List[Dict]:
        """Detecta anomalías en los datos"""
        anomalies = []
        stats = self.get_stats(hours)

        if not stats:
            return anomalies

        if stats.get('cpu_avg', 0) > 80:
            anomalies.append({'type': 'cpu_high', 'severity': 'warning',
                               'message': f"CPU promedio alta: {stats['cpu_avg']:.1f}%"})
            logger.warning("[DataAnalyzer] CPU promedio %.1f%%", stats['cpu_avg'])

        if stats.get('temp_max', 0) > 80:
            anomalies.append({'type': 'temp_high', 'severity': 'critical',
                               'message': f"Temperatura máxima: {stats['temp_max']:.1f}°C"})
            logger.warning("[DataAnalyzer] Temperatura máxima %.1f°C", stats['temp_max'])

        if stats.get('ram_avg', 0) > 85:
            anomalies.append({'type': 'ram_high', 'severity': 'warning',
                               'message': f"RAM promedio alta: {stats['ram_avg']:.1f}%"})
            logger.warning("[DataAnalyzer] RAM promedio %.1f%%", stats['ram_avg'])

        return anomalies

    # ─────────────────────────────────────────────
    # Métodos privados
    # ─────────────────────────────────────────────

    def _get_stats_between(self, start: datetime, end: datetime) -> Dict:
        """Lógica común de estadísticas para cualquier rango start→end."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT
                        AVG(cpu_percent), MAX(cpu_percent), MIN(cpu_percent),
                        AVG(ram_percent), MAX(ram_percent), MIN(ram_percent),
                        AVG(temperature), MAX(temperature), MIN(temperature),
                        AVG(net_download_mb), MAX(net_download_mb), MIN(net_download_mb),
                        AVG(net_upload_mb), MAX(net_upload_mb), MIN(net_upload_mb),
                        AVG(disk_read_mb), MAX(disk_read_mb), MIN(disk_read_mb),
                        AVG(disk_write_mb), MAX(disk_write_mb), MIN(disk_write_mb),
                        AVG(fan_pwm), MAX(fan_pwm), MIN(fan_pwm),
                        MAX(updates_available), MIN(updates_available), AVG(updates_available),
                        COUNT(*)
                    FROM metrics
                    WHERE timestamp >= ? AND timestamp <= ?
                ''', (_fmt(start), _fmt(end)))

                row = cursor.fetchone()
                
            if row and row[27]:
                logger.debug("[DataAnalyzer] _get_stats_between: %s muestras", row[27])
                return {
                    'cpu_avg':   round(row[0],  1) if row[0]  else 0,
                    'cpu_max':   round(row[1],  1) if row[1]  else 0,
                    'cpu_min':   round(row[2],  1) if row[2]  else 0,
                    'ram_avg':   round(row[3],  1) if row[3]  else 0,
                    'ram_max':   round(row[4],  1) if row[4]  else 0,
                    'ram_min':   round(row[5],  1) if row[5]  else 0,
                    'temp_avg':  round(row[6],  1) if row[6]  else 0,
                    'temp_max':  round(row[7],  1) if row[7]  else 0,
                    'temp_min':  round(row[8],  1) if row[8]  else 0,
                    'down_avg':  round(row[9],  2) if row[9]  else 0,
                    'down_max':  round(row[10], 2) if row[10] else 0,
                    'down_min':  round(row[11], 2) if row[11] else 0,
                    'up_avg':    round(row[12], 2) if row[12] else 0,
                    'up_max':    round(row[13], 2) if row[13] else 0,
                    'up_min':    round(row[14], 2) if row[14] else 0,
                    'disk_read_avg':   round(row[15], 2) if row[15] else 0,
                    'disk_read_max':   round(row[16], 2) if row[16] else 0,
                    'disk_read_min':   round(row[17], 2) if row[17] else 0,
                    'disk_write_avg':  round(row[18], 2) if row[18] else 0,
                    'disk_write_max':  round(row[19], 2) if row[19] else 0,
                    'disk_write_min':  round(row[20], 2) if row[20] else 0,
                    'pwm_avg':   round(row[21], 0) if row[21] else 0,
                    'pwm_max':   round(row[22], 0) if row[22] else 0,
                    'pwm_min':   round(row[23], 0) if row[23] else 0,
                    'updates_available_max': row[24] if row[24] else 0,
                    'updates_available_min': row[25] if row[25] else 0,
                    'updates_available_avg': row[26] if row[26] else 0,
                    'total_samples': row[27],
                }

            logger.debug("[DataAnalyzer] _get_stats_between: sin datos en el rango")
            return {}

        except sqlite3.OperationalError as e:
            logger.error("[DataAnalyzer] _get_stats_between: error BD: %s", e)
            return {}
        except Exception as e:
            logger.error("[DataAnalyzer] _get_stats_between: error inesperado: %s", e)
            return {}

    def _extract_metric(self, data: List[Dict], metric: str) -> Tuple[List, List]:
        """Extrae timestamps y valores de una métrica."""
        timestamps, values = [], []
        for entry in data:
            try:
                ts = datetime.strptime(entry['timestamp'], _FMT)
            except ValueError:
                # Por si algún registro antiguo tiene microsegundos
                ts = datetime.fromisoformat(entry['timestamp'])
            timestamps.append(ts)
            values.append(entry.get(metric) or 0)
        return timestamps, values

    def _write_csv(self, output_path: str, data: List[Dict]):
        """Escribe una lista de registros a CSV."""
        try:
            if not data:
                logger.warning("[DataAnalyzer] _write_csv: sin datos para exportar")
                return
            with open(output_path, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            logger.info("[DataAnalyzer] _write_csv: %d registros → %s", len(data), output_path)
        except OSError as e:
            logger.error("[DataAnalyzer] _write_csv: error escribiendo %s: %s", output_path, e)
        except Exception as e:
            logger.error("[DataAnalyzer] _write_csv: error inesperado: %s", e)
