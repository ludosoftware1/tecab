from django.urls import reverse

from .pages import MENU


def _custom_classes(item, has_children=False):
    classes = ['menu-item', 'menu-item-type-custom', 'menu-item-object-custom']
    if has_children:
        classes += ['menu-item-has-children', 'menu-item-%d' % item['id'], 'qodef-menu-item--narrow']
    else:
        classes.append('menu-item-%d' % item['id'])
    return ' '.join(classes)


def menu(request):
    """Monta o menu com as mesmas classes que o WordPress gerava (incluindo o item atual)."""
    match = getattr(request, 'resolver_match', None)
    current = match.url_name if match and match.namespace == 'website' else None
    items = []
    for item in MENU:
        if 'children' in item:
            items.append({
                'label': item['label'], 'url': item['url'], 'current': False,
                'classes': _custom_classes(item, has_children=True),
                'children': [{'label': c['label'], 'url': c['url'], 'classes': _custom_classes(c)}
                             for c in item['children']],
            })
            continue
        is_current = item['url_name'] == current
        classes = ['menu-item', 'menu-item-type-post_type', 'menu-item-object-page']
        if item.get('home'):
            classes.append('menu-item-home')
        if is_current:
            classes += ['current-menu-item', 'page_item', 'page-item-%d' % item['page_id'], 'current_page_item']
        classes.append('menu-item-%d' % item['id'])
        items.append({'label': item['label'], 'url': reverse('website:' + item['url_name']),
                      'current': is_current, 'classes': ' '.join(classes)})
    return {'menu_items': items}
