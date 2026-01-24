from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('confirmed', 'Подтвержден'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
        ('refunded', 'Возвращен'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('failed', 'Ошибка оплаты'),
        ('refunded', 'Возвращен'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Банковская карта'),
        ('electronic', 'Электронные деньги'),
        ('cash', 'Наличные при получении'),
    ]


    promo_code = models.ForeignKey(
        'products.PromoCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Промокод'
    )
    discount_amount = models.DecimalField(
        default=0,
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма скидки'
    )
    final_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Итого с учетом скидки'
    )

    # Основная информация
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('Пользователь')
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name=_('Ключ сессии'))
    order_number = models.CharField(max_length=20, unique=True, blank=True, verbose_name=_('Номер заказа'))


    # Статусы
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending', verbose_name=_('Статус заказа'))
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name=_('Статус оплаты'))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card', verbose_name=_('Способ оплаты'))

    # Платежная информация
    yookassa_payment_id = models.CharField(max_length=100, blank=True, verbose_name=_('ID платежа YooKassa'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_('Общая сумма'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_('Сумма налогов'))
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_('Стоимость доставки'))


    customer_email = models.EmailField(verbose_name=_('Email клиента'))
    customer_phone = models.CharField(max_length=20, verbose_name=_('Телефон клиента'))
    customer_first_name = models.CharField(max_length=50, verbose_name=_('Имя клиента'))
    customer_last_name = models.CharField(max_length=50, verbose_name=_('Фамилия клиента'))

    delivery_days = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Дни доставки'))

    # Адрес доставки
    shipping_address = models.JSONField(verbose_name=_('Адрес доставки'))

    # Комментарии
    customer_notes = models.TextField(blank=True, verbose_name=_('Комментарий клиента'))
    admin_notes = models.TextField(blank=True, verbose_name=_('Комментарий администратора'))

    # Даты
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создан'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлен'))
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Оплачен'))
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Отправлен'))
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Доставлен'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')

    def __str__(self):
        return f"Заказ #{self.order_number}"

    def save(self, *args, **kwargs):
        # Автоматически заполняем final_total если не указан
        if not hasattr(self, '_initial') or self.pk is None:
            self.final_total = self.total_amount or 0
            self.discount_amount = getattr(self, 'discount_amount', 0)

        # Если есть промокод — пересчитываем
        if self.promo_code and self.promo_code.can_use():
            if self.promo_code.discount_type == 'percent':
                self.discount_amount = self.total_amount * (self.promo_code.discount_value / 100)
            else:
                self.discount_amount = self.promo_code.discount_value
            self.discount_amount = min(self.discount_amount, self.total_amount)
            self.final_total = self.total_amount - self.discount_amount

        # Генерируем номер заказа
        if not self.order_number:
            self.order_number = self.generate_order_number()

        super().save(*args, **kwargs)

    def generate_order_number(self):
        import time
        user_id = self.user.id if self.user else 0
        return f"CS{int(time.time())}{user_id:04d}"

    @property
    def subtotal(self):
        return self.total_amount - self.tax_amount - self.shipping_cost

    def can_be_cancelled(self):
        return self.status in ['pending', 'confirmed']

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('order_detail', kwargs={'order_number': self.order_number})


def apply_promo_code(self, promo_code_str):
    """Автоматически применить промокод"""
    from products.models import PromoCode
    from django.utils import timezone
    from django.db.models import F

    try:
        promo = PromoCode.objects.get(
            code=promo_code_str,
            is_active=True,
            valid_until__gt=timezone.now(),
            used_count__lt=F('usage_limit')
        )

        if promo.discount_type == 'percent':
            self.discount_amount = self.total * (promo.discount_value / 100)
        else:
            self.discount_amount = promo.discount_value

        self.discount_amount = min(self.discount_amount, self.total)
        self.final_total = self.total - self.discount_amount
        self.promo_code = promo
        self.save()

        promo.used_count += 1
        promo.save()
        return True, f"Скидка {promo.discount_value}% применена!"

    except PromoCode.DoesNotExist:
        self.discount_amount = 0
        self.final_total = self.total
        self.promo_code = None
        self.save()
        return False, "Промокод недействителен"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    @property
    def get_cost(self):
        return self.total_price


class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_delivery = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class TaxRate(models.Model):
    name = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    country = models.CharField(max_length=2, default='RU')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.rate}%)"
