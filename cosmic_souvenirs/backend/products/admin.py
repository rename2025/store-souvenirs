# Register your models here.
from django.contrib import admin
from .models import Category, Product, ProductImage, ProductAttribute, ProductAttributeValue


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

    #
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