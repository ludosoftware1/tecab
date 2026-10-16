"""Garante o grupo "Gestão ANP" e o usuário inicial do painel de movimentação ANP definido no .env."""
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

GRUPO = 'Gestão ANP'
PERMISSOES = ['view_movimentacaoanp', 'add_movimentacaoanp', 'change_movimentacaoanp', 'delete_movimentacaoanp',
              'view_produtoanp']


class Command(BaseCommand):
    help = ('Cria o grupo "%s" (ver, lançar, importar e exportar a movimentação ANP) e cria/atualiza o usuário '
            'TECAB_ANP_USER / TECAB_ANP_PASSWORD / TECAB_ANP_EMAIL nesse grupo. Sem as variáveis, só garante o grupo. '
            'Para autorizar outras pessoas, inclua-as no grupo pelo /admin/.' % GRUPO)

    def handle(self, *args, **options):
        grupo, _ = Group.objects.get_or_create(name=GRUPO)
        perms = Permission.objects.filter(content_type__app_label='website', codename__in=PERMISSOES)
        grupo.permissions.add(*perms)
        self.stdout.write('Grupo "%s" com %d permissões.' % (GRUPO, perms.count()))

        usuario = os.environ.get('TECAB_ANP_USER', '').strip()
        senha = os.environ.get('TECAB_ANP_PASSWORD', '')
        email = os.environ.get('TECAB_ANP_EMAIL', '').strip()
        if not usuario or not senha:
            self.stdout.write('TECAB_ANP_USER/TECAB_ANP_PASSWORD não definidos; usuário da gestão ANP não alterado.')
            return

        User = get_user_model()
        user, criado = User._default_manager.get_or_create(username=usuario, defaults={'first_name': 'Gestão ANP'})
        alterado = criado or not user.is_active
        user.is_active = True
        if email and user.email != email:
            user.email = email
            alterado = True
        # Só troca a senha se for diferente, para não derrubar as sessões abertas a cada reinício.
        if not user.check_password(senha):
            user.set_password(senha)
            alterado = True
        if alterado:
            user.save()
        user.groups.add(grupo)
        self.stdout.write('Usuário da gestão ANP "%s" %s.' % (usuario, 'criado' if criado else
                                                              'atualizado' if alterado else 'já está em dia'))
