# indexing/tfidf_calculator.py
from typing import List, Dict, Tuple
import math
from collections import Counter


class TFIDFCalculator:
    """
    Класс для расчета TF-IDF весов терминов в документах и запросах
    """

    def __init__(self, vocabulary):
        self.vocabulary = vocabulary

    def calculate_tfidf_weights(self, documents: List) -> Dict[int, List[float]]:
        """
        Вычисляет TF-IDF веса для всех документов
        """
        print("Начинаем расчет TF-IDF весов...")

        tfidf_vectors = {}

        for doc in documents:
            if hasattr(doc, 'processed_content') and doc.processed_content:
                vector = self._document_to_tfidf_vector(doc)
                tfidf_vectors[doc.doc_id] = vector
                doc.tfidf_vector = vector

        print(f"Расчет TF-IDF завершен. Обработано документов: {len(tfidf_vectors)}")
        return tfidf_vectors

    def _document_to_tfidf_vector(self, document) -> List[float]:
        """
        Преобразует документ в вектор TF-IDF
        """
        if not hasattr(document, 'processed_content') or not document.processed_content:
            return [0.0] * self.vocabulary.get_vocabulary_size()

        # Разбиваем на термины
        terms = document.processed_content.split()
        term_freq = Counter(terms)

        vector = [0.0] * self.vocabulary.get_vocabulary_size()
        total_terms = len(terms)

        if total_terms == 0:
            return vector

        # Вычисляем TF-IDF для каждого термина в документе
        for term, count in term_freq.items():
            term_idx = self.vocabulary.get_term_index(term)
            if term_idx != -1:
                # TF (Term Frequency) - нормализованная частота
                tf = count / total_terms
                # IDF (Inverse Document Frequency)
                idf = self._calculate_idf(term)
                vector[term_idx] = tf * idf

        # Нормализуем вектор (евклидова норма)
        norm = self._calculate_euclidean_norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]

        return vector

    def process_query(self, query_text: str, preprocessor) -> Tuple[List[str], List[float]]:
        """
        Полная предобработка запроса
        """
        print(f"Предобработка запроса: '{query_text}'")

        # 1. Предобработка текста запроса
        processed_terms = preprocessor.preprocess_text(query_text, return_string=False)
        print(f"Термины после предобработки: {processed_terms}")

        # 2. Векторизация запроса
        query_vector = self.query_to_tfidf_vector(processed_terms)

        # Отладочная информация
        non_zero_terms = []
        for i, weight in enumerate(query_vector):
            if weight > 0:
                term = self.vocabulary.get_term_by_index(i)
                non_zero_terms.append((term, weight))

        print(f"Ненулевые термины в векторе запроса: {non_zero_terms}")

        return processed_terms, query_vector

    def query_to_tfidf_vector(self, query_terms: List[str]) -> List[float]:
        """
        Преобразует предобработанные термины запроса в вектор TF-IDF
        """
        vector = [0.0] * self.vocabulary.get_vocabulary_size()

        if not query_terms:
            return vector

        # Подсчитываем TF в запросе
        term_freq = Counter(query_terms)
        total_terms = len(query_terms)

        print(f"Векторизация {len(query_terms)} терминов запроса:")

        for term, count in term_freq.items():
            term_idx = self.vocabulary.get_term_index(term)
            if term_idx != -1:
                # TF в запросе (нормализованная частота)
                tf = count / total_terms
                # IDF из словаря документов
                idf = self._calculate_idf(term)
                weight = tf * idf
                vector[term_idx] = weight

                print(f"   '{term}': TF={tf:.3f}, IDF={idf:.3f}, вес={weight:.4f}")
            else:
                print(f"    '{term}': НЕТ В СЛОВАРЕ")

        # Нормализуем вектор запроса
        norm = self._calculate_euclidean_norm(vector)
        print(f"Норма вектора до нормализации: {norm:.4f}")

        if norm > 0:
            vector = [v / norm for v in vector]
            print(f"Вектор запроса нормализован")
        else:
            print(f"Вектор запроса нулевой - нет совпадающих терминов")

        return vector

    def _calculate_idf(self, term: str) -> float:
        """
        Вычисляет обратную частоту документа (IDF)
        IDF(t) = log(N / (df(t) + 1))
        """
        df = self.vocabulary.get_document_frequency(term)
        N = self.vocabulary.total_documents

        if df == 0:
            return 0.0

        idf = math.log(N / (df + 1))
        return idf

    def _calculate_euclidean_norm(self, vector: List[float]) -> float:
        """Вычисляет евклидову норму вектора"""
        return sum(x ** 2 for x in vector) ** 0.5

    def debug_query_processing(self, query_text: str, preprocessor):
        """
        Детальная отладка обработки запроса
        """
        print("\n" + "=" * 50)
        print("ДЕТАЛЬНАЯ ОТЛАДКА ОБРАБОТКИ ЗАПРОСА")
        print("=" * 50)

        # Исходный запрос
        print(f"Исходный запрос: '{query_text}'")

        # Предобработка
        processed_terms = preprocessor.preprocess_text(query_text, return_string=False)
        print(f"Обработанные термины: {processed_terms}")

        # Анализ каждого термина
        print("\nАнализ терминов:")
        for term in set(processed_terms):
            term_idx = self.vocabulary.get_term_index(term)
            if term_idx != -1:
                df = self.vocabulary.get_document_frequency(term)
                idf = self._calculate_idf(term)
                print(f"  '{term}': в словаре (DF={df}, IDF={idf:.3f})")
            else:
                print(f"  '{term}': нет в словаре")

        # Векторизация
        query_vector = self.query_to_tfidf_vector(processed_terms)

        print(f"\nИтоговый вектор: {len(query_vector)} размерность")
        print(f"Ненулевых компонент: {sum(1 for x in query_vector if x > 0)}")

        return processed_terms, query_vector