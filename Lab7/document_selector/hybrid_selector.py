# document_selector/hybrid_selector.py
from typing import List, Dict
from .rule_based_selector import RuleBasedSelector
from .ranking_enhancer import RankingEnhancer


class HybridDocumentSelector:
    """
    Гибридный селектор документов, комбинирующий несколько подходов
    """

    def __init__(self, use_pre_selection: bool = True, use_ranking_enhancement: bool = True):
        self.use_pre_selection = use_pre_selection
        self.use_ranking_enhancement = use_ranking_enhancement

        self.rule_selector = RuleBasedSelector() if use_pre_selection else None
        self.ranking_enhancer = RankingEnhancer() if use_ranking_enhancement else None

        self.selection_stats = {}

    def process_search(self, query: str, all_documents: List,
                       search_function, top_k: int = 10) -> List[Dict]:
        """
        Полный процесс поиска с интеллектуальным отбором:
        1. Предварительный отбор кандидатов
        2. Точный поиск среди кандидатов
        3. Улучшение ранжирования результатов
        """
        print("=== ГИБРИДНЫЙ ОТБОР ДОКУМЕНТОВ ===")

        # 1. Предварительный отбор кандидатов
        if self.use_pre_selection and self.rule_selector:
            print("Этап 1: Предварительный отбор кандидатов")
            candidate_documents = self.rule_selector.select_documents(
                query, all_documents, top_k * 3  # Отбираем в 3 раза больше для точного поиска
            )
            self.selection_stats['pre_selection'] = self.rule_selector.get_selection_stats()
        else:
            candidate_documents = all_documents
            self.selection_stats['pre_selection'] = {'skipped': True}

        print(f"Кандидатов для точного поиска: {len(candidate_documents)}")

        # 2. Точный поиск среди кандидатов
        print("Этап 2: Точный поиск среди кандидатов")
        search_results = search_function(query, candidate_documents, top_k * 2)

        # 3. Улучшение ранжирования
        if self.use_ranking_enhancement and self.ranking_enhancer:
            print("Этап 3: Улучшение ранжирования результатов")
            enhanced_results = self.ranking_enhancer.enhance_ranking(
                query, search_results, all_documents
            )
            self.selection_stats['ranking_enhancement'] = self.ranking_enhancer.get_selection_stats()
            final_results = enhanced_results[:top_k]
        else:
            final_results = search_results[:top_k]
            self.selection_stats['ranking_enhancement'] = {'skipped': True}

        print(f"Финальных результатов: {len(final_results)}")
        return final_results

    def get_detailed_explanation(self, query: str, document) -> Dict:
        """
        Детальное объяснение отбора конкретного документа
        """
        explanation = {
            'query': query,
            'document_id': document.doc_id,
            'document_title': document.title,
            'selection_stages': []
        }

        if self.rule_selector:
            rule_explanation = self.rule_selector.explain_selection(query, document)
            explanation['selection_stages'].append({
                'stage': 'rule_based_selection',
                'explanation': rule_explanation
            })

        return explanation

    def get_selection_statistics(self) -> Dict:
        """
        Возвращает полную статистику отбора
        """
        return self.selection_stats