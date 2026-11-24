"""Carrega o histórico de movimentação publicado até setembro/2026 (planilha "Histórico de movimentação").

Só age no banco padrão e com a tabela vazia, para não duplicar dados nem interferir na cópia do SQLite
legado (website.0003). Novas planilhas são importadas pelo painel ou por `manage.py importar_movimentacoes_anp`.
"""
import csv
import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
from pathlib import Path

from django.db import migrations

ARQUIVO = Path(__file__).resolve().parent.parent / 'data' / 'movimentacoes-anp-inicial.csv'
# "Atualizado em" (célula B1) da planilha de origem.
ATUALIZADO_EM = datetime.datetime(2026, 10, 2, 12, 0, tzinfo=ZoneInfo('America/Fortaleza'))


def carregar(apps, schema_editor):
    if schema_editor.connection.alias != 'default':
        return
    Produto = apps.get_model('website', 'ProdutoANP')
    Movimentacao = apps.get_model('website', 'MovimentacaoANP')
    if Movimentacao.objects.exists():
        return
    produtos, objetos = {}, []
    with open(ARQUIVO, encoding='utf-8', newline='') as fh:
        for linha in csv.DictReader(fh):
            chave = (int(linha['codigo_anp_do_produto']), linha['descricao_do_produto'].strip())
            if chave not in produtos:
                produtos[chave], _ = Produto.objects.get_or_create(codigo_anp=chave[0], descricao=chave[1])
            ano, mes = linha['mes_de_referencia'].split('-')
            objetos.append(Movimentacao(
                mes_referencia='%s-%s-01' % (ano, mes), sentido=int(linha['sentido_da_operacao']),
                tipo_operacao=int(linha['tipo_da_operacao']), modo_transporte=int(linha['modo_de_transporte']),
                produto=produtos[chave], volume_m3=Decimal(linha['volume_m3']).quantize(Decimal('0.001'))))
    Movimentacao.objects.bulk_create(objetos)
    # update() não aciona auto_now: preserva a data de atualização da planilha publicada.
    Movimentacao.objects.update(criado_em=ATUALIZADO_EM, atualizado_em=ATUALIZADO_EM)


def descarregar(apps, schema_editor):
    if schema_editor.connection.alias != 'default':
        return
    apps.get_model('website', 'MovimentacaoANP').objects.all().delete()
    apps.get_model('website', 'ProdutoANP').objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [('website', '0004_movimentacao_anp')]
    operations = [migrations.RunPython(carregar, descarregar)]
