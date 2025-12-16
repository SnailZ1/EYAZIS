# -*- coding: utf-8 -*-
"""Метод вероятностей на основе коротких слов."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import prod
from typing import Dict, List


SHORT_WORD_LIMIT = 5
FREQUENCY_THRESHOLD = 3


@dataclass
class ShortWordsResult:
    language: str
    probability: float


class ShortWordsAnalyzer:
    """Оценивает вероятность языка по распределению коротких слов."""

    def __init__(self, target_languages: List[str] | None = None):
        self.target_languages = target_languages or ["ru", "de"]
        # эвристики для характерных коротких слов по языкам
        self.short_word_hints: Dict[str, List[str]] = {
            "ru": ["и", "в", "на", "что", "не", "из"],
            "de": ["der", "die", "das", "und", "ist", "ein"],
        }

    def extract_short_words(self, tokens: List[str]) -> Counter:
        short_tokens = [
            token for token in tokens if len(token) <= SHORT_WORD_LIMIT
        ]
        counter = Counter(short_tokens)
        filtered = Counter(
            {word: count for word, count in counter.items() if count > FREQUENCY_THRESHOLD}
        )
        return filtered

    def calc_probability(self, counter: Counter, language: str) -> float:
        total = sum(counter.values()) or 1
        probabilities = []
        for word in self.short_word_hints.get(language, []):
            freq = counter.get(word, 0)
            probabilities.append((freq / total) if freq else 0.01)
        return prod(probabilities) if probabilities else 0.0

    def detect(self, tokens: List[str]) -> ShortWordsResult:
        counter = self.extract_short_words(tokens)
        scored = [
            ShortWordsResult(language=lang, probability=self.calc_probability(counter, lang))
            for lang in self.target_languages
        ]
        return max(scored, key=lambda result: result.probability)

