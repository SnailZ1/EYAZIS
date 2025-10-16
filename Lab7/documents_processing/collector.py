import os
import glob
import re
from .document import Document
from .file_reader import FileReader
from .metadata_collect import MetadataExtractor
from datetime import datetime
from langdetect import detect, LangDetectException

class DocumentCollector:
    """
    Класс для сбора и обработки документов из директории
    """
    
    def __init__(self, supported_extensions=None):
        if supported_extensions is None:
            self.supported_extensions = {
                '.txt': FileReader.read_txt,
                '.pdf': FileReader.read_pdf,
                '.docx': FileReader.read_docx,
                '.doc': FileReader.read_docx
            }
        else:
            self.supported_extensions = supported_extensions
        
        self.documents = []
        self.next_id = 1
    
    def _get_file_title(self, file_path):
        """Извлекает заголовок из имени файла"""
        base_name = os.path.basename(file_path)
        name_without_ext = os.path.splitext(base_name)[0]
        title = re.sub(r'[_-]', ' ', name_without_ext)
        return title.title()
    
    def _is_text_file(self, file_path):
        """Проверяет, является ли файл текстовым и поддерживаемым"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_extensions
    
    def _is_english(self, text):
        """Проверяет, написан ли текст на английском языке"""
        try:
            if not text.strip():
                return False
            lang = detect(text)
            return lang == 'en'
        except LangDetectException:
            return False
        except Exception as e:
            print(f"Ошибка определения языка: {e}")
            return False
    
    def collect_documents(self, directory_path, recursive=True, use_file_metadata=True):
        """
        Собирает все документы из указанной директории
        """
        if not os.path.exists(directory_path):
            print(f"Директория {directory_path} не существует!")
            return []
        
        print(f"Начинаем сбор документов из: {directory_path}")
        
        pattern = os.path.join(directory_path, "**", "*") if recursive else os.path.join(directory_path, "*")
        all_files = glob.glob(pattern, recursive=recursive)
        text_files = [f for f in all_files if os.path.isfile(f) and self._is_text_file(f)]
        
        print(f"Найдено {len(text_files)} поддерживаемых файлов")
        
        for file_path in text_files:
            try:
                _, ext = os.path.splitext(file_path.lower())
                content = self.supported_extensions[ext](file_path)
                
                if content and content.strip():

                    if not self._is_english(content):
                        break

                    if use_file_metadata:
                        date_created, date_modified = MetadataExtractor.get_file_dates(file_path)
                    else:
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        date_created, date_modified = current_time, current_time
                    
                    title = self._get_file_title(file_path)
                    file_size = os.path.getsize(file_path)
                    
                    document = Document(
                        doc_id=self.next_id,
                        title=title,
                        content=content,
                        file_path=file_path,
                        file_type=ext.upper(),
                        file_size=file_size,
                        date_created=date_created,
                        date_modified=date_modified
                    )
                    
                    self.documents.append(document)
                    self.next_id += 1
                    print(f"Обработан: {title} ({ext}), создан: {date_created}")
                else:
                    print(f"Пропущен пустой файл: {file_path}")
                    
            except Exception as e:
                print(f"Ошибка обработки файла {file_path}: {e}")
        
        print(f"Сбор документов завершен. Обработано: {len(self.documents)} документов")
        return self.documents

    
    def get_documents_stats(self):
        """Возвращает статистику по собранным документам"""
        if not self.documents:
            return "Нет документов"
        
        from datetime import datetime
        dates = [datetime.strptime(doc.date_created, "%Y-%m-%d %H:%M:%S") for doc in self.documents]
        oldest = min(dates).strftime("%Y-%m-%d")
        newest = max(dates).strftime("%Y-%m-%d")
        
        stats = {
            'total_documents': len(self.documents),
            'total_chars': sum(len(doc.content) for doc in self.documents),
            'file_types': {},
            'avg_chars_per_doc': sum(len(doc.content) for doc in self.documents) / len(self.documents),
            'date_range': f"{oldest} - {newest}",
            'oldest_document': oldest,
            'newest_document': newest
        }
        
        for doc in self.documents:
            stats['file_types'][doc.file_type] = stats['file_types'].get(doc.file_type, 0) + 1
        
        return stats
    
    def get_document_by_id(self, doc_id):
        """Возвращает документ по ID"""
        for doc in self.documents:
            if doc.doc_id == doc_id:
                return doc
        return None
    
    def clear_documents(self):
        """Очищает список документов"""
        self.documents = []
        self.next_id = 1