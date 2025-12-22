from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from products.models import Product


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.email}"
        return f"Anonymous cart {self.session_key}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    def get_item(self, product):
        try:
            return self.items.get(product=product)
        except CartItem.DoesNotExist:
            return None

    def merge_with_session_cart(self, session_cart):
        """Объединяет корзину пользователя с сессионной корзиной"""
        for session_item in session_cart.items.all():
            user_item = self.get_item(session_item.product)
            if user_item:
                user_item.quantity += session_item.quantity
                user_item.save()
            else:
                session_item.cart = self
                session_item.save()
        session_cart.delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.product.price

    def clean(self):
        if self.quantity < 1:
            raise ValidationError("Quantity must be at least 1")

        # Проверка наличия товара
        if not self.product.is_in_stock() and not self.product.allow_backorder:
            raise ValidationError("Product is out of stock")

        if self.product.track_quantity and self.quantity > self.product.stock_quantity:
            if self.product.allow_backorder:
                # Можно заказать больше чем в наличии
                pass
            else:
                # УДАЛИТЕ эту строку: from poetry.core.json import ValidationError
                raise ValidationError(f"Only {self.product.stock_quantity} items available")  # ← Используем правильный ValidationError