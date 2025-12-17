from django.contrib import admin
from .models import Category, Brand, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'is_main', 'order']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'order']
    list_filter = ['parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'brand', 'price', 
                   'availability', 'is_active', 'created_at']
    list_filter = ['category', 'brand', 'availability', 'is_active', 
                  'is_new', 'is_sale', 'is_featured']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'brand', 'sku')
        }),
        ('Цены и наличие', {
            'fields': ('price', 'old_price', 'availability', 'quantity')
        }),
        ('Описание', {
            'fields': ('description', 'features')
        }),
        ('Флаги', {
            'fields': ('is_active', 'is_new', 'is_sale', 'is_featured')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')