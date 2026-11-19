// 운세 나침반 — 꿈 키워드 실시간 검색 필터
(function () {
  var q = document.getElementById('q');
  if (!q) return;
  var noresult = document.getElementById('noresult');
  function norm(s) { return (s || '').replace(/\s+/g, '').toLowerCase(); }
  q.addEventListener('input', function () {
    var needle = norm(q.value);
    var visible = 0;
    document.querySelectorAll('.card').forEach(function (card) {
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
  });
})();
