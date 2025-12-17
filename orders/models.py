from django.db import models
from django.conf import settings
from catalog.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    PAYMENT_CHOICES = [
        ('card', 'Карта онлайн'),
        ('cash', 'Наличные при получении'),
        ('bank', 'Банковский перевод'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                           on_delete=models.CASCADE, 
                           related_name='orders', null=True, blank=True)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20)
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    address = models.TextField('Адрес доставки')
    city = models.CharField('Город', max_length=100)
    postal_code = models.CharField('Почтовый индекс', max_length=20)
    status = models.CharField('Статус', max_length=20, 
                            choices=STATUS_CHOICES, default='new')
    payment_method = models.CharField('Способ оплаты', max_length=20,
                                    choices=PAYMENT_CHOICES)
    total_price = models.DecimalField('Общая сумма', max_digits=10, 
                                    decimal_places=2)
    notes = models.TextField('Примечания', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.email}"
    
    @property
    def get_status_display_class(self):
        status_classes = {
            'new': 'badge badge-primary',
            'processing': 'badge badge-info',
            'shipped': 'badge badge-warning',
            'delivered': 'badge badge-success',
            'cancelled': 'badge badge-danger',
        }
        return status_classes.get(self.status, 'badge badge-secondary')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, 
                            related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)
    
    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.price * self.quantity