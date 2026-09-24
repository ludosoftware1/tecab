from django.contrib import admin

from .models import Candidatura, MensagemContato


@admin.register(MensagemContato)
class MensagemContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'criado_em')
    search_fields = ('nome', 'email', 'mensagem')
    readonly_fields = ('criado_em',)


@admin.register(Candidatura)
class CandidaturaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'email', 'telefone', 'criado_em')
    search_fields = ('nome', 'cidade', 'email')
    list_filter = ('cidade',)
    readonly_fields = ('criado_em',)
