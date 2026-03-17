from django import forms
from .models import Review, ReviewImage

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'advantages', 'disadvantages']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'rating-input'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Краткое описание вашего опыта'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Расскажите подробнее о товаре...'
            }),
            'advantages': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Что понравилось?'
            }),
            'disadvantages': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Что не понравилось?'
            }),
        }
        labels = {
            'rating': 'Оценка',
            'title': 'Заголовок отзыва',
            'comment': 'Комментарий',
            'advantages': 'Достоинства',
            'disadvantages': 'Недостатки',
        }
        help_texts = {
            'rating': 'Оцените товар от 1 до 5 звезд',
        }


class ReviewImageForm(forms.ModelForm):
    class Meta:
        model = ReviewImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }