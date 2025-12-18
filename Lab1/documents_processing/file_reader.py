import PyPDF2
import docx

class FileReader:
    """Класс для чтения файлов различных форматов"""
    
    @staticmethod
    def read_txt(file_path):
        """Чтение текстовых файлов"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='cp1251') as file:
                    return file.read()
            except:
                return ""
        except Exception as e:
            print(f"Ошибка чтения TXT файла {file_path}: {e}")
            return ""
    
    @staticmethod
    def read_pdf(file_path):
        """Чтение PDF файлов"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"Ошибка чтения PDF файла {file_path}: {e}")
            return ""
    
    @staticmethod
    def read_docx(file_path):
        """Чтение DOCX файлов"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Ошибка чтения DOCX файла {file_path}: {e}")
            return ""