"""Copia os dados do banco SQLite da versão anterior para o PostgreSQL.

Só age quando o banco padrão não é SQLite, o alias `legado` está configurado (variável
DJANGO_SQLITE_LEGADO apontando para um arquivo existente) e o banco novo ainda não tem dados.
Os registros são copiados com as mesmas chaves primárias, de modo que usuários, senhas, sessões,
permissões, histórico do admin, mensagens, candidaturas e relatos continuam idênticos.

O SQLite legado precisa estar com o esquema atualizado antes (o docker-entrypoint.sh roda
`migrate --database=legado` primeiro); nele esta migration não faz nada.
"""
from django.core.management.color import no_style
from django.db import connections, migrations

LEGADO = 'legado'

# Em ordem de dependência (chaves estrangeiras). Tuplas de 3 itens são tabelas many-to-many.
TABELAS = [
    ('contenttypes', 'ContentType'),
    ('auth', 'Permission'),
    ('auth', 'Group'),
    ('auth', 'Group', 'permissions'),
    ('auth', 'User'),
    ('auth', 'User', 'groups'),
    ('auth', 'User', 'user_permissions'),
    ('admin', 'LogEntry'),
    ('sessions', 'Session'),
    ('website', 'MensagemContato'),
    ('website', 'Candidatura'),
    ('website', 'RelatoIntegridade'),
]

# Tabelas que o post_migrate do Django pode ter preenchido; são recriadas com os IDs do legado.
RECRIAVEIS = {('contenttypes', 'ContentType'), ('auth', 'Permission'), ('auth', 'Group', 'permissions')}


def _modelo(apps, item):
    model = apps.get_model(item[0], item[1])
    if len(item) == 3:
        return model._meta.get_field(item[2]).remote_field.through
    return model


def importar_sqlite(apps, schema_editor):
    destino = schema_editor.connection
    if destino.alias != 'default' or destino.vendor == 'sqlite' or LEGADO not in connections.settings:
        return

    modelos = [(item, _modelo(apps, item)) for item in TABELAS]

    if not modelos[0][1].objects.using(LEGADO).exists():
        print('\n  SQLite legado sem dados; nada a importar.')
        return
    ocupadas = [m._meta.db_table for item, m in modelos
                if item not in RECRIAVEIS and m.objects.using(destino.alias).exists()]
    if ocupadas:
        print('\n  PostgreSQL já possui dados (%s); importação do SQLite ignorada.' % ', '.join(ocupadas))
        return

    # Apaga tipos de conteúdo/permissões criados automaticamente (cascata para as permissões).
    for item, model in reversed(modelos):
        if item in RECRIAVEIS:
            model.objects.using(destino.alias).all().delete()

    print()
    for item, model in modelos:
        # Mantém as datas originais (ex.: criado_em), que o auto_now_add sobrescreveria.
        # Os modelos históricos existem só durante esta migration, então alterá-los é seguro.
        for f in model._meta.concrete_fields:
            if getattr(f, 'auto_now_add', False) or getattr(f, 'auto_now', False):
                f.auto_now_add = f.auto_now = False
        campos = [f.attname for f in model._meta.concrete_fields]
        # vars() pega o valor bruto (ex.: o caminho do currículo em vez de um FieldFile).
        novos = [model(**{c: vars(obj)[c] for c in campos})
                 for obj in model.objects.using(LEGADO).order_by('pk').iterator()]
        model.objects.using(destino.alias).bulk_create(novos, batch_size=500)
        print('  %-35s %d registro(s)' % (model._meta.db_table, len(novos)))

    # Ajusta as sequências para continuar a partir do maior ID importado.
    sql = destino.ops.sequence_reset_sql(no_style(), [m for _, m in modelos])
    with destino.cursor() as cursor:
        for comando in sql:
            cursor.execute(comando)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_redesenho'),
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(importar_sqlite, migrations.RunPython.noop, elidable=True),
    ]
