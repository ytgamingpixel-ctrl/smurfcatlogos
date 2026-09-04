/* ===================================================================
   SMURFCAT - site behaviour
   -------------------------------------------------------------------
   You shouldn't need to edit this file to run the site day to day.
   To change the portfolio, edit  assets/js/work.js  instead.

   What's in here:
     1. Build the portfolio grid + filter buttons from WORK
     2. Reveal elements as they scroll into view
     3. Add a hairline under the header once you scroll
     4. Copy-to-clipboard on the Discord username
     5. Keep the footer year current
   =================================================================== */

(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;


  /* ── 1. PORTFOLIO GRID ─────────────────────────────────────────── */
  var grid    = document.getElementById('work-grid');
  var filters = document.getElementById('filters');

  // A full URL is used as-is; anything else is a file in assets/img/work/
  function imageSrc(value) {
    return /^https?:\/\//i.test(value) ? value : 'assets/img/work/' + value;
  }

  if (grid && typeof WORK !== 'undefined') {

    WORK.forEach(function (item) {
      var li = document.createElement('li');
      li.className = 'work-card';
      li.dataset.type = item.type;

      var img = document.createElement('img');
      img.className = 'work-card__img';
      img.src = imageSrc(item.img);
      img.alt = item.name + ' logo';
      img.loading = 'lazy';
      img.decoding = 'async';

      // If a link breaks (an expired Discord CDN URL, a deleted upload) the
      // tile is removed rather than left showing a broken-image icon.
      img.addEventListener('error', function () {
        li.hidden = true;
        li.dataset.broken = 'true';
        if (window.console) {
          console.warn('Logo image failed to load: ' + item.img +
                       ' - check the link in assets/js/work.js');
        }
      });

      // Make casual saving awkward: no dragging the image out to the desktop.
      // (The real protection is the watermark baked into the file itself -
      // anyone determined can still screenshot or open devtools.)
      img.draggable = false;
      img.addEventListener('dragstart', function (e) { e.preventDefault(); });

      // A transparent layer over the image, so right-click and long-press
      // land on this instead of the <img> and get no "Save image as".
      var shield = document.createElement('span');
      shield.className = 'work-card__shield';
      shield.setAttribute('aria-hidden', 'true');
      shield.addEventListener('contextmenu', function (e) { e.preventDefault(); });

      var meta = document.createElement('div');
      meta.className = 'work-card__meta';
      meta.innerHTML =
        '<span class="work-card__name"></span>' +
        '<span class="work-card__type"></span>';
      // textContent (not innerHTML) so names with & or < can't break the page
      meta.querySelector('.work-card__name').textContent = item.name;
      meta.querySelector('.work-card__type').textContent = item.type;

      li.appendChild(img);
      li.appendChild(shield);
      li.appendChild(meta);
      grid.appendChild(li);
    });

    // Build one filter button per unique "type", plus an "All" button
    if (filters) {
      var types = ['All'];
      WORK.forEach(function (item) {
        if (types.indexOf(item.type) === -1) types.push(item.type);
      });

      // Only worth showing filters if there's more than one category
      if (types.length > 2) {
        types.forEach(function (type, i) {
          var btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'filter' + (i === 0 ? ' is-active' : '');
          btn.textContent = type;
          btn.setAttribute('aria-pressed', i === 0 ? 'true' : 'false');

          btn.addEventListener('click', function () {
            filters.querySelectorAll('.filter').forEach(function (b) {
              b.classList.remove('is-active');
              b.setAttribute('aria-pressed', 'false');
            });
            btn.classList.add('is-active');
            btn.setAttribute('aria-pressed', 'true');

            grid.querySelectorAll('.work-card').forEach(function (card) {
              if (card.dataset.broken === 'true') return;   // stays hidden
              card.hidden = (type !== 'All' && card.dataset.type !== type);
            });
          });

          filters.appendChild(btn);
        });
      }
    }
  }


  /* ── 2. SCROLL REVEAL ──────────────────────────────────────────── */
  var revealables = document.querySelectorAll('.reveal');

  if (reduceMotion || !('IntersectionObserver' in window)) {
    // No animation: just show everything straight away
    revealables.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

    revealables.forEach(function (el, i) {
      // Stagger siblings slightly so groups cascade instead of popping
      el.style.transitionDelay = (i % 6) * 60 + 'ms';
      observer.observe(el);
    });
  }


  /* ── 3. HEADER HAIRLINE ON SCROLL ──────────────────────────────── */
  var header = document.querySelector('.site-header');
  if (header) {
    var onScroll = function () {
      header.classList.toggle('is-stuck', window.scrollY > 8);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }


  /* ── 4. COPY THE DISCORD USERNAME ──────────────────────────────── */
  var copyBtn = document.querySelector('.discord__copy');
  var copyStatus = document.getElementById('copy-status');

  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      var handle = copyBtn.dataset.copy || '';

      // Fallback for browsers that block the clipboard API (or any page
      // served over plain http): select the username so Ctrl+C actually
      // has something to copy, rather than just telling them to press it.
      var selectHandle = function () {
        var el = document.getElementById('discord-handle');
        if (!el || !window.getSelection || !document.createRange) return;
        var range = document.createRange();
        range.selectNodeContents(el);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
      };

      var done = function (ok) {
        if (!ok) selectHandle();
        if (!copyStatus) return;
        copyStatus.textContent = ok
          ? 'Copied. Paste it into Discord search.'
          : 'Selected — press Ctrl+C to copy.';
        copyStatus.className = 'discord__status' + (ok ? ' is-ok' : '');
        window.setTimeout(function () {
          copyStatus.textContent = '';
          copyStatus.className = 'discord__status';
        }, 4000);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(handle)
          .then(function () { done(true); })
          .catch(function () { done(false); });
      } else {
        done(false);
      }
    });
  }


  /* ── 5. FOOTER YEAR ────────────────────────────────────────────── */
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

})();
