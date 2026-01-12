from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart
from orders.models import Order
from .forms import OrderForm


def order_create(request):
    if not request.session.session_key:
        request.session.create()

    # Форма для контактных данных
    form = OrderForm()

    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    cart_items = []
    total_price = 0

    if cart.items.exists():
        cart_items = cart.items.all()
        total_price = cart.total_price
    else:
        messages.warning(request, 'Корзина пуста')

    context = {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    }

    # Если POST - создаем заказ (БЕЗ ИЗМЕНЕНИЙ)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid() and cart_items:  # Проверка на пустую корзину
            # Создаем заказ из формы
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                **form.cleaned_data
            )

            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()
                if cart:
                    for item in cart.items.all():
                        order.items.create(
                            product=item.product,
                            price=item.price,
                            quantity=item.quantity
                        )
                    cart.delete()  # Очищаем корзину

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
        # ordered=True  # раскомментируй когда будет поле ordered
    ).order_by('-created')[:10]  # последние 10 заказов

    context = {
        'orders': orders,
        'title': 'История заказов'
    }
    return render(request, 'orders/order_history.html', context)
