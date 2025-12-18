# document_selector/ranking_enhancer.py
from typing import List, Dict
from .base_selector import BaseDocumentSelector


class RankingEnhancer(BaseDocumentSelector):
    """
    Улучшение ранжирования существующих результатов поиска
    """

    def __init__(self):
        super().__init__("RankingEnhancer")

    def enhance_ranking(self, query: str, search_results: List[Dict], original_documents: List) -> List[Dict]:
        """
        Улучшает ранжирование существующих результатов поиска
        """
        print("Улучшение ранжирования результатов...")

        if not search_results:
            return []

        # Создаем маппинг doc_id -> документ
        doc_map = {doc.doc_id: doc for doc in original_documents}

        enhanced_results = []
        for result in search_results:
            doc_id = result['metadata']['doc_id']
            document = doc_map.get(doc_id)

            if document:
                # Рассчитываем дополнительные метрики
                enhancement_score = self._calculate_enhancement_score(query, document)

                # Комбинируем с оригинальным score
                original_score = result['similarity_score']
                enhanced_score = self._combine_scores(original_score, enhancement_score)

                # Создаем улучшенный результат
                enhanced_result = result.copy()
                enhanced_result['similarity_score'] = enhanced_score
                enhanced_result['enhancement_info'] = {
                    'original_score': original_score,
                    'enhancement_score': enhancement_score,
                    'combined_score': enhanced_score
                }

                enhanced_results.append(enhanced_result)
            else:
                enhanced_results.append(result)

        # Пересортируем по улучшенному score
        enhanced_results.sort(key=lambda x: x['similarity_score'], reverse=True)

        self.stats = {
            'enhanced_results': len(enhanced_results),
            'average_enhancement': sum(r['enhancement_info']['enhancement_score'] for r in enhanced_results) / len(
                enhanced_results)
        }

        return enhanced_results

    def _calculate_enhancement_score(self, query: str, document) -> float:
        """
        Расчет скора улучшения на основе дополнительных факторов
        """
        score = 0.0
        query_terms = set(query.lower().split())

        # 1. Плотность терминов (сколько % документа покрыто терминами запроса)
        if hasattr(document, 'processed_content'):
            content_terms = set(document.processed_content.split())
            coverage = len(query_terms & content_terms) / len(query_terms) if query_terms else 0
            score += coverage * 0.3

        # 2. Свежесть документа
        freshness = self.calculate_freshness_score(document)
        score += freshness * 0.3

        # 3. Качество документа (длина + структура)
        length_score = self.calculate_length_score(document)
        score += length_score * 0.2

        # 4. Репутация типа файла
        file_type_bonus = 1.2 if document.file_type.upper() == 'PDF' else 1.0
        score += (file_type_bonus - 1.0) * 0.2

        return min(score, 1.0)  # Нормализуем до [0, 1]

    def _combine_scores(self, original_score: float, enhancement_score: float) -> float:
        """
        Комбинирование оригинального скора и скора улучшения
        """
        # Взвешенная комбинация (70% оригинальный score, 30% улучшение)
        return 0.7 * original_score + 0.3 * enhancement_score

    def select_documents(self, query: str, documents: List, top_k: int = 10) -> List:
        """
        Реализация абстрактного метода (не используется напрямую для этого класса)
        """
        # Для этого класса используем enhance_ranking вместо select_documents
        raise NotImplementedError("Используйте метод enhance_ranking для этого класса")