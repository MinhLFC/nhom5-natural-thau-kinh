/* =========================================================
   Phần lý thuyết: chùm sáng song song (Hình 8.5) + phân loại thấu kính
   ========================================================= */
(function () {
  // ---------- Chùm sáng song song qua TKHT / TKPK ----------
  const beams = [
    { view: new LensView(document.getElementById('cv-beam-ht'), 44), type: 'ht' },
    { view: new LensView(document.getElementById('cv-beam-pk'), 44), type: 'pk' },
  ];
  let prog = Infinity;
  const F = 9;

  function drawBeam(b) {
    const v = b.view, p = getPalette();
    const f = b.type === 'ht' ? F : -F;
    Draw.background(v, p, 0);
    Draw.axis(v, p, false);
    Draw.lens(v, p, b.type, v.ymax * 0.8);
    const c = v.ctx;
    c.save();
    c.fillStyle = p.focus;
    c.font = '700 12px "Be Vietnam Pro", sans-serif';
    c.textAlign = 'center';
    const leftLabel = b.type === 'pk' ? "F'" : "F";
    const rightLabel = b.type === 'pk' ? "F" : "F'";
    [[-F, leftLabel], [F, rightLabel]].forEach(([x, l]) => {
      c.beginPath(); c.arc(v.X(x), v.Y(0), 3.5, 0, 7); c.fill();
      c.fillText(l, v.X(x), v.Y(0) + 16);
    });
    c.fillStyle = p.text;
    c.fillText('O', v.X(0) + 8, v.Y(0) + 15);
    c.restore();
    const hs = [-0.6, -0.3, 0.3, 0.6].map((k) => k * v.ymax);
    hs.forEach((h) => {
      const r = traceRay(v.xmin, h, 0, f, v.xmax + 2);
      if (b.type === 'pk') r.segs.push({ x1: 0, y1: r.yh, x2: -F, y2: 0, dashed: true });
      Draw.rayPath(v, p, r.segs, p.rayP, prog);
    });
  }
  const drawAll = () => beams.forEach(drawBeam);
  beams.forEach((b) => autoRedraw(b.view, () => drawBeam(b)));

  function replay() {
    animate(1800, (k) => { prog = k * beams[0].view.w * 1.15; drawAll(); }, () => { prog = Infinity; drawAll(); });
  }
  document.getElementById('btn-beam-replay').addEventListener('click', () => { Sound.play('ray'); replay(); });
  document.addEventListener('tabshown', (e) => {
    if (e.detail === 'ly-thuyet') {
      beams.forEach((b) => b.view.resize());
      replay();
    }
  });

  // ---------- Phân loại thấu kính ----------
  const shapes = [
    { d: 'M40 10 Q70 70 40 130 Q10 70 40 10Z', a: 'ht' },                         // hai mặt lồi
    { d: 'M30 10 L30 130 Q75 70 30 10Z', a: 'ht' },                               // phẳng – lồi
    { d: 'M30 10 Q72 70 30 130 Q48 70 30 10Z', a: 'ht' },                         // lõm – lồi (rìa mỏng)
    { d: 'M20 10 L60 10 Q42 70 60 130 L20 130 Q38 70 20 10Z', a: 'pk' },          // hai mặt lõm
    { d: 'M25 10 L60 10 Q38 70 60 130 L25 130Z', a: 'pk' },                       // phẳng – lõm
    { d: 'M25 10 L55 10 Q22 70 55 130 L25 130 Q12 70 25 10Z', a: 'pk' },          // lồi – lõm (rìa dày)
  ];
  const box = document.getElementById('classify');
  const result = document.getElementById('classify-result');

  function build() {
    box.innerHTML = '';
    result.textContent = '';
    result.className = 'result';
    const order = shapes.map((s, i) => i).sort(() => Math.random() - 0.5);
    order.forEach((i, n) => {
      const s = shapes[i];
      const el = document.createElement('div');
      el.className = 'cls-item';
      el.dataset.ans = s.a;
      el.innerHTML = `
        <div><b>${String.fromCharCode(97 + n)})</b></div>
        <svg viewBox="0 0 80 140"><path d="${s.d}" class="lt-shape"/></svg>
        <div class="cls-btns">
          <button data-v="ht">Hội tụ</button>
          <button data-v="pk">Phân kì</button>
        </div>`;
      el.querySelectorAll('button').forEach((bt) => bt.addEventListener('click', () => {
        el.querySelectorAll('button').forEach((x) => x.classList.remove('sel'));
        bt.classList.add('sel');
        el.dataset.sel = bt.dataset.v;
        el.classList.remove('ok', 'bad');
        Sound.play('click');
      }));
      box.appendChild(el);
    });
  }

  document.getElementById('btn-classify-check').addEventListener('click', () => {
    let ok = 0;
    const items = box.querySelectorAll('.cls-item');
    items.forEach((el) => {
      el.classList.remove('ok', 'bad');
      void el.offsetWidth;
      const good = el.dataset.sel === el.dataset.ans;
      el.classList.add(good ? 'ok' : 'bad');
      if (good) ok++;
    });
    const all = ok === items.length;
    result.textContent = all ? `🎉 Chính xác cả ${ok}/${items.length}! Rìa mỏng → hội tụ, rìa dày → phân kì.` : `Đúng ${ok}/${items.length}. Gợi ý: so sánh độ dày phần rìa và phần giữa.`;
    result.className = 'result ' + (all ? 'ok' : 'bad');
    Sound.play(all ? 'correct' : 'wrong');
  });
  document.getElementById('btn-classify-reset').addEventListener('click', build);
  build();
})();
