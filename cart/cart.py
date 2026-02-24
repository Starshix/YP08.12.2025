# cart/cart.py
from django.conf import settings
from catalog.models import Product
from django.contrib import messages

class Cart:
    def __init__(self, request):
        self.session = request.session
        self.request = request
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, override_quantity=False, show_messages=True):
        product_id = str(product.id)
        
        available_quantity = product.quantity
        
        if product_id in self.cart:
            if override_quantity:
                # Если перезаписываем количество
                if quantity > available_quantity:
                    message = f'Доступно только {available_quantity} шт. товара "{product.name}"'
                    if show_messages and self.request:
                        messages.error(self.request, message)
                    return False, message
                self.cart[product_id]['quantity'] = quantity
                message = f'Количество товара "{product.name}" обновлено'
            else:
                # Если добавляем к существующему
                current_quantity = self.cart[product_id]['quantity']
                new_quantity = current_quantity + quantity
                
                if new_quantity > available_quantity:
                    message = (f'Доступно только {available_quantity} шт. товара "{product.name}". '
                              f'У вас уже {current_quantity} шт. в корзине.')
                    if show_messages and self.request:
                        messages.error(self.request, message)
                    return False, message
                
                self.cart[product_id]['quantity'] = new_quantity
                message = f'Товар "{product.name}" добавлен в корзину'
        else:
            # Если товара еще нет в корзине
            if quantity > available_quantity:
                message = f'Доступно только {available_quantity} шт. товара "{product.name}"'
                if show_messages and self.request:
                    messages.error(self.request, message)
                return False, message
            
            self.cart[product_id] = {
                'quantity': quantity,
                'price': str(product.price),
                'name': product.name  # Сохраняем имя для сообщений
            }
            message = f'Товар "{product.name}" добавлен в корзину'
        
        self.save()
        if show_messages and self.request:
            messages.success(self.request, message)
        return True, message
    
    def save(self):
        self.session.modified = True
    
    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()
    
    def get_total_price(self):
        return sum(
            float(item['price']) * item['quantity'] 
            for item in self.cart.values()
        )
    
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['total_price'] = float(item['price']) * item['quantity']
            yield item
    
    def get_item_quantity(self, product_id):
        """Получить количество товара в корзине"""
        product_id = str(product_id)
        return self.cart.get(product_id, {}).get('quantity', 0)