# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from .models import (Category, Product, ProductImage, ProductAttribute,
                     ProductAttributeValue, PromoCode)

# Импорты для аналитики
try:
    from orders.models import Order, OrderItem
except ImportError:
    Order = OrderItem = None


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'price', 'stock_quantity', 'is_active', 'is_featured', 'is_in_stock']
    list_filter = ['is_active', 'is_featured', 'is_bestseller', 'categories']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductAttributeInline]
    readonly_fields = ['created_at', 'updated_at']

    def is_in_stock(self, obj):
        """В наличии"""
        return obj.is_in_stock()

    is_in_stock.boolean = True
    is_in_stock.short_description = 'В наличии'

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'sku', 'description', 'categories')
        }),
        ('Цены', {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        ('Инвентарь', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'track_quantity', 'allow_backorder')
        }),
        ('Статусы', {
            'fields': ('is_active', 'is_featured', 'is_bestseller', 'is_new')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )


# dashbord
class SalesDashboardMixin:
    def get_stats_context(self, request):
        context = {}
        if Order:
            context['total_orders'] = Order.objects.count()
            context['paid_orders'] = Order.objects.filter(
                status__in=['paid', 'delivered']
            ).count()
            context['total_revenue'] = Order.objects.filter(
                status__in=['paid', 'delivered']
            ).aggregate(total=Sum('total_amount'))['total'] or 0

            context['promo_orders'] = Order.objects.filter(
                promo_code__isnull=False
            ).count()
            context['promo_savings'] = Order.objects.filter(
                discount_amount__gt=0
            ).aggregate(savings=Sum('discount_amount'))['savings'] or 0

        return context


@admin.register(PromoCode)
class PromoCodeAdmin(SalesDashboardMixin, admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'valid_from', 'valid_until', 'used_count', 'can_use']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code']
    readonly_fields = ['used_count']

    change_list_template = 'admin/promocode_dashboard.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self.get_stats_context(request))
        return super().changelist_view(request, extra_context=extra_context)

    def can_use(self, obj):
        return obj.can_use()

    def promo_stats(self, obj):
        """Статистика по промокоду БЕЗ format кода"""
        if Order:
            orders_count = Order.objects.filter(promo_code=obj).count()
            savings = Order.objects.filter(promo_code=obj).aggregate(
                s=Sum('discount_amount')
            )['s'] or 0

            return format_html(
                '<span style="color: green;">{} заказов</span> '
                '<span style="color: blue;">экономия: {}₽</span>',
                orders_count, int(savings)
            )
        return "Нет данных"

    can_use.boolean = True
    can_use.short_description = 'Можно использовать'
    promo_stats.short_description = 'Статистика'
