import os

from celery import Celery
from django.conf import settings



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cosmic_souvenirs.settings')

app = Celery('cosmic_store')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# tasks.py в приложении orders
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
#from orders.models import Order


@shared_task
def send_order_confirmation_email(order_id):
    """Отправляет email подтверждения заказа"""
    try:
        from orders.models import Order
        order = Order.objects.get(id=order_id)

        subject = f'Подтверждение заказа #{order.order_number}'
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order
        })
        text_message = render_to_string('emails/order_confirmation.txt', {
            'order': order
        })

        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            html_message=html_message
        )

    except Order.DoesNotExist:
        pass


@shared_task
def cleanup_expired_carts():
    """Очищает корзины старше 7 дней"""
    from cart.models import Cart
    from django.utils import timezone
    from datetime import timedelta

    expired_date = timezone.now() - timedelta(days=7)
    expired_carts = Cart.objects.filter(
        user__isnull=True,
        created_at__lt=expired_date
    )
    count = expired_carts.count()
    expired_carts.delete()

    return f"Deleted {count} expired carts"


@shared_task
def update_product_popularity():
    """Обновляет популярность товаров на основе продаж"""
    from products.models import Product
    from orders.models import OrderItem


    # Получаем самые продаваемые товары за последние 30 дней
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count

    thirty_days_ago = timezone.now() - timedelta(days=30)

    popular_products = OrderItem.objects.filter(
        order__created_at__gte=thirty_days_ago,
        order__status__in=['delivered', 'shipped']
    ).values('product').annotate(
        total_sold=Count('id')
    ).order_by('-total_sold')[:10]

    # Сбрасываем все хит товары
    Product.objects.filter(is_bestseller=True).update(is_bestseller=False)

    # Устанавливаем новые хиты
    for item in popular_products:
        Product.objects.filter(id=item['product']).update(is_bestseller=True)

    return f"Updated popularity for {len(popular_products)} products"