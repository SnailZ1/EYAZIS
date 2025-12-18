import os
from datetime import datetime
import PyPDF2
import docx

class MetadataExtractor:
    """Класс для извлечения метаданных из файлов"""
    
    @staticmethod
    def get_file_dates(file_path):
        """
        Получает даты создания и изменения файла из файловой системы
        """
        try:
            stat = os.stat(file_path)
            created_timestamp = stat.st_ctime
            modified_timestamp = stat.st_mtime
            
            date_created = datetime.fromtimestamp(created_timestamp).strftime("%Y-%m-%d %H:%M:%S")
            date_modified = datetime.fromtimestamp(modified_timestamp).strftime("%Y-%m-%d %H:%M:%S")
            
            return date_created, date_modified
        except Exception as e:
            print(f"Ошибка получения дат файла {file_path}: {e}")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return current_time, current_time
    
    @staticmethod
    def get_pdf_metadata(file_path):
        """Получает метаданные из PDF файла"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                created_date = None
                modified_date = None
                
                if metadata:
                    if '/CreationDate' in metadata:
                        created_date = MetadataExtractor._parse_pdf_date(metadata['/CreationDate'])
                    if '/ModDate' in metadata:
                        modified_date = MetadataExtractor._parse_pdf_date(metadata['/ModDate'])
                
                return created_date, modified_date
        except Exception as e:
            print(f"Ошибка чтения метаданных PDF {file_path}: {e}")
            return None, None
    
    @staticmethod
    def _parse_pdf_date(pdf_date):
        """Парсит дату из формата PDF"""
        if not pdf_date:
            return None
        
        try:
            pdf_date = pdf_date.replace('D:', '').strip()
            year = int(pdf_date[0:4]) if len(pdf_date) >= 4 else datetime.now().year
            month = int(pdf_date[4:6]) if len(pdf_date) >= 6 else 1
            day = int(pdf_date[6:8]) if len(pdf_date) >= 8 else 1
            hour = int(pdf_date[8:10]) if len(pdf_date) >= 10 else 0
            minute = int(pdf_date[10:12]) if len(pdf_date) >= 12 else 0
            second = int(pdf_date[12:14]) if len(pdf_date) >= 14 else 0
            
            date_obj = datetime(year, month, day, hour, minute, second)
            return date_obj.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"Ошибка парсинга PDF даты {pdf_date}: {e}")
            return None
    
    @staticmethod
    def get_docx_metadata(file_path):
        """Получает метаданные из DOCX файла"""
        try:
            doc = docx.Document(file_path)
            core_properties = doc.core_properties
            
            created_date = None
            modified_date = None
            
            if core_properties.created:
                created_date = core_properties.created.strftime("%Y-%m-%d %H:%M:%S")
            if core_properties.modified:
                modified_date = core_properties.modified.strftime("%Y-%m-%d %H:%M:%S")
            
            return created_date, modified_date
        except Exception as e:
            print(f"Ошибка чтения метаданных DOCX {file_path}: {e}")
            return None, None