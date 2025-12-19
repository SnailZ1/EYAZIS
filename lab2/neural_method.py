# -*- coding: utf-8 -*-
"""Нейросетевой метод определения языка (MLP + TF-IDF)"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List
from pathlib import Path

import joblib

from config import ASSETS_DIR


@dataclass
class NeuralResult:
    language: str
    probability: float


class NeuralLanguageDetector:

    def __init__(
        self,
        allowed_languages: List[str] | None = None,
        model_filename: str = "lang_mlp.joblib",
    ):
        self.allowed_languages = allowed_languages or ["ru", "de"]
        self.model = None

        model_path = ASSETS_DIR / model_filename
        if model_path.exists():
            self.model = joblib.load(model_path)
        else:
            print(f"⚠️ Модель не найдена: {model_path}")

    def detect(self, text: str) -> NeuralResult:
        if not self.model or not text.strip():
            return NeuralResult(language="unknown", probability=0.0)

        try:
            probs = self.model.predict_proba([text])[0]
            classes = self.model.classes_

            best_idx = probs.argmax()
            return NeuralResult(
                language=classes[best_idx],
                probability=float(probs[best_idx]),
            )

        except Exception:
            return NeuralResult(language="unknown", probability=0.0)
