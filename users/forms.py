from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите ваш email'
        })
    )
    username = forms.CharField(
        required=True,
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Придумайте имя пользователя'
        })
    )
    first_name = forms.CharField(
        required=True,
        label='Имя',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите ваше имя'
        })
    )
    last_name = forms.CharField(
        required=False,
        label='Фамилия',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите вашу фамилию'
        })
    )
    phone = forms.CharField(
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите ваш телефон'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Устанавливаем русские метки для полей паролей
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение пароля'
        
        # Устанавливаем атрибуты виджетов
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Придумайте пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Повторите пароль'
        })
        
        # Добавляем русские help_text для паролей
        self.fields['password1'].help_text = '''
        <div class="form-text small mt-1">
            <ul class="mb-0 ps-3">
                <li>Пароль не должен быть слишком похож на другую вашу личную информацию.</li>
                <li>Ваш пароль должен содержать как минимум 8 символов.</li>
                <li>Пароль не должен быть слишком простым и распространенным.</li>
                <li>Пароль не может состоять только из цифр.</li>
            </ul>
        </div>
        '''
        self.fields['password2'].help_text = '''
        <div class="form-text small mt-1">
            Для подтверждения введите, пожалуйста, пароль ещё раз.
        </div>
        '''
        
        # Убираем стандартный help_text Django для username
        self.fields['username'].help_text = ''
    
    def clean_email(self):
        """Валидация email на уникальность"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Устанавливаем роль по умолчанию
        if not user.role:
            from .models import Role
            try:
                customer_role = Role.objects.get(name='customer')
                user.role = customer_role
            except Role.DoesNotExist:
                pass
        
        if commit:
            user.save()
        
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите ваш email'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите ваш пароль'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages['invalid_login'] = 'Неверный email или пароль.'
    
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise forms.ValidationError('Неверный пароль')
            except User.DoesNotExist:
                raise forms.ValidationError('Пользователь с таким email не найден')
            
            self.user_cache = authenticate(
                self.request, 
                username=user.username,  # Используем username для аутентификации
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError('Ошибка аутентификации')
            
            self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'address', 'postal_code', 'birth_date')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Устанавливаем русские метки
        self.fields['username'].label = 'Имя пользователя'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].label = 'Email'
        self.fields['phone'].label = 'Телефон'
        self.fields['address'].label = 'Адрес'
        self.fields['postal_code'].label = 'Почтовый индекс'
        self.fields['birth_date'].label = 'Дата рождения'
        
        # Добавляем placeholder для удобства
        self.fields['username'].widget.attrs['placeholder'] = 'Имя пользователя'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Введите ваше имя'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Введите вашу фамилию'
        self.fields['email'].widget.attrs['placeholder'] = 'Введите ваш email'
        self.fields['phone'].widget.attrs['placeholder'] = 'Введите ваш телефон'
        self.fields['address'].widget.attrs['placeholder'] = 'Введите ваш адрес'
        self.fields['postal_code'].widget.attrs['placeholder'] = 'Введите почтовый индекс'