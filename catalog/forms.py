from django import forms
from .models import Product, ProductImage, Category

class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Все категории",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'От'})
    )
    
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'До'})
    )
    
    availability = forms.ChoiceField(
        choices=[('', 'Любое наличие')] + Product.AVAILABILITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    in_stock_only = forms.BooleanField(
        required=False,
        label='Только в наличии',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('created_at', 'По новизне'),
            ('price_asc', 'По возрастанию цены'),
            ('price_desc', 'По убыванию цены'),
            ('name', 'По названию'),
            ('quantity_desc', 'Больше товаров сначала'),
        ],
        required=False,
        initial='created_at',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'category', 'brand', 'sku', 'price', 'old_price',
            'description', 'features', 'availability', 'quantity',
            'is_active', 'is_new', 'is_sale', 'is_featured'
        ] 
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL (заполнится автоматически)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Описание товара'}),
            'features': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Характеристики'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'old_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'availability': forms.Select(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Артикул'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['slug'].required = False
        self.fields['slug'].help_text = 'URL-адрес товара. Заполнится автоматически из названия.'

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        slug = cleaned_data.get('slug')
        
        if name and (not slug or slug.strip() == ''):
            from django.utils.text import slugify
            base_slug = slugify(name)
            
            if not base_slug:

                import re
                translit_map = {
                    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
                    'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
                    'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
                    'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
                    'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
                    'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
                    'э': 'e', 'ю': 'yu', 'я': 'ya',
                }
                
                name_lower = name.lower()
                result = []
                for char in name_lower:
                    if char in translit_map:
                        result.append(translit_map[char])
                    elif char.isalnum():
                        result.append(char)
                    elif char == ' ':
                        result.append('-')
                
                base_slug = ''.join(result)
                base_slug = re.sub(r'-+', '-', base_slug).strip('-')
            
            if not base_slug:
                sku = cleaned_data.get('sku', '')
                base_slug = slugify(sku) if sku else "product"
            
            original_slug = base_slug
            counter = 1
            
            while Product.objects.filter(slug=base_slug).exclude(pk=self.instance.pk if self.instance else None).exists():
                base_slug = f"{original_slug}-{counter}"
                counter += 1
            
            cleaned_data['slug'] = base_slug
        
        return cleaned_data

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_main', 'order']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent', 'image', 'description', 'order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Название категории',
                'id': 'id_name'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'URL (заполнится автоматически)',
                'id': 'id_slug'
            }),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Описание категории'
            }),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].help_text = 'URL-адрес категории. Заполнится автоматически из названия.'
        
        if self.instance and self.instance.pk:
            exclude_ids = [self.instance.pk]
            exclude_ids.extend(child.id for child in self.instance.get_all_children)
            self.fields['parent'].queryset = Category.objects.exclude(id__in=exclude_ids)
        else:
            self.fields['parent'].queryset = Category.objects.all()
        
        self.fields['parent'].empty_label = 'Нет (основная категория)'
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        slug = cleaned_data.get('slug')
        
        if name and (not slug or slug.strip() == ''):
            from django.utils.text import slugify
            base_slug = slugify(name)
            
            if not base_slug:
                import re
                name_lower = name.lower()
                translit_result = []
                for char in name_lower:
                    if 'а' <= char <= 'я':

                        translit_dict = {
                            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
                            'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
                            'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
                            'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
                            'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
                            'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
                            'э': 'e', 'ю': 'yu', 'я': 'ya',
                        }
                        translit_result.append(translit_dict.get(char, char))
                    elif char.isalnum():
                        translit_result.append(char)
                    elif char == ' ':
                        translit_result.append('-')
                
                base_slug = ''.join(translit_result)
                base_slug = re.sub(r'-+', '-', base_slug).strip('-')
            
            if not base_slug:
                base_slug = "category"
            

            original_slug = base_slug
            counter = 1
            
            while Category.objects.filter(slug=base_slug).exclude(pk=self.instance.pk if self.instance else None).exists():
                base_slug = f"{original_slug}-{counter}"
                counter += 1
            
            cleaned_data['slug'] = base_slug
        
        return cleaned_data

