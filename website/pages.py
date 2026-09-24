"""Mapeamento dos endereços antigos do WordPress para as rotas atuais (redirecionamentos 301)."""

# ?page_id= / ?p= -> nome da rota
WP_PAGE_IDS = {
    6069: 'home', 2174: 'quem_somos', 5331: 'informacoes_anp', 6946: 'area_colaborador',
    2381: 'contato', 6953: 'login', 6954: 'registrar', 6958: 'recuperar_senha',
}

# Itens e categorias do antigo portfólio (conteúdo de demonstração do tema). Os quatro diferenciais reais
# agora ficam na home; todos os endereços antigos levam para essa seção.
WP_PORTFOLIO_IDS = {
    4383, 4404, 4400, 6473, 4377, 4465, 4457, 4453, 4445, 4426, 4416, 4449, 4436, 4420, 4430, 4408, 4396, 4360,
    4356, 4351, 4345,
}
