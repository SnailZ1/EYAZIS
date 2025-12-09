# Алгоритм Sentence Extraction

## Общее описание

Алгоритм извлечения ключевых предложений (Sentence Extraction) основан на методе TF-IDF (Term Frequency - Inverse Document Frequency) с дополнительным позиционным взвешиванием. Цель алгоритма - выбрать N наиболее информативных предложений из документа, которые наилучшим образом представляют его содержание.

## Входные данные

- **text**: исходный текст документа (строка)
- **num_sentences**: количество предложений для извлечения (по умолчанию 10)
- **language**: язык документа ('ru' или 'en', определяется автоматически)

## Выходные данные

- **sentences**: список из N выбранных предложений в исходном порядке
- **keywords**: список ключевых слов с весами
- **tfidf_scores**: словарь TF-IDF весов для всех слов

## Этапы алгоритма

### Этап 1: Предобработка текста

#### 1.1 Определение языка

```
ФУНКЦИЯ detect_language(text):
    ПОПЫТКА:
        lang = langdetect.detect(text)
        ЕСЛИ lang == 'ru':
            ВЕРНУТЬ 'ru'
        ИНАЧЕ:
            ВЕРНУТЬ 'en'
    ИСКЛЮЧЕНИЕ:
        ЕСЛИ в тексте есть кириллица:
            ВЕРНУТЬ 'ru'
        ИНАЧЕ:
            ВЕРНУТЬ 'en'
```

**Сложность**: O(n), где n - длина текста

#### 1.2 Токенизация предложений

```
ФУНКЦИЯ tokenize_sentences(text):
    sentences = []
    paragraphs = text.split('\n')
    
    ДЛЯ КАЖДОГО para_idx, paragraph В paragraphs:
        ЕСЛИ paragraph пустой:
            ПРОДОЛЖИТЬ
        
        # Разбиение на предложения по знакам .!?
        para_sentences = regex_split(paragraph, '[.!?]+')
        
        ДЛЯ КАЖДОГО sent_idx, sentence В para_sentences:
            ЕСЛИ sentence не пустое:
                sentences.append((sentence, para_idx, sent_idx))
    
    ВЕРНУТЬ sentences
```

**Сложность**: O(n), где n - длина текста

#### 1.3 Токенизация слов с фильтрацией

```
ФУНКЦИЯ tokenize_words(text, language):
    text = text.lower()
    words = regex_findall(text, '\b\w+\b')
    filtered_words = []
    
    ДЛЯ КАЖДОГО word В words:
        # Фильтр 1: Стоп-слова
        ЕСЛИ word В stopwords[language]:
            ПРОДОЛЖИТЬ
        
        # Фильтр 2: Числа
        ЕСЛИ word.isdigit():
            ПРОДОЛЖИТЬ
        
        # Фильтр 3: Латиница в русском тексте
        ЕСЛИ language == 'ru' И word содержит латиницу:
            ПРОДОЛЖИТЬ
        
        # Фильтр 4: Короткие слова
        ЕСЛИ len(word) < 3:
            ПРОДОЛЖИТЬ
        
        filtered_words.append(word)
    
    ВЕРНУТЬ filtered_words
```

**Сложность**: O(m), где m - количество слов

### Этап 2: Вычисление TF-IDF

#### 2.1 Вычисление TF (Term Frequency)

```
ФУНКЦИЯ calculate_tf(words):
    word_count = Counter(words)
    total_words = len(words)
    tf = {}
    
    ДЛЯ КАЖДОГО word, count В word_count:
        tf[word] = count / total_words
    
    ВЕРНУТЬ tf
```

**Формула**: 
```
TF(слово) = количество_вхождений_слова / общее_количество_слов
```

**Сложность**: O(m), где m - количество слов

#### 2.2 Вычисление IDF (Inverse Document Frequency)

```
ФУНКЦИЯ calculate_idf(documents):
    # documents - список списков слов (каждое предложение - документ)
    num_docs = len(documents)
    word_doc_count = {}
    
    ДЛЯ КАЖДОГО doc В documents:
        unique_words = set(doc)
        ДЛЯ КАЖДОГО word В unique_words:
            word_doc_count[word] += 1
    
    idf = {}
    ДЛЯ КАЖДОГО word, doc_count В word_doc_count:
        idf[word] = log(num_docs / doc_count)
    
    ВЕРНУТЬ idf
```

**Формула**:
```
IDF(слово) = log(количество_документов / количество_документов_содержащих_слово)
```

**Сложность**: O(d × k), где d - количество документов (предложений), k - средняя длина

#### 2.3 Вычисление TF-IDF

```
ФУНКЦИЯ calculate_tfidf(tf, idf):
    tfidf = {}
    
    ДЛЯ КАЖДОГО word, tf_value В tf:
        idf_value = idf.get(word, 0)
        tfidf[word] = tf_value × idf_value
    
    ВЕРНУТЬ tfidf
```

**Формула**:
```
TF-IDF(слово) = TF(слово) × IDF(слово)
```

**Сложность**: O(v), где v - размер словаря

### Этап 3: Взвешивание предложений

#### 3.1 Вычисление позиционного веса

```
ФУНКЦИЯ get_sentence_position_weight(para_idx, sent_idx, total_paras):
    # Вес абзаца
    ЕСЛИ para_idx == 0 ИЛИ para_idx == total_paras - 1:
        para_weight = 1.5  # Первый и последний абзацы важнее
    ИНАЧЕ ЕСЛИ para_idx == 1 ИЛИ para_idx == total_paras - 2:
        para_weight = 1.2  # Второй и предпоследний абзацы
    ИНАЧЕ:
        para_weight = 1.0  # Средние абзацы
    
    # Вес позиции в абзаце
    ЕСЛИ sent_idx == 0:
        sent_weight = 1.3  # Первое предложение важнее
    ИНАЧЕ ЕСЛИ sent_idx == 1:
        sent_weight = 1.1  # Второе предложение
    ИНАЧЕ:
        sent_weight = 1.0  # Остальные
    
    ВЕРНУТЬ para_weight × sent_weight
```

**Сложность**: O(1)

#### 3.2 Вычисление итогового веса предложения

```
ФУНКЦИЯ calculate_sentence_score(sentence, words, tfidf, para_idx, sent_idx, total_paras):
    # 1. Базовый TF-IDF вес
    ЕСЛИ words не пусто:
        tfidf_score = sum(tfidf.get(word, 0) ДЛЯ word В words) / len(words)
    ИНАЧЕ:
        tfidf_score = 0
    
    # 2. Позиционный вес
    position_weight = get_sentence_position_weight(para_idx, sent_idx, total_paras)
    
    # 3. Нормализация по длине
    # Оптимальная длина ~20 слов
    length_norm = min(len(words) / 20, 1.0)
    
    # 4. Итоговый вес
    final_score = tfidf_score × position_weight × (0.5 + 0.5 × length_norm)
    
    ВЕРНУТЬ final_score
```

**Формула**:
```
Score(предложение) = avg_TFIDF × position_weight × length_factor

где:
  avg_TFIDF = (Σ TF-IDF(слово)) / количество_слов
  position_weight = para_weight × sent_weight
  length_factor = 0.5 + 0.5 × min(len/20, 1)
```

**Сложность**: O(k), где k - количество слов в предложении

### Этап 4: Выбор предложений

```
ФУНКЦИЯ extract_summary(text, num_sentences):
    # 1. Предобработка
    language = detect_language(text)
    sentences = tokenize_sentences(text)
    total_paras = count_paragraphs(text)
    
    # Если предложений меньше требуемого
    ЕСЛИ len(sentences) <= num_sentences:
        ВЕРНУТЬ все предложения
    
    # 2. Токенизация каждого предложения
    sentence_words = []
    ДЛЯ КАЖДОГО sent, _, _ В sentences:
        words = tokenize_words(sent, language)
        sentence_words.append(words)
    
    # 3. Вычисление TF-IDF
    all_words = flatten(sentence_words)
    tf = calculate_tf(all_words)
    idf = calculate_idf(sentence_words)
    tfidf = calculate_tfidf(tf, idf)
    
    # 4. Вычисление весов предложений
    sentence_scores = []
    ДЛЯ КАЖДОГО idx, (sent, para_idx, sent_idx) В enumerate(sentences):
        words = sentence_words[idx]
        score = calculate_sentence_score(
            sent, words, tfidf, para_idx, sent_idx, total_paras
        )
        sentence_scores.append((idx, score, sent))
    
    # 5. Сортировка по весу и выбор топ-N
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = [s[0] ДЛЯ s В sentence_scores[:num_sentences]]
    
    # 6. Сортировка индексов для сохранения исходного порядка
    top_indices.sort()
    
    # 7. Формирование итогового реферата
    summary_sentences = [sentences[idx][0] ДЛЯ idx В top_indices]
    
    ВЕРНУТЬ {
        'sentences': summary_sentences,
        'language': language,
        'tfidf_scores': tfidf,
        'sentence_scores': sentence_scores
    }
```

**Общая сложность**: O(n + d×k + d log d), где:
- n - длина текста
- d - количество предложений
- k - средняя длина предложения

## Пример работы алгоритма

### Входной текст

```
Сердечно-сосудистые заболевания остаются ведущей причиной смертности.
Современные методы диагностики значительно улучшили прогноз пациентов.
Электрокардиография является основным методом диагностики.
Эхокардиография позволяет визуализировать структуру сердца.
Лечение включает медикаментозную терапию и хирургические методы.
```

### Шаг 1: Токенизация

**Предложения**:
1. (S1, 0, 0): "Сердечно-сосудистые заболевания..."
2. (S2, 0, 1): "Современные методы диагностики..."
3. (S3, 0, 2): "Электрокардиография является..."
4. (S4, 0, 3): "Эхокардиография позволяет..."
5. (S5, 0, 4): "Лечение включает..."

**Слова (после фильтрации)**:
- S1: [сердечно-сосудистые, заболевания, остаются, ведущей, причиной, смертности]
- S2: [современные, методы, диагностики, значительно, улучшили, прогноз, пациентов]
- S3: [электрокардиография, является, основным, методом, диагностики]
- S4: [эхокардиография, позволяет, визуализировать, структуру, сердца]
- S5: [лечение, включает, медикаментозную, терапию, хирургические, методы]

### Шаг 2: TF-IDF

**TF** (пример для нескольких слов):
- диагностики: 2/30 = 0.067
- методы: 2/30 = 0.067
- заболевания: 1/30 = 0.033

**IDF**:
- диагностики: log(5/2) = 0.916 (встречается в 2 предложениях)
- методы: log(5/2) = 0.916
- заболевания: log(5/1) = 1.609 (встречается в 1 предложении)

**TF-IDF**:
- диагностики: 0.067 × 0.916 = 0.061
- методы: 0.067 × 0.916 = 0.061
- заболевания: 0.033 × 1.609 = 0.053

### Шаг 3: Взвешивание предложений

**S1** (первое предложение первого абзаца):
- avg_TFIDF = 0.045
- position_weight = 1.5 × 1.3 = 1.95
- length_norm = min(6/20, 1) = 0.3
- **score = 0.045 × 1.95 × (0.5 + 0.5×0.3) = 0.057**

**S2**:
- avg_TFIDF = 0.052
- position_weight = 1.5 × 1.1 = 1.65
- length_norm = min(7/20, 1) = 0.35
- **score = 0.052 × 1.65 × (0.5 + 0.5×0.35) = 0.056**

### Шаг 4: Выбор топ-N

Сортировка по весу:
1. S1: 0.057
2. S2: 0.056
3. S5: 0.048
4. ...

Выбираем топ-3, сохраняем исходный порядок: S1, S2, S5

## Оптимизации

1. **Кэширование IDF**: Сохранение IDF для повторного использования
2. **Ранняя остановка**: Если предложений мало, пропускаем вычисления
3. **Векторизация**: Использование NumPy для матричных операций
4. **Параллелизация**: Обработка предложений параллельно (для больших документов)

## Ограничения и улучшения

### Текущие ограничения

1. Не учитывается семантическая близость предложений
2. Может выбирать похожие предложения
3. Не учитывается связность текста

### Возможные улучшения

1. **MMR (Maximal Marginal Relevance)**: Учет разнообразия выбранных предложений
2. **Sentence embeddings**: Использование BERT/Word2Vec для семантического анализа
3. **Graph-based methods**: TextRank, LexRank
4. **Coreference resolution**: Разрешение анафор для лучшего понимания контекста

## Сложность алгоритма

| Операция | Сложность |
|----------|-----------|
| Определение языка | O(n) |
| Токенизация предложений | O(n) |
| Токенизация слов | O(n) |
| Вычисление TF | O(m) |
| Вычисление IDF | O(d × k) |
| Взвешивание предложений | O(d × k) |
| Сортировка | O(d log d) |
| **Общая сложность** | **O(n + d×k + d log d)** |

Где:
- n - длина текста в символах
- d - количество предложений
- k - средняя длина предложения в словах
- m - общее количество слов

Для типичного документа (10 страниц, ~200 предложений):
- Время работы: < 2 секунды
- Память: < 10 MB
