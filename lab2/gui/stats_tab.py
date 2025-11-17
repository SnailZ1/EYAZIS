# -*- coding: utf-8 -*-
"""Вкладка статистики с панелями и графиками."""

from __future__ import annotations

import json
import customtkinter as ctk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from config import HISTORY_FILE, LANGUAGE_DISPLAY, PROFILES_DIR


class StatsTab(ctk.CTkFrame):
    """Визуализирует показатели точности и историю распознаваний."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.data: pd.DataFrame | None = None
        self._build_layout()
        self._load_history()

    def _build_layout(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        action_bar = ctk.CTkFrame(self)
        action_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        action_bar.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(action_bar, text="Статистика распознаваний", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        ctk.CTkButton(action_bar, text="Обновить", command=self._load_history).grid(
            row=0, column=1, padx=10, pady=10
        )

        self.dashboard_frame = ctk.CTkFrame(self, corner_radius=12)
        self.dashboard_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.dashboard_frame.grid_columnconfigure((0, 1), weight=1)
        self.dashboard_frame.grid_rowconfigure((0, 1), weight=1)

        self.summary_label = ctk.CTkLabel(self.dashboard_frame, text="Нет данных")
        self.summary_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.figure = Figure(figsize=(8, 4))
        self.axes_accuracy = self.figure.add_subplot(211)
        self.axes_timeline = self.figure.add_subplot(212)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.dashboard_frame)
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)

        self.heatmap_fig = Figure(figsize=(4, 3))
        self.heatmap_ax = self.heatmap_fig.add_subplot(111)
        self.heatmap_colorbar = None
        self.heatmap_canvas = FigureCanvasTkAgg(self.heatmap_fig, master=self.dashboard_frame)
        self.heatmap_canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def _load_history(self):
        if HISTORY_FILE.exists():
            self.data = pd.read_csv(HISTORY_FILE)
            self.data["score"] = pd.to_numeric(self.data["score"], errors="coerce")
            self.summary_label.configure(text=f"Записей: {len(self.data)}")
            self._render_accuracy()
            self._render_timeline()
            self._render_heatmap()
        else:
            self.data = None
            self.summary_label.configure(text="История отсутствует")
            self.axes_accuracy.clear()
            self.axes_timeline.clear()
            self.heatmap_ax.clear()
            self.canvas.draw_idle()
            self.heatmap_canvas.draw_idle()

    def _render_accuracy(self):
        if self.data is None or self.data.empty:
            return
        pivot = self.data.groupby("method")["score"].mean()
        self.axes_accuracy.clear()
        pivot.plot(kind="bar", ax=self.axes_accuracy, color="#1E88E5")
        self.axes_accuracy.set_ylim(0, 1)
        self.axes_accuracy.set_ylabel("Средний счёт")
        self.axes_accuracy.set_title("Средняя уверенность методов")
        self.canvas.draw_idle()

    def _render_timeline(self):
        if self.data is None or self.data.empty:
            return
        self.axes_timeline.clear()
        series = self.data.copy()
        series["timestamp"] = pd.to_datetime(series["timestamp"])
        timeline = series.resample("D", on="timestamp").size()
        timeline.plot(ax=self.axes_timeline, marker="o", color="#26A69A")
        self.axes_timeline.set_ylabel("Количество")
        self.axes_timeline.set_title("Активность по дням")
        self.canvas.draw_idle()

    def _render_heatmap(self):
        languages = []
        method_scores = []
        for profile_file in PROFILES_DIR.glob("*.json"):
            try:
                payload = json.loads(profile_file.read_text(encoding="utf-8"))
                freq_map = payload.get("frequencies", {})
            except Exception:
                continue
            if not freq_map:
                continue
            languages.append(LANGUAGE_DISPLAY.get(profile_file.stem, profile_file.stem))
            method_scores.append(list(freq_map.values())[:10])

        self.heatmap_ax.clear()
        if self.heatmap_colorbar:
            self.heatmap_colorbar.remove()
            self.heatmap_colorbar = None
        if method_scores:
            im = self.heatmap_ax.imshow(method_scores, aspect="auto", cmap="YlGnBu")
            self.heatmap_ax.set_yticks(range(len(languages)))
            self.heatmap_ax.set_yticklabels(languages)
            self.heatmap_ax.set_title("Heatmap частот топ-10 слов")
            self.heatmap_colorbar = self.heatmap_fig.colorbar(im, ax=self.heatmap_ax, shrink=0.6)
        else:
            self.heatmap_ax.text(0.5, 0.5, "Нет профилей", ha="center", va="center")
        self.heatmap_canvas.draw_idle()

