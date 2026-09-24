/* TECAB — interações do site (sem dependências). Todo o conteúdo funciona sem JavaScript. */
(function () {
  'use strict';
  var doc = document.documentElement;
  doc.classList.add('js');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Cabeçalho: fundo sólido após rolar */
  var header = document.querySelector('.site-header');
  var backToTop = document.querySelector('.back-to-top');
  function onScroll() {
    var y = window.scrollY;
    if (header) header.classList.toggle('is-solid', y > 24);
    if (backToTop) backToTop.classList.toggle('is-visible', y > 600);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  if (backToTop) {
    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
      var skip = document.getElementById('conteudo');
      if (skip) skip.focus({ preventScroll: true });
    });
  }

  /* Menu móvel */
  var navToggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('menu-principal');
  function setNav(open) {
    document.body.classList.toggle('nav-open', open);
    navToggle.setAttribute('aria-expanded', String(open));
    navToggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    if (open) {
      var first = nav.querySelector('a, button');
      if (first) first.focus();
    }
  }
  if (navToggle && nav) {
    navToggle.addEventListener('click', function () {
      setNav(navToggle.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && document.body.classList.contains('nav-open')) {
        setNav(false);
        navToggle.focus();
      }
    });
    window.matchMedia('(min-width: 1081px)').addEventListener('change', function (mq) {
      if (mq.matches) setNav(false);
    });
  }

  /* Menus suspensos (Portal do Cliente) */
  document.querySelectorAll('[data-dropdown]').forEach(function (dropdown) {
    var button = dropdown.querySelector('.dropdown__toggle');
    var menu = dropdown.querySelector('.dropdown__menu');
    function set(open) {
      dropdown.classList.toggle('is-open', open);
      button.setAttribute('aria-expanded', String(open));
    }
    button.addEventListener('click', function (e) {
      e.stopPropagation();
      set(!dropdown.classList.contains('is-open'));
    });
    document.addEventListener('click', function (e) {
      if (!dropdown.contains(e.target)) set(false);
    });
    dropdown.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && dropdown.classList.contains('is-open')) {
        set(false);
        button.focus();
      }
    });
    menu.addEventListener('focusout', function (e) {
      if (!dropdown.contains(e.relatedTarget)) set(false);
    });
  });

  /* Animação de entrada ao rolar */
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* Abas acessíveis (padrão WAI-ARIA) */
  document.querySelectorAll('[data-tabs]').forEach(function (root) {
    var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var selected = t === tab;
        t.setAttribute('aria-selected', String(selected));
        t.tabIndex = selected ? 0 : -1;
        document.getElementById(t.getAttribute('aria-controls')).hidden = !selected;
      });
      if (focus) tab.focus();
      if (history.replaceState) {
        var url = new URL(window.location.href);
        url.searchParams.set('aba', tab.dataset.tab);
        url.hash = 'formularios';
        history.replaceState(null, '', url);
      }
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () { select(tab, false); });
      tab.addEventListener('keydown', function (e) {
        var next = null;
        if (e.key === 'ArrowRight') next = tabs[(i + 1) % tabs.length];
        if (e.key === 'ArrowLeft') next = tabs[(i - 1 + tabs.length) % tabs.length];
        if (e.key === 'Home') next = tabs[0];
        if (e.key === 'End') next = tabs[tabs.length - 1];
        if (next) { e.preventDefault(); select(next, true); }
      });
    });
  });

  /* Galeria com visualização ampliada */
  var lightbox = document.getElementById('lightbox');
  var galleryButtons = Array.prototype.slice.call(document.querySelectorAll('[data-lightbox]'));
  if (lightbox && galleryButtons.length && typeof lightbox.showModal === 'function') {
    var lbImg = lightbox.querySelector('img');
    var lbCaption = lightbox.querySelector('[data-caption]');
    var lbCounter = lightbox.querySelector('[data-counter]');
    var current = 0;
    function show(i) {
      current = (i + galleryButtons.length) % galleryButtons.length;
      var b = galleryButtons[current];
      lbImg.src = b.dataset.lightbox;
      lbImg.alt = b.dataset.caption;
      lbCaption.textContent = b.dataset.caption;
      lbCounter.textContent = (current + 1) + ' de ' + galleryButtons.length;
    }
    galleryButtons.forEach(function (b, i) {
      b.addEventListener('click', function () { show(i); lightbox.showModal(); });
    });
    lightbox.querySelector('[data-prev]').addEventListener('click', function () { show(current - 1); });
    lightbox.querySelector('[data-next]').addEventListener('click', function () { show(current + 1); });
    lightbox.querySelector('[data-close]').addEventListener('click', function () { lightbox.close(); });
    lightbox.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') show(current + 1);
      if (e.key === 'ArrowLeft') show(current - 1);
    });
    lightbox.addEventListener('click', function (e) { if (e.target === lightbox) lightbox.close(); });
    lightbox.addEventListener('close', function () { galleryButtons[current].focus(); });
  }

  /* Mapa carregado somente com o consentimento do visitante (privacidade e desempenho) */
  document.querySelectorAll('[data-map]').forEach(function (box) {
    var button = box.querySelector('button');
    if (!button) return;
    button.addEventListener('click', function () {
      var iframe = document.createElement('iframe');
      iframe.src = box.dataset.map;
      iframe.title = box.dataset.title || 'Mapa';
      iframe.loading = 'lazy';
      iframe.referrerPolicy = 'no-referrer-when-downgrade';
      box.appendChild(iframe);
      box.classList.add('is-loaded');
      box.querySelector('.map-embed__placeholder').remove();
      iframe.focus();
    });
  });

  /* Mostrar/ocultar senha */
  document.querySelectorAll('.password-toggle').forEach(function (btn) {
    btn.hidden = false;
    btn.addEventListener('click', function () {
      var input = document.getElementById(btn.getAttribute('aria-controls'));
      var show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.setAttribute('aria-pressed', String(show));
      btn.setAttribute('aria-label', show ? 'Ocultar senha' : 'Mostrar senha');
      btn.querySelector('use').setAttribute('href', show ? '#i-eye-off' : '#i-eye');
    });
  });

  /* Nome do arquivo escolhido */
  document.querySelectorAll('.file-drop input[type="file"]').forEach(function (input) {
    var label = input.closest('.file-drop').querySelector('[data-file-name]');
    var original = label.textContent;
    input.addEventListener('change', function () {
      label.textContent = input.files.length ? input.files[0].name : original;
    });
  });

  /* Evita envio duplicado e leva o foco ao primeiro erro */
  document.querySelectorAll('form[data-enhance]').forEach(function (form) {
    form.addEventListener('submit', function () {
      var btn = form.querySelector('[type="submit"]');
      if (btn) { btn.classList.add('is-loading'); btn.setAttribute('aria-busy', 'true'); }
    });
  });
  var firstError = document.querySelector('[aria-invalid="true"]');
  if (firstError) {
    // após o carregamento, para não ser sobrescrito pela navegação até a âncora (#formularios)
    window.addEventListener('load', function () {
      firstError.focus({ preventScroll: true });
      firstError.scrollIntoView({ block: 'center', behavior: 'auto' });
    });
  }
})();
