from .preprocessor import TextPreprocessor

class PreprocessorFactory:
    """Фабрика для создания различных конфигураций препроцессоров"""
    
    @staticmethod
    def create_basic_preprocessor():
        """Базовый препроцессор только с очисткой и стоп-словами"""
        return TextPreprocessor(use_stemming=False, use_lemmatization=False)
    
    @staticmethod
    def create_stemming_preprocessor():
        """Препроцессор со стеммингом"""
        return TextPreprocessor(use_stemming=True, use_lemmatization=False)
    
    @staticmethod
    def create_lemmatization_preprocessor():
        """Препроцессор с лемматизацией"""
        return TextPreprocessor(use_stemming=False, use_lemmatization=True)
    
    @staticmethod
    def create_advanced_preprocessor():
        """Продвинутый препроцессор со стеммингом и лемматизацией"""
        return TextPreprocessor(use_stemming=True, use_lemmatization=True)
    
    @staticmethod
    def create_custom_preprocessor(custom_stopwords=None, use_stemming=True, use_lemmatization=False):
        """Кастомный препроцессор с пользовательскими настройками"""
        return TextPreprocessor(
            use_stemming=use_stemming,
            use_lemmatization=use_lemmatization,
            custom_stopwords=custom_stopwords
        )