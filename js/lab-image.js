/* =========================================================
   Thí nghiệm 2: Vẽ ảnh của vật qua thấu kính
   ========================================================= */
(function () {
  const canvas = document.getElementById('cv-image');
  const view = new LensView(canvas, 90);
  const st = { type: 'ht', f: 10, d: 25, h: 5, rays: { o: true, p: true, f: false }, ext: true, drag: false, prog: Infinity };
  let stopAnim = null;
  const fmt = (x) => (Math.round(x * 10) / 10).toString().replace('.', ',');

  function compute() {
    const f = st.type === 'ht' ? st.f : -st.f;
    if (Math.abs(st.d - f) < 1e-6) return { f, inf: true };
    const dp = (st.d * f) / (st.d - f);   // d' > 0: ảnh thật (bên phải); d' < 0: ảnh ảo (bên trái)
    const hp = (-st.h * dp) / st.d;        // h' < 0: ảnh ngược chiều
    return { f, dp, hp, inf: false };
  }

  function draw() {
    const p = getPalette();
    const c = view.ctx;
    const R = compute();
    const f = R.f;
    Draw.background(view, p, 5);
    Draw.axis(view, p);
    Draw.lens(view, p, st.type, view.ymax * 0.85);
    Draw.foci(view, p, st.f, st.type === 'ht');

    const xB = -st.d, yB = st.h, xr = view.xmax + 5;
    const colors = { o: p.rayO, p: p.rayP, f: p.rayF };
    const virtual = !R.inf && R.dp < 0;

    const build = (k) => {
      let m;
      if (k === 'o') m = yB / xB;
      else if (k === 'p') m = 0;
      else {
        const ax = -f;
        if (Math.abs(xB - ax) < 0.3) return null;
        m = yB / (xB - ax);
      }
      const r = traceRay(xB, yB, m, f, xr);
      if (st.ext) {
        if (virtual) r.segs.push({ x1: 0, y1: r.yh, x2: R.dp, y2: r.yh + r.m2 * R.dp, dashed: true });
        if (k === 'f' && st.type === 'pk') r.segs.push({ x1: 0, y1: r.yh, x2: -f, y2: 0, dashed: true });
        if (k === 'f' && st.type === 'ht' && xB > -f) r.segs.push({ x1: -f, y1: 0, x2: xB, y2: yB, dashed: true });
      }
      return r;
    };
    ['p', 'f', 'o'].forEach((k) => {
      if (!st.rays[k]) return;
      const r = build(k);
      if (r) Draw.rayPath(view, p, r.segs, colors[k], st.prog);
    });

    // Vật AB
    Draw.arrowObj(view, p, xB, yB, p.obj, { base: 'A', tip: 'B' });
    // vòng tròn kéo thả
    c.save();
    c.strokeStyle = p.obj;
    c.globalAlpha = 0.5;
    c.setLineDash([3, 3]);
    c.beginPath(); c.arc(view.X(xB), view.Y(yB), 14, 0, 7); c.stroke();
    c.restore();

    // Ảnh A'B'
    if (!R.inf && st.prog > view.w * 0.9 && Math.abs(R.dp) < 400) {
      Draw.arrowObj(view, p, R.dp, R.hp, p.img, { base: "A'", tip: "B'", dashed: virtual });
    }

    c.save();
    c.font = '600 12px "Be Vietnam Pro", sans-serif';
    c.textAlign = 'right';
    c.fillStyle = p.text;
    c.fillText(st.type === 'ht' ? 'Thấu kính hội tụ' : 'Thấu kính phân kì', view.w - 10, 20);
    if (R.inf) {
      c.fillStyle = p.focus;
      c.textAlign = 'center';
      c.fillText('Vật đặt tại tiêu điểm: các tia ló song song → không tạo được ảnh (ảnh ở rất xa)', view.w / 2, view.h - 12);
    } else if (!virtual && R.dp > view.xmax) {
      c.fillStyle = p.img;
      c.textAlign = 'center';
      c.fillText(`Ảnh thật ở xa ngoài khung hình (d' ≈ ${fmt(R.dp)} cm)`, view.w / 2, view.h - 12);
    }
    c.restore();
    readout(R);
  }

  function readout(R) {
    const el = document.getElementById('i-readout');
    let props = '';
    if (R.inf) {
      props = '<span class="pill">Không tạo ảnh (ảnh ở vô cực)</span>';
    } else {
      const real = R.dp > 0;
      const k = Math.abs(R.hp) / st.h;
      const size = Math.abs(k - 1) < 0.02 ? 'Bằng vật' : k > 1 ? 'Lớn hơn vật' : 'Nhỏ hơn vật';
      props = `
        <span class="pill ${real ? 'real' : 'virtual'}">${real ? 'Ảnh thật' : 'Ảnh ảo'}</span>
        <span class="pill">${R.hp < 0 ? 'Ngược chiều với vật' : 'Cùng chiều với vật'}</span>
        <span class="pill">${size}</span>
        <span class="pill">${real ? 'Hứng được trên màn chắn' : 'Không hứng được trên màn chắn'}</span>`;
    }
    el.innerHTML = `
      <div class="ro"><span>Tiêu cự f</span><b>${st.f} cm</b></div>
      <div class="ro"><span>Khoảng cách vật d = OA</span><b>${fmt(st.d)} cm</b></div>
      <div class="ro"><span>Chiều cao vật h = AB</span><b>${fmt(st.h)} cm</b></div>
      <div class="ro"><span>Khoảng cách ảnh d' = OA'</span><b>${R.inf ? '∞' : fmt(Math.abs(R.dp)) + ' cm'}</b></div>
      <div class="ro"><span>Chiều cao ảnh h' = A'B'</span><b>${R.inf ? '∞' : fmt(Math.abs(R.hp)) + ' cm'}</b></div>
      <div class="ro wide"><span style="width:100%">Tính chất ảnh</span>${props}</div>`;
  }

  function play() {
    if (stopAnim) stopAnim();
    Sound.play('ray');
    const total = view.w * 1.3;
    stopAnim = animate(1300, (k) => { st.prog = k * total; draw(); }, () => { st.prog = Infinity; draw(); stopAnim = null; Sound.play('pop'); });
  }

  // ---------- Điều khiển ----------
  const presetBox = document.getElementById('i-presets');
  document.querySelectorAll('[data-group="i-type"] .seg-btn').forEach((b) => b.addEventListener('click', () => {
    document.querySelectorAll('[data-group="i-type"] .seg-btn').forEach((x) => x.classList.remove('active'));
    b.classList.add('active');
    st.type = b.dataset.val;
    presetBox.style.display = st.type === 'ht' ? '' : 'none';
    play();
  }));
  const fIn = document.getElementById('i-f');
  fIn.addEventListener('input', () => {
    st.f = +fIn.value;
    document.getElementById('i-f-val').textContent = st.f;
    st.prog = Infinity; Sound.play('drag'); draw();
  });
  const hIn = document.getElementById('i-h');
  hIn.addEventListener('input', () => {
    st.h = +hIn.value;
    document.getElementById('i-h-val').textContent = fmt(st.h);
    st.prog = Infinity; Sound.play('drag'); draw();
  });
  ['o', 'p', 'f'].forEach((k) => document.getElementById('i-ray-' + k).addEventListener('change', (e) => {
    st.rays[k] = e.target.checked; Sound.play('toggle'); play();
  }));
  document.getElementById('i-ext').addEventListener('change', (e) => { st.ext = e.target.checked; Sound.play('toggle'); draw(); });
  presetBox.querySelectorAll('button').forEach((b) => b.addEventListener('click', () => {
    st.d = st.f * +b.dataset.k;
    play();
  }));

  // ---------- Kéo thả đỉnh B ----------
  function setB(pt) {
    st.d = Math.max(1, Math.min(view.xmax - 2, -pt.x));
    st.d = Math.round(st.d * 2) / 2;
    st.h = Math.max(1, Math.min(Math.min(12, view.ymax * 0.8), pt.y));
    st.h = Math.round(st.h * 2) / 2;
    hIn.value = st.h;
    document.getElementById('i-h-val').textContent = fmt(st.h);
  }
  const nearB = (pt) => Math.hypot(pt.px - view.X(-st.d), pt.py - view.Y(st.h)) < 26
    || (Math.abs(pt.px - view.X(-st.d)) < 12 && pt.y > -0.5 && pt.y < st.h + 1);
  canvas.addEventListener('pointerdown', (e) => {
    const pt = view.pointer(e);
    if (nearB(pt)) {
      st.drag = true;
      canvas.setPointerCapture(e.pointerId);
      if (stopAnim) { stopAnim(); stopAnim = null; }
      st.prog = Infinity;
      Sound.play('click');
    }
  });
  canvas.addEventListener('pointermove', (e) => {
    const pt = view.pointer(e);
    if (st.drag) { setB(pt); Sound.play('drag'); draw(); return; }
    canvas.style.cursor = nearB(pt) ? 'grab' : 'default';
  });
  const end = () => { st.drag = false; };
  canvas.addEventListener('pointerup', end);
  canvas.addEventListener('pointercancel', end);

  autoRedraw(view, draw);
  draw();
  document.addEventListener('tabshown', (e) => {
    if (e.detail === 'tn2') {
      view.resize();
      play();
    }
  });
})();
