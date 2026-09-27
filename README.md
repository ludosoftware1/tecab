# TECAB – site institucional (Django)

Site do TECAB – Terminais de Armazenagens de Cabedelo, reconstruído em Django com layout próprio,
mantendo a identidade visual da empresa (vermelho `#ee0d08`, grafite `#101010`, cinza-claro `#f1f3f5`, fonte Mulish).

## Executar com Docker

```bash
cp .env.example .env        # defina DJANGO_SECRET_KEY, POSTGRES_PASSWORD, DJANGO_ADMIN_* e, se quiser, TECAB_PORT
./build.sh                  # git pull + docker compose up -d --build
```

O site sobe em `http://localhost:8090` (ou na porta de `TECAB_PORT`). O banco é PostgreSQL (serviço `db`,
volume `tecab2-pgdata`); os currículos enviados ficam no volume `tecab2-data` (`/data/media`).

**Container do PostgreSQL opcional:** no `.env`, `COMPOSE_PROFILES=postgres` sobe o container do banco junto
com o site. Deixe `COMPOSE_PROFILES=` vazio para não subir e usar um PostgreSQL externo, informando
`POSTGRES_HOST`/`POSTGRES_PORT` (para um banco no próprio servidor use `POSTGRES_HOST=host.docker.internal`).

**Migração do SQLite:** se o volume `tecab2-data` tiver o `db.sqlite3` da versão anterior, a migration
`website.0003_importar_sqlite` copia todos os dados dele (usuários e senhas, grupos, permissões, sessões,
histórico do admin, mensagens, candidaturas e relatos) para o PostgreSQL, com os mesmos IDs, na primeira
inicialização. O arquivo SQLite é mantido como cópia de segurança.

**Administrador:** a cada inicialização o container cria/atualiza o superusuário definido em
`DJANGO_ADMIN_USER` / `DJANGO_ADMIN_PASSWORD` / `DJANGO_ADMIN_EMAIL` (o `.env` é a fonte da senha; para
trocá-la, altere o `.env` e rode `./build.sh`). Acesso em `/admin/`.

## Desenvolvimento

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
python manage.py test website   # suíte de testes
```

## Onde editar o conteúdo

| O quê | Onde |
|---|---|
| Telefones, e-mails, endereço, horários, links do Portal do Cliente | `website/content.py` → `EMPRESA` |
| Números do terminal, modais, diferenciais, clientes, certificações, galeria, documentos ANP | `website/content.py` |
| Textos das páginas | `website/templates/website/pages/` |
| Cores, tipografia e componentes | `website/static/css/site.css` (variáveis no início do arquivo) |
| Documentos (PDF/DOCX/XLSX) | `website/static/docs/` + `website/content.py` |

### Imagens

As imagens são servidas em WebP responsivo (várias larguras), geradas a partir dos originais:

1. Coloque o original em `assets_src/` (pasta fora do repositório).
2. Registre-o em `website/images.py` (chave, larguras e recorte).
3. Rode `python manage.py gerar_imagens` (use `--extras` para regenerar favicons e a imagem de compartilhamento).
4. Use no template: `{% picture 'chave' 'texto alternativo' '(max-width: 900px) 100vw, 50vw' %}`.

## Páginas e funcionalidades

| Rota | Conteúdo |
|---|---|
| `/` | Apresentação, números do terminal, modais, diferenciais, certificações, clientes |
| `/quem-somos/` | História, vídeo, missão/visão/valores, galeria, Porto de Cabedelo, política do SGI, ética |
| `/informacoes-anp/` | Documentos da Resolução ANP 881/2022, formulários e histórico de movimentações |
| `/contato/` | Telefones por setor, e-mails, horários, formulários "Fale conosco" e "Trabalhe conosco", mapa |
| `/canal-de-integridade/` | Relatos anônimos (ou identificados) com número de protocolo |
| `/area-do-colaborador/` | Área restrita: login por usuário ou e-mail, cadastro, recuperação e troca de senha |
| `/sitemap.xml`, `/robots.txt` | SEO |

Os endereços antigos do WordPress (`?page_id=`, `?p=`, `?portfolio-item=`...) redirecionam (301) para as novas rotas.

Os formulários gravam no banco (visível no admin) e enviam e-mail para `TECAB_CONTATO_DESTINATARIOS`;
os relatos do Canal de Integridade notificam `TECAB_INTEGRIDADE_DESTINATARIOS` **sem** incluir o conteúdo do
relato no e-mail. Por padrão os e-mails saem no console; configure SMTP pelas variáveis `DJANGO_EMAIL_*`
(veja `.env.example`). Em produção com HTTPS, defina `DJANGO_HTTPS=1`.
