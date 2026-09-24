import json
import os
from functools import lru_cache

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@lru_cache(maxsize=1)
def _manifest():
    path = finders.find('img/manifest.json')
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def _info(key):
    try:
        return _manifest()[key]
    except KeyError:
        raise template.TemplateSyntaxError('Imagem "%s" não está no manifesto (rode gerar_imagens).' % key)


@register.simple_tag
def picture(key, alt='', sizes='100vw', css_class='', loading='lazy', priority=False):
    """<img> responsivo (WebP) com srcset, dimensões intrínsecas e carregamento preguiçoso."""
    info = _info(key)
    widths = info['widths']
    srcset = ', '.join('%s %dw' % (static('img/%s-%d.webp' % (key, w)), w) for w in widths)
    fallback = widths[min(1, len(widths) - 1)]
    return format_html(
        '<img src="{}" srcset="{}" sizes="{}" width="{}" height="{}" alt="{}" class="{}" loading="{}" decoding="async"{}>',
        static('img/%s-%d.webp' % (key, fallback)), srcset, sizes, info['width'], info['height'], alt, css_class,
        'eager' if priority else loading, format_html(' fetchpriority="high"') if priority else '',
    )


@register.simple_tag
def img_url(key, width=None):
    """URL de uma variante: a menor com pelo menos `width` pixels (ou a maior disponível)."""
    widths = _info(key)['widths']
    chosen = next((w for w in widths if width and w >= int(width)), widths[-1])
    return static('img/%s-%d.webp' % (key, chosen))


@register.simple_tag
def icon(name, css_class='', label=''):
    """Ícone SVG do sprite em includes/icons.html."""
    attrs = format_html(' role="img" aria-label="{}"', label) if label else format_html(' aria-hidden="true"')
    return format_html('<svg class="icon {}"{} focusable="false"><use href="#i-{}"></use></svg>', css_class, attrs, name)


@register.filter
def filesize(static_path):
    """Tamanho legível de um arquivo estático (ex.: 'PDF · 916 KB')."""
    path = finders.find(static_path)
    if not path:
        return ''
    size = os.path.getsize(path)
    ext = os.path.splitext(static_path)[1].lstrip('.').upper()
    if size >= 1024 * 1024:
        human = ('%.1f MB' % (size / 1024 / 1024)).replace('.', ',')
    else:
        human = '%d KB' % max(1, round(size / 1024))
    return '%s · %s' % (ext, human)


@register.simple_tag(takes_context=True)
def absolute_static(context, path):
    request = context.get('request')
    url = static(path)
    return request.build_absolute_uri(url) if request else url


@register.simple_tag
def json_ld(data):
    # JSON não pode ser escapado como HTML; basta impedir o fechamento prematuro da tag <script>.
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    return mark_safe('<script type="application/ld+json">%s</script>' % payload)
