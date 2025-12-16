# vector_storage/chroma_storage.py
import chromadb
from typing import List, Dict, Any
import numpy as np
from .base_storage import VectorStorage


class ChromaStorage(VectorStorage):
    """Векторное хранилище на основе ChromaDB"""

    def __init__(self, collection_name: str = "document_search", persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Document search system with TF-IDF vectors"}
        )
        self.persist_directory = persist_directory

    def store_documents(self, documents: List, tfidf_vectors: Dict[int, List[float]]) -> None:
        """Сохраняет документы и их векторы в ChromaDB"""
        print("Сохраняем документы в векторную БД...")

        ids = []
        embeddings = []
        metadatas = []
        documents_text = []

        for doc in documents:
            doc_id = str(doc.doc_id)
            vector = tfidf_vectors.get(doc.doc_id)

            if vector is None:
                continue

            # Преобразуем в numpy array и нормализуем для косинусного сходства
            vector_np = np.array(vector, dtype=np.float32)
            norm = np.linalg.norm(vector_np)
            if norm > 0:
                vector_np = vector_np / norm

            ids.append(doc_id)
            embeddings.append(vector_np.tolist())

            metadata = {
                "doc_id": doc.doc_id,
                "title": doc.title,
                "file_path": doc.file_path,
                "file_type": doc.file_type,
                "date_created": doc.date_created,
                "date_added": doc.date_added,
                "content_length": len(doc.content),
                "processed_length": len(doc.processed_content) if hasattr(doc, 'processed_content') else 0
            }
            metadatas.append(metadata)

            documents_text.append(doc.processed_content if hasattr(doc, 'processed_content') else doc.content[:500])

        # Добавляем в коллекцию
        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_text
            )
            print(f"Сохранено документов в векторную БД: {len(ids)}")
        else:
            print("Нет документов для сохранения")

    def search_similar(self, query_vector: List[float], top_k: int = 10) -> List[Dict]:
        """Поиск похожих документов по вектору запроса"""
        if not query_vector or all(x == 0 for x in query_vector):
            print("Запросный вектор нулевой - нет совпадающих терминов")
            return []

        # Нормализуем query vector для косинусного сходства
        query_np = np.array(query_vector, dtype=np.float32)
        query_norm = np.linalg.norm(query_np)
        if query_norm > 0:
            query_np = query_np / query_norm
        else:
            print("Норма query vector равна 0")
            return []

        print(f"Поиск по вектору размерности {len(query_vector)}")
        print(f"Нормализованный query vector: {query_norm:.4f}")

        try:
            results = self.collection.query(
                query_embeddings=[query_np.tolist()],
                n_results=min(top_k, self.collection.count()),
                include=["metadatas", "distances", "documents"]
            )

            formatted_results = []
            if results['ids'] and results['ids'][0]:
                print(f"Найдено результатов: {len(results['ids'][0])}")

                for i, doc_id in enumerate(results['ids'][0]):
                
                    distance = results['distances'][0][i]
                    similarity = abs(distance / 2 - 1)  # Преобразуем расстояние в сходство

                    if not round(similarity, 1): continue

                    formatted_results.append({
                        'doc_id': int(doc_id),
                        'metadata': results['metadatas'][0][i],
                        'similarity_score': similarity,
                        'distance': distance,
                        'snippet': results['documents'][0][i][:300] if results['documents'][0][i] else ""
                    })

                    print(f"{results['metadatas'][0][i]['title']}: similarity={similarity:.4f}")
            else:
                print("Chroma не вернула результатов")

            return formatted_results

        except Exception as e:
            print(f"Ошибка поиска в Chroma: {e}")
            return []

    def get_document_count(self) -> int:
        """Возвращает количество документов в хранилище"""
        return self.collection.count()

    def clear_storage(self) -> None:
        """Очищает хранилище"""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"description": "Document search system with TF-IDF vectors"}
        )

    def get_collection_info(self) -> Dict:
        """Возвращает информацию о коллекции"""
        return {
            "name": self.collection.name,
            "document_count": self.get_document_count(),
            "persist_directory": self.persist_directory
        }