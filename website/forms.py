import os

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, UserCreationForm
from django.db.models import Q
from django.templatetags.static import static
from django.utils.html import format_html

from .models import Candidatura, MensagemContato, RelatoIntegridade

OBRIGATORIO = 'Preencha este campo.'
EMAIL_INVALIDO = 'Informe um e-mail válido, como nome@empresa.com.br.'
ACEITE = 'Para continuar, é necessário concordar com a Política de Privacidade.'


class SiteFormMixin:
    """Mensagens em português, autocomplete e um campo-armadilha (honeypot) contra spam."""

    autocomplete = {
        'nome': 'name', 'email': 'email', 'telefone': 'tel', 'cidade': 'address-level2',
        'username': 'username', 'first_name': 'given-name', 'last_name': 'family-name',
    }
    honeypot = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.required and name != 'aceite_privacidade':  # o aceite tem mensagem própria
                field.error_messages['required'] = OBRIGATORIO
            if isinstance(field, forms.EmailField):
                field.error_messages['invalid'] = EMAIL_INVALIDO
            if name in self.autocomplete:
                field.widget.attrs.setdefault('autocomplete', self.autocomplete[name])
            if name == 'telefone':
                field.widget.input_type = 'tel'
                field.widget.attrs.setdefault('inputmode', 'tel')
        if 'aceite_privacidade' in self.fields:
            self.fields['aceite_privacidade'].label = format_html(
                'Li e concordo com a <a href="{}" target="_blank" rel="noopener">Política de Privacidade</a> e autorizo '
                'o uso dos meus dados para este atendimento.', static('docs/politica-de-privacidade.pdf'))
        if self.honeypot:
            self.fields['site_empresa'] = forms.CharField(required=False, label='Não preencha este campo',
                                                          widget=forms.TextInput(attrs={'tabindex': '-1',
                                                                                        'autocomplete': 'off'}))

    @property
    def is_spam(self):
        return bool(self.honeypot and self.cleaned_data.get('site_empresa'))


class ContatoForm(SiteFormMixin, forms.ModelForm):
    aceite_privacidade = forms.BooleanField(error_messages={'required': ACEITE})

    class Meta:
        model = MensagemContato
        fields = ['nome', 'email', 'telefone', 'assunto', 'mensagem', 'aceite_privacidade']
        labels = {'nome': 'Nome completo', 'email': 'E-mail', 'telefone': 'Telefone', 'assunto': 'Assunto',
                  'mensagem': 'Mensagem'}
        widgets = {'mensagem': forms.Textarea(attrs={'rows': 5})}


class TrabalheConoscoForm(SiteFormMixin, forms.ModelForm):
    EXTENSOES = ('.pdf', '.doc', '.docx')
    aceite_privacidade = forms.BooleanField(error_messages={'required': ACEITE})

    class Meta:
        model = Candidatura
        fields = ['nome', 'cidade', 'email', 'telefone', 'mensagem', 'curriculo', 'aceite_privacidade']
        labels = {'nome': 'Nome completo', 'cidade': 'Cidade onde mora', 'email': 'E-mail', 'telefone': 'Telefone',
                  'mensagem': 'Conte um pouco sobre você', 'curriculo': 'Currículo'}
        help_texts = {'curriculo': 'PDF, DOC ou DOCX, até %d MB.'}
        widgets = {'mensagem': forms.Textarea(attrs={'rows': 4}),
                   'curriculo': forms.ClearableFileInput(attrs={'accept': '.pdf,.doc,.docx'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curriculo'].help_text = self.fields['curriculo'].help_text % (
            settings.TECAB_CURRICULO_MAX_BYTES // (1024 * 1024))

    def clean_curriculo(self):
        arquivo = self.cleaned_data['curriculo']
        if os.path.splitext(arquivo.name)[1].lower() not in self.EXTENSOES:
            raise forms.ValidationError('Envie o currículo em PDF, DOC ou DOCX.')
        if arquivo.size > settings.TECAB_CURRICULO_MAX_BYTES:
            raise forms.ValidationError('O arquivo é maior que %d MB.' % (settings.TECAB_CURRICULO_MAX_BYTES // (1024 * 1024)))
        return arquivo


class IntegridadeForm(SiteFormMixin, forms.ModelForm):
    class Meta:
        model = RelatoIntegridade
        fields = ['categoria', 'descricao', 'quando_onde', 'envolvidos', 'nome', 'email', 'telefone']
        labels = {'categoria': 'Tipo de ocorrência', 'descricao': 'Descreva o que aconteceu',
                  'quando_onde': 'Quando e onde ocorreu', 'envolvidos': 'Pessoas ou áreas envolvidas',
                  'nome': 'Nome', 'email': 'E-mail', 'telefone': 'Telefone'}
        help_texts = {'descricao': 'Inclua o máximo de detalhes que puder: o que ocorreu, como e se há evidências.',
                      'quando_onde': 'Opcional. Ex.: março de 2026, área de carregamento.',
                      'envolvidos': 'Opcional.'}
        widgets = {'descricao': forms.Textarea(attrs={'rows': 6})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].choices = [('', 'Selecione...')] + RelatoIntegridade.CATEGORIAS

    def clean_descricao(self):
        texto = self.cleaned_data['descricao'].strip()
        if len(texto) < 20:
            raise forms.ValidationError('Descreva a situação com pelo menos 20 caracteres.')
        return texto


# --------------------------------------------------------------------------- Área do Colaborador
class LoginForm(SiteFormMixin, AuthenticationForm):
    honeypot = False
    lembrar = forms.BooleanField(required=False, label='Manter conectado neste dispositivo')

    error_messages = {
        'invalid_login': 'Usuário/e-mail ou senha incorretos. Verifique os dados e tente novamente.',
        'inactive': 'Esta conta está desativada.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuário ou e-mail'
        self.fields['password'].label = 'Senha'
        self.fields['password'].widget.attrs['autocomplete'] = 'current-password'


class RegistroForm(SiteFormMixin, UserCreationForm):
    honeypot = False
    first_name = forms.CharField(label='Nome', max_length=150)
    last_name = forms.CharField(label='Sobrenome', max_length=150, required=False)
    email = forms.EmailField(label='E-mail', help_text='Usado para recuperar sua senha.')

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'username')
        labels = {'username': 'Nome de usuário'}

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model()._default_manager.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail. Use a opção "Esqueceu a senha?".')
        return email


class RecuperarSenhaForm(SiteFormMixin, PasswordResetForm):
    """Aceita nome de usuário ou e-mail."""
    honeypot = False
    email = forms.CharField(label='Usuário ou e-mail', max_length=254,
                            widget=forms.TextInput(attrs={'autocomplete': 'username'}))

    def get_users(self, identifier):
        User = get_user_model()
        email_field = User.get_email_field_name()
        users = User._default_manager.filter(
            Q(**{'%s__iexact' % email_field: identifier}) | Q(username__iexact=identifier), is_active=True)
        # O save() do PasswordResetForm envia o link para o e-mail cadastrado de cada usuário.
        return (u for u in users if u.has_usable_password() and getattr(u, email_field))
