from documents_processing.collector import DocumentCollector
from text_preprocessing.preprocessor_factory import PreprocessorFactory
from text_preprocessing.batching import BatchTextPreprocessor
from text_preprocessing.utils import PreprocessingUtils

def main():
    """Основная функция для демонстрации работы системы"""
    
    # 1. Сбор документов
    print("=== СБОР ДОКУМЕНТОВ ===")
    collector = DocumentCollector()
    documents = collector.collect_documents("./docs", use_file_metadata=True)
    
    # Выводим статистику
    stats = collector.get_documents_stats()
    print(stats)
    print(f"Собрано документов: {stats['total_documents']}")
    
    # 2. Предобработка текстов
    print("\n=== ПРЕДОБРАБОТКА ТЕКСТОВ ===")
    preprocessor = PreprocessorFactory.create_lemmatization_preprocessor()
    batch_processor = BatchTextPreprocessor(preprocessor)
    
    # Обрабатываем коллекцию
    processing_stats = batch_processor.preprocess_collection(documents)
    batch_processor.print_statistics()
    
    # 3. Сохранение результатов
    print("\n=== СОХРАНЕНИЕ РЕЗУЛЬТАТОВ ===")
    PreprocessingUtils.save_processed_documents(documents, "processed_documents.json")
    print("Результаты сохранены в 'processed_documents.json'")
    
    # 4. Демонстрация работы
    print("\n=== ДЕМОНСТРАЦИЯ ===")
    if documents:
        first_doc = documents[0]
        print(f"Документ: {first_doc.title}")
        print(f"Оригинал: {first_doc.content[:200]}...")
        print(f"Обработанный: {first_doc.processed_content[:200]}...")

if __name__ == "__main__":
    main()