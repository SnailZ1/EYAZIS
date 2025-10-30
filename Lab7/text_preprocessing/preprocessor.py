# text_preprocessing/preprocessor.py
import re
import string
from .nltk_setup import download_nltk_resources
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag as nltk_pos_tag  
from typing import List, Dict


class TextPreprocessor:
    """
    Класс для предобработки текстовых документов на английском языке
    """

    def __init__(self, use_lemmatization=True, custom_stopwords=None):
        self.use_lemmatization = use_lemmatization
        self.stop_words = set(stopwords.words('english'))

        if custom_stopwords:
            self.stop_words.update(custom_stopwords)

        if self.use_lemmatization:
            self.lemmatizer = WordNetLemmatizer()
        else:
            self.lemmatizer = None

    def clean_text(self, text: str) -> str:
        """Очистка текста"""
        if not text:
            return ""

        text = text.lower()
        # Удаляем пунктуацию и цифры
        text = text.translate(str.maketrans('', '', string.punctuation + string.digits))
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def get_wordnet_pos(self, treebank_tag):
        """Преобразует теги Treebank в теги WordNet"""
        if treebank_tag.startswith('J'):
            return 'a'  # adjective
        elif treebank_tag.startswith('V'):
            return 'v'  # verb
        elif treebank_tag.startswith('N'):
            return 'n'  # noun
        elif treebank_tag.startswith('R'):
            return 'r'  # adverb
        else:
            return 'n'  # по умолчанию noun

    def smart_lemmatize(self, tokens):
        """Умная лемматизация с определением части речи"""
        if not self.lemmatizer:
            return tokens

        # Получаем части речи для каждого токена
        pos_tags = nltk_pos_tag(tokens)  # Используем переименованный импорт
        lemmatized_tokens = []

        for token, tag in pos_tags:  # ИСПРАВЛЕНО: используем tag вместо pos_tag
            wordnet_pos = self.get_wordnet_pos(tag)
            lemma = self.lemmatizer.lemmatize(token, pos=wordnet_pos)
            lemmatized_tokens.append(lemma)

            # Отладочная информация для глаголов
            if tag.startswith('V') and token != lemma:
                print(f"   🔄 Лемматизация глагола: '{token}' -> '{lemma}' (POS: {tag})")

        return lemmatized_tokens

    def preprocess_text(self, text: str, return_string: bool = True, debug: bool = False):
        """Пайплайн предобработки с правильной лемматизацией"""
        if not text:
            return "" if return_string else []

        if debug:
            print(f"🔍 Исходный текст: '{text}'")

        # Очистка
        cleaned_text = self.clean_text(text)
        if debug:
            print(f"📝 После очистки: '{cleaned_text}'")

        # Токенизация
        tokens = word_tokenize(cleaned_text)
        if debug:
            print(f"🔤 Токены: {tokens}")

        # Удаление стоп-слов и коротких токенов
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        if debug:
            print(f"🚫 После удаления стоп-слов: {tokens}")

        # Умная лемматизация с определением части речи
        if self.use_lemmatization and self.lemmatizer:
            if debug:
                print("🧠 Применяем умную лемматизацию...")
            tokens = self.smart_lemmatize(tokens)
            if debug:
                print(f"✅ После лемматизации: {tokens}")

        if return_string:
            result = ' '.join(tokens)
            if debug:
                print(f"🎯 Финальный результат: '{result}'")
            return result
        else:
            if debug:
                print(f"🎯 Финальные токены: {tokens}")
            return tokens

    def preprocess_document(self, document) -> Dict:
        """Предобработка документа"""
        if not document or not document.content:
            return {
                'original_content': '',
                'processed_content': '',
                'tokens': [],
                'token_count': 0,
                'unique_tokens': set()
            }

        original_content = document.content
        processed_content = self.preprocess_text(original_content, return_string=True, debug=False)
        tokens = self.preprocess_text(original_content, return_string=False, debug=False)

        document.processed_content = processed_content

        return {
            'original_content': original_content[:200] + '...' if len(original_content) > 200 else original_content,
            'processed_content': processed_content,
            'tokens': tokens,
            'token_count': len(tokens),
            'unique_tokens': set(tokens)
        }

    def debug_term(self, term: str):
        """Отладочная функция для одного термина"""
        print(f"\n🔍 ОТЛАДКА ТЕРМИНА: '{term}'")
        print("=" * 40)

        result = self.preprocess_text(term, return_string=True, debug=True)
        return result