/* VIGOR — bio modal and FAQ accordion. No dependencies. */
(function () {
  'use strict';

  /* ---------------- bio modal ---------------- */
  var dialog = document.getElementById('bio-modal');
  var dataEl = document.getElementById('team-data');
  if (dialog && dataEl) {
    var team = JSON.parse(dataEl.textContent);
    var tiles = document.querySelectorAll('.team-card[data-index]');
    var els = {
      count: document.getElementById('bio-count'),
      portrait: document.getElementById('bio-portrait'),
      name: document.getElementById('bio-name'),
      role: document.getElementById('bio-role'),
      inst: document.getElementById('bio-inst'),
      bio: document.getElementById('bio-text')
    };
    var current = 0;
    var trigger = null;

    function render(i) {
      current = (i + team.length) % team.length;
      var p = team[current];

      // The aria-labelledby target (#bio-name) changes with the visible name,
      // so a screen reader announces the right person on Previous/Next.
      els.name.textContent = p.name;
      els.count.textContent = (current + 1) + ' of ' + team.length;
      els.role.textContent = p.role;
      els.role.hidden = !p.role;
      els.inst.textContent = p.institution;
      els.inst.hidden = !p.institution;

      els.portrait.textContent = '';
      if (p.portrait) {
        var img = document.createElement('img');
        img.src = p.portrait; img.alt = ''; img.width = 150; img.height = 150;
        els.portrait.appendChild(img);
      } else {
        var ini = document.createElement('span');
        ini.className = 'bio-modal__initials'; ini.setAttribute('aria-hidden', 'true');
        ini.textContent = p.initials;
        els.portrait.appendChild(ini);
      }

      els.bio.textContent = '';
      els.bio.hidden = !p.bio;
      if (p.bio) {
        var para = document.createElement('p');
        para.textContent = p.bio;
        els.bio.appendChild(para);
      }
    }

    function open(i, from) {
      trigger = from || null;
      render(i);
      document.documentElement.classList.add('is-modal-open');   // scroll lock
      dialog.showModal();
      dialog.querySelector('[data-bio-close]').focus();
    }

    function close() { dialog.close(); }

    dialog.addEventListener('close', function () {
      document.documentElement.classList.remove('is-modal-open');
      // Return focus to the tile that opened the dialog.
      if (trigger) trigger.focus();
    });

    Array.prototype.forEach.call(tiles, function (tile) {
      tile.addEventListener('click', function () {
        open(parseInt(tile.getAttribute('data-index'), 10), tile);
      });
    });

    dialog.querySelector('[data-bio-close]').addEventListener('click', close);
    dialog.querySelector('[data-bio-prev]').addEventListener('click', function () { render(current - 1); });
    dialog.querySelector('[data-bio-next]').addEventListener('click', function () { render(current + 1); });

    // Backdrop click: the <dialog> itself is the backdrop-sized box;
    // clicks inside .bio-modal__dialog never reach this branch.
    dialog.addEventListener('click', function (e) { if (e.target === dialog) close(); });

    // Focus trap. showModal() makes the page inert, but Tab can still leave
    // to the browser chrome; keep it cycling inside the dialog.
    dialog.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;
      var f = dialog.querySelectorAll('button:not([hidden])');
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  /* ---------------- FAQ accordion ---------------- */
  // Without JS every panel stays open. With JS, collapsed ones hide.
  var triggers = document.querySelectorAll('.faq__trigger');
  Array.prototype.forEach.call(triggers, function (btn) {
    var panel = document.getElementById(btn.getAttribute('aria-controls'));
    if (!panel) return;
    panel.hidden = btn.getAttribute('aria-expanded') !== 'true';
    btn.addEventListener('click', function () {
      var expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!expanded));
      panel.hidden = expanded;
    });
  });
})();
