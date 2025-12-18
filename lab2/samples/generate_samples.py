# -*- coding: utf-8 -*-
"""Утилита для генерации демонстрационных PDF на русском и немецком языках."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


SAMPLES = {
    "sample_ru.pdf": "Это демонстрационный текст на русском языке. Он содержит несколько предложений, "
    "которые помогают протестировать алгоритмы распознавания.",
    "sample_de.pdf": "Dies ist ein deutscher Beispielsatz mit Umlauten wie ä, ö, ü und dem Eszett ß, "
    "um das Erkennen der Sprache zu überprüfen.",
}


def create_pdf(path: Path, text: str):
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    text_object = c.beginText(40, height - 50)
    text_object.setFont("Helvetica", 12)
    for line in text.split(". "):
        text_object.textLine(line)
    c.drawText(text_object)
    c.showPage()
    c.save()


def main():
    samples_dir = Path(__file__).parent
    for name, text in SAMPLES.items():
        create_pdf(samples_dir / name, text)
        print(f"Generated {name}")


if __name__ == "__main__":
    main()

