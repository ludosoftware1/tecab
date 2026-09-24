from django.urls import reverse
from django.utils import timezone

from .content import EMPRESA

NAV = [
    ('home', 'Início'),
    ('quem_somos', 'Quem somos'),
    ('informacoes_anp', 'Informações ANP'),
    ('contato', 'Contato'),
]


def site(request):
    match = getattr(request, 'resolver_match', None)
    current = match.url_name if match else None
    return {
        'empresa': EMPRESA,
        'nav': [{'url': reverse('website:' + name), 'label': label, 'active': name == current} for name, label in NAV],
        'current_url_name': current,
        'ano_atual': timezone.localdate().year,
    }
