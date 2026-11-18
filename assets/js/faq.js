/* VIGOR — FAQ accordion. No dependencies. Without JS every panel stays open;
   with JS, collapsed ones hide. Loaded by faq.html and the FAQ page. */
(function () {
  'use strict';
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
