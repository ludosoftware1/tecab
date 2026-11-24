import secrets

from django.db import models


class MensagemContato(models.Model):
    ASSUNTOS = [
        ('comercial', 'Comercial'),
        ('operacoes', 'Operações'),
        ('administrativo', 'Administrativo / Financeiro'),
        ('outros', 'Outros assuntos'),
    ]

    nome = models.CharField(max_length=200)
    email = models.EmailField('e-mail')
    telefone = models.CharField(max_length=30, blank=True)
    assunto = models.CharField(max_length=20, choices=ASSUNTOS, default='comercial')
    mensagem = models.TextField()
    aceite_privacidade = models.BooleanField('aceitou a política de privacidade', default=False)
    criado_em = models.DateTimeField('recebida em', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'mensagem de contato'
        verbose_name_plural = 'mensagens de contato'

    def __str__(self):
        return '%s <%s>' % (self.nome, self.email)


class Candidatura(models.Model):
    nome = models.CharField(max_length=200)
    cidade = models.CharField(max_length=200)
    email = models.EmailField('e-mail')
    telefone = models.CharField(max_length=30, blank=True)
    mensagem = models.TextField(blank=True)
    curriculo = models.FileField('currículo', upload_to='curriculos/%Y/%m/')
    aceite_privacidade = models.BooleanField('aceitou a política de privacidade', default=False)
    criado_em = models.DateTimeField('recebida em', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'candidatura (Trabalhe Conosco)'
        verbose_name_plural = 'candidaturas (Trabalhe Conosco)'

    def __str__(self):
        return '%s - %s' % (self.nome, self.cidade)


def _novo_protocolo():
    return 'TCB-' + ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))


class RelatoIntegridade(models.Model):
    """Relato do Canal de Integridade. Não armazena IP nem dados de navegação do relator."""

    CATEGORIAS = [
        ('etica', 'Violação do Código de Conduta e Ética'),
        ('fraude', 'Fraude ou desvio de recursos'),
        ('corrupcao', 'Corrupção ou suborno'),
        ('conflito', 'Conflito de interesses'),
        ('assedio', 'Assédio ou discriminação'),
        ('seguranca', 'Segurança, saúde ou meio ambiente'),
        ('lgpd', 'Privacidade e proteção de dados (LGPD)'),
        ('outros', 'Outros'),
    ]
    STATUS = [('novo', 'Novo'), ('em_analise', 'Em análise'), ('concluido', 'Concluído')]

    protocolo = models.CharField(max_length=12, unique=True, default=_novo_protocolo, editable=False)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    descricao = models.TextField('descrição')
    quando_onde = models.CharField('quando e onde ocorreu', max_length=255, blank=True)
    envolvidos = models.CharField('pessoas ou áreas envolvidas', max_length=255, blank=True)
    nome = models.CharField(max_length=200, blank=True)
    email = models.EmailField('e-mail', blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='novo')
    anotacoes = models.TextField('anotações internas', blank=True)
    criado_em = models.DateTimeField('recebido em', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'relato do Canal de Integridade'
        verbose_name_plural = 'relatos do Canal de Integridade'

    def __str__(self):
        return '%s - %s' % (self.protocolo, self.get_categoria_display())

    @property
    def anonimo(self):
        return not (self.nome or self.email or self.telefone)


# --------------------------------------------------------------------------- Movimentação ANP
class ProdutoANP(models.Model):
    """Produto movimentado, conforme a tabela T012 do SIMP (código zero quando o produto não tem código ANP)."""

    codigo_anp = models.PositiveIntegerField('código ANP', help_text='9 dígitos, tabela T012 do SIMP. Use 0 se não houver.')
    descricao = models.CharField('descrição', max_length=148)
    ativo = models.BooleanField(default=True, help_text='Produtos inativos não aparecem para novos lançamentos.')

    class Meta:
        ordering = ['descricao']
        verbose_name = 'produto (ANP)'
        verbose_name_plural = 'produtos (ANP)'
        constraints = [models.UniqueConstraint(fields=['codigo_anp', 'descricao'], name='produto_anp_unico')]

    def __str__(self):
        return '%s (%09d)' % (self.descricao, self.codigo_anp)


class MovimentacaoANP(models.Model):
    """Volume mensal movimentado no terminal: uma linha da aba "Dados" da planilha da Resolução ANP nº 881/2022."""

    SENTIDOS = [(1, 'Recepção'), (2, 'Entrega')]
    TIPOS = [(1, 'Com armazenagem'), (2, 'Sem armazenagem'), (3, 'Transbordo'), (4, 'Abastecimento'), (9, 'Outros')]
    MODOS = [(1, 'Rodoviário'), (2, 'Ferroviário'), (4, 'Aquaviário'), (5, 'Dutoviário'), (9, 'Outros')]

    mes_referencia = models.DateField('mês de referência', db_index=True, help_text='Sempre o dia 1º do mês.')
    sentido = models.PositiveSmallIntegerField('sentido da operação', choices=SENTIDOS)
    tipo_operacao = models.PositiveSmallIntegerField('tipo da operação', choices=TIPOS, default=1)
    modo_transporte = models.PositiveSmallIntegerField('modo de transporte', choices=MODOS)
    produto = models.ForeignKey(ProdutoANP, on_delete=models.PROTECT, related_name='movimentacoes')
    volume_m3 = models.DecimalField('volume (m³ a 20 °C)', max_digits=12, decimal_places=3)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)
    criado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
                                   verbose_name='criado por')
    atualizado_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='+',
                                       verbose_name='atualizado por')

    class Meta:
        # Mesma ordem da planilha: cronológica e, dentro do mês, na ordem de lançamento.
        ordering = ['mes_referencia', 'id']
        verbose_name = 'movimentação (ANP)'
        verbose_name_plural = 'movimentações (ANP)'
        constraints = [models.CheckConstraint(condition=models.Q(volume_m3__gte=0), name='movimentacao_volume_nao_negativo')]

    def __str__(self):
        return '%s · %s · %s · %s m³' % (self.mes_referencia.strftime('%Y-%m'), self.get_sentido_display(),
                                         self.produto.descricao, self.volume_m3)

    @property
    def mes(self):
        return self.mes_referencia.strftime('%Y-%m')
