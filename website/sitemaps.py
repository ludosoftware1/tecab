from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class PaginasSitemap(Sitemap):
    changefreq = 'monthly'

    def items(self):
        return ['home', 'quem_somos', 'informacoes_anp', 'contato', 'canal_integridade']

    def location(self, item):
        return reverse('website:' + item)

    def priority(self, item):
        return 1.0 if item == 'home' else 0.7
