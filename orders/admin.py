from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'first_name', 'last_name', 
                   'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at', 'payment_method']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('user', 'status', 'total_price', 'payment_method')
        }),
        ('Информация о покупателе', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Адрес доставки', {
            'fields': ('address', 'city', 'postal_code')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'price', 'quantity']
    list_filter = ['order__status']