/* =========================================================
   Phiếu học tập điện tử + Trạm Mã QR + Đồng bộ nộp bài trực tuyến Thời gian thực
   ========================================================= */
(function () {
  const IS_STUDENT_PAGE =
    document.body.dataset.role === 'student' ||
    document.body.classList.contains('standalone-ws-body');

  // Kênh đồng bộ thời gian thực giữa trang Học sinh (phieu-hoc-tap.html) và trang Giáo viên (index.html)
  const CLOUD_TOPIC = 'natural_hcmue_khtn9_bai8_v1';
  const CLOUD_BASE = `https://ntfy.sh/${CLOUD_TOPIC}`;

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

  const ANS_KEYS = [
    'thang', 'thang',
    'quaF2', 'keoF',
    'songsong', 'songsong',
    'that', 'nguoc', 'lon',
    'ao', 'cung', 'nho',
  ];

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

  function drawPadContent(v, type, strokes, showAns = false) {
    const c = v.ctx, p = PAPER_PALETTE;
    const cfg = SETUP[type];
    Draw.background(v, p, 2);
    Draw.axis(v, p, false);
    Draw.lens(v, p, type, v.ymax * 0.85, { shape: false });
    Draw.foci(v, p, F);
    Draw.arrowObj(v, p, -cfg.d, cfg.h, p.obj, { base: 'A', tip: 'B' });

    if (showAns) {
      const f = type === 'ht' ? F : -F;
      const { d, h } = cfg;
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
        if (type === 'pk' && m === 0) r.segs.push({ x1: 0, y1: r.yh, x2: f, y2: 0, dashed: true });
        Draw.rayPath(v, p, r.segs, col);
      });
      Draw.arrowObj(v, p, dp, hp, PAPER_PALETTE.img, { base: "A'", tip: "B'", dashed: virtual });
      c.restore();
    }

    (strokes || []).forEach((s) => {
      c.save();
      c.strokeStyle = s.color || '#d32f2f';
      c.lineWidth = s.tool === 'pen' ? 2.2 : 2;
      c.lineCap = 'round';
      c.lineJoin = 'round';
      if (s.tool === 'dash') c.setLineDash([7, 6]);
      c.beginPath();
      (s.pts || []).forEach(([x, y], i) => (i ? c.lineTo(v.X(x), v.Y(y)) : c.moveTo(v.X(x), v.Y(y))));
      c.stroke();
      c.restore();
    });
  }

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
      const btnUndo = r.querySelector('[data-act="undo"]');
      if (btnUndo) {
        btnUndo.addEventListener('click', () => {
          this.strokes.pop();
          Sound.play('click');
          this.draw();
        });
      }
      const btnClear = r.querySelector('[data-act="clear"]');
      if (btnClear) {
        btnClear.addEventListener('click', () => {
          this.strokes = [];
          Sound.play('pop');
          this.draw();
        });
      }
      const ans = r.querySelector('[data-act="answer"]');
      if (ans) {
        ans.addEventListener('click', () => {
          this.showAns = !this.showAns;
          ans.classList.toggle('active', this.showAns);
          Sound.play('toggle');
          this.draw();
        });
      }

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

    draw() {
      const all = this.cur ? [...this.strokes, this.cur] : this.strokes;
      drawPadContent(this.view, this.type, all, !IS_STUDENT_PAGE && this.showAns);
    }

    reset() {
      this.strokes = [];
      this.showAns = false;
      const ans = this.root.querySelector('[data-act="answer"]');
      if (ans) ans.classList.remove('active');
      this.draw();
    }
  }

  const pads = [...document.querySelectorAll('.ws-draw')].map((r) => new SketchPad(r));
  document.addEventListener('tabshown', (e) => {
    if (e.detail === 'phieu') {
      pads.forEach((p) => {
        p.view.resize();
        p.draw();
      });
    }
  });

  // Nén nét vẽ để truyền qua mạng nhanh gọn (< 2 KB)
  function compactStrokes(strokes) {
    return (strokes || []).slice(0, 35).map((s) => {
      let pts = s.pts || [];
      if (pts.length > 24) {
        const step = (pts.length - 1) / 23;
        pts = Array.from({ length: 24 }, (_, i) => pts[Math.round(i * step)]);
      }
      return {
        tool: s.tool,
        color: s.color,
        pts: pts.map(([x, y]) => [Math.round(x * 10) / 10, Math.round(y * 10) / 10]),
      };
    });
  }

  // Dựng ảnh canvas offscreen cho 1 khung vẽ bất kỳ (dùng khi GV xem bài nộp của HS)
  function renderOffscreenPad(type, strokes) {
    const cv = document.createElement('canvas');
    cv.style.width = '520px';
    cv.style.height = '346px';
    document.body.appendChild(cv);
    cv.getBoundingClientRect = () => ({ width: 520, height: 346 });
    const v = new LensView(cv, 64);
    drawPadContent(v, type, strokes || [], false);
    cv.remove();
    return cv;
  }

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

  function evaluateValues(vals) {
    let ok = 0;
    const answers = ANS_KEYS.map((ansKey, i) => {
      const val = (vals && vals[i]) || '';
      const good = val === ansKey;
      if (good) ok++;
      return {
        val,
        text: OPT_TEXT[val] || '(Chưa chọn)',
        good,
      };
    });
    return { ok, total: ANS_KEYS.length, answers, vals };
  }

  function gradeWorksheet(highlight = true) {
    const qs = [...document.querySelectorAll('select.ws-q')];
    const vals = qs.map((s) => s.value);
    const info = evaluateValues(vals);
    if (highlight && !IS_STUDENT_PAGE) {
      qs.forEach((s, i) => {
        s.classList.remove('ok', 'bad');
        s.classList.add(info.answers[i].good ? 'ok' : 'bad');
      });
    }
    return info;
  }

  const btnCheck = document.getElementById('ws-check');
  if (btnCheck && !IS_STUDENT_PAGE) {
    btnCheck.addEventListener('click', () => {
      const { ok, total } = gradeWorksheet(true);
      const name = document.getElementById('ws-name').value.trim();
      const all = ok === total;
      result.className = 'result ' + (all ? 'ok' : 'bad');
      result.textContent = all
        ? `🎉 Xuất sắc${name ? ', ' + name : ''}! Đúng ${ok}/${total} câu.`
        : `Đúng ${ok}/${total} câu. Hãy xem lại các ô màu đỏ và làm lại thí nghiệm nhé!`;
      Sound.play(all ? 'correct' : 'wrong');
    });
  }

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

  /**
   * Dựng ảnh Phiếu học tập:
   * - Khi Học sinh tải/xem trên phieu-hoc-tap.html: showGrade = false (KHÔNG lộ điểm, KHÔNG lộ đúng/sai ✓/✗)
   * - Khi Giáo viên xem trên index.html: showGrade = true (Hiện điểm chấm tự động & dấu ✓/✗ từng câu)
   */
  function renderWorksheetImage(data, opts = {}) {
    const { showGrade = false } = opts;
    const name = data.n || 'Chưa ghi tên';
    const cls = data.c || '—';
    const note = data.note || '(Học sinh chưa ghi nhận xét)';
    const nowStr = data.t || new Date().toLocaleString('vi-VN');
    const gradeInfo = data.gradeInfo || evaluateValues(data.vals || []);
    const padCanvases = data.padCanvases || pads.map((p) => p.view.canvas);

    const W = 1200, H = 1480;
    const cv = document.createElement('canvas');
    cv.width = W;
    cv.height = H;
    const c = cv.getContext('2d');

    c.fillStyle = '#ffffff';
    c.fillRect(0, 0, W, H);
    c.strokeStyle = '#0d4a7a';
    c.lineWidth = 6;
    c.strokeRect(18, 18, W - 36, H - 36);

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

    // Huy hiệu góc phải: Giáo viên thấy điểm, Học sinh chỉ thấy "Đã nộp bài"
    c.fillStyle = showGrade ? (gradeInfo.ok === gradeInfo.total ? '#16a34a' : '#0d4a7a') : '#0d4a7a';
    c.fillRect(W - 320, 169, 255, 46);
    c.fillStyle = '#ffffff';
    c.textAlign = 'center';
    c.font = '800 19px "Be Vietnam Pro", sans-serif';
    c.fillText(
      showGrade ? `Điểm: ${gradeInfo.ok}/${gradeInfo.total} câu đúng` : 'Trạng thái: Đã nộp bài',
      W - 192,
      198
    );

    // Phần 1
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
        if (showGrade) {
          c.fillStyle = ans.good ? '#15803d' : '#dc2626';
          c.font = '700 16px "Be Vietnam Pro", sans-serif';
          c.fillText(`${ans.good ? '✓' : '✗'} ${ans.text}`, x0, y + 33);
        } else {
          c.fillStyle = '#10233a';
          c.font = '600 16px "Be Vietnam Pro", sans-serif';
          c.fillText(ans.text, x0, y + 33);
        }
      });
    });

    // Phần 2
    const y2 = 535;
    c.fillStyle = '#0d4a7a';
    c.font = '800 22px "Be Vietnam Pro", sans-serif';
    c.fillText('2. Vẽ ảnh của vật qua thấu kính hội tụ và thấu kính phân kì', 45, y2);

    const boxW = (W - 114) / 2;
    const boxH = 360;
    [0, 1].forEach((idx) => {
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

      if (padCanvases[idx]) {
        c.drawImage(padCanvases[idx], bx + 12, by + 40, boxW - 24, boxH - 12);
      }

      const baseIdx = idx === 0 ? 6 : 9;
      const p1 = gradeInfo.answers[baseIdx];
      const p2 = gradeInfo.answers[baseIdx + 1];
      const p3 = gradeInfo.answers[baseIdx + 2];
      c.fillStyle = '#10233a';
      c.font = '700 16px "Be Vietnam Pro", sans-serif';
      const propStr = showGrade
        ? `Ảnh A'B': ${p1.text} (${p1.good ? '✓' : '✗'}) · ${p2.text} (${p2.good ? '✓' : '✗'}) · ${p3.text} (${p3.good ? '✓' : '✗'})`
        : `Ảnh A'B': ${p1.text} · ${p2.text} · ${p3.text}`;
      c.fillText(propStr, bx + 14, by + boxH + 62);
    });

    // Phần 3
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
    c.fillText('Phiếu học tập điện tử – Bài 8: Thấu kính · Nhóm Natural (Trường ĐHSP TP.HCM)', W / 2, H - 36);

    return cv;
  }

  // ---------- ĐỒNG BỘ HỘP BÀI NỘP CỦA GIÁO VIÊN (REAL-TIME QUA MẠNG) ----------
  const bc = typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('natural-ws-channel') : null;

  function getInboxList() {
    try {
      return JSON.parse(localStorage.getItem('natural-ws-inbox') || '[]');
    } catch {
      return [];
    }
  }

  function saveToInbox(entry, notify = false) {
    if (!entry || !entry.n) return false;
    const list = getInboxList();
    const uid = entry.id || `${entry.n}_${entry.c}_${entry.t}`;
    const existIdx = list.findIndex((x) => (x.id || `${x.n}_${x.c}_${x.t}`) === uid);
    if (existIdx !== -1) {
      if (entry.vals && !list[existIdx].vals) {
        list[existIdx] = { ...list[existIdx], ...entry, id: uid };
        localStorage.setItem('natural-ws-inbox', JSON.stringify(list.slice(0, 80)));
        updateInboxUI();
      }
      return false; // Đã có trong danh sách
    }
    entry.id = uid;
    list.unshift(entry);
    localStorage.setItem('natural-ws-inbox', JSON.stringify(list.slice(0, 80)));
    updateInboxUI();
    if (notify && !IS_STUDENT_PAGE) {
      Sound.play('correct');
      showToast(`📥 Học sinh ${entry.n} (${entry.c}) vừa nộp bài! Điểm: ${entry.s}`);
    }
    return true;
  }

  // Nạp trực tiếp bài làm của học sinh vào Phiếu học tập bên dưới trên màn hình Giáo viên để chữa bài
  function loadSubmissionIntoForm(entry) {
    if (!entry || IS_STUDENT_PAGE) return;
    const nameEl = document.getElementById('ws-name');
    const classEl = document.getElementById('ws-class');
    const noteEl = document.getElementById('ws-note');
    if (nameEl) nameEl.value = entry.n || '';
    if (classEl) classEl.value = entry.c || '';
    if (noteEl) noteEl.value = entry.note || '';

    const qs = [...document.querySelectorAll('select.ws-q')];
    const vals = entry.vals || [];
    qs.forEach((s, i) => {
      s.value = vals[i] || '';
    });
    const g = gradeWorksheet(true);

    if (pads[0]) {
      pads[0].strokes = JSON.parse(JSON.stringify(entry.drw?.ht || []));
      pads[0].view.resize();
      pads[0].draw();
    }
    if (pads[1]) {
      pads[1].strokes = JSON.parse(JSON.stringify(entry.drw?.pk || []));
      pads[1].view.resize();
      pads[1].draw();
    }

    if (result) {
      result.className = 'result ' + (g.ok === g.total ? 'ok' : 'bad');
      result.textContent = `📋 Đang hiển thị bài làm của học sinh: ${entry.n} (Lớp ${entry.c}) — Điểm trắc nghiệm: ${entry.s || `${g.ok}/${g.total}`}`;
    }
  }

  // Mở hộp thoại xem chi tiết phiếu + hình vẽ của 1 học sinh bất kỳ (dành cho Giáo viên)
  let currentTeacherDetailCanvas = null;
  let currentTeacherDetailName = 'PhieuHocTap.png';

  function openStudentDetailModal(entry) {
    if (!entry) return;
    // Đồng thời nạp bài của học sinh xuống Phiếu bên dưới để Giáo viên có thể chữa trực tiếp
    loadSubmissionIntoForm(entry);

    const modal = document.getElementById('student-detail-modal');
    if (!modal) return;
    const padHt = renderOffscreenPad('ht', entry.drw?.ht || []);
    const padPk = renderOffscreenPad('pk', entry.drw?.pk || []);
    const gradeInfo = evaluateValues(entry.vals || []);
    const scoreText = entry.vals ? `${gradeInfo.ok}/${gradeInfo.total}` : (entry.s || `${gradeInfo.ok}/${gradeInfo.total}`);
    currentTeacherDetailCanvas = renderWorksheetImage(
      {
        n: entry.n,
        c: entry.c,
        t: entry.t,
        note: entry.note,
        gradeInfo,
        padCanvases: [padHt, padPk],
      },
      { showGrade: true }
    );
    const safeName = (entry.n || 'HS').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]+/g, '_');
    currentTeacherDetailName = `PhieuDaCham_${safeName}_${entry.c || ''}.png`;
    document.getElementById('stu-detail-title').textContent = `Phiếu của ${entry.n} (Lớp ${entry.c}) – Điểm: ${scoreText}`;
    document.getElementById('stu-detail-img').src = currentTeacherDetailCanvas.toDataURL('image/png');
    modal.classList.remove('hidden');
    Sound.play('pop');
  }

  const btnStuEditLive = document.getElementById('btn-stu-edit-live');
  if (btnStuEditLive) {
    btnStuEditLive.addEventListener('click', () => {
      document.getElementById('student-detail-modal')?.classList.add('hidden');
      document.getElementById('inbox-modal')?.classList.add('hidden');
      const ws = document.getElementById('worksheet');
      if (ws) ws.scrollIntoView({ behavior: 'smooth', block: 'start' });
      Sound.play('click');
      showToast('✏️ Đã nạp bài học sinh vào Phiếu bên dưới để Giáo viên chữa trực tiếp!');
    });
  }

  const btnStuDetailDl = document.getElementById('btn-stu-detail-dl');
  if (btnStuDetailDl) {
    btnStuDetailDl.addEventListener('click', () => {
      if (!currentTeacherDetailCanvas) return;
      const a = document.createElement('a');
      a.download = currentTeacherDetailName;
      a.href = currentTeacherDetailCanvas.toDataURL('image/png');
      a.click();
      showToast('⬇ Đã tải ảnh Phiếu đã chấm của học sinh!');
    });
  }

  function renderInboxListHTML(list) {
    if (!list.length) {
      return '<div class="muted" style="text-align:center;padding:22px">Chưa có học sinh nào nộp bài. Khi học sinh bấm <b>“🚀 Nộp bài cho Giáo viên”</b> ở link <code>phieu-hoc-tap.html</code>, bài làm sẽ tự động hiện ngay tại đây.</div>';
    }
    return list
      .map(
        (it, i) => `
      <div class="inbox-item" data-row-idx="${i}" title="Bấm vào đây để xem toàn bộ Phiếu học tập và hình vẽ của ${it.n}">
        <div>
          <b>${i + 1}. ${it.n}</b> <span class="badge">Lớp: ${it.c}</span>
          <div class="muted" style="font-size:.82rem">Điểm tự động: <b style="color:var(--ok)">${it.s || '—'}</b> · Nộp lúc: ${it.t || ''}</div>
          ${it.note ? `<div style="font-size:.85rem;margin-top:4px">💬 <i>${it.note}</i></div>` : ''}
        </div>
        <div class="row-actions">
          <button type="button" class="btn btn-primary btn-tiny" data-view-idx="${i}">👁 Xem phiếu &amp; hình vẽ</button>
        </div>
      </div>`
      )
      .join('');
  }

  function updateInboxUI() {
    const list = getInboxList();
    const cnt1 = document.getElementById('inbox-count');
    const cnt2 = document.getElementById('live-inbox-count');
    if (cnt1) cnt1.textContent = list.length;
    if (cnt2) cnt2.textContent = list.length;

    const html = renderInboxListHTML(list);
    ['inbox-list', 'live-inbox-list'].forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.innerHTML = html;
      // Bấm vào bất kỳ vị trí nào trên dòng tên học sinh hoặc nút "Xem phiếu & hình vẽ" đều mở ngay bài làm
      el.querySelectorAll('.inbox-item').forEach((row) => {
        row.addEventListener('click', () => {
          const item = list[+row.dataset.rowIdx];
          if (item) openStudentDetailModal(item);
        });
      });
    });
  }

  // Kênh nhận bài trực tuyến cho trang Giáo viên
  async function syncCloudSubmissions(showNotice = false) {
    if (IS_STUDENT_PAGE) return;
    try {
      const res = await fetch(`${CLOUD_BASE}/json?poll=1&since=all`, { cache: 'no-store' });
      const text = await res.text();
      const lines = text.trim().split('\n').filter(Boolean);
      let added = 0;
      for (const line of lines) {
        try {
          const ev = JSON.parse(line);
          if (ev.event === 'message' && ev.message) {
            const payload = JSON.parse(ev.message);
            if (payload && payload.n && saveToInbox(payload, false)) {
              added++;
            }
          }
        } catch {
          /* bỏ qua dòng lỗi */
        }
      }
      if (added > 0) {
        Sound.play('correct');
        showToast(`📥 Đã nhận thêm ${added} bài nộp mới từ Học sinh!`);
      } else if (showNotice) {
        showToast('✔ Danh sách bài nộp đã được cập nhật mới nhất');
      }
    } catch {
      if (showNotice) showToast('⚠️ Không thể kết nối máy chủ đồng bộ');
    }
  }

  if (!IS_STUDENT_PAGE) {
    updateInboxUI();
    syncCloudSubmissions(false);

    // Lắng nghe SSE thời gian thực (< 0.5 giây khi HS bấm nộp)
    if (typeof EventSource !== 'undefined') {
      try {
        const es = new EventSource(`${CLOUD_BASE}/sse`);
        es.onmessage = (e) => {
          try {
            const ev = JSON.parse(e.data);
            if (ev.event === 'message' && ev.message) {
              const payload = JSON.parse(ev.message);
              saveToInbox(payload, true);
            }
          } catch {
            /* bỏ qua */
          }
        };
      } catch {
        /* fallback qua bộ đếm định kỳ */
      }
    }
    setInterval(() => syncCloudSubmissions(false), 7000);
  }

  if (bc) {
    bc.onmessage = (ev) => {
      if (ev.data && ev.data.type === 'ws-submit') {
        saveToInbox(ev.data.payload, true);
      }
    };
  }

  const btnLiveRefresh = document.getElementById('btn-live-refresh');
  if (btnLiveRefresh) {
    btnLiveRefresh.addEventListener('click', () => syncCloudSubmissions(true));
  }

  ['btn-inbox-open', 'btn-inbox-open-2'].forEach((id) => {
    const b = document.getElementById(id);
    if (b) {
      b.addEventListener('click', () => {
        updateInboxUI();
        document.getElementById('inbox-modal').classList.remove('hidden');
        Sound.play('pop');
      });
    }
  });

  const btnInboxImport = document.getElementById('btn-inbox-import');
  if (btnInboxImport) {
    btnInboxImport.addEventListener('click', () => {
      const inp = document.getElementById('inbox-import-input');
      const raw = inp ? inp.value.trim() : '';
      if (!raw || (/^https?:\/\//i.test(raw) && !raw.includes('code='))) {
        if (inp) inp.value = '';
        syncCloudSubmissions(true);
        return;
      }
      try {
        const code = raw.includes('code=') ? decodeURIComponent(raw.split('code=')[1].split('&')[0]) : raw;
        const json = decodeURIComponent(escape(atob(code)));
        const data = JSON.parse(json);
        saveToInbox(data, false);
        if (inp) inp.value = '';
        Sound.play('correct');
        showToast(`✔ Đã nhập bài của ${data.n} (${data.c})!`);
        openStudentDetailModal(data);
      } catch (e) {
        Sound.play('wrong');
        showToast('⚠️ Mã bài nộp không hợp lệ');
      }
    });
    document.getElementById('btn-inbox-clear').addEventListener('click', () => {
      if (!confirm('Xoá danh sách bài nộp lưu trên trình duyệt này?')) return;
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

      // Chấm ngầm để gửi điểm cho Giáo viên (nhưng KHÔNG hiển thị đúng/sai trên màn hình Học sinh)
      const g = gradeWorksheet(!IS_STUDENT_PAGE);
      if (!IS_STUDENT_PAGE && result) {
        result.className = 'result ' + (g.ok === g.total ? 'ok' : 'bad');
        result.textContent = `Đã chấm: ${g.ok}/${g.total} câu đúng.`;
      } else if (result) {
        result.className = 'result ok';
        result.textContent = '✔ Đã nộp bài cho Giáo viên!';
      }

      const nowStr = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      const noteText = document.getElementById('ws-note').value.trim();

      // Vẽ ảnh phiếu (bên Học sinh không hiện điểm/đáp án; bên Giáo viên hiện đầy đủ)
      lastRenderedCanvas = renderWorksheetImage(
        {
          n: name,
          c: cls,
          t: nowStr,
          note: noteText,
          gradeInfo: g,
        },
        { showGrade: !IS_STUDENT_PAGE }
      );

      const safeName = name.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]+/g, '_');
      const safeCls = cls.replace(/[^a-zA-Z0-9]+/g, '_');
      lastFileName = `PhieuHocTap_Bai8_${safeName}_${safeCls}.png`;

      const dataUrl = lastRenderedCanvas.toDataURL('image/png');
      document.getElementById('sub-preview-img').src = dataUrl;
      document.getElementById('sub-title').textContent = IS_STUDENT_PAGE
        ? `🎉 Đã nộp Phiếu học tập của ${name} (${cls})!`
        : `🎉 Đã hoàn thành phiếu của ${name} (${cls}) – ${g.ok}/${g.total} câu đúng!`;

      // Đóng gói toàn bộ dữ liệu bài làm (gồm cả 12 câu trả lời + nét vẽ 2 thấu kính) để gửi về trang Giáo viên
      const payload = {
        id: `sub_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        n: name,
        c: cls,
        s: `${g.ok}/${g.total}`,
        t: nowStr,
        vals: g.vals,
        note: noteText.slice(0, 220),
        drw: {
          ht: compactStrokes(pads[0]?.strokes),
          pk: compactStrokes(pads[1]?.strokes),
        },
      };

      const codeStr = btoa(unescape(encodeURIComponent(JSON.stringify(payload))));
      document.getElementById('sub-code-text').value = codeStr;

      const cvResQr = document.getElementById('cv-qr-result');
      if (cvResQr && typeof QR !== 'undefined') {
        try {
          QR.render(cvResQr, `${name} (${cls}) - Ma: ${payload.id}`, { size: 160 });
        } catch {
          /* bỏ qua */
        }
      }

      // Lưu cục bộ & bắn qua BroadcastChannel (nếu cùng máy)
      if (!IS_STUDENT_PAGE) saveToInbox(payload, false);
      if (bc) bc.postMessage({ type: 'ws-submit', payload });

      document.getElementById('submit-modal').classList.remove('hidden');
      Sound.play('correct');

      // Gửi trực tuyến lên kênh Cloud để máy Giáo viên nhận ngay lập tức
      const badgeStatus = document.getElementById('sub-badge-status');
      const liveStatus = document.getElementById('sub-live-status');
      try {
        if (badgeStatus) badgeStatus.textContent = '📡 Đang đồng bộ bài làm về máy Giáo viên...';
        await fetch(CLOUD_BASE, {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain; charset=utf-8' },
          body: JSON.stringify(payload),
        });
        if (badgeStatus) badgeStatus.textContent = '✅ Giáo viên đã nhận được bài của em!';
        if (liveStatus) {
          liveStatus.innerHTML =
            '<div class="sub-status-icon">✅</div><div class="sub-status-text">Đã gửi bài làm trực tuyến về trang của Giáo viên thành công!</div>';
        }
        showToast('✅ Đã gửi bài nộp tới Giáo viên thành công!');
      } catch {
        if (badgeStatus) badgeStatus.textContent = '⚠️ Chế độ ngoại tuyến';
        if (liveStatus) {
          liveStatus.innerHTML =
            '<div class="sub-status-icon">⚠️</div><div class="sub-status-text">Mạng yếu – em hãy bấm "Tải ảnh Phiếu" hoặc chép Mã bài nộp gửi cho Giáo viên nhé.</div>';
        }
      }

      // Hỗ trợ thêm Webhook riêng nếu GV cấu hình
      const params = new URLSearchParams(window.location.search);
      const submitTarget = params.get('submit') || localStorage.getItem('natural-qr-submit') || '';
      const extBtn = document.getElementById('btn-sub-ext-link');
      const statusEl = document.getElementById('sub-webhook-status');
      if (statusEl) statusEl.textContent = '';

      if (submitTarget) {
        extBtn.style.display = '';
        extBtn.onclick = () => window.open(submitTarget, '_blank');
        if (submitTarget.includes('script.google.com') || submitTarget.includes('webhook')) {
          try {
            await fetch(submitTarget, {
              method: 'POST',
              mode: 'no-cors',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload),
            });
          } catch {
            /* bỏ qua */
          }
        }
      } else if (extBtn) {
        extBtn.style.display = 'none';
      }
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

  // Nút chia sẻ nhanh trên điện thoại
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
            /* huỷ chia sẻ */
          }
        }
        const a = document.createElement('a');
        a.download = lastFileName;
        a.href = URL.createObjectURL(blob);
        a.click();
        showToast('⬇ Đã tải ảnh phiếu về máy!');
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
    if (result) result.textContent = '';
    Sound.play('pop');
  });
})();
