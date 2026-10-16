"""Gestão do histórico de movimentação ANP (área restrita, acessível apenas pelo link direto)."""
import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.forms import modelformset_factory
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from . import anp
from .forms import BaseLancamentoFormSet, ImportarPlanilhaForm, MovimentacaoForm
from .models import MovimentacaoANP, ProdutoANP

VER = 'website.view_movimentacaoanp'
EDITAR = ('website.add_movimentacaoanp', 'website.change_movimentacaoanp', 'website.delete_movimentacaoanp')


def restrito(perms):
    """Exige login; usuário logado sem a permissão recebe 403 (e não um novo pedido de login)."""
    def decorator(view):
        return login_required(permission_required(perms, raise_exception=True)(view))
    return decorator


def _sem_indexacao(response):
    response['X-Robots-Tag'] = 'noindex, nofollow'
    response['Cache-Control'] = 'private, no-store'
    return response


@require_GET
@restrito(VER)
def painel(request):
    movimentacoes = list(MovimentacaoANP.objects.select_related('produto'))
    produtos = list(ProdutoANP.objects.order_by('pk'))
    return _sem_indexacao(render(request, 'website/anp/painel.html', {
        'dados': anp.dados_painel(movimentacoes, produtos),
        'situacao': anp.situacao_publicacao(),
        'avisos': anp.pontos_de_atencao(movimentacoes),
        'atualizado_em': anp.data_atualizacao(),
        'pode_editar': request.user.has_perms(EDITAR),
        'terminal': anp.TERMINAL,
    }))


def _mes_da_url(valor):
    try:
        return anp.mes_para_data(valor)
    except ValueError:
        raise Http404('Mês inválido.')


@require_http_methods(['GET', 'POST'])
@restrito(EDITAR)
def lancamento(request, mes=None):
    if mes is None:
        # Sem mês na URL: o mês seguinte ao último lançado (ou o mês anterior ao atual).
        escolhido = request.GET.get('mes')
        if escolhido:
            return redirect('website:anp_lancamento_mes', mes=_mes_da_url(escolhido).strftime('%Y-%m'))
        ultimo = MovimentacaoANP.objects.order_by('-mes_referencia').values_list('mes_referencia', flat=True).first()
        alvo = anp.mes_seguinte(ultimo) if ultimo else anp.mes_seguinte(timezone.localdate().replace(day=1), -1)
        return redirect('website:anp_lancamento_mes', mes=alvo.strftime('%Y-%m'))

    data = _mes_da_url(mes)
    if data > timezone.localdate():
        messages.error(request, 'Não é possível lançar um mês que ainda não começou.')
        return redirect('website:anp_lancamento')

    queryset = MovimentacaoANP.objects.filter(mes_referencia=data).select_related('produto')
    novo = not queryset.exists()
    initial = []
    base = None
    if novo:
        # Mês vazio: sugere as mesmas combinações do último mês lançado antes dele, com o volume em branco.
        base = (MovimentacaoANP.objects.filter(mes_referencia__lt=data).order_by('-mes_referencia')
                .values_list('mes_referencia', flat=True).first())
        if base:
            initial = [{'sentido': m.sentido, 'tipo_operacao': m.tipo_operacao, 'modo_transporte': m.modo_transporte,
                        'produto': m.produto_id}
                       for m in MovimentacaoANP.objects.filter(mes_referencia=base, produto__ativo=True)]
    FormSet = modelformset_factory(MovimentacaoANP, form=MovimentacaoForm, formset=BaseLancamentoFormSet,
                                   extra=len(initial) if novo else 0, can_delete=True)

    formset = FormSet(request.POST or None, queryset=queryset, initial=initial or None, prefix='mov')
    if request.method == 'POST' and formset.is_valid():
        with transaction.atomic():
            objetos = formset.save(commit=False)
            for obj in objetos:
                obj.mes_referencia = data
                if not obj.pk:
                    obj.criado_por = request.user
                obj.atualizado_por = request.user
                obj.save()
            for obj in formset.deleted_objects:
                obj.delete()
        alterados = len(objetos) + len(formset.deleted_objects)
        if alterados:
            messages.success(request, 'Movimentação de %s salva: %d linha(s) gravada(s), %d excluída(s).'
                             % (data.strftime('%m/%Y'), len(objetos), len(formset.deleted_objects)))
        else:
            messages.success(request, 'Nenhuma alteração em %s.' % data.strftime('%m/%Y'))
        return redirect(reverse('website:anp_painel') + '#tabela')

    meses = list(MovimentacaoANP.objects.dates('mes_referencia', 'month', order='DESC'))
    return _sem_indexacao(render(request, 'website/anp/lancamento.html', {
        'formset': formset, 'mes': data, 'novo': novo, 'base': base,
        'anterior': anp.mes_seguinte(data, -1), 'seguinte': anp.mes_seguinte(data),
        'mes_atual': timezone.localdate().replace(day=1), 'meses': meses,
    }, status=400 if request.method == 'POST' else 200))


@require_http_methods(['GET', 'POST'])
@restrito(EDITAR)
def importar(request):
    form = ImportarPlanilhaForm(request.POST or None, request.FILES or None)
    erros = []
    if request.method == 'POST' and form.is_valid():
        try:
            linhas, erros = anp.ler_xlsx(form.cleaned_data['arquivo'])
        except anp.PlanilhaInvalida as exc:
            form.add_error('arquivo', str(exc))
        else:
            if not erros and not linhas:
                form.add_error('arquivo', 'A aba "Dados" não tem nenhuma linha de movimentação.')
            elif not erros:
                r = anp.importar(linhas, request.user)
                messages.success(request, 'Planilha importada: %d linha(s) de %d mês(es), de %s a %s. %d lançamento(s) '
                                 'anterior(es) desses meses foram substituídos.'
                                 % (r['linhas'], r['meses'], r['primeiro'].strftime('%m/%Y'),
                                    r['ultimo'].strftime('%m/%Y'), r['removidas']))
                return redirect('website:anp_painel')
    return _sem_indexacao(render(request, 'website/anp/importar.html', {'form': form, 'erros': erros[:50],
                                                                        'total_erros': len(erros)},
                                 status=400 if request.method == 'POST' else 200))


def _nome_arquivo(extensao):
    return 'historico-movimentacao-tecab-%s.%s' % (timezone.localdate().strftime('%Y-%m-%d'), extensao)


@require_GET
@restrito(VER)
def exportar_xlsx(request):
    response = HttpResponse(anp.exportar_xlsx(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="%s"' % _nome_arquivo('xlsx')
    return _sem_indexacao(response)


@require_GET
@restrito(VER)
def exportar_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="%s"' % _nome_arquivo('csv')
    response.write('﻿')  # BOM: o Excel reconhece o UTF-8
    writer = csv.writer(response, delimiter=';')
    for linha in anp.linhas_csv():
        writer.writerow(linha)
    return _sem_indexacao(response)
