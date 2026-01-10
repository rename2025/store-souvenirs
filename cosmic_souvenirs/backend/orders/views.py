from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from cart.models import Cart
from orders.models import Order
from .forms import OrderForm


def order_create(request):
    if not request.session.session_key:
        request.session.save()

    # Форма для контактных данных
    form = OrderForm()

    # Корзина
    context = {
        'form': form,
        'cart_items': [],
        'total_price': 0
    }

    session_key = request.session.session_key
    if session_key:
        try:
            cart = Cart.objects.get(session_key=session_key)
            context['cart_items'] = cart.items.all()
            context['total_price'] = cart.total_price
        except Cart.DoesNotExist:
            pass

    # Если POST - создаем заказ
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Создаем заказ из формы
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                **form.cleaned_data
            )

            # Копируем товары из корзины в заказ
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

            return redirect('order_history')

    return render(request, 'orders/create.html', context)


@login_required  # Только для авторизованных пользователей
def order_history(request):
    """Показывает историю заказов пользователя"""
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')  # Новые заказы сверху

    context = {
        'orders': orders
    }
    return render(request, 'orders/history.html', context)

#from django.shortcuts import render
#def order_create(request):
    #return render(request, 'orders/create.html')

#def order_created(request, order_id):
    #return render(request, 'orders/created.html')

#def order_history(request):
    #return render(request, 'orders/history.html')

