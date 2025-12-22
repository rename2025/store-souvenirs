from .models import Category

def categories(request):
    """Добавляет категории во ВСЕ шаблоны автоматически"""
    return {
        'categories': Category.objects.filter(is_active=True, parent__isnull=True)
    }