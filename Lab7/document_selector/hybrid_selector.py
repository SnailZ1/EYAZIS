from typing import List, Dict
from .rule_based_selector import RuleBasedSelector
from .ranking_enhancer import RankingEnhancer
from .semantic_enhancer import SemanticEnhancer


class HybridDocumentSelector:
    """
    Гибридный селектор документов, комбинирующий несколько подходов
    """

    def __init__(self, use_pre_selection: bool = False, 
                 use_ranking_enhancement: bool = False,
                 use_semantic_search: bool = True,
                 word2vec_model_path: str = 'models/glove-wiki-gigaword-200.bin'):
        self.use_pre_selection = use_pre_selection
        self.use_ranking_enhancement = use_ranking_enhancement
        self.use_semantic_search = use_semantic_search

        self.rule_selector = RuleBasedSelector() if use_pre_selection else None
        self.ranking_enhancer = RankingEnhancer() if use_ranking_enhancement else None
        self.semantic_enhancer = SemanticEnhancer(word2vec_model_path) if self.use_semantic_search else None

        self.selection_stats = {}
        self.last_expansion_result = None  # Сохраняем результат расширения

    def process_search(self, query: str, all_documents: List,
                       search_function, top_k: int = 10) -> List[Dict]:
        """
        Полный процесс поиска с интеллектуальным отбором
        """
        print("=== ГИБРИДНЫЙ ОТБОР ДОКУМЕНТОВ ===")

        # Сохраняем оригинальный запрос
        original_query = query
        
        # 0. Семантическое расширение запроса (если включено)

        print(bool(self.use_semantic_search), self.semantic_enhancer)

        if self.use_semantic_search and self.semantic_enhancer:
            print("🎯 Этап 0: Семантическое расширение запроса")
            expansion_result = self.semantic_enhancer.expand_query_with_similar_words(query)
            self.last_expansion_result = expansion_result
            
            # Создаем расширенный запрос для поиска
            expanded_query = " ".join(expansion_result['all_terms'])
            print(f"   📖 Оригинальный запрос: '{query}'")
            print(f"   🔍 Расширенный запрос: '{expanded_query}'")
            
            # Используем расширенный запрос для следующих этапов
            query = expanded_query

        # 1. Предварительный отбор кандидатов
        if self.use_pre_selection and self.rule_selector:
            print("Этап 1: Предварительный отбор кандидатов")
            candidate_documents = self.rule_selector.select_documents(
                query, all_documents, top_k * 3
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
        else:
            enhanced_results = search_results
            self.selection_stats['ranking_enhancement'] = {'skipped': True}

        # 4. Семантическое улучшение
        if self.use_semantic_search and self.semantic_enhancer:
            print("Этап 4: Семантическое улучшение результатов")
            # Используем оригинальный запрос для подсветки
            final_results = self.semantic_enhancer.enhance_search_with_semantics(
                original_query, enhanced_results, all_documents
            )
            self.selection_stats['semantic_enhancement'] = self.semantic_enhancer.get_selection_stats()
        else:
            final_results = enhanced_results
            self.selection_stats['semantic_enhancement'] = {'skipped': True}

        final_results = final_results[:top_k]
        print(f"Финальных результатов: {len(final_results)}")
        return final_results

    def semantic_query_expansion(self, query: str) -> Dict:
        """
        Расширение запроса семантически похожими словами
        """
        if self.use_semantic_search and self.semantic_enhancer:
            return self.semantic_enhancer.expand_query_with_similar_words(query)
        return {
            'original_terms': query.split(), 
            'expanded_terms': query.split(), 
            'similar_terms': {},
            'all_terms': query.split()
        }

    def get_last_expansion_result(self) -> Dict:
        """
        Возвращает результат последнего расширения запроса
        """
        return self.last_expansion_result

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

        if self.use_semantic_search and self.semantic_enhancer:
            semantic_analysis = self.semantic_enhancer.get_semantic_analysis(query, document)
            explanation['selection_stages'].append({
                'stage': 'semantic_enhancement',
                'explanation': semantic_analysis
            })

        return explanation

    def get_selection_statistics(self) -> Dict:
        """
        Возвращает полную статистику отбора
        """
        return self.selection_stats