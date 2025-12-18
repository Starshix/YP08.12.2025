from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from catalog.models import Product
from .cart import Cart
from .forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    

    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override') == 'true'
    

    cart.add(
        product=product, 
        quantity=quantity, 
        override_quantity=override
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Товар добавлен в корзину',
            'cart_total_quantity': len(cart),
            'cart_total_price': str(cart.get_total_price()),
        })
    
    return redirect('catalog:product_list')

@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    

    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override') == 'true'


    cart.add(
        product=product, 
        quantity=quantity, 
        override_quantity=override
    )
    

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Товар добавлен в корзину',
            'cart_total_quantity': len(cart),
            'cart_total_price': str(cart.get_total_price()),
        })
    
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    

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
    
    context = {
        'cart': cart,
    }
    return render(request, 'cart/detail.html', context)


def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Корзина очищена',
            'cart_total_quantity': 0,
            'cart_total_price': '0',
        })
    
    return redirect('cart:cart_detail')