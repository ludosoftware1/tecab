import datetime
import io
import os
import re
import shutil
import tempfile
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from . import anp
from .models import Candidatura, MensagemContato, MovimentacaoANP, ProdutoANP, RelatoIntegridade

MEDIA = tempfile.mkdtemp()


class PaginasTests(TestCase):
    def test_paginas_publicas(self):
        for name in ['home', 'quem_somos', 'informacoes_anp', 'contato', 'canal_integridade', 'login',
                     'registrar', 'recuperar_senha']:
            with self.subTest(name=name):
                r = self.client.get(reverse('website:' + name))
                self.assertEqual(r.status_code, 200)
                self.assertContains(r, '<main id="conteudo"')
                self.assertContains(r, '<h1')

    def test_menu_marca_pagina_atual(self):
        r = self.client.get(reverse('website:quem_somos'))
        self.assertContains(r, 'aria-current="page">Quem somos</a>')

    def test_documentos_anp(self):
        r = self.client.get(reverse('website:informacoes_anp'))
        self.assertContains(r, 'condicoes-gerais-de-servico-do-terminal.pdf')
        self.assertContains(r, 'PDF · ')

    def test_imagens_responsivas(self):
        r = self.client.get(reverse('website:home'))
        self.assertRegex(r.content.decode(), r'srcset="[^"]+-640\.webp 640w')

    def test_redirecionamentos_wordpress(self):
        casos = {
            '/?page_id=2174': reverse('website:quem_somos'),
            '/?p=2381': reverse('website:contato'),
            '/?page_id=6953': reverse('website:login'),
            '/?portfolio-item=instalacoes-2': reverse('website:home') + '#diferenciais',
            '/?p=4383': reverse('website:home') + '#diferenciais',
            '/portfolio/tecab/': reverse('website:home') + '#diferenciais',
        }
        for origem, destino in casos.items():
            with self.subTest(origem=origem):
                r = self.client.get(origem)
                self.assertEqual(r.status_code, 301)
                self.assertEqual(r['Location'], destino)

    def test_sitemap_robots_404(self):
        self.assertContains(self.client.get('/sitemap.xml'), '/quem-somos/')
        self.assertContains(self.client.get('/robots.txt'), 'Sitemap:')
        self.assertEqual(self.client.get('/nao-existe/').status_code, 404)


class ContatoTests(TestCase):
    def dados(self, **extra):
        base = {'form_id': 'contato', 'contato-nome': 'Maria', 'contato-email': 'maria@empresa.com',
                'contato-assunto': 'comercial', 'contato-mensagem': 'Gostaria de uma proposta.',
                'contato-aceite_privacidade': 'on'}
        base.update(extra)
        return base

    def test_envio_valido(self):
        r = self.client.post(reverse('website:contato'), self.dados(), follow=True)
        self.assertContains(r, 'Mensagem enviada!')
        self.assertEqual(MensagemContato.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].reply_to, ['maria@empresa.com'])

    def test_erros_e_consentimento(self):
        r = self.client.post(reverse('website:contato'), self.dados(**{'contato-email': 'x', 'contato-aceite_privacidade': ''}))
        self.assertEqual(r.status_code, 400)
        self.assertContains(r, 'Informe um e-mail válido', status_code=400)
        self.assertContains(r, 'concordar com a Política de Privacidade', status_code=400)
        self.assertContains(r, 'aria-invalid="true"', status_code=400)
        self.assertEqual(MensagemContato.objects.count(), 0)

    def test_honeypot_descarta_spam(self):
        r = self.client.post(reverse('website:contato'), self.dados(**{'contato-site_empresa': 'http://spam'}))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(MensagemContato.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)


@override_settings(MEDIA_ROOT=MEDIA)
class TrabalheConoscoTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def dados(self, arquivo):
        return {'form_id': 'trabalhe', 'trabalhe-nome': 'João', 'trabalhe-cidade': 'João Pessoa',
                'trabalhe-email': 'joao@x.com', 'trabalhe-curriculo': arquivo, 'trabalhe-aceite_privacidade': 'on'}

    def test_curriculo_valido(self):
        r = self.client.post(reverse('website:contato'), self.dados(SimpleUploadedFile('cv.pdf', b'%PDF-1.4')))
        self.assertRedirects(r, reverse('website:contato') + '?aba=trabalhe#formularios', fetch_redirect_response=False)
        self.assertEqual(Candidatura.objects.count(), 1)
        self.assertEqual(len(mail.outbox[0].attachments), 1)
        r = self.client.get(r['Location'])
        self.assertContains(r, 'Currículo recebido!')
        self.assertContains(r, 'id="painel-contato" aria-labelledby="aba-contato" tabindex="0" hidden')

    def test_extensao_invalida_abre_aba_certa(self):
        r = self.client.post(reverse('website:contato'), self.dados(SimpleUploadedFile('cv.exe', b'MZ')))
        self.assertContains(r, 'Envie o currículo em PDF, DOC ou DOCX.', status_code=400)
        self.assertContains(r, 'id="painel-contato" aria-labelledby="aba-contato" tabindex="0" hidden', status_code=400)


class CanalIntegridadeTests(TestCase):
    def test_relato_anonimo_gera_protocolo(self):
        r = self.client.post(reverse('website:canal_integridade'), {
            'categoria': 'fraude', 'descricao': 'Descrição detalhada do ocorrido na área X.'}, follow=True)
        relato = RelatoIntegridade.objects.get()
        self.assertTrue(relato.anonimo)
        self.assertRegex(relato.protocolo, r'^TCB-[A-Z0-9]{8}$')
        self.assertContains(r, relato.protocolo)
        # a notificação não inclui o conteúdo do relato
        self.assertNotIn('Descrição detalhada', mail.outbox[0].body)
        # o protocolo só é exibido uma vez
        self.assertRedirects(self.client.get(reverse('website:canal_integridade_enviado')),
                             reverse('website:canal_integridade'))

    def test_descricao_curta(self):
        r = self.client.post(reverse('website:canal_integridade'), {'categoria': 'outros', 'descricao': 'curto'})
        self.assertContains(r, 'pelo menos 20 caracteres', status_code=400)


class AreaColaboradorTests(TestCase):
    def test_exige_login(self):
        r = self.client.get(reverse('website:area_colaborador'))
        self.assertRedirects(r, reverse('website:login') + '?next=' + reverse('website:area_colaborador'))

    def test_cadastro_login_por_email_e_recuperacao(self):
        r = self.client.post(reverse('website:registrar'), {
            'first_name': 'Ana', 'email': 'ana@tecab.com', 'username': 'ana',
            'password1': 'SenhaForte!2026', 'password2': 'SenhaForte!2026'}, follow=True)
        self.assertContains(r, 'Olá, Ana!')
        self.client.post(reverse('website:logout'))

        r = self.client.post(reverse('website:login'), {'username': 'ana@tecab.com', 'password': 'errada'})
        self.assertContains(r, 'Usuário/e-mail ou senha incorretos')
        r = self.client.post(reverse('website:login'), {'username': 'ana@tecab.com', 'password': 'SenhaForte!2026'})
        self.assertRedirects(r, reverse('website:area_colaborador'))
        self.client.post(reverse('website:logout'))

        self.client.post(reverse('website:recuperar_senha'), {'email': 'ana'})
        self.assertEqual(mail.outbox[-1].to, ['ana@tecab.com'])
        link = re.search(r'https?://\S+/redefinir-senha/\S+', mail.outbox[-1].body).group(0)
        r = self.client.get(link.split('testserver', 1)[1], follow=True)
        r = self.client.post(r.redirect_chain[-1][0], {'new_password1': 'OutraSenha!2026',
                                                       'new_password2': 'OutraSenha!2026'})
        self.assertRedirects(r, reverse('website:redefinir_senha_concluido'))
        self.assertTrue(self.client.login(username='ana', password='OutraSenha!2026'))

    def test_email_duplicado(self):
        get_user_model().objects.create_user('x', 'dup@tecab.com', 'SenhaForte!2026')
        r = self.client.post(reverse('website:registrar'), {
            'first_name': 'B', 'email': 'dup@tecab.com', 'username': 'b',
            'password1': 'SenhaForte!2026', 'password2': 'SenhaForte!2026'})
        self.assertContains(r, 'Já existe uma conta com este e-mail')


class MovimentacaoANPTests(TestCase):
    """Painel restrito do histórico de movimentação ANP (a carga inicial vem da migration 0005)."""

    def setUp(self):
        with mock.patch.dict(os.environ, {'TECAB_ANP_USER': 'gestor', 'TECAB_ANP_PASSWORD': 'SenhaForte!2026'}):
            call_command('garantir_usuario_anp', stdout=io.StringIO())
        self.gestor = get_user_model().objects.get(username='gestor')

    def entrar(self):
        self.client.force_login(self.gestor)

    def dados_formset(self, forms, iniciais, campos):
        dados = {'mov-TOTAL_FORMS': str(len(forms)), 'mov-INITIAL_FORMS': str(iniciais), 'mov-MIN_NUM_FORMS': '0',
                 'mov-MAX_NUM_FORMS': '1000'}
        for i, form in enumerate(forms):
            for campo in campos:
                valor = form[campo].value()
                dados['mov-%d-%s' % (i, campo)] = '' if valor is None else valor
        return dados

    def test_carga_inicial_da_planilha(self):
        self.assertEqual(MovimentacaoANP.objects.count(), 735)
        self.assertEqual(ProdutoANP.objects.count(), 6)
        meses = MovimentacaoANP.objects.dates('mes_referencia', 'month')
        self.assertEqual((meses.first(), meses.last()), (datetime.date(2022, 9, 1), datetime.date(2026, 9, 1)))
        m = MovimentacaoANP.objects.get(mes_referencia='2023-02-01', produto__codigo_anp=420102004,
                                        modo_transporte=1, sentido=1)
        self.assertEqual(m.volume_m3, Decimal('57.783'))

    def test_acesso_restrito(self):
        url = reverse('website:anp_painel')
        self.assertRedirects(self.client.get(url), reverse('website:login') + '?next=' + url)
        comum = get_user_model().objects.create_user('comum', 'c@tecab.com', 'SenhaForte!2026')
        self.client.force_login(comum)
        for nome in ('anp_painel', 'anp_importar', 'anp_exportar_xlsx', 'anp_lancamento'):
            with self.subTest(nome=nome):
                self.assertContains(self.client.get(reverse('website:' + nome)), 'Acesso não autorizado',
                                    status_code=403)

    def test_painel_fora_do_menu_e_sem_indexacao(self):
        self.entrar()
        r = self.client.get(reverse('website:anp_painel'))
        self.assertContains(r, 'id="anp-dados"')
        self.assertContains(r, 'vendor/echarts/echarts.min.js')
        self.assertContains(r, 'noindex')
        self.assertEqual(r['X-Robots-Tag'], 'noindex, nofollow')
        self.assertNotContains(self.client.get(reverse('website:home')), '/movimentacao-anp/')
        self.assertNotContains(self.client.get('/robots.txt'), 'movimentacao-anp')
        self.assertNotContains(self.client.get('/sitemap.xml'), 'movimentacao-anp')
        # duplicidade existente na planilha original (02/2023, entrega rodoviária de etanol anidro)
        self.assertContains(r, '2 lançamentos com a mesma combinação')

    def test_lancamento_de_mes_novo(self):
        self.entrar()
        url = reverse('website:anp_lancamento_mes', args=['2026-10'])
        with mock.patch('django.utils.timezone.localdate', return_value=datetime.date(2026, 11, 3)):
            r = self.client.get(url)
            self.assertContains(r, 'repetem as combinações lançadas em')
            forms = r.context['formset'].forms
            self.assertEqual(len(forms), 16)
            dados = self.dados_formset(forms, 0, ('sentido', 'tipo_operacao', 'modo_transporte', 'produto'))
            dados['mov-0-volume_m3'] = '1.234,5'  # separador de milhar não é aceito
            r = self.client.post(url, dados)
            self.assertContains(r, 'Volume inválido', status_code=400)
            dados['mov-0-volume_m3'] = '1234,5'
            dados['mov-1-volume_m3'] = '0'
            r = self.client.post(url, dados)
        self.assertRedirects(r, reverse('website:anp_painel') + '#tabela')
        novos = MovimentacaoANP.objects.filter(mes_referencia='2026-10-01')
        self.assertEqual(novos.count(), 2)  # linhas sem volume são ignoradas
        self.assertEqual(sorted(novos.values_list('volume_m3', flat=True)), [Decimal('0'), Decimal('1234.5')])
        self.assertEqual(novos.first().criado_por, self.gestor)

    def test_lancamento_rejeita_combinacao_repetida(self):
        self.entrar()
        url = reverse('website:anp_lancamento_mes', args=['2026-09'])
        forms = self.client.get(url).context['formset'].forms
        dados = self.dados_formset(forms, len(forms),
                                   ('id', 'sentido', 'tipo_operacao', 'modo_transporte', 'produto', 'volume_m3'))
        for campo in ('sentido', 'tipo_operacao', 'modo_transporte', 'produto'):
            dados['mov-1-%s' % campo] = dados['mov-0-%s' % campo]
        self.assertContains(self.client.post(url, dados), 'Combinação repetida', status_code=400)
        dados['mov-1-DELETE'] = 'on'  # excluir a linha repetida resolve
        self.assertEqual(self.client.post(url, dados).status_code, 302)
        self.assertEqual(MovimentacaoANP.objects.filter(mes_referencia='2026-09-01').count(), len(forms) - 1)

    def test_mes_futuro_ou_invalido(self):
        self.entrar()
        r = self.client.get(reverse('website:anp_lancamento_mes', args=['2099-01']))
        self.assertRedirects(r, reverse('website:anp_lancamento'), fetch_redirect_response=False)
        self.assertEqual(self.client.get(reverse('website:anp_lancamento_mes', args=['2026-13'])).status_code, 404)

    def test_exportar_e_reimportar_planilha(self):
        self.entrar()
        r = self.client.get(reverse('website:anp_exportar_xlsx'))
        self.assertEqual(r.status_code, 200)
        linhas, erros = anp.ler_xlsx(io.BytesIO(r.content))
        self.assertEqual((len(linhas), erros), (735, []))
        MovimentacaoANP.objects.filter(mes_referencia='2026-09-01').update(volume_m3=1)
        arquivo = SimpleUploadedFile('historico.xlsx', r.content)
        r = self.client.post(reverse('website:anp_importar'), {'arquivo': arquivo, 'confirmo': 'on'}, follow=True)
        self.assertContains(r, 'Planilha importada: 735 linha(s) de 49 mês(es)')
        self.assertEqual(MovimentacaoANP.objects.count(), 735)
        self.assertFalse(MovimentacaoANP.objects.filter(mes_referencia='2026-09-01', volume_m3=1).exists())

        linhas_csv = self.client.get(reverse('website:anp_exportar_csv')).content.decode('utf-8-sig').splitlines()
        self.assertEqual(linhas_csv[0].split(';'), anp.CAMPOS)
        self.assertEqual(linhas_csv[1], '2022-09;1033585;TERMINAL TECAB;CABEDELO;PB;1;1;1;810102001;ETANOL ANIDRO;6324,710')

    def test_importacao_com_erros_nao_grava(self):
        import openpyxl

        self.entrar()
        wb = openpyxl.load_workbook(io.BytesIO(self.client.get(reverse('website:anp_exportar_xlsx')).content))
        wb['Dados']['K4'] = 'abc'
        wb['Dados']['F5'] = 7
        saida = io.BytesIO()
        wb.save(saida)
        r = self.client.post(reverse('website:anp_importar'),
                             {'arquivo': SimpleUploadedFile('x.xlsx', saida.getvalue()), 'confirmo': 'on'})
        self.assertContains(r, 'Linha 4: volume inválido', status_code=400)
        self.assertContains(r, 'Linha 5: sentido da operação inválido', status_code=400)
        r = self.client.post(reverse('website:anp_importar'),
                             {'arquivo': SimpleUploadedFile('x.xlsx', b'nao e excel'), 'confirmo': 'on'})
        self.assertContains(r, 'Não foi possível abrir o arquivo', status_code=400)

    def test_situacao_da_publicacao(self):
        self.assertEqual(anp.situacao_publicacao(datetime.date(2026, 10, 15))['status'], 'em_dia')
        s = anp.situacao_publicacao(datetime.date(2026, 11, 10))
        self.assertEqual((s['status'], s['mes'], s['dias']), ('pendente', datetime.date(2026, 10, 1), 5))
        self.assertEqual(anp.situacao_publicacao(datetime.date(2026, 11, 16))['status'], 'atrasado')

    def test_comando_do_usuario_inicial(self):
        self.assertTrue(self.gestor.has_perms(['website.view_movimentacaoanp', 'website.add_movimentacaoanp',
                                               'website.change_movimentacaoanp', 'website.delete_movimentacaoanp']))
        self.assertFalse(self.gestor.is_staff)
        self.assertTrue(self.client.login(username='gestor', password='SenhaForte!2026'))
