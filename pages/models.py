from django.db import models

class Page(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL', unique=True)
    content = models.TextField('Содержание')
    is_active = models.BooleanField('Активная', default=True)
    meta_title = models.CharField('Meta заголовок', max_length=200, blank=True)
    meta_description = models.TextField('Meta описание', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    
    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = ['title']
    
    def __str__(self):
        return self.title

class Contact(models.Model):
    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    subject = models.CharField('Тема', max_length=200)
    message = models.TextField('Сообщение')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Контактное сообщение'
        verbose_name_plural = 'Контактные сообщения'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"