"""
Loop de actualizacion del menu principal.

Gestiona dos ciclos independientes:
  - Reloj / uptime: cada 1 segundo via root.after
  - Badges del menu: cada update_interval ms via root.after

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
"""
from datetime import datetime
from config.settings import COLORS
from utils.logger import get_logger

logger = get_logger(__name__)


class UpdateLoop:
    """
    Encapsula los dos loops de actualizacion del dashboard:
    reloj/uptime y badges del menu principal.
    """

    def __init__(self, root, badge_mgr, monitors: dict,
                 update_interval: int, clock_label, uptime_label):
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
        """
        self._root            = root
        self._badge_mgr       = badge_mgr
        self._monitors        = monitors
        self._update_interval = update_interval
        self._clock_label     = clock_label
        self._uptime_label    = uptime_label
        self._uptime_tick     = 0

    # ── Arranque ──────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Arranca ambos loops. Llamar una sola vez tras construir la UI."""
        self._tick_clock()
        self._update_badges()

    # ── Loop de reloj / uptime ────────────────────────────────────────────────

    def _tick_clock(self) -> None:
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
        self._root.after(1000, self._tick_clock)

    # ── Loop de badges ────────────────────────────────────────────────────────

    def _update_badges(self) -> None:
        """Actualiza todos los badges del menu. Solo lee caches — nunca bloquea la UI."""
        self._update_misc_badges()
        self._update_service_badge()
        self._update_system_badges()
        self._root.after(self._update_interval, self._update_badges)

    def _update_misc_badges(self) -> None:
        bm = self._badge_mgr
        try:
            pending = (self._monitors["update_monitor"]
                       .cached_result.get('pending', 0))
            bm.update("updates", pending)
            hb = self._monitors["homebridge_monitor"]
            bm.update("hb_offline", hb.get_offline_count())
            bm.update("hb_on",      hb.get_on_count(),
                      color=COLORS.get('warning', '#ffaa00'))
            bm.update("hb_fault",   hb.get_fault_count())
            bm.update("pihole_offline",
                      self._monitors["pihole_monitor"].get_offline_count())
            bm.update("vpn_offline",
                      self._monitors["vpn_monitor"].get_offline_count())
        except Exception:
            pass

    def _update_service_badge(self) -> None:
        bm = self._badge_mgr
        try:
            stats  = self._monitors["service_monitor"].get_stats()
            failed = stats.get('failed', 0)
            bm.update("services", failed)
        except Exception:
            pass

    def _update_system_badges(self) -> None:
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
            disk = stats['disk_usage']
            if disk >= bm.DISK_CRIT:
                bm.update("disk", int(disk), COLORS['danger'])
            elif disk >= bm.DISK_WARN:
                bm.update("disk", int(disk), COLORS.get('warning', '#ffaa00'))
            else:
                bm.update("disk", 0)

        except Exception:
            pass
