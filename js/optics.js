/* =========================================================
   Công cụ quang học dùng chung: hệ toạ độ, vẽ thấu kính, tia sáng
   Hệ toạ độ thế giới (cm): x hướng phải, y hướng lên, quang tâm O ở (0,0)
   Thấu kính mỏng: tia tới độ dốc m, gặp thấu kính ở độ cao y  ->  tia ló m' = m - y/f
   (f > 0: hội tụ, f < 0: phân kì)
   ========================================================= */

class LensView {
  constructor(canvas, worldWidth) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.worldWidth = worldWidth;
    this.resize();
  }
  resize() {
    const r = this.canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.w = Math.max(r.width, 10);
    this.h = Math.max(r.height, 10);
    this.canvas.width = Math.round(this.w * dpr);
    this.canvas.height = Math.round(this.h * dpr);
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this.s = this.w / this.worldWidth;
    this.cx = this.w / 2;
    this.cy = this.h / 2;
  }
  X(x) { return this.cx + x * this.s; }
  Y(y) { return this.cy - y * this.s; }
  wx(px) { return (px - this.cx) / this.s; }
  wy(py) { return (this.cy - py) / this.s; }
  get xmin() { return -this.worldWidth / 2; }
  get xmax() { return this.worldWidth / 2; }
  get ymax() { return this.h / 2 / this.s; }
  pointer(e) {
    const r = this.canvas.getBoundingClientRect();
    const px = e.clientX - r.left, py = e.clientY - r.top;
    return { px, py, x: this.wx(px), y: this.wy(py) };
  }
}

function getPalette() {
  const s = getComputedStyle(document.documentElement);
  const g = (n) => s.getPropertyValue(n).trim();
  return {
    bg: g('--cv-bg'), grid: g('--cv-grid'), axis: g('--cv-axis'), text: g('--cv-text'),
    lensFill: g('--cv-lens-fill'), lensStroke: g('--cv-lens-stroke'), focus: g('--cv-focus'),
    obj: g('--cv-obj'), img: g('--cv-img'),
    rayO: g('--ray-o'), rayP: g('--ray-p'), rayF: g('--ray-f'),
    glow: g('--cv-glow') === '1',
  };
}

const PAPER_PALETTE = {
  bg: '#ffffff', grid: '#eef2f7', axis: '#33475b', text: '#1d3047',
  lensFill: 'rgba(80,160,230,.18)', lensStroke: '#2b7bbd', focus: '#d63a3f',
  obj: '#15803d', img: '#8e24aa', rayO: '#e53935', rayP: '#f08c00', rayF: '#1e6fd9', glow: false,
};

const Draw = {
  background(v, p, gridStep = 5) {
    const c = v.ctx;
    c.save();
    c.fillStyle = p.bg;
    c.fillRect(0, 0, v.w, v.h);
    if (gridStep) {
      c.strokeStyle = p.grid;
      c.lineWidth = 1;
      c.beginPath();
      for (let x = 0; x <= v.xmax; x += gridStep) {
        [x, -x].forEach((xx) => { c.moveTo(v.X(xx), 0); c.lineTo(v.X(xx), v.h); });
      }
      for (let y = 0; y <= v.ymax; y += gridStep) {
        [y, -y].forEach((yy) => { c.moveTo(0, v.Y(yy)); c.lineTo(v.w, v.Y(yy)); });
      }
      c.stroke();
    }
    c.restore();
  },

  axis(v, p, label = true) {
    const c = v.ctx;
    c.save();
    c.strokeStyle = p.axis;
    c.lineWidth = 1.4;
    c.setLineDash([8, 5]);
    c.beginPath();
    c.moveTo(0, v.Y(0));
    c.lineTo(v.w, v.Y(0));
    c.stroke();
    c.setLineDash([]);
    if (label) {
      c.fillStyle = p.text;
      c.font = '600 12px "Be Vietnam Pro", sans-serif';
      c.textAlign = 'left';
      c.fillText('Trục chính', 8, v.Y(0) - 8);
    }
    c.restore();
  },

  lens(v, p, type, half, opts = {}) {
    const c = v.ctx;
    const x0 = v.X(0), yt = v.Y(half), yb = v.Y(-half);
    const b = Math.min(half * v.s * 0.16, 26);
    c.save();
    if (opts.shape !== false) {
      c.beginPath();
      if (type === 'ht') {
        c.moveTo(x0, yt);
        c.quadraticCurveTo(x0 + b * 2, v.Y(0), x0, yb);
        c.quadraticCurveTo(x0 - b * 2, v.Y(0), x0, yt);
      } else {
        const e = b * 0.9;
        c.moveTo(x0 - e, yt);
        c.lineTo(x0 + e, yt);
        c.quadraticCurveTo(x0 - e * 0.15, v.Y(0), x0 + e, yb);
        c.lineTo(x0 - e, yb);
        c.quadraticCurveTo(x0 + e * 0.15, v.Y(0), x0 - e, yt);
      }
      c.closePath();
      c.fillStyle = p.lensFill;
      c.fill();
      c.strokeStyle = p.lensStroke;
      c.globalAlpha = 0.55;
      c.lineWidth = 1.5;
      c.stroke();
      c.globalAlpha = 1;
    }
    // Kí hiệu thấu kính
    c.strokeStyle = p.lensStroke;
    c.lineWidth = 2.4;
    c.lineCap = 'round';
    c.beginPath();
    c.moveTo(x0, yt);
    c.lineTo(x0, yb);
    const a = 9;
    if (type === 'ht') {
      c.moveTo(x0 - a, yt + a); c.lineTo(x0, yt); c.lineTo(x0 + a, yt + a);
      c.moveTo(x0 - a, yb - a); c.lineTo(x0, yb); c.lineTo(x0 + a, yb - a);
    } else {
      c.moveTo(x0 - a, yt - a * 0.2); c.lineTo(x0, yt + a * 0.8); c.lineTo(x0 + a, yt - a * 0.2);
      c.moveTo(x0 - a, yb + a * 0.2); c.lineTo(x0, yb - a * 0.8); c.lineTo(x0 + a, yb + a * 0.2);
    }
    c.stroke();
    c.restore();
  },

  foci(v, p, f, typeOrShow2f = 'ht', maybeShow2f = false) {
    const c = v.ctx;
    c.save();
    c.font = '700 14px "Be Vietnam Pro", sans-serif';
    c.textAlign = 'center';

    let type = 'ht';
    let show2f = false;
    if (typeof typeOrShow2f === 'boolean') {
      show2f = typeOrShow2f;
      type = typeof maybeShow2f === 'string' ? maybeShow2f : 'ht';
    } else if (typeof typeOrShow2f === 'string') {
      type = typeOrShow2f;
      show2f = Boolean(maybeShow2f);
    } else if (typeOrShow2f && typeof typeOrShow2f === 'object') {
      type = typeOrShow2f.type || 'ht';
      show2f = Boolean(typeOrShow2f.show2f);
    }

    // ĐỐI VỚI THẤU KÍNH HỘI TỤ (TKHT):
    // Tiêu điểm vật chính F ở phía trước (bên trái, x = -f)
    // Tiêu điểm ảnh chính F' ở phía sau (bên phải, x = +f)
    //
    // ĐỐI VỚI THẤU KÍNH PHÂN KÌ (TKPK):
    // Tiêu điểm ảnh chính F' ở phía trước (bên trái, x = -f)
    // Tiêu điểm vật chính F ở phía sau (bên phải, x = +f)
    const isPK = type === 'pk';
    const leftLabel = isPK ? "F'" : "F";
    const rightLabel = isPK ? "F" : "F'";
    const pts = [[-f, leftLabel], [f, rightLabel]];
    if (show2f) {
      const left2Label = isPK ? "2F'" : "2F";
      const right2Label = isPK ? "2F" : "2F'";
      pts.push([-2 * f, left2Label], [2 * f, right2Label]);
    }
    pts.forEach(([x, lb]) => {
      const big = !lb.startsWith('2');
      c.fillStyle = big ? p.focus : p.axis;
      c.beginPath();
      c.arc(v.X(x), v.Y(0), big ? 4.5 : 3, 0, Math.PI * 2);
      c.fill();
      c.fillStyle = big ? p.focus : p.text;
      c.fillText(lb, v.X(x), v.Y(0) + 20);
    });
    c.fillStyle = p.text;
    c.fillText('O', v.X(0) + 11, v.Y(0) + 18);
    c.beginPath();
    c.arc(v.X(0), v.Y(0), 3, 0, Math.PI * 2);
    c.fill();
    c.restore();
  },

  arrowHead(c, x, y, ang, size, color) {
    c.save();
    c.fillStyle = color;
    c.translate(x, y);
    c.rotate(ang);
    c.beginPath();
    c.moveTo(size, 0);
    c.lineTo(-size * 0.7, size * 0.6);
    c.lineTo(-size * 0.7, -size * 0.6);
    c.closePath();
    c.fill();
    c.restore();
  },

  // Vật / ảnh dạng mũi tên vuông góc trục chính
  arrowObj(v, p, x, h, color, opts = {}) {
    const c = v.ctx;
    const X = v.X(x), Y0 = v.Y(0), Y1 = v.Y(h);
    c.save();
    c.strokeStyle = color;
    c.lineWidth = opts.width || 3.2;
    if (opts.dashed) c.setLineDash([6, 4]);
    c.beginPath();
    c.moveTo(X, Y0);
    c.lineTo(X, Y1 + (h > 0 ? 8 : -8));
    c.stroke();
    c.setLineDash([]);
    Draw.arrowHead(c, X, Y1, h > 0 ? -Math.PI / 2 : Math.PI / 2, 11, color);
    c.fillStyle = color;
    c.font = '700 14px "Be Vietnam Pro", sans-serif';
    c.textAlign = 'center';
    if (opts.base) c.fillText(opts.base, X, Y0 + (h > 0 ? 18 : -10));
    if (opts.tip) c.fillText(opts.tip, X + 12, Y1 + (h > 0 ? -6 : 16));
    c.restore();
  },

  /**
   * Vẽ danh sách đoạn tia sáng với hiệu ứng lan truyền.
   * segs: [{x1,y1,x2,y2,dashed}] theo thứ tự lan truyền; progress tính theo px.
   * Trả về tổng chiều dài (px) của các đoạn liền (không tính nét đứt).
   */
  rayPath(v, p, segs, color, progress = Infinity) {
    const c = v.ctx;
    let used = 0;
    let total = 0;
    c.save();
    c.lineCap = 'round';
    c.strokeStyle = color;
    if (p.glow) { c.shadowColor = color; c.shadowBlur = 12; }
    segs.forEach((s) => {
      const X1 = v.X(s.x1), Y1 = v.Y(s.y1), X2 = v.X(s.x2), Y2 = v.Y(s.y2);
      const L = Math.hypot(X2 - X1, Y2 - Y1);
      if (!s.dashed) total += L;
      if (s.dashed) {
        if (progress < used) return;
        c.save();
        c.shadowBlur = 0;
        c.globalAlpha = 0.85;
        c.lineWidth = 1.6;
        c.setLineDash([7, 6]);
        c.beginPath();
        c.moveTo(X1, Y1);
        c.lineTo(X2, Y2);
        c.stroke();
        c.restore();
        return;
      }
      const remain = progress - used;
      if (remain <= 0) { used += L; return; }
      const k = Math.min(1, remain / L);
      const XE = X1 + (X2 - X1) * k, YE = Y1 + (Y2 - Y1) * k;
      c.lineWidth = 2.6;
      c.beginPath();
      c.moveTo(X1, Y1);
      c.lineTo(XE, YE);
      c.stroke();
      // mũi tên chỉ hướng truyền
      const am = Math.min(0.5, 120 / Math.max(L, 1));
      if (k > am + 0.02 && L > 40) {
        const ang = Math.atan2(Y2 - Y1, X2 - X1);
        Draw.arrowHead(c, X1 + (X2 - X1) * am, Y1 + (Y2 - Y1) * am, ang, 8, color);
      }
      used += L;
    });
    c.restore();
    return total;
  },

  label(v, p, text, x, y, color, align = 'center') {
    const c = v.ctx;
    c.save();
    c.fillStyle = color || p.text;
    c.font = '700 13px "Be Vietnam Pro", sans-serif';
    c.textAlign = align;
    c.fillText(text, v.X(x), v.Y(y));
    c.restore();
  },
};

/** Truy vết một tia: từ điểm (x0,y0) với độ dốc m đến thấu kính, rồi ló ra đến xEnd. */
function traceRay(x0, y0, m, f, xEnd) {
  const yh = y0 - m * x0;      // độ cao điểm tới trên thấu kính
  const m2 = m - yh / f;       // độ dốc tia ló
  return {
    yh, m2,
    segs: [
      { x1: x0, y1: y0, x2: 0, y2: yh },
      { x1: 0, y1: yh, x2: xEnd, y2: yh + m2 * xEnd },
    ],
  };
}

/** Hoạt ảnh tiến trình 0 -> 1 */
function animate(duration, onFrame, onDone) {
  const t0 = performance.now();
  let id;
  const step = (t) => {
    const k = Math.min(1, (t - t0) / duration);
    onFrame(k);
    if (k < 1) id = requestAnimationFrame(step);
    else if (onDone) onDone();
  };
  id = requestAnimationFrame(step);
  return () => cancelAnimationFrame(id);
}

/** Tiện ích: tự vẽ lại khi kích thước / chủ đề thay đổi */
function autoRedraw(view, draw) {
  const ro = new ResizeObserver(() => { view.resize(); draw(); });
  ro.observe(view.canvas);
  document.addEventListener('themechange', draw);
}
