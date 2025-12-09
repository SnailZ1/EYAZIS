# Структура SC-кода и интеграция с OSTIS

## Введение в OSTIS

OSTIS (Open Semantic Technology for Intelligent Systems) - это технология разработки интеллектуальных систем, основанная на семантических сетях. SC-код (Semantic Code) - это формальный язык представления знаний в OSTIS.

## Формат SCs

SCs (Semantic Code string) - текстовый формат представления SC-кода. Основные элементы:

### Узлы (Nodes)

```scs
node_identifier
```

### Связи (Edges)

```scs
source_node
=> relation_type: target_node;;
```

### Атрибуты

```scs
node
=> nrel_main_idtf:
   [Название] (* <- lang_ru;; *);;
```

## Структура SC-кода для документа

### 1. Определение документа

```scs
// Идентификатор документа
medical_ru_1

// Основной идентификатор (название)
=> nrel_main_idtf:
   [medical_ru_1.txt] (* <- lang_ru;; *);

// Классификация
<- concept_document;           // Это документ
<- concept_medical_document;   // Медицинский документ
<- concept_ru_text;;           // Русскоязычный текст
```

**Объяснение**:
- `medical_ru_1` - уникальный идентификатор документа
- `nrel_main_idtf` - отношение "главный идентификатор"
- `<-` - принадлежность к классу
- `;;` - конец определения

### 2. Определение реферата

```scs
// Идентификатор реферата
medical_ru_1_summary

// Название
=> nrel_main_idtf:
   [Реферат: medical_ru_1.txt] (* <- lang_ru;; *);

// Классификация
<- concept_summary;                      // Это реферат
<- concept_sentence_extraction_summary;; // Метод: sentence extraction
```

### 3. Связь документа и реферата

```scs
medical_ru_1
=> nrel_summary: medical_ru_1_summary;;
```

**Семантика**: "Документ medical_ru_1 имеет реферат medical_ru_1_summary"

### 4. Предложения реферата

```scs
// Первое предложение
medical_ru_1_summary_sent_1
=> nrel_main_idtf:
   ["Сердечно-сосудистые заболевания остаются..."] (* <- lang_ru;; *);
<- concept_sentence;      // Это предложение
<- rrel_sentence_1;;      // Порядковый номер

// Связь с рефератом
medical_ru_1_summary
=> nrel_includes: medical_ru_1_summary_sent_1;;
```

**Семантика**: "Реферат включает предложение №1"

### 5. Ключевые слова

```scs
// Ключевое слово
medical_ru_1_kw_диагностика
=> nrel_main_idtf:
   [диагностика] (* <- lang_ru;; *);
<- concept_keyword;        // Это ключевое слово
<- concept_medical_term;;  // Медицинский термин

// Связь с документом
medical_ru_1
=> nrel_key_concept: medical_ru_1_kw_диагностика;;
```

**Семантика**: "Ключевое понятие документа - диагностика"

### 6. Семантические связи между терминами

```scs
// Связанные термины
medical_ru_1_kw_диагностика
=> nrel_related_term: medical_ru_1_kw_обследование;
=> nrel_related_term: medical_ru_1_kw_анализ;;

// Синонимы
medical_ru_1_kw_врач
=> nrel_synonym: medical_ru_1_kw_доктор;;
```

**Типы связей**:
- `nrel_related_term` - связанный термин (гипоним, гипероним)
- `nrel_synonym` - синоним
- `nrel_hyponym` - гипоним (более узкое понятие)
- `nrel_hypernym` - гипероним (более широкое понятие)

### 7. Метаданные

```scs
medical_ru_1
=> nrel_language: lang_ru;
=> nrel_domain: concept_medical;
=> nrel_sentence_count: [10];
=> nrel_keyword_count: [20];;
```

## Полный пример SC-кода

```scs
// SC-code representation of document summary
// Generated: 2024-12-04 00:00:00
// Source: medical_ru_1.txt

// ========== ДОКУМЕНТ ==========

medical_ru_1
=> nrel_main_idtf:
   [medical_ru_1.txt] (* <- lang_ru;; *);
<- concept_document;
<- concept_medical_document;
<- concept_ru_text;;

// ========== РЕФЕРАТ ==========

medical_ru_1_summary
=> nrel_main_idtf:
   [Реферат: medical_ru_1.txt] (* <- lang_ru;; *);
<- concept_summary;
<- concept_sentence_extraction_summary;;

medical_ru_1
=> nrel_summary: medical_ru_1_summary;;

// ========== ПРЕДЛОЖЕНИЯ ==========

medical_ru_1_summary_sent_1
=> nrel_main_idtf:
   ["Сердечно-сосудистые заболевания остаются ведущей причиной смертности."] 
   (* <- lang_ru;; *);
<- concept_sentence;
<- rrel_sentence_1;;

medical_ru_1_summary
=> nrel_includes: medical_ru_1_summary_sent_1;;

medical_ru_1_summary_sent_2
=> nrel_main_idtf:
   ["Современные методы диагностики значительно улучшили прогноз."] 
   (* <- lang_ru;; *);
<- concept_sentence;
<- rrel_sentence_2;;

medical_ru_1_summary
=> nrel_includes: medical_ru_1_summary_sent_2;;

// ========== КЛЮЧЕВЫЕ СЛОВА ==========

medical_ru_1_kw_диагностика
=> nrel_main_idtf:
   [диагностика] (* <- lang_ru;; *);
<- concept_keyword;
<- concept_medical_term;;

medical_ru_1
=> nrel_key_concept: medical_ru_1_kw_диагностика;;

medical_ru_1_kw_лечение
=> nrel_main_idtf:
   [лечение] (* <- lang_ru;; *);
<- concept_keyword;
<- concept_medical_term;;

medical_ru_1
=> nrel_key_concept: medical_ru_1_kw_лечение;;

// ========== СЕМАНТИЧЕСКИЕ СВЯЗИ ==========

medical_ru_1_kw_диагностика
=> nrel_related_term: medical_ru_1_kw_обследование;
=> nrel_related_term: medical_ru_1_kw_анализ;;

medical_ru_1_kw_лечение
=> nrel_related_term: medical_ru_1_kw_терапия;;

// ========== МЕТАДАННЫЕ ==========

medical_ru_1
=> nrel_language: lang_ru;
=> nrel_domain: concept_medical;
=> nrel_sentence_count: [10];
=> nrel_keyword_count: [20];;
```

## Онтология системы

### Классы концептов

```scs
// Базовые классы
concept_document;           // Документ
concept_summary;            // Реферат
concept_sentence;           // Предложение
concept_keyword;            // Ключевое слово

// Типы документов
concept_medical_document;   // Медицинский документ
concept_art_document;       // Искусствоведческий документ

// Языки
concept_ru_text;            // Русскоязычный текст
concept_en_text;            // Англоязычный текст

// Методы реферирования
concept_sentence_extraction_summary;  // Sentence extraction
concept_abstraction_summary;          // Abstraction

// Предметные области
concept_medical_term;       // Медицинский термин
concept_art_term;           // Искусствоведческий термин
```

### Отношения (Relations)

```scs
// Неролевые отношения (nrel - non-role relation)
nrel_summary;               // "имеет реферат"
nrel_includes;              // "включает"
nrel_key_concept;           // "ключевое понятие"
nrel_related_term;          // "связанный термин"
nrel_synonym;               // "синоним"
nrel_main_idtf;             // "главный идентификатор"
nrel_language;              // "язык"
nrel_domain;                // "предметная область"
nrel_sentence_count;        // "количество предложений"
nrel_keyword_count;         // "количество ключевых слов"

// Ролевые отношения (rrel - role relation)
rrel_sentence_1;            // "предложение №1"
rrel_sentence_2;            // "предложение №2"
// ... и т.д.
```

## Использование SC-кода

### 1. Импорт в OSTIS

Сгенерированные `.scs` файлы могут быть импортированы в OSTIS платформу:

```bash
# Копирование в базу знаний OSTIS
cp output.scs /path/to/ostis/kb/

# Перезапуск OSTIS для загрузки новых знаний
ostis-restart
```

### 2. Запросы к базе знаний

После импорта можно выполнять запросы:

**Запрос 1**: Найти все рефераты медицинских документов

```scs
?x
<- concept_medical_document;
=> nrel_summary: ?summary;;
```

**Запрос 2**: Найти все ключевые слова документа

```scs
medical_ru_1
=> nrel_key_concept: ?keyword;;
```

**Запрос 3**: Найти связанные термины

```scs
medical_ru_1_kw_диагностика
=> nrel_related_term: ?related;;
```

### 3. Визуализация в SCg

SC-код может быть визуализирован в виде графа (SCg - SC-graph):

```
[medical_ru_1] --nrel_summary--> [medical_ru_1_summary]
                                        |
                                        | nrel_includes
                                        ↓
                                  [sent_1] [sent_2] ...
                                  
[medical_ru_1] --nrel_key_concept--> [диагностика]
                                           |
                                           | nrel_related_term
                                           ↓
                                     [обследование]
```

## Преимущества SC-кода

1. **Формальность**: Строгая семантика, машинная обработка
2. **Расширяемость**: Легко добавлять новые отношения и концепты
3. **Интероперабельность**: Стандартный формат для обмена знаниями
4. **Логический вывод**: Возможность автоматического вывода новых знаний
5. **Многоязычность**: Поддержка нескольких языков

## Интеграция с системой реферирования

### Улучшение извлечения ключевых слов

SC-код используется для:

1. **Группировки терминов**: Связанные термины объединяются
2. **Усиления весов**: Термины из базы знаний получают бонус
3. **Расширения**: Добавление связанных терминов с пониженным весом

```python
# Пример использования
if keyword in knowledge_base:
    tfidf_score *= 1.5  # Усиление доменного термина
    
    # Добавление связанных терминов
    for related in knowledge_base[keyword]:
        if related not in keywords:
            keywords[related] = tfidf_score * 0.5
```

### Построение иерархии

```python
# Группировка по семантическим связям
for main_term, related_terms in knowledge_base.items():
    if main_term in keywords:
        group = [r for r in related_terms if r in keywords]
        if group:
            hierarchy[main_term] = group
```

## Ограничения текущей реализации

1. **Упрощенная онтология**: Базовый набор отношений
2. **Статическая база знаний**: Не обновляется автоматически
3. **Ручное создание связей**: Требуется экспертная разметка
4. **Отсутствие логического вывода**: Только хранение, без рассуждений

## Возможные улучшения

1. **Автоматическое извлечение отношений**: Использование NLP для поиска связей
2. **Динамическое обновление**: Пополнение базы знаний из обработанных документов
3. **Интеграция с внешними онтологиями**: SNOMED CT для медицины, Getty AAT для искусства
4. **Логический вывод**: Использование правил для автоматического вывода
5. **Многоуровневая иерархия**: Более сложные таксономии терминов
