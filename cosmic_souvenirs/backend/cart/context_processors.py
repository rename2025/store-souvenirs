# cart/context_processors.py
from django.db import models

from .models import Cart, CartItem  # замените на ваши модели корзины


def cart_items_count(request):
    item_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            item_count = cart.items.aggregate(total=models.Sum('quantity'))['total'] or 0
        except Cart.DoesNotExist:
            pass
    # Для неавторизованных пользователей - логика с сессией
    elif 'cart' in request.session:
        item_count = sum(request.session['cart'].values())

    return {'cart_items_count': item_count}
