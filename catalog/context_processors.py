# catalog/context_processors.py
from .models import Category

def categories(request):
    # Фильтруем категории с пустым slug и сортируем их
    main_categories = Category.objects.filter(
        parent__isnull=True
    ).exclude(
        slug=''  # Исключаем пустые slug
    ).exclude(
        slug__isnull=True  # Исключаем null slug
    ).prefetch_related('children').order_by('order', 'name')
    
    return {
        'categories': main_categories,
        'all_categories': Category.objects.exclude(slug='').exclude(slug__isnull=True)
    }