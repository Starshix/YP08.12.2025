from .models import Category

def categories(request):

    main_categories = Category.objects.filter(
        parent__isnull=True
    ).exclude(
        slug=''
    ).exclude(
        slug__isnull=True 
    ).prefetch_related('children').order_by('order', 'name')
    
    return {
        'categories': main_categories,
        'all_categories': Category.objects.exclude(slug='').exclude(slug__isnull=True)
    }