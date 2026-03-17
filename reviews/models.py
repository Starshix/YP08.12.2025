from django.db import models
from django.conf import settings
from catalog.models import Product
from orders.models import Order

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Товар'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Пользователь'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name='Заказ'
    )
    rating = models.PositiveSmallIntegerField(
        'Оценка',
        choices=RATING_CHOICES
    )
    title = models.CharField('Заголовок', max_length=200)
    comment = models.TextField('Комментарий')
    advantages = models.TextField('Достоинства', blank=True)
    disadvantages = models.TextField('Недостатки', blank=True)
    
    # Модерация
    is_approved = models.BooleanField('Одобрен', default=False)
    is_purchased = models.BooleanField('Покупка подтверждена', default=False)
    
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # Один отзыв на товар от пользователя
    
    def __str__(self):
        return f"{self.product.name} - {self.user.email} - {self.rating}★"
    
    def save(self, *args, **kwargs):
        # Проверяем, покупал ли пользователь этот товар
        if not self.pk:  # Только при создании
            self.is_purchased = Order.objects.filter(
                user=self.user,
                items__product=self.product,
                status='delivered'
            ).exists()
        super().save(*args, **kwargs)


class ReviewImage(models.Model):
    """Изображения к отзыву"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='reviews/'
    )
    
    class Meta:
        verbose_name = 'Изображение отзыва'
        verbose_name_plural = 'Изображения отзывов'
    
    def __str__(self):
        return f"Изображение к отзыву {self.review.id}"


class ReviewVote(models.Model):
    """Голосование за полезность отзыва"""
    VOTE_CHOICES = [
        ('like', 'Полезно'),
        ('dislike', 'Бесполезно'),
    ]
    
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_votes'
    )
    vote = models.CharField('Голос', max_length=10, choices=VOTE_CHOICES)
    created_at = models.DateTimeField('Дата', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Голос за отзыв'
        verbose_name_plural = 'Голоса за отзывы'
        unique_together = ['review', 'user']