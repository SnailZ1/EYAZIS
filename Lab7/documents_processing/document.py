from datetime import datetime

class Document:
    """
    Класс для представления документа в информационно-поисковой системе
    """
    def __init__(self, doc_id, title, content, file_path, file_type, file_size=0, date_created=None, date_modified=None):
        self.doc_id = doc_id
        self.title = title
        self.content = content
        self.file_path = file_path
        self.file_type = file_type
        self.file_size = file_size
        self.date_created = date_created or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date_modified = date_modified or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.processed_content = ""
        self.vector = None
    
    def __str__(self):
        return f"Document(id={self.doc_id}, title='{self.title}', type={self.file_type}, created={self.date_created})"
    
    def __repr__(self):
        return self.__str__()
    
    def get_snippet(self, max_length=300):
        """Возвращает фрагмент текста документа"""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:]
    
    def get_metadata(self):
        """Возвращает метаданные документа"""
        return {
            'documentId': self.doc_id,
            'title': self.title,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'date_created': self.date_created,
            'date_modified': self.date_modified,
            'date_added': self.date_added,
            'content_length': len(self.content)
        }