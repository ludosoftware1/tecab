"""Conteúdo institucional do site (contatos, números, clientes, documentos...).

Centralizado aqui para que alterações de texto/telefone não exijam mexer nos templates.
"""

EMPRESA = {
    'nome': 'TECAB',
    'razao_social': 'TECAB - Terminais de Armazenagens de Cabedelo S/A',
    'descricao': ('Terminal privado de armazenagem de derivados de petróleo e biocombustíveis no Porto de '
                  'Cabedelo (PB), com operação pelos modais marítimo, rodoviário e dutoviário.'),
    'fundacao': 1994,
    'endereco': {
        'logradouro': 'Rua Conde Augusto Chericatti, 315',
        'bairro': 'Santa Catarina',
        'cidade': 'Cabedelo',
        'uf': 'PB',
        'cep': '58100-355',
    },
    'mapa_url': 'https://maps.app.goo.gl/M7LgnjVvkf3d4HgTA',
    'mapa_embed': ('https://maps.google.com/maps?q=25M5%2B7G%20Vila%20Sao%20Joao%2C%20Cabedelo%20-%20PB'
                   '&t=m&z=16&output=embed&iwloc=near'),
    'emails': [
        {'rotulo': 'Comercial', 'email': 'comercial@tecab.srv.br'},
        {'rotulo': 'Operações', 'email': 'operacoes@tecab.srv.br'},
    ],
    'email_lgpd': 'lgpd@tecab.srv.br',
    'telefone_principal': {'numero': '(83) 3228-3934', 'tel': '+558332283934'},
    'telefones': [
        {'setor': 'Geral', 'numeros': [('(83) 3228-3934', '+558332283934')]},
        {'setor': 'Comercial', 'numeros': [('(83) 99857-0019', '+5583998570019'), ('(83) 2179-5387', '+558321795387')]},
        {'setor': 'Operação', 'numeros': [('(83) 99851-0011', '+5583998510011'), ('(83) 2184-0003', '+558321840003')]},
        {'setor': 'Segurança', 'numeros': [('(83) 99810-0014', '+5583998100014'), ('(83) 2184-0004', '+558321840004')]},
        {'setor': 'Administrativo / Financeiro', 'numeros': [('(83) 2177-3822', '+558321773822')]},
    ],
    'horarios': [
        {'setor': 'Administrativo', 'periodos': ['Segunda a sexta, das 8h às 18h']},
        {'setor': 'Operação', 'periodos': ['Segunda a sexta, 24 horas', 'Sábados, das 6h às 14h']},
    ],
    'portal_cliente': [
        {'rotulo': 'Portal do Cliente', 'descricao': 'Acesso principal', 'url': 'https://autoload.tecab.srv.br/Portal/Portal/'},
        {'rotulo': 'Portal do Cliente (alternativo)', 'descricao': 'Use se o acesso principal estiver indisponível',
         'url': 'http://128.201.185.254/Portal/Portal'},
    ],
    'politica_privacidade': 'docs/politica-de-privacidade.pdf',
}

NUMEROS = [
    {'valor': '50 mil m³', 'rotulo': 'de capacidade estática'},
    {'valor': '11', 'rotulo': 'tanques de 1.450 a 8.500 m³'},
    {'valor': '3', 'rotulo': 'linhas de píer'},
    {'valor': '8', 'rotulo': 'baias de carga e descarga'},
]

MODAIS = [
    {
        'icone': 'ship', 'titulo': 'Marítimo',
        'texto': '3 linhas de píer conectam o terminal ao Porto de Cabedelo, que conta com berço dedicado à operação de granéis líquidos.',
        'itens': ['Cais de 602 m de extensão', 'Calado de 11 m'],
    },
    {
        'icone': 'truck', 'titulo': 'Rodoviário',
        'texto': '8 baias de carga e descarga com plataforma automatizada, garantindo agilidade e precisão no atendimento às distribuidoras.',
        'itens': ['BR-230 a 18 km, integrada à BR-101', 'Recife a 120 km e Natal a 185 km'],
    },
    {
        'icone': 'pipe', 'titulo': 'Dutoviário',
        'texto': 'Recebimento e expedição de produtos por dutos, complementando as operações marítimas e rodoviárias do terminal.',
        'itens': ['Recebimento e expedição por dutos'],
    },
]

PRODUTOS = ['Etanol', 'Gasolina', 'Óleo Diesel', 'Biodiesel']

DIFERENCIAIS = [
    {'imagem': 'profissional-qualificado', 'icone': 'users', 'titulo': 'Profissionais qualificados',
     'texto': 'Equipes com treinamentos contínuos, alinhadas às melhores práticas operacionais, de segurança e ambientais.',
     'alt': 'Operador do TECAB com equipamento de proteção utilizando painel de controle'},
    {'imagem': 'plataforma-automatizada', 'icone': 'zap', 'titulo': 'Plataforma automatizada',
     'texto': 'Sistema automatizado de carga e descarga que garante agilidade, precisão e confiabilidade nas operações.',
     'alt': 'Caminhão-tanque na plataforma de carregamento coberta'},
    {'imagem': 'integridade-equipamentos', 'icone': 'wrench', 'titulo': 'Integridade de equipamentos',
     'texto': 'Inspeções regulares de tanques, bombas e tubulações asseguram processos eficientes e sustentáveis.',
     'alt': 'Tubulações e válvulas da casa de bombas do terminal'},
    {'imagem': 'combate-incendio', 'icone': 'flame', 'titulo': 'Combate a incêndio',
     'texto': 'Sistema de combate a incêndio com captação infinita de água do rio, pronto para responder a emergências.',
     'alt': 'Tubulações vermelhas e reservatórios do sistema de combate a incêndio'},
]

CERTIFICACOES = [
    {'imagem': 'iso-9001', 'titulo': 'ISO 9001', 'texto': 'Gestão da Qualidade'},
    {'imagem': 'iso-14001', 'titulo': 'ISO 14001', 'texto': 'Gestão Ambiental'},
    {'imagem': 'iso-45001', 'titulo': 'ISO 45001', 'texto': 'Segurança e Saúde no Trabalho'},
    {'imagem': 'isps-code', 'titulo': 'ISPS Code', 'texto': 'Proteção de Navios e Instalações Portuárias'},
]

CLIENTES = [
    {'chave': 'petrobahia', 'nome': 'Petrobahia', 'url': 'https://www.petrobahia.com.br'},
    {'chave': 'vibra', 'nome': 'Vibra Energia', 'url': 'https://www.vibraenergia.com.br/'},
    {'chave': 'raizen', 'nome': 'Raízen', 'url': 'https://www.raizen.com.br'},
    {'chave': 'ipiranga', 'nome': 'Ipiranga', 'url': 'https://portal.ipiranga/wps/portal/ipiranga/inicio'},
    {'chave': 'ale', 'nome': 'ALE Combustíveis', 'url': 'https://www2.ale.com.br'},
    {'chave': 'temape', 'nome': 'Temape', 'url': 'https://www.temape.com.br/temape'},
    {'chave': 'petrox', 'nome': 'Petrox', 'url': 'https://www.petrox.com.br'},
    {'chave': 'petronac', 'nome': 'Petronac', 'url': 'https://www.petronac.com.br'},
    {'chave': 'meg', 'nome': 'MEG Combustíveis', 'url': 'https://www.megcombustiveis.com.br'},
    {'chave': 'fan', 'nome': 'FAN Distribuidora', 'url': 'https://fandistribuidora.com.br'},
    {'chave': 'larco', 'nome': 'Larco Petróleo', 'url': 'https://www.larcopetroleo.com.br'},
    {'chave': 'sada', 'nome': 'Grupo Sada', 'url': 'https://www.gruposada.com.br'},
    {'chave': 'setta', 'nome': 'Setta Combustíveis', 'url': 'https://settacombustiveis.com.br'},
    {'chave': 'sp', 'nome': 'SP Distribuidora', 'url': 'http://spdistribuidora.com'},
    {'chave': 'dislub', 'nome': 'Dislub Equador', 'url': 'https://dislubenergia.com.br'},
    {'chave': 'federal', 'nome': 'Federal Petróleo', 'url': 'https://www.federalpetroleo.com.br'},
]

HISTORIA = [
    {'ano': '1994', 'titulo': 'Fundação',
     'texto': 'Constituído pelos grupos JB, Tavares de Melo e Família Menezes para atender às operações de '
              'importação e exportação de etanol das usinas da região.'},
    {'ano': '1997', 'titulo': 'Ampliação das operações',
     'texto': 'Para atender às distribuidoras de combustíveis, o terminal passa a armazenar e movimentar derivados '
              'de petróleo (gasolina e óleo diesel) e biocombustíveis (biodiesel).'},
    {'ano': 'Hoje', 'titulo': 'Gestão integrada e certificada',
     'texto': 'Operação pelos modais marítimo, rodoviário e dutoviário, com certificações ISO 9001, ISO 14001, '
              'ISO 45001 e ISPS Code.'},
]

MVV = [
    {'icone': 'target', 'titulo': 'Missão',
     'texto': 'Prover soluções em armazenagem e movimentação de granéis líquidos de forma segura e eficiente.'},
    {'icone': 'eye', 'titulo': 'Visão',
     'texto': 'Ser reconhecido no mercado de terminais de combustíveis pela eficiência e segurança operacional, '
              'impulsionando o desenvolvimento do setor.'},
    {'icone': 'heart', 'titulo': 'Valores',
     'itens': ['Cultura de segurança', 'Ética e confiabilidade', 'Satisfação do cliente',
               'Responsabilidade socioambiental', 'Senso de dono', 'Motivação e engajamento de pessoas']},
]

GALERIA = [
    ('terminal-porto', 'Vista aérea do TECAB com o Porto de Cabedelo ao fundo'),
    ('tancagem-plataforma', 'Tanques de armazenagem e plataforma de carregamento'),
    ('terminal-margem-rio', 'Terminal às margens do rio Paraíba'),
    ('tanques-acesso-rodoviario', 'Parque de tanques e acesso rodoviário'),
    ('plataforma-rodoviaria', 'Plataforma coberta de carga e descarga rodoviária'),
    ('operador-plataforma', 'Operador utilizando o sistema automatizado de carregamento'),
    ('centro-controle', 'Centro de controle operacional'),
    ('casa-bombas', 'Casa de bombas'),
    ('tanques', 'Tanques de armazenagem com escadas de acesso'),
    ('bracos-carregamento', 'Braços de carregamento da plataforma rodoviária'),
    ('teste-combate-incendio', 'Teste do sistema de combate a incêndio'),
    ('instalacoes-aereas', 'Vista aérea das instalações e do pátio de caminhões'),
]

PORTO = {
    'fatos': [
        {'valor': '602 m', 'rotulo': 'de cais'},
        {'valor': '11 m', 'rotulo': 'de calado'},
        {'valor': '18 km', 'rotulo': 'até a BR-230'},
        {'valor': '120 km', 'rotulo': 'até Recife'},
    ],
    'url': 'https://portodecabedelo.pb.gov.br/quem-somos/',
}

POLITICA_SGI = [
    'Assegurar a satisfação dos clientes, visando atender seus requisitos.',
    'Melhorar continuamente a eficácia do Sistema de Gestão Integrado (Qualidade, Meio Ambiente, Segurança e Saúde).',
    'Conscientizar sobre a importância da preservação do meio ambiente.',
    'Comprometer-se com a proteção do meio ambiente, incluindo a prevenção da poluição e a proteção dos recursos hídricos.',
    'Desenvolver programas para atendimento dos objetivos e metas da Gestão Integrada.',
    'Atender à legislação, às normas regulamentares vigentes e a outros requisitos subscritos pela organização.',
    'Eliminar os perigos e reduzir os riscos de segurança e saúde ocupacional.',
    'Proporcionar condições de trabalho seguras e saudáveis para a prevenção de lesões e problemas de saúde.',
    'Envolver, quando necessário, os trabalhadores e seus representantes no desenvolvimento, planejamento, '
    'implementação, avaliação de desempenho e ações de melhoria do SGI.',
]

DOCUMENTOS_ANP = [
    {'titulo': 'Condições Gerais de Serviço do Terminal', 'arquivo': 'docs/condicoes-gerais-de-servico-do-terminal.pdf',
     'codigo': 'DC-GC-0001', 'revisao': 'Rev. 08', 'publicacao': '18/11/2025', 'paginas': 21},
    {'titulo': 'Remuneração de Referência', 'arquivo': 'docs/remuneracao-de-referencia.pdf',
     'codigo': 'DC-GC-0002', 'revisao': 'Rev. 00', 'publicacao': '18/11/2025', 'paginas': 3},
    {'titulo': 'Capacidade Máxima de Movimentação', 'arquivo': 'docs/capacidade-maxima-de-movimentacao.pdf',
     'codigo': 'DC-GC-0003', 'revisao': 'Rev. 04', 'publicacao': '18/11/2025', 'paginas': 4},
]

FORMULARIOS_ANP = [
    {'codigo': 'F.GC.08', 'titulo': 'Solicitação de Serviço', 'arquivo': 'docs/F.GC.08-solicitacao-de-servico.docx'},
    {'codigo': 'F.GC.09', 'titulo': 'Negativa de Acesso', 'arquivo': 'docs/F.GC.09-negativa-de-acesso.docx'},
]

HISTORICO_ANP = [
    {'titulo': 'Histórico de movimentação', 'descricao': 'Resolução ANP nº 881/2022, art. 26 — planilha atualizada.',
     'url': ('https://docs.google.com/spreadsheets/d/119rDrAyWfXNEp70WdmgvA7OMEbbNX1wZ/edit?usp=sharing'
             '&ouid=117270492241327981311&rtpof=true&sd=true'), 'externo': True},
    {'titulo': 'Atendimento à Resolução nº 251/2000', 'descricao': 'Histórico de movimentações até setembro de 2022.',
     'arquivo': 'docs/historico-de-movimentacoes-ate-setembro-2022.xlsx'},
]


def jsonld_empresa(site_url):
    """Dados estruturados (schema.org) da empresa para mecanismos de busca."""
    end = EMPRESA['endereco']
    return {
        '@context': 'https://schema.org',
        '@type': 'LocalBusiness',
        'name': EMPRESA['razao_social'],
        'alternateName': EMPRESA['nome'],
        'description': EMPRESA['descricao'],
        'url': site_url,
        'foundingDate': str(EMPRESA['fundacao']),
        'telephone': EMPRESA['telefone_principal']['tel'],
        'email': EMPRESA['emails'][0]['email'],
        'address': {
            '@type': 'PostalAddress', 'streetAddress': end['logradouro'], 'addressLocality': end['cidade'],
            'addressRegion': end['uf'], 'postalCode': end['cep'], 'addressCountry': 'BR',
        },
        'openingHours': 'Mo-Fr 08:00-18:00',
    }
