import os
import gensim.downloader as api
from gensim.models import KeyedVectors

def download_word2vec_model(model_name='glove-wiki-gigaword-200', save_path='models/'):
    """
    Загружает и сохраняет предобученную модель Word2Vec
    """
    os.makedirs(save_path, exist_ok=True)
    
    model_file = os.path.join(save_path, f"{model_name}.bin")
    
    if os.path.exists(model_file):
        print(f"Модель уже загружена: {model_file}")
        return model_file
    
    try:
        print(f"Загрузка модели {model_name}...")
        model = api.load(model_name)
        
        # Сохраняем в бинарном формате
        if isinstance(model, KeyedVectors):
            model.save_word2vec_format(model_file, binary=True)
        else:
            model.wv.save_word2vec_format(model_file, binary=True)
        
        print(f"Модель сохранена: {model_file}")
        return model_file
        
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
        return None

if __name__ == "__main__":
    # Загружаем легкую модель для начала
    model_path = download_word2vec_model('glove-wiki-gigaword-200')
    if model_path:
        print(f"Модель готова к использованию: {model_path}")