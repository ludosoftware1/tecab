import re
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Candidatura, MensagemContato, RelatoIntegridade

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
