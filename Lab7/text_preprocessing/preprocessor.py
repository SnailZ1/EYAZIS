import re
import string
from .nltk_setup import download_nltk_resources
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
import nltk
from typing import List, Dict

class TextPreprocessor:
    """
    Класс для предобработки текстовых документов на английском языке
    """

    def __init__(self, use_stemming=False, use_lemmatization=True, custom_stopwords=None):
        self.use_stemming = use_stemming
        self.use_lemmatization = use_lemmatization
        self.stop_words = set(stopwords.words('english'))

        if custom_stopwords:
            self.stop_words.update(custom_stopwords)

        if self.use_stemming:
            self.stemmer = PorterStemmer()

        if self.use_lemmatization:
            self.lemmatizer = WordNetLemmatizer()

    def clean_text(self, text: str) -> str:
        """Очистка текста от лишних символов и нормализация"""
        if not text:
            return ""

        text = text.lower()
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'http\S+|www\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        text = re.sub(r'\w*\d\w*', '', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def tokenize_text(self, text: str) -> List[str]:
        """Токенизация текста на слова"""
        return word_tokenize(text)

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Удаление стоп-слов из списка токенов"""
        return [token for token in tokens if token not in self.stop_words and len(token) > 2]

    def get_wordnet_pos(self, treebank_tag: str) -> str:
        """Преобразование POS-тегов Treebank в WordNet теги"""
        if treebank_tag.startswith('J'):
            return 'a'
        elif treebank_tag.startswith('V'):
            return 'v'
        elif treebank_tag.startswith('N'):
            return 'n'
        elif treebank_tag.startswith('R'):
            return 'r'
        else:
            return 'n'

    def apply_stemming(self, tokens: List[str]) -> List[str]:
        """Применение стемминга к списку токенов"""
        if not self.use_stemming:
            return tokens
        return [self.stemmer.stem(token) for token in tokens]

    def apply_lemmatization(self, tokens: List[str]) -> List[str]:
        """Применение лемматизации к списку токенов"""
        if not self.use_lemmatization:
            return tokens

        pos_tags = nltk.pos_tag(tokens)
        lemmatized_tokens = []
        for token, pos_tag in pos_tags:
            wordnet_pos = self.get_wordnet_pos(pos_tag)
            lemma = self.lemmatizer.lemmatize(token, pos=wordnet_pos)
            lemmatized_tokens.append(lemma)

        return lemmatized_tokens

    def preprocess_text(self, text: str, return_string: bool = False):
        """Полный пайплайн предобработки текста"""
        if not text:
            return "" if return_string else []

        cleaned_text = self.clean_text(text)
        tokens = self.tokenize_text(cleaned_text)
        tokens = self.remove_stopwords(tokens)

        if self.use_lemmatization:
            tokens = self.apply_lemmatization(tokens)

        if self.use_stemming:
            tokens = self.apply_stemming(tokens)

        if return_string:
            return ' '.join(tokens)
        else:
            return tokens

    def preprocess_document(self, document) -> Dict:
        """Предобработка всего документа"""
        if not document or not document.content:
            return {
                'original_content': '',
                'processed_content': '',
                'tokens': [],
                'unique_tokens': set(),
                'token_count': 0,
                'vocabulary_size': 0
            }

        original_content = document.content
        processed_content = self.preprocess_text(original_content, return_string=True)
        tokens = self.preprocess_text(original_content, return_string=False)

        document.processed_content = processed_content

        return {
            'original_content': original_content[:500] + '...' if len(original_content) > 500 else original_content,
            'processed_content': processed_content[:500] + '...' if len(processed_content) > 500 else processed_content,
            'tokens': tokens,
            'unique_tokens': set(tokens),
            'token_count': len(tokens),
            'vocabulary_size': len(set(tokens))
        }