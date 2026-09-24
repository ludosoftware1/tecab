"""Catálogo de imagens do site.

Cada entrada gera variantes WebP em `static/img/<chave>-<largura>.webp` pelo comando
`python manage.py gerar_imagens` (os originais ficam em `assets_src/`, fora do repositório).

Formato: chave -> (arquivo de origem, larguras, proporção de recorte (largura/altura) ou None, aparar transparência)
"""

FOTO = [480, 960, 1600]
FOTO_GRANDE = [640, 1024, 1600, 2400]

IMAGES = {
    # Fotos do terminal
    'terminal-aereo-rio': ('fotos/terminal-aereo-rio.png', FOTO_GRANDE, 16 / 9, False),
    'terminal-porto': ('fotos/terminal-porto.jpg', FOTO_GRANDE, 16 / 9, False),
    'terminal-margem-rio': ('fotos/terminal-margem-rio.jpg', FOTO, 3 / 2, False),
    'terminal-vertical': ('fotos/terminal-vertical.jpg', FOTO, 3 / 4, False),
    'tancagem-plataforma': ('fotos/tancagem-plataforma.jpg', FOTO, 3 / 2, False),
    'tanques-acesso-rodoviario': ('fotos/tanques-acesso-rodoviario.jpg', FOTO, 3 / 2, False),
    'plataforma-rodoviaria': ('fotos/plataforma-rodoviaria.jpg', FOTO, 3 / 2, False),
    'operador-plataforma': ('fotos/operador-plataforma.jpg', FOTO, 3 / 2, False),
    'centro-controle': ('fotos/centro-controle.jpg', FOTO, 3 / 2, False),
    'casa-bombas': ('fotos/casa-bombas.jpg', FOTO, 3 / 2, False),
    'tanques': ('fotos/tanques.jpg', FOTO, 3 / 2, False),
    'bracos-carregamento': ('fotos/bracos-carregamento.jpg', FOTO, 3 / 2, False),
    'teste-combate-incendio': ('fotos/teste-combate-incendio.jpg', FOTO, 3 / 2, False),
    'instalacoes-aereas': ('fotos/instalacoes-aereas.jpg', FOTO, 3 / 2, False),
    'instalacoes-porto': ('fotos/instalacoes-porto.jpg', FOTO, 3 / 2, False),
    'porto-navio': ('fotos/porto-navio.jpg', FOTO, 3 / 2, False),
    'porto-cabedelo': ('fotos/porto-cabedelo.jpg', [480, 876], None, False),
    'video-capa': ('fotos/video-capa.png', [960, 1528], 16 / 9, False),
    # Cabeçalhos das páginas internas
    'banner-tanques': ('fotos/banner-tanques.png', [960, 1600, 2400], 3, False),
    'banner-tanque-logo': ('fotos/banner-tanque-logo.png', [960, 1600, 2400], 3, False),
    'banner-porto': ('fotos/banner-porto.png', [960, 1600, 2400], 3, False),
    # Diferenciais
    'profissional-qualificado': ('fotos/profissional-qualificado.png', [480, 800], 4 / 3, False),
    'plataforma-automatizada': ('fotos/plataforma-automatizada.jpg', [480, 800], 4 / 3, False),
    'integridade-equipamentos': ('fotos/integridade-equipamentos.jpg', [480, 800], 4 / 3, False),
    'combate-incendio': ('fotos/combate-incendio.jpg', [480, 800], 4 / 3, False),
    # Marca
    'logo': ('marca/logo.png', [120, 240], None, True),
    'logo-branco': ('marca/logo-branco.png', [120, 240], None, True),
    # Certificações
    'iso-9001': ('certificacoes/iso-9001.png', [120, 240], None, True),
    'iso-14001': ('certificacoes/iso-14001.png', [120, 240], None, True),
    'iso-45001': ('certificacoes/iso-45001.png', [120, 240], None, True),
    'isps-code': ('certificacoes/isps-code.png', [120, 240], None, True),
}

CLIENTES = ['petrobahia', 'vibra', 'raizen', 'ipiranga', 'ale', 'temape', 'petrox', 'petronac', 'meg', 'fan',
            'larco', 'sada', 'setta', 'sp', 'dislub', 'federal']
for _cliente in CLIENTES:
    IMAGES['cliente-' + _cliente] = ('clientes/%s.png' % _cliente, [240, 480], None, False)
