from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, 
                             null=True, blank=True, related_name='children')
    image = models.ImageField('Изображение', upload_to='categories/', null=True, blank=True)
    description = models.TextField('Описание', blank=True)
    order = models.IntegerField('Порядок', default=0)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        # Генерируем slug только если он пустой
        if not self.slug or self.slug.strip() == '':
            # Создаем slug из имени
            if self.name:
                base_slug = slugify(self.name)
                
                # Если slugify вернул пустую строку (например, для "123" или спецсимволов)
                if not base_slug:
                    base_slug = f"category-{self.name.lower().replace(' ', '-')}"
                
                self.slug = base_slug
                
                # Проверяем уникальность и добавляем суффикс если нужно
                original_slug = self.slug
                counter = 1
                
                # Используем while True с выходом по break
                while True:
                    # Проверяем, существует ли уже такой slug
                    exists = Category.objects.filter(slug=self.slug)
                    if self.pk:
                        exists = exists.exclude(pk=self.pk)
                    
                    if not exists.exists():
                        break  # Уникальный slug, выходим из цикла
                    
                    # Если slug уже существует, добавляем суффикс
                    self.slug = f"{original_slug}-{counter}"
                    counter += 1
            else:
                # Если имя пустое, создаем временный slug
                self.slug = f"category-{self.pk or 'temp'}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    @property
    def get_all_children(self):
        children = list(self.children.all())
        for child in self.children.all():
            children.extend(child.get_all_children)
        return children

# Сигнал для более надежной генерации slug
@receiver(pre_save, sender=Category)
def generate_category_slug(sender, instance, **kwargs):
    """
    Генерирует slug для категории перед сохранением.
    Работает даже если метод save() не вызывается напрямую.
    """
    if not instance.slug or instance.slug.strip() == '':
        if instance.name:
            base_slug = slugify(instance.name)
            
            # Если slugify вернул пустую строку
            if not base_slug:
                # Преобразуем имя в латиницу или используем транслитерацию
                import re
                # Простая транслитерация для кириллицы
                translit_map = {
                    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
                    'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
                    'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
                    'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
                    'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
                    'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
                    'э': 'e', 'ю': 'yu', 'я': 'ya',
                }
                
                # Конвертируем имя
                name_lower = instance.name.lower()
                result = []
                for char in name_lower:
                    if char in translit_map:
                        result.append(translit_map[char])
                    elif char.isalnum():
                        result.append(char)
                    elif char == ' ':
                        result.append('-')
                
                base_slug = ''.join(result)
                # Убираем лишние дефисы
                base_slug = re.sub(r'-+', '-', base_slug).strip('-')
            
            # Если все еще пусто, используем "category"
            if not base_slug:
                base_slug = "category"
            
            instance.slug = base_slug
            
            # Проверяем уникальность
            original_slug = instance.slug
            counter = 1
            
            while Category.objects.filter(slug=instance.slug).exclude(pk=instance.pk).exists():
                instance.slug = f"{original_slug}-{counter}"
                counter += 1
        else:
            # Если имя пустое, используем временный slug
            instance.slug = f"category-temp"

class Brand(models.Model):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', unique=True)
    logo = models.ImageField('Логотип', upload_to='brands/', null=True, blank=True)
    description = models.TextField('Описание', blank=True)
    
    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    AVAILABILITY_CHOICES = [
        ('in_stock', 'В наличии'),
        ('limited', 'Мало'),
        ('out_of_stock', 'Нет в наличии'),
        ('preorder', 'Под заказ'),
    ]
    
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=200, unique=True, blank=True)  # Добавили blank=True
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                               related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, 
                            related_name='products', null=True, blank=True)
    sku = models.CharField('Артикул', max_length=50, unique=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    old_price = models.DecimalField('Старая цена', max_digits=10, 
                                   decimal_places=2, null=True, blank=True)
    description = models.TextField('Описание')
    features = models.TextField('Характеристики', blank=True)
    availability = models.CharField('Наличие', max_length=20,
                                  choices=AVAILABILITY_CHOICES, default='in_stock')
    quantity = models.IntegerField('Количество', default=0)
    is_active = models.BooleanField('Активный', default=True)
    is_new = models.BooleanField('Новинка', default=False)
    is_sale = models.BooleanField('Распродажа', default=False)
    is_featured = models.BooleanField('Рекомендуемый', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Обновляем наличие в зависимости от количества
        if self.quantity > 10:
            self.availability = 'in_stock'
        elif 1 <= self.quantity <= 10:
            self.availability = 'limited'
        elif self.quantity == 0:
            self.availability = 'out_of_stock'
        
        # Генерируем slug, если он пустой
        if not self.slug or self.slug.strip() == '':
            from django.utils.text import slugify
            
            if self.name:
                # Создаем slug из имени товара
                base_slug = slugify(self.name)
                
                # Если slugify вернул пустую строку
                if not base_slug:
                    # Используем транслитерацию как для категорий
                    import re
                    translit_map = {
                        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
                        'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
                        'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
                        'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
                        'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
                        'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
                        'э': 'e', 'ю': 'yu', 'я': 'ya',
                    }
                    
                    name_lower = self.name.lower()
                    result = []
                    for char in name_lower:
                        if char in translit_map:
                            result.append(translit_map[char])
                        elif char.isalnum():
                            result.append(char)
                        elif char == ' ':
                            result.append('-')
                    
                    base_slug = ''.join(result)
                    base_slug = re.sub(r'-+', '-', base_slug).strip('-')
                
                # Если все еще пусто, используем sku
                if not base_slug:
                    base_slug = slugify(self.sku) if self.sku else f"product-{self.pk or 'temp'}"
                
                self.slug = base_slug
                
                # Проверяем уникальность slug
                original_slug = self.slug
                counter = 1
                
                while Product.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                    self.slug = f"{original_slug}-{counter}"
                    counter += 1
            else:
                # Если имя пустое, используем sku
                self.slug = slugify(self.sku) if self.sku else f"product-{self.pk or 'temp'}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0
    
    @property
    def main_image(self):
        image = self.images.filter(is_main=True).first()
        if image:
            return image.image
        return None
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                              related_name='images')
    image = models.ImageField('Изображение', upload_to='products/')
    is_main = models.BooleanField('Основное', default=False)
    order = models.IntegerField('Порядок', default=0)
    
    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['is_main', 'order']
    
    def __str__(self):
        return f"Изображение {self.product.name}"
    
    def save(self, *args, **kwargs):
        if self.is_main:
            # Убираем флаг is_main у других изображений этого товара
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)