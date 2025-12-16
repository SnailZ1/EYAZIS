# -*- coding: utf-8 -*-
"""Метод распознавания языка на основе частот."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import sqrt
from typing import Dict, List

from language_profile import LanguageProfileManager


def cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    intersection = set(vec_a.keys()) & set(vec_b.keys())
    numerator = sum(vec_a[word] * vec_b[word] for word in intersection)
    norm_a = sqrt(sum(value * value for value in vec_a.values()))
    norm_b = sqrt(sum(value * value for value in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return numerator / (norm_a * norm_b)


@dataclass
class FrequencyResult:
    language: str
    similarity: float


class FrequencyAnalyzer:
    """Сравнивает токены документа с сохранёнными языковыми профилями."""

    def __init__(self, manager: LanguageProfileManager | None = None, top_k: int = 100):
        self.manager = manager or LanguageProfileManager()
        self.top_k = top_k

    def build_vector(self, tokens: List[str]) -> Dict[str, float]:
        counter = Counter(tokens)
        most_common = dict(counter.most_common(self.top_k))
        return most_common

    def detect(self, tokens: List[str]) -> FrequencyResult:
        doc_vector = self.build_vector(tokens)
        similarities = []
        for lang in ("ru", "de"):
            profile = self.manager.load(lang)
            similarity = cosine_similarity(doc_vector, profile.top_words(self.top_k))
            similarities.append(FrequencyResult(language=lang, similarity=similarity))
        return max(similarities, key=lambda result: result.similarity)

