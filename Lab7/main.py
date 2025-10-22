from documents_processing.collector import DocumentCollector
from text_preprocessing.preprocessor_factory import PreprocessorFactory
from text_preprocessing.batching import BatchTextPreprocessor
from text_preprocessing.utils import PreprocessingUtils
from indexing.index_builder import IndexBuilder


def main():
    """Полный процесс построения поисковой системы"""

    print("=== СИСТЕМА ИНФОРМАЦИОННОГО ПОИСКА ===")
    print("Вариант 33: Модуль отбора документов, ЛВС, Векторная модель, Английский")

    # 1. Сбор документов
    print("\n1. СБОР ДОКУМЕНТОВ")
    collector = DocumentCollector()
    documents = collector.collect_documents("docs")

    if not documents:
        print("Не найдено документов для обработки!")
        return

    # 2. Предобработка текстов
    print("\n2. ПРЕДОБРАБОТКА ТЕКСТОВ")
    preprocessor = PreprocessorFactory.create_lemmatization_preprocessor()
    batch_processor = BatchTextPreprocessor(preprocessor)
    batch_processor.preprocess_collection(documents)
    batch_processor.print_statistics()

    # 3. Построение индекса (словарь + TF-IDF)
    print("\n3. ПОСТРОЕНИЕ ИНДЕКСА")
    index_builder = IndexBuilder()
    index_builder.build_index(documents)

    # 4. Сохранение индекса
    print("\n4. СОХРАНЕНИЕ ИНДЕКСА")
    index_builder.save_index("search_index")

    # 5. Статистика
    print("\n5. СТАТИСТИКА")
    index_builder.print_detailed_statistics()

    print("\n=== ПРОЦЕСС ЗАВЕРШЕН ===")


if __name__ == "__main__":
    main()