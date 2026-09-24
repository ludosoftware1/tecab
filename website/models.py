from django.db import models


class MensagemContato(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField('e-mail')
    mensagem = models.TextField(blank=True)
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
    telefone = models.CharField(max_length=50, blank=True)
    mensagem = models.TextField(blank=True)
    curriculo = models.FileField('currículo', upload_to='curriculos/%Y/%m/')
    criado_em = models.DateTimeField('recebida em', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'candidatura (Trabalhe Conosco)'
        verbose_name_plural = 'candidaturas (Trabalhe Conosco)'

    def __str__(self):
        return '%s - %s' % (self.nome, self.cidade)
