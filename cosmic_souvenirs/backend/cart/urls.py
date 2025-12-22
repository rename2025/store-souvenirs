from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('add/', views.cart_add, name='cart_add_alias'),  # ← ДОБАВИТЬ ЭТУ СТРОКУ
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),

]
