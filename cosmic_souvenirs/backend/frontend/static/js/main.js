// main.js - Основные функции сайта

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initCartFunctionality();
    initProductGallery();
    initSearchAutocomplete();
    initMobileMenu();
    initNotifications();
    initAjaxForms();
});

// ==================== КОРЗИНА ====================

function initCartFunctionality() {
    // Добавление в корзину
    document.addEventListener('click', function(e) {
        if (e.target.closest('.add-to-cart') || e.target.classList.contains('add-to-cart')) {
            e.preventDefault();
            const button = e.target.closest('.add-to-cart') || e.target;
            addToCart(button);
        }
    });

    // Обновление количества в корзине
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('cart-quantity')) {
            updateCartItem(e.target);
        }
    });

    // Удаление из корзины
    document.addEventListener('click', function(e) {
        if (e.target.closest('.remove-from-cart')) {
            e.preventDefault();
            removeFromCart(e.target.closest('.remove-from-cart'));
        }
    });
}

// ==================== УВЕДОМЛЕНИЯ ====================

function initNotifications() {
    // Автоматическое скрытие alert через 5 секунд
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}

// ==================== МОБИЛЬНОЕ МЕНЮ ====================

function initMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mainNav = document.querySelector('.main-navigation');

    if (mobileMenuToggle && mainNav) {
        mobileMenuToggle.addEventListener('click', function() {
            mainNav.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
}

// ==================== ПОИСК ====================

function initSearchAutocomplete() {
    const searchInput = document.querySelector('.search-input');
    const searchResults = document.querySelector('.search-results');

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
                fetchSearchResults(query);
            }, 300);
        });

        // Скрытие результатов при клике вне области
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-container')) {
                searchResults.style.display = 'none';
            }
        });
    }
}

// ==================== ГАЛЕРЕЯ ТОВАРОВ ====================

function initProductGallery() {
    const mainImage = document.querySelector('.product-main-image');
    const thumbnails = document.querySelectorAll('.product-thumbnail');

    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                // Обновляем главное изображение
                mainImage.src = this.dataset.image || this.src;
                mainImage.alt = this.alt;

                // Обновляем активный thumbnail
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }
}

// ==================== AJAX ФОРМЫ ====================

function initAjaxForms() {
    const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');

    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitAjaxForm(this);
        });
    });
}

// ==================== УТИЛИТЫ ====================

// Показ уведомлений
function showNotification(message, type = 'success', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-alert`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1060;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;

    document.body.appendChild(notification);

    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }

    return notification;
}

// Получение CSRF токена
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];

    return cookieValue || '';
}

// Форматирование цены
function formatPrice(price) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
    }).format(price);
}

// Загрузка данных с индикатором
async function fetchWithLoader(url, options = {}) {
    showLoader();
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken(),
                ...options.headers
            }
        });
        return await response.json();
    } finally {
        hideLoader();
    }
}

// Показать/скрыть лоадер
function showLoader() {
    let loader = document.querySelector('.global-loader');
    if (!loader) {
        loader = document.createElement('div');
        loader.className = 'global-loader';
        loader.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Загрузка...</span>
            </div>
        `;
        loader.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 9999;
        `;
        document.body.appendChild(loader);
    }
}

function hideLoader() {
    const loader = document.querySelector('.global-loader');
    if (loader) {
        loader.remove();
    }
}