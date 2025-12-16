# -*- coding: utf-8 -*-
"""Высокоуровневый модуль оркестрации распознавания языка в PDF."""

from __future__ import annotations

import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from config import HISTORY_FILE, DEFAULT_SETTINGS
from document_processor import DocumentProcessor
from frequency_method import FrequencyAnalyzer
from models import MethodResult, RecognitionResult
from neural_method import NeuralLanguageDetector
from short_words_method import ShortWordsAnalyzer


class RecognitionEngine:
    """Координирует обработку документов и работу методов распознавания."""

    def __init__(self):
        self.processor = DocumentProcessor()
        self.frequency_method = FrequencyAnalyzer()
        self.short_method = ShortWordsAnalyzer()
        self.neural_method = NeuralLanguageDetector()

    def analyze_file(self, pdf_path: Path, true_language: str | None = None) -> RecognitionResult:
        start = time.perf_counter()
        document = self.processor.process(pdf_path)

        freq = self.frequency_method.detect(document.tokens)
        short = self.short_method.detect(document.tokens)
        neural = self.neural_method.detect(document.raw_text)

        method_results = [
            MethodResult("frequency", freq.language, freq.similarity, {"similarity": freq.similarity}),
            MethodResult("short_words", short.language, short.probability, {"probability": short.probability}),
            MethodResult("neural", neural.language, neural.probability, {"probability": neural.probability}),
        ]

        aggregate_scores = {}
        for result in method_results:
            aggregate_scores.setdefault(result.language, 0.0)
            aggregate_scores[result.language] += result.score

        decided_language = max(aggregate_scores, key=aggregate_scores.get)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        return RecognitionResult(
            file_path=pdf_path,
            true_language=true_language,
            method_results=method_results,
            decided_language=decided_language,
            created_at=datetime.now(),
            processing_time_ms=elapsed_ms,
            preview_text=document.raw_text[: DEFAULT_SETTINGS["preview_max_chars"]],
        )

    def analyze_folder(self, folder: Path) -> List[RecognitionResult]:
        results = []
        for pdf in folder.glob("*.pdf"):
            results.append(self.analyze_file(pdf))
        return results

    def export_results(self, results: Iterable[RecognitionResult], target: Path) -> None:
        rows = []
        for result in results:
            for method in result.method_results:
                rows.append(
                    {
                        "Файл": result.file_path.name,
                        "Реальный_язык": result.true_language or "",
                        "Метод": method.method,
                        "Результат": method.language,
                        "Вероятность": round(method.score, 4),
                        "Время": result.processing_time_ms,
                    }
                )
        df = pd.DataFrame(rows)
        if target.suffix == ".csv":
            df.to_csv(target, index=False, encoding="utf-8")
        elif target.suffix in (".xlsx", ".xls"):
            df.to_excel(target, index=False, engine="openpyxl")
        elif target.suffix == ".pdf":
            self._export_pdf(df, target)
        else:
            raise ValueError("Unsupported export format")

    def _export_pdf(self, dataframe: pd.DataFrame, target: Path) -> None:
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(str(target), pagesize=A4)
        data = [list(dataframe.columns)] + dataframe.values.tolist()
        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E88E5")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.gray),
                ]
            )
        )
        doc.build([Paragraph("Результаты распознавания", styles["Heading2"]), table])

    def append_history(self, results: Iterable[RecognitionResult]) -> None:
        is_new = not HISTORY_FILE.exists()
        with HISTORY_FILE.open("a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if is_new:
                writer.writerow(
                    ["timestamp", "file", "method", "result_language", "score", "duration_ms"]
                )
            for result in results:
                for method in result.method_results:
                    writer.writerow(
                        [
                            result.created_at.isoformat(),
                            str(result.file_path),
                            method.method,
                            method.language,
                            f"{method.score:.4f}",
                            result.processing_time_ms,
                        ]
                    )

