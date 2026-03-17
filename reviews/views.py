from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.views.decorators.http import require_POST
from catalog.models import Product
from orders.models import Order
from .models import Review, ReviewVote
from .forms import ReviewForm, ReviewImageForm

@login_required
def add_review(request, product_id):
    """Добавление отзыва к товару"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Проверяем, не оставлял ли пользователь уже отзыв
    existing_review = Review.objects.filter(
        product=product,
        user=request.user
    ).first()
    
    if existing_review:
        messages.warning(request, 'Вы уже оставили отзыв на этот товар')
        return redirect('catalog:product_detail', slug=product.slug)
    
    # Проверяем, покупал ли пользователь этот товар
    purchased_order = Order.objects.filter(
        user=request.user,
        items__product=product,
        status='delivered'
    ).exists()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_purchased = purchased_order
            review.save()
            
            messages.success(
                request, 
                'Спасибо за ваш отзыв! Он будет опубликован после проверки модератором.'
            )
            return redirect('catalog:product_detail', slug=product.slug)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/add_review.html', {
        'form': form,
        'product': product,
        'purchased': purchased_order
    })


@login_required
def edit_review(request, review_id):
    """Редактирование отзыва"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв успешно обновлен')
            return redirect('catalog:product_detail', slug=review.product.slug)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'reviews/edit_review.html', {
        'form': form,
        'review': review
    })


@login_required
def delete_review(request, review_id):
    """Удаление отзыва"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        product_slug = review.product.slug
        review.delete()
        messages.success(request, 'Отзыв успешно удален')
        return redirect('catalog:product_detail', slug=product_slug)
    
    return render(request, 'reviews/delete_review.html', {'review': review})


@require_POST
@login_required
def vote_review(request, review_id):
    """Голосование за полезность отзыва"""
    review = get_object_or_404(Review, id=review_id)
    vote_type = request.POST.get('vote')
    
    if vote_type not in ['like', 'dislike']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    
    # Проверяем существующий голос
    existing_vote = ReviewVote.objects.filter(
        review=review,
        user=request.user
    ).first()
    
    if existing_vote:
        if existing_vote.vote == vote_type:
            # Удаляем голос (передумал)
            existing_vote.delete()
            action = 'removed'
        else:
            # Меняем голос
            existing_vote.vote = vote_type
            existing_vote.save()
            action = 'changed'
    else:
        # Создаем новый голос
        ReviewVote.objects.create(
            review=review,
            user=request.user,
            vote=vote_type
        )
        action = 'added'
    
    # Получаем обновленную статистику с использованием Q
    stats = review.votes.aggregate(
        likes=Count('id', filter=Q(vote='like')),
        dislikes=Count('id', filter=Q(vote='dislike'))
    )
    
    return JsonResponse({
        'success': True,
        'action': action,
        'likes': stats['likes'],
        'dislikes': stats['dislikes']
    })


def product_reviews(request, product_id):
    """AJAX запрос для подгрузки отзывов"""
    try:
        product = get_object_or_404(Product, id=product_id)
        page = int(request.GET.get('page', 1))
        per_page = 5
        
        reviews = Review.objects.filter(
            product=product,
            # is_approved=True
        ).select_related('user').prefetch_related('images', 'votes')
        
        # Статистика
        stats = reviews.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        # Распределение оценок
        rating_distribution = []
        for i in range(5, 0, -1):
            count = reviews.filter(rating=i).count()
            percent = (count / stats['total_reviews'] * 100) if stats['total_reviews'] > 0 else 0
            rating_distribution.append({
                'stars': i,
                'count': count,
                'percent': round(percent, 1)
            })
        
        # Пагинация
        start = (page - 1) * per_page
        end = start + per_page
        paginated_reviews = reviews[start:end]
        
        # Формируем HTML
        html = render(request, 'reviews/review_list_partial.html', {
            'reviews': paginated_reviews
        }).content.decode('utf-8')
        
        return JsonResponse({
            'success': True,
            'html': html,
            'has_next': reviews.count() > end,
            'stats': {
                'avg_rating': round(stats['avg_rating'] or 0, 1),
                'total_reviews': stats['total_reviews'],
                'distribution': rating_distribution
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)