import json
from typing import List

class PreprocessingUtils:
    """Утилиты для работы с предобработанными данными"""
    
    @staticmethod
    def save_processed_documents(documents: List, filepath: str):
        """Сохраняет предобработанные документы в файл"""
        data = []
        for doc in documents:
            doc_data = {
                'doc_id': doc.doc_id,
                'title': doc.title,
                'original_content': doc.content,
                'processed_content': doc.processed_content,
                'file_path': doc.file_path,
                'file_type': doc.file_type,
                'date_created': doc.date_created
            }
            data.append(doc_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_processed_documents(filepath: str):
        """Загружает предобработанные документы из файла"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = []
        for item in data:
            doc = type('Document', (), {
                'doc_id': item['doc_id'],
                'title': item['title'],
                'content': item['original_content'],
                'processed_content': item['processed_content'],
                'file_path': item['file_path'],
                'file_type': item['file_type'],
                'date_created': item['date_created']
            })()
            documents.append(doc)
        
        return documents