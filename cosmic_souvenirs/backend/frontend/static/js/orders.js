// orders.js - Функции для оформления заказов

function initOrderForm() {
    const orderForm = document.querySelector('#order-form');

    if (orderForm) {
        // Валидация формы
        orderForm.addEventListener('submit', function(e) {
            if (!validateOrderForm()) {
                e.preventDefault();
            }
        });

        // Расчет стоимости доставки
        const shippingMethodSelect = document.querySelector('#id_shipping_method');
        if (shippingMethodSelect) {
            shippingMethodSelect.addEventListener('change', updateOrderSummary);
        }

        // Обновление при изменении количества
        document.addEventListener('change', '.order-item-quantity', updateOrderSummary);
    }
}

// Валидация формы заказа
function validateOrderForm() {
    const requiredFields = document.querySelectorAll('#order-form [required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    // Валидация email
    const emailField = document.querySelector('#id_email');
    if (emailField && emailField.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailField.value)) {
            emailField.classList.add('is-invalid');
            isValid = false;
        }
    }

    if (!isValid) {
        showNotification('Пожалуйста, заполните все обязательные поля', 'error');
    }

    return isValid;
}

// Обновление итоговой суммы заказа
async function updateOrderSummary() {
    const formData = new FormData(document.querySelector('#order-form'));

    try {
        const data = await fetchWithLoader('/api/order/calculate/', {
            method: 'POST',
            body: formData
        });

        if (data.success) {
            updateOrderTotals(data.totals);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Обновление отображения сумм
function updateOrderTotals(totals) {
    const elements = {
        subtotal: document.querySelector('.order-subtotal'),
        shipping: document.querySelector('.order-shipping'),
        tax: document.querySelector('.order-tax'),
        total: document.querySelector('.order-total')
    };

    for (const [key, element] of Object.entries(elements)) {
        if (element && totals[key] !== undefined) {
            element.textContent = formatPrice(totals[key]);
        }
    }
}
