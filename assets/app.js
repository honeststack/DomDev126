/* Astradive — site interactions
   sticky header · mobile nav · hero rotator · scroll reveal · accordion
   stat counters · sprint bars · marquee loop · demo form
   All progressive enhancement: the page reads fine with JS disabled. */

(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $  = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ------------------------------------------------ sticky header state */
  var header = $('#header');
  var onScroll = function () {
    header.classList.toggle('is-stuck', window.scrollY > 12);
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ------------------------------------------------ mobile nav */
  var toggle = $('#navToggle');
  var nav = $('#nav');
  toggle.addEventListener('click', function () {
    var open = header.classList.toggle('nav-open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) {
      header.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && header.classList.contains('nav-open')) {
      header.classList.remove('nav-open');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.focus();
    }
  });

  /* ------------------------------------------------ hero word rotator */
  var rotator = $('#rotator');
  if (rotator && !reduce) {
    var words = [
      'AI custom software',
      'AI-powered MVPs',
      'enterprise AI platforms',
      'data products that scale'
    ];
    var i = 0;
    var slot = rotator.firstElementChild;
    setInterval(function () {
      slot.classList.add('out');
      setTimeout(function () {
        i = (i + 1) % words.length;
        slot.textContent = words[i];
        slot.classList.remove('out');
      }, 400);
    }, 3200);
  }

  /* ------------------------------------------------ scroll reveal */
  var revealables = $$('.reveal');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, idx) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        // slight stagger for siblings entering together
        setTimeout(function () { el.classList.add('in'); }, idx * 70);
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.1 });
    revealables.forEach(function (el) { io.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add('in'); });
  }

  /* ------------------------------------------------ process accordion */
  $$('#steps .step').forEach(function (step) {
    var btn = $('.step-btn', step);
    btn.addEventListener('click', function () {
      var isOpen = step.classList.contains('open');
      $$('#steps .step').forEach(function (s) {
        s.classList.remove('open');
        $('.step-btn', s).setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        step.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });

  /* ------------------------------------------------ stat counters */
  var stats = $('#stats');
  var runCounters = function () {
    $$('b[data-count]', stats).forEach(function (el) {
      var target = parseFloat(el.getAttribute('data-count'));
      var suffix = el.getAttribute('data-suffix') || '';
      if (reduce) { el.textContent = target + suffix; return; }
      var start = null;
      var dur = 1400;
      var tick = function (ts) {
        if (start === null) start = ts;
        var p = Math.min((ts - start) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  };
  if (stats) {
    if ('IntersectionObserver' in window) {
      var so = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { runCounters(); so.disconnect(); }
      }, { threshold: 0.4 });
      so.observe(stats);
    } else {
      runCounters();
    }
  }

  /* ------------------------------------------------ hero sprint bars */
  var sprint = $('#sprint');
  if (sprint) {
    var fill = function () {
      $$('.bar i', sprint).forEach(function (bar, n) {
        setTimeout(function () { bar.style.width = bar.getAttribute('data-fill'); }, reduce ? 0 : 200 + n * 180);
      });
    };
    window.requestAnimationFrame(fill);
  }

  /* ------------------------------------------------ marquee: duplicate for seamless loop */
  var marquee = $('#marquee');
  if (marquee) {
    var list = marquee.firstElementChild;
    var clone = list.cloneNode(true);
    clone.setAttribute('aria-hidden', 'true');
    marquee.appendChild(clone);
  }

  /* ------------------------------------------------ demo contact form */
  var form = $('#contactForm');
  var status = $('#formStatus');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var missing = ['name', 'email', 'brief'].filter(function (k) {
        return !String(data.get(k) || '').trim();
      });
      if (missing.length) {
        status.style.color = '#f072b6';
        status.textContent = 'Please fill in your name, email and a short brief.';
        var first = form.querySelector('[name="' + missing[0] + '"]');
        if (first) first.focus();
        return;
      }
      status.style.color = '';
      status.textContent = 'Thanks — this demo form does not submit anywhere yet.';
      form.reset();
    });
  }

  /* ------------------------------------------------ booking slot picker */
  var slots = $('#slots');
  if (slots) {
    slots.addEventListener('click', function (e) {
      var btn = e.target.closest('button');
      if (!btn) return;
      $$('button', slots).forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
      btn.setAttribute('aria-pressed', 'true');
      if (status) {
        status.style.color = '';
        status.textContent = 'Slot noted: ' + btn.textContent.trim() + ' — add your scheduling provider to confirm it.';
      }
    });
  }

  /* ------------------------------------------------ footer year */
  var year = $('#year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
