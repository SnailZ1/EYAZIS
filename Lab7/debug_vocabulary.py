# debug_vocabulary.py
# !/usr/bin/env python3
"""
Отладка словаря и поиска терминов
"""

import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def debug_vocabulary():
    """Отладка словаря"""
    print("=== ОТЛАДКА СЛОВАРЯ ===")

    try:
        # Загружаем словарь
        with open('search_index/vocabulary.json', 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)

        term_to_index = vocab_data['term_to_index']
        print(f"Размер словаря: {len(term_to_index)} терминов")

        # Ищем термины связанные с read
        print("\n🔍 Поиск терминов связанных с 'read':")
        read_terms = [term for term in term_to_index.keys() if 'read' in term.lower()]
        for term in read_terms:
            idx = term_to_index[term]
            df = vocab_data['term_document_frequency'][term]
            print(f"  '{term}': индекс={idx}, документов={df}")

        # Показываем примеры терминов
        print(f"\n📚 Примеры терминов в словаре:")
        sample_terms = list(term_to_index.keys())[:30]
        for i, term in enumerate(sample_terms):
            print(f"  {i + 1:2d}. '{term}'")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == '__main__':
    debug_vocabulary()