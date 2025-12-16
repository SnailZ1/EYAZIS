# -*- coding: utf-8 -*-
"""Нейросетевой (langdetect) метод определения языка."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from langdetect import DetectorFactory, detect_langs

DetectorFactory.seed = 42


@dataclass
class NeuralResult:
    language: str
    probability: float


class NeuralLanguageDetector:
    """Использует langdetect для оценки вероятностей языка."""

    def __init__(self, allowed_languages: List[str] | None = None):
        self.allowed_languages = allowed_languages or ["ru", "de"]

    def detect(self, text: str) -> NeuralResult:
        try:
            predictions = detect_langs(text)
        except Exception:
            return NeuralResult(language="unknown", probability=0.0)

        filtered = [
            (pred.lang, pred.prob)
            for pred in predictions
            if pred.lang in self.allowed_languages
        ]

        if not filtered:
            top = max(predictions, key=lambda item: item.prob)
            return NeuralResult(language=top.lang, probability=top.prob)

        best_lang, prob = max(filtered, key=lambda item: item[1])
        return NeuralResult(language=best_lang, probability=prob)

