"""
Модуль автоматического реферирования
Реализует алгоритм sentence extraction с использованием TF-IDF
"""

import numpy as np
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
import math

from text_processor import TextProcessor
from knowledge_base import KNOWLEDGE_BASE


class TFIDFCalculator:
    """Класс для вычисления TF-IDF"""
    
    def __init__(self):
        self.idf_cache = {}
    
    def calculate_tf(self, words: List[str]) -> Dict[str, float]:
        """Вычисление Term Frequency"""
        word_count = Counter(words)
        total_words = len(words)
        
        tf = {}
        for word, count in word_count.items():
            tf[word] = count / total_words
        
        return tf
    
    def calculate_idf(self, documents: List[List[str]]) -> Dict[str, float]:
        """Вычисление Inverse Document Frequency"""
        num_docs = len(documents)
        word_doc_count = defaultdict(int)
        
        # Подсчитываем в скольких документах встречается каждое слово
        for doc in documents:
            unique_words = set(doc)
            for word in unique_words:
                word_doc_count[word] += 1
        
        # Вычисляем IDF
        idf = {}
        for word, doc_count in word_doc_count.items():
            idf[word] = math.log(num_docs / doc_count)
        
        self.idf_cache = idf
        return idf
    
    def calculate_tfidf(self, tf: Dict[str, float], idf: Dict[str, float]) -> Dict[str, float]:
        """Вычисление TF-IDF"""
        tfidf = {}
        for word, tf_value in tf.items():
            idf_value = idf.get(word, 0)
            tfidf[word] = tf_value * idf_value
        
        return tfidf


class SentenceExtractor:
    """Класс для извлечения ключевых предложений"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.tfidf_calculator = TFIDFCalculator()
    
    def extract_summary(self, text: str, num_sentences: int = 10) -> Dict:
        """
        Извлечение реферата из текста
        
        Returns:
            dict с ключами:
                - sentences: список выбранных предложений
                - language: определенный язык
                - keywords: ключевые слова
                - tfidf_scores: TF-IDF оценки
        """
        # Определяем язык
        language = self.text_processor.detect_language(text)
        
        # Разбиваем на предложения
        sentences = self.text_processor.tokenize_sentences(text)
        total_paras = self.text_processor.get_paragraph_count(text)
        
        if len(sentences) <= num_sentences:
            # Если предложений меньше или равно требуемому количеству
            return {
                'sentences': [s[0] for s in sentences],
                'language': language,
                'keywords': [],
                'tfidf_scores': {}
            }
        
        # Разбиваем каждое предложение на слова
        sentence_words = []
        for sent, _, _ in sentences:
            words = self.text_processor.tokenize_words(sent, language)
            sentence_words.append(words)
        
        # Вычисляем TF-IDF для всего документа
        all_words = []
        for words in sentence_words:
            all_words.extend(words)
        
        tf = self.tfidf_calculator.calculate_tf(all_words)
        idf = self.tfidf_calculator.calculate_idf(sentence_words)
        tfidf = self.tfidf_calculator.calculate_tfidf(tf, idf)
        
        # Вычисляем вес каждого предложения
        sentence_scores = []
        for idx, (sent, para_idx, sent_idx) in enumerate(sentences):
            words = sentence_words[idx]
            
            # Базовый вес - сумма TF-IDF слов в предложении
            if words:
                tfidf_score = sum(tfidf.get(word, 0) for word in words) / len(words)
            else:
                tfidf_score = 0
            
            # Позиционный вес
            position_weight = self.text_processor.get_sentence_position_weight(
                para_idx, sent_idx, total_paras
            )
            
            # Нормализация по длине предложения
            length_norm = min(len(words) / 20, 1.0)  # Оптимальная длина ~20 слов
            
            # Итоговый вес
            final_score = tfidf_score * position_weight * (0.5 + 0.5 * length_norm)
            
            sentence_scores.append((idx, final_score, sent))
        
        # Сортируем по весу и выбираем топ-N
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences_idx = sorted([s[0] for s in sentence_scores[:num_sentences]])
        
        # Формируем итоговый реферат (сохраняем порядок из исходного текста)
        summary_sentences = [sentences[idx][0] for idx in top_sentences_idx]
        
        return {
            'sentences': summary_sentences,
            'language': language,
            'tfidf_scores': tfidf,
            'sentence_scores': sentence_scores
        }


class KeywordExtractor:
    """Класс для извлечения ключевых слов и построения иерархии"""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.tfidf_calculator = TFIDFCalculator()
    
    def extract_keywords(self, text: str, language: str, 
                        domain: str = None, top_n: int = 20) -> List[Tuple[str, float]]:
        """
        Извлечение ключевых слов
        
        Args:
            text: исходный текст
            language: язык ('ru' или 'en')
            domain: предметная область ('medical' или 'art')
            top_n: количество ключевых слов
        """
        # Разбиваем на слова
        words = self.text_processor.tokenize_words(text, language)
        
        # Вычисляем TF-IDF
        tf = self.tfidf_calculator.calculate_tf(words)
        
        # Для IDF используем предложения как документы
        sentences = self.text_processor.tokenize_sentences(text)
        sentence_words = [
            self.text_processor.tokenize_words(sent[0], language) 
            for sent in sentences
        ]
        idf = self.tfidf_calculator.calculate_idf(sentence_words)
        tfidf = self.tfidf_calculator.calculate_tfidf(tf, idf)
        
        # Усиливаем вес терминов из базы знаний
        if domain and domain in KNOWLEDGE_BASE:
            kb = KNOWLEDGE_BASE[domain][language]
            for word in tfidf:
                if word in kb:
                    tfidf[word] *= 1.5  # Усиливаем термины из базы знаний
        
        # Сортируем по TF-IDF
        sorted_keywords = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_keywords[:top_n]
    
    def build_keyword_tree(self, keywords: List[Tuple[str, float]], 
                          language: str, domain: str = None) -> Dict:
        """
        Построение иерархического дерева ключевых слов
        
        Использует базу знаний для группировки связанных терминов
        """
        tree = {
            'root': [],
            'groups': {}
        }
        
        if not domain or domain not in KNOWLEDGE_BASE:
            # Без базы знаний - просто плоский список
            tree['root'] = [kw[0] for kw in keywords]
            return tree
        
        kb = KNOWLEDGE_BASE[domain][language]
        used_keywords = set()
        
        # Группируем по связям из базы знаний
        for main_term, related_terms in kb.items():
            group_keywords = []
            
            # Проверяем, есть ли главный термин в ключевых словах
            main_in_keywords = False
            for kw, score in keywords:
                if kw == main_term.lower():
                    main_in_keywords = True
                    used_keywords.add(kw)
                    break
            
            if main_in_keywords:
                # Ищем связанные термины
                for kw, score in keywords:
                    if kw in [rt.lower() for rt in related_terms]:
                        group_keywords.append(kw)
                        used_keywords.add(kw)
                
                if group_keywords:
                    tree['groups'][main_term] = group_keywords
        
        # Добавляем несгруппированные ключевые слова в корень
        for kw, score in keywords:
            if kw not in used_keywords:
                tree['root'].append(kw)
        
        return tree
