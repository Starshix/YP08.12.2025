from django.db import models
from django.conf import settings
from catalog.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                              related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                           on_delete=models.CASCADE)
    rating = models.PositiveIntegerField('Рейтинг', 
                                       validators=[MinValueValidator(1), 
                                                 MaxValueValidator(5)])
    text = models.TextField('Отзыв')
    advantages = models.TextField('Достоинства', blank=True)
    disadvantages = models.TextField('Недостатки', blank=True)
    is_verified = models.BooleanField('Проверенный', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ['product', 'user']
    
    def __str__(self):
        return f"Отзыв от {self.user} на {self.product}"
    
    @property
    def get_stars(self):
        return range(self.rating)
    
    @property
    def get_empty_stars(self):
        return range(5 - self.rating)