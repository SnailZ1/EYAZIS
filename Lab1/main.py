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


def main():
    parser = argparse.ArgumentParser(description='Информационно-поисковая система')
    parser.add_argument('--build-index', action='store_true',
                        help='Построить поисковый индекс')
    parser.add_argument('--web', action='store_true',
                        help='Запустить веб-интерфейс')
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
    if not any([args.build_index, args.web]):
        parser.print_help()
        return

    # Построение индекса
    if args.build_index:
        build_search_index(args.docs)
        print("\n" + "=" * 50)

    # Запуск веб-интерфейса
    if args.web:
        run_web_interface(host=args.host, port=args.port)


if __name__ == '__main__':
    main()