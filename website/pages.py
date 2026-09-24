"""Registro das páginas do site (espelhadas de tecab.srv.br).

`elementor` indica se a página original carregava os assets do Elementor
(CSS do kit, fontes e scripts do frontend) — o base.html os inclui somente nesse caso.
"""

PAGES = {
    'home': {'template': 'website/pages/home.html', 'elementor': True},
    'quem_somos': {'template': 'website/pages/quem_somos.html', 'elementor': True},
    'informacoes_anp': {'template': 'website/pages/informacoes_anp.html', 'elementor': True},
    'area_colaborador': {'template': 'website/pages/area_colaborador.html', 'elementor': True},
    'contato': {'template': 'website/pages/contato.html', 'elementor': True},
    'login': {'template': 'website/accounts/login.html', 'elementor': False},
    'registrar': {'template': 'website/accounts/registrar.html', 'elementor': False},
    'recuperar_senha': {'template': 'website/accounts/recuperar_senha.html', 'elementor': False},
}

PORTFOLIO_ITEMS = {
    'instalacoes-2': {'title': 'Profissionais Qualificados', 'elementor': True},
    'profissionais-qualificados': {'title': 'Plataforma Automatizada', 'elementor': True},
    'profissionais-qualificados-2': {'title': 'Integridade de Equipamentos', 'elementor': True},
    'profissionais-qualificados-3': {'title': 'Equipamentos', 'elementor': True},
    'tecab': {'title': 'Sistema de combate a incêndio com captação infinita de água do rio', 'elementor': False},
    'construction': {'title': 'Título Foto 18', 'elementor': True},
    'new-project': {'title': 'Título Foto 18', 'elementor': True},
    'team-work': {'title': 'Título Foto 17', 'elementor': True},
    'team-power': {'title': 'Título Foto 16', 'elementor': True},
    'work-in-progress': {'title': 'Título Foto 15', 'elementor': True},
    'work-safety': {'title': 'Título Foto 14', 'elementor': True},
    'building-smart': {'title': 'Título Foto 13', 'elementor': True},
    'heavy-equipment': {'title': 'Título Foto 12', 'elementor': True},
    'industry-systems': {'title': 'Título Foto 10', 'elementor': True},
    'building-systems': {'title': 'Título Foto 9', 'elementor': True},
    'frame-construction': {'title': 'Título Foto 8', 'elementor': True},
    'new-structures-2': {'title': 'Título Foto 5', 'elementor': True},
    'innovative-project': {'title': 'Título Foto 21', 'elementor': True},
    'new-structures': {'title': 'Título Foto 20', 'elementor': True},
    'custom-fabrication': {'title': 'Custom Fabrication', 'elementor': True},
    'hard-work': {'title': 'Hard Work', 'elementor': True},
}

PORTFOLIO_CATEGORIES = {
    'instalacoes-e-profissionais': {'title': 'Instalações e Profissionais', 'elementor': False},
    'arquivado': {'title': 'Arquivado', 'elementor': False},
    'industry': {'title': 'Industry', 'elementor': False},
    'materials': {'title': 'Materials', 'elementor': False},
    'shape-making': {'title': 'Shape Making', 'elementor': False},
    'metal': {'title': 'Metal', 'elementor': False},
}

# IDs do WordPress, para redirecionar links antigos (?page_id=, ?p=).
WP_PAGE_IDS = {
    6069: 'home', 2174: 'quem_somos', 5331: 'informacoes_anp', 6946: 'area_colaborador',
    2381: 'contato', 6953: 'login', 6954: 'registrar', 6958: 'recuperar_senha',
}
WP_PORTFOLIO_IDS = {
    4383: 'instalacoes-2', 4404: 'profissionais-qualificados', 4400: 'profissionais-qualificados-2',
    6473: 'tecab', 4377: 'profissionais-qualificados-3', 4465: 'construction', 4457: 'new-project',
    4453: 'team-work', 4445: 'work-in-progress', 4426: 'heavy-equipment', 4416: 'building-systems',
    4449: 'team-power', 4436: 'work-safety', 4420: 'industry-systems', 4430: 'building-smart',
    4408: 'frame-construction', 4396: 'new-structures-2', 4360: 'custom-fabrication', 4356: 'hard-work',
    4351: 'innovative-project', 4345: 'new-structures',
}

# Menu principal (mesmos IDs/classes do WordPress, usados pelo CSS/JS do tema Stal).
MENU = [
    {'id': 6224, 'label': 'Home', 'url_name': 'home', 'page_id': 6069, 'home': True},
    {'id': 6227, 'label': 'Quem Somos', 'url_name': 'quem_somos', 'page_id': 2174},
    {'id': 6228, 'label': 'Informações ANP', 'url_name': 'informacoes_anp', 'page_id': 5331},
    {'id': 6980, 'label': 'Área do Colaborador', 'url_name': 'area_colaborador', 'page_id': 6946},
    {'id': 6810, 'label': 'Portal do Cliente', 'url': 'https://autoload.tecab.srv.br/autoloadportal', 'children': [
        {'id': 6934, 'label': 'LINK 1', 'url': 'http://128.201.185.254/Portal/Portal'},
        {'id': 6935, 'label': 'LINK 2', 'url': 'https://autoload.tecab.srv.br/Portal/Portal/'},
    ]},
    {'id': 6225, 'label': 'Contato', 'url_name': 'contato', 'page_id': 2381},
]
