from typing import Optional, Any
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.http import HttpRequest
from django.contrib.auth.models import AbstractBaseUser


# Case insensitive for email (Letter Capitals)
class CaseInsensitiveModelBackend(ModelBackend):       
   
    def authenticate(self, request: Optional[HttpRequest], email: Optional[str] = ..., password: Optional[str] = ..., **kwargs: Any) -> Optional[AbstractBaseUser]:
        UserModel = get_user_model()
        if email is None:
            email = kwargs.get(UserModel.EMAIL_FIELD)
        try:
            case_insensitive_email_field = '{}__iexact'.format(UserModel.USERNAME_FIELD)
            user = UserModel._default_manager.get(**{case_insensitive_email_field: email})
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user