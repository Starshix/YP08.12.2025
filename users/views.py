from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from catalog.models import Product, Category
from django.db.models import Count, Q, Sum
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .decorators import customer_required, manager_required, content_manager_required, admin_required
from .models import User, Role
from orders.models import Order
from django.contrib.auth import authenticate

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            authenticated_user = authenticate(
                request,
                username=user.email,  # или user.username, если есть
                password=form.cleaned_data['password1']
            )
            
            if authenticated_user:
                login(request, authenticated_user)
            else:
                # Если аутентификация не сработала, логиним с указанием backend
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
            
            messages.success(request, 'Вы успешно зарегистрировались как покупатель!')
            return redirect('users:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            
            # Перенаправляем на дашборд в зависимости от роли
            next_url = request.GET.get('next', 'users:dashboard')  # Добавили 'users:'
            return redirect(next_url)
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})
    

def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')

@login_required
def dashboard(request):
    """Дашборд для всех пользователей"""
    context = {}
    user = request.user
    
    # Определяем роль пользователя
    if user.role:
        is_customer = user.role.name == 'customer'
        is_manager = user.role.name == 'manager'
        is_content_manager = user.role.name == 'content_manager'
        is_admin = user.role.name == 'admin' or user.is_superuser
    else:
        # Если нет роли, используем стандартные поля Django
        is_customer = not user.is_staff and not user.is_superuser
        is_manager = user.is_staff and not user.is_superuser
        is_content_manager = user.is_staff and not user.is_superuser
        is_admin = user.is_superuser
    
    if is_customer:
        # Для покупателей - получаем их заказы
        user_orders = Order.objects.filter(user=user)
        context['order_count'] = user_orders.count()
        context['recent_orders'] = user_orders.order_by('-created_at')[:5]
        context['user'] = user
        context['is_customer'] = True
    
    elif is_manager or is_admin:
        # Для менеджеров и администраторов - общая статистика
        all_orders = Order.objects.all()
        context['total_orders'] = all_orders.count()
        context['completed_orders'] = all_orders.filter(status='delivered').count()
        context['pending_orders'] = all_orders.filter(status='processing').count()
        
        # Подсчитываем клиентов
        try:
            customer_role = Role.objects.get(name='customer')
            context['total_customers'] = User.objects.filter(role=customer_role).count()
        except Role.DoesNotExist:
            context['total_customers'] = User.objects.filter(is_staff=False, is_superuser=False).count()
        
        # Вычисляем общую выручку
        total_revenue = all_orders.aggregate(total=Sum('total_price'))['total'] or 0
        context['total_revenue'] = total_revenue
        
        context['is_manager'] = True
        context['user'] = user
    
    elif is_content_manager:
        # Для контент-менеджеров - статистика каталога
        total_products = Product.objects.count()
        in_stock = Product.objects.filter(quantity__gt=0).count()
        out_of_stock = Product.objects.filter(quantity=0).count()
        active_products = Product.objects.filter(is_active=True).count()
        total_categories = Category.objects.count()
        
        context.update({
            'total_products': total_products,
            'in_stock': in_stock,
            'out_of_stock': out_of_stock,
            'active_products': active_products,
            'total_categories': total_categories,
            'is_content_manager': True,
            'user': user,
        })
    
    return render(request, 'users/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})

# Пример защищённых вьюшек для разных ролей


@login_required
@content_manager_required
def content_dashboard(request):
    """Дашборд для контент-менеджеров"""
    return render(request, 'users/content_dashboard.html')

@login_required
@admin_required
def admin_dashboard(request):
    """Дашборд для администраторов"""
    return render(request, 'users/admin_dashboard.html')

@login_required
@manager_required
def customer_list(request):
    """Список клиентов для менеджера"""
    from django.utils import timezone
    from datetime import timedelta
    
    # Получаем всех покупателей
    customers = User.objects.filter(role__name='customer').order_by('-date_joined')
    
    # Статистика
    today = timezone.now().date()
    active_customers = customers.filter(is_active=True).count()
    new_customers_today = customers.filter(date_joined__date=today).count()
    customers_with_phone = customers.exclude(phone='').count()
    
    context = {
        'customers': customers,
        'active_customers': active_customers,
        'new_customers_today': new_customers_today,
        'customers_with_phone': customers_with_phone,
    }
    
    return render(request, 'users/customer_list.html', context)


@login_required
def manager_dashboard(request):
    """Дашборд для всех пользователей"""
    context = {}
    user = request.user
    
    # Для менеджеров и администраторов - общая статистика
    all_orders = Order.objects.all()
    context['total_orders'] = all_orders.count()
    context['completed_orders'] = all_orders.filter(status='delivered').count()
    context['pending_orders'] = all_orders.filter(status='processing').count()
        
    # Подсчитываем клиентов
    try:
        customer_role = Role.objects.get(name='customer')
        context['total_customers'] = User.objects.filter(role=customer_role).count()
    except Role.DoesNotExist:
        context['total_customers'] = User.objects.filter(is_staff=False, is_superuser=False).count()
        
    # Вычисляем общую выручку
    total_revenue = all_orders.aggregate(total=Sum('total_price'))['total'] or 0
    context['total_revenue'] = total_revenue
        
    context['is_manager'] = True
    context['user'] = user
    # Для контент-менеджеров - статистика каталога
    total_products = Product.objects.count()
    in_stock = Product.objects.filter(quantity__gt=0).count()
    out_of_stock = Product.objects.filter(quantity=0).count()
    active_products = Product.objects.filter(is_active=True).count()
    total_categories = Category.objects.count()
    all_orders = Order.objects.all()


    context.update({
        'total_products': total_products,
        'in_stock': in_stock,
        'out_of_stock': out_of_stock,
        'active_products': active_products,
        'total_categories': total_categories,
        'is_content_manager': True,
        'user': user,
        'recent_orders': Order.objects.select_related('user').order_by('-created_at')[:10],
    })
    
    return render(request, 'users/manager_dashboard.html', context)

@login_required
@content_manager_required
def content_dashboard(request):
    """Дашборд для контент-менеджеров"""
    
    # Получаем статистику товаров
    total_products = Product.objects.count()
    
    # Используем поле quantity вместо stock
    in_stock = Product.objects.filter(quantity__gt=0).count()
    out_of_stock = Product.objects.filter(quantity=0).count()
    active_products = Product.objects.filter(is_active=True).count()
    
    # Получаем статистику категорий с количеством товаров
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count')[:10]  # Топ 10 категорий
    
    total_categories = Category.objects.count()
    
    # Последние добавленные товары
    recent_products = Product.objects.select_related('category').order_by('-created_at')[:10]
    
    # Товары с изображениями
    # Проверяем наличие поля image в модели
    try:
        # Проверяем, есть ли у товаров поле image
        products_with_images = Product.objects.exclude(Q(image='') | Q(image__isnull=True)).count()
    except:
        # Если нет поля image, проверяем наличие images (многие ко многим)
        try:
            products_with_images = Product.objects.filter(images__isnull=False).distinct().count()
        except:
            products_with_images = 0
    
    products_with_images_percentage = (products_with_images / total_products * 100) if total_products > 0 else 0
    
    # Рассчитываем заполненность каталога (произвольная метрика)
    catalog_fill_percentage = min(100, (total_products / 100) * 10) if total_products > 0 else 0
    
    # Собираем все статистики в один словарь
    stats = {
        'total_products': total_products,
        'total_categories': total_categories,
        'in_stock': in_stock,
        'out_of_stock': out_of_stock,
        'active_products': active_products,
        'products_with_images': products_with_images,
        'products_with_images_percentage': round(products_with_images_percentage, 1),
        'catalog_fill_percentage': round(catalog_fill_percentage, 1),
    }
    
    context = {
        'stats': stats,
        'recent_products': recent_products,
        'categories': categories,
    }
    
    return render(request, 'users/content_dashboard.html', context)