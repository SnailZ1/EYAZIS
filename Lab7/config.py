# config.py
import os

class Config:
    # Пути к моделям
    WORD2VEC_MODELS = {
        'light': 'models/test_model.bin',
        'google_news': 'models/word2vec-google-news-300.bin',
        'glove_100': 'models/glove-wiki-gigaword-100.bin',
        'glove_300': 'models/glove-wiki-gigaword-300.bin'
    }
    
    # Настройки семантического поиска
    SEMANTIC_SEARCH = {
        'similarity_threshold': 0.6,
        'top_similar_words': 5,
        'enabled': True
    }
    
    @classmethod
    def get_model_path(cls, model_name='light'):
        return cls.WORD2VEC_MODELS.get(model_name, cls.WORD2VEC_MODELS['light'])