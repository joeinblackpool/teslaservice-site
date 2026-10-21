// Directions helpers for teslaservice.co.uk (same behaviour as teslachargers.co.uk):
// "Send to your Tesla" (phones with a share menu), Navigate button that opens Apple Maps on iPhone,
// and "X miles from you" when the visitor has already allowed location for this site.
(function () {
  'use strict';
  var root = document.documentElement;
  if (navigator.share) root.classList.add('can-share');
  var HELP = 'In the share menu, pick the <strong>Tesla</strong> app. It sends this address to your car’s navigation. The address is also copied, so you can paste it into the car if needed.';
  document.addEventListener('click', function (e) {
    var b = e.target && e.target.closest ? e.target.closest('[data-share]') : null;
    if (!b || !navigator.share) return;
    var t = b.getAttribute('data-share');
    try { if (navigator.clipboard) navigator.clipboard.writeText(t).catch(function () {}); } catch (err) {}
    navigator.share({ title: t, text: t, url: 'https://www.google.com/maps/search/?api=1&query=' + b.getAttribute('data-lat') + ',' + b.getAttribute('data-lon') }).catch(function () {});
    var box = b.closest('.go-sm, .actions.dir') || b.parentNode, h = box.nextElementSibling;
    if (!h || !h.classList.contains('share-help')) { h = document.createElement('p'); h.className = 'share-help'; h.innerHTML = HELP; box.parentNode.insertBefore(h, box.nextSibling); }
    h.hidden = false;
  });
  var nv = document.querySelector('[data-nav]');
  if (nv) {
    document.body.classList.add('has-nav');
    if (/iPhone|iPad/.test(navigator.userAgent) || (/Macintosh/.test(navigator.userAgent) && 'ontouchend' in document)) nv.href = nv.getAttribute('data-apple');
  }
  function miles(a, o, b, p) { var r = Math.PI / 180, x = Math.sin((b - a) * r / 2), y = Math.sin((p - o) * r / 2), h = x * x + Math.cos(a * r) * Math.cos(b * r) * y * y; return 7917.6 * Math.asin(Math.sqrt(h)); }
  var dd = document.querySelector('[data-you]');
  if (dd && navigator.permissions && navigator.geolocation) {
    navigator.permissions.query({ name: 'geolocation' }).then(function (st) {
      if (st.state !== 'granted') return;
      navigator.geolocation.getCurrentPosition(function (p) {
        var m = miles(p.coords.latitude, p.coords.longitude, +dd.getAttribute('data-lat'), +dd.getAttribute('data-lon'));
        dd.textContent = 'About ' + (m < 10 ? m.toFixed(1) : Math.round(m)) + ' miles from you in a straight line.';
        dd.hidden = false;
      }, function () {}, { maximumAge: 600000, timeout: 8000 });
    }).catch(function () {});
  }
})();
