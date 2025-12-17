from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Пытаемся найти пользователя по email или username
            user = UserModel.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except UserModel.DoesNotExist:
            # Если пользователь не найден, создаем новый
            UserModel().set_password(password)
            return None
        except UserModel.MultipleObjectsReturned:
            # Если найдено несколько пользователей, берем первого
            user = UserModel.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()
        
        # Проверяем пароль и разрешения
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None