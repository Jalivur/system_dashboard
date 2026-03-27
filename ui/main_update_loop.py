"""
Loop de actualizacion del menu principal.

Gestiona tres ciclos independientes:
  - Reloj / uptime: cada 1 segundo via root.after
  - Badges del menu: cada update_interval ms via root.after
  - Eventos del bus: procesa eventos publicados desde threads secundarios

Ambos ciclos leen exclusivamente caches de los monitores — nunca bloquean la UI.

Uso en MainWindow:
    self._update_loop = UpdateLoop(
        root=self.root,
        badge_mgr=self._badge_mgr,
        monitors={...},
        update_interval=2000,
        clock_label=self._clock_label,
        uptime_label=self._uptime_label,
    )
    self._update_loop.start()

    # Al salir, antes de root.destroy():
    self._update_loop.stop()
"""
from datetime import datetime
from config.settings import COLORS
from core.event_bus import get_event_bus
from utils.logger import get_logger

logger = get_logger(__name__)


class UpdateLoop:
    """
    Encapsula los dos loops de actualizacion del dashboard:
    reloj/uptime y badges del menu principal.
    """

    def __init__(self, root, badge_mgr, monitors: dict,
                 update_interval: int, clock_label, uptime_label,
                 weather_service=None):
        """
        Args:
            root:            widget Tk raiz
            badge_mgr:       instancia de BadgeManager
            monitors:        dict con los monitores necesarios:
                             system_monitor, update_monitor, homebridge_monitor,
                             pihole_monitor, vpn_monitor, service_monitor
            update_interval: intervalo en ms para el loop de badges
            clock_label:     CTkLabel del reloj en el header
            uptime_label:    CTkLabel del uptime en el header
            weather_service: WeatherService opcional para badge de lluvia
        """
        self._root            = root
        self._badge_mgr       = badge_mgr
        self._monitors        = monitors
        self._update_interval = update_interval
        self._clock_label     = clock_label
        self._uptime_label    = uptime_label
        self._weather_service = weather_service
        self._uptime_tick     = 0
        self._running         = False
        self._clock_after_id  = None
        self._badges_after_id = None

    # ── Arranque / parada ─────────────────────────────────────────────────────

    def start(self) -> None:
        """Arranca ambos loops. Llamar una sola vez tras construir la UI."""
        self._running = True
        self._tick_clock()
        self._update_badges()

    def stop(self) -> None:
        """
        Detiene ambos loops cancelando los after() pendientes.
        Llamar antes de root.destroy() para evitar callbacks sobre
        widgets ya destruidos.
        """
        self._running = False
        if self._clock_after_id is not None:
            try:
                self._root.after_cancel(self._clock_after_id)
            except Exception:
                pass
            self._clock_after_id = None
        if self._badges_after_id is not None:
            try:
                self._root.after_cancel(self._badges_after_id)
            except Exception:
                pass
            self._badges_after_id = None
        logger.debug("[UpdateLoop] Detenido")

    # ── Loop de reloj / uptime ────────────────────────────────────────────────

    def _tick_clock(self) -> None:
        """
        Actualiza reloj cada segundo y uptime cada minuto
        """
        if not self._running:
            return
        self._clock_label.configure(text=datetime.now().strftime("%H:%M:%S"))
        self._uptime_tick += 1
        if self._uptime_tick == 1 or self._uptime_tick >= 60:
            self._uptime_tick = 1
            try:
                uptime_str = (self._monitors["system_monitor"]
                              .get_current_stats().get("uptime_str", "--"))
                self._uptime_label.configure(text=uptime_str)
            except Exception:
                pass
        self._clock_after_id = self._root.after(1000, self._tick_clock)

    # ── Loop de badges ────────────────────────────────────────────────────────

    def _update_badges(self) -> None:
        """Actualiza todos los badges del menu. Solo lee caches — nunca bloquea la UI."""
        if not self._running:
            return
        get_event_bus().process_events()

        self._update_misc_badges()
        self._update_service_badge()
        self._update_system_badges()
        self._update_weather_badge()
        self._update_watchdog_badge()
        self._badges_after_id = self._root.after(self._update_interval, self._update_badges)

    def _update_misc_badges(self) -> None:
        """
        Actualiza badges misceláneos: updates, homebridge, pihole, vpn
        """
        bm = self._badge_mgr

        try:
            pending = (self._monitors["update_monitor"]
                       .check_updates(force=False).get('pending', 0))
            bm.update("updates", pending)
        except Exception as e:
            logger.warning("[UpdateLoop] badge 'updates' error: %s", e)

        try:
            hb = self._monitors["homebridge_monitor"]
            bm.update("hb_offline", hb.get_offline_count())
            bm.update("hb_on",      hb.get_on_count(),
                      color=COLORS.get('warning', '#ffaa00'))
            bm.update("hb_fault",   hb.get_fault_count())
        except Exception as e:
            logger.warning("[UpdateLoop] badge 'homebridge' error: %s", e)

        try:
            bm.update("pihole_offline",
                      self._monitors["pihole_monitor"].get_offline_count())
        except Exception as e:
            logger.warning("[UpdateLoop] badge 'pihole_offline' error: %s", e)

        try:
            bm.update("vpn_offline",
                      self._monitors["vpn_monitor"].get_offline_count())
        except Exception as e:
            logger.warning("[UpdateLoop] badge 'vpn_offline' error: %s", e)

    def _update_service_badge(self) -> None:
        """
        Actualiza badge de servicios fallidos desde service_monitor
        """
        bm = self._badge_mgr
        try:
            stats  = self._monitors["service_monitor"].get_stats()
            failed = stats.get('failed', 0)
            bm.update("services", failed)
        except Exception as e:
            logger.warning("[UpdateLoop] badge 'services' error: %s", e)

    def _update_weather_badge(self) -> None:
        """Muestra badge en el botón de clima si hay lluvia probable en las próximas 3h."""
        if self._weather_service is None:
            return
        bm = self._badge_mgr
        try:
            stats    = self._weather_service.get_stats()
            forecast = stats.get("forecast", [])
            max_precip = max(
                (item.get("precip_prob", 0) for item in forecast[:3]),
                default=0
            )
            if max_precip >= 80:
                bm.update("weather_rain", 1, COLORS['danger'])
            elif max_precip >= 50:
                bm.update("weather_rain", 1, COLORS.get('warning', '#ffaa00'))
            else:
                bm.update("weather_rain", 0)
        except Exception as e:
            logger.warning("[UpdateLoop] badge 'weather_rain' error: %s", e)
    
    def _update_watchdog_badge(self) -> None:
        """
        Actualiza badge de reinicios del service_watchdog

        Muestra contados de reinicios del día si hay alguno.
        """
        bm = self._badge_mgr
        try:
            wd = self._monitors.get("service_watchdog")
            if wd is None:
                return
            restarts = wd.get_stats().get('restarts_today', 0)
            bm.update("service_watchdog_restarts", restarts,
                    color=COLORS['danger'] if restarts > 0 else None)
        except Exception as e:
            logger.warning("[UpdateLoop] badge 'service_watchdog_restarts' error: %s", e)

    def _update_system_badges(self) -> None:
        """
        Actualiza badges de sistema (temp, cpu, ram, disk) desde system_monitor cache
        """
        bm = self._badge_mgr
        try:
            stats = self._monitors["system_monitor"].get_current_stats()

            # Temperatura
            temp = stats['temp']
            if temp >= bm.TEMP_CRIT:
                bm.update_temp("temp_fan",     int(temp), COLORS['danger'])
                bm.update_temp("temp_monitor", int(temp), COLORS['danger'])
            elif temp >= bm.TEMP_WARN:
                warn = COLORS.get('warning', '#ffaa00')
                bm.update_temp("temp_fan",     int(temp), warn)
                bm.update_temp("temp_monitor", int(temp), warn)
            else:
                bm.update("temp_fan",     0)
                bm.update("temp_monitor", 0)

            # CPU
            cpu = stats['cpu']
            if cpu >= bm.CPU_CRIT:
                bm.update("cpu", int(cpu), COLORS['danger'])
            elif cpu >= bm.CPU_WARN:
                bm.update("cpu", int(cpu), COLORS.get('warning', '#ffaa00'))
            else:
                bm.update("cpu", 0)

            # RAM
            ram = stats['ram']
            if ram >= bm.RAM_CRIT:
                bm.update("ram", int(ram), COLORS['danger'])
            elif ram >= bm.RAM_WARN:
                bm.update("ram", int(ram), COLORS.get('warning', '#ffaa00'))
            else:
                bm.update("ram", 0)

            # Disco
            disk = stats.get('disk_usage', 0)
            if disk >= bm.DISK_CRIT:
                bm.update("disk", int(disk), COLORS['danger'])
            elif disk >= bm.DISK_WARN:
                bm.update("disk", int(disk), COLORS.get('warning', '#ffaa00'))
            else:
                bm.update("disk", 0)

        except Exception as e:
            logger.warning("[UpdateLoop] badge 'system' error: %s", e)
