import nltk

def download_nltk_resources():
    """Загружает необходимые ресурсы NLTK при первом запуске"""
    resources = [
        'tokenizers/punkt_tab',
        'corpora/stopwords',
        'corpora/wordnet',
        'taggers/averaged_perceptron_tagger'
    ]
    
    for resource in resources:
        try:
            nltk.data.find(resource)
            print(f"✓ Ресурс {resource} уже установлен")
        except LookupError:
            print(f"📥 Загрузка ресурса {resource}...")
            resource_name = resource.split('/')[-1]
            nltk.download(resource_name)
            print(f"✓ Ресурс {resource} успешно загружен")

# Автоматическая загрузка при импорте
download_nltk_resources()