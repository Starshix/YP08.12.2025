from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Код выполняется перед view
        
        response = self.get_response(request)
        
        # Код выполняется после view
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Проверяем доступ к страницам админки
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                return redirect(f'{reverse("users:login")}?next={request.path}')
            
            if not (request.user.is_staff or request.user.is_superuser):
                messages.error(request, 'У вас нет доступа к админ-панели')
                return redirect('home')
        
        return None