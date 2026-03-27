"""
Ventana de Widget de Clima.

Muestra datos meteorológicos actuales y previsión de las próximas 12 horas
via Open-Meteo (gratuito, sin clave API).

Arquitectura:
  - Todos los datos vienen de WeatherService.get_stats() — caché, no bloquea UI
  - Refresco solo al abrir la ventana y con el botón Actualizar
  - Ciudad editable desde la propia ventana
  - Favoritos: guardar ciudad activa, seleccionar desde desplegable, eliminar
  - Máximo de favoritos editable y persistido en config/local_settings.py
  - Scroll vertical para todo el contenido
  - Scroll horizontal para la previsión por horas
  - StringVar siempre con master= explícito
"""
import tkinter as tk
import customtkinter as ctk
import threading, time
from datetime import datetime
from config.settings import COLORS, FONT_FAMILY, FONT_SIZES, DSI_WIDTH, DSI_HEIGHT, DSI_X, DSI_Y, Icons
from ui.styles import StyleManager, make_window_header, make_futuristic_button
from utils.logger import get_logger

logger = get_logger(__name__)



class WeatherWindow(ctk.CTkToplevel):
    """Ventana de datos meteorológicos con favoritos."""

    def __init__(self, parent, weather_service):
        """Inicializa la ventana de clima: configura geometría, variables de estado y construye UI completa."""
        
        super().__init__(parent)
        self._svc = weather_service

        self.title("Clima")
        self.configure(fg_color=COLORS['bg_medium'])
        self.overrideredirect(True)
        self.geometry(f"{DSI_WIDTH}x{DSI_HEIGHT}+{DSI_X}+{DSI_Y}")
        self.resizable(False, False)
        self.transient(parent)
        self.after(150, self.focus_set)

        self._city_var    = ctk.StringVar(master=self, value=self._svc.get_city())
        self._current_sunrise  = "--"
        self._current_sunset   = "--"
        self._drilldown_active = False   # True cuando estamos en vista de horas de un día
        self._fav_var     = ctk.StringVar(master=self, value="")
        self._max_fav_var = ctk.StringVar(master=self,
                                          value=str(self._svc.get_max_favorites()))
        self._after_id    = None

        self._create_ui()
        self._refresh_favorites_dropdown()
        self._update()
        logger.info("[WeatherWindow] Ventana abierta")

    # ── Cierre limpio ─────────────────────────────────────────────────────────

    def destroy(self):
        """Limpia temporizadores y recursos al cerrar la ventana de manera segura."""
        
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        super().destroy()

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _create_ui(self):
        """Construye toda la interfaz de usuario: header, búsqueda, favoritos, datos actuales y área de previsión."""
        
        main = ctk.CTkFrame(self, fg_color=COLORS['bg_medium'])
        main.pack(fill="both", expand=True, padx=5, pady=5)

        make_window_header(main, title="WIDGET DE CLIMA", on_close=self.destroy)

        # ── Zona scrollable vertical ──────────────────────────────────────────
        scroll_container = ctk.CTkFrame(main, fg_color=COLORS['bg_medium'])
        scroll_container.pack(fill="both", expand=True, padx=0, pady=4)

        canvas = ctk.CTkCanvas(
            scroll_container, bg=COLORS['bg_medium'], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            scroll_container, orientation="vertical",
            command=canvas.yview, width=30)
        scrollbar.pack(side="right", fill="y")
        StyleManager.style_scrollbar_ctk(scrollbar)
        canvas.configure(yscrollcommand=scrollbar.set)

        self._inner = ctk.CTkFrame(canvas, fg_color=COLORS['bg_medium'])
        canvas.create_window((0, 0), window=self._inner, anchor="nw", width=DSI_WIDTH - 50)
        self._inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # ── Barra de búsqueda de ciudad ───────────────────────────────────────
        search_frame = ctk.CTkFrame(self._inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        search_frame.pack(fill="x", padx=8, pady=(4, 0))

        ctk.CTkLabel(
            search_frame,
            text=f"{Icons.SEARCH}  Ciudad:",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['text_dim'],
        ).pack(side="left", padx=(12, 6), pady=10)

        self._city_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self._city_var,
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            width=200,
            height=36,
        )
        self._city_entry.pack(side="left", padx=6, pady=10)
        self._city_entry.bind("<Return>", lambda e: self._on_search())

        self._search_btn = make_futuristic_button(
            search_frame,
            text=f"{Icons.SEARCH}  Buscar",
            command=self._on_search,
            width=11, height=6, font_size=FONT_SIZES['small'],
        )
        self._search_btn.pack(side="left", padx=4, pady=10)

        self._refresh_btn = make_futuristic_button(
            search_frame,
            text=f"{Icons.REFRESH}  Actualizar",
            command=self._on_refresh,
            width=12, height=6, font_size=FONT_SIZES['small'],
        )
        self._refresh_btn.pack(side="left", padx=4, pady=10)

        # ── Barra de favoritos ────────────────────────────────────────────────
        fav_frame = ctk.CTkFrame(self._inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        fav_frame.pack(fill="x", padx=8, pady=(4, 0))

        ctk.CTkLabel(
            fav_frame,
            text=f"{Icons.STAR}  Favoritos:",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['text_dim'],
        ).pack(side="left", padx=(12, 6), pady=8)


        self._fav_menu = ctk.CTkOptionMenu(
            fav_frame,
            variable=self._fav_var,
            values=["(ninguno)"],
            command=self._on_favorite_selected,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary'],
            dropdown_fg_color=COLORS['bg_dark'],
            dropdown_text_color=COLORS['text'],
            text_color=COLORS['text'],
            width=180,
            height=32,
        )
        self._fav_menu.pack(side="left", padx=4, pady=8)

        self._save_fav_btn = make_futuristic_button(
            fav_frame,
            text=f"{Icons.SAVE}  Guardar",
            command=self._on_save_favorite,
            width=11, height=6, font_size=FONT_SIZES['small'],
        )
        self._save_fav_btn.pack(side="left", padx=4, pady=8)

        self._del_fav_btn = make_futuristic_button(
            fav_frame,
            text=f"{Icons.DELETE}  Eliminar",
            command=self._on_delete_favorite,
            width=11, height=6, font_size=FONT_SIZES['small'],
        )
        self._del_fav_btn.pack(side="left", padx=4, pady=8)

        ctk.CTkLabel(
            fav_frame,
            text="Máx:",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(side="left", padx=(10, 2), pady=8)

        self._max_entry = ctk.CTkEntry(
            fav_frame,
            textvariable=self._max_fav_var,
            font=(FONT_FAMILY, FONT_SIZES['small']),
            fg_color=COLORS['bg_medium'],
            border_color=COLORS['border'],
            text_color=COLORS['text'],
            width=44,
            height=32,
            justify="center",
        )
        self._max_entry.pack(side="left", padx=(0, 4), pady=8)
        self._max_entry.bind("<FocusOut>", lambda e: self._on_max_changed())
        self._max_entry.bind("<Return>",   lambda e: self._on_max_changed())

        self._fav_status_lbl = ctk.CTkLabel(
            fav_frame,
            text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['danger'],
        )
        self._fav_status_lbl.pack(side="left", padx=6, pady=8)

        # ── Última actualización + error ──────────────────────────────────────
        info_row = ctk.CTkFrame(self._inner, fg_color="transparent")
        info_row.pack(fill="x", padx=12, pady=(3, 0))

        self._error_lbl = ctk.CTkLabel(
            info_row, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['danger'], anchor="w",
        )
        self._error_lbl.pack(side="left")

        self._last_update_lbl = ctk.CTkLabel(
            info_row, text="",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'], anchor="e",
        )
        self._last_update_lbl.pack(side="right")

        # ── Panel datos actuales ──────────────────────────────────────────────
        self._current_frame = ctk.CTkFrame(self._inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        self._current_frame.pack(fill="x", padx=8, pady=(6, 0))
        current_frame = self._current_frame

        top_row = ctk.CTkFrame(current_frame, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 4))

        self._weather_icon_lbl = ctk.CTkLabel(
            top_row, text="--",
            font=(FONT_FAMILY, 40), text_color=COLORS['text'],
        )
        self._weather_icon_lbl.pack(side="left", padx=(0, 12))

        temp_col = ctk.CTkFrame(top_row, fg_color="transparent")
        temp_col.pack(side="left")

        self._city_display_lbl = ctk.CTkLabel(
            temp_col, text="--",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['secondary'],
        )
        self._city_display_lbl.pack(anchor="w")

        self._temp_lbl = ctk.CTkLabel(
            temp_col, text="--°C",
            font=(FONT_FAMILY, FONT_SIZES['xxlarge'], "bold"),
            text_color=COLORS['primary'],
        )
        self._temp_lbl.pack(anchor="w")

        self._desc_lbl = ctk.CTkLabel(
            temp_col, text="--",
            font=(FONT_FAMILY, FONT_SIZES['medium']),
            text_color=COLORS['text'],
        )
        self._desc_lbl.pack(anchor="w")

        self._feels_lbl = ctk.CTkLabel(
            temp_col, text="Sensación: --°C",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        )
        self._feels_lbl.pack(anchor="w")

        # ── Barra de progreso del día (sunrise → sunset) ─────────────────────
        prog_frame = ctk.CTkFrame(current_frame, fg_color="transparent")
        prog_frame.pack(fill="x", padx=12, pady=(0, 6))

        self._day_progress_canvas = tk.Canvas(
            prog_frame, bg=COLORS['bg_dark'],
            highlightthickness=0, height=10, cursor="arrow")
        self._day_progress_canvas.pack(fill="x")
        self._day_progress_canvas.bind(
            "<Configure>", lambda e: self._redraw_day_progress())

        # ── Fila de detalles con scroll horizontal ───────────────────────────
        detail_outer = ctk.CTkFrame(current_frame, fg_color="transparent")
        detail_outer.pack(fill="x", padx=8, pady=(0, 6))

        self._detail_canvas = tk.Canvas(
            detail_outer, bg=COLORS['bg_dark'],
            highlightthickness=0, height=10)
        self._detail_canvas.pack(side="top", fill="x", expand=True)

        detail_hscroll = ctk.CTkScrollbar(
            detail_outer, orientation="horizontal",
            command=self._detail_canvas.xview, height=16)
        detail_hscroll.pack(side="bottom", fill="x")
        StyleManager.style_scrollbar_ctk(detail_hscroll)
        self._detail_canvas.configure(xscrollcommand=detail_hscroll.set)

        detail_row = ctk.CTkFrame(self._detail_canvas, fg_color="transparent")
        self._detail_canvas.create_window((0, 0), window=detail_row, anchor="nw")
        detail_row.bind("<Configure>", self._on_detail_configure)

        self._humidity_lbl = self._make_detail(detail_row, Icons.WEATHER_HUMIDITY,   "Humedad",       "--")
        self._wind_lbl     = self._make_detail(detail_row, Icons.WEATHER_WIND,        "Viento",        "--")
        self._precip_lbl   = self._make_detail(detail_row, Icons.WEATHER_PRECIP_PCT,  "Precipitación", "--")
        self._uv_lbl       = self._make_detail(detail_row, Icons.SUN,                 "Índice UV",     "--")
        self._sun_lbl      = self._make_detail(detail_row, Icons.SUNRISE,             "Sol",           "--")
        self._aqi_lbl      = self._make_detail(detail_row, Icons.AIR,                 "Aire (AQI)",    "--")

        # ── Selector de vista de previsión ───────────────────────────────────
        view_row = ctk.CTkFrame(self._inner, fg_color="transparent")
        view_row.pack(fill="x", padx=8, pady=(10, 2))

        ctk.CTkLabel(
            view_row, text="Previsión:",
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['text_dim'],
        ).pack(side="left", padx=(6, 10))

        self._view_mode = ctk.StringVar(master=self, value="hours")

        self._btn_hours = make_futuristic_button(
            view_row,
            text=f"{Icons.CLOCK}  Horas",
            command=lambda: self._set_view_mode("hours"),
            width=11, height=6, font_size=FONT_SIZES['small'],
        )
        self._btn_hours.pack(side="left", padx=4)

        self._btn_days = make_futuristic_button(
            view_row,
            text=f"{Icons.CALENDAR}  14 días",
            command=lambda: self._set_view_mode("days"),
            width=12, height=6, font_size=FONT_SIZES['small'],
        )
        self._btn_days.pack(side="left", padx=4)

        self._btn_back = make_futuristic_button(
            view_row,
            text=f"{Icons.BACK}  Volver",
            command=self._drilldown_back,
            width=10, height=6, font_size=FONT_SIZES['small'],
        )
        # Oculto hasta que se active drill-down
        self._drilldown_label = ctk.CTkLabel(
            view_row, text="",
            font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
            text_color=COLORS['primary'],
        )

        # ── Área de previsión (scroll horizontal compartida) ──────────────────
        forecast_outer = ctk.CTkFrame(self._inner, fg_color=COLORS['bg_dark'], corner_radius=8)
        forecast_outer.pack(fill="x", padx=8, pady=(0, 8))

        self._forecast_canvas = tk.Canvas(
            forecast_outer, bg=COLORS['bg_dark'],
            highlightthickness=0, height=10,
        )
        self._forecast_canvas.pack(side="top", fill="x", expand=True)

        hscroll = ctk.CTkScrollbar(
            forecast_outer, orientation="horizontal",
            command=self._forecast_canvas.xview, height=20)
        hscroll.pack(side="bottom", fill="x")
        StyleManager.style_scrollbar_ctk(hscroll)
        self._forecast_canvas.configure(xscrollcommand=hscroll.set)

        self._forecast_inner = ctk.CTkFrame(self._forecast_canvas, fg_color=COLORS['bg_dark'])
        self._forecast_canvas.create_window((0, 0), window=self._forecast_inner, anchor="nw")
        self._forecast_inner.bind(
            "<Configure>", self._on_forecast_inner_configure)

        self._forecast_cells = []

    def _on_forecast_inner_configure(self, event) -> None:
        """Ajusta automáticamente el canvas de previsión a la altura real del contenido interno."""
        
        self._forecast_canvas.configure(
            scrollregion=self._forecast_canvas.bbox("all"),
            height=event.height,
        )

    def _on_detail_configure(self, event) -> None:
        """Ajusta automáticamente el canvas de detalles meteorológicos a la altura real del contenido."""
        
        self._detail_canvas.configure(
            scrollregion=self._detail_canvas.bbox("all"),
            height=event.height,
        )

    @staticmethod
    def _aqi_color(aqi) -> str:
        """Color según índice AQI europeo (0–500+)."""
        try:
            v = int(aqi)
        except (ValueError, TypeError):
            return COLORS['text']
        if v <= 20:   return "#4caf50"   # Bueno
        if v <= 40:   return "#8bc34a"   # Aceptable
        if v <= 60:   return "#ffeb3b"   # Moderado
        if v <= 80:   return "#ff9800"   # Malo
        if v <= 100:  return "#f44336"   # Muy malo
        return "#9c27b0"                 # Extremadamente malo

    @staticmethod
    def _wmo_bg_color(code) -> str:
        """Color de fondo del panel actual según código WMO."""
        try:
            c = int(code)
        except (ValueError, TypeError):
            return COLORS['bg_dark']
        if c == 0:                          return "#0d1f2d"   # Despejado — azul noche profundo
        if c in (1, 2, 3):                  return "#111a24"   # Nuboso — gris azulado
        if c in (45, 48):                   return "#151515"   # Niebla — gris oscuro
        if c in (51, 53, 55,
                 61, 63, 65,
                 80, 81, 82):               return "#0a1a1a"   # Lluvia — verde azulado oscuro
        if c in (71, 73, 75):               return "#141e28"   # Nieve — azul pálido oscuro
        if c in (95, 96, 99):               return "#1a0d0d"   # Tormenta — rojo muy oscuro
        return COLORS['bg_dark']

    @staticmethod
    def _temp_color(temp) -> str:
        """Devuelve un color hex interpolado según la temperatura."""
        try:
            t = float(temp)
        except (ValueError, TypeError):
            return COLORS['primary']
        # Escala: ≤0°→azul, 10°→cian, 20°→verde, 30°→naranja, ≥40°→rojo
        stops = [
            (-10, (100, 180, 255)),
            (  0, ( 80, 160, 255)),
            ( 10, ( 80, 220, 180)),
            ( 20, (100, 220,  80)),
            ( 30, (255, 160,  40)),
            ( 40, (255,  60,  40)),
        ]
        if t <= stops[0][0]:
            r, g, b = stops[0][1]
        elif t >= stops[-1][0]:
            r, g, b = stops[-1][1]
        else:
            for i in range(len(stops) - 1):
                t0, c0 = stops[i]
                t1, c1 = stops[i + 1]
                if t0 <= t <= t1:
                    ratio = (t - t0) / (t1 - t0)
                    r = int(c0[0] + ratio * (c1[0] - c0[0]))
                    g = int(c0[1] + ratio * (c1[1] - c0[1]))
                    b = int(c0[2] + ratio * (c1[2] - c0[2]))
                    break
        return f"#{r:02x}{g:02x}{b:02x}"

    def _redraw_day_progress(self) -> None:
        """Dibuja la barra de progreso del día (desde salida hasta puesta de sol) con marcador actual y etiquetas."""
        
        c = self._day_progress_canvas
        if not self.winfo_exists():
            return
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 2:
            return

        # Fondo
        c.create_rectangle(0, 0, w, h,
                            fill=COLORS['bg_medium'], outline="", tags="bg")

        sr = self._current_sunrise
        ss = self._current_sunset
        if sr == "--" or ss == "--":
            return

        try:
            fmt = "%H:%M"
            now   = datetime.now()
            t_sr  = datetime.strptime(sr, fmt).replace(
                year=now.year, month=now.month, day=now.day)
            t_ss  = datetime.strptime(ss, fmt).replace(
                year=now.year, month=now.month, day=now.day)
            total = (t_ss - t_sr).total_seconds()
            if total <= 0:
                return
            elapsed = (now - t_sr).total_seconds()
            ratio   = max(0.0, min(1.0, elapsed / total))
        except Exception:
            return

        # Barra de fondo (día completo)
        bar_h = h - 2
        c.create_rectangle(2, 1, w - 2, bar_h,
                            fill=COLORS['border'], outline="", tags="track")

        # Barra de progreso
        fill_w = max(4, int((w - 4) * ratio))
        # Color: naranja al amanecer → amarillo a mediodía → naranja al atardecer
        mid = 0.5
        if ratio < mid:
            r2 = ratio / mid
            color = f"#{int(255):02x}{int(140 + 115 * r2):02x}{int(20):02x}"
        else:
            r2 = (ratio - mid) / mid
            color = f"#{int(255):02x}{int(255 - 115 * r2):02x}{int(20):02x}"

        c.create_rectangle(2, 1, 2 + fill_w, bar_h,
                            fill=color, outline="", tags="progress")

        # Marcador posición actual (línea vertical)
        x_now = 2 + fill_w
        c.create_line(x_now, 0, x_now, h,
                      fill="white", width=2, tags="marker")

        # Etiquetas sunrise / sunset
        c.create_text(4, h // 2, anchor="w",
                      text=f"{Icons.SUNRISE} {sr}",
                      fill=COLORS['text_dim'],
                      font=(FONT_FAMILY, 9))
        c.create_text(w - 4, h // 2, anchor="e",
                      text=f"{Icons.SUNSET} {ss}",
                      fill=COLORS['text_dim'],
                      font=(FONT_FAMILY, 9))

    def _make_detail(self, parent, emoji, label, value):
        """Crea un widget compacto de detalle meteorológico (icono + etiqueta + valor destacado)."""
        
        cell = ctk.CTkFrame(parent, fg_color=COLORS['bg_medium'], corner_radius=6)
        cell.pack(side="left", padx=6, pady=4, ipadx=10, ipady=6)
        ctk.CTkLabel(
            cell, text=f"{emoji}  {label}",
            font=(FONT_FAMILY, FONT_SIZES['small']),
            text_color=COLORS['text_dim'],
        ).pack(anchor="w", padx=8, pady=(4, 0))
        val_lbl = ctk.CTkLabel(
            cell, text=value,
            font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
            text_color=COLORS['text'],
        )
        val_lbl.pack(anchor="w", padx=8, pady=(0, 4))
        return val_lbl

    # ── Actualización de datos ────────────────────────────────────────────────

    def _update(self):
        """Actualiza toda la interfaz con datos frescos del servicio: condiciones actuales, detalles y previsión."""
        
        if not self.winfo_exists():
            return
        stats = self._svc.get_stats()
        
        if not self._svc.is_running():
            StyleManager.show_service_stopped_banner(self._inner, "Weather Service")
            return

        if not stats:
            msg = ("Cargando datos meteorológicos..."
                   if self._svc.get_city()
                   else "Introduce una ciudad y pulsa Buscar")
            self._error_lbl.configure(text=msg, text_color=COLORS['text_dim'])
            return

        error = stats.get("error", "")
        self._error_lbl.configure(
            text=error,
            text_color=COLORS['danger'] if error else COLORS['text_dim'])

        last = stats.get("last_update", "")
        self._last_update_lbl.configure(
            text=f"Actualizado: {last}" if last else "")

        city = stats.get("city", "")
        if city and self._city_var.get() != city:
            self._city_var.set(city)

        temp     = stats.get("temp",         "--")
        feels    = stats.get("feels_like",   "--")
        humidity = stats.get("humidity",     "--")
        wind_spd = stats.get("wind_speed",   "--")
        wind_dir = stats.get("wind_dir",     "--")
        precip   = stats.get("precip",       "--")
        desc     = stats.get("weather_desc", "--")
        icon     = stats.get("weather_icon", "")
        wmo_code = stats.get("weather_code", 0)
        uv       = stats.get("uv_index",     "--")
        sunrise  = stats.get("sunrise",      "--")
        sunset   = stats.get("sunset",       "--")

        self._current_frame.configure(fg_color=self._wmo_bg_color(wmo_code))
        self._weather_icon_lbl.configure(text=icon)
        self._city_display_lbl.configure(text=city if city else "--")
        self._temp_lbl.configure(
            text=f"{temp}°C" if temp != "--" else "--°C",
            text_color=self._temp_color(temp))
        self._desc_lbl.configure(text=desc)
        self._feels_lbl.configure(
            text=f"Sensación: {feels}°C" if feels != "--" else "Sensación: --")

        # Barra de progreso — guardar sunrise/sunset para redibujar en resize
        self._current_sunrise = sunrise
        self._current_sunset  = sunset
        self._redraw_day_progress()
        self._humidity_lbl.configure(
            text=f"{humidity}%" if humidity != "--" else "--")
        self._wind_lbl.configure(
            text=f"{wind_spd} km/h {self._wind_dir_arrow(wind_dir)}"
            if wind_spd != "--" else "--")
        self._precip_lbl.configure(
            text=f"{precip} mm" if precip != "--" else "--")
        self._uv_lbl.configure(
            text=f"{uv}" if uv != "--" else "--")
        self._sun_lbl.configure(
            text=f"{sunrise} / {sunset}" if sunrise != "--" else "--")

        aqi = stats.get("aqi", "--")
        self._aqi_lbl.configure(
            text=str(aqi) if aqi != "--" else "--",
            text_color=self._aqi_color(aqi))

        # Si estamos en drill-down no tocamos el área de previsión
        if self._drilldown_active:
            return
        if self._view_mode.get() == "hours":
            self._update_forecast(stats.get("forecast", []))
        else:
            self._update_forecast_daily(stats.get("forecast_daily", []))

    def _update_forecast(self, forecast, max_items: int = 12):
        """Renderiza las celdas de previsión por horas en el área de scroll horizontal (máx. 12 items)."""
        
        for w in self._forecast_inner.winfo_children():
            w.destroy()
        self._forecast_cells = []

        for item in forecast[:max_items]:
            cell = ctk.CTkFrame(
                self._forecast_inner,
                fg_color=COLORS['bg_medium'], corner_radius=6)
            cell.pack(side="left", padx=4, pady=6, ipadx=6)

            ctk.CTkLabel(
                cell, text=item.get("hour", "--"),
                font=(FONT_FAMILY, FONT_SIZES['small'], "bold"),
                text_color=COLORS['text_dim'],
            ).pack(pady=(6, 0))

            ctk.CTkLabel(
                cell, text=item.get("weather_icon", ""),
                font=(FONT_FAMILY, 20),
            ).pack()

            temp = item.get("temp", "--")
            ctk.CTkLabel(
                cell, text=f"{temp}°" if temp != "--" else "--",
                font=(FONT_FAMILY, FONT_SIZES['medium'], "bold"),
                text_color=self._temp_color(temp),
            ).pack()

            precip = item.get("precip_prob", 0)
            ctk.CTkLabel(
                cell,
                text=f"{Icons.WEATHER_PRECIP_PCT} {precip}%",
                font=(FONT_FAMILY, FONT_SIZES['small']),
                text_color=(COLORS['text_dim'] if precip < 40
                            else COLORS.get('warning', '#ffaa00')),
            ).pack(pady=(0, 6))

            self._forecast_cells.append(cell)

    # ── Selector de vista ────────────────────────────────────────────────────

    def _set_view_mode(self, mode: str) -> None:
        """Cambia el modo de vista de previsión entre 'hours' (12h) y 'days' (14 días), actualizando contenido."""
        
        self._view_mode.set(mode)
        stats = self._svc.get_stats()
        if not stats:
            return
        if mode == "hours":
            self._update_forecast(stats.get("forecast", []))
        else:
            self._update_forecast_daily(stats.get("forecast_daily", []))

    # ── Callbacks — búsqueda ──────────────────────────────────────────────────

    def _on_search(self):
        """Callback del botón/Enter de búsqueda: valida ciudad, inicia thread asíncrono y actualiza UI."""
        
        city = self._city_var.get().strip()
        if not city:
            return
        self._search_btn.configure(state="disabled")
        self._error_lbl.configure(
            text=f"Buscando '{city}'...", text_color=COLORS['text_dim'])

        def _do():
            """Función auxiliar interna para ejecutar set_city en hilo separado."""
            
            result = self._svc.set_city(city)
            self.after(0, lambda: self._on_search_done(result))

        threading.Thread(target=_do, daemon=True, name="WeatherSearch").start()

    def _on_search_done(self, result):
        """Callback post-búsqueda desde thread: re-activa UI, maneja éxito/error y refresca datos."""
        
        if not self.winfo_exists():
            return
        self._search_btn.configure(state="normal")
        if result["ok"]:
            self._error_lbl.configure(text="", text_color=COLORS['danger'])
            self._city_var.set(result["city"])
            self._update()
        else:
            self._error_lbl.configure(
                text=result["error"], text_color=COLORS['danger'])

    def _on_refresh(self):
        """Inicia actualización asíncrona de datos meteorológicos actuales, deshabilitando botón durante proceso."""
        
        if not self._svc.get_city():
            return
        self._refresh_btn.configure(state="disabled")
        self._error_lbl.configure(text="Actualizando...", text_color=COLORS['text_dim'])

        
        def _do():
            """Función auxiliar interna para fetch_now en hilo separado con delay post-fetch."""
            
            self._svc.fetch_now()
            time.sleep(2)
            if self.winfo_exists():
                self.after(0, self._on_refresh_done)

        threading.Thread(target=_do, daemon=True, name="WeatherRefresh").start()

    def _on_refresh_done(self):
        """Finaliza refresh: re-habilita botón, limpia mensajes y actualiza toda la UI."""
        
        if not self.winfo_exists():
            return
        self._refresh_btn.configure(state="normal")
        self._error_lbl.configure(text="")
        self._update()

    def _update_forecast_daily(self, forecast: list) -> None:
        """Renderiza previsión extendida de 14 días con celdas clickeables para drill-down a horas específicas."""
        
        for w in self._forecast_inner.winfo_children():
            w.destroy()
        self._forecast_cells = []

        for item in forecast:
            cell = ctk.CTkFrame(
                self._forecast_inner,
                fg_color=COLORS['bg_medium'], corner_radius=6)
            cell.pack(side="left", padx=2, pady=4, ipadx=4)

            label = item.get("label", "--")
            date  = item.get("date", "")

            # Día + fecha
            ctk.CTkLabel(
                cell, text=f"{label} {date}",
                font=(FONT_FAMILY, 10, "bold"),
                text_color=COLORS['primary'] if label == "Hoy"
                           else COLORS['text_dim'],
            ).pack(pady=(4, 0))

            # Icono WMO
            ctk.CTkLabel(
                cell, text=item.get("weather_icon", ""),
                font=(FONT_FAMILY, 16),
            ).pack(pady=0)

            # Máx
            t_max = item.get("temp_max", "--")
            ctk.CTkLabel(
                cell,
                text=f"{t_max}°" if t_max != "--" else "--",
                font=(FONT_FAMILY, 11, "bold"),
                text_color=self._temp_color(t_max),
            ).pack(pady=0)

            # Mín
            t_min = item.get("temp_min", "--")
            ctk.CTkLabel(
                cell,
                text=f"{t_min}°" if t_min != "--" else "--",
                font=(FONT_FAMILY, 10),
                text_color=COLORS['text_dim'],
            ).pack(pady=0)

            # Precipitación
            precip = item.get("precip_prob", 0)
            ctk.CTkLabel(
                cell,
                text=f"{Icons.WEATHER_PRECIP_PCT} {precip}%",
                font=(FONT_FAMILY, 10),
                text_color=COLORS['text_dim'] if precip < 40
                           else COLORS.get('warning', '#ffaa00'),
            ).pack(pady=0)

            # Sunrise / sunset
            sr = item.get("sunrise", "--")
            ss = item.get("sunset",  "--")
            ctk.CTkLabel(
                cell,
                text=f"{Icons.SUNRISE} {sr}",
                font=(FONT_FAMILY, 9),
                text_color=COLORS.get('warning', '#ffaa00'),
            ).pack(pady=0)
            ctk.CTkLabel(
                cell,
                text=f"{Icons.SUNSET} {ss}",
                font=(FONT_FAMILY, 9),
                text_color=COLORS['text_dim'],
            ).pack(pady=(0, 3))

            # Drill-down: pulsar la celda muestra las horas de ese día
            date_key = item.get("date_iso", "")
            if date_key:
                for widget in self._iter_all_children(cell):
                    widget.bind("<Button-1>",
                        lambda e, dk=date_key, lbl=f"{label} {date}":
                            self._drilldown_day(dk, lbl))
                cell.bind("<Button-1>",
                    lambda e, dk=date_key, lbl=f"{label} {date}":
                        self._drilldown_day(dk, lbl))
                cell.configure(cursor="hand2")

            self._forecast_cells.append(cell)

    # ── Drill-down días → horas ───────────────────────────────────────────────

    @staticmethod
    def _iter_all_children(widget):
        """Generador recursivo que itera todos los widgets hijos para binding de eventos drill-down."""
        
        for child in widget.winfo_children():
            yield child
            yield from WeatherWindow._iter_all_children(child)

    def _drilldown_day(self, date_key: str, label: str) -> None:
        """Activa modo drill-down: muestra previsión horaria específica del día seleccionado, ocultando selectores."""
        
        stats = self._svc.get_stats()
        if not stats:
            return
        hours = stats.get("hourly_by_date", {}).get(date_key, [])
        if not hours:
            return

        self._drilldown_active = True

        # Mostrar botón Volver y etiqueta, ocultar selectores
        self._btn_hours.pack_forget()
        self._btn_days.pack_forget()
        self._btn_back.pack(side="left", padx=4)
        self._drilldown_label.configure(text=label)
        self._drilldown_label.pack(side="left", padx=(8, 0))

        self._update_forecast(hours, max_items=24)

    def _drilldown_back(self) -> None:
        """Regresa del drill-down de horas a la vista general de 14 días."""
        
        self._drilldown_active = False

        self._btn_back.pack_forget()
        self._drilldown_label.pack_forget()
        self._btn_hours.pack(side="left", padx=4)
        self._btn_days.pack(side="left", padx=4)

        self._set_view_mode("days")

    # ── Callbacks — favoritos ─────────────────────────────────────────────────

    def _on_save_favorite(self):
        """Guarda la ciudad actualmente activa en la lista de favoritos del servicio."""
        
        city = self._svc.get_city()
        if not city:
            self._set_fav_status("No hay ciudad activa", ok=False)
            return
        result = self._svc.add_favorite(city)
        if result["ok"]:
            self._set_fav_status(f"'{city}' guardada", ok=True)
            self._refresh_favorites_dropdown()
        else:
            self._set_fav_status(result["error"], ok=False)

    def _on_delete_favorite(self):
        """Elimina el favorito seleccionado del dropdown de la lista del servicio y refresca UI."""
        
        city = self._fav_var.get()
        if not city or city == "(ninguno)":
            self._set_fav_status("Selecciona un favorito primero", ok=False)
            return
        self._svc.remove_favorite(city)
        self._set_fav_status(f"'{city}' eliminada", ok=True)
        self._refresh_favorites_dropdown()

    def _on_favorite_selected(self, city):
        """Carga automáticamente la ciudad seleccionada desde favoritos y ejecuta búsqueda."""
        
        if not city or city == "(ninguno)":
            return
        self._city_var.set(city)
        self._on_search()

    def _on_max_changed(self):
        """Valida y persiste el nuevo máximo de favoritos desde el campo de entrada."""
        
        try:
            n = int(self._max_fav_var.get())
            if n < 1:
                raise ValueError
        except ValueError:
            self._max_fav_var.set(str(self._svc.get_max_favorites()))
            self._set_fav_status("Máximo inválido (mín. 1)", ok=False)
            return
        self._svc.set_max_favorites(n)
        self._set_fav_status(f"Máximo: {n}", ok=True)
        self._refresh_favorites_dropdown()

    def _refresh_favorites_dropdown(self):
        """Recarga dinámicamente la lista de favoritos en el OptionMenu desde el servicio."""
        
        if not self.winfo_exists():
            return
        favs = self._svc.get_favorites()
        values = favs if favs else ["(ninguno)"]
        self._fav_menu.configure(values=values)
        if self._fav_var.get() not in values:
            self._fav_var.set(values[0])

    def _set_fav_status(self, msg, ok=True):
        """Muestra mensaje de estado temporal (3s) en la UI de favoritos con color según éxito/error."""
        
        if not self.winfo_exists():
            return
        color = COLORS.get('success', '#44cc88') if ok else COLORS['danger']
        self._fav_status_lbl.configure(text=msg, text_color=color)
        self.after(3000, lambda: self._fav_status_lbl.configure(text="")
                   if self.winfo_exists() else None)

    # ── Utilidades ────────────────────────────────────────────────────────────

    @staticmethod
    def _wind_dir_arrow(degrees):
        """Convierte la dirección del viento en grados a símbolo de flecha unicode (8 direcciones)."""
        
        if degrees == "--" or degrees is None:
            return ""
        try:
            d = float(degrees)
        except (ValueError, TypeError):
            return ""
        arrows = ["↓", "↙", "←", "↖", "↑", "↗", "→", "↘"]
        return arrows[round(d / 45) % 8]
