# indexing/index_builder.py
from typing import List, Dict
import json
from .vocabulary import Vocabulary
from .tfidf_calculator import TFIDFCalculator
from vector_storage.chroma_storage import ChromaStorage
from document_selector.hybrid_selector import HybridDocumentSelector

class IndexBuilder:
    """
    Класс для построения и сохранения поискового индекса
    """

    def __init__(self, use_vector_db: bool = True, use_document_selector: bool = True):
        self.vocabulary = Vocabulary()
        self.tfidf_calculator = None
        self.tfidf_vectors = {}
        self.use_vector_db = use_vector_db
        self.vector_storage = None
        self.document_selector = None

        if use_vector_db:
            self.vector_storage = ChromaStorage()

        if use_document_selector:
            self.document_selector = HybridDocumentSelector(
                use_pre_selection=True,
                use_ranking_enhancement=True
            )

    def build_index(self, documents: List) -> None:
        """
        Полный процесс построения индекса:
        1. Построение словаря
        2. Расчет TF-IDF весов
        3. Сохранение в векторную БД (если включено)
        """
        print("=== НАЧАЛО ПОСТРОЕНИЯ ИНДЕКСА ===")

        # 1. Построение словаря
        self.vocabulary.build_from_documents(documents)

        # 2. Расчет TF-IDF весов
        self.tfidf_calculator = TFIDFCalculator(self.vocabulary)
        self.tfidf_vectors = self.tfidf_calculator.calculate_tfidf_weights(documents)

        # 3. Сохранение в векторную БД
        if self.use_vector_db and self.vector_storage:
            self.vector_storage.store_documents(documents, self.tfidf_vectors)

        print("=== ПОСТРОЕНИЕ ИНДЕКСА ЗАВЕРШЕНО ===")

    def save_index(self, base_path: str) -> None:
        """
        Сохраняет индекс в файлы:
        - vocabulary.json - словарь
        - index_metadata.json - метаданные индекса
        """
        import os
        os.makedirs(base_path, exist_ok=True)

        # Сохраняем словарь (все еще нужен для обработки запросов)
        vocab_path = f"{base_path}/vocabulary.json"
        self.vocabulary.save_vocabulary(vocab_path)

        # Сохраняем метаданные
        metadata = {
            'vocabulary_size': self.vocabulary.get_vocabulary_size(),
            'total_documents': self.vocabulary.total_documents,
            'use_vector_db': self.use_vector_db,
            'vector_db_documents': self.vector_storage.get_document_count() if self.vector_storage else 0,
            'index_version': '2.0',
            'description': 'Vector space model index with ChromaDB storage'
        }

        metadata_path = f"{base_path}/index_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"Индекс сохранен. Векторная БД: {metadata['vector_db_documents']} документов")

    def search(self, query_text: str, preprocessor, top_k: int = 10) -> List[Dict]:
        """
        Поиск документов по запросу с полной предобработкой
        """
        if not self.vector_storage:
            raise ValueError("Векторная БД не инициализирована")

        if not self.tfidf_calculator:
            raise ValueError("TF-IDF калькулятор не инициализирован")

        # Полная предобработка запроса
        processed_terms, query_vector = self.tfidf_calculator.process_query(query_text, preprocessor)

        # Логирование для отладки
        print(f"Обработанные термины запроса: {processed_terms}")
        print(f"Размер вектора запроса: {len(query_vector)}")
        print(f"Ненулевые компоненты: {sum(1 for x in query_vector if x > 0)}")

        # Ищем в векторной БД
        results = self.vector_storage.search_similar(query_vector, top_k)

        # Добавляем информацию о терминах запроса в результаты
        for result in results:
            result['query_terms'] = processed_terms

        return results

    def analyze_query(self, query_text: str, preprocessor) -> Dict:
        """
        Анализ запроса: показывает какие термины были извлечены и их веса
        """
        if not self.tfidf_calculator:
            return {'error': 'TF-IDF калькулятор не инициализирован'}

        processed_terms, query_vector = self.tfidf_calculator.process_query(query_text, preprocessor)

        # Анализ терминов и их весов
        term_analysis = []
        for term in set(processed_terms):
            term_idx = self.vocabulary.get_term_index(term)
            if term_idx != -1:
                weight = query_vector[term_idx]
                df = self.vocabulary.get_document_frequency(term)
                idf = self.tfidf_calculator._calculate_idf(term)
                term_analysis.append({
                    'term': term,
                    'in_vocabulary': True,
                    'document_frequency': df,
                    'idf': round(idf, 4),
                    'weight_in_query': round(weight, 4)
                })
            else:
                term_analysis.append({
                    'term': term,
                    'in_vocabulary': False,
                    'document_frequency': 0,
                    'idf': 0,
                    'weight_in_query': 0
                })

        return {
            'original_query': query_text,
            'processed_terms': processed_terms,
            'term_analysis': term_analysis,
            'query_vector_length': len(query_vector),
            'non_zero_components': sum(1 for x in query_vector if x > 0)
        }

    def get_index_statistics(self) -> Dict:
        """Возвращает статистику индекса"""
        vocab_stats = self.vocabulary.get_statistics()

        stats = {
            **vocab_stats,
            'use_vector_db': self.use_vector_db,
            'vector_db_documents': self.vector_storage.get_document_count() if self.vector_storage else 0,
            'tfidf_vectors_calculated': len(self.tfidf_vectors)
        }

        if self.vector_storage:
            stats.update(self.vector_storage.get_collection_info())

        return stats

    def print_detailed_statistics(self) -> None:
        """Выводит детальную статистику индекса"""
        stats = self.get_index_statistics()

        print("\n" + "=" * 60)
        print("ДЕТАЛЬНАЯ СТАТИСТИКА ИНДЕКСА")
        print("=" * 60)
        print(f"Размер словаря: {stats['vocabulary_size']}")
        print(f"Количество документов: {stats['total_documents']}")
        print(f"Используется векторная БД: {'Да' if stats['use_vector_db'] else 'Нет'}")

        if stats['use_vector_db']:
            print(f"Документов в векторной БД: {stats['vector_db_documents']}")
            print(f"Коллекция: {stats['name']}")
            print(f"Папка хранения: {stats['persist_directory']}")

        print(f"\nСамые частые термины:")
        for term, freq in stats['most_frequent_terms']:
            print(f"  {term}: {freq} документов")

    def search_with_selection(self, query_text: str, preprocessor,
                              all_documents: List, top_k: int = 10) -> List[Dict]:
        """
        Поиск с интеллектуальным отбором документов
        """
        if not self.document_selector:
            # Если селектор не используется, выполняем обычный поиск
            return self.search(query_text, preprocessor, top_k)

        # Функция для точного поиска (будет использоваться селектором)
        def exact_search(query, documents, k):
            processed_terms, query_vector = self.tfidf_calculator.process_query(query, preprocessor)
            # Здесь должна быть логика поиска по подмножеству документов
            # Для простоты используем существующий метод
            return self.vector_storage.search_similar(query_vector, k)

        # Используем гибридный селектор
        results = self.document_selector.process_search(
            query_text, all_documents, exact_search, top_k
        )

        return results

    def get_selection_stats(self) -> Dict:
        """
        Возвращает статистику отбора документов
        """
        if self.document_selector:
            return self.document_selector.get_selection_statistics()
        return {'document_selector': 'not_used'}