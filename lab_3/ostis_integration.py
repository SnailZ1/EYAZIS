"""
Модуль интеграции с OSTIS
Генерация SC-кода и семантических связей
"""

from typing import List, Dict, Tuple
from datetime import datetime


class SCsGenerator:
    """Генератор SC-кода в формате SCs"""
    
    def __init__(self):
        self.nodes = []
        self.edges = []
    
    def generate_document_scs(self, filename: str, text: str, summary: Dict, 
                             keywords: List[Tuple[str, float]], 
                             keyword_tree: Dict, language: str, 
                             domain: str) -> str:
        """
        Генерация SCs-файла для документа и его реферата
        
        Args:
            filename: имя исходного файла
            text: исходный текст
            summary: результат реферирования
            keywords: список ключевых слов
            keyword_tree: иерархия ключевых слов
            language: язык документа
            domain: предметная область
        """
        scs_content = []
        
        # Заголовок
        scs_content.append("// SC-code representation of document summary")
        scs_content.append(f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        scs_content.append(f"// Source: {filename}")
        scs_content.append("")
        
        # Определение документа
        doc_id = self._sanitize_identifier(filename)
        scs_content.append(f"{doc_id}")
        scs_content.append(f"=> nrel_main_idtf:")
        scs_content.append(f"   [{filename}] (* <- lang_{language};; *);")
        scs_content.append(f"<- concept_document;")
        scs_content.append(f"<- concept_{domain}_document;")
        scs_content.append(f"<- concept_{language}_text;;")
        scs_content.append("")
        
        # Реферат
        summary_id = f"{doc_id}_summary"
        scs_content.append(f"{summary_id}")
        scs_content.append(f"=> nrel_main_idtf:")
        scs_content.append(f"   [Реферат: {filename}] (* <- lang_ru;; *);")
        scs_content.append(f"<- concept_summary;")
        scs_content.append(f"<- concept_sentence_extraction_summary;;")
        scs_content.append("")
        
        # Связь документа и реферата
        scs_content.append(f"{doc_id}")
        scs_content.append(f"=> nrel_summary: {summary_id};;")
        scs_content.append("")
        
        # Предложения реферата
        scs_content.append("// Summary sentences")
        for idx, sentence in enumerate(summary['sentences'], 1):
            sent_id = f"{summary_id}_sent_{idx}"
            clean_sent = sentence.replace('"', '\\"')[:100]  # Ограничиваем длину
            
            scs_content.append(f"{sent_id}")
            scs_content.append(f"=> nrel_main_idtf:")
            scs_content.append(f'   ["{clean_sent}..."] (* <- lang_{language};; *);')
            scs_content.append(f"<- concept_sentence;")
            scs_content.append(f"<- rrel_sentence_{idx};;")
            scs_content.append("")
            
            # Связь с рефератом
            scs_content.append(f"{summary_id}")
            scs_content.append(f"=> nrel_includes: {sent_id};;")
            scs_content.append("")
        
        # Ключевые слова
        scs_content.append("// Keywords")
        keyword_ids = []
        for idx, (keyword, score) in enumerate(keywords, 1):
            kw_id = f"{doc_id}_kw_{self._sanitize_identifier(keyword)}"
            keyword_ids.append((kw_id, keyword, score))
            
            scs_content.append(f"{kw_id}")
            scs_content.append(f"=> nrel_main_idtf:")
            scs_content.append(f"   [{keyword}] (* <- lang_{language};; *);")
            scs_content.append(f"<- concept_keyword;")
            scs_content.append(f"<- concept_{domain}_term;;")
            scs_content.append("")
            
            # Связь с документом
            scs_content.append(f"{doc_id}")
            scs_content.append(f"=> nrel_key_concept: {kw_id};;")
            scs_content.append("")
        
        # Иерархия ключевых слов
        if keyword_tree.get('groups'):
            scs_content.append("// Keyword hierarchy (semantic groups)")
            for main_term, related in keyword_tree['groups'].items():
                main_id = f"{doc_id}_kw_{self._sanitize_identifier(main_term)}"
                
                for rel_term in related:
                    rel_id = f"{doc_id}_kw_{self._sanitize_identifier(rel_term)}"
                    scs_content.append(f"{main_id}")
                    scs_content.append(f"=> nrel_related_term: {rel_id};;")
                    scs_content.append("")
        
        # Метаданные
        scs_content.append("// Metadata")
        scs_content.append(f"{doc_id}")
        scs_content.append(f"=> nrel_language: lang_{language};")
        scs_content.append(f"=> nrel_domain: concept_{domain};")
        scs_content.append(f"=> nrel_sentence_count: [{len(summary['sentences'])}];")
        scs_content.append(f"=> nrel_keyword_count: [{len(keywords)}];;")
        scs_content.append("")
        
        return '\n'.join(scs_content)
    
    def _sanitize_identifier(self, text: str) -> str:
        """Преобразование текста в валидный идентификатор SC"""
        # Убираем расширение файла
        if '.' in text:
            text = text.rsplit('.', 1)[0]
        
        # Заменяем недопустимые символы
        import re
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '_', text)
        return text.lower()


class SemanticLinker:
    """Класс для создания семантических связей между концептами"""
    
    def __init__(self, knowledge_base: Dict):
        self.kb = knowledge_base
    
    def find_semantic_links(self, keywords: List[str], language: str, 
                           domain: str) -> List[Tuple[str, str, str]]:
        """
        Поиск семантических связей между ключевыми словами
        
        Returns:
            Список троек (термин1, тип_связи, термин2)
        """
        links = []
        
        if domain not in self.kb:
            return links
        
        domain_kb = self.kb[domain].get(language, {})
        
        # Ищем связи типа "главный термин - связанный термин"
        for main_term, related_terms in domain_kb.items():
            main_lower = main_term.lower()
            
            if main_lower in keywords:
                for rel_term in related_terms:
                    rel_lower = rel_term.lower()
                    if rel_lower in keywords:
                        links.append((main_lower, 'nrel_related_term', rel_lower))
        
        # Ищем синонимы (термины в одной группе)
        for main_term, related_terms in domain_kb.items():
            related_in_kw = [rt.lower() for rt in related_terms if rt.lower() in keywords]
            
            # Если несколько связанных терминов присутствуют, они синонимы
            for i, term1 in enumerate(related_in_kw):
                for term2 in related_in_kw[i+1:]:
                    links.append((term1, 'nrel_synonym', term2))
        
        return links
    
    def enhance_keywords_with_semantics(self, keywords: List[Tuple[str, float]], 
                                       language: str, domain: str) -> List[Tuple[str, float]]:
        """
        Улучшение списка ключевых слов с использованием семантических связей
        
        Добавляет связанные термины, если они важны
        """
        if domain not in self.kb:
            return keywords
        
        domain_kb = self.kb[domain].get(language, {})
        keyword_dict = dict(keywords)
        enhanced = dict(keywords)
        
        # Для каждого ключевого слова ищем связанные термины
        for main_term, related_terms in domain_kb.items():
            main_lower = main_term.lower()
            
            # Если главный термин есть в ключевых словах
            if main_lower in keyword_dict:
                main_score = keyword_dict[main_lower]
                
                # Добавляем связанные термины с пониженным весом
                for rel_term in related_terms:
                    rel_lower = rel_term.lower()
                    if rel_lower not in enhanced:
                        enhanced[rel_lower] = main_score * 0.5
        
        # Сортируем по весу
        result = sorted(enhanced.items(), key=lambda x: x[1], reverse=True)
        return result
