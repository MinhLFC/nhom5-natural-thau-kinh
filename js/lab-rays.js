/* =========================================================
   Thí nghiệm 1: Đường đi của các tia sáng đặc biệt qua thấu kính
   ========================================================= */
(function () {
  const canvas = document.getElementById('cv-rays');
  const view = new LensView(canvas, 80);
  const DEFAULT_S = { x: -30, y: 6 };
  const st = {
    type: 'ht',
    f: 12,
    S: { ...DEFAULT_S },
    rays: { o: true, p: false, f: false },
    ext: true,
    prog: Infinity,
    drag: false,
  };
  let stopAnim = null;

  const CONC = {
    ht: {
      o: 'Tia tới đi qua quang tâm O thì tia ló tiếp tục <b>truyền thẳng</b> (không đổi hướng).',
      p: "Tia tới song song với trục chính thì tia ló <b>đi qua tiêu điểm chính F'</b>.",
      f: 'Tia tới đi qua tiêu điểm chính F thì tia ló <b>song song với trục chính</b>.',
    },
    pk: {
      o: 'Tia tới đi qua quang tâm O thì tia ló tiếp tục <b>truyền thẳng</b> (không đổi hướng).',
      p: 'Tia tới song song với trục chính thì tia ló có <b>đường kéo dài đi qua tiêu điểm chính F</b>.',
      f: "Tia tới có đường kéo dài đi qua tiêu điểm chính F' thì tia ló <b>song song với trục chính</b>.",
    },
  };
  const NAMES = { o: 'Tia qua quang tâm', p: 'Tia song song trục chính', f: 'Tia qua tiêu điểm' };

  const fSigned = () => (st.type === 'ht' ? st.f : -st.f);

  function buildRay(kind) {
    const S = st.S, f = fSigned(), xr = view.xmax + 5;
    let m;
    if (kind === 'o') m = S.y / S.x;
    else if (kind === 'p') m = 0;
    else {
      const ax = -f; // TKHT: F bên trái; TKPK: F' bên phải
      if (Math.abs(S.x - ax) < 0.4) return null;
      m = S.y / (S.x - ax);
    }
    const r = traceRay(S.x, S.y, m, f, xr);
    if (st.ext) {
      if (st.type === 'pk' && kind === 'p') r.segs.push({ x1: 0, y1: r.yh, x2: f, y2: 0, dashed: true });
      if (st.type === 'pk' && kind === 'f') r.segs.push({ x1: 0, y1: r.yh, x2: -f, y2: 0, dashed: true });
      if (st.type === 'ht' && kind === 'f' && S.x > -f) r.segs.push({ x1: -f, y1: 0, x2: S.x, y2: S.y, dashed: true });
    }
    return r;
  }

  function draw() {
    const p = getPalette();
    const c = view.ctx;
    Draw.background(view, p, 5);
    Draw.axis(view, p);
    Draw.lens(view, p, st.type, view.ymax * 0.82);
    Draw.foci(view, p, st.f);

    const colors = { o: p.rayO, p: p.rayP, f: p.rayF };
    let warn = '';
    ['p', 'f', 'o'].forEach((k) => {
      if (!st.rays[k]) return;
      const r = buildRay(k);
      if (!r) { warn = 'Nguồn S nằm ngay trên đường thẳng đứng qua tiêu điểm – hãy dịch S để tạo tia qua tiêu điểm.'; return; }
      Draw.rayPath(view, p, r.segs, colors[k], st.prog);
    });

    // Nguồn sáng S
    const X = view.X(st.S.x), Y = view.Y(st.S.y);
    c.save();
    const grd = c.createRadialGradient(X, Y, 2, X, Y, 22);
    grd.addColorStop(0, 'rgba(255,220,90,.95)');
    grd.addColorStop(1, 'rgba(255,200,60,0)');
    c.fillStyle = grd;
    c.beginPath(); c.arc(X, Y, 22, 0, 7); c.fill();
    c.fillStyle = '#ffb300';
    c.strokeStyle = p.text;
    c.lineWidth = 1.5;
    c.beginPath(); c.arc(X, Y, 8, 0, 7); c.fill(); c.stroke();
    c.fillStyle = p.text;
    c.font = '800 14px "Be Vietnam Pro", sans-serif';
    c.textAlign = 'center';
    c.fillText('S', X - 16, Y - 12);
    c.restore();

    // Chú thích
    c.save();
    c.font = '600 12px "Be Vietnam Pro", sans-serif';
    c.textAlign = 'right';
    c.fillStyle = p.text;
    c.fillText(st.type === 'ht' ? 'Thấu kính hội tụ' : 'Thấu kính phân kì', view.w - 10, 20);
    c.fillText(`f = ${st.f} cm`, view.w - 10, 38);
    if (warn) {
      c.fillStyle = p.focus;
      c.textAlign = 'center';
      c.fillText(warn, view.w / 2, view.h - 12);
    }
    c.restore();
  }

  function play() {
    if (stopAnim) stopAnim();
    Sound.play('ray');
    const total = view.w * 1.5;
    stopAnim = animate(1500, (k) => { st.prog = k * total; draw(); }, () => { st.prog = Infinity; draw(); stopAnim = null; });
  }

  function updateConclusion() {
    const box = document.getElementById('r-conc');
    const p = { o: '--ray-o', p: '--ray-p', f: '--ray-f' };
    const keys = ['o', 'p', 'f'].filter((k) => st.rays[k]);
    box.innerHTML = keys.length
      ? keys.map((k) => `<div class="conc-item" style="--c:var(${p[k]})"><b>${NAMES[k]} (${st.type === 'ht' ? 'TKHT' : 'TKPK'}):</b> ${CONC[st.type][k]}</div>`).join('')
      : '<div class="muted">Hãy chọn ít nhất một tia tới.</div>';
    box.innerHTML += '<div class="conc-item" style="--c:var(--primary)"><b>Chốt kiến thức:</b> Có 3 đường truyền đặc biệt của tia sáng qua thấu kính. Vận dụng 3 đường đặc biệt này, ta vẽ được ảnh của vật qua thấu kính.</div>';
  }

  // ---------- Điều khiển ----------
  document.querySelectorAll('[data-group="r-type"] .seg-btn').forEach((b) => b.addEventListener('click', () => {
    document.querySelectorAll('[data-group="r-type"] .seg-btn').forEach((x) => x.classList.remove('active'));
    b.classList.add('active');
    st.type = b.dataset.val;
    document.getElementById('r-ray-f-label').textContent = st.type === 'ht'
      ? 'Tia đi qua tiêu điểm chính F' : "Tia có đường kéo dài qua tiêu điểm F'";
    updateConclusion();
    play();
  }));
  ['o', 'p', 'f'].forEach((k) => {
    document.getElementById('r-ray-' + k).addEventListener('change', (e) => {
      st.rays[k] = e.target.checked;
      Sound.play('toggle');
      updateConclusion();
      play();
    });
  });
  const fIn = document.getElementById('r-f');
  fIn.addEventListener('input', () => {
    st.f = +fIn.value;
    document.getElementById('r-f-val').textContent = st.f;
    st.prog = Infinity;
    Sound.play('drag');
    draw();
  });
  document.getElementById('r-ext').addEventListener('change', (e) => { st.ext = e.target.checked; Sound.play('toggle'); draw(); });
  document.getElementById('r-play').addEventListener('click', play);
  document.getElementById('r-reset').addEventListener('click', () => {
    st.S = { ...DEFAULT_S };
    st.f = 12; fIn.value = 12; document.getElementById('r-f-val').textContent = 12;
    play();
  });
  document.getElementById('r-conc-btn').addEventListener('click', (e) => {
    const box = document.getElementById('r-conc');
    box.classList.toggle('hidden');
    e.target.textContent = box.classList.contains('hidden') ? 'Hiện kết luận' : 'Ẩn kết luận';
    Sound.play('pop');
  });

  // ---------- Kéo thả nguồn S ----------
  function setS(pt) {
    st.S.x = Math.max(view.xmin + 2, Math.min(-3, pt.x));
    st.S.y = Math.max(-view.ymax * 0.85, Math.min(view.ymax * 0.85, pt.y));
    st.S.x = Math.round(st.S.x * 2) / 2;
    st.S.y = Math.round(st.S.y * 2) / 2;
  }
  canvas.addEventListener('pointerdown', (e) => {
    const pt = view.pointer(e);
    const near = Math.hypot(pt.px - view.X(st.S.x), pt.py - view.Y(st.S.y)) < 24;
    if (near || pt.x < 0) {
      st.drag = true;
      canvas.setPointerCapture(e.pointerId);
      if (stopAnim) { stopAnim(); stopAnim = null; }
      st.prog = Infinity;
      setS(pt);
      Sound.play('click');
      draw();
    }
  });
  canvas.addEventListener('pointermove', (e) => {
    const pt = view.pointer(e);
    if (st.drag) { setS(pt); Sound.play('drag'); draw(); return; }
    const near = Math.hypot(pt.px - view.X(st.S.x), pt.py - view.Y(st.S.y)) < 24;
    canvas.style.cursor = near ? 'grab' : pt.x < 0 ? 'crosshair' : 'default';
  });
  const end = () => { st.drag = false; };
  canvas.addEventListener('pointerup', end);
  canvas.addEventListener('pointercancel', end);

  autoRedraw(view, draw);
  updateConclusion();
  draw();
  document.addEventListener('tabshown', (e) => {
    if (e.detail === 'tn1') {
      view.resize();
      play();
    }
  });
})();
