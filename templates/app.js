// 운세 나침반 — 꿈 키워드 검색: 실시간 필터 + 결과 확인하기 이동
(function () {
  var q = document.getElementById('q');
  if (!q) return;
  var go = document.getElementById('go');
  var noresult = document.getElementById('noresult');
  function norm(s) { return (s || '').replace(/\s+/g, '').toLowerCase(); }
  function cards() { return Array.prototype.slice.call(document.querySelectorAll('.card')); }
  function filter() {
    var needle = norm(q.value);
    var visible = 0;
    cards().forEach(function (card) {
      var hit = !needle || norm(card.getAttribute('data-kw')).indexOf(needle) >= 0;
      card.style.display = hit ? '' : 'none';
      if (hit) visible++;
    });
    document.querySelectorAll('.cat').forEach(function (cat) {
      var any = Array.prototype.some.call(cat.querySelectorAll('.card'), function (c) {
        return c.style.display !== 'none';
      });
      cat.style.display = any ? '' : 'none';
    });
    if (noresult) noresult.classList.toggle('hidden', visible > 0);
    return visible;
  }
  q.addEventListener('input', filter);
  function move() {
    var needle = norm(q.value);
    if (!needle) { q.focus(); return; }
    var list = cards();
    var exact = null, partial = null;
    list.forEach(function (card) {
      var kw = norm(card.getAttribute('data-kw'));
      if (kw === needle) exact = card;
      else if (!partial && kw.indexOf(needle) >= 0) partial = card;
    });
    var target = exact || partial;
    if (target) { location.href = '/d/' + target.getAttribute('data-slug') + '.html'; }
    else if (noresult) { noresult.classList.remove('hidden'); }
  }
  if (go) go.addEventListener('click', move);
  q.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); move(); } });
})();
