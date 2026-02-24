from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Role(models.Model):
    """Кастомные роли пользователей"""
    ROLE_CHOICES = [
        ('customer', 'Покупатель'),
        ('manager', 'Менеджер'),
        ('content_manager', 'Контент-менеджер'),
        ('admin', 'Администратор'),
    ]
    
    name = models.CharField('Название', max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField('Описание', blank=True)
    permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='Права доступа',
        blank=True,
        related_name='roles'
    )
    
    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):

    email = models.EmailField(_('email address'), unique=True)
    

    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Роль',
        related_name='users'
    )
    

    phone = models.CharField('Телефон', max_length=20, blank=True)
    address = models.TextField('Адрес', blank=True)

    postal_code = models.CharField('Почтовый индекс', max_length=20, blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.email
    
    @property
    def is_customer(self):
        return self.role and self.role.name == 'customer'
    
    @property
    def is_manager(self):
        return self.role and self.role.name == 'manager'
    
    @property
    def is_content_manager(self):
        return self.role and self.role.name == 'content_manager'
    
    @property
    def is_admin_user(self):
        return self.role and self.role.name == 'admin'
    
    def get_all_permissions(self):
        """Получить все права пользователя (роль + личные)"""
        permissions = set()
        
        if self.role:
            permissions.update(self.role.permissions.all())
        
        permissions.update(self.user_permissions.all())
        

        for group in self.groups.all():
            permissions.update(group.permissions.all())
        
        return permissions
    
def has_perm(self, perm, obj=None):
    """Проверка прав доступа"""
    if self.is_superuser:
        return True
    

    if '.' in perm:

        codename = perm.split('.')[1]
    else:
        codename = perm
    

    if self.role:

        if self.role.permissions.filter(codename=codename).exists():
            return True
        

        for group in self.role.groups.all():
            if group.permissions.filter(codename=codename).exists():
                return True
    

    if self.user_permissions.filter(codename=codename).exists():
        return True
    

    for group in self.groups.all():
        if group.permissions.filter(codename=codename).exists():
            return True
    

    return super().has_perm(perm, obj)

