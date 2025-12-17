from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.home, name='home'),  # /catalog/
    

    path('products/create/', views.product_create, name='product_create'),  # /catalog/products/create/
    path('products/<slug:slug>/update/', views.product_update, name='product_update'),  # /catalog/products/<slug>/update/
    path('products/<slug:slug>/delete/', views.product_delete, name='product_delete'),  # /catalog/products/<slug>/delete/
    

    path('products/', views.ProductListView.as_view(), name='product_list'),  # /catalog/products/
    path('products/category/<slug:category_slug>/', views.ProductListView.as_view(), name='product_list_by_category'),  # /catalog/products/category/<slug>/
    path('products/brand/<slug:brand_slug>/', views.ProductListView.as_view(), name='product_list_by_brand'),  # /catalog/products/brand/<slug>/
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),  # /catalog/products/<slug>/
    

    path('categories/', views.category_list, name='category_list'),  # /catalog/categories/
    path('categories/create/', views.category_create, name='category_create'),  # /catalog/categories/create/
    path('categories/<slug:slug>/update/', views.category_update, name='category_update'),  # /catalog/categories/<slug>/update/
    path('categories/<slug:slug>/delete/', views.category_delete, name='category_delete'),  # /catalog/categories/<slug>/delete/
    path('categories/<slug:slug>/', views.category_detail_slug, name='category_detail'),  # /catalog/categories/<slug>/
    
    path('search/', views.SearchView.as_view(), name='search'),  # /catalog/search/
]