# indexing/vocabulary.py
from typing import List, Dict, Set
import json
from collections import Counter


class Vocabulary:
    """
    Класс для построения и управления словарем терминов
    """

    def __init__(self):
        self.term_to_index: Dict[str, int] = {}
        self.index_to_term: Dict[int, str] = {}
        self.term_document_frequency: Dict[str, int] = {}  # df(t) - сколько документов содержат термин
        self.total_documents: int = 0
        self.next_index: int = 0

    def build_from_documents(self, documents: List) -> None:
        """
        Построение словаря из коллекции документов
        """
        print("Начинаем построение словаря...")

        # Собираем все уникальные термины из всех документов
        all_terms: Set[str] = set()
        doc_term_sets: List[Set[str]] = []

        for doc in documents:
            if hasattr(doc, 'processed_content') and doc.processed_content:
                # Разбиваем обработанный контент на термины
                terms = set(doc.processed_content.split())
                all_terms.update(terms)
                doc_term_sets.append(terms)

        self.total_documents = len(documents)

        # Сортируем термины для воспроизводимости
        sorted_terms = sorted(list(all_terms))

        # Строим отображения
        for term in sorted_terms:
            self.term_to_index[term] = self.next_index
            self.index_to_term[self.next_index] = term
            self.next_index += 1

        # Вычисляем document frequency для каждого термина
        self._calculate_document_frequency(doc_term_sets)

        print(f"Словарь построен. Уникальных терминов: {len(self.term_to_index)}")

    def _calculate_document_frequency(self, doc_term_sets: List[Set[str]]) -> None:
        """Вычисляет частоту документов для каждого термина"""
        for term in self.term_to_index.keys():
            count = sum(1 for doc_terms in doc_term_sets if term in doc_terms)
            self.term_document_frequency[term] = count

    def get_term_index(self, term: str) -> int:
        """Возвращает индекс термина в словаре"""
        return self.term_to_index.get(term, -1)

    def get_term_by_index(self, index: int) -> str:
        """Возвращает термин по индексу"""
        return self.index_to_term.get(index, "")

    def get_document_frequency(self, term: str) -> int:
        """Возвращает частоту документов для термина"""
        return self.term_document_frequency.get(term, 0)

    def get_vocabulary_size(self) -> int:
        """Возвращает размер словаря"""
        return len(self.term_to_index)

    def get_most_frequent_terms(self, top_n: int = 20) -> List[tuple]:
        """Возвращает самые частые термины"""
        sorted_terms = sorted(
            self.term_document_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_terms[:top_n]

    def get_rare_terms(self, threshold: int = 2) -> List[tuple]:
        """Возвращает редкие термины (встречаются <= threshold документов)"""
        return [(term, freq) for term, freq in self.term_document_frequency.items()
                if freq <= threshold]

    def save_vocabulary(self, filepath: str) -> None:
        """Сохраняет словарь в файл"""
        data = {
            'term_to_index': self.term_to_index,
            'index_to_term': self.index_to_term,
            'term_document_frequency': self.term_document_frequency,
            'total_documents': self.total_documents,
            'next_index': self.next_index
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_vocabulary(self, filepath: str) -> None:
        """Загружает словарь из файла"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.term_to_index = data['term_to_index']
        self.index_to_term = {int(k): v for k, v in data['index_to_term'].items()}
        self.term_document_frequency = data['term_document_frequency']
        self.total_documents = data['total_documents']
        self.next_index = data['next_index']

    def get_statistics(self) -> Dict:
        """Возвращает статистику словаря"""
        return {
            'vocabulary_size': self.get_vocabulary_size(),
            'total_documents': self.total_documents,
            'average_terms_per_document': self.get_vocabulary_size() / self.total_documents if self.total_documents > 0 else 0,
            'most_frequent_terms': self.get_most_frequent_terms(10),
            'rare_terms_count': len(self.get_rare_terms(1))
        }

    def __str__(self) -> str:
        stats = self.get_statistics()
        return (f"Vocabulary(size={stats['vocabulary_size']}, "
                f"documents={stats['total_documents']})")