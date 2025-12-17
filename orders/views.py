from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.cart import Cart
from .models import Order, OrderItem
from .forms import OrderCreateForm
from users.decorators import manager_required
from .forms import OrderUpdateForm

@login_required
def order_create(request):
    cart = Cart(request)
    
    if not cart:
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            
            if request.user.is_authenticated:
                order.user = request.user
            
            order.total_price = cart.get_total_price()
            order.save()
            
            # Сохраняем товары в заказе
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            # Очищаем корзину
            cart.clear()
            
            messages.success(request, f'Заказ #{order.id} успешно оформлен!')
            return redirect('orders:order_detail', order_id=order.id)
    else:
        # Заполняем форму данными пользователя, если он авторизован
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': request.user.phone,
            }
        form = OrderCreateForm(initial=initial_data)
    
    return render(request, 'orders/order_create.html', {
        'cart': cart,
        'form': form
    })

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
@manager_required
def all_orders(request):
    """Все заказы для менеджера с фильтрацией"""
    orders = Order.objects.all().order_by('-created_at')
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Фильтрация по дате
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    return render(request, 'orders/all_orders.html', {'orders': orders})

@login_required
@manager_required
def order_detail_manager(request, order_id):
    """Детальный просмотр заказа для менеджера"""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()
    
    return render(request, 'orders/order_detail_manager.html', {
        'order': order,
        'order_items': order_items,
    })

@login_required
@manager_required
def order_update(request, order_id):
    """Редактирование заказа"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'Заказ #{order.id} успешно обновлен!')
            return redirect('orders:order_detail_manager', order_id=order.id)
    else:
        form = OrderUpdateForm(instance=order)
    
    return render(request, 'orders/order_update.html', {
        'form': form,
        'order': order,
    })

@login_required
@manager_required
def change_order_status(request, order_id):
    """Быстрое изменение статуса заказа"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Статус заказа #{order.id} изменен на {order.get_status_display()}')
    
    return redirect('orders:order_detail_manager', order_id=order.id)