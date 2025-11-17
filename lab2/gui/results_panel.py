# -*- coding: utf-8 -*-
"""Многоразовые виджеты для отображения результатов распознавания."""

from __future__ import annotations

import customtkinter as ctk
from typing import List

from config import THEME
from models import MethodResult


class ResultCard(ctk.CTkFrame):
    """Карточка с кратким итогом отдельного метода."""

    def __init__(self, master, title: str, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.configure(border_color=THEME.primary, border_width=1, corner_radius=12)

        self.title_label = ctk.CTkLabel(self, text=title, font=("Segoe UI", 14, "bold"))
        self.title_label.pack(anchor="w", padx=12, pady=(10, 0))

        self.value_label = ctk.CTkLabel(
            self, text="--", font=("Segoe UI", 28, "bold"), text_color=THEME.primary
        )
        self.value_label.pack(anchor="w", padx=12, pady=(4, 0))

        self.score_label = ctk.CTkLabel(self, text="", font=("Segoe UI", 12))
        self.score_label.pack(anchor="w", padx=12, pady=(0, 10))

    def update_values(self, language: str, score: float):
        self.value_label.configure(text=language.upper())
        self.score_label.configure(text=f"Score: {score:.3f}")


class ResultsPanel(ctk.CTkFrame):
    """Набор карточек, показывающих результаты трёх методов."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")
        self.cards = {
            "frequency": ResultCard(self, "Частотный метод"),
            "short_words": ResultCard(self, "Короткие слова"),
            "neural": ResultCard(self, "Нейросеть"),
        }
        for idx, card in enumerate(self.cards.values()):
            card.grid(row=0, column=idx, padx=8, pady=8, sticky="nsew")

    def populate(self, method_results: List[MethodResult]):
        if not method_results:
            for card in self.cards.values():
                card.update_values("--", 0.0)
            return
        for result in method_results:
            if result.method in self.cards:
                self.cards[result.method].update_values(result.language, result.score)

