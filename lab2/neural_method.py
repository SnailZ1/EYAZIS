# -*- coding: utf-8 -*-
"""Нейросетевой (FastText) метод определения языка."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

# Импорт пути к ресурсам для модели lid.176.bin
from config import ASSETS_DIR

import fasttext


@dataclass
class NeuralResult:
    language: str
    probability: float


class NeuralLanguageDetector:
    """Использует FastText (lid.176.bin) для оценки вероятностей языка."""

    def __init__(self, allowed_languages: List[str] | None = None, model_filename: str = "lid.176.bin"):
        self.allowed_languages = allowed_languages or ["ru", "de"]
        self.model = None

        if fasttext:
            model_path = ASSETS_DIR / model_filename
            try:
                # FastText загружает модель. Передаем путь как строку.
                self.model = fasttext.load_model(str(model_path))
                # print(f"FastText модель успешно загружена из {model_path}")
            except ValueError as e:
                print(f"Ошибка загрузки FastText модели из {model_path}. Проверьте наличие и целостность файла: {e}")
            except Exception as e:
                print(f"Неизвестная ошибка при загрузке FastText модели: {e}")

    def detect(self, text: str) -> NeuralResult:
        if not self.model:
            # Возврат неизвестного результата, если модель не загружена
            return NeuralResult(language="unknown", probability=0.0)

        # FastText лучше работает с однострочным текстом, очистим переносы
        clean_text = text.replace('\n', ' ')

        try:
            # k=len(self.allowed_languages) гарантирует, что мы получим
            # предсказания для всех целевых языков (ru, de).
            # predictions: (labels: tuple, probabilities: tuple)
            predictions = self.model.predict(clean_text, k=len(self.allowed_languages))

            labels, probs = predictions

            filtered_results = []
            for label, prob in zip(labels, probs):
                # Удаляем префикс FastText '__label__'
                lang = label.replace('__label__', '')
                if lang in self.allowed_languages:
                    filtered_results.append((lang, prob))

            if not filtered_results:
                # Если ни один из разрешенных языков не попал в top-k,
                # возвращаем наиболее вероятный из всех (первый элемент в labels/probs)
                # Это может быть "ru", "de" или любой другой язык, который предсказала модель.
                best_label = labels[0]
                best_prob = probs[0]
                return NeuralResult(
                    language=best_label.replace('__label__', ''),
                    probability=best_prob
                )

            # Выбираем лучший результат среди разрешенных языков
            best_lang, best_prob = max(filtered_results, key=lambda item: item[1])
            return NeuralResult(language=best_lang, probability=best_prob)

        except Exception as e:
            # print(f"Ошибка во время предсказания FastText: {e}")
            return NeuralResult(language="unknown", probability=0.0)