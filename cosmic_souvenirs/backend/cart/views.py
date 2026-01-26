from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from products.models import Product, PromoCode
from orders.models import Order
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
        product_id = request.POST.get('product_id') or request.GET.get('product_id')

    if not product_id:
        return redirect('cart:cart')

    try:
        product = Product.objects.get(id=int(product_id), is_active=True)
    except (ValueError, Product.DoesNotExist):
        return redirect('cart:cart')

    cart = _get_cart(request)
    product_id_str = str(product_id)
    cart[product_id_str] = cart.get(product_id_str, 0) + 1
    _save_cart(request, cart)

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
    """Для AJAX запросов из JavaScript"""
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

    try:
        data = json.loads(request.body)
        promo_code = data.get('promo_code', '').strip().upper()

        if not promo_code:
            return JsonResponse({'success': False, 'message': 'Промокод не указан'})

        # Вычисляем сумму корзины
        cart = _get_cart(request)
        total_amount = 0

        for product_id_str, quantity in cart.items():
            try:
                product = Product.objects.get(id=int(product_id_str), is_active=True)
                total_amount += product.price * quantity
            except (ValueError, Product.DoesNotExist):
                continue

        if total_amount == 0:
            return JsonResponse({'success': False, 'message': 'Корзина пуста'})


        promo = PromoCode.objects.filter(code=promo_code, is_active=True).first()

        if not promo:
            return JsonResponse({'success': False, 'message': 'Промокод не найден или неактивен'})

        # Расчет скидки
        discount = 0
        if promo.discount_type == 'percent':
            discount = total_amount * (promo.discount_value / 100)
        else:  # fixed
            discount = min(promo.discount_value, total_amount * 0.9)  # Макс 90%

        final_total = total_amount - discount

        # Сохраняем в сессию для checkout
        request.session['promo_code'] = promo_code
        request.session['promo_discount'] = float(discount)
        request.session['promo_final_total'] = float(final_total)
        request.session.modified = True

        return JsonResponse({
            'success': True,
            'message': f'Промокод "{promo_code}" применен!',
            'discount_amount': f'{discount:.2f}',
            'final_total': f'{final_total:.2f}'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Ошибка: {str(e)}'}, status=500)


@login_required
def checkout(request):
    """Оформление заказа """
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

    if request.method == 'POST':

        order = Order.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            address=request.POST['address'],
            total_amount=total,
            session_key=request.session.session_key
        )

         # ПОСЛЕ СОЗДАНИЯ ORDER - ПРИМЕНЯЕМ ПРОМОКОД
        promo_code = request.session.get('promo_code')
        if promo_code:
            success, message = order.apply_promo_code(promo_code)
            # Сохраняем сообщение
            request.session['order_message'] = message

        # Очищаем корзину и промокод
        request.session['cart'] = {}
        request.session['promo_code'] = None
        request.session.modified = True

        # Перенаправляем на страницу заказа
        return redirect('orders:order_detail', order_id=order.id)

    # GET - показываем форму
    discount = request.session.get('promo_discount', 0)
    final_total = request.session.get('promo_final_total', total)

    context = {
        'cart_items': cart_items,
        'total': total,
        'discount': discount,
        'final_total': final_total,
        'cart_items_count': len(cart_items)
    }
    return render(request, 'cart/checkout.html', context)
