// products.js - Функции для работы с товарами

// Фильтрация товаров
function initProductFilters() {
    const filterForm = document.querySelector('.product-filters');
    const productsContainer = document.querySelector('.products-container');

    if (filterForm && productsContainer) {
        filterForm.addEventListener('change', function() {
            applyProductFilters();
        });

        // Обработка поля цены
        const priceInputs = filterForm.querySelectorAll('input[name="min_price"], input[name="max_price"]');
        priceInputs.forEach(input => {
            input.addEventListener('input', debounce(() => {
                applyProductFilters();
            }, 500));
        });
    }
}

// Применение фильтров
async function applyProductFilters() {
    const filterForm = document.querySelector('.product-filters');
    const productsContainer = document.querySelector('.products-container');
    const loader = document.querySelector('.filters-loader');

    if (!filterForm || !productsContainer) return;

    // Показываем лоадер
    if (loader) loader.style.display = 'block';

    const formData = new FormData(filterForm);
    const params = new URLSearchParams();

    // Собираем параметры
    for (let [key, value] of formData.entries()) {
        if (value) params.append(key, value);
    }

    try {
        const response = await fetch(`/api/products/filter/?${params}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (data.success) {
            productsContainer.innerHTML = data.html;
            updateProductCount(data.count);
            updatePagination(data.pagination);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Ошибка при фильтрации товаров', 'error');
    } finally {
        if (loader) loader.style.display = 'none';
    }
}

// Быстрый просмотр товара
function initQuickView() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.quick-view-btn')) {
            e.preventDefault();
            const productId = e.target.closest('.quick-view-btn').dataset.productId;
            showQuickView(productId);
        }
    });
}

// Показать быстрый просмотр
async function showQuickView(productId) {
    try {
        const data = await fetchWithLoader(`/api/products/${productId}/quick-view/`);

        if (data.success) {
            // Создаем модальное окно
            const modal = createQuickViewModal(data.product);
            document.body.appendChild(modal);

            // Показываем модальное окно
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();

            // Удаляем модальное окно после закрытия
            modal.addEventListener('hidden.bs.modal', function() {
                modal.remove();
            });
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Ошибка при загрузке товара', 'error');
    }
}

// Создание модального окна быстрого просмотра
function createQuickViewModal(product) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">${product.name}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-md-6">
                            <img src="${product.image}" class="img-fluid" alt="${product.name}">
                        </div>
                        <div class="col-md-6">
                            <h4 class="text-primary">${formatPrice(product.price)}</h4>
                            ${product.compare_price ? `<del class="text-muted">${formatPrice(product.compare_price)}</del>` : ''}
                            <p class="mt-3">${product.short_description}</p>
                            <div class="mb-3">
                                <label class="form-label">Количество:</label>
                                <input type="number" class="form-control" value="1" min="1" style="width: 100px;">
                            </div>
                            <button class="btn btn-primary add-to-cart" data-product-id="${product.id}">
                                <i class="fas fa-cart-plus"></i> Добавить в корзину
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    return modal;
}

// Избранное (wishlist)
function initWishlist() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.wishlist-btn')) {
            e.preventDefault();
            const button = e.target.closest('.wishlist-btn');
            toggleWishlist(button);
        }
    });
}

// Добавление/удаление из избранного
async function toggleWishlist(button) {
    const productId = button.dataset.productId;
    const isActive = button.classList.contains('active');

    try {
        const data = await fetchWithLoader('/api/wishlist/toggle/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId
            })
        });

        if (data.success) {
            button.classList.toggle('active', data.in_wishlist);
            button.innerHTML = data.in_wishlist ?
                '<i class="fas fa-heart"></i>' :
                '<i class="far fa-heart"></i>';

            showNotification(
                data.in_wishlist ? 'Добавлено в избранное ' : 'Удалено из избранного',
                'success'
            );
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Ошибка при обновлении избранного', 'error');
    }
}

// Сравнение товаров
function initCompare() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.compare-btn')) {
            e.preventDefault();
            const button = e.target.closest('.compare-btn');
            toggleCompare(button);
        }
    });
}

// Утилита для дебаунса
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}