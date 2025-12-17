from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from functools import wraps

def role_required(role_name, login_url=None, message=None):
    """
    Декоратор для проверки роли пользователя
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if login_url:
                    return redirect(login_url)
                return redirect('users:login')
            
            if not hasattr(request.user, 'role'):
                if message:
                    messages.error(request, message)
                return redirect('home')
            
            if request.user.role and request.user.role.name == role_name:
                return view_func(request, *args, **kwargs)
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if message:
                messages.error(request, message)
            
            return redirect('home')
        
        return _wrapped_view
    return decorator

def permission_required(perm, login_url=None, message=None):
    """
    Декоратор для проверки конкретного права
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if login_url:
                    return redirect(login_url)
                return redirect('users:login')
            
            if not request.user.has_perm(perm):
                if message:
                    messages.error(request, message or 'У вас нет прав для доступа к этой странице')
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator

# Готовые декораторы для конкретных ролей
customer_required = role_required('customer', message='Требуется роль покупателя')
manager_required = role_required('manager', message='Требуется роль менеджера')
content_manager_required = role_required('content_manager', message='Требуется роль контент-менеджера')
admin_required = role_required('admin', message='Требуется роль администратора')

# Стандартные декораторы Django с нашими правами
def staff_required(view_func=None, login_url=None, message=None):
    """
    Декоратор для проверки is_staff
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and (u.is_staff or u.is_superuser),
        login_url=login_url,
    )
    
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator