# web_interface/app.py
from flask import Flask, render_template, request, jsonify
import sys
import os

# Добавляем пути к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from indexing.index_builder import IndexBuilder
from text_preprocessing.preprocessor_factory import PreprocessorFactory
from vector_storage.chroma_storage import ChromaStorage


class SearchApp:
    """Класс для управления поисковым приложением"""

    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'search-system-secret-key'
        self.index_builder = None
        self.preprocessor = None
        self.is_loaded = False

        self.setup_routes()
        self.load_search_system()

    def load_search_system(self):
        """Загрузка поисковой системы"""
        try:
            print("Загрузка поисковой системы...")

            # Создаем препроцессор
            self.preprocessor = PreprocessorFactory.create_lemmatization_preprocessor()

            # Загружаем индекс
            self.index_builder = IndexBuilder(use_vector_db=True)

            # Пытаемся загрузить существующий индекс
            try:
                self.index_builder.vocabulary.load_vocabulary("search_index/vocabulary.json")
                self.index_builder.vector_storage = ChromaStorage()
                self.index_builder.tfidf_calculator = None  # Сбрасываем
                from indexing.tfidf_calculator import TFIDFCalculator
                self.index_builder.tfidf_calculator = TFIDFCalculator(self.index_builder.vocabulary)
                self.is_loaded = True
                print("✅ Поисковая система успешно загружена")
            except Exception as e:
                print(f"❌ Не удалось загрузить индекс: {e}")
                self.is_loaded = False

        except Exception as e:
            print(f"❌ Ошибка инициализации: {e}")
            self.is_loaded = False

    def setup_routes(self):
        """Настройка маршрутов Flask"""

        @self.app.route('/')
        def index():
            """Главная страница с поиском"""
            total_docs = 0
            if self.index_builder and self.index_builder.vector_storage:
                total_docs = self.index_builder.vector_storage.get_document_count()

            return render_template('index.html',
                                   system_loaded=self.is_loaded,
                                   total_documents=total_docs)

        @self.app.route('/search', methods=['POST'])
        def search():
            """Обработка поискового запроса"""
            if not self.is_loaded:
                return jsonify({'error': 'Поисковая система не загружена'}), 500

            try:
                # Получаем запрос из формы
                query = request.form.get('query', '').strip()
                top_k = int(request.form.get('top_k', 10))
                show_analysis = request.form.get('show_analysis', 'false') == 'true'

                if not query:
                    return jsonify({'error': 'Пустой запрос'}), 400

                print(f"Поиск запроса: '{query}'")

                # Выполняем поиск
                results = self.index_builder.search(query, self.preprocessor, top_k=top_k)

                # Анализ запроса (если нужно)
                query_analysis = None
                if show_analysis:
                    query_analysis = self.index_builder.analyze_query(query, self.preprocessor)

                # Форматируем результаты для отображения
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        'doc_id': result['metadata']['doc_id'],
                        'title': result['metadata']['title'],
                        'snippet': self._generate_snippet(result['snippet'], query),
                        'relevance': round(result['similarity_score'] * 100, 1),
                        'file_type': result['metadata']['file_type'],
                        'date_created': result['metadata']['date_created'],
                        'file_path': result['metadata']['file_path'],
                        'query_terms_in_doc': self._find_query_terms(query, result['snippet'])
                    })

                response_data = {
                    'query': query,
                    'total_found': len(results),
                    'results': formatted_results
                }

                if query_analysis:
                    response_data['query_analysis'] = query_analysis

                return jsonify(response_data)

            except Exception as e:
                print(f"Ошибка поиска: {e}")
                return jsonify({'error': f'Ошибка поиска: {str(e)}'}), 500

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
                return jsonify(analysis)

            except Exception as e:
                return jsonify({'error': f'Ошибка анализа: {str(e)}'}), 500

        @self.app.route('/stats')
        def stats():
            """Статистика системы"""
            if not self.is_loaded:
                return jsonify({'error': 'Система не загружена'}), 500

            stats = self.index_builder.get_index_statistics()
            return jsonify(stats)

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