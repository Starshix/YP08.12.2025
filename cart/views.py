# cart/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from catalog.models import Product
from .cart import Cart

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    # Получаем количество из формы
    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override') == 'true'
    
    # Добавляем товар в корзину
    success, message = cart.add(
        product=product, 
        quantity=quantity, 
        override_quantity=override,
        show_messages=False  # Не показываем сообщения здесь, сделаем это ниже
    )
    
    # Для AJAX запросов
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_total_quantity': len(cart),
                'cart_total_price': str(cart.get_total_price()),
                'available_quantity': product.quantity,
                'in_cart_quantity': cart.get_item_quantity(product.id),
            })
        else:
            return JsonResponse({
                'success': False,
                'message': message,
                'cart_total_quantity': len(cart),
                'cart_total_price': str(cart.get_total_price()),
                'available_quantity': product.quantity,
                'in_cart_quantity': cart.get_item_quantity(product.id),
            }, status=400)
    
    # Для обычных запросов
    if success:
        messages.success(request, message)
        # Возвращаем на ту же страницу
        referer = request.META.get('HTTP_REFERER', 'cart:cart_detail')
        return redirect(referer)
    else:
        messages.error(request, message)
        return redirect('catalog:product_detail', slug=product.slug)

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    quantity = int(request.POST.get('quantity', 1))
    override = True  # При обновлении всегда перезаписываем
    
    success, message = cart.add(
        product=product, 
        quantity=quantity, 
        override_quantity=override,
        show_messages=False
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if success:
            return JsonResponse({
                'success': True,
                'message': message,
                'cart_total_quantity': len(cart),
                'cart_total_price': str(cart.get_total_price()),
                'available_quantity': product.quantity,
                'in_cart_quantity': cart.get_item_quantity(product.id),
            })
        else:
            return JsonResponse({
                'success': False,
                'message': message,
                'cart_total_quantity': len(cart),
                'cart_total_price': str(cart.get_total_price()),
                'available_quantity': product.quantity,
                'in_cart_quantity': cart.get_item_quantity(product.id),
            }, status=400)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    cart.remove(product)
    messages.success(request, f'Товар "{product.name}" удален из корзины')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Товар удален из корзины',
            'cart_total_quantity': len(cart),
            'cart_total_price': str(cart.get_total_price()),
        })
    
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    
    # Проверяем актуальность товаров в корзине
    items_to_remove = []
    for item in cart:
        product = item['product']
        quantity_in_cart = item['quantity']
        
        if product.quantity < quantity_in_cart:
            # Товара стало меньше, чем в корзине
            if product.quantity == 0:
                items_to_remove.append(product)
                messages.warning(request, 
                    f'Товар "{product.name}" больше не доступен и удален из корзины')
            else:
                # Обновляем количество до доступного
                cart.add(product, product.quantity, override_quantity=True)
                messages.warning(request, 
                    f'Количество товара "{product.name}" уменьшено до {product.quantity} шт. (максимально доступное)')
    
    # Удаляем товары, которых больше нет
    for product in items_to_remove:
        cart.remove(product)
    
    context = {
        'cart': cart,
    }
    return render(request, 'cart/detail.html', context)

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Корзина очищена')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Корзина очищена',
            'cart_total_quantity': 0,
            'cart_total_price': '0',
        })
    
    return redirect('cart:cart_detail')