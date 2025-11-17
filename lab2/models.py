# -*- coding: utf-8 -*-
"""Общие датаклассы для результатов распознавания."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
from datetime import datetime


@dataclass
class MethodResult:
    method: str
    language: str
    score: float
    details: Dict[str, float] = field(default_factory=dict)


@dataclass
class RecognitionResult:
    file_path: Path
    true_language: str | None
    method_results: List[MethodResult]
    decided_language: str
    created_at: datetime
    processing_time_ms: int
    preview_text: str = ""

    @property
    def best_result(self) -> MethodResult:
        return max(self.method_results, key=lambda result: result.score)

