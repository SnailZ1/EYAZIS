from typing import List, Dict
import numpy as np
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from .base_selector import BaseDocumentSelector


class SemanticEnhancer(BaseDocumentSelector):
    """
    Улучшение поиска с использованием семантической схожести Word2Vec
    с расширением запроса и подсветкой терминов
    """

    def __init__(self, word2vec_model_path: str = None, similarity_threshold: float = 0.6):
        super().__init__("SemanticEnhancer")
        self.similarity_threshold = float(similarity_threshold)  # Гарантируем float
        self.word_vectors = None
        self.vocabulary = set()
        
        if word2vec_model_path:
            self.load_word2vec_model(word2vec_model_path)
        else:
            self._create_demo_model()

    def load_word2vec_model(self, model_path: str):
        """Загрузка предобученной модели Word2Vec"""
        try:
            print(f"Загрузка Word2Vec модели из {model_path}...")
            self.word_vectors = KeyedVectors.load_word2vec_format(model_path, binary=True)
            self.vocabulary = set(self.word_vectors.key_to_index.keys())
            print(f"Word2Vec модель загружена. Размер словаря: {len(self.vocabulary)}")
        except Exception as e:
            print(f"Ошибка загрузки Word2Vec модели: {e}")

    def expand_query_with_similar_words(self, query: str, top_n: int = 3) -> Dict:
        """
        Расширяет запрос семантически похожими словами
        Возвращает оригинальные термины, расширенные термины и словарь похожих слов
        """
        if not self.word_vectors:
            return {
                'original_terms': query.split(),
                'expanded_terms': query.split(),
                'similar_terms': {},
                'all_terms': query.split(),
                'expansion_ratio': 1.0
            }

        original_terms = [term.lower().strip() for term in query.split() if term.strip()]
        expanded_terms = original_terms.copy()
        similar_terms = {}
        
        print(f"Семантическое расширение запроса: '{query}'")

        for term in original_terms:
            if term in self.vocabulary:
                try:
                    similar_words = self.word_vectors.most_similar(term, topn=top_n)
                    # Фильтруем по порогу схожести и конвертируем в float
                    filtered_similar = [
                        (similar_word, float(similarity))  # Конвертируем в float
                        for similar_word, similarity in similar_words 
                        if similarity >= self.similarity_threshold and similar_word != term
                    ]
                    
                    if filtered_similar:
                        similar_terms[term] = filtered_similar
                        # Добавляем похожие слова в расширенный запрос
                        for similar_word, similarity in filtered_similar:
                            if similar_word not in expanded_terms:
                                expanded_terms.append(similar_word)
                                
                        print(f"'{term}': {[f'{word}({sim:.2f})' for word, sim in filtered_similar]}")
                    else:
                        print(f"Для '{term}' не найдено достаточно похожих слов")
                        
                except KeyError:
                    print(f"Слово '{term}' не найдено в модели Word2Vec")
            else:
                print(f"Слово '{term}' нет в словаре Word2Vec")

        # Все термины для поиска (оригинальные + расширенные)
        all_search_terms = list(set(original_terms + expanded_terms))
        expansion_ratio = len(expanded_terms) / len(original_terms) if original_terms else 1.0

        return {
            'original_terms': original_terms,
            'expanded_terms': expanded_terms,
            'similar_terms': similar_terms,
            'all_terms': all_search_terms,
            'expansion_ratio': float(expansion_ratio)  # Гарантируем float
        }

    def highlight_semantic_terms(self, text: str, expansion_result: Dict) -> str:
        """
        Подсвечивает в тексте оригинальные и семантически похожие термины
        """
        if not text:
            return ""

        highlighted_text = text
        
        # Создаем словарь для подсветки: термин -> тип подсветки
        highlight_terms = {}
        
        # Оригинальные термины - зеленый цвет
        for term in expansion_result['original_terms']:
            if len(term) > 2:  # Только термины длиннее 2 символов
                highlight_terms[term] = 'semantic-original'
        
        # Расширенные термины - синий цвет
        for original_term, similar_list in expansion_result['similar_terms'].items():
            for similar_term, similarity in similar_list:
                if len(similar_term) > 2:
                    highlight_terms[similar_term] = 'semantic-expanded'

        # Сортируем термины по длине (сначала длинные, чтобы избежать пересечений)
        sorted_terms = sorted(highlight_terms.keys(), key=len, reverse=True)
        
        # Применяем подсветку
        for term in sorted_terms:
            if term.lower() in highlighted_text.lower():
                color_class = highlight_terms[term]
                if color_class == 'semantic-original':
                    highlight_html = f'<mark class="semantic-original" title="Оригинальный термин запроса">{term}</mark>'
                else:
                    highlight_html = f'<mark class="semantic-expanded" title="Семантически похожий термин">{term}</mark>'
                
                # Заменяем с учетом регистра
                import re
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted_text = pattern.sub(highlight_html, highlighted_text)

        return highlighted_text

    def calculate_semantic_similarity(self, query: str, document) -> float:
        """
        Вычисляет семантическую схожесть между запросом и документом
        """
        if not self.word_vectors or not hasattr(document, 'processed_content'):
            return 0.0

        # Расширяем запрос
        expansion_result = self.expand_query_with_similar_words(query)
        all_search_terms = expansion_result['all_terms']
        
        if not all_search_terms:
            return 0.0

        # Получаем термины документа
        doc_terms = set(document.processed_content.split())
        
        # Вычисляем семантическое сходство
        semantic_score = 0.0
        matched_terms = 0

        for query_term in all_search_terms:
            if query_term in doc_terms:
                # Прямое совпадение
                semantic_score += 1.0
                matched_terms += 1
            elif query_term in self.vocabulary:
                # Ищем семантически похожие слова в документе
                best_similarity = 0.0
                for doc_term in doc_terms:
                    if doc_term in self.vocabulary:
                        try:
                            similarity = float(self.word_vectors.similarity(query_term, doc_term))  # Конвертируем
                            if similarity > best_similarity:
                                best_similarity = similarity
                        except KeyError:
                            continue
                
                if best_similarity >= self.similarity_threshold:
                    semantic_score += best_similarity
                    matched_terms += 1

        # Нормализуем скор
        if matched_terms > 0:
            semantic_score = semantic_score / len(all_search_terms)
            
        return float(min(semantic_score, 1.0))  # Гарантируем float

    def enhance_search_with_semantics(self, query: str, search_results: List[Dict], 
                                    documents: List) -> List[Dict]:
        """
        Улучшает результаты поиска с учетом семантической схожести
        и добавляет информацию для подсветки
        """
        print("Применение семантического поиска с расширением запроса...")

        # Расширяем запрос
        expansion_result = self.expand_query_with_similar_words(query)
        
        # Создаем маппинг doc_id -> документ
        doc_map = {doc.doc_id: doc for doc in documents}
        
        enhanced_results = []
        
        for result in search_results:
            doc_id = result['metadata']['doc_id']
            document = doc_map.get(doc_id)
            
            if document:
                # Вычисляем семантический скор
                semantic_score = self.calculate_semantic_similarity(query, document)
                
                # Комбинируем с оригинальным скором
                original_score = float(result['similarity_score'])  # Конвертируем
                combined_score = self._combine_scores(original_score, semantic_score)
                
                # Подсвечиваем термины в сниппете
                original_snippet = result.get('snippet', '')
                highlighted_snippet = self.highlight_semantic_terms(original_snippet, expansion_result)
                
                # Обновляем результат
                enhanced_result = result.copy()
                enhanced_result['similarity_score'] = float(combined_score)  # Гарантируем float
                enhanced_result['semantic_info'] = {
                    'original_score': float(original_score),
                    'semantic_score': float(semantic_score),
                    'combined_score': float(combined_score),
                    'expansion_result': expansion_result,
                    'highlighted_snippet': highlighted_snippet
                }
                enhanced_result['snippet'] = highlighted_snippet  # Заменяем сниппет
                
                enhanced_results.append(enhanced_result)
            else:
                enhanced_results.append(result)
        
        # Сортируем по улучшенному скору
        enhanced_results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        self.stats = {
            'semantically_enhanced': len(enhanced_results),
            'avg_semantic_score': float(sum(r['semantic_info']['semantic_score'] for r in enhanced_results) / len(enhanced_results)) if enhanced_results else 0.0,
            'query_expansion_ratio': float(expansion_result['expansion_ratio'])
        }
        
        return enhanced_results

    def _combine_scores(self, original_score: float, semantic_score: float) -> float:
        """
        Комбинирование TF-IDF и семантического скора
        """
        return float(0.7 * original_score + 0.3 * semantic_score)  # Гарантируем float

    def select_documents(self, query: str, documents: List, top_k: int = 10) -> List:
        """Реализация абстрактного метода"""
        scored_docs = []
        
        for doc in documents:
            semantic_score = self.calculate_semantic_similarity(query, doc)
            scored_docs.append((semantic_score, doc))
        
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]

    def get_semantic_analysis(self, query: str, document) -> Dict:
        """
        Детальный анализ семантической схожести
        """
        expansion_result = self.expand_query_with_similar_words(query)
        
        analysis = {
            'query': query,
            'original_terms': expansion_result['original_terms'],
            'expanded_terms': expansion_result['expanded_terms'],
            'similar_terms': expansion_result['similar_terms'],
            'document_terms_count': len(document.processed_content.split()),
            'semantic_score': self.calculate_semantic_similarity(query, document)
        }
        
        return analysis