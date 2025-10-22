# indexing/index_builder.py
from typing import List, Dict
import json
import pickle
from .vocabulary import Vocabulary
from .tfidf_calculator import TFIDFCalculator


class IndexBuilder:
    """
    Класс для построения и сохранения поискового индекса
    """

    def __init__(self):
        self.vocabulary = Vocabulary()
        self.tfidf_calculator = None
        self.tfidf_vectors = {}

    def build_index(self, documents: List) -> None:
        """
        Полный процесс построения индекса:
        1. Построение словаря
        2. Расчет TF-IDF весов
        """
        print("=== НАЧАЛО ПОСТРОЕНИЯ ИНДЕКСА ===")

        # 1. Построение словаря
        self.vocabulary.build_from_documents(documents)

        # 2. Расчет TF-IDF весов
        self.tfidf_calculator = TFIDFCalculator(self.vocabulary)
        self.tfidf_vectors = self.tfidf_calculator.calculate_tfidf_weights(documents)

        print("=== ПОСТРОЕНИЕ ИНДЕКСА ЗАВЕРШЕНО ===")

    def save_index(self, base_path: str) -> None:
        """
        Сохраняет индекс в файлы:
        - vocabulary.json - словарь
        - tfidf_vectors.pkl - TF-IDF векторы
        - index_metadata.json - метаданные индекса
        """
        import os
        os.makedirs(base_path, exist_ok=True)

        # Сохраняем словарь
        vocab_path = f"{base_path}/vocabulary.json"
        self.vocabulary.save_vocabulary(vocab_path)

        # Сохраняем TF-IDF векторы (бинарный формат для эффективности)
        vectors_path = f"{base_path}/tfidf_vectors.pkl"
        with open(vectors_path, 'wb') as f:
            pickle.dump(self.tfidf_vectors, f)

        # Сохраняем метаданные
        metadata = {
            'vocabulary_size': self.vocabulary.get_vocabulary_size(),
            'total_documents': self.vocabulary.total_documents,
            'index_version': '1.0',
            'description': 'Vector space model index with TF-IDF weights'
        }

        metadata_path = f"{base_path}/index_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"Индекс сохранен в папку: {base_path}")

    def load_index(self, base_path: str) -> None:
        """
        Загружает индекс из файлов
        """
        # Загружаем словарь
        vocab_path = f"{base_path}/vocabulary.json"
        self.vocabulary.load_vocabulary(vocab_path)

        # Загружаем TF-IDF векторы
        vectors_path = f"{base_path}/tfidf_vectors.pkl"
        with open(vectors_path, 'rb') as f:
            self.tfidf_vectors = pickle.load(f)

        # Инициализируем калькулятор TF-IDF
        self.tfidf_calculator = TFIDFCalculator(self.vocabulary)

        print(f"Индекс загружен из папки: {base_path}")

    def get_index_statistics(self) -> Dict:
        """Возвращает статистику индекса"""
        vocab_stats = self.vocabulary.get_statistics()

        # Анализ распределения весов
        all_weights = []
        for vector in self.tfidf_vectors.values():
            all_weights.extend([w for w in vector if w > 0])

        stats = {
            **vocab_stats,
            'documents_with_vectors': len(self.tfidf_vectors),
            'total_non_zero_weights': len(all_weights),
            'average_weights_per_document': len(all_weights) / len(self.tfidf_vectors) if self.tfidf_vectors else 0,
            'max_weight': max(all_weights) if all_weights else 0,
            'min_weight': min(all_weights) if all_weights else 0,
            'average_weight': sum(all_weights) / len(all_weights) if all_weights else 0
        }

        return stats

    def print_detailed_statistics(self) -> None:
        """Выводит детальную статистику индекса"""
        stats = self.get_index_statistics()

        print("\n" + "=" * 60)
        print("ДЕТАЛЬНАЯ СТАТИСТИКА ИНДЕКСА")
        print("=" * 60)
        print(f"Размер словаря: {stats['vocabulary_size']}")
        print(f"Количество документов: {stats['total_documents']}")
        print(f"Документов с векторами: {stats['documents_with_vectors']}")
        print(f"Всего ненулевых весов: {stats['total_non_zero_weights']}")
        print(f"Среднее весов на документ: {stats['average_weights_per_document']:.1f}")
        print(f"Максимальный вес: {stats['max_weight']:.4f}")
        print(f"Минимальный вес: {stats['min_weight']:.4f}")
        print(f"Средний вес: {stats['average_weight']:.4f}")

        print(f"\nСамые частые термины:")
        for term, freq in stats['most_frequent_terms']:
            print(f"  {term}: {freq} документов")