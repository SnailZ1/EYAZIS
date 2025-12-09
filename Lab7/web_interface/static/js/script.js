// web_interface/static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const queryInput = document.getElementById('query');
    const loadingElement = document.getElementById('loading');
    const resultsSection = document.getElementById('results-section');
    const resultsContainer = document.getElementById('results-container'); // Используем правильный ID
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

        // Создаем FormData для отправки
        const formData = new FormData();
        formData.append('query', query);
        formData.append('top_k', top_k);

        // Отправляем запрос на сервер
        fetch('/search', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка сервера: ' + response.status);
            }
            return response.json();
        })
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
            console.error('Ошибка поиска:', error);
        });
    }

    function displayResults(data) {
        // Показываем расширение запроса
        if (data.expansion_result && data.expansion_result.similar_terms && Object.keys(data.expansion_result.similar_terms).length > 0) {
            displayExpansionInfo(data.expansion_result);
        } else {
            hideExpansionInfo();
        }
        
        // Показываем результаты
        displaySearchResults(data);
        
        // Показываем статистику
        if (data.selection_stats) {
            displaySelectionStats(data.selection_stats);
        } else {
            hideSelectionStats();
        }
        
        showResults();
    }

    function displayExpansionInfo(expansion) {
        const expansionDiv = document.getElementById('expansionInfo');
        const contentDiv = document.getElementById('expansionContent');
        
        if (!expansionDiv || !contentDiv) {
            console.error('Элементы расширения не найдены');
            return;
        }
        
        let html = '<div class="mb-3">';
        html += '<strong>Оригинальные термины:</strong> ';
        expansion.original_terms.forEach(term => {
            html += `<span class="term-badge term-original">${term}</span> `;
        });
        html += '</div>';
        
        if (Object.keys(expansion.similar_terms).length > 0) {
            html += '<div><strong>Расширенные термины:</strong><br>';
            for (const [original, similarList] of Object.entries(expansion.similar_terms)) {
                html += `<div class="mt-1">`;
                html += `<span class="term-badge term-original">${original}</span> → `;
                similarList.forEach(([similar, score]) => {
                    html += `<span class="term-badge term-expanded">${similar} <span class="similarity-score">(${score.toFixed(2)})</span></span> `;
                });
                html += `</div>`;
            }
            html += '</div>';
            
            html += `<div class="mt-2"><small class="text-muted">`;
            html += `Примечание: зеленым цветом подсвечены оригинальные термины запроса,<br>`;
            html += `а голубым цветом подсвечены семантически похожие термины, найденные в документах`;
            html += `</small></div>`;
        }
        
        contentDiv.innerHTML = html;
        expansionDiv.style.display = 'block';
    }

    function hideExpansionInfo() {
        const expansionDiv = document.getElementById('expansionInfo');
        if (expansionDiv) {
            expansionDiv.style.display = 'none';
        }
    }

    function displaySearchResults(data) {
        if (!resultsContainer) {
            console.error('Контейнер результатов не найден');
            return;
        }
        
        if (!data.results || data.results.length === 0) {
            resultsContainer.innerHTML = `
                <div class="no-results">
                    <p>К сожалению по вашему запросу ничего не найдено.</p>
                    <p>Попробуйте изменить запрос или использовать другие ключевые слова.</p>
                </div>
            `;
            return;
        }
        
        let html = `
            <div class="search-info">
                <p>Запрос: "<strong>${escapeHtml(data.query)}</strong>"</p>
                <p>Найдено документов: <strong>${data.total_found}</strong></p>
            </div>
            <div class="results-list">
        `;

        data.results.forEach(result => {
            // Используем сниппет с семантической подсветкой если есть
            const snippet = result.semantic_info && result.semantic_info.highlighted_snippet 
                ? result.semantic_info.highlighted_snippet 
                : (result.snippet || 'Нет текста для отображения');
            
            

            html += `
                <div class="result-item">
                    <div class="result-header">
                        <h3 class="result-title">
                            Название документа: ${escapeHtml(result.metadata.title || 'Без названия')}
                            <span class="file-type">(${escapeHtml(result.metadata.file_type || 'Неизвестно')})</span>
                        </h3>
                        <div class="relevance-badge">
                            Релевантность: ${(result.enhancement_info.combined_score * 100).toFixed(1)}%
                        </div>
                    </div>

                    <div class="result-meta">
                        <span class="doc-id">ID: ${result.doc_id}</span>
                        <span class="date">Создан: ${escapeHtml(result.metadata.date_created || 'Неизвестно')}</span>
                        <span class="file-path">Путь: ${escapeHtml(result.metadata.file_path || 'Неизвестно')}</span>
                    </div>

                    <div class="result-snippet">
                        ${snippet}
                    </div>

                    ${result.query_terms_in_doc && result.query_terms_in_doc.length > 0 ? `
                    <div class="query-terms">
                        <strong>Найденные термины:</strong>
                        ${result.query_terms_in_doc.map(term => 
                            `<span class="term-tag">${escapeHtml(term)}</span>`
                        ).join('')}
                    </div>
                    ` : ''}
                    
                    ${result.semantic_info ? `
                    <div class="query-terms mt-2">
                        <strong>Семантический анализ:</strong>
                        <span class="term-tag" style="background: #17a2b8; color: white;">
                            Семантическая релевантность: ${(result.semantic_info.semantic_score * 100).toFixed(1)}%
                        </span>
                    </div>
                    ` : ''}
                </div>
            `;
        });
        
        html += '</div>';
        resultsContainer.innerHTML = html;
    }

    function displaySelectionStats(stats) {
        const statsDiv = document.getElementById('selectionStats');
        const contentDiv = document.getElementById('statsContent');
        
        if (!statsDiv || !contentDiv) {
            console.error('Элементы статистики не найдены');
            return;
        }
        
        let statsHTML = '<div class="stats-grid">';
        
        if (stats.pre_selection && !stats.pre_selection.skipped) {
            const efficiency = stats.pre_selection.initial_documents > 0 
                ? ((stats.pre_selection.after_filtering / stats.pre_selection.initial_documents) * 100).toFixed(1)
                : 0;
            statsHTML += `
                <div class="stat-item">
                    <strong>Предварительный отбор</strong><br>
                    <small>${stats.pre_selection.initial_documents} → ${stats.pre_selection.after_filtering} документов</small><br>
                    <small>Эффективность: ${efficiency}%</small>
                </div>
            `;
        }
        
        if (stats.ranking_enhancement && !stats.ranking_enhancement.skipped) {
            statsHTML += `
                <div class="stat-item">
                    <strong>Улучшение ранжирования</strong><br>
                    <small>${stats.ranking_enhancement.enhanced_results} документов</small><br>
                    <small>Улучшение: ${(stats.ranking_enhancement.average_enhancement * 100).toFixed(1)}%</small>
                </div>
            `;
        }
        
        if (stats.semantic_enhancement && !stats.semantic_enhancement.skipped) {
            statsHTML += `
                <div class="stat-item">
                    <strong>Семантический поиск</strong><br>
                    <small>Расширение: ${stats.semantic_enhancement.query_expansion_ratio.toFixed(1)}x</small><br>
                    <small>Скор: ${(stats.semantic_enhancement.avg_semantic_score * 100).toFixed(1)}%</small>
                </div>
            `;
        }
        
        statsHTML += '</div>';
        contentDiv.innerHTML = statsHTML;
        statsDiv.style.display = 'block';
    }

    function hideSelectionStats() {
        const statsDiv = document.getElementById('selectionStats');
        if (statsDiv) {
            statsDiv.style.display = 'none';
        }
    }

    function showLoading() {
        if (loadingElement) {
            loadingElement.classList.remove('hidden');
        }
    }

    function hideLoading() {
        if (loadingElement) {
            loadingElement.classList.add('hidden');
        }
    }

    function showResults() {
        if (resultsSection) {
            resultsSection.classList.remove('hidden');
        }
    }

    function hideResults() {
        if (resultsSection) {
            resultsSection.classList.add('hidden');
        }
    }

    function showError(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.classList.remove('hidden');
        }
    }

    function hideError() {
        if (errorMessage) {
            errorMessage.classList.add('hidden');
        }
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