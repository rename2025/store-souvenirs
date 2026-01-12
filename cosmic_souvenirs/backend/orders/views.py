from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from .forms import OrderForm
from cart.views import _get_cart


def order_create(request):
    # ЧИТАЕМ КОРЗИНУ ИЗ СЕССИИ (как в cart/views.py)
    cart = _get_cart(request)

    # Формируем cart_items ТОЧНО как в cart_detail
    cart_items = []
    total_price = 0

    for product_id_str, quantity in cart.items():
        try:
            product_id = int(product_id_str)
            from products.models import Product  # импортируем здесь
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.price * quantity
            total_price += item_total

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
        except (ValueError, Product.DoesNotExist):
            continue

    # Если корзина пуста
    if not cart_items:
        messages.warning(request, 'Корзина пуста')

    form = OrderForm()
    context = {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    }

    # POST - создаем заказ ИЗ СЕССИИ (исправлено!)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid() and cart_items:  # проверяем cart_items из сессии
            session_key = request.session.session_key

            # Создаем заказ
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                **form.cleaned_data
            )

            # Копируем товары ИЗ СЕССИИ в заказ
            for product_id_str, quantity in cart.items():
                try:
                    product_id = int(product_id_str)
                    product = Product.objects.get(id=product_id, is_active=True)
                    order.items.create(
                        product=product,
                        price=product.price,
                        quantity=quantity
                    )
                except (ValueError, Product.DoesNotExist):
                    continue

            # Очищаем корзину в сессии
            request.session['cart'] = {}
            request.session.modified = True

            messages.success(request, 'Заказ успешно создан!')
            return redirect('order_history')
        else:
            messages.error(request, 'Ошибка в форме или корзина пуста')

    return render(request, 'orders/create.html', context)


@login_required
def order_history(request):
    """История заказов авторизованного пользователя"""
    orders = Order.objects.filter(
        user=request.user,
    ).order_by('-created')[:10]

    context = {
        'orders': orders,
        'title': 'История заказов'
    }
    return render(request, 'orders/order_history.html', context)
