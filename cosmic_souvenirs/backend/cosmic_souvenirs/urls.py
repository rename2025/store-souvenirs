from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [

    # Админ-панель
    path('admin/', admin.site.urls),

    #path('reviews/',include('reviews.urls')),
    #shop
    #path('shop/', include('shop.urls')),

    # Главная страница (через products)
    path('', include('products.urls')),

    # Аутентификация (Django built-in)
    path('accounts/', include('django.contrib.auth.urls')),

    # Пользовательские URL
    path('users/', include('users.urls')),

    # Корзина
    path('cart/', include('cart.urls')),

    # Заказы
    path('orders/', include('orders.urls')),

    # Статические страницы
    path('about/', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    path('contacts/', TemplateView.as_view(template_name='pages/contacts.html'), name='contacts'),
    path('shipping/', TemplateView.as_view(template_name='pages/shipping.html'), name='shipping'),
    path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
   #path('catalog/<slug:category_slug>/', CategoryDetailView.as_view(), name='category'),

]

# Обслуживание медиафайлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Для статических файлов в DEBUG режиме (опционально, если не используете collectstatic)
    if not settings.STATIC_URL.startswith('http'):
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Добавляем debug_toolbar (рекомендуется для разработки)
    try:
        import debug_toolbar

        urlpatterns = [
                          #path('__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns
    except ImportError:
        pass