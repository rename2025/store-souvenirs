from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('success/', views.yookassa_success, name='order_create_success'),
    path('fail/', views.yookassa_fail, name='order_create_fail'),
    path('webhook/yookassa/', views.yookassa_webhook, name='yookassa_webhook'),
    path('created/<int:order_id>/', views.order_create, name='order_created'),
    path('history/', views.order_history, name='order_history'),
]