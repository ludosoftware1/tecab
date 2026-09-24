from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.templatetags.static import static as static_url
from django.urls import include, path
from django.views.generic import RedirectView

from website.sitemaps import PaginasSitemap
from website.views import robots_txt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': {'paginas': PaginasSitemap}}, name='sitemap'),
    path('robots.txt', robots_txt),
    path('favicon.ico', RedirectView.as_view(url=static_url('img/favicon-32.png'), permanent=True)),
    path('', include('website.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
