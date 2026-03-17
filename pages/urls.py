from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Управление сообщениями для менеджера
    path('messages/', views.message_list, name='message_list'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/<int:message_id>/read/', views.message_mark_read, name='message_mark_read'),
    path('messages/<int:message_id>/unread/', views.message_mark_unread, name='message_mark_unread'),
    path('messages/<int:message_id>/delete/', views.message_delete, name='message_delete'),
    path('messages/bulk-action/', views.message_bulk_action, name='message_bulk_action'),
]