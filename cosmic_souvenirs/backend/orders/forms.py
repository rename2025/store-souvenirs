from django import forms
from orders.models import Order


class OrderForm(forms.Form):
    # ✅ ПРАВИЛЬНЫЕ имена полей модели Order!
    customer_first_name = forms.CharField(max_length=50, label='Имя')
    customer_last_name = forms.CharField(max_length=50, label='Фамилия')
    customer_email = forms.EmailField(label='Email')
    customer_phone = forms.CharField(max_length=20, label='Телефон')

    # Разбиваем address на структуру JSON для shipping_address
    city = forms.CharField(max_length=100, label='Город')
    street = forms.CharField(max_length=200, label='Улица')
    house = forms.CharField(max_length=20, label='Дом')
    apartment = forms.CharField(max_length=20, label='Квартира', required=False)
    index = forms.CharField(max_length=6, label='Индекс')

    # Дополнительные поля
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        label='Способ оплаты',
        initial='card'
    )
    customer_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Комментарий к заказу'
    )
