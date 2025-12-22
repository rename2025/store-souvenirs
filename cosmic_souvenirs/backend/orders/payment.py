import uuid
from datetime import timezone

import requests
from django.conf import settings
from django.urls import reverse
from .models import Order
from ..cosmic_souvenirs.celery import send_order_confirmation_email


class YooKassaPayment:
    BASE_URL = "https://api.yookassa.ru/v3"

    def __init__(self):
        self.shop_id = settings.YOOKASSA_SHOP_ID
        self.secret_key = settings.YOOKASSA_SECRET_KEY

    def create_payment(self, order, return_url):

        payload = {
            "amount": {
                "value": f"{order.total_amount:.2f}",
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": f"Заказ №{order.order_number}",
            "metadata": {
                "order_number": order.order_number
            },
            "receipt": {
                "customer": {
                    "email": order.customer_email,
                    "phone": order.customer_phone
                },
                "items": self._get_receipt_items(order)
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Idempotence-Key": str(uuid.uuid4())
        }

        response = requests.post(
            f"{self.BASE_URL}/payments",
            json=payload,
            auth=(self.shop_id, self.secret_key),
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            order.yookassa_payment_id = data['id']
            order.save()
            return data
        else:
            raise Exception(f"YooKassa error: {response.text}")

    def _get_receipt_items(self, order):
        """Формирует позиции для чека"""
        items = []
        for item in order.items.all():
            items.append({
                "description": item.product_name,
                "quantity": str(item.quantity),
                "amount": {
                    "value": f"{item.unit_price:.2f}",
                    "currency": "RUB"
                },
                "vat_code": 1,  # НДС 20%
                "payment_mode": "full_payment",
                "payment_subject": "commodity"
            })

        # Добавляем доставку
        if order.shipping_cost > 0:
            items.append({
                "description": "Доставка",
                "quantity": "1",
                "amount": {
                    "value": f"{order.shipping_cost:.2f}",
                    "currency": "RUB"
                },
                "vat_code": 1,
                "payment_mode": "full_payment",
                "payment_subject": "service"
            })

        return items

    def check_payment_status(self, payment_id):
        """Проверяет статус платежа"""
        response = requests.get(
            f"{self.BASE_URL}/payments/{payment_id}",
            auth=(self.shop_id, self.secret_key)
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"YooKassa error: {response.text}")


def handle_yookassa_webhook(data):
    """Обрабатывает вебхук от YooKassa"""
    payment_id = data['object']['id']
    status = data['object']['status']

    try:
        order = Order.objects.get(yookassa_payment_id=payment_id)

        if status == 'succeeded':
            order.payment_status = 'paid'
            order.paid_at = timezone.now()
            order.status = 'confirmed'
            order.save()

            # Отправляем уведомление
            send_order_confirmation_email(order)
        elif status == 'canceled':
            order.payment_status = 'failed'
            order.save()

    except Order.DoesNotExist:
        pass