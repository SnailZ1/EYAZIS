# Структуры данных системы реферирования

## Основные классы и структуры

### 1. Document (концептуальная структура)

Хотя явного класса Document нет, документ представлен следующими данными:

```python
{
    'filename': str,           # Имя файла
    'text': str,              # Исходный текст
    'language': str,          # 'ru' или 'en'
    'domain': str,            # 'medical' или 'art'
    'paragraphs': List[str],  # Список абзацев
    'sentences': List[Tuple[str, int, int]]  # (текст, номер_абзаца, позиция)
}
```

### 2. Sentence (кортеж)

Предложение представлено кортежем:

```python
(
    sentence_text: str,    # Текст предложения
    paragraph_idx: int,    # Номер абзаца (0-indexed)
    sentence_idx: int      # Позиция в абзаце (0-indexed)
)
```

**Пример**:
```python
("Это первое предложение.", 0, 0)
("Это второе предложение.", 0, 1)
```

### 3. SummaryResult (словарь)

Результат реферирования:

```python
{
    'sentences': List[str],              # Выбранные предложения
    'language': str,                     # Определенный язык
    'tfidf_scores': Dict[str, float],   # TF-IDF для каждого слова
    'sentence_scores': List[Tuple[int, float, str]]  # (индекс, вес, текст)
}
```

**Пример**:
```python
{
    'sentences': [
        "Сердечно-сосудистые заболевания остаются ведущей причиной смертности.",
        "Современные методы диагностики значительно улучшили прогноз.",
        ...
    ],
    'language': 'ru',
    'tfidf_scores': {
        'заболевание': 0.234,
        'диагностика': 0.198,
        'лечение': 0.187,
        ...
    },
    'sentence_scores': [
        (0, 0.456, "Сердечно-сосудистые заболевания..."),
        (5, 0.423, "Современные методы диагностики..."),
        ...
    ]
}
```

### 4. Keyword (кортеж)

Ключевое слово с весом:

```python
(
    keyword: str,    # Термин
    score: float     # TF-IDF вес
)
```

**Пример**:
```python
[
    ('диагностика', 0.234),
    ('лечение', 0.198),
    ('пациент', 0.176),
    ...
]
```

### 5. KeywordTree (словарь)

Иерархическая структура ключевых слов:

```python
{
    'root': List[str],                    # Несгруппированные термины
    'groups': Dict[str, List[str]]        # Главный термин → связанные
}
```

**Пример**:
```python
{
    'root': ['симптом', 'профилактика'],
    'groups': {
        'диагностика': ['обследование', 'анализ', 'исследование'],
        'лечение': ['терапия', 'медикаментозное'],
        'врач': ['доктор', 'специалист']
    }
}
```

### 6. TF-IDF Matrices

#### TF (Term Frequency)

```python
tf: Dict[str, float] = {
    'слово1': частота1,
    'слово2': частота2,
    ...
}
```

**Формула**: `TF(слово) = количество_вхождений / общее_количество_слов`

**Пример**:
```python
{
    'диагностика': 0.015,  # встречается 15 раз из 1000 слов
    'лечение': 0.012,
    'пациент': 0.020
}
```

#### IDF (Inverse Document Frequency)

```python
idf: Dict[str, float] = {
    'слово1': idf1,
    'слово2': idf2,
    ...
}
```

**Формула**: `IDF(слово) = log(количество_документов / количество_документов_со_словом)`

**Пример**:
```python
{
    'диагностика': 1.386,  # log(20/10) - встречается в половине предложений
    'лечение': 1.609,      # log(20/8) - более редкое
    'и': 0.105             # log(20/19) - встречается почти везде
}
```

#### TF-IDF

```python
tfidf: Dict[str, float] = {
    'слово1': tfidf1,
    'слово2': tfidf2,
    ...
}
```

**Формула**: `TF-IDF(слово) = TF(слово) × IDF(слово)`

**Пример**:
```python
{
    'диагностика': 0.0208,  # 0.015 × 1.386
    'лечение': 0.0193,      # 0.012 × 1.609
    'и': 0.0002             # 0.002 × 0.105 - низкий вес из-за частоты
}
```

### 7. Sentence Score Calculation

Структура для хранения веса предложения:

```python
sentence_score = (
    index: int,           # Индекс предложения в документе
    score: float,         # Итоговый вес
    text: str            # Текст предложения
)
```

**Компоненты веса**:

```python
# 1. Базовый TF-IDF вес
tfidf_score = sum(tfidf[word] for word in sentence_words) / len(sentence_words)

# 2. Позиционный вес абзаца
if para_idx in [0, last]:
    para_weight = 1.5
elif para_idx in [1, last-1]:
    para_weight = 1.2
else:
    para_weight = 1.0

# 3. Позиционный вес в абзаце
if sent_idx == 0:
    sent_weight = 1.3
elif sent_idx == 1:
    sent_weight = 1.1
else:
    sent_weight = 1.0

# 4. Нормализация по длине
length_norm = min(len(words) / 20, 1.0)

# Итоговый вес
final_score = tfidf_score * para_weight * sent_weight * (0.5 + 0.5 * length_norm)
```

### 8. Knowledge Base Structure

```python
KNOWLEDGE_BASE: Dict[str, Dict[str, Dict[str, List[str]]]] = {
    'domain': {
        'language': {
            'main_term': ['related_term1', 'related_term2', ...]
        }
    }
}
```

**Пример**:
```python
{
    'medical': {
        'ru': {
            'диагностика': ['обследование', 'анализ', 'исследование'],
            'лечение': ['терапия', 'медикаментозное', 'хирургическое']
        },
        'en': {
            'diagnosis': ['examination', 'analysis', 'investigation'],
            'treatment': ['therapy', 'medication', 'surgery']
        }
    },
    'art': {
        'ru': {
            'живопись': ['картина', 'полотно', 'изображение'],
            'художник': ['живописец', 'мастер', 'автор']
        },
        'en': {
            'painting': ['picture', 'canvas', 'artwork'],
            'artist': ['painter', 'master', 'creator']
        }
    }
}
```

### 9. SC-code Structures

#### Document Node

```scs
document_id
=> nrel_main_idtf:
   [filename] (* <- lang_ru;; *);
<- concept_document;
<- concept_medical_document;
<- concept_ru_text;;
```

#### Summary Node

```scs
summary_id
=> nrel_main_idtf:
   [Реферат: filename] (* <- lang_ru;; *);
<- concept_summary;
<- concept_sentence_extraction_summary;;
```

#### Keyword Node

```scs
keyword_id
=> nrel_main_idtf:
   [термин] (* <- lang_ru;; *);
<- concept_keyword;
<- concept_medical_term;;
```

#### Semantic Links

```python
semantic_links: List[Tuple[str, str, str]] = [
    ('термин1', 'nrel_related_term', 'термин2'),
    ('термин3', 'nrel_synonym', 'термин4'),
    ...
]
```

## Внутренние структуры данных

### StopWords Set

```python
stopwords: Set[str] = {
    'и', 'в', 'во', 'не', 'что', 'он', 'на', ...
}
```

Используется для быстрой проверки принадлежности O(1).

### Word Tokenization Result

```python
words: List[str] = ['слово1', 'слово2', 'слово3', ...]
```

После фильтрации:
- Стоп-слова удалены
- Числа удалены (опционально)
- Латиница удалена для русского текста (опционально)
- Короткие слова (< 3 символов) удалены

### Sentence Tokenization Result

```python
sentences: List[Tuple[str, int, int]] = [
    ("Первое предложение.", 0, 0),
    ("Второе предложение.", 0, 1),
    ("Предложение нового абзаца.", 1, 0),
    ...
]
```

## Сложность структур данных

| Структура | Операция | Сложность |
|-----------|----------|-----------|
| Dict (TF-IDF) | Поиск | O(1) |
| Dict (TF-IDF) | Вставка | O(1) |
| List (sentences) | Доступ по индексу | O(1) |
| List (sentences) | Сортировка | O(n log n) |
| Set (stopwords) | Проверка принадлежности | O(1) |
| Dict (knowledge_base) | Поиск термина | O(1) |

## Использование памяти

Для типичного документа (~10 страниц):

- **Исходный текст**: ~50 KB
- **Токенизированные предложения**: ~100 KB
- **TF-IDF матрица**: ~10 KB (для ~500 уникальных слов)
- **Результаты**: ~5 KB
- **Общее**: ~165 KB

Система эффективна по памяти и может обрабатывать документы до 100 страниц без проблем.

## Сериализация

### Сохранение реферата (текст)

```
РЕФЕРАТ
Документ: filename.txt
Язык: RU
Предметная область: medical
Количество предложений: 10
================================================================================

1. Первое предложение реферата.

2. Второе предложение реферата.

...
```

### Сохранение ключевых слов (текст)

```
КЛЮЧЕВЫЕ СЛОВА
================================================================================

ИЕРАРХИЯ ТЕРМИНОВ:

▸ ДИАГНОСТИКА
  • обследование
  • анализ
  • исследование

▸ ЛЕЧЕНИЕ
  • терапия
  • медикаментозное

...
```

### Сохранение SC-кода (SCs формат)

```scs
// SC-code representation of document summary
// Generated: 2024-12-04 00:00:00
// Source: filename.txt

document_id
=> nrel_main_idtf:
   [filename.txt] (* <- lang_ru;; *);
<- concept_document;
<- concept_medical_document;;

...
```
