import os

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, UserCreationForm
from django.db.models import Q

from .models import Candidatura, MensagemContato

# Mensagens padrão do Contact Form 7 (o formulário de contato original usava en_US,
# o "Trabalhe Conosco" usava pt_BR).
CF7_MESSAGES = {
    'en': {
        'sent': 'Thank you for your message. It has been sent.',
        'invalid': 'One or more fields have an error. Please check and try again.',
        'failed': 'There was an error trying to send your message. Please try again later.',
        'required': 'Please fill out this field.',
        'email': 'Please enter an email address.',
    },
    'pt': {
        'sent': 'Agradecemos a sua mensagem.',
        'invalid': 'Um ou mais campos possuem um erro. Verifique e tente novamente.',
        'failed': 'Ocorreu um erro ao tentar enviar sua mensagem. Tente novamente mais tarde.',
        'required': 'Preencha este campo.',
        'email': 'Digite um endereço de e-mail.',
        'file_type': 'Você não tem permissão para enviar esse tipo de arquivo.',
        'file_size': 'O arquivo enviado é muito grande.',
    },
}


class ContatoForm(forms.ModelForm):
    lang = 'en'

    class Meta:
        model = MensagemContato
        fields = ['nome', 'email', 'mensagem']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        msgs = CF7_MESSAGES[self.lang]
        for field in self.fields.values():
            field.error_messages['required'] = msgs['required']
        self.fields['email'].error_messages['invalid'] = msgs['email']


class TrabalheConoscoForm(forms.ModelForm):
    lang = 'pt'
    EXTENSOES = ('.pdf', '.doc', '.docx')

    class Meta:
        model = Candidatura
        fields = ['nome', 'cidade', 'email', 'telefone', 'mensagem', 'curriculo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        msgs = CF7_MESSAGES[self.lang]
        for field in self.fields.values():
            field.error_messages['required'] = msgs['required']
        self.fields['email'].error_messages['invalid'] = msgs['email']

    def clean_curriculo(self):
        arquivo = self.cleaned_data['curriculo']
        if os.path.splitext(arquivo.name)[1].lower() not in self.EXTENSOES:
            raise forms.ValidationError(CF7_MESSAGES['pt']['file_type'])
        if arquivo.size > settings.TECAB_CURRICULO_MAX_BYTES:
            raise forms.ValidationError(CF7_MESSAGES['pt']['file_size'])
        return arquivo


# --------------------------------------------------------------------------- Área do Colaborador
class LoginForm(AuthenticationForm):
    rememberme = forms.BooleanField(required=False)

    error_messages = {
        'invalid_login': 'Password is incorrect. Please try again.',
        'inactive': 'This account is inactive.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].error_messages['required'] = 'Please enter your username or email'
        self.fields['password'].error_messages['required'] = 'Please enter your password'


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(required=False, max_length=150)
    last_name = forms.CharField(required=False, max_length=150)
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and get_user_model()._default_manager.filter(email__iexact=email).exists():
            raise forms.ValidationError('The email you entered is already registered')
        return email


class RecuperarSenhaForm(PasswordResetForm):
    """Aceita nome de usuário ou e-mail, como o formulário do Ultimate Member."""
    email = forms.CharField(max_length=254, error_messages={'required': 'Please provide your username or email'})

    def get_users(self, identifier):
        User = get_user_model()
        users = User._default_manager.filter(
            Q(**{'%s__iexact' % User.get_email_field_name(): identifier}) | Q(username__iexact=identifier),
            is_active=True,
        )
        # O save() do PasswordResetForm envia o link para o e-mail cadastrado de cada usuário.
        return (u for u in users if u.has_usable_password() and getattr(u, User.get_email_field_name()))


class NovaSenhaForm(SetPasswordForm):
    pass
