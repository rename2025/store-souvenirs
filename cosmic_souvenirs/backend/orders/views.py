from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from orders.models import Order, OrderItem
from .forms import OrderForm
from cart.views import _get_cart
from products.models import Product  # импортируем заранее


def order_create(request):
    # ЧИТАЕМ КОРЗИНУ ИЗ СЕССИИ (как в cart/views.py)
    cart = _get_cart(request)

    # Формируем cart_items ТОЧНО как в cart_detail
    cart_items = []
    total_price = Decimal('0.00')

    for product_id_str, quantity in cart.items():
        try:
            product_id = int(product_id_str)
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
        return render(request, 'orders/create.html', {
            'cart_items': [],
            'total_price': 0
        })

    form = OrderForm()
    context = {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price
    }

    # POST - создаем заказ ИЗ СЕССИИ (ИСПРАВЛЕНО!)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid() and cart_items:
            session_key = request.session.session_key

            # ✅ ИСПРАВЛЕНО: используем ПРАВИЛЬНЫЕ имена полей модели Order!
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                customer_first_name=form.cleaned_data['customer_first_name'],
                customer_last_name=form.cleaned_data['customer_last_name'],
                customer_email=form.cleaned_data['customer_email'],
                customer_phone=form.cleaned_data['customer_phone'],
                payment_method=form.cleaned_data.get('payment_method', 'card'),
                customer_notes=form.cleaned_data.get('customer_notes', ''),
                # Данные из формы адреса (добавьте в OrderForm!)
                shipping_address={
                    'city': form.cleaned_data.get('city', ''),
                    'street': form.cleaned_data.get('street', ''),
                    'house': form.cleaned_data.get('house', ''),
                    'apartment': form.cleaned_data.get('apartment', ''),
                    'index': form.cleaned_data.get('index', ''),
                },
                # Суммы из корзины (НЕ из формы!)
                total_amount=total_price,
                tax_amount=Decimal('0.00'),  # или рассчитайте
                shipping_cost=Decimal('0.00'),  # или рассчитайте
                status='pending',
                payment_status='pending'
            )

            # ✅ ИСПРАВЛЕНО: используем модель OrderItem с ПРАВИЛЬНЫМИ полями!
            for product_id_str, quantity in cart.items():
                try:
                    product_id = int(product_id_str)
                    product = Product.objects.get(id=product_id, is_active=True)

                    # ПРАВИЛЬНЫЕ поля OrderItem модели!
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,  # сохраняем название
                        product_sku=getattr(product, 'sku', ''),  # если есть SKU
                        unit_price=product.price,  # unit_price вместо price!
                        quantity=quantity
                    )
                except (ValueError, Product.DoesNotExist):
                    continue

            # Очищаем корзину в сессии
            if 'cart' in request.session:
                del request.session['cart']
            request.session.modified = True

            messages.success(request, f'Заказ #{order.order_number} успешно создан!')
            return redirect('orders:order_history')

        else:
            messages.error(request, 'Проверьте правильность заполнения формы')
            context['form'] = form

    return render(request, 'orders/create.html', context)


@login_required
def order_history(request):
    """История заказов авторизованного пользователя"""
    orders = Order.objects.filter(
        user=request.user,
    ).order_by('-created_at')[:10]  # исправлено created → created_at

    context = {
        'orders': orders,
        'title': 'История заказов'
    }
    return render(request, 'orders/order_history.html', context)
