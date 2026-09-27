#!/bin/sh
set -e
# Atualiza o esquema do SQLite da versão anterior (se existir) para que a migration
# website.0003 consiga copiar os dados dele para o PostgreSQL.
if [ -n "$DJANGO_SQLITE_LEGADO" ] && [ -f "$DJANGO_SQLITE_LEGADO" ]; then
    python manage.py migrate --database=legado --noinput
fi
python manage.py migrate --noinput
python manage.py garantir_admin
exec "$@"
