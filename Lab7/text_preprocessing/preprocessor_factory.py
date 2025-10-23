# text_preprocessing/preprocessor_factory.py
from .preprocessor import TextPreprocessor


class PreprocessorFactory:
    """Фабрика для создания различных конфигураций препроцессоров"""

    @staticmethod
    def create_basic_preprocessor():
        """Базовый препроцессор только с очисткой и стоп-словами"""
        return TextPreprocessor(use_lemmatization=False)

    @staticmethod
    def create_lemmatization_preprocessor():
        """Препроцессор с лемматизацией"""
        return TextPreprocessor(use_lemmatization=True)

    @staticmethod
    def create_custom_preprocessor(custom_stopwords=None, use_lemmatization=True):
        """Кастомный препроцессор с пользовательскими настройками"""
        return TextPreprocessor(
            use_lemmatization=use_lemmatization,
            custom_stopwords=custom_stopwords
        )