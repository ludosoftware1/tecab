from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class UsernameOrEmailBackend(ModelBackend):
    """Autentica pelo nome de usuário ou pelo e-mail (campo "Login ou E-mail")."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username and '@' in username:
            User = get_user_model()
            user = User._default_manager.filter(email__iexact=username).order_by('pk').first()
            if user is not None:
                username = user.get_username()
        return super().authenticate(request, username=username, password=password, **kwargs)
