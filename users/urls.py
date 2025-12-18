from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('customers/', views.customer_list, name='customer_list'),
    

    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('content/dashboard/', views.content_dashboard, name='content_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
]