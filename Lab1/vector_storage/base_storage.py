# vector_storage/base_storage.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class VectorStorage(ABC):
    """Абстрактный класс для векторного хранилища"""

    @abstractmethod
    def store_documents(self, documents: List, tfidf_vectors: Dict[int, List[float]]) -> None:
        """Сохраняет документы и их векторы в хранилище"""
        pass

    @abstractmethod
    def search_similar(self, query_vector: List[float], top_k: int = 10) -> List[Dict]:
        """Поиск похожих документов по вектору запроса"""
        pass

    @abstractmethod
    def get_document_count(self) -> int:
        """Возвращает количество документов в хранилище"""
        pass

    @abstractmethod
    def clear_storage(self) -> None:
        """Очищает хранилище"""
        pass