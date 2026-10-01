import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_GET, require_http_methods

from . import content
from .forms import ContatoForm, IntegridadeForm, LoginForm, RecuperarSenhaForm, RegistroForm, TrabalheConoscoForm
from .pages import WP_PAGE_IDS, WP_PORTFOLIO_IDS

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- páginas institucionais
def _legacy_redirect(request):
    """Endereços antigos do WordPress (?page_id=, ?p=, ?portfolio-item=...)."""
    get = request.GET
    for param in ('page_id', 'p'):
        if param in get:
            try:
                pid = int(get[param])
            except ValueError:
                return None
            if pid in WP_PAGE_IDS:
                return reverse('website:' + WP_PAGE_IDS[pid])
            if pid in WP_PORTFOLIO_IDS:
                return reverse('website:home') + '#diferenciais'
    if 'portfolio-item' in get or 'portfolio-category' in get:
        return reverse('website:home') + '#diferenciais'
    return None


def home(request):
    target = _legacy_redirect(request)
    if target:
        return redirect(target, permanent=True)
    return render(request, 'website/pages/home.html', {
        'numeros': content.NUMEROS, 'modais': content.MODAIS, 'produtos': content.PRODUTOS,
        'diferenciais': content.DIFERENCIAIS, 'certificacoes': content.CERTIFICACOES, 'clientes': content.CLIENTES,
        'jsonld': content.jsonld_empresa(request.build_absolute_uri('/')),
    })


def quem_somos(request):
    return render(request, 'website/pages/quem_somos.html', {
        'historia': content.HISTORIA, 'mvv': content.MVV, 'galeria': content.GALERIA, 'porto': content.PORTO,
        'certificacoes': content.CERTIFICACOES, 'politica_sgi': content.POLITICA_SGI,
    })


def informacoes_anp(request):
    return render(request, 'website/pages/informacoes_anp.html', {
        'documentos': content.DOCUMENTOS_ANP, 'formularios': content.FORMULARIOS_ANP,
        'historico': content.HISTORICO_ANP,
    })


def legacy_portfolio(request, slug):
    return redirect(reverse('website:home') + '#diferenciais', permanent=True)


# --------------------------------------------------------------------------- formulários
def _notificar(assunto, corpo, destinatarios, reply_to=None, anexo=None):
    msg = EmailMessage(assunto, corpo, to=destinatarios, reply_to=[reply_to] if reply_to else None)
    if anexo:
        with anexo.open('rb') as fh:
            msg.attach(anexo.name.rsplit('/', 1)[-1], fh.read())
    msg.send()


@require_http_methods(['GET', 'POST'])
def contato(request):
    forms = {'contato': ContatoForm(prefix='contato'), 'trabalhe': TrabalheConoscoForm(prefix='trabalhe')}
    aba = request.GET.get('aba') if request.GET.get('aba') in forms else 'contato'

    if request.method == 'POST':
        aba = request.POST.get('form_id')
        if aba not in forms:
            return redirect('website:contato')
        form_class = ContatoForm if aba == 'contato' else TrabalheConoscoForm
        form = forms[aba] = form_class(request.POST, request.FILES, prefix=aba)
        if form.is_valid():
            if not form.is_spam:
                obj = form.save()
                try:
                    if aba == 'contato':
                        _notificar('[Site TECAB] %s - %s' % (obj.get_assunto_display(), obj.nome),
                                   'Nome: %s\nE-mail: %s\nTelefone: %s\nAssunto: %s\n\n%s'
                                   % (obj.nome, obj.email, obj.telefone, obj.get_assunto_display(), obj.mensagem),
                                   settings.TECAB_CONTATO_FALE_DESTINATARIOS, obj.email)
                    else:
                        _notificar('[Site TECAB] Trabalhe Conosco - %s' % obj.nome,
                                   'Nome: %s\nCidade: %s\nE-mail: %s\nTelefone: %s\n\n%s\n\n'
                                   'Currículo em anexo: %s (%d bytes).'
                                   % (obj.nome, obj.cidade, obj.email, obj.telefone, obj.mensagem,
                                      obj.curriculo.name, obj.curriculo.size),
                                   settings.TECAB_CONTATO_TRABALHE_DESTINATARIOS, obj.email, anexo=obj.curriculo)
                except Exception:  # a mensagem já está gravada; apenas o aviso por e-mail falhou
                    logger.exception('Falha ao enviar o e-mail do formulário %s', aba)
            if aba == 'contato':
                messages.success(request, 'Mensagem enviada! Nossa equipe responderá em breve pelo e-mail informado.',
                                 extra_tags='contato')
            else:
                messages.success(request, 'Currículo recebido! Obrigado pelo interesse em trabalhar no TECAB.',
                                 extra_tags='trabalhe')
            return redirect(reverse('website:contato') + '?aba=%s#formularios' % aba)

    return render(request, 'website/pages/contato.html', {
        'form_contato': forms['contato'], 'form_trabalhe': forms['trabalhe'], 'aba': aba,
    }, status=400 if request.method == 'POST' else 200)


@require_http_methods(['GET', 'POST'])
def canal_integridade(request):
    form = IntegridadeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if form.is_spam:
            return redirect('website:canal_integridade')
        relato = form.save()
        try:
            _notificar('[Canal de Integridade] Novo relato %s' % relato.protocolo,
                       'Um novo relato foi registrado no Canal de Integridade.\n\nProtocolo: %s\nCategoria: %s\n\n'
                       'Acesse a área administrativa do site para consultar o conteúdo.'
                       % (relato.protocolo, relato.get_categoria_display()),
                       settings.TECAB_INTEGRIDADE_DESTINATARIOS)
        except Exception:
            logger.exception('Falha ao notificar o relato %s', relato.protocolo)
        request.session['protocolo_integridade'] = relato.protocolo
        return redirect('website:canal_integridade_enviado')
    return render(request, 'website/pages/canal_integridade.html', {'form': form},
                  status=400 if request.method == 'POST' else 200)


def canal_integridade_enviado(request):
    protocolo = request.session.pop('protocolo_integridade', None)
    if not protocolo:
        return redirect('website:canal_integridade')
    return render(request, 'website/pages/canal_integridade_enviado.html', {'protocolo': protocolo})


# --------------------------------------------------------------------------- Área do Colaborador
@login_required
def area_colaborador(request):
    return render(request, 'website/accounts/area_colaborador.html')


class LoginView(auth_views.LoginView):
    template_name = 'website/accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if not form.cleaned_data.get('lembrar'):
            self.request.session.set_expiry(0)
        return response


@require_http_methods(['GET', 'POST'])
def registrar(request):
    if request.user.is_authenticated:
        return redirect('website:area_colaborador')
    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user, backend='website.backends.UsernameOrEmailBackend')
        messages.success(request, 'Conta criada com sucesso. Bem-vindo(a)!')
        return redirect('website:area_colaborador')
    return render(request, 'website/accounts/registrar.html', {'form': form})


class RecuperarSenhaView(auth_views.PasswordResetView):
    template_name = 'website/accounts/recuperar_senha.html'
    form_class = RecuperarSenhaForm
    email_template_name = 'website/accounts/email/redefinir_senha.txt'
    subject_template_name = 'website/accounts/email/redefinir_senha_assunto.txt'
    success_url = reverse_lazy('website:recuperar_senha_enviado')


class RecuperarSenhaEnviadoView(auth_views.PasswordResetDoneView):
    template_name = 'website/accounts/recuperar_senha_enviado.html'


class RedefinirSenhaView(auth_views.PasswordResetConfirmView):
    template_name = 'website/accounts/redefinir_senha.html'
    success_url = reverse_lazy('website:redefinir_senha_concluido')


class RedefinirSenhaConcluidoView(auth_views.PasswordResetCompleteView):
    template_name = 'website/accounts/redefinir_senha_concluido.html'


class AlterarSenhaView(auth_views.PasswordChangeView):
    template_name = 'website/accounts/alterar_senha.html'
    success_url = reverse_lazy('website:area_colaborador')

    def form_valid(self, form):
        messages.success(self.request, 'Senha alterada com sucesso.')
        return super().form_valid(form)


# --------------------------------------------------------------------------- utilitários
@require_GET
def robots_txt(request):
    lines = ['User-agent: *', 'Disallow: /admin/', 'Disallow: /area-do-colaborador/', 'Disallow: /login/',
             'Disallow: /registrar/', 'Disallow: /recuperar-senha/', 'Disallow: /redefinir-senha/',
             'Sitemap: %s' % request.build_absolute_uri(reverse('sitemap'))]
    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain')