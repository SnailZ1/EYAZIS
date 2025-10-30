# main.py
import sys
import os
import argparse
from documents_processing.collector import DocumentCollector
from text_preprocessing.preprocessor_factory import PreprocessorFactory
from text_preprocessing.batching import BatchTextPreprocessor
from indexing.index_builder import IndexBuilder
from web_interface.app import SearchApp


def build_search_index(docs_directory: str = "docs"):
    """Построение поискового индекса"""
    print("=== ПОСТРОЕНИЕ ПОИСКОВОГО ИНДЕКСА ===")

    # 1. Сбор документов
    print("\n1. СБОР ДОКУМЕНТОВ")
    collector = DocumentCollector()
    documents = collector.collect_documents(docs_directory)

    if not documents:
        print("Не найдено документов для обработки!")
        return None

    # 2. Предобработка текстов
    print("\n2. ПРЕДОБРАБОТКА ТЕКСТОВ")
    preprocessor = PreprocessorFactory.create_lemmatization_preprocessor()
    batch_processor = BatchTextPreprocessor(preprocessor)
    batch_processor.preprocess_collection(documents)
    batch_processor.print_statistics()

    # 3. Построение индекса с векторной БД
    print("\n3. ПОСТРОЕНИЕ ИНДЕКСА")
    index_builder = IndexBuilder(use_vector_db=True, use_semantic_search=True)
    index_builder.build_index(documents)

    # 4. Сохранение индекса
    print("\n4. СОХРАНЕНИЕ ИНДЕКСА")
    index_builder.save_index("search_index")

    # 5. Статистика
    print("\n5. СТАТИСТИКА")
    index_builder.print_detailed_statistics()

    return index_builder


def run_web_interface(host='127.0.0.1', port=5000, debug=True):
    """Запуск веб-интерфейса"""
    print("=== ЗАПУСК ВЕБ-ИНТЕРФЕЙСА ===")

    # Создаем и запускаем веб-приложение
    search_app = SearchApp()
    search_app.run(host=host, port=port, debug=debug)

def test_search_system():
    """Тестирование поисковой системы с гибридным селектором"""
    print("=== ТЕСТИРОВАНИЕ ПОИСКОВОЙ СИСТЕМЫ С ГИБРИДНЫМ СЕЛЕКТОРОМ ===")

    try:
        from text_preprocessing.preprocessor_factory import PreprocessorFactory
        from indexing.index_builder import IndexBuilder
        from documents_processing.collector import DocumentCollector
        from text_preprocessing.batching import BatchTextPreprocessor
        from vector_storage.chroma_storage import ChromaStorage

        # Загружаем документы
        collector = DocumentCollector()
        documents = collector.collect_documents("docs", recursive=True)
        
        if not documents:
            print("❌ Нет документов для тестирования")
            return

        # Предобрабатываем
        preprocessor = PreprocessorFactory.create_lemmatization_preprocessor()
        batch_processor = BatchTextPreprocessor(preprocessor)
        batch_processor.preprocess_collection(documents)

        # Загружаем существующий индекс С селектором
        index_builder = IndexBuilder(
            use_vector_db=True,
            use_document_selector=True,  # ВКЛЮЧАЕМ селектор!
            use_semantic_search=False
        )
        
        try:
            index_builder.vocabulary.load_vocabulary("search_index/vocabulary.json")
            index_builder.vector_storage = ChromaStorage()
            from indexing.tfidf_calculator import TFIDFCalculator
            index_builder.tfidf_calculator = TFIDFCalculator(index_builder.vocabulary)
            index_builder.all_documents = documents  
        except:
            print("⚠️  Индекс не найден, строим с нуля...")
            index_builder.build_index(documents)
            index_builder.save_index("search_index")

        # Тестовые запросы
        test_queries = [
            "computer science and artificial intelligence",
            "data analysis and machine learning", 
            "programming and development"
        ]

        print("\n🧪 Тестирование гибридного селектора:")
        for query in test_queries:
            print(f"\n🔍 Запрос: '{query}'")

            # Поиск с селектором
            results = index_builder.search(query, preprocessor, top_k=3)
            
            # Статистика селектора
            if index_builder.document_selector:
                stats = index_builder.document_selector.get_selection_statistics()
                print(f"📊 Статистика селектора: {stats}")

            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['metadata']['title']} " 
                          f"(сходство: {result['similarity_score']:.3f})")
            else:
                print("  ❌ Ничего не найдено")

    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

    
def test_document_selector():
    """Тестирование модуля отбора документов"""
    print("=== ТЕСТИРОВАНИЕ МОДУЛЯ ОТБОРА ДОКУМЕНТОВ ===")

    try:
        from document_selector.hybrid_selector import HybridDocumentSelector
        from document_selector.rule_based_selector import RuleBasedSelector
        from text_preprocessing.preprocessor_factory import PreprocessorFactory

        # Загружаем документы для теста
        collector = DocumentCollector()
        documents = collector.collect_documents("docs", recursive=True)

        if not documents:
            print("Нет документов для тестирования")
            return

        # Предобработка
        preprocessor = PreprocessorFactory.create_lemmatization_preprocessor()
        batch_processor = BatchTextPreprocessor(preprocessor)
        batch_processor.preprocess_collection(documents)

        # Тестируем RuleBasedSelector
        print("\n1. Тестирование RuleBasedSelector:")
        rule_selector = RuleBasedSelector()
        test_query = "computer science data"

        selected_docs = rule_selector.select_documents(test_query, documents, top_k=5)
        print(f"Отобрано документов: {len(selected_docs)}")
        print("Статистика отбора:", rule_selector.get_selection_stats())

        for i, doc in enumerate(selected_docs, 1):
            explanation = rule_selector.explain_selection(test_query, doc)
            print(f"  {i}. {doc.title} (score: {explanation['total_score']:.2f})")

        # Тестируем объяснение для первого документа
        if selected_docs:
            first_doc = selected_docs[0]
            detailed_explanation = rule_selector.explain_selection(test_query, first_doc)
            print(f"\nДетальное объяснение для '{first_doc.title}':")
            for factor in detailed_explanation['factors']:
                print(f"  - {factor['factor']}: {factor['score']:.2f} * {factor['weighted_score']:.2f}")

    except Exception as e:
        print(f"Ошибка тестирования селектора: {e}")

def main():
    parser = argparse.ArgumentParser(description='Информационно-поисковая система')
    parser.add_argument('--build-index', action='store_true',
                        help='Построить поисковый индекс')
    parser.add_argument('--web', action='store_true',
                        help='Запустить веб-интерфейс')
    parser.add_argument('--use-word2vec', action='store_true',
                        help='Использовать Word2Vec для семантического поиска')
    parser.add_argument('--word2vec-model', default='models/word2vec.bin',
                        help='Путь к модели Word2Vec')
    parser.add_argument('--test', action='store_true',
                        help='Протестировать поисковую систему')
    parser.add_argument('--test-selector', action='store_true',
                        help='Протестировать модуль отбора документов')
    parser.add_argument('--host', default='127.0.0.1',
                        help='Хост для веб-интерфейса (по умолчанию: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Порт для веб-интерфейса (по умолчанию: 5000)')
    parser.add_argument('--docs', default='docs',
                        help='Папка с документами (по умолчанию: docs)')

    args = parser.parse_args()

    print("=== ИНФОРМАЦИОННО-ПОИСКОВАЯ СИСТЕМА ===")
    print("Вариант 33: Векторная модель, Английский язык")
    print("Лабораторная работа #7 - БГУИР 2024")
    print()

    # Если не указаны аргументы, показываем справку
    if not any([args.build_index, args.web, args.test]):
        parser.print_help()
        return

    # Построение индекса
    if args.build_index:
        build_search_index(args.docs)
        print("\n" + "=" * 50)

    # Тестирование системы
    if args.test:
        test_search_system()
        print("\n" + "=" * 50)

    if args.test_selector:
        test_document_selector()
        print("\n" + "=" * 50)

    # Запуск веб-интерфейса
    if args.web:
        run_web_interface(host=args.host, port=args.port)

    if args.use_word2vec:
        print("🔍 Активация семантического поиска Word2Vec...")
        # Проверяем наличие модели
        if not os.path.exists(args.word2vec_model):
            print("❌ Модель Word2Vec не найдена. Создаем тестовую...")
            from scripts.download_model import download_word2vec_model
            args.word2vec_model = download_word2vec_model()


if __name__ == '__main__':
    main()