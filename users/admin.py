from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Role

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_name_display', 'get_users_count']
    filter_horizontal = ['permissions']
    search_fields = ['name']
    
    def get_users_count(self, obj):
        return obj.users.count()
    get_users_count.short_description = 'Количество пользователей'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['email']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Персональная информация'), {
            'fields': ('first_name', 'last_name', 'phone', 'address', 'city', 
                      'postal_code', 'birth_date')
        }),
        (_('Роли и права'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser',
                      'groups', 'user_permissions')
        }),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 
                      'password1', 'password2', 'role'),
        }),
    )