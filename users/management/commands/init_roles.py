from django.core.management.base import BaseCommand
from django.apps import apps  # Добавляем импорт
from django.contrib.auth.models import Permission, ContentType
from django.contrib.auth.management import create_permissions
from users.models import Role, User

class Command(BaseCommand):
    help = 'Инициализация ролей и прав доступа'
    
    def handle(self, *args, **kwargs):
        # Создаём разрешения для всех приложений
        for app_config in apps.get_app_configs():
            app_config.models_module = True
            create_permissions(app_config, verbosity=0)
            app_config.models_module = None
        
        # Получаем все разрешения
        permissions = Permission.objects.all()
        
        # Создаём роли с правами
        
        # 1. Покупатель (Customer)
        customer_role, created = Role.objects.get_or_create(
            name='customer',
            defaults={'description': 'Обычный покупатель магазина'}
        )
        
        # Права для покупателя (только просмотр и создание своих данных)
        customer_perms = permissions.filter(
            codename__in=[
                # Заказы - только свои
                'add_order', 'change_order', 'view_order', 'delete_order',
                # Отзывы - только свои
                'add_review', 'change_review', 'delete_review', 'view_review',
                # Просмотр каталога
                'view_product', 'view_category', 'view_brand',
                # Профиль
                'change_user', 'view_user',
            ]
        )
        customer_role.permissions.set(customer_perms)
        
        # 2. Менеджер (Manager)
        manager_role, created = Role.objects.get_or_create(
            name='manager',
            defaults={'description': 'Менеджер по продажам'}
        )
        
        # Права для менеджера
        manager_perms = permissions.filter(
            codename__in=[
                # Заказы - все
                'view_order', 'change_order', 'delete_order',
                # Пользователи - просмотр
                'view_user', 'change_user',
                # Товары - просмотр
                'view_product', 'view_category', 'view_brand',
                # Создание товаров
                'add_product', 'change_product',
            ]
        )
        manager_role.permissions.set(manager_perms)
        
        # 3. Контент-менеджер (Content Manager)
        content_manager_role, created = Role.objects.get_or_create(
            name='content_manager',
            defaults={'description': 'Редактор контента'}
        )
        
        # Права для контент-менеджера
        content_manager_perms = permissions.filter(
            codename__in=[
                # Товары - полный доступ
                'add_product', 'change_product', 'delete_product', 'view_product',
                # Категории - полный доступ
                'add_category', 'change_category', 'delete_category', 'view_category',
                # Бренды - полный доступ
                'add_brand', 'change_brand', 'delete_brand', 'view_brand',
                # Страницы - полный доступ
                'add_page', 'change_page', 'delete_page', 'view_page',
                # Отзывы - модерация
                'view_review', 'change_review', 'delete_review',
                # Контакты
                'view_contact', 'change_contact', 'delete_contact',
            ]
        )
        content_manager_role.permissions.set(content_manager_perms)
        
        # 4. Администратор (Admin)
        admin_role, created = Role.objects.get_or_create(
            name='admin',
            defaults={'description': 'Полный доступ к системе'}
        )
        
        # Права для администратора (все права)
        admin_role.permissions.set(permissions)
        
        self.stdout.write(self.style.SUCCESS('✅ Роли успешно созданы и настроены!'))
        
        # Назначаем роль админа суперпользователям
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            if not user.role:
                user.role = admin_role
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Пользователю {user.email} назначена роль администратора')
                )
        
        # Создаём тестовых пользователей для каждой роли (если не существуют)
        self.create_test_users(customer_role, manager_role, content_manager_role, admin_role)
        
        self.stdout.write(self.style.SUCCESS('✅ Инициализация ролей завершена успешно!'))
    
    def create_test_users(self, customer_role, manager_role, content_role, admin_role):
        """Создание тестовых пользователей для каждой роли"""
        from django.contrib.auth.hashers import make_password
        
        test_users = [
            {
                'email': 'customer@gearlock.ru',
                'username': 'customer',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'password': 'customer123',
                'role': customer_role,
            },
            {
                'email': 'manager@gearlock.ru',
                'username': 'manager',
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'password': 'manager123',
                'role': manager_role,
            },
            {
                'email': 'content@gearlock.ru',
                'username': 'content',
                'first_name': 'Алексей',
                'last_name': 'Иванов',
                'password': 'content123',
                'role': content_role,
            },
            {
                'email': 'admin@gearlock.ru',
                'username': 'admin',
                'first_name': 'Администратор',
                'last_name': 'Системы',
                'password': 'admin123',
                'role': admin_role,
            },
        ]
        
        for user_data in test_users:
            if not User.objects.filter(email=user_data['email']).exists():
                user = User.objects.create(
                    email=user_data['email'],
                    username=user_data['username'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    password=make_password(user_data['password']),
                    is_active=True,
                    is_staff=user_data['role'] in [admin_role, content_role, manager_role]
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Создан тестовый пользователь: {user.email} '
                        f'({user.role.get_name_display()}) '
                        f'пароль: {user_data["password"]}'
                    )
                )