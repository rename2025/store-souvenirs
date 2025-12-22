// cart.js - Функции для работы с корзиной

// Добавление товара в корзину
async function addToCart(button) {
    const productId = button.dataset.productId;
    const quantityInput = document.getElementById(`quantity-${productId}`);
    const quantity = quantityInput ? parseInt(quantityInput.value) : 1;

    // Блокируем кнопку на время запроса
    const originalText = button.innerHTML;
    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
    button.disabled = true;

    try {
        const data = await fetchWithLoader('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        });

        if (data.success) {
            updateCartBadge(data.cart_items_count);
            showNotification('Товар добавлен в корзину! 🛒', 'success');

            // Обновляем мини-корзину если есть
            updateMiniCart(data);
        } else {
            showNotification(data.error || 'Ошибка при добавлении товара', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Произошла ошибка при добавлении товара', 'error');
    } finally {
        // Восстанавливаем кнопку
        button.innerHTML = originalText;
        button.disabled = false;
    }
}

// Обновление количества товара в корзине
async function updateCartItem(input) {
    const itemId = input.dataset.itemId;
    const quantity = parseInt(input.value);

    if (quantity < 1) {
        removeFromCartByItemId(itemId);
        return;
    }

    try {
        const data = await fetchWithLoader(`/cart/update/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                quantity: quantity
            })
        });

        if (data.success) {
            // Обновляем сумму для конкретного товара
            const itemTotalElement = document.querySelector(`[data-item-total="${itemId}"]`);
            if (itemTotalElement) {
                itemTotalElement.textContent = formatPrice(data.item_total);
            }

            // Обновляем общую сумму
            const cartTotalElement = document.querySelector('.cart-total-price');
            if (cartTotalElement) {
                cartTotalElement.textContent = formatPrice(data.total_price);
            }

            updateCartBadge(data.cart_items_count);
        } else {
            showNotification(data.error || 'Ошибка при обновлении', 'error');
            // Восстанавливаем предыдущее значение
            input.value = input.dataset.oldValue;
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Ошибка при обновлении корзины', 'error');
        input.value = input.dataset.oldValue;
    }
}

// Удаление товара из корзины
async function removeFromCart(button) {
    const itemId = button.dataset.itemId;

    if (!confirm('Удалить товар из корзины?')) {
        return;
    }

    try {
        const data = await fetchWithLoader(`/cart/remove/${itemId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (data.success) {
            // Удаляем строку из таблицы
            const row = document.querySelector(`[data-cart-item="${itemId}"]`);
            if (row) {
                row.style.opacity = '0';
                setTimeout(() => row.remove(), 300);
            }

            // Обновляем общую сумму
            const cartTotalElement = document.querySelector('.cart-total-price');
            if (cartTotalElement) {
                cartTotalElement.textContent = formatPrice(data.total_price);
            }

            updateCartBadge(data.cart_items_count);
            showNotification('Товар удален из корзины', 'success');

            // Если корзина пуста, покажем сообщение
            if (data.cart_items_count === 0) {
                showEmptyCartMessage();
            }
        } else {
            showNotification(data.error || 'Ошибка при удалении', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Ошибка при удалении товара', 'error');
    }
}

// Удаление по ID товара
async function removeFromCartByItemId(itemId) {
    const button = document.querySelector(`[data-item-id="${itemId}"]`);
    if (button) {
        removeFromCart(button);
    }
}

// Обновление бейджа корзины
function updateCartBadge(count) {
    const badges = document.querySelectorAll('.cart-badge');
    badges.forEach(badge => {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    });
}

// Обновление мини-корзины
function updateMiniCart(data) {
    const miniCart = document.querySelector('.mini-cart');
    if (miniCart && data.cart_items) {
        // Здесь можно обновить содержимое мини-корзины
        // Например, через AJAX запрос за полными данными
    }
}

// Показать сообщение о пустой корзине
function showEmptyCartMessage() {
    const cartContainer = document.querySelector('.cart-container');
    if (cartContainer) {
        cartContainer.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-shopping-cart fa-4x text-muted mb-3"></i>
                <h3>Корзина пуста</h3>
                <p class="text-muted">Добавьте товары из каталога</p>
                <a href="/catalog/" class="btn btn-primary">В каталог</a>
            </div>
        `;
    }
}

// Быстрое добавление в корзину (без выбора количества)
function quickAddToCart(productId) {
    const button = document.querySelector(`[data-product-id="${productId}"]`);
    if (button) {
        addToCart(button);
    }
}

// Очистка всей корзины
async function clearCart() {
    if (!confirm('Очистить всю корзину?')) {
        return;
    }

    try {
        const data = await fetchWithLoader('/cart/clear/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (data.success) {
            updateCartBadge(0);
            showEmptyCartMessage();
            showNotification('Корзина очищена', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Ошибка при очистке корзины', 'error');
    }
}