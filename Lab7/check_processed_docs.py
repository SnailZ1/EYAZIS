# check_processed_docs.py
# !/usr/bin/env python3
"""
Проверка обработанных документов
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from documents_processing.collector import DocumentCollector
from text_preprocessing.preprocessor_factory import PreprocessorFactory


def check_processed_docs():
    """Проверка обработки документов"""
    print("=== ПРОВЕРКА ОБРАБОТКИ ДОКУМЕНТОВ ===")

    collector = DocumentCollector()
    documents = collector.collect_documents("docs")

    preprocessor = PreprocessorFactory.create_lemmatization_preprocessor()

    print(f"📚 Всего документов: {len(documents)}")

    # Проверяем каждый документ
    for i, doc in enumerate(documents[:5]):  # Первые 5 документов
        print(f"\n--- Документ {i + 1}: {doc.title} ---")
        print(f"Оригинальный размер: {len(doc.content)} символов")

        # Обрабатываем
        processed = preprocessor.preprocess_text(doc.content, return_string=True)
        doc.processed_content = processed

        print(f"Обработанный размер: {len(processed)} символов")
        print(f"Обработанный текст: {processed[:200]}...")

        # Ищем термины related to read
        if 'read' in processed:
            print("✅ Содержит 'read'")
        else:
            print("❌ Не содержит 'read'")


if __name__ == '__main__':
    check_processed_docs()