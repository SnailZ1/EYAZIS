# document_selector/rule_based_selector.py
from typing import List, Dict
from collections import defaultdict
from .base_selector import BaseDocumentSelector


class RuleBasedSelector(BaseDocumentSelector):
    """
    Правиловой селектор документов на основе эвристик
    """

    def __init__(self):
        super().__init__("RuleBasedSelector")
        self.rule_weights = {
            'title_match': 3.0,  # Совпадение в заголовке
            'term_frequency': 2.0,  # Частота терминов
            'freshness': 1.5,  # Свежесть документа
            'optimal_length': 1.2,  # Оптимальная длина
            'file_type': 0.5,  # Тип файла (PDF предпочтительнее)
        }

    def select_documents(self, query: str, documents: List, top_k: int = 10) -> List:
        """
        Отбор документов на основе правил
        """
        print(f"Правиловой отбор из {len(documents)} документов...")

        if not documents:
            return []

        # Предварительная фильтрация
        filtered_docs = self.pre_filter(query, documents)
        print(f"После предфильтрации: {len(filtered_docs)} документов")

        # Оцениваем каждый документ
        scored_docs = []
        for doc in filtered_docs:
            score = self._calculate_document_score(query, doc)
            scored_docs.append((score, doc))

        # Сортируем по убыванию скора
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # Выбираем топ-K
        selected_docs = [doc for score, doc in scored_docs[:top_k]]

        # Сохраняем статистику
        self.stats = {
            'initial_documents': len(documents),
            'after_filtering': len(filtered_docs),
            'selected_documents': len(selected_docs),
            'average_score': sum(score for score, _ in scored_docs[:top_k]) / len(
                selected_docs) if selected_docs else 0,
            'max_score': scored_docs[0][0] if scored_docs else 0
        }

        print(f"Отобрано документов: {len(selected_docs)}")
        return selected_docs

    def _calculate_document_score(self, query: str, document) -> float:
        """
        Расчет комплексной оценки документа для запроса
        """
        score = 0.0
        query_terms = set(query.lower().split())

        # 1. Совпадение в заголовке
        title_score = self._calculate_title_score(query_terms, document)
        score += title_score * self.rule_weights['title_match']

        # 2. Частота терминов в контенте
        term_freq_score = self._calculate_term_frequency_score(query_terms, document)
        score += term_freq_score * self.rule_weights['term_frequency']

        # 3. Свежесть документа
        freshness_score = self.calculate_freshness_score(document)
        score += freshness_score * self.rule_weights['freshness']

        # 4. Оптимальная длина
        length_score = self.calculate_length_score(document)
        score += length_score * self.rule_weights['optimal_length']

        # 5. Бонус за тип файла (PDF обычно более структурированные)
        file_type_score = 1.2 if document.file_type.upper() == 'PDF' else 1.0
        score += file_type_score * self.rule_weights['file_type']

        return score

    def _calculate_title_score(self, query_terms: set, document) -> float:
        """
        Оценка совпадения терминов в заголовке
        """
        title_terms = set(document.title.lower().split())
        overlap = len(query_terms & title_terms)

        if overlap == len(query_terms):  # Все термины в заголовке
            return 3.0
        elif overlap > 0:
            return overlap / len(query_terms) * 2.0
        else:
            return 0.0

    def _calculate_term_frequency_score(self, query_terms: set, document) -> float:
        """
        Оценка частоты терминов в документе
        """
        if not hasattr(document, 'processed_content') or not document.processed_content:
            return 0.0

        content_terms = document.processed_content.split()
        total_terms = len(content_terms)

        if total_terms == 0:
            return 0.0

        # Считаем общую частоту терминов запроса
        term_count = 0
        for term in query_terms:
            term_count += content_terms.count(term)

        # Нормализуем по длине документа
        normalized_freq = term_count / total_terms

        # Логарифмическое масштабирование для уменьшения влияния очень частых терминов
        return min(normalized_freq * 10, 2.0)  # Ограничиваем максимальный score

    def explain_selection(self, query: str, document) -> Dict:
        """
        Объяснение почему документ был отобран
        """
        query_terms = set(query.lower().split())

        explanation = {
            'document_id': document.doc_id,
            'document_title': document.title,
            'total_score': self._calculate_document_score(query, document),
            'factors': []
        }

        # Title match
        title_score = self._calculate_title_score(query_terms, document)
        if title_score > 0:
            explanation['factors'].append({
                'factor': 'title_match',
                'score': title_score,
                'weighted_score': title_score * self.rule_weights['title_match'],
                'description': f'Совпадение в заголовке: {len(query_terms & set(document.title.lower().split()))} терминов'
            })

        # Term frequency
        term_freq_score = self._calculate_term_frequency_score(query_terms, document)
        if term_freq_score > 0:
            explanation['factors'].append({
                'factor': 'term_frequency',
                'score': term_freq_score,
                'weighted_score': term_freq_score * self.rule_weights['term_frequency'],
                'description': 'Высокая частота терминов запроса в документе'
            })

        # Freshness
        freshness_score = self.calculate_freshness_score(document)
        explanation['factors'].append({
            'factor': 'freshness',
            'score': freshness_score,
            'weighted_score': freshness_score * self.rule_weights['freshness'],
            'description': f'Свежесть документа: {document.date_created}'
        })

        # Length
        length_score = self.calculate_length_score(document)
        explanation['factors'].append({
            'factor': 'optimal_length',
            'score': length_score,
            'weighted_score': length_score * self.rule_weights['optimal_length'],
            'description': f'Оптимальная длина: {len(document.content)} символов'
        })

        return explanation