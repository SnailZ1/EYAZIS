# indexing/tfidf_calculator.py
from typing import List, Dict, Tuple
import math
from collections import Counter


class TFIDFCalculator:
    """
    Класс для расчета TF-IDF весов терминов в документах
    """

    def __init__(self, vocabulary):
        self.vocabulary = vocabulary

    def calculate_tfidf_weights(self, documents: List) -> Dict[int, List[float]]:
        """
        Вычисляет TF-IDF веса для всех документов
        Возвращает словарь: doc_id -> вектор TF-IDF весов
        """
        print("Начинаем расчет TF-IDF весов...")

        tfidf_vectors = {}

        for doc in documents:
            if hasattr(doc, 'processed_content') and doc.processed_content:
                vector = self._document_to_tfidf_vector(doc)
                tfidf_vectors[doc.doc_id] = vector
                doc.tfidf_vector = vector  # Сохраняем в документе

        print(f"Расчет TF-IDF завершен. Обработано документов: {len(tfidf_vectors)}")
        return tfidf_vectors

    def _document_to_tfidf_vector(self, document) -> List[float]:
        """
        Преобразует документ в вектор TF-IDF
        Возвращает нормализованный вектор согласно формуле из задания
        """
        if not hasattr(document, 'processed_content') or not document.processed_content:
            return [0.0] * self.vocabulary.get_vocabulary_size()

        # Разбиваем на термины
        terms = document.processed_content.split()
        term_freq = Counter(terms)

        vector = [0.0] * self.vocabulary.get_vocabulary_size()

        # Вычисляем TF-IDF для каждого термина в документе
        for term, tf in term_freq.items():
            term_idx = self.vocabulary.get_term_index(term)
            if term_idx != -1:
                idf = self._calculate_idf(term)
                vector[term_idx] = tf * idf

        # Нормализуем вектор (евклидова норма)
        norm = self._calculate_euclidean_norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]

        return vector

    def _calculate_idf(self, term: str) -> float:
        """
        Вычисляет обратную частоту документа (IDF) по формуле из задания
        IDF(t) = log(N / (df(t) + 1))
        """
        df = self.vocabulary.get_document_frequency(term)
        if df == 0:
            return 0.0
        return math.log(self.vocabulary.total_documents / (df + 1))

    def _calculate_euclidean_norm(self, vector: List[float]) -> float:
        """Вычисляет евклидову норму вектора"""
        return sum(x ** 2 for x in vector) ** 0.5

    def query_to_tfidf_vector(self, query_terms: List[str]) -> List[float]:
        """
        Преобразует запрос в вектор TF-IDF
        Согласно заданию: w_qj = 1 если термин присутствует в запросе
        """
        vector = [0.0] * self.vocabulary.get_vocabulary_size()

        for term in query_terms:
            term_idx = self.vocabulary.get_term_index(term)
            if term_idx != -1:
                # Бинарное представление как в задании
                vector[term_idx] = 1.0

        # Нормализуем вектор запроса
        norm = self._calculate_euclidean_norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]

        return vector

    def get_term_weights_for_document(self, doc_id: int, tfidf_vectors: Dict) -> List[Tuple[str, float]]:
        """
        Возвращает список (термин, вес) для конкретного документа
        """
        vector = tfidf_vectors.get(doc_id, [])
        weighted_terms = []

        for idx, weight in enumerate(vector):
            if weight > 0:
                term = self.vocabulary.get_term_by_index(idx)
                weighted_terms.append((term, weight))

        # Сортируем по весу по убыванию
        return sorted(weighted_terms, key=lambda x: x[1], reverse=True)