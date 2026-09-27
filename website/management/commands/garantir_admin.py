"""Garante que o administrador definido no .env exista, com a senha do .env."""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ('Cria (ou atualiza) o superusuário a partir de DJANGO_ADMIN_USER, DJANGO_ADMIN_PASSWORD '
            'e DJANGO_ADMIN_EMAIL. Sem essas variáveis, não faz nada.')

    def handle(self, *args, **options):
        usuario = os.environ.get('DJANGO_ADMIN_USER', '').strip()
        senha = os.environ.get('DJANGO_ADMIN_PASSWORD', '')
        email = os.environ.get('DJANGO_ADMIN_EMAIL', '').strip()
        if not usuario or not senha:
            self.stdout.write('DJANGO_ADMIN_USER/DJANGO_ADMIN_PASSWORD não definidos; administrador não alterado.')
            return

        User = get_user_model()
        user, criado = User._default_manager.get_or_create(username=usuario)
        alterado = criado or not (user.is_active and user.is_staff and user.is_superuser)
        user.is_active = user.is_staff = user.is_superuser = True
        if email and user.email != email:
            user.email = email
            alterado = True
        # Só troca a senha se for diferente, para não derrubar as sessões abertas a cada reinício.
        if not user.check_password(senha):
            user.set_password(senha)
            alterado = True
        if alterado:
            user.save()
        self.stdout.write('Administrador "%s" %s.' % (usuario, 'criado' if criado else
                                                      'atualizado' if alterado else 'já está em dia'))
