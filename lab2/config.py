# -*- coding: utf-8 -*-
"""Глобальная конфигурация комплекса распознавания языка в PDF."""

from pathlib import Path
from dataclasses import dataclass


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PROFILES_DIR = BASE_DIR / "profiles"
ASSETS_DIR = BASE_DIR / "assets"
SAMPLES_DIR = BASE_DIR / "samples"
HISTORY_FILE = DATA_DIR / "history.csv"


DATA_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
SAMPLES_DIR.mkdir(exist_ok=True)


@dataclass
class ThemeConfig:
    """Палитра темы, используемая всеми виджетами CustomTkinter."""

    primary: str = "#1E88E5"
    secondary: str = "#26A69A"
    accent: str = "#00ACC1"
    danger: str = "#EF5350"
    success: str = "#43A047"
    warning: str = "#FDD835"


THEME = ThemeConfig()

SUPPORTED_LANGUAGES = ["ru", "de"]
LANGUAGE_DISPLAY = {"ru": "Русский", "de": "Deutsch"}


class ExportFormat:
    CSV = "csv"
    EXCEL = "xlsx"
    PDF = "pdf"


DEFAULT_SETTINGS = {
    "theme": "dark",
    "auto_save_history": True,
    "batch_limit": 25,
    "preview_max_chars": 2000,
}

