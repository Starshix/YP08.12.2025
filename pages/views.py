from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from users.decorators import manager_required
from .models import Page, Contact
from .forms import ContactForm
from django.db.models import Avg, Count, Q

def about(request):
    page = Page.objects.filter(slug='about').first()
    return render(request, 'pages/about.html', {'page': page})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время.')
            return redirect('pages:contact')
    else:
        form = ContactForm()
    
    return render(request, 'pages/contact.html', {'form': form})

def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    return render(request, 'pages/page_detail.html', {'page': page})


@login_required
@manager_required
def message_list(request):
    """Список всех сообщений для менеджера"""
    messages_list = Contact.objects.all().order_by('-created_at')
    
    # Фильтрация по статусу
    status = request.GET.get('status')
    if status == 'read':
        messages_list = messages_list.filter(is_read=True)
    elif status == 'unread':
        messages_list = messages_list.filter(is_read=False)
    
    # Поиск
    search = request.GET.get('search')
    if search:
        messages_list = messages_list.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(subject__icontains=search) |
            Q(message__icontains=search)
        )
    
    # Пагинация
    paginator = Paginator(messages_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Статистика
    total_messages = Contact.objects.count()
    unread_count = Contact.objects.filter(is_read=False).count()
    read_count = Contact.objects.filter(is_read=True).count()
    
    context = {
        'page_obj': page_obj,
        'total_messages': total_messages,
        'unread_count': unread_count,
        'read_count': read_count,
        'current_status': status,
        'search_query': search or '',
    }
    return render(request, 'pages/message_list.html', context)


@login_required
@manager_required
def message_detail(request, message_id):
    """Детальный просмотр сообщения"""
    message = get_object_or_404(Contact, id=message_id)
    
    # Отмечаем как прочитанное при просмотре
    if not message.is_read:
        message.is_read = True
        message.save()
    
    # Получаем предыдущее и следующее сообщение
    prev_message = Contact.objects.filter(id__lt=message.id).order_by('-id').first()
    next_message = Contact.objects.filter(id__gt=message.id).order_by('id').first()
    
    context = {
        'message': message,
        'prev_message': prev_message,
        'next_message': next_message,
    }
    return render(request, 'pages/message_detail.html', context)


@login_required
@manager_required
def message_mark_read(request, message_id):
    """Отметить сообщение как прочитанное"""
    message = get_object_or_404(Contact, id=message_id)
    message.is_read = True
    message.save()
    messages.success(request, f'Сообщение от {message.name} отмечено как прочитанное')
    return redirect('pages:message_list')


@login_required
@manager_required
def message_mark_unread(request, message_id):
    """Отметить сообщение как непрочитанное"""
    message = get_object_or_404(Contact, id=message_id)
    message.is_read = False
    message.save()
    messages.success(request, f'Сообщение от {message.name} отмечено как непрочитанное')
    return redirect('pages:message_list')


@login_required
@manager_required
def message_delete(request, message_id):
    """Удаление сообщения"""
    message = get_object_or_404(Contact, id=message_id)
    name = message.name
    message.delete()
    messages.success(request, f'Сообщение от {name} удалено')
    return redirect('pages:message_list')


@login_required
@manager_required
def message_bulk_action(request):
    """Массовые действия с сообщениями"""
    if request.method == 'POST':
        action = request.POST.get('action')
        message_ids = request.POST.getlist('selected_messages')
        
        if not message_ids:
            messages.warning(request, 'Не выбрано ни одного сообщения')
            return redirect('pages:message_list')
        
        if action == 'mark_read':
            Contact.objects.filter(id__in=message_ids).update(is_read=True)
            messages.success(request, f'{len(message_ids)} сообщений отмечено как прочитанные')
        
        elif action == 'mark_unread':
            Contact.objects.filter(id__in=message_ids).update(is_read=False)
            messages.success(request, f'{len(message_ids)} сообщений отмечено как непрочитанные')
        
        elif action == 'delete':
            Contact.objects.filter(id__in=message_ids).delete()
            messages.success(request, f'{len(message_ids)} сообщений удалено')
        
    return redirect('pages:message_list')