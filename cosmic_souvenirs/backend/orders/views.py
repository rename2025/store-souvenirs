from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
import uuid
import logging
import requests
import base64
import json
import binascii

from orders.models import Order, OrderItem
from .forms import OrderForm
from cart.views import _get_cart
from products.models import Product

logger = logging.getLogger('yookassa')


def order_create(request):
    cart = _get_cart(request)
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
        'total_price': total_price,
        'yookassa_shop_id': getattr(settings, 'YOOKASSA_SHOP_ID', 'NOT_SET')
    }

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid() and cart_items:
            session_key = request.session.session_key

            # Создаем заказ со статусом pending
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                customer_first_name=form.cleaned_data['customer_first_name'],
                customer_last_name=form.cleaned_data['customer_last_name'],
                customer_email=form.cleaned_data['customer_email'],
                customer_phone=form.cleaned_data['customer_phone'],
                payment_method='yookassa',
                customer_notes=form.cleaned_data.get('customer_notes', ''),
                shipping_address={
                    'city': form.cleaned_data.get('city', 'Не указан'),
                    'street': form.cleaned_data.get('street', 'Не указан'),
                    'house': form.cleaned_data.get('house', ''),
                    'apartment': form.cleaned_data.get('apartment', ''),
                    'index': form.cleaned_data.get('index', '')
                },
                total_amount=total_price,
                tax_amount=Decimal('0.00'),
                shipping_cost=Decimal('0.00'),
                status='pending',
                payment_status='pending'
            )

            # Создаем OrderItem
            for product_id_str, quantity in cart.items():
                try:
                    product_id = int(product_id_str)
                    product = Product.objects.get(id=product_id, is_active=True)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        product_sku=getattr(product, 'sku', ''),
                        unit_price=product.price,
                        quantity=quantity
                    )
                except (ValueError, Product.DoesNotExist):
                    continue

            # YOO KASSA - Исправленный API вызов
            try:
                shop_id = getattr(settings, 'YOOKASSA_SHOP_ID', None)
                secret_key = getattr(settings, 'YOOKASSA_SECRET_KEY', None)

                # КРИТИЧНО: Проверяем наличие ключей
                if not shop_id or not secret_key:
                    raise Exception("YOOKASSA_SHOP_ID или YOOKASSA_SECRET_KEY не настроены в settings")

                return_url = getattr(settings, 'YOOKASSA_SUCCESS_URL', 'http://localhost:8000/orders/success/')

                #  Детальное логирование ключей (БЕЗ полного secret_key!)
                logger.info(f" SHOP_ID: {shop_id}")
                logger.info(f" SECRET_KEY starts with: {secret_key[:8]}...")
                print(f" SHOP: {shop_id}")
                print(f" SECRET starts with: {secret_key[:8]}...")

                #  Исправленный Basic Auth - без лишних символов
                auth_string = f"{shop_id}:{secret_key}"
                logger.info(f" Auth string length: {len(auth_string)}")

                try:
                    auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
                    logger.info(f"Base64 length: {len(auth_b64)}")
                except binascii.Error as e:
                    raise Exception(f"Ошибка кодирования Base64: {e}")

                idempotence_key = str(uuid.uuid4())
                headers = {
                    'Authorization': f'Basic {auth_b64}',
                    'Idempotence-Key': idempotence_key,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }

                # Исправленный amount - всегда строка с 2 знаками
                amount_value = f"{float(total_price):.2f}"
                payment_data = {
                    "amount": {
                        "value": amount_value,
                        "currency": "RUB"
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": settings.YOOKASSA_SUCCESS_URL
                        #"return_url": return_url
                    },
                    "capture": True,
                    "description": f"Заказ CS{order.id}",
                    "metadata": {
                        "order_id": str(order.id),
                        "session_key": session_key[:32] if session_key else ""
                    }
                }

                logger.info(f" URL: https://api.yookassa.ru/v3/payments")
                logger.info(f" HEADERS: {dict(headers)}")
                logger.info(f" PAYLOAD: {payment_data}")
                print(f" SENDING amount: {amount_value}")

                response = requests.post(
                    'https://api.yookassa.ru/v3/payments',
                    headers=headers,
                    json=payment_data,
                    timeout=30
                )

                logger.info(f" STATUS: {response.status_code}")
                logger.info(f" RESPONSE: {response.text}")

                data = response.json()
                print(f" GOT: {data}")

                if response.status_code in [200, 201]:
                    logger.info(f" Payment created: {data.get('id')} for order {order.id}")
                    order.payment_id = data['id']
                    order.payment_url = data['confirmation']['confirmation_url']
                    order.save()
                    # Очищаем корзину
                    if 'cart' in request.session:
                        del request.session['cart']
                    request.session.modified = True

                    messages.success(request, f'Заказ #{order.order_number} создан! Переходим к оплате...')
                    request.session['last_order_id'] = order.id
                    return redirect(data['confirmation']['confirmation_url'])
                else:
                    error_msg = f"API Error {response.status_code}: {data}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

            except requests.exceptions.RequestException as e:
                error_msg = f"Network error: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)
            except Exception as e:
                logger.error(f"YooKassa error for order {order.id}: {str(e)}")
                print(f" YOOKASSA ERROR {order.id}: {str(e)}")
                messages.error(request, f'Ошибка платежа: {str(e)[:150]}')
                order.status = 'failed'
                order.save()
        else:
            messages.error(request, 'Проверьте правильность заполнения формы')
            context['form'] = form

    return render(request, 'orders/create.html', context)


@csrf_exempt
def yookassa_success(request):
    """Страница успешной оплаты"""

    order_id = request.session.get('last_order_id')

    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            if order.payment_status == 'paid':
                messages.success(request, f'Заказ #{order.order_number} успешно оплачен!')
                return render(request, 'orders/success.html', {'order': order})
        except Order.DoesNotExist:
            pass

    messages.warning(request, 'Заказ не найден. Проверьте статус оплаты.')
    return render(request, 'orders/success.html', {'order': None})


@csrf_exempt
def yookassa_fail(request):
    """Страница неуспешной оплаты"""
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            order.payment_status = 'failed'
            order.status = 'failed'
            order.save()
        except Order.DoesNotExist:
            pass

    messages.error(request, 'Оплата не удалась. Попробуйте еще раз.')
    return redirect('orders:order_create')


@csrf_exempt
def yookassa_webhook(request):
    """Webhook для обновления статуса платежа"""
    try:
        event_json = request.body
        event = json.loads(event_json)

        payment_id = event.get('object', {}).get('id')
        status = event.get('object', {}).get('status')

        if payment_id and status:
            try:
                order = Order.objects.get(payment_id=payment_id)
            except Order.DoesNotExist:
                logger.warning(f"Order not found for payment {payment_id}")
                return JsonResponse({'status': 'ok'})

            if status == 'succeeded':
                order.payment_status = 'paid'
                order.status = 'confirmed'
                order.save()
                logger.info(f"✅ Payment succeeded: {payment_id}, Order: {order.order_number}")
            elif status in ['canceled', 'rejected']:
                order.payment_status = 'failed'
                order.status = 'failed'
                order.save()
                logger.error(f" Payment failed: {payment_id}, Order: {order.order_number}")

        return JsonResponse({'status': 'ok'})
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'status': 'error'}, status=400)


@login_required
def order_history(request):
    """История заказов авторизованного пользователя"""
    orders = Order.objects.filter(
        user=request.user,
    ).order_by('-created_at')[:10]

    context = {
        'orders': orders,
        'title': 'История заказов'
    }
    return render(request, 'orders/order_history.html', context)
