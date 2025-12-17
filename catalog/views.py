from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from users.decorators import content_manager_required
from .models import Product, Category, Brand
from .forms import ProductForm, CategoryForm, ProductFilterForm
from django.contrib import messages

class ProductListView(ListView):
    model = Product
    template_name = 'catalog/product_list.html'
    paginate_by = 12
    context_object_name = 'products'
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'brand')
        

        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)

            all_categories = [category.id]
            all_categories.extend(cat.id for cat in category.get_all_children)
            queryset = queryset.filter(category_id__in=all_categories)
        

        brand_slug = self.kwargs.get('brand_slug')
        if brand_slug:
            brand = get_object_or_404(Brand, slug=brand_slug)
            queryset = queryset.filter(brand=brand)
        

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query) |
                Q(features__icontains=search_query)
            )
        

        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        

        availability = self.request.GET.get('availability')
        if availability:
            queryset = queryset.filter(availability=availability)
        

        in_stock_only = self.request.GET.get('in_stock_only')
        if in_stock_only:
            queryset = queryset.filter(quantity__gt=0)
        

        sort = self.request.GET.get('sort', 'created_at')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        elif sort == 'quantity_desc':
            queryset = queryset.order_by('-quantity')
        elif sort == 'popular':

            queryset = queryset.order_by('-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent=None)
        context['brands'] = Brand.objects.all()
        context['category_slug'] = self.kwargs.get('category_slug')
        context['brand_slug'] = self.kwargs.get('brand_slug')
        context['search_query'] = self.request.GET.get('q', '')
        

        context['filter_form'] = ProductFilterForm(self.request.GET)
        

        total_products = self.get_queryset().count()
        in_stock_count = self.get_queryset().filter(quantity__gt=0).count()
        out_of_stock_count = total_products - in_stock_count
        
        context['stats'] = {
            'total': total_products,
            'in_stock': in_stock_count,
            'out_of_stock': out_of_stock_count,
            'in_stock_percent': int((in_stock_count / total_products * 100) if total_products > 0 else 0),
        }
        
        return context
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent=None)
        context['brands'] = Brand.objects.all()
        context['category_slug'] = self.kwargs.get('category_slug')
        context['brand_slug'] = self.kwargs.get('brand_slug')
        context['search_query'] = self.request.GET.get('q', '')
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        

        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        

        context['new_products'] = Product.objects.filter(
            is_active=True,
            is_new=True
        ).exclude(id=product.id)[:4]
        
        return context

class SearchView(ListView):
    model = Product
    template_name = 'catalog/search_results.html'
    paginate_by = 12
    context_object_name = 'products'
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(sku__icontains=query) |
                Q(features__icontains=query)
            ).filter(is_active=True)
        return Product.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q')
        return context

def home(request):


    categories = Category.objects.filter(parent__isnull=True).exclude(slug='').prefetch_related('children')
    

    featured_products = Product.objects.filter(
        is_active=True, 
        is_featured=True
    )[:8]
    

    new_products = Product.objects.filter(
        is_active=True, 
        is_new=True
    )[:8]
    

    sale_products = Product.objects.filter(
        is_active=True, 
        is_sale=True
    ).exclude(old_price__isnull=True)[:8]
    


    main_categories = categories[:6]
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'sale_products': sale_products,
        'categories': main_categories,  # Используем отфильтрованные
    }
    return render(request, 'catalog/home.html', context)

@login_required
@content_manager_required
def category_list(request):
    """Список категорий для контент-менеджера"""
    categories = Category.objects.all().order_by('name')
    

    parent_count = Category.objects.filter(parent=None).count()
    child_count = Category.objects.filter(parent__isnull=False).count()
    with_images_count = Category.objects.exclude(image='').count()
    
    context = {
        'categories': categories,
        'parent_count': parent_count,
        'child_count': child_count,
        'with_images_count': with_images_count,
    }
    
    return render(request, 'catalog/category_list.html', context)


@login_required
@content_manager_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Товар "{product.name}" успешно создан!')
            return redirect('catalog:product_detail', slug=product.slug)
    else:
        form = ProductForm()
    
    return render(request, 'catalog/product_form.html', {
        'form': form,
        'title': 'Создание товара'
    })

@login_required
@content_manager_required
def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Товар "{product.name}" успешно обновлен!')
            return redirect('catalog:product_detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'catalog/product_form.html', {
        'form': form,
        'title': f'Редактирование: {product.name}',
        'product': product
    })

@login_required
@content_manager_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Товар "{product_name}" успешно удален!')
        return redirect('catalog:product_list')
    
    return render(request, 'catalog/product_confirm_delete.html', {
        'product': product
    })

@login_required
@content_manager_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Категория "{category.name}" успешно создана!')
            return redirect('catalog:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'catalog/category_form.html', {
        'form': form,
        'title': 'Создание категории'
    })

@login_required
@content_manager_required
def category_update(request, slug):
    category = get_object_or_404(Category, slug=slug)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Категория "{category.name}" успешно обновлена!')
            return redirect('catalog:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'catalog/category_form.html', {
        'form': form,
        'title': f'Редактирование: {category.name}',
        'category': category
    })

@login_required
@content_manager_required
def category_delete(request, slug):
    category = get_object_or_404(Category, slug=slug)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Категория "{category_name}" успешно удалена!')
        return redirect('catalog:category_list')
    
    return render(request, 'catalog/category_confirm_delete.html', {
        'category': category
    })

@login_required
@content_manager_required
def category_detail_slug(request, slug):
    category = get_object_or_404(Category, slug=slug)
        

    products = Product.objects.filter(category=category, is_active=True)
    

    subcategories = Category.objects.filter(parent=category)
    
    context = {
        'category': category,
        'products': products,
        'subcategories': subcategories,
    }
    return render(request, 'catalog/category_detail.html', context)

@login_required
@content_manager_required
def category_list(request):
    """Список категорий для контент-менеджера"""
    categories = Category.objects.all().order_by('name')
    

    parent_count = Category.objects.filter(parent=None).count()
    child_count = Category.objects.filter(parent__isnull=False).count()
    with_images_count = Category.objects.exclude(image='').count()
    
    context = {
        'categories': categories,
        'parent_count': parent_count,
        'child_count': child_count,
        'with_images_count': with_images_count,
    }
    
    return render(request, 'catalog/category_list.html', context)