from django.contrib import admin

from .models import Candidatura, MensagemContato, RelatoIntegridade

admin.site.site_header = 'TECAB - Administração do site'
admin.site.site_title = 'TECAB'


@admin.register(MensagemContato)
class MensagemContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'assunto', 'email', 'telefone', 'criado_em')
    list_filter = ('assunto', 'criado_em')
    search_fields = ('nome', 'email', 'mensagem')
    readonly_fields = ('criado_em', 'aceite_privacidade')


@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'email', 'telefone', 'criado_em')
    search_fields = ('nome', 'cidade', 'email')
    list_filter = ('cidade', 'criado_em')
    readonly_fields = ('criado_em', 'aceite_privacidade')


@admin.register(RelatoIntegridade)
class RelatoIntegridadeAdmin(admin.ModelAdmin):
    list_display = ('protocolo', 'categoria', 'status', 'identificado', 'criado_em')
    list_filter = ('status', 'categoria', 'criado_em')
    search_fields = ('protocolo', 'descricao')
    readonly_fields = ('protocolo', 'categoria', 'descricao', 'quando_onde', 'envolvidos', 'nome', 'email',
                       'telefone', 'criado_em')
    fieldsets = (
        (None, {'fields': ('protocolo', 'status', 'anotacoes')}),
        ('Relato', {'fields': ('categoria', 'descricao', 'quando_onde', 'envolvidos', 'criado_em')}),
        ('Identificação (opcional)', {'fields': ('nome', 'email', 'telefone')}),
    )

    @admin.display(boolean=True, description='identificado')
    def identificado(self, obj):
        return not obj.anonimo

    def has_add_permission(self, request):
        return False
