// web_interface/static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const queryInput = document.getElementById('query');
    const loadingElement = document.getElementById('loading');
    const resultsSection = document.getElementById('results-section');
    const resultsContainer = document.getElementById('results-container');
    const errorMessage = document.getElementById('error-message');

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const query = queryInput.value.trim();
        const top_k = document.getElementById('top_k').value;

        if (!query) {
            showError('Пожалуйста, введите поисковый запрос');
            return;
        }

        performSearch(query, top_k);
    });

    function performSearch(query, top_k) {
        // Показываем индикатор загрузки
        showLoading();
        hideResults();
        hideError();

        // Отправляем запрос на сервер
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `query=${encodeURIComponent(query)}&top_k=${top_k}`
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();

            if (data.error) {
                showError(data.error);
            } else {
                displayResults(data);
            }
        })
        .catch(error => {
            hideLoading();
            showError('Ошибка сети: ' + error.message);
        });
    }

    function displayResults(data) {
        // Создаем HTML для результатов
        let html = `
            <div class="search-info">
                <p>Запрос: "<strong>${escapeHtml(data.query)}</strong>"</p>
                <p>Найдено документов: <strong>${data.total_found}</strong></p>
            </div>
        `;

        if (data.results && data.results.length > 0) {
            html += '<div class="results-list">';

            data.results.forEach(result => {
                html += `
                    <div class="result-item">
                        <div class="result-header">
                            <h3 class="result-title">
                                📄 ${escapeHtml(result.title)}
                                <span class="file-type">(${result.file_type})</span>
                            </h3>
                            <div class="relevance-badge">
                                Релевантность: ${result.relevance}%
                            </div>
                        </div>

                        <div class="result-meta">
                            <span class="doc-id">ID: ${result.doc_id}</span>
                            <span class="date">Создан: ${result.date_created}</span>
                            <span class="file-path">Путь: ${escapeHtml(result.file_path)}</span>
                        </div>

                        <div class="result-snippet">
                            ${result.snippet}
                        </div>

                        ${result.query_terms_in_doc && result.query_terms_in_doc.length > 0 ? `
                            <div class="query-terms">
                                <strong>Найденные термины:</strong>
                                ${result.query_terms_in_doc.map(term =>
                                    `<span class="term-tag">${escapeHtml(term)}</span>`
                                ).join('')}
                            </div>
                        ` : ''}
                    </div>
                `;
            });

            html += '</div>';
        } else {
            html += `
                <div class="no-results">
                    <p>😕 По вашему запросу ничего не найдено.</p>
                    <p>Попробуйте изменить запрос или использовать другие ключевые слова.</p>
                </div>
            `;
        }

        resultsContainer.innerHTML = html;
        showResults();
    }

    function showLoading() {
        loadingElement.classList.remove('hidden');
    }

    function hideLoading() {
        loadingElement.classList.add('hidden');
    }

    function showResults() {
        resultsSection.classList.remove('hidden');
    }

    function hideResults() {
        resultsSection.classList.add('hidden');
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }

    function escapeHtml(unsafe) {
        if (unsafe === null || unsafe === undefined) return '';
        return unsafe
            .toString()
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Фокус на поле ввода при загрузке
    if (queryInput && !queryInput.disabled) {
        queryInput.focus();
    }
});