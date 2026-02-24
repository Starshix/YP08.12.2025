import pytest
from django.urls import reverse
from django.test import Client
from catalog.models import Product, Category

@pytest.mark.django_db
class TestProductListView:
    """Тесты для представления списка товаров"""
    
    @pytest.fixture
    def client(self):
        """Фикстура клиента"""
        return Client()
    
    @pytest.fixture
    def category(self):
        """Фикстура категории"""
        return Category.objects.create(name="Тестовая категория", slug="test-cat")
    
    @pytest.fixture
    def products(self, category):
        """Фикстура тестовых товаров"""
        products = []
        for i in range(15):
            product = Product.objects.create(
                name=f"Тестовый товар {i}",
                slug=f"test-product-{i}",
                sku=f"TEST-{i:03d}",
                price=1000 + i * 100,
                category=category,
                quantity=10,
                is_active=True
            )
            products.append(product)
        return products
    
    def test_product_list_status_code(self, client, products):
        """Тест доступности страницы каталога"""
        url = reverse('catalog:product_list')
        response = client.get(url)
        assert response.status_code == 200
    
    def test_product_list_template_used(self, client, products):
        """Тест использования правильного шаблона"""
        url = reverse('catalog:product_list')
        response = client.get(url)
        assert 'catalog/product_list.html' in [t.name for t in response.templates]
    
    def test_product_list_context_contains_products(self, client, products):
        """Тест наличия товаров в контексте"""
        url = reverse('catalog:product_list')
        response = client.get(url)
        assert 'products' in response.context
        assert len(response.context['products']) == 12  # Пагинация по 12
    
    def test_product_list_pagination(self, client, products):
        """Тест пагинации"""
        # Первая страница
        url = reverse('catalog:product_list')
        response = client.get(url)
        assert len(response.context['products']) == 12
        
        # Вторая страница
        url = reverse('catalog:product_list') + '?page=2'
        response = client.get(url)
        assert len(response.context['products']) == 3  # Оставшиеся 3 товара
    
    def test_product_list_filter_by_category(self, client, category, products):
        """Тест фильтрации по категории"""
        url = reverse('catalog:category_detail', args=[category.slug])
        response = client.get(url)
        assert response.status_code == 200
        assert response.context['category'] == category
        assert len(response.context['products']) == 12
    
    def test_product_list_search(self, client, products):
        """Тест поиска товаров"""
        url = reverse('catalog:search') + '?q=Тестовый товар 5'
        response = client.get(url)
        assert response.status_code == 200
        assert 'products' in response.context
        # Должен найти товар с номером 5
        assert any(p.name == "Тестовый товар 5" for p in response.context['products'])
    
    def test_inactive_products_not_shown(self, client, category):
        """Тест, что неактивные товары не отображаются"""
        # Создаём активный товар
        active = Product.objects.create(
            name="Активный товар",
            slug="active",
            sku="ACTIVE-001",
            price=1000,
            category=category,
            quantity=10,
            is_active=True
        )
        
        # Создаём неактивный товар
        inactive = Product.objects.create(
            name="Неактивный товар",
            slug="inactive",
            sku="INACTIVE-001",
            price=2000,
            category=category,
            quantity=5,
            is_active=False
        )
        
        url = reverse('catalog:product_list')
        response = client.get(url)
        
        product_names = [p.name for p in response.context['products']]
        assert "Активный товар" in product_names
        assert "Неактивный товар" not in product_names