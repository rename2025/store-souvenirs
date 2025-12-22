
from django.core.cache import cache
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from .models import Product, Category
from reviews.models import Review
from django.views.generic import DetailView


def home(request):

   cache_key = 'home_page_data'
   data = cache.get(cache_key)

   if not data:
        popular_products = Product.objects.filter(
            is_active=True,
            is_bestseller=True
        )[:8]

        new_products = Product.objects.filter(
            is_active=True,
            is_new=True
        )[:8]

        # Временно закомментируем отзывы, пока не создадим модель Review
        # reviews = Review.objects.filter(
        #     # is_approved=True
        # ).select_related('user', 'product')[:3]

        stats = {
            'customers': 1248,
            'customers_growth': 12,
            'products': Product.objects.filter(is_active=True).count(),
            'new_products': Product.objects.filter(is_active=True, is_new=True).count(),
            'delivery_time': '24ч',
            'rating': 4.9,
            'satisfaction': 96,
        }
        categories = Category.objects.filter(is_active=True, parent__isnull=True)

        data = {
            'popular_products': popular_products,
            'new_products': new_products,
            'stats': stats,
            'categories': Category.objects.filter(is_active=True, parent__isnull=True),  # ← ДОБАВЬТЕ
        }

        return render(request, 'index.html', data)


class ProductListView(ListView):
    model = Product
    template_name = 'products/catalog.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)

        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(categories=category)

        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        sort = self.request.GET.get('sort', 'newest')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'popular':
            queryset = queryset.filter(is_bestseller=True)
        elif sort == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        context['current_category'] = self.kwargs.get('category_slug')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        # Временно убираем prefetch_related('reviews')
        return Product.objects.filter(is_active=True).prefetch_related(
            'images', 'attributes'
            # 'reviews'  # Временно убираем
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object

        # Временно закомментируем вычисление среднего рейтинга
        # context['average_rating'] = product.reviews.aggregate(
        #     avg_rating=Avg('rating')
        # )['avg_rating'] or 0

        context['average_rating'] = 0  # Временное значение

        context['related_products'] = Product.objects.filter(
            categories__in=product.categories.all(),
            is_active=True
        ).exclude(id=product.id).distinct()[:4]

        return context


def new_arrivals(request):
    """Показывает новинки"""
    new_products = Product.objects.filter(
        is_active=True,
        is_new=True
    )[:10]

    return render(request, 'products/catalog.html', {
        'products': new_products,
        'title': 'Новинки'
    })


def sales(request):
    """Показывает товары со скидкой"""
    # Предполагаем, что есть поле discount или on_sale
    # Проверяем, есть ли поле discount в модели Product
    try:
        # Проверяем, есть ли у модели поле discount
        if hasattr(Product, 'discount'):
            sale_products = Product.objects.filter(
                is_active=True,
                discount__gt=0
            )[:10]
        else:
            # Если поля нет, показываем бестселлеры
            sale_products = Product.objects.filter(
                is_active=True,
                is_bestseller=True
            )[:10]
    except:
        # В случае ошибки показываем пустой список
        sale_products = Product.objects.none()

    return render(request, 'products/catalog.html', {
        'products': sale_products,
        'title': 'Акции'
    })


def search(request):
    """Поиск товаров"""
    query = request.GET.get('q', '').strip()

    if query:
        products = Product.objects.filter(
            is_active=True
        ).filter(
            name__icontains=query
        ) | Product.objects.filter(
            is_active=True
        ).filter(
            description__icontains=query
        )
        products = products.distinct()[:20]
        title = f'Результаты поиска: "{query}"'
    else:
        products = Product.objects.filter(is_active=True)[:20]
        title = 'Все товары'

    return render(request, 'products/catalog.html', {
        'products': products,
        'title': title,
        'query': query
    })


class CategoryDetailView(ListView):
    model = Product
    template_name = 'products/catalog.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category, slug=category_slug)
        return Product.objects.filter(
            categories=category,
            is_active=True
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        context['current_category'] = category_slug
        context['category'] = get_object_or_404(Category, slug=category_slug)
        context['categories'] = Category.objects.filter(is_active=True, parent__isnull=True)
        return context
