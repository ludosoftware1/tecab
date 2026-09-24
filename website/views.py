import logging

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.core.mail import EmailMessage
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods

from .forms import (CF7_MESSAGES, ContatoForm, LoginForm, NovaSenhaForm, RecuperarSenhaForm, RegistroForm,
                    TrabalheConoscoForm)
from .pages import PAGES, PORTFOLIO_CATEGORIES, PORTFOLIO_ITEMS, WP_PAGE_IDS, WP_PORTFOLIO_IDS

logger = logging.getLogger(__name__)


def _legacy_redirect(request):
    """Redireciona URLs antigas do WordPress (?page_id=, ?p=, ?portfolio-item=...)."""
    get = request.GET
    try:
        if 'page_id' in get and int(get['page_id']) in WP_PAGE_IDS:
            return reverse('website:' + WP_PAGE_IDS[int(get['page_id'])])
        if 'p' in get:
            pid = int(get['p'])
            if pid in WP_PAGE_IDS:
                return reverse('website:' + WP_PAGE_IDS[pid])
            if pid in WP_PORTFOLIO_IDS:
                return reverse('website:portfolio_item', args=[WP_PORTFOLIO_IDS[pid]])
    except ValueError:
        return None
    if get.get('portfolio-item') in PORTFOLIO_ITEMS:
        return reverse('website:portfolio_item', args=[get['portfolio-item']])
    if get.get('portfolio-category') in PORTFOLIO_CATEGORIES:
        return reverse('website:portfolio_category', args=[get['portfolio-category']])
    return None


def render_page(request, name, context=None, status=200):
    ctx = {'page': PAGES[name]}
    ctx.update(context or {})
    return render(request, PAGES[name]['template'], ctx, status=status)


def home(request):
    target = _legacy_redirect(request)
    if target:
        return redirect(target, permanent=True)
    return render_page(request, 'home')


def page(request, name):
    return render_page(request, name)


def portfolio_item(request, slug):
    if slug not in PORTFOLIO_ITEMS:
        raise Http404
    return render(request, 'website/portfolio/item/%s.html' % slug, {'page': PORTFOLIO_ITEMS[slug]})


def portfolio_category(request, slug):
    if slug not in PORTFOLIO_CATEGORIES:
        raise Http404
    return render(request, 'website/portfolio/categoria/%s.html' % slug, {'page': PORTFOLIO_CATEGORIES[slug]})


# --------------------------------------------------------------------------- Contato
def _notificar(assunto, corpo, reply_to, anexo=None):
    msg = EmailMessage(assunto, corpo, to=settings.TECAB_CONTATO_DESTINATARIOS, reply_to=[reply_to])
    if anexo:
        anexo.open('rb')
        msg.attach(anexo.name.rsplit('/', 1)[-1], anexo.read())
        anexo.close()
    msg.send()


@require_http_methods(['GET', 'POST'])
def contato(request):
    forms = {'contato': ContatoForm(prefix='contato'), 'trabalhe-conosco': TrabalheConoscoForm(prefix='trabalhe')}
    # estado de cada formulário no padrão do Contact Form 7: init | sent | invalid | failed
    state = {'contato': 'init', 'trabalhe-conosco': 'init'}
    active_tab = None

    if request.method == 'POST':
        form_id = request.POST.get('form_id')
        if form_id not in forms:
            return redirect('website:contato')
        form_class = ContatoForm if form_id == 'contato' else TrabalheConoscoForm
        form = form_class(request.POST, request.FILES, prefix=forms[form_id].prefix)
        forms[form_id] = form
        active_tab = form_id
        if form.is_valid():
            obj = form.save()
            try:
                if form_id == 'contato':
                    _notificar('[TECAB] Contato de %s' % obj.nome,
                               'Nome: %s\nE-mail: %s\n\n%s' % (obj.nome, obj.email, obj.mensagem), obj.email)
                else:
                    _notificar('[TECAB] Trabalhe Conosco - %s' % obj.nome,
                               'Nome: %s\nCidade: %s\nE-mail: %s\nTelefone: %s\n\n%s'
                               % (obj.nome, obj.cidade, obj.email, obj.telefone, obj.mensagem),
                               obj.email, anexo=obj.curriculo)
                request.session['cf7_state'] = [form_id, 'sent']
            except Exception:  # a mensagem já foi gravada; só o aviso por e-mail falhou
                logger.exception('Falha ao enviar e-mail do formulário %s', form_id)
                request.session['cf7_state'] = [form_id, 'failed']
            anchor = '#wpcf7-f131-p2381-o1' if form_id == 'contato' else '#wpcf7-f6642-p2381-o2'
            return redirect(reverse('website:contato') + anchor)
        state[form_id] = 'invalid'
    else:
        saved = request.session.pop('cf7_state', None)
        if saved and saved[0] in state:
            state[saved[0]] = saved[1]
            active_tab = saved[0]

    def response(form_id, lang):
        st = state[form_id]
        return {'form': forms[form_id], 'state': st, 'message': '' if st == 'init' else CF7_MESSAGES[lang][st]}

    return render_page(request, 'contato', {
        'contato': response('contato', 'en'),
        'trabalhe': response('trabalhe-conosco', 'pt'),
        'active_tab': active_tab,
    })


# --------------------------------------------------------------------------- Área do Colaborador
class PageContextMixin:
    page_name = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page'] = PAGES[self.page_name]
        return ctx


class LoginView(PageContextMixin, auth_views.LoginView):
    page_name = 'login'
    template_name = 'website/accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if not form.cleaned_data.get('rememberme'):
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
        return redirect('website:area_colaborador')
    return render_page(request, 'registrar', {'form': form})


class RecuperarSenhaView(PageContextMixin, auth_views.PasswordResetView):
    page_name = 'recuperar_senha'
    template_name = 'website/accounts/recuperar_senha.html'
    form_class = RecuperarSenhaForm
    email_template_name = 'website/accounts/email/redefinir_senha.txt'
    subject_template_name = 'website/accounts/email/redefinir_senha_assunto.txt'
    success_url = reverse_lazy('website:recuperar_senha_enviado')


class RecuperarSenhaEnviadoView(PageContextMixin, auth_views.PasswordResetDoneView):
    page_name = 'recuperar_senha'
    template_name = 'website/accounts/recuperar_senha_enviado.html'


class RedefinirSenhaView(PageContextMixin, auth_views.PasswordResetConfirmView):
    page_name = 'recuperar_senha'
    template_name = 'website/accounts/redefinir_senha.html'
    form_class = NovaSenhaForm
    success_url = reverse_lazy('website:redefinir_senha_concluido')


class RedefinirSenhaConcluidoView(PageContextMixin, auth_views.PasswordResetCompleteView):
    page_name = 'recuperar_senha'
    template_name = 'website/accounts/redefinir_senha_concluido.html'
