# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('', views.order_list, name='order_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('all/', views.all_orders, name='all_orders'),
    
    # Новые маршруты для менеджера
    path('manager/<int:order_id>/', views.order_detail_manager, name='order_detail_manager'),
    path('manager/<int:order_id>/update/', views.order_update, name='order_update'),
    path('manager/<int:order_id>/change-status/', views.change_order_status, name='change_order_status'),
]