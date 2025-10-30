from flask import Flask, render_template, request, jsonify
import sys
import os
import json
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from indexing.index_builder import IndexBuilder
from text_preprocessing.preprocessor_factory import PreprocessorFactory
from vector_storage.chroma_storage import ChromaStorage
from documents_processing.collector import DocumentCollector  # Добавляем импорт
from text_preprocessing.batching import BatchTextPreprocessor  # Добавляем импорт
from .json_utils import safe_json_response, CustomJSONEncoder


class SearchApp:
    """Класс для управления поисковым приложением"""

    def __init__(self):
        self.app = Flask(__name__, 
                        template_folder='templates',
                        static_folder='static')
        self.app.config['SECRET_KEY'] = 'search-system-secret-key'
        self.app.json_encoder = CustomJSONEncoder
        self.index_builder = None
        self.preprocessor = None
        self.is_loaded = False
        self.all_documents = []  # Храним все документы

        self.setup_routes()
        self.load_search_system()

    def load_search_system(self):
        """Загрузка поисковой системы с гибридным селектором"""
        try:
            print("Загрузка поисковой системы с гибридным селектором...")

            # Создаем препроцессор
            self.preprocessor = PreprocessorFactory.create_lemmatization_preprocessor()


            # Пытаемся загрузить существующий индекс
            try:
                # Загружаем словарь
                self.index_builder = IndexBuilder(
                    use_vector_db=True,
                    use_document_selector=True,  # ВКЛЮЧАЕМ селектор!
                    use_semantic_search=True    # Можно включить позже
                )
                
                
                self.index_builder.vocabulary.load_vocabulary("search_index/vocabulary.json")
                self.index_builder.vector_storage = ChromaStorage()
                
                # Инициализируем TF-IDF калькулятор
                from indexing.tfidf_calculator import TFIDFCalculator
                self.index_builder.tfidf_calculator = TFIDFCalculator(self.index_builder.vocabulary)
                
                # Загружаем документы для селектора
                self._load_documents_for_selector()
                
                self.is_loaded = True
                print("✅ Поисковая система с гибридным селектором успешно загружена")
                
            except Exception as e:
                print(f"❌ Не удалось загрузить индекс: {e}")
                print("🔄 Пробуем построить индекс с нуля...")
                self._build_index_from_scratch()

        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            self.is_loaded = False

    def _load_documents_for_selector(self):
        """Загружает документы для работы селектора"""
        try:
            # Собираем документы из папки docs
            collector = DocumentCollector()
            self.all_documents = collector.collect_documents("docs", recursive=True)
            
            if self.all_documents:
                # Предобрабатываем документы
                batch_processor = BatchTextPreprocessor(self.preprocessor)
                batch_processor.preprocess_collection(self.all_documents)
                
                # Сохраняем в index_builder для селектора
                self.index_builder.all_documents = self.all_documents
                print(f"✅ Загружено {len(self.all_documents)} документов для селектора")
            else:
                print("⚠️  Не найдено документов для селектора")
                
        except Exception as e:
            print(f"❌ Ошибка загрузки документов для селектора: {e}")

    def _build_index_from_scratch(self):
        """Строит индекс с нуля"""
        try:
            # Собираем документы
            collector = DocumentCollector()
            documents = collector.collect_documents("docs", recursive=True)
            
            if not documents:
                print("❌ Не найдено документов для индексации")
                return
                
            # Предобрабатываем
            batch_processor = BatchTextPreprocessor(self.preprocessor)
            batch_processor.preprocess_collection(documents)
            
            # Строим индекс с селектором
            self.index_builder = IndexBuilder(
                use_vector_db=True,
                use_document_selector=True,
                use_semantic_search=False
            )
            self.index_builder.build_index(documents)
            self.index_builder.save_index("search_index")
            
            self.all_documents = documents
            self.is_loaded = True
            print("✅ Индекс успешно построен с гибридным селектором")
            
        except Exception as e:
            print(f"❌ Ошибка построения индекса: {e}")

    def setup_routes(self):
        """Настройка маршрутов Flask"""

        @self.app.route('/')
        def index():
            """Главная страница с поиском"""
            total_docs = 0
            selection_stats = {}
            
            if self.index_builder and self.index_builder.vector_storage:
                total_docs = self.index_builder.vector_storage.get_document_count()
                
            if self.index_builder and self.index_builder.document_selector:
                selection_stats = self.index_builder.document_selector.get_selection_statistics()

            return render_template('index.html',
                                   system_loaded=self.is_loaded,
                                   total_documents=total_docs,
                                   selection_stats=selection_stats)

        @self.app.route('/search', methods=['POST'])
        def search():
            """Обработка поискового запроса с гибридным селектором"""
            if not self.is_loaded:
                return jsonify({'error': 'Поисковая система не загружена'}), 500

            try:
                # Получаем запрос из формы
                query = request.form.get('query', '').strip()
                top_k = int(request.form.get('top_k', 10))
                show_analysis = request.form.get('show_analysis', 'false') == 'true'

                if not query:
                    return jsonify({'error': 'Пустой запрос'}), 400

                print(f"🔍 Поиск запроса с гибридным селектором: '{query}'")

                # Выполняем поиск (теперь автоматически использует селектор)
                results = self.index_builder.search(query, self.preprocessor, top_k=top_k)

                # Получаем статистику селектора и расширение запроса
                selection_stats = {}
                expansion_result = {}
                
                if self.index_builder.document_selector:
                    selection_stats = self._safe_serialize_stats(
                        self.index_builder.document_selector.get_selection_statistics()
                    )
                    expansion_result = self._safe_serialize_expansion(
                        self.index_builder.document_selector.get_last_expansion_result()
                    )

                # Форматируем результаты для отображения
                formatted_results = []
                for result in results:
                    # Безопасно сериализуем каждый результат
                    safe_result = self._safe_serialize_result(result)
                    formatted_results.append(safe_result)

                response_data = {
                    'query': query,
                    'total_found': len(results),
                    'results': formatted_results,
                    'selection_stats': selection_stats,
                    'expansion_result': expansion_result
                }

                # Анализ запроса (если нужно)
                if show_analysis:
                    query_analysis = self.index_builder.analyze_query(query, self.preprocessor)
                    response_data['query_analysis'] = self._safe_serialize_analysis(query_analysis)

                # Используем безопасную сериализацию
                return safe_json_response(response_data)

            except Exception as e:
                print(f"Ошибка поиска: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'Ошибка поиска: {str(e)}'}), 500

        @self.app.route('/selection-stats')
        def selection_stats():
            """Статистика работы селектора"""
            if not self.is_loaded or not self.index_builder.document_selector:
                return jsonify({'error': 'Селектор не активирован'}), 500

            stats = self.index_builder.document_selector.get_selection_statistics()
            return safe_json_response(self._safe_serialize_stats(stats))

        @self.app.route('/analyze-query', methods=['POST'])
        def analyze_query():
            """Анализ запроса без выполнения поиска"""
            if not self.is_loaded:
                return jsonify({'error': 'Поисковая система не загружена'}), 500

            try:
                query = request.form.get('query', '').strip()
                if not query:
                    return jsonify({'error': 'Пустой запрос'}), 400

                analysis = self.index_builder.analyze_query(query, self.preprocessor)
                return safe_json_response(self._safe_serialize_analysis(analysis))

            except Exception as e:
                return jsonify({'error': f'Ошибка анализа: {str(e)}'}), 500

        @self.app.route('/stats')
        def stats():
            """Статистика системы"""
            if not self.is_loaded:
                return jsonify({'error': 'Система не загружена'}), 500

            stats = self.index_builder.get_index_statistics()
            return safe_json_response(self._safe_serialize_stats(stats))

        @self.app.route('/health')
        def health():
            """Проверка состояния системы"""
            total_docs = 0
            if self.index_builder and self.index_builder.vector_storage:
                total_docs = self.index_builder.vector_storage.get_document_count()

            return jsonify({
                'status': 'ready' if self.is_loaded else 'loading',
                'documents_loaded': total_docs
            })

        @self.app.route('/debug-query', methods=['POST'])
        def debug_query():
            """Отладочная информация по запросу"""
            if not self.is_loaded:
                return jsonify({'error': 'Поисковая система не загружена'}), 500

            try:
                query = request.form.get('query', '').strip()
                if not query:
                    return jsonify({'error': 'Пустой запрос'}), 400

                # Детальная отладка
                analysis = self.index_builder.tfidf_calculator.debug_query_processing(query, self.preprocessor)

                return jsonify({
                    'query': query,
                    'debug_info': 'Проверьте консоль сервера для детальной отладки'
                })

            except Exception as e:
                return jsonify({'error': f'Ошибка отладки: {str(e)}'}), 500

        @self.app.route('/vocabulary-stats')
        def vocabulary_stats():
            """Статистика словаря"""
            if not self.is_loaded:
                return jsonify({'error': 'Система не загружена'}), 500

            vocab = self.index_builder.vocabulary
            stats = vocab.get_statistics()

            # Примеры терминов
            sample_terms = list(vocab.term_to_index.keys())[:50]

            return jsonify({
                'vocabulary_size': stats['vocabulary_size'],
                'total_documents': stats['total_documents'],
                'sample_terms': sample_terms,
                'most_frequent_terms': stats['most_frequent_terms'][:20]
            })
        
    def _safe_serialize_stats(self, stats):
        """Безопасная сериализация статистики"""
        if not stats:
            return {}
        
        safe_stats = {}
        for key, value in stats.items():
            if value is None:
                safe_stats[key] = None
            elif isinstance(value, (int, str, bool)):
                safe_stats[key] = value
            elif isinstance(value, (float, np.float32, np.float64)):
                safe_stats[key] = float(value)
            elif isinstance(value, dict):
                safe_stats[key] = self._safe_serialize_stats(value)
            elif isinstance(value, list):
                safe_stats[key] = [self._safe_serialize_stats(item) if isinstance(item, dict) else item for item in value]
            else:
                safe_stats[key] = str(value)
        
        return safe_stats

    def _safe_serialize_expansion(self, expansion_result):
        """Безопасная сериализация результата расширения запроса"""
        if not expansion_result:
            return {
                'original_terms': [],
                'expanded_terms': [],
                'similar_terms': {},
                'all_terms': [],
                'expansion_ratio': 1.0
            }
        
        safe_expansion = {}
        for key, value in expansion_result.items():
            if key == 'similar_terms' and isinstance(value, dict):
                # Сериализуем similar_terms
                safe_similar = {}
                for term, similar_list in value.items():
                    safe_similar[term] = [
                        (similar_word, float(score)) 
                        for similar_word, score in similar_list
                    ]
                safe_expansion[key] = safe_similar
            elif key == 'expansion_ratio':
                safe_expansion[key] = float(value)
            elif isinstance(value, list):
                safe_expansion[key] = [str(item) for item in value]
            else:
                safe_expansion[key] = value
        
        return safe_expansion

    def _safe_serialize_result(self, result):
        """Безопасная сериализация результата поиска"""
        if not result:
            return {}
        
        safe_result = {}
        for key, value in result.items():
            if key == 'similarity_score':
                safe_result[key] = float(value)
            elif key == 'metadata' and isinstance(value, dict):
                safe_result[key] = self._safe_serialize_stats(value)
            elif key == 'semantic_info' and isinstance(value, dict):
                safe_semantic = {}
                for sem_key, sem_value in value.items():
                    if sem_key in ['original_score', 'semantic_score', 'combined_score']:
                        safe_semantic[sem_key] = float(sem_value)
                    elif sem_key == 'expansion_result':
                        safe_semantic[sem_key] = self._safe_serialize_expansion(sem_value)
                    else:
                        safe_semantic[sem_key] = sem_value
                safe_result[key] = safe_semantic
            elif key == 'distance':
                safe_result[key] = float(value) if value is not None else None
            else:
                safe_result[key] = value
        
        return safe_result

    def _safe_serialize_analysis(self, analysis):
        """Безопасная сериализация анализа запроса"""
        if not analysis:
            return {}
        
        safe_analysis = {}
        for key, value in analysis.items():
            if key == 'term_analysis' and isinstance(value, list):
                safe_terms = []
                for term_info in value:
                    safe_term = {}
                    for term_key, term_value in term_info.items():
                        if term_key in ['idf', 'weight_in_query']:
                            safe_term[term_key] = float(term_value)
                        else:
                            safe_term[term_key] = term_value
                    safe_terms.append(safe_term)
                safe_analysis[key] = safe_terms
            else:
                safe_analysis[key] = value
        
        return safe_analysis

    def _generate_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """Генерация сниппета с подсветкой запроса"""
        if not text:
            return ""

        query_terms = query.lower().split()
        text_lower = text.lower()

        # Ищем позицию первого вхождения любого термина запроса
        best_position = len(text)
        for term in query_terms:
            pos = text_lower.find(term)
            if pos != -1 and pos < best_position:
                best_position = pos

        # Вырезаем фрагмент вокруг найденного термина
        start = max(0, best_position - 50)
        end = min(len(text), start + max_length)

        snippet = text[start:end]

        # Добавляем многоточие если текст обрезан
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        # Подсветка терминов запроса
        for term in query_terms:
            snippet = self._highlight_term(snippet, term)

        return snippet

    def _highlight_term(self, text: str, term: str) -> str:
        """Подсветка термина в тексте"""
        import re
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        return pattern.sub(f'<mark>{term}</mark>', text)

    def _find_query_terms(self, query: str, text: str) -> list:
        """Поиск терминов запроса в тексте"""
        query_terms = set(query.lower().split())
        text_terms = set(text.lower().split())
        return list(query_terms & text_terms)

    def run(self, host='127.0.0.1', port=5000, debug=True):
        """Запуск веб-сервера"""
        print(f"🚀 Запуск веб-интерфейса на http://{host}:{port}")
        if self.is_loaded:
            total_docs = self.index_builder.vector_storage.get_document_count()
            print(f"📊 Система готова к поиску! Документов в индексе: {total_docs}")
        else:
            print("⚠️  Система не загружена! Сначала выполните построение индекса.")

        self.app.run(host=host, port=port, debug=debug)