"""Importa a planilha de histórico de movimentação no layout da ANP (aba "Dados")."""
from django.core.management.base import BaseCommand, CommandError

from website import anp


class Command(BaseCommand):
    help = ('Importa um .xlsx no layout da ANP. Os meses presentes na planilha têm os lançamentos atuais '
            'substituídos; os demais meses não são alterados.')

    def add_arguments(self, parser):
        parser.add_argument('arquivo', help='caminho da planilha .xlsx')

    def handle(self, arquivo, **options):
        try:
            linhas, erros = anp.ler_xlsx(arquivo)
        except anp.PlanilhaInvalida as exc:
            raise CommandError(str(exc))
        if erros:
            raise CommandError('Planilha com %d erro(s); nada foi importado:\n%s' % (len(erros), '\n'.join(erros[:30])))
        if not linhas:
            raise CommandError('Nenhuma linha de movimentação encontrada.')
        r = anp.importar(linhas)
        self.stdout.write(self.style.SUCCESS(
            '%d linha(s) de %d mês(es) importada(s) (%s a %s); %d lançamento(s) anterior(es) substituído(s).'
            % (r['linhas'], r['meses'], r['primeiro'].strftime('%Y-%m'), r['ultimo'].strftime('%Y-%m'),
               r['removidas'])))
