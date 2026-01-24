# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product
from orders.models import Order
from django.views.decorators.csrf import csrf_exempt
import json

def _get_cart(request):
    """Получает корзину из сессии"""
    cart = request.session.get('cart', {})
    return cart


def _save_cart(request, cart):
    """Сохраняет корзину в сессию"""
    request.session['cart'] = cart
    request.session.modified = True


def cart_detail(request):
    """Детальная страница корзины"""
    cart = _get_cart(request)

    # Получаем товары из корзины
    cart_items = []
    total_price = 0

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

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart_items_count': len(cart_items)
    }

    return render(request, 'cart/detail.html', context)


def cart_add(request, product_id=None):
    """Добавляет товар в корзину"""
    if product_id is None:
        # Для AJAX запросов
        product_id = request.POST.get('product_id') or request.GET.get('product_id')

    if not product_id:
        return redirect('cart:cart')

    try:
        product = Product.objects.get(id=int(product_id), is_active=True)
    except (ValueError, Product.DoesNotExist):
        return redirect('cart:cart')

    cart = _get_cart(request)
    product_id_str = str(product_id)

    # Увеличиваем количество
    cart[product_id_str] = cart.get(product_id_str, 0) + 1
    _save_cart(request, cart)

    # Если это AJAX запрос
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_items_count': sum(cart.values()),
            'message': f'Товар "{product.name}" добавлен в корзину'
        })

    return redirect('cart:cart')


def cart_remove(request, product_id):
    """Удаляет товар из корзины"""
    cart = _get_cart(request)
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        _save_cart(request, cart)

    return redirect('cart:cart')


def add_to_cart(request):
    """Для AJAX запросов из JavaScript (альтернатива)"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity', 1)
        try:
            quantity = int(quantity)
        except ValueError:
            quantity = 1

    if product_id:
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        # Увеличиваем количество
        current_quantity = cart.get(product_id_str, 0)
        cart[product_id_str] = current_quantity + quantity

        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'cart_items_count': sum(cart.values())
        })

    return JsonResponse({'success': False}, status=400)

@csrf_exempt
@require_POST
def apply_promo(request):
    """AJAX: применить промокод к корзине"""
    try:
        data = json.loads(request.body)
        promo_code = data.get('promo_code', '').strip().upper()

        if not promo_code:
            return JsonResponse({'success': False, 'message': 'Промокод не указан'})

        # Получаем общую сумму корзины
        cart = _get_cart(request)
        total_amount = 0

        for product_id_str, quantity in cart.items():
            try:
                product_id = int(product_id_str)
                product = Product.objects.get(id=product_id, is_active=True)
                total_amount += product.price * quantity
            except (ValueError, Product.DoesNotExist):
                continue

        if total_amount == 0:
            return JsonResponse({'success': False, 'message': 'Корзина пуста'})

        # Создаем временный заказ для расчета скидки
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        temp_order = Order(
            total_amount=total_amount,
            session_key=session_key,
            customer_email='promo@test.com'  # заглушка
        )

        # Применяем промокод
        success, message = temp_order.apply_promo_code(promo_code)

        return JsonResponse({
            'success': success,
            'message': message,
            'discount_amount': f'{temp_order.discount_amount:.2f}',
            'final_total': f'{temp_order.final_total:.2f}'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Ошибка: {str(e)}'}, status=500)


def checkout(request):
    """Оформление заказа"""
    cart = _get_cart(request)
    cart_items = []
    total = 0

    for product_id_str, quantity in cart.items():
        try:
            product_id = int(product_id_str)
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.price * quantity
            total += item_total

            cart_items.append({
                'name': product.name,
                'price': product.price,
                'quantity': quantity,
                'total': item_total
            })
        except (ValueError, Product.DoesNotExist):
            continue

    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_items_count': len(cart_items)
    }

    return render(request, 'cart/checkout.html', context)

