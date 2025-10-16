from typing import List, Dict

class BatchTextPreprocessor:
    """
    Класс для пакетной предобработки коллекции документов
    """
    
    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        self.stats = {}
    
    def preprocess_collection(self, documents: List) -> Dict:
        """Предобработка всей коллекции документов"""
        if not documents:
            return {}
        
        total_stats = {
            'total_documents': len(documents),
            'total_tokens': 0,
            'total_unique_tokens': set(),
            'avg_tokens_per_doc': 0,
            'document_stats': []
        }
        
        print(f"Начинаем предобработку {len(documents)} документов...")
        
        for i, doc in enumerate(documents, 1):
            print(f"Обработка документа {i}/{len(documents)}: {doc.title}")
            
            doc_stats = self.preprocessor.preprocess_document(doc)
            total_stats['total_tokens'] += doc_stats['token_count']
            total_stats['total_unique_tokens'].update(doc_stats['unique_tokens'])
            
            doc_stat = {
                'doc_id': doc.doc_id,
                'title': doc.title,
                'token_count': doc_stats['token_count'],
                'vocabulary_size': doc_stats['vocabulary_size'],
                'original_length': len(doc.content),
                'processed_length': len(doc.processed_content)
            }
            total_stats['document_stats'].append(doc_stat)
        
        total_stats['avg_tokens_per_doc'] = total_stats['total_tokens'] / len(documents)
        total_stats['total_vocabulary_size'] = len(total_stats['total_unique_tokens'])
        
        self.stats = total_stats
        return total_stats
    
    def print_statistics(self):
        """Вывод статистики предобработки"""
        if not self.stats:
            print("Статистика недоступна. Сначала выполните предобработку.")
            return
        
        stats = self.stats
        print("\n" + "="*60)
        print("СТАТИСТИКА ПРЕДОБРАБОТКИ ТЕКСТА")
        print("="*60)
        print(f"Всего документов: {stats['total_documents']}")
        print(f"Всего токенов: {stats['total_tokens']}")
        print(f"Размер словаря: {stats['total_vocabulary_size']}")
        print(f"Среднее токенов на документ: {stats['avg_tokens_per_doc']:.1f}")
        
        if stats['document_stats']:
            first_doc = stats['document_stats'][0]
            print(f"\nПример обработанного документа:")
            print(f"Документ ID: {first_doc['doc_id']}")
            print(f"Токенов: {first_doc['token_count']}")
            print(f"Уникальных слов: {first_doc['vocabulary_size']}")
            print(f"Сжатие: {(1 - first_doc['processed_length'] / first_doc['original_length']) * 100:.1f}%")