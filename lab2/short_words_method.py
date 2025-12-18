# -*- coding: utf-8 -*-
"""Метод распознавания языка на основе коротких слов."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import log
from typing import Dict, List

from language_profile import LanguageProfileManager

SHORT_WORD_LIMIT = 5
MIN_PROB = 1e-6


@dataclass
class ShortWordsResult:
    language: str
    probability: float


class ShortWordsAnalyzer:
    """Оценивает язык по характерным коротким словам."""

    def __init__(self, manager: LanguageProfileManager | None = None, target_languages: List[str] | None = None):
        self.manager = manager or LanguageProfileManager()
        self.target_languages = target_languages or ["ru", "de"]
        self.short_word_hints: Dict[str, List[str]] = {
            "ru": ["и", "в", "на", "не", "что", "из"],
            "de": ["der", "die", "das", "und", "ist", "ein"],
        }

    def extract_short_words(self, tokens: List[str]) -> Counter:
        return Counter(
            token for token in tokens if len(token) <= SHORT_WORD_LIMIT
        )

    def calc_log_score(self, counter: Counter, language: str) -> float:
        total = sum(counter.values()) or 1
        score = 0.0


        profile = self.manager.load(language)
        
        if profile: short_words = {k: v for k, v in profile.frequencies.items() if len(k) < SHORT_WORD_LIMIT}

        if short_words:
            for word, _ in short_words.items():
                freq = counter.get(word, 0)
                prob = freq / total if freq else MIN_PROB
                score += log(prob)
        else:
            for word in self.short_word_hints.get(language, []):

                freq = counter.get(word, 0)
                prob = freq / total if freq else MIN_PROB
                score += log(prob)

        return score

    def detect(self, tokens: List[str]) -> ShortWordsResult:
        counter = self.extract_short_words(tokens)

        scores = {
            lang: self.calc_log_score(counter, lang)
            for lang in self.target_languages
        }

        # сортируем языки по score
        sorted_langs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_lang, best_score = sorted_langs[0]
        second_score = sorted_langs[1][1]

        # разница логарифмов
        delta = best_score - second_score

        # Сигмоида с поправочным коэффициентом (0.02)
        probability = 1 / (1 + pow(2.71828, -delta * 0.02)) 

        return ShortWordsResult(
            language=best_lang,
            probability=probability,
        )
