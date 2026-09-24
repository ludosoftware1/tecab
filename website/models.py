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
