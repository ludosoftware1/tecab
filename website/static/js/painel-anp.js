/* TECAB — Painel de movimentação ANP (gráficos com Apache ECharts) e lançamento mensal. */
(function () {
  'use strict';

  var LOCALE = 'pt-BR';
  var fmtInt = new Intl.NumberFormat(LOCALE, { maximumFractionDigits: 0 });
  var fmtVol = new Intl.NumberFormat(LOCALE, { minimumFractionDigits: 2, maximumFractionDigits: 3 });
  var fmtPct = new Intl.NumberFormat(LOCALE, { style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1 });
  var fmtCompact = new Intl.NumberFormat(LOCALE, { notation: 'compact', maximumFractionDigits: 1 });
  var MESES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function el(tag, attrs, text) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (text != null) e.textContent = text;
    return e;
  }

  /* ======================================================================= lançamento mensal */
  function initLancamento(form) {
    var total = form.querySelector('input[name$="-TOTAL_FORMS"]');
    var tbody = form.querySelector('[data-rows]');
    var template = form.querySelector('template[data-empty-row]');

    function parseVolume(v) {
      v = (v || '').trim().replace(/\s/g, '');
      if (!v) return null;
      if (v.indexOf(',') >= 0) v = v.replace(/\./g, '').replace(',', '.');
      var n = Number(v);
      return isFinite(n) ? n : null;
    }
    function somar() {
      var soma = { 1: 0, 2: 0 };
      tbody.querySelectorAll('tr[data-row]').forEach(function (tr) {
        if (tr.classList.contains('is-removed') || tr.classList.contains('is-deleting')) return;
        var sentido = tr.querySelector('select[name$="-sentido"]');
        var vol = parseVolume((tr.querySelector('input[name$="-volume_m3"]') || {}).value);
        if (sentido && vol != null && soma[sentido.value] != null) soma[sentido.value] += vol;
      });
      form.querySelectorAll('[data-soma]').forEach(function (td) {
        td.textContent = fmtVol.format(soma[td.dataset.soma]) + ' m³';
      });
    }
    function prepararLinha(tr) {
      var remover = tr.querySelector('[data-remove-row]');
      if (remover) {
        remover.addEventListener('click', function () {
          var del = tr.querySelector('input[name$="-DELETE"]');
          if (del) del.checked = true;
          tr.classList.add('is-removed');
          somar();
        });
      }
      var excluir = tr.querySelector('.check input[name$="-DELETE"]');
      if (excluir) {
        var sync = function () { tr.classList.toggle('is-deleting', excluir.checked); somar(); };
        excluir.addEventListener('change', sync);
        sync();
      }
    }
    tbody.querySelectorAll('tr[data-row]').forEach(prepararLinha);
    form.addEventListener('input', somar);
    form.addEventListener('change', somar);
    var add = form.querySelector('[data-add-row]');
    if (add && template && total) {
      add.addEventListener('click', function () {
        var i = parseInt(total.value, 10);
        var html = template.innerHTML.replace(/__prefix__/g, String(i));
        var holder = document.createElement('tbody');
        holder.innerHTML = html.trim();
        var tr = holder.firstElementChild;
        tbody.appendChild(tr);
        total.value = String(i + 1);
        prepararLinha(tr);
        var first = tr.querySelector('select, input:not([type="hidden"])');
        if (first) first.focus();
        somar();
      });
    }
    somar();
  }

  /* ======================================================================= painel */
  // Paleta categórica validada (ordem fixa; a cor acompanha o produto, nunca a posição no ranking).
  var SERIES = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948'];
  var COR = {
    recepcao: '#6250d6', entrega: '#e34948', outros: '#868b91',
    ink: '#101010', ink2: '#5a5f65', muted: '#868b91', grid: '#e9ebee', axis: '#cfd4da', surface: '#ffffff',
    seq: ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#256abf', '#184f95', '#0d366b'],
  };
  var FONTE = 'Mulish, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';

  function mesIdx(m) { var p = m.split('-'); return parseInt(p[0], 10) * 12 + parseInt(p[1], 10) - 1; }
  function idxMes(i) { var y = Math.floor(i / 12), mm = i % 12 + 1; return y + '-' + (mm < 10 ? '0' : '') + mm; }
  function rotuloMes(m) { var p = m.split('-'); return MESES[parseInt(p[1], 10) - 1] + '/' + p[0].slice(2); }
  function rotuloMesLongo(m) { var p = m.split('-'); return p[1] + '/' + p[0]; }
  function m3(v) { return fmtInt.format(Math.round(v)) + ' m³'; }

  function initPainel(dados) {
    var linhas = dados.linhas.map(function (l) {
      return { id: l[0], mes: l[1], idx: mesIdx(l[1]), sentido: l[2], tipo: l[3], modo: l[4], produto: l[5], volume: l[6] };
    });
    var produtos = dados.produtos;
    var corProduto = {}, nomeProduto = {};
    produtos.forEach(function (p, i) { corProduto[p.id] = SERIES[i] || COR.outros; nomeProduto[p.id] = p.nome; });
    var mesesComDados = {};
    linhas.forEach(function (l) { mesesComDados[l.idx] = true; });
    var idxs = Object.keys(mesesComDados).map(Number).sort(function (a, b) { return a - b; });
    var primeiro = idxs[0], ultimo = idxs[idxs.length - 1];
    var urlLancamento = (document.getElementById('tabela') || {}).dataset ? document.getElementById('tabela').dataset.lancamento : null;

    /* ------------------------------------------------------------ filtros */
    var f = {
      periodo: document.getElementById('f-periodo'), de: document.getElementById('f-de'),
      ate: document.getElementById('f-ate'), sentido: document.getElementById('f-sentido'),
      modo: document.getElementById('f-modo'), produto: document.getElementById('f-produto'),
    };
    function opt(select, value, label) { select.appendChild(el('option', { value: value }, label)); }
    opt(f.periodo, 'u12', 'Últimos 12 meses');
    opt(f.periodo, 'u24', 'Últimos 24 meses');
    var anos = [];
    for (var y = Math.floor(ultimo / 12); y >= Math.floor(primeiro / 12); y--) anos.push(y);
    anos.forEach(function (a) { opt(f.periodo, 'a' + a, String(a)); });
    opt(f.periodo, 'tudo', 'Todo o histórico');
    opt(f.periodo, 'custom', 'Personalizado…');
    for (var i = ultimo; i >= primeiro; i--) { opt(f.de, String(i), rotuloMesLongo(idxMes(i))); opt(f.ate, String(i), rotuloMesLongo(idxMes(i))); }
    Object.keys(dados.sentidos).forEach(function (k) { opt(f.sentido, k, dados.sentidos[k]); });
    var modosUsados = {};
    linhas.forEach(function (l) { modosUsados[l.modo] = true; });
    Object.keys(dados.modos).forEach(function (k) { if (modosUsados[k]) opt(f.modo, k, dados.modos[k]); });
    produtos.forEach(function (p) { opt(f.produto, String(p.id), p.nome); });

    // estado inicial a partir da URL (links com filtros podem ser compartilhados)
    var qs = new URLSearchParams(window.location.search);
    function setIf(select, v) { if (v != null && select.querySelector('option[value="' + CSS.escape(v) + '"]')) select.value = v; }
    setIf(f.periodo, qs.get('periodo') || 'u12');
    setIf(f.de, qs.get('de') ? String(mesIdx(qs.get('de'))) : String(Math.max(primeiro, ultimo - 11)));
    setIf(f.ate, qs.get('ate') ? String(mesIdx(qs.get('ate'))) : String(ultimo));
    setIf(f.sentido, qs.get('sentido'));
    setIf(f.modo, qs.get('modal'));
    setIf(f.produto, qs.get('produto'));

    function intervalo() {
      var p = f.periodo.value;
      if (p === 'u12') return [Math.max(primeiro, ultimo - 11), ultimo];
      if (p === 'u24') return [Math.max(primeiro, ultimo - 23), ultimo];
      if (p === 'tudo') return [primeiro, ultimo];
      if (p.charAt(0) === 'a') { var a = parseInt(p.slice(1), 10); return [Math.max(primeiro, a * 12), Math.min(ultimo, a * 12 + 11)]; }
      var de = parseInt(f.de.value, 10), ate = parseInt(f.ate.value, 10);
      return de <= ate ? [de, ate] : [ate, de];
    }
    function filtroDimensoes(l, ignorar) {
      ignorar = ignorar || {};
      if (!ignorar.sentido && f.sentido.value && l.sentido !== +f.sentido.value) return false;
      if (!ignorar.modo && f.modo.value && l.modo !== +f.modo.value) return false;
      if (f.produto.value && l.produto !== +f.produto.value) return false;
      return true;
    }
    function sincronizarUrl(r) {
      if (!history.replaceState) return;
      var u = new URL(window.location.href);
      u.search = '';
      if (f.periodo.value !== 'u12') u.searchParams.set('periodo', f.periodo.value);
      if (f.periodo.value === 'custom') { u.searchParams.set('de', idxMes(r[0])); u.searchParams.set('ate', idxMes(r[1])); }
      if (f.sentido.value) u.searchParams.set('sentido', f.sentido.value);
      if (f.modo.value) u.searchParams.set('modal', f.modo.value);
      if (f.produto.value) u.searchParams.set('produto', f.produto.value);
      history.replaceState(null, '', u);
    }

    /* ------------------------------------------------------------ agregações */
    function porMes(rows, ini, fim, valor) {
      // vetor alinhado aos meses ini..fim; null para meses sem nenhum lançamento (lacuna real)
      var out = [];
      for (var k = ini; k <= fim; k++) out.push(mesesComDados[k] ? 0 : null);
      rows.forEach(function (l) {
        if (l.idx < ini || l.idx > fim) return;
        var v = valor ? valor(l) : l.volume;
        if (v) out[l.idx - ini] = (out[l.idx - ini] || 0) + v;
      });
      return out;
    }
    function soma(rows, pred) { return rows.reduce(function (s, l) { return pred && !pred(l) ? s : s + l.volume; }, 0); }
    function coberto(ini, fim) { for (var k = ini; k <= fim; k++) if (!mesesComDados[k]) return false; return true; }

    /* ------------------------------------------------------------ ECharts: base comum */
    var charts = {};
    function chart(id) {
      if (!charts[id]) {
        var node = document.getElementById(id);
        charts[id] = echarts.init(node, null, { locale: 'PT-br', renderer: 'canvas' });
      }
      return charts[id];
    }
    var reduzirMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    function base(extra) {
      var o = {
        animation: !reduzirMovimento, animationDuration: 400,
        textStyle: { fontFamily: FONTE, color: COR.ink2 },
        grid: { left: 8, right: 16, top: 44, bottom: 8, containLabel: true },
        tooltip: {
          trigger: 'axis', confine: true, backgroundColor: '#fff', borderColor: '#e2e5e9', borderWidth: 1,
          padding: [8, 12], textStyle: { color: COR.ink, fontFamily: FONTE, fontSize: 13 },
          extraCssText: 'box-shadow:0 8px 24px -8px rgb(16 16 16 / .25);border-radius:10px;',
          axisPointer: { type: 'line', lineStyle: { color: COR.axis, width: 1 } },
        },
        legend: { top: 0, left: 0, icon: 'roundRect', itemWidth: 12, itemHeight: 12, itemGap: 16,
                  textStyle: { color: COR.ink2, fontFamily: FONTE, fontSize: 12 } },
      };
      return Object.assign(o, extra);
    }
    function eixoValor(extra) {
      return Object.assign({
        type: 'value', axisLine: { show: false }, axisTick: { show: false },
        splitLine: { lineStyle: { color: COR.grid, width: 1, type: 'solid' } },
        axisLabel: { color: COR.muted, fontSize: 11, formatter: function (v) { return fmtCompact.format(v); } },
      }, extra || {});
    }
    function eixoMeses(meses, extra) {
      return Object.assign({
        type: 'category', data: meses.map(rotuloMes),
        axisLine: { lineStyle: { color: COR.axis } }, axisTick: { show: false },
        axisLabel: { color: COR.muted, fontSize: 11, hideOverlap: true },
      }, extra || {});
    }
    function zoom(n) {
      if (n <= 24) return [];
      return [{ type: 'inside', start: Math.max(0, 100 - 2400 / n), end: 100 },
              { type: 'slider', height: 18, bottom: 4, start: Math.max(0, 100 - 2400 / n), end: 100,
                borderColor: 'transparent', backgroundColor: '#f1f3f5', fillerColor: 'rgba(16,16,16,.08)',
                dataBackground: { lineStyle: { color: COR.axis }, areaStyle: { color: '#e9ebee' } },
                handleStyle: { color: '#fff', borderColor: COR.axis }, textStyle: { color: COR.muted, fontSize: 10 },
                labelFormatter: '' }];
    }
    // linha do tooltip: valor em destaque, nome da série depois, chave curta na cor da série
    function linhaTooltip(cor, nome, valor) {
      return '<div style="display:flex;align-items:center;gap:8px;line-height:1.7">' +
        '<span style="display:inline-block;width:12px;height:3px;border-radius:2px;background:' + cor + '"></span>' +
        '<strong style="font-variant-numeric:tabular-nums">' + esc(valor) + '</strong>' +
        '<span style="color:' + COR.ink2 + '">' + esc(nome) + '</span></div>';
    }
    function tituloTooltip(t) { return '<div style="font-weight:800;margin-bottom:2px">' + esc(t) + '</div>'; }
    function vazio(msg) {
      return { title: { text: msg, left: 'center', top: 'middle',
                        textStyle: { color: COR.muted, fontSize: 13, fontWeight: 600, fontFamily: FONTE } },
               xAxis: { show: false }, yAxis: { show: false }, series: [] };
    }
    var BARRA = { type: 'bar', barMaxWidth: 24, itemStyle: { borderRadius: [4, 4, 0, 0] }, emphasis: { focus: 'none' } };

    /* ------------------------------------------------------------ indicadores */
    function kpi(nome, valor, unidade) {
      var node = document.querySelector('[data-kpi="' + nome + '"]');
      node.textContent = valor;
      if (unidade) node.appendChild(el('small', null, unidade));
    }
    function nota(nome, texto) { var n = document.querySelector('[data-kpi-note="' + nome + '"]'); if (n) n.textContent = texto || ''; }
    function delta(nome, atual, anterior, rotulo) {
      var node = document.querySelector('[data-delta="' + nome + '"]');
      node.textContent = '';
      if (anterior == null || !anterior) { if (rotulo) node.textContent = 'Sem base para ' + rotulo; return; }
      var d = (atual - anterior) / anterior;
      var span = el('span', { 'class': d > 0.0005 ? 'up' : d < -0.0005 ? 'down' : '' },
                    (d > 0.0005 ? '▲ ' : d < -0.0005 ? '▼ ' : '● ') + fmtPct.format(Math.abs(d)));
      node.appendChild(span);
      node.appendChild(document.createTextNode(' vs. ' + rotulo));
    }

    function atualizarKpis(rows, r, ini, fim) {
      var semSentido = !!f.sentido.value;
      var total = soma(rows);
      var rec = soma(rows, function (l) { return l.sentido === 1; });
      var ent = soma(rows, function (l) { return l.sentido === 2; });
      kpi('total', fmtInt.format(Math.round(total)), 'm³');
      kpi('recepcao', f.sentido.value === '2' ? '—' : fmtInt.format(Math.round(rec)), f.sentido.value === '2' ? '' : 'm³');
      kpi('entrega', f.sentido.value === '1' ? '—' : fmtInt.format(Math.round(ent)), f.sentido.value === '1' ? '' : 'm³');

      // mesmo período do ano anterior (só quando todos os meses existem no histórico)
      var antIni = ini - 12, antFim = fim - 12;
      var rotuloAnt = 'o mesmo período ' + (fim - ini >= 12 ? 'anterior' : 'de ' + Math.floor(antFim / 12));
      if (coberto(antIni, antFim)) {
        var anteriores = linhas.filter(function (l) { return l.idx >= antIni && l.idx <= antFim && filtroDimensoes(l); });
        delta('total', total, soma(anteriores), rotuloAnt);
        delta('recepcao', rec, f.sentido.value === '2' ? null : soma(anteriores, function (l) { return l.sentido === 1; }), f.sentido.value === '2' ? '' : rotuloAnt);
        delta('entrega', ent, f.sentido.value === '1' ? null : soma(anteriores, function (l) { return l.sentido === 2; }), f.sentido.value === '1' ? '' : rotuloAnt);
      } else {
        delta('total', 0, null, 'comparar com o ano anterior');
        delta('recepcao', 0, null, f.sentido.value === '2' ? '' : 'comparar com o ano anterior');
        delta('entrega', 0, null, f.sentido.value === '1' ? '' : 'comparar com o ano anterior');
      }

      var mesesNoPeriodo = 0;
      for (var k = ini; k <= fim; k++) if (mesesComDados[k]) mesesNoPeriodo++;
      kpi('media', fmtInt.format(Math.round(total / Math.max(1, mesesNoPeriodo))), 'm³/mês');
      nota('media', mesesNoPeriodo + ' ' + (mesesNoPeriodo === 1 ? 'mês lançado' : 'meses lançados') + ' no período');

      var mensal = porMes(rows, ini, fim);
      var vUlt = mensal[mensal.length - 1] || 0;
      kpi('ultimo', fmtInt.format(Math.round(vUlt)), 'm³');
      var porMesTodos = function (idx) { return mesesComDados[idx] ? soma(linhas.filter(function (l) { return l.idx === idx && filtroDimensoes(l); })) : null; };
      delta('ultimo', vUlt, porMesTodos(fim - 1), 'mês anterior');
      var aa = porMesTodos(fim - 12);
      nota('ultimo', rotuloMesLongo(idxMes(fim)) + (aa ? ' · ' + (vUlt >= aa ? '+' : '−') + fmtPct.format(Math.abs(vUlt - aa) / aa) + ' vs. ' + rotuloMesLongo(idxMes(fim - 12)) : ''));

      var recPeriodo = linhas.filter(function (l) { return l.idx >= ini && l.idx <= fim && l.sentido === 1 && filtroDimensoes(l, { sentido: true, modo: true }); });
      var recTotal = soma(recPeriodo), recAqua = soma(recPeriodo, function (l) { return l.modo === 4; });
      kpi('aquaviario', recTotal ? fmtPct.format(recAqua / recTotal) : '—');

      kpi('saldo', semSentido ? '—' : (rec - ent >= 0 ? '+' : '−') + fmtInt.format(Math.abs(Math.round(rec - ent))), semSentido ? '' : 'm³');

      var maxV = -1, maxI = null;
      mensal.forEach(function (v, j) { if (v != null && v > maxV) { maxV = v; maxI = j; } });
      kpi('pico', maxI == null ? '—' : fmtInt.format(Math.round(maxV)), maxI == null ? '' : 'm³');
      nota('pico', maxI == null ? '' : rotuloMesLongo(idxMes(ini + maxI)));
    }

    /* ------------------------------------------------------------ gráficos */
    function gEvolucao(rows, meses, ini, fim) {
      var series = [];
      [[1, 'Recepção', COR.recepcao], [2, 'Entrega', COR.entrega]].forEach(function (s) {
        if (f.sentido.value && +f.sentido.value !== s[0]) return;
        series.push(Object.assign({}, BARRA, { name: s[1], color: s[2], barGap: '10%',
          data: porMes(rows, ini, fim, function (l) { return l.sentido === s[0] ? l.volume : 0; }) }));
      });
      var z = zoom(meses.length);
      chart('c-evolucao').setOption(base({
        grid: { left: 8, right: 16, top: 44, bottom: z.length ? 36 : 8, containLabel: true },
        tooltip: Object.assign(base().tooltip, { axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(16,16,16,.04)' } },
          formatter: function (ps) {
            var h = tituloTooltip(rotuloMesLongo(meses[ps[0].dataIndex]));
            ps.forEach(function (p) { h += linhaTooltip(p.color, p.seriesName, p.value == null ? 'sem lançamento' : m3(p.value)); });
            if (ps.length === 2 && ps[0].value != null) h += linhaTooltip('transparent', 'saldo', (ps[0].value - ps[1].value >= 0 ? '+' : '−') + m3(Math.abs(ps[0].value - ps[1].value)));
            return h;
          } }),
        xAxis: eixoMeses(meses), yAxis: eixoValor(), dataZoom: z, series: series,
      }), true);
    }

    function gTendencia(meses, ini, fim) {
      // a média móvel usa o histórico anterior ao período, quando existe
      var hist = linhas.filter(function (l) { return filtroDimensoes(l); });
      var mensal = porMes(hist, ini, fim);
      var completo = porMes(hist, ini - 11, fim);
      var mm = mensal.map(function (_, j) {
        var janela = completo.slice(j, j + 12);
        if (janela.length < 12 || janela.some(function (v) { return v == null; })) return null;
        return janela.reduce(function (a, b) { return a + b; }, 0) / 12;
      });
      chart('c-tendencia').setOption(base({
        grid: { left: 8, right: 52, top: 44, bottom: 8, containLabel: true },
        tooltip: Object.assign(base().tooltip, { formatter: function (ps) {
          var h = tituloTooltip(rotuloMesLongo(meses[ps[0].dataIndex]));
          ps.forEach(function (p) { h += linhaTooltip(p.color, p.seriesName, p.value == null ? '—' : m3(p.value)); });
          return h;
        } }),
        xAxis: eixoMeses(meses, { boundaryGap: false }), yAxis: eixoValor({ scale: true }),
        series: [
          { name: 'Movimentação mensal', type: 'line', data: mensal, color: '#b9bdc3', symbol: 'circle', symbolSize: 6,
            showSymbol: meses.length <= 24, lineStyle: { width: 2 }, itemStyle: { borderColor: COR.surface, borderWidth: 2 } },
          { name: 'Média móvel 12 meses', type: 'line', data: mm, color: COR.ink, symbol: 'none', smooth: false,
            lineStyle: { width: 2.5 },
            endLabel: { show: true, color: COR.ink, fontWeight: 700, fontSize: 11,
                        formatter: function (p) { return fmtCompact.format(p.value); } } },
        ],
      }), true);
    }

    function gSaldo(rows, meses, ini, fim) {
      if (f.sentido.value) { chart('c-saldo').setOption(vazio('Escolha "Recepção e entrega" em Sentido para ver o saldo'), true); return; }
      var saldo = porMes(rows, ini, fim, function (l) { return l.sentido === 1 ? l.volume : -l.volume; });
      chart('c-saldo').setOption(base({
        legend: { show: true, top: 0, left: 0, data: ['Entrou mais', 'Saiu mais'], icon: 'roundRect', itemWidth: 12, itemHeight: 12,
                  textStyle: { color: COR.ink2, fontFamily: FONTE, fontSize: 12 } },
        tooltip: Object.assign(base().tooltip, { axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(16,16,16,.04)' } },
          formatter: function (ps) {
            var p = ps.filter(function (x) { return x.value != null && x.value !== '-'; })[0] || ps[0];
            var v = saldo[p.dataIndex];
            return tituloTooltip(rotuloMesLongo(meses[p.dataIndex])) +
              linhaTooltip(v >= 0 ? COR.recepcao : COR.entrega, 'recepção − entrega', v == null ? 'sem lançamento' : (v >= 0 ? '+' : '−') + m3(Math.abs(v)));
          } }),
        xAxis: eixoMeses(meses), yAxis: eixoValor(),
        series: [
          Object.assign({}, BARRA, { name: 'Entrou mais', color: COR.recepcao, stack: 's', data: saldo.map(function (v) { return v != null && v >= 0 ? v : '-'; }) }),
          Object.assign({}, BARRA, { name: 'Saiu mais', color: COR.entrega, stack: 's', itemStyle: { borderRadius: [0, 0, 4, 4] },
            data: saldo.map(function (v) { return v != null && v < 0 ? v : '-'; }) }),
        ],
      }), true);
    }

    function gProdutos(rows, meses, ini, fim) {
      var usados = {};
      rows.forEach(function (l) { usados[l.produto] = true; });
      var series = produtos.filter(function (p) { return usados[p.id]; }).map(function (p) {
        return { name: p.nome, type: 'bar', stack: 'p', barMaxWidth: 24, color: corProduto[p.id],
                 itemStyle: { borderColor: COR.surface, borderWidth: 1 },
                 data: porMes(rows, ini, fim, function (l) { return l.produto === p.id ? l.volume : 0; }) };
      });
      var z = zoom(meses.length);
      chart('c-produtos').setOption(base({
        legend: Object.assign(base().legend, { type: 'scroll', right: 0 }),
        grid: { left: 8, right: 16, top: 52, bottom: z.length ? 36 : 8, containLabel: true },
        tooltip: Object.assign(base().tooltip, { axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(16,16,16,.04)' } },
          formatter: function (ps) {
            var t = 0;
            ps.forEach(function (p) { t += p.value || 0; });
            var h = tituloTooltip(rotuloMesLongo(meses[ps[0].dataIndex]) + ' · ' + m3(t));
            ps.slice().reverse().forEach(function (p) { if (p.value) h += linhaTooltip(p.color, p.seriesName + ' (' + fmtPct.format(p.value / t) + ')', m3(p.value)); });
            return h;
          } }),
        xAxis: eixoMeses(meses), yAxis: eixoValor(), dataZoom: z, series: series,
      }), true);
    }

    function gMix(rows) {
      var tot = soma(rows);
      var itens = produtos.map(function (p) { return { p: p, v: soma(rows, function (l) { return l.produto === p.id; }) }; })
        .filter(function (x) { return x.v > 0; }).sort(function (a, b) { return a.v - b.v; });
      if (!itens.length) { chart('c-mix').setOption(vazio('Sem movimentação no filtro escolhido'), true); return; }
      chart('c-mix').setOption(base({
        grid: { left: 8, right: 132, top: 8, bottom: 8, containLabel: true },
        legend: { show: false },
        tooltip: Object.assign(base().tooltip, { trigger: 'item', formatter: function (p) {
          var x = itens[p.dataIndex];
          return tituloTooltip(x.p.nome) + linhaTooltip(corProduto[x.p.id], fmtPct.format(x.v / tot) + ' do volume', m3(x.v));
        } }),
        xAxis: eixoValor({ splitNumber: 3 }),
        yAxis: { type: 'category', data: itens.map(function (x) { return x.p.nome; }), axisLine: { show: false }, axisTick: { show: false },
                 axisLabel: { color: COR.ink2, fontSize: 12, width: 200, overflow: 'truncate' } },
        series: [{ type: 'bar', barMaxWidth: 22, itemStyle: { borderRadius: [0, 4, 4, 0] },
                   data: itens.map(function (x) { return { value: x.v, itemStyle: { color: corProduto[x.p.id] } }; }),
                   label: { show: true, position: 'right', color: COR.ink, fontSize: 12, fontWeight: 700,
                            formatter: function (p) { return fmtCompact.format(p.value) + ' m³ · ' + fmtPct.format(p.value / tot); } } }],
      }), true);
    }

    function gFluxo(rows) {
      var nos = {}, links = {};
      function no(nome, cor) { if (!nos[nome]) nos[nome] = { name: nome, itemStyle: { color: cor, borderColor: cor } }; }
      function link(a, b, v) { var k = a + '\u0000' + b; links[k] = links[k] || { source: a, target: b, value: 0 }; links[k].value += v; }
      rows.forEach(function (l) {
        if (!l.volume) return;
        var prod = nomeProduto[l.produto], modo = dados.modos[l.modo];
        no(prod, corProduto[l.produto]);
        if (l.sentido === 1) { var a = 'Chega · ' + modo; no(a, COR.recepcao); link(a, prod, l.volume); }
        else { var b = 'Sai · ' + modo; no(b, COR.entrega); link(prod, b, l.volume); }
      });
      var lista = Object.keys(links).map(function (k) { return links[k]; });
      if (!lista.length) { chart('c-fluxo').setOption(vazio('Sem movimentação no filtro escolhido'), true); return; }
      chart('c-fluxo').setOption(base({
        legend: { show: false },
        tooltip: Object.assign(base().tooltip, { trigger: 'item', formatter: function (p) {
          if (p.dataType === 'edge') return tituloTooltip(p.data.source + ' → ' + p.data.target) + linhaTooltip(p.color || COR.ink2, 'no período', m3(p.data.value));
          return tituloTooltip(p.name) + linhaTooltip(p.color, 'no período', m3(p.value));
        } }),
        series: [{ type: 'sankey', left: 4, right: 128, top: 8, bottom: 24, nodeWidth: 12, nodeGap: 10, nodeAlign: 'justify',
                   draggable: false, emphasis: { focus: 'adjacency' },
                   data: Object.keys(nos).map(function (k) { return nos[k]; }), links: lista,
                   lineStyle: { color: 'gradient', opacity: 0.28, curveness: 0.5 },
                   label: { color: COR.ink, fontSize: 11, fontWeight: 600, fontFamily: FONTE,
                            formatter: function (p) { return p.name + '\n{v|' + fmtCompact.format(p.value) + ' m³}'; },
                            rich: { v: { color: COR.ink2, fontSize: 10, fontWeight: 400, fontFamily: FONTE } } } }],
      }), true);
    }

    function gAquaviario(meses, ini, fim) {
      var rec = linhas.filter(function (l) { return l.sentido === 1 && filtroDimensoes(l, { sentido: true, modo: true }); });
      var tot = porMes(rec, ini, fim), aqua = porMes(rec, ini, fim, function (l) { return l.modo === 4 ? l.volume : 0; });
      var share = tot.map(function (t, j) { return t ? aqua[j] / t : null; });
      chart('c-aquaviario').setOption(base({
        legend: { show: false }, grid: { left: 8, right: 44, top: 16, bottom: 8, containLabel: true },
        tooltip: Object.assign(base().tooltip, { formatter: function (ps) {
          var j = ps[0].dataIndex;
          return tituloTooltip(rotuloMesLongo(meses[j])) +
            linhaTooltip(COR.recepcao, 'da recepção por navio', share[j] == null ? '—' : fmtPct.format(share[j])) +
            linhaTooltip('transparent', 'aquaviário', tot[j] ? m3(aqua[j]) : '—') +
            linhaTooltip('transparent', 'total recebido', tot[j] ? m3(tot[j]) : '—');
        } }),
        xAxis: eixoMeses(meses, { boundaryGap: false }),
        yAxis: eixoValor({ min: 0, max: 1, interval: 0.25, axisLabel: { color: COR.muted, fontSize: 11, formatter: function (v) { return fmtPct.format(v).replace(',0', ''); } } }),
        series: [{ name: 'Recepção aquaviária', type: 'line', data: share, color: COR.recepcao, symbol: 'circle', symbolSize: 6,
                   showSymbol: meses.length <= 24, lineStyle: { width: 2 }, itemStyle: { borderColor: COR.surface, borderWidth: 2 },
                   areaStyle: { color: COR.recepcao, opacity: 0.1 }, connectNulls: false,
                   endLabel: { show: true, color: COR.ink, fontWeight: 700, fontSize: 11, formatter: function (p) { return p.value == null ? '' : fmtPct.format(p.value); } } }],
      }), true);
    }

    function gAnual() {
      var hist = linhas.filter(function (l) { return filtroDimensoes(l); });
      var porAno = {};
      hist.forEach(function (l) { var a = Math.floor(l.idx / 12); porAno[a] = (porAno[a] || 0) + l.volume; });
      var mesesAno = {};
      idxs.forEach(function (k) { var a = Math.floor(k / 12); mesesAno[a] = (mesesAno[a] || 0) + 1; });
      var lista = Object.keys(mesesAno).map(Number).sort();
      var medias = lista.map(function (a) { return (porAno[a] || 0) / mesesAno[a]; });
      chart('c-anual').setOption(base({
        legend: { show: false }, grid: { left: 8, right: 16, top: 28, bottom: 8, containLabel: true },
        tooltip: Object.assign(base().tooltip, { trigger: 'item', formatter: function (p) {
          var a = lista[p.dataIndex];
          return tituloTooltip(String(a)) + linhaTooltip(COR.ink2, 'média por mês', m3(medias[p.dataIndex])) +
            linhaTooltip('transparent', mesesAno[a] + (mesesAno[a] === 1 ? ' mês lançado' : ' meses lançados'), m3(porAno[a] || 0));
        } }),
        xAxis: { type: 'category', data: lista.map(function (a) { return mesesAno[a] < 12 ? a + '*' : String(a); }),
                 axisLine: { lineStyle: { color: COR.axis } }, axisTick: { show: false }, axisLabel: { color: COR.ink2, fontSize: 12, fontWeight: 700 } },
        yAxis: eixoValor(),
        series: [Object.assign({}, BARRA, { barMaxWidth: 40, data: medias, color: '#34373b',
          label: { show: true, position: 'top', color: COR.ink, fontSize: 11, fontWeight: 700, formatter: function (p) { return fmtCompact.format(p.value); } } })],
        graphic: [{ type: 'text', right: 16, top: 4, style: { text: '* ano parcial', fill: COR.muted, font: '11px ' + FONTE } }],
      }), true);
    }

    function gSazonalidade() {
      var hist = linhas.filter(function (l) { return filtroDimensoes(l); });
      var anosLista = [];
      for (var a = Math.floor(primeiro / 12); a <= Math.floor(ultimo / 12); a++) anosLista.push(a);
      var celulas = {};
      hist.forEach(function (l) { celulas[l.idx] = (celulas[l.idx] || 0) + l.volume; });
      var data = [], max = 0, min = Infinity;
      anosLista.forEach(function (a, yi) {
        for (var m = 0; m < 12; m++) {
          var k = a * 12 + m;
          if (!mesesComDados[k]) continue;
          var v = celulas[k] || 0;
          max = Math.max(max, v); min = Math.min(min, v);
          data.push([m, yi, v]);
        }
      });
      chart('c-sazonalidade').setOption(base({
        legend: { show: false }, grid: { left: 8, right: 16, top: 8, bottom: 56, containLabel: true },
        tooltip: Object.assign(base().tooltip, { trigger: 'item', formatter: function (p) {
          var mm = p.data[0], aa = anosLista[p.data[1]];
          return tituloTooltip(MESES[mm] + '/' + aa) + linhaTooltip(COR.seq[4], 'movimentado', m3(p.data[2]));
        } }),
        xAxis: { type: 'category', data: MESES, splitArea: { show: false }, axisLine: { show: false }, axisTick: { show: false },
                 axisLabel: { color: COR.ink2, fontSize: 12 } },
        yAxis: { type: 'category', data: anosLista.map(String), axisLine: { show: false }, axisTick: { show: false },
                 axisLabel: { color: COR.ink2, fontSize: 12, fontWeight: 700 } },
        visualMap: { min: min === Infinity ? 0 : min, max: max || 1, calculable: true, orient: 'horizontal', left: 'center', bottom: 0,
                     itemHeight: 220, itemWidth: 12, inRange: { color: COR.seq }, textStyle: { color: COR.muted, fontSize: 11 },
                     formatter: function (v) { return fmtCompact.format(v) + ' m³'; } },
        series: [{ type: 'heatmap', data: data, itemStyle: { borderColor: COR.surface, borderWidth: 2, borderRadius: 4 },
                   emphasis: { itemStyle: { borderColor: COR.ink, borderWidth: 2 } } }],
      }), true);
    }

    /* ------------------------------------------------------------ tabelas */
    var ordem = { chave: 'mes', dir: -1 }, pagina = 0, POR_PAGINA = 25, atuais = [];
    var tLanc = document.getElementById('t-lanc');
    var pager = document.querySelector('[data-pager]');
    function valorOrdem(l, chave) {
      if (chave === 'mes') return l.idx * 100000 + (l.sentido * 10 + l.modo) ;
      if (chave === 'sentido') return dados.sentidos[l.sentido];
      if (chave === 'modo') return dados.modos[l.modo];
      if (chave === 'tipo') return dados.tipos[l.tipo];
      if (chave === 'produto') return nomeProduto[l.produto];
      return l.volume;
    }
    function ordenar(rows) {
      return rows.map(function (l, i) { return [l, i]; }).sort(function (a, b) {
        var va = valorOrdem(a[0], ordem.chave), vb = valorOrdem(b[0], ordem.chave);
        var c = typeof va === 'string' ? va.localeCompare(vb, LOCALE) : va - vb;
        return c ? c * ordem.dir : (b[0].idx - a[0].idx) || (a[1] - b[1]);
      }).map(function (x) { return x[0]; });
    }
    function desenharLancamentos() {
      var tbody = tLanc.tBodies[0];
      tbody.textContent = '';
      var paginas = Math.max(1, Math.ceil(atuais.length / POR_PAGINA));
      pagina = Math.min(pagina, paginas - 1);
      atuais.slice(pagina * POR_PAGINA, (pagina + 1) * POR_PAGINA).forEach(function (l) {
        var tr = el('tr');
        tr.appendChild(el('td', null, rotuloMesLongo(l.mes)));
        tr.appendChild(el('td', null, dados.sentidos[l.sentido]));
        tr.appendChild(el('td', null, dados.modos[l.modo]));
        tr.appendChild(el('td', null, dados.tipos[l.tipo]));
        var tdP = el('td');
        tdP.appendChild(el('span', { 'class': 'dot', style: 'background:' + corProduto[l.produto], 'aria-hidden': 'true' }));
        tdP.appendChild(document.createTextNode(nomeProduto[l.produto]));
        tr.appendChild(tdP);
        tr.appendChild(el('td', { 'class': 'num' + (l.volume ? '' : ' muted-cell') }, fmtVol.format(l.volume)));
        if (urlLancamento) {
          var td = el('td');
          var a = el('a', { href: urlLancamento + l.mes + '/' }, 'Editar mês');
          a.appendChild(el('span', { 'class': 'visually-hidden' }, ' ' + rotuloMesLongo(l.mes)));
          td.appendChild(a);
          tr.appendChild(td);
        }
        tbody.appendChild(tr);
      });
      tLanc.querySelector('[data-total]').textContent = fmtVol.format(soma(atuais));
      pager.hidden = paginas <= 1;
      pager.querySelector('[data-page-info]').textContent = 'Página ' + (pagina + 1) + ' de ' + paginas + ' · ' + fmtInt.format(atuais.length) + ' lançamentos';
      pager.querySelector('[data-page="-1"]').disabled = pagina === 0;
      pager.querySelector('[data-page="1"]').disabled = pagina >= paginas - 1;
    }
    tLanc.querySelectorAll('thead [data-sort]').forEach(function (b) {
      b.addEventListener('click', function () {
        var chave = b.dataset.sort;
        ordem = { chave: chave, dir: ordem.chave === chave ? -ordem.dir : (chave === 'mes' || chave === 'volume' ? -1 : 1) };
        tLanc.querySelectorAll('thead th').forEach(function (th) { th.removeAttribute('aria-sort'); });
        b.parentNode.setAttribute('aria-sort', ordem.dir === 1 ? 'ascending' : 'descending');
        atuais = ordenar(atuais); pagina = 0; desenharLancamentos();
      });
    });
    pager.querySelectorAll('[data-page]').forEach(function (b) {
      b.addEventListener('click', function () { pagina += +b.dataset.page; desenharLancamentos(); tLanc.scrollIntoView({ block: 'nearest' }); });
    });

    function desenharResumo(rows, ini, fim) {
      var t = document.getElementById('t-resumo');
      var usados = produtos.filter(function (p) { return rows.some(function (l) { return l.produto === p.id; }); });
      var semSentido = !!f.sentido.value;
      var cols = [['Mês', null]];
      if (!semSentido) cols.push(['Recebido', 'r'], ['Entregue', 'e'], ['Saldo', 's']);
      usados.forEach(function (p) { cols.push([p.nome, 'p' + p.id]); });
      cols.push(['Total', 't']);
      var thead = t.tHead; thead.textContent = '';
      var hr = el('tr');
      cols.forEach(function (c, j) { hr.appendChild(el('th', { scope: 'col', 'class': j ? 'num' : '' }, c[0])); });
      thead.appendChild(hr);
      var tb = t.tBodies[0]; tb.textContent = '';
      var totais = {};
      for (var k = fim; k >= ini; k--) {
        if (!mesesComDados[k]) continue;
        var doMes = rows.filter(function (l) { return l.idx === k; });
        var v = { r: soma(doMes, function (l) { return l.sentido === 1; }), e: soma(doMes, function (l) { return l.sentido === 2; }), t: soma(doMes) };
        v.s = v.r - v.e;
        usados.forEach(function (p) { v['p' + p.id] = soma(doMes, function (l) { return l.produto === p.id; }); });
        var tr = el('tr');
        tr.appendChild(el('th', { scope: 'row' }, rotuloMesLongo(idxMes(k))));
        cols.slice(1).forEach(function (c) {
          totais[c[1]] = (totais[c[1]] || 0) + v[c[1]];
          tr.appendChild(el('td', { 'class': 'num' }, (c[1] === 's' && v.s > 0 ? '+' : '') + fmtInt.format(Math.round(v[c[1]]))));
        });
        tb.appendChild(tr);
      }
      var tf = t.tFoot; tf.textContent = '';
      var fr = el('tr');
      fr.appendChild(el('th', { scope: 'row' }, 'Total'));
      cols.slice(1).forEach(function (c) { fr.appendChild(el('td', { 'class': 'num' }, (c[1] === 's' && totais.s > 0 ? '+' : '') + fmtInt.format(Math.round(totais[c[1]] || 0)))); });
      tf.appendChild(fr);
    }

    // abas da tabela
    var tabs = Array.prototype.slice.call(document.querySelectorAll('[data-anp-tabs] [role="tab"]'));
    tabs.forEach(function (tab, i) {
      function select(t, foco) {
        tabs.forEach(function (x) {
          var sel = x === t;
          x.setAttribute('aria-selected', String(sel)); x.tabIndex = sel ? 0 : -1;
          document.getElementById(x.getAttribute('aria-controls')).hidden = !sel;
        });
        if (foco) t.focus();
      }
      tab.addEventListener('click', function () { select(tab); });
      tab.addEventListener('keydown', function (e) {
        var n = e.key === 'ArrowRight' ? tabs[(i + 1) % tabs.length] : e.key === 'ArrowLeft' ? tabs[(i - 1 + tabs.length) % tabs.length] : null;
        if (n) { e.preventDefault(); select(n, true); }
      });
    });

    /* ------------------------------------------------------------ render */
    var graficos = document.querySelector('.charts');
    function render() {
      var custom = f.periodo.value === 'custom';
      document.querySelectorAll('[data-custom]').forEach(function (n) { n.hidden = !custom; });
      var r = intervalo(), ini = r[0], fim = r[1];
      var meses = [];
      for (var k = ini; k <= fim; k++) meses.push(idxMes(k));
      var rows = linhas.filter(function (l) { return l.idx >= ini && l.idx <= fim && filtroDimensoes(l); });

      document.getElementById('f-resumo').textContent = 'Exibindo ' + rotuloMesLongo(idxMes(ini)) + ' a ' + rotuloMesLongo(idxMes(fim)) +
        ' · ' + meses.length + (meses.length === 1 ? ' mês' : ' meses') + ' · ' + fmtInt.format(rows.length) + ' lançamentos';
      graficos.classList.add('is-updating');
      atualizarKpis(rows, r, ini, fim);
      gEvolucao(rows, meses, ini, fim);
      gTendencia(meses, ini, fim);
      gSaldo(rows, meses, ini, fim);
      gProdutos(rows, meses, ini, fim);
      gMix(rows);
      gFluxo(rows);
      gAquaviario(meses, ini, fim);
      gAnual();
      gSazonalidade();
      atuais = ordenar(rows); pagina = 0; desenharLancamentos();
      desenharResumo(rows, ini, fim);
      sincronizarUrl(r);
      window.requestAnimationFrame(function () { graficos.classList.remove('is-updating'); });
    }
    Object.keys(f).forEach(function (k) { f[k].addEventListener('change', render); });
    document.getElementById('f-limpar').addEventListener('click', function () {
      f.periodo.value = 'u12'; f.sentido.value = ''; f.modo.value = ''; f.produto.value = '';
      f.de.value = String(Math.max(primeiro, ultimo - 11)); f.ate.value = String(ultimo);
      render();
    });
    if ('ResizeObserver' in window) {
      var ro = new ResizeObserver(function () { Object.keys(charts).forEach(function (k) { charts[k].resize(); }); });
      ro.observe(graficos);
    } else {
      window.addEventListener('resize', function () { Object.keys(charts).forEach(function (k) { charts[k].resize(); }); });
    }
    render();
  }

  var formLanc = document.querySelector('form[data-lancamento]');
  if (formLanc) initLancamento(formLanc);
  var fonte = document.getElementById('anp-dados');
  if (fonte && window.echarts) initPainel(JSON.parse(fonte.textContent));
})();
