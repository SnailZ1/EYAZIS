# document_selector/base_selector.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class BaseDocumentSelector(ABC):
    """
    Абстрактный базовый класс для модулей отбора документов
    """

    def __init__(self, name: str = "BaseSelector"):
        self.name = name
        self.stats = {}

    @abstractmethod
    def select_documents(self, query: str, documents: List, top_k: int = 10) -> List:
        """
        Основной метод отбора документов
        """
        pass

    def pre_filter(self, query: str, documents: List) -> List:
        """
        Базовая предварительная фильтрация
        """
        filtered_docs = []
        query_terms = set(query.lower().split())

        for doc in documents:
            # Проверяем наличие хотя бы одного термина запроса
            if hasattr(doc, 'processed_content'):
                doc_terms = set(doc.processed_content.split())
                if query_terms & doc_terms:  # Есть пересечение
                    filtered_docs.append(doc)
            else:
                # Если нет processed_content, используем оригинальный контент
                content_lower = doc.content.lower()
                if any(term in content_lower for term in query_terms):
                    filtered_docs.append(doc)

        return filtered_docs

    def calculate_freshness_score(self, document) -> float:
        """
        Оценка свежести документа (новые документы получают бонус)
        """
        try:
            doc_date = datetime.strptime(document.date_created, "%Y-%m-%d %H:%M:%S")
            days_old = (datetime.now() - doc_date).days

            if days_old < 7:  # Последняя неделя
                return 2.0
            elif days_old < 30:  # Последний месяц
                return 1.5
            elif days_old < 365:  # Последний год
                return 1.0
            else:  # Старые документы
                return 0.5
        except:
            return 0.5

    def calculate_length_score(self, document) -> float:
        """
        Оценка длины документа (средние документы получают бонус)
        """
        content_length = len(document.content)

        if 500 <= content_length <= 5000:  # Идеальная длина
            return 1.5
        elif 100 <= content_length < 500:  # Немного короткий
            return 1.0
        elif content_length > 5000:  # Слишком длинный
            return 0.8
        else:  # Очень короткий
            return 0.5

    def get_selection_stats(self) -> Dict:
        """
        Возвращает статистику отбора
        """
        return self.stats

    def __str__(self) -> str:
        return f"{self.name}(stats={self.stats})"