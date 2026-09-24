# TECAB – site em Django

Reconstrução em Django do site https://tecab.srv.br/ (originalmente WordPress + tema Stal/Elementor),
com todos os assets servidos localmente.

## Executar com Docker

```bash
cp .env.example .env        # ajuste DJANGO_SECRET_KEY e, se quiser, TECAB_PORT
docker compose up -d --build
```

O site sobe em `http://localhost:8090` (ou na porta definida em `TECAB_PORT`).
Banco SQLite e uploads (currículos) ficam no volume `tecab2-data`.

Criar um usuário administrador (para ver mensagens e candidaturas em `/admin/`):

```bash
docker compose exec web python manage.py createsuperuser
```

## Executar localmente (desenvolvimento)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `website/templates/website/base.html` | Cabeçalho, menus, rodapé e CSS/JS comuns a todas as páginas |
| `website/templates/website/pages/` | Home, Quem Somos, Informações ANP, Área do Colaborador, Contato |
| `website/templates/website/portfolio/` | Itens e categorias do portfólio |
| `website/templates/website/accounts/` | Login, cadastro e recuperação de senha |
| `website/templates/website/forms/` | Formulários "Contato" e "Trabalhe Conosco" |
| `website/static/` | Assets baixados do site original (mesma estrutura `wp-content/`, `wp-includes/`) e fontes do Google em `fonts/google/` |
| `website/pages.py` | Registro das páginas, IDs antigos do WordPress e itens do menu |

## Rotas

| Nova URL | URL original |
|---|---|
| `/` | `/` |
| `/quem-somos/` | `/?page_id=2174` |
| `/informacoes-anp/` | `/?page_id=5331` |
| `/area-do-colaborador/` | `/?page_id=6946` |
| `/contato/` | `/?page_id=2381` |
| `/login/`, `/registrar/`, `/recuperar-senha/` | `/?page_id=6953`, `6954`, `6958` |
| `/portfolio/<slug>/` | `/?portfolio-item=<slug>` |
| `/portfolio-category/<slug>/` | `/?portfolio-category=<slug>` |

Os endereços antigos (`?page_id=`, `?p=`, `?portfolio-item=`, `?portfolio-category=`) redirecionam (301) para os novos.

## Funcionalidades

- **Contato / Trabalhe Conosco**: grava no banco (visível no admin) e envia e-mail para
  `TECAB_CONTATO_DESTINATARIOS` (o currículo vai anexado). Mantém o visual e as mensagens do Contact Form 7.
- **Área do Colaborador**: login (por usuário ou e-mail), cadastro e recuperação de senha com a aparência do
  Ultimate Member, usando a autenticação do Django.
- E-mails saem no console por padrão; para SMTP configure as variáveis `DJANGO_EMAIL_*` (veja `.env.example`).
