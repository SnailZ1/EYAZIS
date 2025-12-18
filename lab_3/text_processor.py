"""
Модуль обработки текста
Включает токенизацию, определение языка, фильтрацию стоп-слов
"""

import re
import os
from typing import List, Tuple
from langdetect import detect


class TextProcessor:
    """Класс для предобработки текста"""
    
    def __init__(self):
        self.stopwords_ru = self._load_stopwords('data/stopwords_ru.txt')
        self.stopwords_en = self._load_stopwords('data/stopwords_en.txt')
    
    def _load_stopwords(self, filepath: str) -> set:
        """Загрузка стоп-слов из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return set(word.strip().lower() for word in f.readlines())
        except FileNotFoundError:
            print(f"Warning: {filepath} not found. Using empty stopwords set.")
            return set()
    
    def detect_language(self, text: str) -> str:
        """Определение языка текста (ru или en)"""
        try:
            lang = detect(text)
            return 'ru' if lang == 'ru' else 'en'
        except:
            # Если не удалось определить, проверяем наличие кириллицы
            if re.search('[а-яА-Я]', text):
                return 'ru'
            return 'en'
    
    def tokenize_sentences(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Разбиение текста на предложения
        Возвращает список кортежей (предложение, номер_абзаца, позиция_в_абзаце)
        """
        # Разбиваем на абзацы
        paragraphs = text.split('\n')
        sentences = []
        
        for para_idx, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                continue
            
            # Разбиваем абзац на предложения
            # Учитываем точки, восклицательные и вопросительные знаки
            sent_pattern = r'[^.!?]+[.!?]+|[^.!?]+$'
            para_sentences = re.findall(sent_pattern, paragraph)
            
            for sent_idx, sentence in enumerate(para_sentences):
                sentence = sentence.strip()
                if sentence:
                    sentences.append((sentence, para_idx, sent_idx))
        
        return sentences
    
    def tokenize_words(self, text: str, language: str = 'ru', 
                       filter_stopwords: bool = True,
                       filter_numbers: bool = True,
                       filter_latin_in_russian: bool = True) -> List[str]:
        """
        Разбиение текста на слова с фильтрацией
        
        Args:
            text: исходный текст
            language: язык текста ('ru' или 'en')
            filter_stopwords: удалять стоп-слова
            filter_numbers: удалять числа
            filter_latin_in_russian: удалять латиницу из русского текста
        """
        # Приводим к нижнему регистру
        text = text.lower()
        
        # Извлекаем слова
        words = re.findall(r'\b\w+\b', text)
        
        # Фильтрация
        filtered_words = []
        stopwords = self.stopwords_ru if language == 'ru' else self.stopwords_en
        
        for word in words:
            # Пропускаем стоп-слова
            if filter_stopwords and word in stopwords:
                continue
            
            # Пропускаем числа
            if filter_numbers and word.isdigit():
                continue
            
            # Для русского текста пропускаем слова с латиницей
            if filter_latin_in_russian and language == 'ru':
                if re.search('[a-zA-Z]', word):
                    continue
            
            # Пропускаем слишком короткие слова (1-2 символа)
            if len(word) < 3:
                continue
            
            filtered_words.append(word)
        
        return filtered_words
    
    def normalize_text(self, text: str) -> str:
        """Нормализация текста (удаление лишних пробелов, переносов и т.д.)"""
        # Удаляем множественные пробелы
        text = re.sub(r'\s+', ' ', text)
        # Удаляем пробелы в начале и конце
        text = text.strip()
        return text
    
    def get_paragraph_count(self, text: str) -> int:
        """Подсчет количества абзацев"""
        paragraphs = [p for p in text.split('\n') if p.strip()]
        return len(paragraphs)
    
    def get_sentence_position_weight(self, para_idx: int, sent_idx: int, 
                                     total_paras: int) -> float:
        """
        Вычисление веса предложения на основе его позиции
        
        Первые и последние абзацы важнее
        Первые предложения в абзаце важнее
        """
        # Вес абзаца (первые и последние абзацы важнее)
        if para_idx == 0 or para_idx == total_paras - 1:
            para_weight = 1.5
        elif para_idx == 1 or para_idx == total_paras - 2:
            para_weight = 1.2
        else:
            para_weight = 1.0
        
        # Вес позиции в абзаце (первые предложения важнее)
        if sent_idx == 0:
            sent_weight = 1.3
        elif sent_idx == 1:
            sent_weight = 1.1
        else:
            sent_weight = 1.0
        
        return para_weight * sent_weight
