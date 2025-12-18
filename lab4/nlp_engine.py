
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag, ne_chunk
from deep_translator import GoogleTranslator
from db_manager import DBManager
import time


TAG_DESCRIPTIONS = {
    'CC': 'Coordinating conjunction',
    'CD': 'Cardinal number',
    'DT': 'Determiner',
    'EX': 'Existential there',
    'FW': 'Foreign word',
    'IN': 'Preposition or subordinating conjunction',
    'JJ': 'Adjective',
    'JJR': 'Adjective, comparative',
    'JJS': 'Adjective, superlative',
    'LS': 'List item marker',
    'MD': 'Modal',
    'NN': 'Noun, singular or mass',
    'NNS': 'Noun, plural',
    'NNP': 'Proper noun, singular',
    'NNPS': 'Proper noun, plural',
    'PDT': 'Predeterminer',
    'POS': 'Possessive ending',
    'PRP': 'Personal pronoun',
    'PRP$': 'Possessive pronoun',
    'RB': 'Adverb',
    'RBR': 'Adverb, comparative',
    'RBS': 'Adverb, superlative',
    'RP': 'Particle',
    'SYM': 'Symbol',
    'TO': 'to',
    'UH': 'Interjection',
    'VB': 'Verb, base form',
    'VBD': 'Verb, past tense',
    'VBG': 'Verb, gerund or present participle',
    'VBN': 'Verb, past participle',
    'VBP': 'Verb, non-3rd person singular present',
    'VBZ': 'Verb, 3rd person singular present',
    'WDT': 'Wh-determiner',
    'WP': 'Wh-pronoun',
    'WP$': 'Possessive wh-pronoun',
    'WRB': 'Wh-adverb'
}

class NLPEngine:
    def __init__(self):
        self._check_nltk_resources()
        self.db = DBManager()
        self.translator = GoogleTranslator(source='en', target='ru')

    def _check_nltk_resources(self):
        resources = [
            'tokenizers/punkt',
            'taggers/averaged_perceptron_tagger',
            'chunkers/maxent_ne_chunker',
            'corpora/words'
        ]
        for res in resources:
            try:
                nltk.data.find(res)
            except LookupError:
                # Handle specific names for download if they differ from resource path
                name = res.split('/')[-1]
                try:
                    nltk.download(name)
                except PermissionError:
                    # On Windows, sometimes deleting the zip fails.
                    # If the resource is found now, we are good.
                    print(f"Warning: PermissionError while downloading {name}. Checking if installed...")
                
                # Verify installation
                try:
                    nltk.data.find(res)
                except LookupError:
                    print(f"Error: Failed to download/find resource {res}")

    def process_text(self, text):
        """
        Полная обработка текста:
        1. Токенизация и POS-теггинг
        2. Перевод (поиск в БД или онлайн)
        3. Сбор статистики
        4. Формирование перевода текста
        """
        sentences = sent_tokenize(text)
        
        full_translation = []
        word_stats = {}
        total_words = 0
        translated_counter = 0
        
        # Для построения списка слов
        processed_words_list = []

        for sentence in sentences:
            tokens = word_tokenize(sentence)
            tags = pos_tag(tokens)
            
            sent_translation = []
            
            for word, tag in tags:
                if not word.isalnum():
                    sent_translation.append(word)
                    continue
                
                total_words += 1
                
                # Поиск в БД
                db_entry = self.db.get_word(word)
                
                if db_entry:
                    ru_word, stored_tag, freq = db_entry
                    # Обновляем частоту в БД (происходит автоматически в add_word, но нам нужно просто учесть это)
                    # Но пока мы просто читаем. 
                    # Логика: если слово встретилось в тексте, мы должны "добавить" его чтобы +1 к частоте
                    self.db.add_word(word, ru_word, tag) # Обновляем частоту и, возможно, тег
                    translated_counter += 1
                    sent_translation.append(ru_word)
                    
                    processed_words_list.append({
                        'word': word,
                        'trans': ru_word,
                        'tag': tag,
                        'desc': TAG_DESCRIPTIONS.get(tag, 'Unknown')
                    })
                else:
                    # Перевод через API
                    # Попытка перевода с повтором (retries)
                    max_retries = 3
                    ru_word = None
                    
                    for attempt in range(max_retries):
                        try:
                            # Пауза чтобы не банило
                            time.sleep(0.1) 
                            ru_word = self.translator.translate(word)
                            if ru_word:
                                break
                        except Exception:
                            if attempt == max_retries - 1:
                                # Если это была последняя попытка, просто используем оригинал
                                print(f"Failed to translate '{word}' after {max_retries} attempts.")
                            continue

                    if not ru_word: 
                        ru_word = word
                    
                    # Сохраняем в БД даже если не перевелось? 
                    # Лучше сохранять если перевелось нормально. 
                    # Но по логике старого кода - сохраняем.
                    # Если ru_word == word, возможно нет смысла в БД, но оставим как было.
                    self.db.add_word(word, ru_word, tag)
                    
                    sent_translation.append(ru_word)
                    translated_counter += 1
                    
                    processed_words_list.append({
                        'word': word,
                        'trans': ru_word,
                        'tag': tag,
                        'desc': TAG_DESCRIPTIONS.get(tag, 'Unknown')
                    })
            
            full_translation.append(" ".join(sent_translation))

        # Сортировка списка слов по частоте (в рамках текущего текста или глобально?
        # Т.к. есть БД, логично показать статистику из БД, но часто просят "статистику текста".
        # Сделаем статистику по текущему тексту.
        
        # Сгруппируем processed_words_list
        word_frequency = {}
        for item in processed_words_list:
            w = item['word'].lower()
            if w not in word_frequency:
                word_frequency[w] = {
                    'word': item['word'], # Original case
                    'trans': item['trans'],
                    'tag': item['tag'],
                    'desc': item['desc'],
                    'count': 0
                }
            word_frequency[w]['count'] += 1
            
        sorted_words = sorted(word_frequency.values(), key=lambda x: x['count'], reverse=True)
        
        return {
            'total_words': total_words,
            'translated_count': translated_counter,
            'full_translation': "\n".join(full_translation),
            'word_stats': sorted_words,
            'sentences': sentences # Возвращаем исходные предложения для выбора дерева
        }

    def get_syntax_tree(self, sentence):
        """Строит синтаксическое дерево для предложения"""
        # Используем NLTK ne_chunk для простой структуры
        tokens = word_tokenize(sentence)
        tags = pos_tag(tokens)
        chunked = ne_chunk(tags)
        return str(chunked) # Возвращаем строковое представление (скобочная нотация)
