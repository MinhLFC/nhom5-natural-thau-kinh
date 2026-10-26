/* =========================================================
   Phiếu học tập điện tử + Trạm Mã QR + Xuất ảnh phiếu & Nộp bài
   ========================================================= */
(function () {
  // ---------- Phần 1 & nhận xét ảnh: các lựa chọn ----------
  const RAY_OPTS = [
    ['', '— Chọn đường truyền tia ló —'],
    ['thang', 'Tiếp tục truyền thẳng, không đổi hướng'],
    ['quaF2', "Tia ló đi qua tiêu điểm chính F'"],
    ['keoF', 'Tia ló có đường kéo dài đi qua tiêu điểm chính F'],
    ['songsong', 'Tia ló song song với trục chính'],
    ['quaO', 'Tia ló đi qua quang tâm O'],
  ];
  const PROP_OPTS = {
    thatao: [['', '— thật/ảo —'], ['that', 'ảnh thật'], ['ao', 'ảnh ảo']],
    chieu: [['', '— chiều —'], ['cung', 'cùng chiều với vật'], ['nguoc', 'ngược chiều với vật']],
    coanh: [['', '— độ lớn —'], ['lon', 'lớn hơn vật'], ['nho', 'nhỏ hơn vật'], ['bang', 'bằng vật']],
  };
  const OPT_TEXT = {};
  [...RAY_OPTS, ...PROP_OPTS.thatao, ...PROP_OPTS.chieu, ...PROP_OPTS.coanh].forEach(([k, v]) => {
    if (k) OPT_TEXT[k] = v;
  });

  const fill = (sel, opts) => {
    sel.innerHTML = opts.map(([v, t]) => `<option value="${v}">${t}</option>`).join('');
  };
  document.querySelectorAll('.ws-table select').forEach((s) => fill(s, RAY_OPTS));
  document.querySelectorAll('.img-props select').forEach((s) => fill(s, PROP_OPTS[s.dataset.opts]));
  document.querySelectorAll('select.ws-q').forEach((s) =>
    s.addEventListener('change', () => {
      s.classList.remove('ok', 'bad');
      Sound.play('click');
    })
  );

  // ---------- Bảng vẽ ----------
  const F = 10;
  const SETUP = { ht: { d: 18, h: 5 }, pk: { d: 15, h: 6 } };

  class SketchPad {
    constructor(root) {
      this.root = root;
      this.type = root.dataset.pad;
      this.cfg = SETUP[this.type];
      this.view = new LensView(root.querySelector('canvas'), 64);
      this.strokes = [];
      this.cur = null;
      this.tool = 'line';
      this.color = '#d32f2f';
      this.showAns = false;
      this.bind();
      autoRedraw(this.view, () => this.draw());
      this.draw();
    }

    bind() {
      const r = this.root;
      r.querySelectorAll('[data-tool]').forEach((b) =>
        b.addEventListener('click', () => {
          r.querySelectorAll('[data-tool]').forEach((x) => x.classList.remove('active'));
          b.classList.add('active');
          this.tool = b.dataset.tool;
          Sound.play('click');
        })
      );
      r.querySelectorAll('.color').forEach((b) =>
        b.addEventListener('click', () => {
          r.querySelectorAll('.color').forEach((x) => x.classList.remove('active'));
          b.classList.add('active');
          this.color = b.dataset.color;
          Sound.play('click');
        })
      );
      r.querySelector('[data-act="undo"]').addEventListener('click', () => {
        this.strokes.pop();
        Sound.play('click');
        this.draw();
      });
      r.querySelector('[data-act="clear"]').addEventListener('click', () => {
        this.strokes = [];
        Sound.play('pop');
        this.draw();
      });
      const ans = r.querySelector('[data-act="answer"]');
      ans.addEventListener('click', () => {
        this.showAns = !this.showAns;
        ans.classList.toggle('active', this.showAns);
        Sound.play('toggle');
        this.draw();
      });

      const cv = this.view.canvas;
      cv.addEventListener('pointerdown', (e) => {
        cv.setPointerCapture(e.pointerId);
        const pt = this.view.pointer(e);
        this.cur = { tool: this.tool, color: this.color, pts: [[pt.x, pt.y], [pt.x, pt.y]] };
        e.preventDefault();
      });
      cv.addEventListener('pointermove', (e) => {
        if (!this.cur) return;
        const pt = this.view.pointer(e);
        if (this.cur.tool === 'pen') this.cur.pts.push([pt.x, pt.y]);
        else this.cur.pts[1] = this.snap(this.cur.pts[0], [pt.x, pt.y]);
        this.draw();
      });
      const end = () => {
        if (!this.cur) return;
        const [a, b] = [this.cur.pts[0], this.cur.pts[this.cur.pts.length - 1]];
        if (this.cur.tool === 'pen' ? this.cur.pts.length > 2 : Math.hypot(a[0] - b[0], a[1] - b[1]) > 0.3) {
          this.strokes.push(this.cur);
          Sound.play('drag');
        }
        this.cur = null;
        this.draw();
      };
      cv.addEventListener('pointerup', end);
      cv.addEventListener('pointercancel', end);
    }

    snap(a, b) {
      const key = [[0, 0], [-F, 0], [F, 0], [-this.cfg.d, this.cfg.h], [-this.cfg.d, 0]];
      const tol = 12 / this.view.s;
      for (const k of key) if (Math.hypot(k[0] - b[0], k[1] - b[1]) < tol) return k.slice();
      if (Math.abs(b[0]) < tol) return [0, b[1]];
      if (Math.abs(b[1] - a[1]) < tol * 0.6) return [b[0], a[1]];
      return b;
    }

    drawAnswer(p) {
      const v = this.view, c = v.ctx;
      const f = this.type === 'ht' ? F : -F;
      const { d, h } = this.cfg;
      const dp = (d * f) / (d - f), hp = (-h * dp) / d;
      const virtual = dp < 0;
      const xr = v.xmax + 2;
      c.save();
      c.globalAlpha = 0.85;
      const rays = [
        [0, PAPER_PALETTE.rayP],
        [h / -d, PAPER_PALETTE.rayO],
      ];
      rays.forEach(([m, col]) => {
        const r = traceRay(-d, h, m, f, xr);
        if (virtual) r.segs.push({ x1: 0, y1: r.yh, x2: dp, y2: r.yh + r.m2 * dp, dashed: true });
        if (this.type === 'pk' && m === 0) r.segs.push({ x1: 0, y1: r.yh, x2: f, y2: 0, dashed: true });
        Draw.rayPath(v, p, r.segs, col);
      });
      Draw.arrowObj(v, p, dp, hp, PAPER_PALETTE.img, { base: "A'", tip: "B'", dashed: virtual });
      c.restore();
    }

    draw() {
      const v = this.view, c = v.ctx, p = PAPER_PALETTE;
      Draw.background(v, p, 2);
      Draw.axis(v, p, false);
      Draw.lens(v, p, this.type, v.ymax * 0.85, { shape: false });
      Draw.foci(v, p, F);
      Draw.arrowObj(v, p, -this.cfg.d, this.cfg.h, p.obj, { base: 'A', tip: 'B' });
      if (this.showAns) this.drawAnswer(p);

      const all = this.cur ? [...this.strokes, this.cur] : this.strokes;
      all.forEach((s) => {
        c.save();
        c.strokeStyle = s.color;
        c.lineWidth = s.tool === 'pen' ? 2.2 : 2;
        c.lineCap = 'round';
        c.lineJoin = 'round';
        if (s.tool === 'dash') c.setLineDash([7, 6]);
        c.beginPath();
        s.pts.forEach(([x, y], i) => (i ? c.lineTo(v.X(x), v.Y(y)) : c.moveTo(v.X(x), v.Y(y))));
        c.stroke();
        c.restore();
      });
    }

    reset() {
      this.strokes = [];
      this.showAns = false;
      this.root.querySelector('[data-act="answer"]').classList.remove('active');
      this.draw();
    }
  }

  const pads = [...document.querySelectorAll('.ws-draw')].map((r) => new SketchPad(r));
  document.addEventListener('tabshown', (e) => {
    if (e.detail === 'phieu') {
      pads.forEach((p) => { p.view.resize(); p.draw(); });
    }
  });

  // ---------- TRẠM MÃ QR DÀNH CHO GIÁO VIÊN ----------
  const PUBLIC_WORKSHEET_URL = 'https://minhlfc.github.io/nhom5-natural-thau-kinh/phieu-hoc-tap.html';

  function getDefaultWorksheetUrl() {
    if (window.location.protocol === 'file:') {
      return PUBLIC_WORKSHEET_URL;
    }
    const loc = window.location.href.split('#')[0].split('?')[0];
    if (loc.endsWith('phieu-hoc-tap.html')) return loc;
    if (loc.endsWith('.html')) return loc.replace(/[^/]+$/, 'phieu-hoc-tap.html');
    return (loc.endsWith('/') ? loc : loc + '/') + 'phieu-hoc-tap.html';
  }

  const qrUrlInput = document.getElementById('qr-url-input');
  const qrSubmitInput = document.getElementById('qr-submit-url');
  const cvQrMain = document.getElementById('cv-qr-main');
  const cvQrZoom = document.getElementById('cv-qr-zoom');

  function getEffectiveQrLink() {
    let base = (qrUrlInput && qrUrlInput.value.trim()) || getDefaultWorksheetUrl();
    const sub = qrSubmitInput && qrSubmitInput.value.trim();
    if (sub && base.includes('phieu-hoc-tap.html')) {
      const sep = base.includes('?') ? '&' : '?';
      base = `${base}${sep}submit=${encodeURIComponent(sub)}`;
    }
    return base;
  }

  function updateTeacherQr() {
    if (!cvQrMain || typeof QR === 'undefined') return;
    const link = getEffectiveQrLink();
    try {
      QR.render(cvQrMain, link, { size: 210 });
      if (cvQrZoom) QR.render(cvQrZoom, link, { size: 340 });
      const txt = document.getElementById('qr-zoom-url-text');
      if (txt) txt.textContent = link;
    } catch (e) {
      showToast('⚠️ Liên kết quá dài để tạo mã QR');
    }
  }

  if (qrUrlInput) {
    let savedUrl = localStorage.getItem('natural-qr-url');
    if (savedUrl && savedUrl.startsWith('file:')) {
      localStorage.removeItem('natural-qr-url');
      savedUrl = '';
    }
    const savedSub = localStorage.getItem('natural-qr-submit');
    qrUrlInput.value = savedUrl || getDefaultWorksheetUrl();
    if (qrSubmitInput && savedSub) qrSubmitInput.value = savedSub;
    updateTeacherQr();

    qrUrlInput.addEventListener('input', () => {
      localStorage.setItem('natural-qr-url', qrUrlInput.value.trim());
      updateTeacherQr();
    });
    if (qrSubmitInput) {
      qrSubmitInput.addEventListener('input', () => {
        localStorage.setItem('natural-qr-submit', qrSubmitInput.value.trim());
        updateTeacherQr();
      });
    }

    document.getElementById('btn-qr-default').addEventListener('click', () => {
      localStorage.removeItem('natural-qr-url');
      qrUrlInput.value = getDefaultWorksheetUrl();
      updateTeacherQr();
      showToast('↺ Đã đặt lại đường dẫn mặc định');
    });

    document.getElementById('btn-qr-copy').addEventListener('click', () => {
      navigator.clipboard?.writeText(getEffectiveQrLink());
      showToast('📋 Đã sao chép liên kết Phiếu học tập!');
    });

    const openZoom = () => {
      updateTeacherQr();
      document.getElementById('qr-modal').classList.remove('hidden');
      Sound.play('pop');
    };
    document.getElementById('btn-qr-zoom').addEventListener('click', openZoom);
    document.getElementById('qr-open-zoom').addEventListener('click', openZoom);

    const downloadQrCard = () => {
      const link = getEffectiveQrLink();
      const out = document.createElement('canvas');
      out.width = 760;
      out.height = 900;
      const ctx = out.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, out.width, out.height);
      ctx.strokeStyle = '#0d4a7a';
      ctx.lineWidth = 8;
      ctx.strokeRect(20, 20, out.width - 40, out.height - 40);

      const logo = document.querySelector('.ws-logo');
      if (logo && logo.complete && logo.naturalWidth) {
        const lw = 380;
        const lh = (logo.naturalHeight / logo.naturalWidth) * lw;
        ctx.drawImage(logo, (out.width - lw) / 2, 46, lw, lh);
      }

      ctx.fillStyle = '#d63a3f';
      ctx.font = '800 30px "Be Vietnam Pro", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('PHIẾU HỌC TẬP ĐIỆN TỬ – BÀI 8: THẤU KÍNH', out.width / 2, 195);
      ctx.fillStyle = '#0d4a7a';
      ctx.font = '700 21px "Be Vietnam Pro", sans-serif';
      ctx.fillText('Nhóm Natural · Khoa học tự nhiên 9', out.width / 2, 230);

      const tmp = document.createElement('canvas');
      QR.render(tmp, link, { size: 480 });
      ctx.drawImage(tmp, (out.width - 480) / 2, 265, 480, 480);

      ctx.fillStyle = '#10233a';
      ctx.font = '700 20px "Be Vietnam Pro", sans-serif';
      ctx.fillText('📱 Quét mã QR bằng Camera hoặc Zalo để làm bài & nộp cho Giáo viên', out.width / 2, 790);
      ctx.fillStyle = '#5b6d82';
      ctx.font = '500 15px "Be Vietnam Pro", sans-serif';
      ctx.fillText(link.slice(0, 85), out.width / 2, 830);

      const a = document.createElement('a');
      a.download = 'Ma-QR-Phieu-Hoc-Tap-Bai8-ThauKinh-Natural.png';
      a.href = out.toDataURL('image/png');
      a.click();
      showToast('⬇ Đã tải thẻ Mã QR Phiếu học tập!');
    };
    document.getElementById('btn-qr-dl').addEventListener('click', downloadQrCard);
    document.getElementById('btn-qr-zoom-dl').addEventListener('click', downloadQrCard);
  }

  // ---------- Chấm điểm ----------
  const result = document.getElementById('ws-result');
  function gradeWorksheet(highlight = true) {
    const qs = [...document.querySelectorAll('select.ws-q')];
    let ok = 0;
    const answers = [];
    qs.forEach((s) => {
      if (highlight) s.classList.remove('ok', 'bad');
      const good = s.value === s.dataset.ans;
      if (highlight) s.classList.add(good ? 'ok' : 'bad');
      if (good) ok++;
      answers.push({
        label: s.dataset.label || '',
        val: s.value,
        text: OPT_TEXT[s.value] || '(Chưa chọn)',
        good,
      });
    });
    return { ok, total: qs.length, answers };
  }

  document.getElementById('ws-check').addEventListener('click', () => {
    const { ok, total } = gradeWorksheet(true);
    const name = document.getElementById('ws-name').value.trim();
    const all = ok === total;
    result.className = 'result ' + (all ? 'ok' : 'bad');
    result.textContent = all
      ? `🎉 Xuất sắc${name ? ', ' + name : ''}! Đúng ${ok}/${total} câu.`
      : `Đúng ${ok}/${total} câu. Hãy xem lại các ô màu đỏ và làm lại thí nghiệm nhé!`;
    Sound.play(all ? 'correct' : 'wrong');
  });

  // ---------- Vẽ ảnh tổng hợp toàn bộ Phiếu học tập (PNG chất lượng cao) ----------
  function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
    const words = (text || '').split(/\s+/);
    let line = '';
    let curY = y;
    for (let n = 0; n < words.length; n++) {
      const testLine = line + words[n] + ' ';
      if (ctx.measureText(testLine).width > maxWidth && n > 0) {
        ctx.fillText(line, x, curY);
        line = words[n] + ' ';
        curY += lineHeight;
      } else {
        line = testLine;
      }
    }
    ctx.fillText(line, x, curY);
    return curY;
  }

  function renderWorksheetImage(gradeInfo) {
    const name = document.getElementById('ws-name').value.trim() || 'Chưa ghi tên';
    const cls = document.getElementById('ws-class').value.trim() || '—';
    const note = document.getElementById('ws-note').value.trim() || '(Học sinh chưa ghi nhận xét)';
    const nowStr = new Date().toLocaleString('vi-VN');

    const W = 1200, H = 1480;
    const cv = document.createElement('canvas');
    cv.width = W;
    cv.height = H;
    const c = cv.getContext('2d');

    // Nền giấy trắng
    c.fillStyle = '#ffffff';
    c.fillRect(0, 0, W, H);
    c.strokeStyle = '#0d4a7a';
    c.lineWidth = 6;
    c.strokeRect(18, 18, W - 36, H - 36);

    // Header: Logo + Tiêu đề
    const logo = document.querySelector('.ws-logo');
    if (logo && logo.complete && logo.naturalWidth) {
      const lw = 340;
      const lh = (logo.naturalHeight / logo.naturalWidth) * lw;
      c.drawImage(logo, 45, 42, lw, lh);
    }
    c.textAlign = 'right';
    c.fillStyle = '#0d4a7a';
    c.font = '800 18px "Be Vietnam Pro", sans-serif';
    c.fillText('NHÓM NATURAL · KHOA HỌC TỰ NHIÊN 9', W - 48, 62);
    c.fillStyle = '#d63a3f';
    c.font = '800 34px "Be Vietnam Pro", sans-serif';
    c.fillText('PHIẾU HỌC TẬP – BÀI 8: THẤU KÍNH', W - 48, 102);
    c.fillStyle = '#5b6d82';
    c.font = '600 16px "Be Vietnam Pro", sans-serif';
    c.fillText(`Thời gian nộp: ${nowStr}`, W - 48, 130);

    // Khung thông tin HS & Điểm
    c.fillStyle = '#f3f7fc';
    c.strokeStyle = '#cfdceb';
    c.lineWidth = 2;
    c.fillRect(45, 155, W - 90, 74);
    c.strokeRect(45, 155, W - 90, 74);

    c.textAlign = 'left';
    c.fillStyle = '#10233a';
    c.font = '700 22px "Be Vietnam Pro", sans-serif';
    c.fillText(`Họ và tên: ${name}`, 68, 200);
    c.fillText(`Lớp: ${cls}`, 620, 200);

    // Huy hiệu điểm
    c.fillStyle = gradeInfo.ok === gradeInfo.total ? '#16a34a' : '#0d4a7a';
    c.fillRect(W - 310, 169, 245, 46);
    c.fillStyle = '#ffffff';
    c.textAlign = 'center';
    c.font = '800 20px "Be Vietnam Pro", sans-serif';
    c.fillText(`Kết quả: ${gradeInfo.ok}/${gradeInfo.total} câu đúng`, W - 187, 199);

    // Phần 1: Bảng đường truyền tia sáng
    c.textAlign = 'left';
    c.fillStyle = '#0d4a7a';
    c.font = '800 22px "Be Vietnam Pro", sans-serif';
    c.fillText('1. Đường truyền của các tia sáng đặc biệt qua thấu kính', 45, 268);

    const rows = [
      ['Tia sáng đi qua quang tâm O', gradeInfo.answers[0], gradeInfo.answers[1]],
      ['Tia sáng song song với trục chính', gradeInfo.answers[2], gradeInfo.answers[3]],
      ["Tia sáng đi qua tiêu điểm chính (TKPK: hướng tới F')", gradeInfo.answers[4], gradeInfo.answers[5]],
    ];
    const tx = 45, ty = 285, tw = W - 90, rh = 54;
    const cw = [360, (tw - 360) / 2, (tw - 360) / 2];

    // Header bảng
    c.fillStyle = '#e7eff8';
    c.fillRect(tx, ty, tw, 46);
    c.strokeStyle = '#b9cde3';
    c.strokeRect(tx, ty, tw, 46);
    c.fillStyle = '#10233a';
    c.font = '700 17px "Be Vietnam Pro", sans-serif';
    c.fillText('Tia tới', tx + 14, ty + 29);
    c.fillText('Thấu kính hội tụ – Tia ló', tx + cw[0] + 14, ty + 29);
    c.fillText('Thấu kính phân kì – Tia ló', tx + cw[0] + cw[1] + 14, ty + 29);

    rows.forEach((r, idx) => {
      const y = ty + 46 + idx * rh;
      c.fillStyle = idx % 2 === 0 ? '#ffffff' : '#f9fbfe';
      c.fillRect(tx, y, tw, rh);
      c.strokeStyle = '#cbd9ea';
      c.strokeRect(tx, y, tw, rh);
      c.beginPath();
      c.moveTo(tx + cw[0], y); c.lineTo(tx + cw[0], y + rh);
      c.moveTo(tx + cw[0] + cw[1], y); c.lineTo(tx + cw[0] + cw[1], y + rh);
      c.stroke();

      c.fillStyle = '#10233a';
      c.font = '600 16px "Be Vietnam Pro", sans-serif';
      c.fillText(r[0], tx + 14, y + 33);

      [r[1], r[2]].forEach((ans, j) => {
        const x0 = tx + cw[0] + (j === 1 ? cw[1] : 0) + 14;
        c.fillStyle = ans.good ? '#15803d' : '#dc2626';
        c.font = '700 16px "Be Vietnam Pro", sans-serif';
        c.fillText(`${ans.good ? '✓' : '✗'} ${ans.text}`, x0, y + 33);
      });
    });

    // Phần 2: Hình vẽ ảnh qua TKHT & TKPK
    const y2 = 535;
    c.fillStyle = '#0d4a7a';
    c.font = '800 22px "Be Vietnam Pro", sans-serif';
    c.fillText('2. Vẽ ảnh của vật qua thấu kính hội tụ và thấu kính phân kì', 45, y2);

    const boxW = (W - 114) / 2;
    const boxH = 360;
    pads.forEach((pad, idx) => {
      const bx = 45 + idx * (boxW + 24);
      const by = y2 + 18;
      c.fillStyle = '#f8fafd';
      c.strokeStyle = '#b9cde3';
      c.lineWidth = 2;
      c.fillRect(bx, by, boxW, boxH + 88);
      c.strokeRect(bx, by, boxW, boxH + 88);

      c.fillStyle = '#10233a';
      c.font = '700 18px "Be Vietnam Pro", sans-serif';
      c.fillText(
        idx === 0 ? 'a) Thấu kính hội tụ (f = 10 cm, d = 18 cm)' : 'b) Thấu kính phân kì (f = 10 cm, d = 15 cm)',
        bx + 14,
        by + 28
      );

      c.drawImage(pad.view.canvas, bx + 12, by + 40, boxW - 24, boxH - 12);

      const baseIdx = idx === 0 ? 6 : 9;
      const p1 = gradeInfo.answers[baseIdx];
      const p2 = gradeInfo.answers[baseIdx + 1];
      const p3 = gradeInfo.answers[baseIdx + 2];
      c.fillStyle = '#10233a';
      c.font = '700 16px "Be Vietnam Pro", sans-serif';
      c.fillText(
        `Tính chất ảnh A'B': ${p1.text} (${p1.good ? '✓' : '✗'}) · ${p2.text} (${p2.good ? '✓' : '✗'}) · ${p3.text} (${p3.good ? '✓' : '✗'})`,
        bx + 14,
        by + boxH + 62
      );
    });

    // Phần 3: Nhận xét của học sinh
    const y3 = 1045;
    c.fillStyle = '#0d4a7a';
    c.font = '800 22px "Be Vietnam Pro", sans-serif';
    c.fillText('3. Nhận xét / kết luận của học sinh', 45, y3);

    c.fillStyle = '#f8fafd';
    c.strokeStyle = '#b9cde3';
    c.fillRect(45, y3 + 16, W - 90, 355);
    c.strokeRect(45, y3 + 16, W - 90, 355);

    c.fillStyle = '#10233a';
    c.font = '500 19px "Be Vietnam Pro", sans-serif';
    wrapText(c, note, 68, y3 + 56, W - 136, 30);

    c.textAlign = 'center';
    c.fillStyle = '#5b6d82';
    c.font = '600 15px "Be Vietnam Pro", sans-serif';
    c.fillText('Phiếu học tập điện tử được tạo từ Phòng thí nghiệm ảo Bài 8: Thấu kính – Nhóm Natural (Trường ĐHSP TP.HCM)', W / 2, H - 36);

    return cv;
  }

  // ---------- Lưu & Đồng bộ Hộp bài nộp của Giáo viên ----------
  const bc = typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('natural-ws-channel') : null;

  function getInboxList() {
    try {
      return JSON.parse(localStorage.getItem('natural-ws-inbox') || '[]');
    } catch {
      return [];
    }
  }

  function saveToInbox(entry) {
    const list = getInboxList();
    list.unshift(entry);
    localStorage.setItem('natural-ws-inbox', JSON.stringify(list.slice(0, 50)));
    updateInboxUI();
  }

  function updateInboxUI() {
    const cnt = document.getElementById('inbox-count');
    const listEl = document.getElementById('inbox-list');
    const list = getInboxList();
    if (cnt) cnt.textContent = list.length;
    if (!listEl) return;
    if (!list.length) {
      listEl.innerHTML = '<div class="muted" style="text-align:center;padding:24px">Chưa có bài nộp nào. Khi học sinh nộp bài hoặc khi GV dán Mã bài nộp, kết quả sẽ hiện tại đây.</div>';
      return;
    }
    listEl.innerHTML = list
      .map(
        (it, i) => `
      <div class="inbox-item">
        <div>
          <b>${i + 1}. ${it.n}</b> <span class="badge">Lớp: ${it.c}</span>
          <div class="muted" style="font-size:.82rem">Điểm trắc nghiệm: <b style="color:var(--ok)">${it.s}</b> · Nộp lúc: ${it.t}</div>
          ${it.note ? `<div style="font-size:.85rem;margin-top:4px">💬 <i>${it.note}</i></div>` : ''}
        </div>
        <span class="role-badge leader">${it.s}</span>
      </div>`
      )
      .join('');
  }

  if (bc) {
    bc.onmessage = (ev) => {
      if (ev.data && ev.data.type === 'ws-submit') {
        saveToInbox(ev.data.payload);
        showToast(`📥 Học sinh ${ev.data.payload.n} (${ev.data.payload.c}) vừa nộp phiếu!`);
      }
    };
  }
  updateInboxUI();

  const btnInboxOpen = document.getElementById('btn-inbox-open');
  if (btnInboxOpen) {
    btnInboxOpen.addEventListener('click', () => {
      updateInboxUI();
      document.getElementById('inbox-modal').classList.remove('hidden');
      Sound.play('pop');
    });
    document.getElementById('btn-inbox-import').addEventListener('click', () => {
      const raw = document.getElementById('inbox-import-input').value.trim();
      if (!raw) return;
      try {
        const code = raw.includes('code=') ? decodeURIComponent(raw.split('code=')[1].split('&')[0]) : raw;
        const json = decodeURIComponent(escape(atob(code)));
        const data = JSON.parse(json);
        saveToInbox(data);
        document.getElementById('inbox-import-input').value = '';
        Sound.play('correct');
        showToast(`✔ Đã nhập bài của ${data.n} (${data.c})!`);
      } catch (e) {
        Sound.play('wrong');
        showToast('⚠️ Mã bài nộp không hợp lệ');
      }
    });
    document.getElementById('btn-inbox-clear').addEventListener('click', () => {
      if (!confirm('Xoá danh sách bài nộp trên máy này?')) return;
      localStorage.removeItem('natural-ws-inbox');
      updateInboxUI();
    });
  }

  // ---------- Nút NỘP BÀI CHO GIÁO VIÊN ----------
  let lastRenderedCanvas = null;
  let lastFileName = 'Phieu-Hoc-Tap-Bai8.png';

  const btnSubmit = document.getElementById('ws-submit');
  if (btnSubmit) {
    btnSubmit.addEventListener('click', async () => {
      const nameEl = document.getElementById('ws-name');
      const classEl = document.getElementById('ws-class');
      const name = nameEl.value.trim();
      const cls = classEl.value.trim();

      if (!name) {
        showToast('⚠️ Em hãy nhập Họ và tên trước khi nộp bài nhé!');
        Sound.play('wrong');
        nameEl.focus();
        return;
      }
      if (!cls) {
        showToast('⚠️ Em hãy nhập Lớp trước khi nộp bài nhé!');
        Sound.play('wrong');
        classEl.focus();
        return;
      }

      const g = gradeWorksheet(true);
      result.className = 'result ' + (g.ok === g.total ? 'ok' : 'bad');
      result.textContent = `Đã chấm: ${g.ok}/${g.total} câu đúng.`;

      // Vẽ ảnh phiếu
      lastRenderedCanvas = renderWorksheetImage(g);
      const safeName = name.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]+/g, '_');
      const safeCls = cls.replace(/[^a-zA-Z0-9]+/g, '_');
      lastFileName = `PhieuHocTap_Bai8_${safeName}_${safeCls}.png`;

      const dataUrl = lastRenderedCanvas.toDataURL('image/png');
      document.getElementById('sub-preview-img').src = dataUrl;
      document.getElementById('sub-title').textContent = `🎉 Đã hoàn thành phiếu của ${name} (${cls}) – ${g.ok}/${g.total} câu đúng!`;

      // Tạo gói kết quả gọn cho Mã QR & Hộp bài nộp
      const payload = {
        n: name,
        c: cls,
        s: `${g.ok}/${g.total}`,
        t: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
        note: document.getElementById('ws-note').value.trim().slice(0, 120),
      };
      const codeStr = btoa(unescape(encodeURIComponent(JSON.stringify(payload))));
      document.getElementById('sub-code-text').value = codeStr;

      const cvResQr = document.getElementById('cv-qr-result');
      if (cvResQr && typeof QR !== 'undefined') {
        try {
          QR.render(cvResQr, codeStr, { size: 180 });
        } catch {
          QR.render(cvResQr, `${name} - ${cls}: ${g.ok}/${g.total}`, { size: 180 });
        }
      }

      // Lưu vào hộp bài nộp & phát qua BroadcastChannel
      saveToInbox(payload);
      if (bc) bc.postMessage({ type: 'ws-submit', payload });

      // Kiểm tra link nhận bài của GV (từ tham số URL ?submit= hoặc ô cấu hình của GV)
      const params = new URLSearchParams(window.location.search);
      const submitTarget = params.get('submit') || localStorage.getItem('natural-qr-submit') || '';
      const extBtn = document.getElementById('btn-sub-ext-link');
      const statusEl = document.getElementById('sub-webhook-status');
      statusEl.textContent = '';

      if (submitTarget) {
        extBtn.style.display = '';
        extBtn.onclick = () => window.open(submitTarget, '_blank');
        if (submitTarget.includes('script.google.com') || submitTarget.includes('webhook')) {
          statusEl.textContent = '⏳ Đang gửi kết quả về hệ thống của Giáo viên...';
          try {
            await fetch(submitTarget, {
              method: 'POST',
              mode: 'no-cors',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ ...payload, image: dataUrl }),
            });
            statusEl.textContent = '✅ Đã gửi dữ liệu bài làm về hệ thống của Giáo viên!';
            statusEl.style.color = 'var(--ok)';
          } catch {
            statusEl.textContent = '⚠️ Không kết nối được webhook, em hãy tải ảnh phiếu để nộp nhé.';
          }
        }
      } else {
        extBtn.style.display = 'none';
      }

      document.getElementById('submit-modal').classList.remove('hidden');
      Sound.play('correct');
    });
  }

  // Nút tải ảnh Phiếu PNG
  const btnSubDl = document.getElementById('btn-sub-dl');
  if (btnSubDl) {
    btnSubDl.addEventListener('click', () => {
      if (!lastRenderedCanvas) return;
      const a = document.createElement('a');
      a.download = lastFileName;
      a.href = lastRenderedCanvas.toDataURL('image/png');
      a.click();
      showToast('⬇ Đã tải ảnh Phiếu học tập (PNG)!');
    });
  }

  // Nút chia sẻ nhanh trên điện thoại (Web Share API)
  const btnSubShare = document.getElementById('btn-sub-share');
  if (btnSubShare) {
    btnSubShare.addEventListener('click', () => {
      if (!lastRenderedCanvas) return;
      lastRenderedCanvas.toBlob(async (blob) => {
        if (!blob) return;
        const file = new File([blob], lastFileName, { type: 'image/png' });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
          try {
            await navigator.share({
              title: 'Phiếu học tập Bài 8: Thấu kính',
              text: `Bài làm của ${document.getElementById('ws-name').value.trim()} (${document.getElementById('ws-class').value.trim()})`,
              files: [file],
            });
            return;
          } catch {
            /* người dùng huỷ chia sẻ */
          }
        }
        // Fallback: tải ảnh về máy
        const a = document.createElement('a');
        a.download = lastFileName;
        a.href = URL.createObjectURL(blob);
        a.click();
        showToast('⬇ Đã tải ảnh phiếu để em đính kèm gửi Giáo viên!');
      }, 'image/png');
    });
  }

  const btnCopyCode = document.getElementById('btn-sub-copy-code');
  if (btnCopyCode) {
    btnCopyCode.addEventListener('click', () => {
      const inp = document.getElementById('sub-code-text');
      navigator.clipboard?.writeText(inp.value);
      showToast('📋 Đã sao chép Mã bài nộp!');
    });
  }

  document.getElementById('ws-print').addEventListener('click', () => {
    if (!document.getElementById('ws-name').value.trim()) {
      showToast('⚠️ Em hãy nhập họ và tên trước khi in phiếu!');
      Sound.play('wrong');
      document.getElementById('ws-name').focus();
      return;
    }
    Sound.play('click');
    setTimeout(() => window.print(), 150);
  });

  document.getElementById('ws-reset').addEventListener('click', () => {
    if (!confirm('Xoá toàn bộ câu trả lời và hình vẽ trên phiếu?')) return;
    document.querySelectorAll('select.ws-q').forEach((s) => {
      s.value = '';
      s.classList.remove('ok', 'bad');
    });
    document.getElementById('ws-note').value = '';
    pads.forEach((p) => p.reset());
    result.textContent = '';
    Sound.play('pop');
  });
})();
