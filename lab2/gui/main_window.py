# -*- coding: utf-8 -*-
"""Инициализация главного окна CustomTkinter с навигационными вкладками."""

from __future__ import annotations

import customtkinter as ctk

from gui.recognition_tab import RecognitionTab
from gui.training_tab import TrainingTab
from gui.stats_tab import StatsTab
from config import DEFAULT_SETTINGS, THEME


class SettingsTab(ctk.CTkFrame):
    """Настройки приложения с переключением темы и опциями."""

    def __init__(self, master, on_theme_change, **kwargs):
        super().__init__(master, **kwargs)
        self.on_theme_change = on_theme_change
        self.theme_var = ctk.StringVar(value=DEFAULT_SETTINGS["theme"])
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Настройки интерфейса", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="w"
        )

        ctk.CTkLabel(self, text="Тема").grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")
        theme_switch = ctk.CTkSegmentedButton(
            self, values=["dark", "light"], variable=self.theme_var, command=self._change_theme
        )
        theme_switch.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")

        self.history_switch = ctk.CTkSwitch(self, text="Сохранять историю", onvalue="on", offvalue="off")
        self.history_switch.select() if DEFAULT_SETTINGS["auto_save_history"] else self.history_switch.deselect()
        self.history_switch.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="w")

        ctk.CTkLabel(self, text="Обновление графиков каждые 60 секунд").grid(
            row=4, column=0, padx=20, pady=(0, 20), sticky="w"
        )

    def _change_theme(self, value: str):
        ctk.set_appearance_mode(value)
        self.on_theme_change(value)


class MainWindow(ctk.CTk):
    """Главное окно приложения с навигационными вкладками."""

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode(DEFAULT_SETTINGS["theme"])
        ctk.set_default_color_theme("dark-blue")

        self.title("PDF Language Recognition")
        self.geometry("1400x850")
        self.minsize(1200, 720)

        self._build_ui()

    def _build_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        recognition_frame = self.tabview.add("Распознавание")
        training_frame = self.tabview.add("Обучение")
        stats_frame = self.tabview.add("Статистика")
        settings_frame = self.tabview.add("Настройки")

        RecognitionTab(recognition_frame).pack(fill="both", expand=True)
        TrainingTab(training_frame).pack(fill="both", expand=True)
        StatsTab(stats_frame).pack(fill="both", expand=True)
        SettingsTab(settings_frame, on_theme_change=self._on_theme_change).pack(fill="both", expand=True)

    def _on_theme_change(self, mode: str):
        # При необходимости можно сохранить режим в настройках
        pass

