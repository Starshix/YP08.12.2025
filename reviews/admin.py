from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewImage, ReviewVote

class ReviewImageInline(admin.TabularInline):
    """Изображения к отзыву"""
    model = ReviewImage
    extra = 0
    fields = ['image', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Превью"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Простая админка для отзывов"""
    
    list_display = [
        'id',
        'product_name',
        'user_email',
        'rating_stars',
        'is_approved',
        'is_purchased',
        'created_at'
    ]
    
    list_filter = [
        'is_approved',
        'is_purchased',
        'rating',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'comment',
        'user__email',
        'product__name'
    ]
    
    list_editable = ['is_approved']
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Товар и пользователь', {
            'fields': ['product', 'user', 'order']
        }),
        ('Отзыв', {
            'fields': ['rating', 'title', 'comment', 'advantages', 'disadvantages']
        }),
        ('Статус', {
            'fields': ['is_approved', 'is_purchased', 'created_at', 'updated_at']
        }),
    ]
    
    inlines = [ReviewImageInline]
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = "Товар"
    product_name.admin_order_field = 'product__name'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Пользователь"
    user_email.admin_order_field = 'user__email'
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: gold;">{}</span>', stars)
    rating_stars.short_description = "Рейтинг"
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} отзывов одобрено")
    approve_reviews.short_description = "Одобрить выбранные отзывы"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} отзывов отклонено")
    disapprove_reviews.short_description = "Отклонить выбранные отзывы"


@admin.register(ReviewImage)
class ReviewImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Изображение"


@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'user', 'vote', 'created_at']
    list_filter = ['vote']