# -*- coding: utf-8 -*-
"""Менеджер языковых профилей для хранения и сравнения частот слов."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from collections import Counter
from pathlib import Path
from typing import Dict, List

from config import PROFILES_DIR, SUPPORTED_LANGUAGES


@dataclass
class LanguageProfile:
    language: str
    frequencies: Dict[str, float] = field(default_factory=dict)

    def top_words(self, limit: int = 100) -> Dict[str, float]:
        sorted_items = sorted(
            self.frequencies.items(), key=lambda item: item[1], reverse=True
        )
        return dict(sorted_items[:limit])


class LanguageProfileManager:
    """Загружает и сохраняет языковые профили в формате JSON."""

    def __init__(self, profiles_dir: Path = PROFILES_DIR):
        self.profiles_dir = profiles_dir
        self._cache: Dict[str, LanguageProfile] = {}

    def profile_path(self, language: str) -> Path:
        return self.profiles_dir / f"{language}.json"

    def load(self, language: str) -> LanguageProfile:
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")

        if language in self._cache:
            return self._cache[language]

        path = self.profile_path(language)
        if not path.exists():
            raise FileNotFoundError(
                f"Language profile '{language}' not found at {path}"
            )

        data = json.loads(path.read_text(encoding="utf-8"))
        profile = LanguageProfile(language=language, frequencies=data["frequencies"])
        self._cache[language] = profile
        return profile

    def save(self, profile: LanguageProfile) -> None:
        path = self.profile_path(profile.language)
        payload = json.dumps({"frequencies": profile.frequencies}, ensure_ascii=False, indent=2)
        path.write_text(payload, encoding="utf-8")
        self._cache[profile.language] = profile

    def build_from_tokens(
        self, language: str, tokens: List[str], top_k: int = 100
    ) -> LanguageProfile:
        counter = Counter(tokens)
        most_common = dict(counter.most_common(top_k))
        profile = LanguageProfile(language=language, frequencies=most_common)
        self.save(profile)
        return profile

