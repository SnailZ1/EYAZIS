# -*- coding: utf-8 -*-
"""Вспомогательные средства обработки PDF-документов."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

import pdfplumber


LOWERCASE_MAP = str.maketrans(
    {
        "Ä": "ä",
        "Ö": "ö",
        "Ü": "ü",
        "ẞ": "ß",
    }
)

NON_LETTER_PATTERN = re.compile(r"[^a-zа-яёäöüß]+", re.IGNORECASE)


@dataclass
class Document:
    path: Path
    raw_text: str
    tokens: List[str]


class DocumentProcessor:
    """Извлекает текст из PDF и подготавливает его к анализу."""

    def __init__(self, lowercase_map=None):
        self.lowercase_map = lowercase_map or LOWERCASE_MAP

    def extract_text(self, pdf_path: Path) -> str:
        with pdfplumber.open(pdf_path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages)

    def preprocess(self, text: str) -> List[str]:
        normalized = text.translate(self.lowercase_map).lower()
        clean = NON_LETTER_PATTERN.sub(" ", normalized)
        tokens = [token for token in clean.split() if token]
        return tokens

    def process(self, pdf_path: Path) -> Document:
        raw = self.extract_text(pdf_path)
        tokens = self.preprocess(raw)
        return Document(path=pdf_path, raw_text=raw, tokens=tokens)

