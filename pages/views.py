from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Page, Contact
from .forms import ContactForm

def about(request):
    page = Page.objects.filter(slug='about').first()
    return render(request, 'pages/about.html', {'page': page})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время.')
            return redirect('pages:contact')  # Теперь redirect работает
    else:
        form = ContactForm()
    
    return render(request, 'pages/contact.html', {'form': form})

def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    return render(request, 'pages/page_detail.html', {'page': page})