// search.js - Функции поиска

let searchController = null;

async function fetchSearchResults(query) {
    // Отменяем предыдущий запрос
    if (searchController) {
        searchController.abort();
    }

    searchController = new AbortController();

    try {
        const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`, {
            signal: searchController.signal,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();
        displaySearchResults(data.results, query);
    } catch (error) {
        if (error.name !== 'AbortError') {
            console.error('Search error:', error);
        }
    }
}

function displaySearchResults(results, query) {
    const searchResults = document.querySelector('.search-results');
    if (!searchResults) return;

    if (results.length === 0) {
        searchResults.innerHTML = `
            <div class="search-no-results">
                <p>По запросу "${query}" ничего не найдено</p>
            </div>
        `;
    } else {
        searchResults.innerHTML = results.map(product => `
            <div class="search-result-item" data-product-id="${product.id}">
                <div class="row align-items-center">
                    <div class="col-3">
                        <img src="${product.image}" alt="${product.name}" class="img-fluid">
                    </div>
                    <div class="col-7">
                        <h6 class="mb-1">${product.name}</h6>
                        <p class="text-muted small mb-0">${product.short_description}</p>
                        <div class="price">${formatPrice(product.price)}</div>
                    </div>
                    <div class="col-2">
                        <button class="btn btn-sm btn-primary add-to-cart"
                                data-product-id="${product.id}"
                                title="Добавить в корзину">
                            <i class="fas fa-cart-plus"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    searchResults.style.display = 'block';
}

// Инициализация живого поиска
function initLiveSearch() {
    const searchInput = document.querySelector('.live-search-input');
    const searchResults = document.querySelector('.live-search-results');

    if (searchInput && searchResults) {
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length < 2) {
                searchResults.style.display = 'none';
                return;
            }

            searchTimeout = setTimeout(() => {
                fetchLiveSearchResults(query, searchResults);
            }, 300);
        });

        // Закрытие результатов при клике вне
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.live-search-container')) {
                searchResults.style.display = 'none';
            }
        });
    }
}