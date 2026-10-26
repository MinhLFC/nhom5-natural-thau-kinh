/* =========================================================
   Trình tạo Mã QR độc lập (ISO/IEC 18004 – Byte Mode UTF-8, EC Level L)
   Hoạt động 100% offline, hỗ trợ vẽ lên Canvas và tải ảnh PNG
   ========================================================= */
const QR = (() => {
  // Bảng thông số Version 1..14 (Error Correction Level L): [totalCodewords, ecCodewordsPerBlock, numBlocks1, dataPerBlock1, numBlocks2, dataPerBlock2]
  const V_INFO = [
    null,
    [26, 7, 1, 19, 0, 0],
    [44, 10, 1, 34, 0, 0],
    [70, 15, 1, 55, 0, 0],
    [100, 20, 1, 80, 0, 0],
    [134, 26, 1, 108, 0, 0],
    [172, 18, 2, 68, 0, 0],
    [196, 20, 2, 78, 0, 0],
    [242, 24, 2, 97, 0, 0],
    [292, 30, 2, 116, 0, 0],
    [346, 18, 2, 68, 2, 69],
    [404, 20, 4, 81, 0, 0],
    [466, 24, 2, 92, 2, 93],
    [532, 26, 4, 107, 0, 0],
    [581, 30, 3, 115, 1, 116],
  ];

  const ALIGN_POS = [
    null, [], [6, 18], [6, 22], [6, 26], [6, 30], [6, 34],
    [6, 22, 38], [6, 24, 42], [6, 26, 46], [6, 28, 50],
    [6, 30, 54], [6, 32, 58], [6, 34, 62], [6, 26, 46, 66],
  ];

  // GF(256) cho Reed-Solomon
  const EXP = new Uint8Array(512);
  const LOG = new Uint8Array(256);
  (() => {
    let x = 1;
    for (let i = 0; i < 255; i++) {
      EXP[i] = x;
      LOG[x] = i;
      x <<= 1;
      if (x & 0x100) x ^= 0x11d;
    }
    for (let i = 255; i < 512; i++) EXP[i] = EXP[i - 255];
  })();

  function gfMul(a, b) {
    return a === 0 || b === 0 ? 0 : EXP[LOG[a] + LOG[b]];
  }

  function rsGeneratorPoly(deg) {
    let poly = [1];
    for (let i = 0; i < deg; i++) {
      const next = new Array(poly.length + 1).fill(0);
      const root = EXP[i];
      for (let j = 0; j < poly.length; j++) {
        next[j] ^= poly[j];
        next[j + 1] ^= gfMul(poly[j], root);
      }
      poly = next;
    }
    return poly;
  }

  function rsEncode(data, ecLen) {
    const gen = rsGeneratorPoly(ecLen);
    const res = new Uint8Array(ecLen);
    for (let i = 0; i < data.length; i++) {
      const factor = data[i] ^ res[0];
      res.copyWithin(0, 1);
      res[ecLen - 1] = 0;
      for (let j = 0; j < ecLen; j++) {
        res[j] ^= gfMul(gen[j + 1], factor);
      }
    }
    return res;
  }

  function pickVersion(byteLen) {
    for (let v = 1; v < V_INFO.length; v++) {
      const [, , b1, d1, b2, d2] = V_INFO[v];
      const cap = b1 * d1 + b2 * d2;
      const hdrBits = 4 + (v <= 9 ? 8 : 16);
      if (Math.ceil((hdrBits + byteLen * 8) / 8) <= cap) return v;
    }
    throw new Error('Nội dung QR quá dài');
  }

  function buildDataCodewords(bytes, v) {
    const [, ecLen, b1, d1, b2, d2] = V_INFO[v];
    const totalData = b1 * d1 + b2 * d2;
    const bits = [];
    const pushBits = (val, n) => {
      for (let i = n - 1; i >= 0; i--) bits.push((val >>> i) & 1);
    };
    pushBits(0b0100, 4); // Byte mode
    pushBits(bytes.length, v <= 9 ? 8 : 16);
    for (const b of bytes) pushBits(b, 8);
    const maxBits = totalData * 8;
    for (let i = 0; i < 4 && bits.length < maxBits; i++) bits.push(0);
    while (bits.length % 8 !== 0) bits.push(0);
    const cw = [];
    for (let i = 0; i < bits.length; i += 8) {
      let byte = 0;
      for (let j = 0; j < 8; j++) byte = (byte << 1) | bits[i + j];
      cw.push(byte);
    }
    const pads = [0xec, 0x11];
    let p = 0;
    while (cw.length < totalData) cw.push(pads[p++ % 2]);

    // Chia block & tính EC
    const dataBlocks = [];
    const ecBlocks = [];
    let offset = 0;
    for (let i = 0; i < b1; i++) {
      const blk = cw.slice(offset, offset + d1);
      offset += d1;
      dataBlocks.push(blk);
      ecBlocks.push(rsEncode(blk, ecLen));
    }
    for (let i = 0; i < b2; i++) {
      const blk = cw.slice(offset, offset + d2);
      offset += d2;
      dataBlocks.push(blk);
      ecBlocks.push(rsEncode(blk, ecLen));
    }

    const out = [];
    const maxD = Math.max(d1, d2);
    for (let i = 0; i < maxD; i++) {
      for (const blk of dataBlocks) if (i < blk.length) out.push(blk[i]);
    }
    for (let i = 0; i < ecLen; i++) {
      for (const blk of ecBlocks) out.push(blk[i]);
    }
    return out;
  }

  function makeMatrix(text) {
    const bytes = new TextEncoder().encode(text);
    const v = pickVersion(bytes.length);
    const size = v * 4 + 17;
    const mat = Array.from({ length: size }, () => new Int8Array(size)); // 0/1
    const isFunc = Array.from({ length: size }, () => new Uint8Array(size));

    const setFunc = (r, c, val) => {
      if (r < 0 || c < 0 || r >= size || c >= size) return;
      mat[r][c] = val ? 1 : 0;
      isFunc[r][c] = 1;
    };

    const drawFinder = (r0, c0) => {
      for (let dr = -1; dr <= 7; dr++) {
        for (let dc = -1; dc <= 7; dc++) {
          const on =
            dr >= 0 && dr <= 6 && dc >= 0 && dc <= 6 &&
            (dr === 0 || dr === 6 || dc === 0 || dc === 6 || (dr >= 2 && dr <= 4 && dc >= 2 && dc <= 4));
          setFunc(r0 + dr, c0 + dc, on);
        }
      }
    };
    drawFinder(0, 0);
    drawFinder(0, size - 7);
    drawFinder(size - 7, 0);

    // Timing
    for (let i = 8; i < size - 8; i++) {
      setFunc(6, i, i % 2 === 0);
      setFunc(i, 6, i % 2 === 0);
    }

    // Alignment
    const apos = ALIGN_POS[v];
    for (const r of apos) {
      for (const c of apos) {
        if ((r === 6 && c === 6) || (r === 6 && c === size - 7) || (r === size - 7 && c === 6)) continue;
        for (let dr = -2; dr <= 2; dr++) {
          for (let dc = -2; dc <= 2; dc++) {
            setFunc(r + dr, c + dc, Math.max(Math.abs(dr), Math.abs(dc)) !== 1);
          }
        }
      }
    }

    // Reserve format areas + dark module
    for (let i = 0; i <= 8; i++) {
      if (!isFunc[8][i]) setFunc(8, i, 0);
      if (!isFunc[i][8]) setFunc(i, 8, 0);
      if (i < 8) {
        if (!isFunc[8][size - 1 - i]) setFunc(8, size - 1 - i, 0);
        if (!isFunc[size - 1 - i][8]) setFunc(size - 1 - i, 8, 0);
      }
    }
    setFunc(size - 8, 8, 1);

    // Version info for v >= 7
    if (v >= 7) {
      let rem = v;
      for (let i = 0; i < 12; i++) rem = (rem << 1) ^ ((rem >>> 11) * 0x1f25);
      const vBits = (v << 12) | rem;
      for (let i = 0; i < 18; i++) {
        const bit = (vBits >>> i) & 1;
        const a = size - 11 + (i % 3), b = Math.floor(i / 3);
        setFunc(a, b, bit);
        setFunc(b, a, bit);
      }
    }

    // Đặt bit dữ liệu
    const codewords = buildDataCodewords(bytes, v);
    let bitIdx = 0;
    const totalBits = codewords.length * 8;
    let upward = true;
    for (let right = size - 1; right >= 1; right -= 2) {
      if (right === 6) right = 5;
      for (let vert = 0; vert < size; vert++) {
        const r = upward ? size - 1 - vert : vert;
        for (let j = 0; j < 2; j++) {
          const c = right - j;
          if (!isFunc[r][c]) {
            let bit = 0;
            if (bitIdx < totalBits) {
              bit = (codewords[bitIdx >>> 3] >>> (7 - (bitIdx & 7))) & 1;
              bitIdx++;
            }
            mat[r][c] = bit;
          }
        }
      }
      upward = !upward;
    }

    // Mask 0: (r + c) % 2 === 0, Format bits cho Level L (01) + Mask 0 (000)
    const mask = 0;
    for (let r = 0; r < size; r++) {
      for (let c = 0; c < size; c++) {
        if (!isFunc[r][c] && (r + c) % 2 === 0) mat[r][c] ^= 1;
      }
    }

    // Format info: EC L = 01, mask = 000 -> data = 0b01000
    const fmtData = (0b01 << 3) | mask;
    let rem = fmtData;
    for (let i = 0; i < 10; i++) rem = (rem << 1) ^ ((rem >>> 9) * 0x537);
    const fmtBits = ((fmtData << 10) | rem) ^ 0x5412;
    const bitAt = (i) => (fmtBits >>> i) & 1;

    // Cột 8 từ trên xuống (bit 0..7)
    for (let i = 0; i <= 5; i++) mat[i][8] = bitAt(i);
    mat[7][8] = bitAt(6);
    mat[8][8] = bitAt(7);
    // Hàng 8 từ phải qua trái ở góc trên-trái (bit 8..14)
    mat[8][7] = bitAt(8);
    for (let i = 9; i < 15; i++) mat[8][14 - i] = bitAt(i);

    // Hàng 8 góc trên-phải (bit 0..7) và cột 8 góc dưới-trái (bit 8..14)
    for (let i = 0; i < 8; i++) mat[8][size - 1 - i] = bitAt(i);
    for (let i = 8; i < 15; i++) mat[size - 15 + i][8] = bitAt(i);

    return mat;
  }

  function render(canvas, text, opts = {}) {
    const {
      size = 220,
      margin = 3,
      dark = '#0d4a7a',
      light = '#ffffff',
      accent = '#d63a3f',
    } = opts;
    const mat = makeMatrix(text || 'https://hcmue.edu.vn');
    const n = mat.length;
    const total = n + margin * 2;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    canvas.style.width = size + 'px';
    canvas.style.height = size + 'px';
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const cell = size / total;
    ctx.fillStyle = light;
    ctx.fillRect(0, 0, size, size);

    const isFinderCenter = (r, c) =>
      (r >= 2 && r <= 4 && c >= 2 && c <= 4) ||
      (r >= 2 && r <= 4 && c >= n - 5 && c <= n - 3) ||
      (r >= n - 5 && r <= n - 3 && c >= 2 && c <= 4);

    for (let r = 0; r < n; r++) {
      for (let c = 0; c < n; c++) {
        if (!mat[r][c]) continue;
        ctx.fillStyle = isFinderCenter(r, c) ? accent : dark;
        const x = (c + margin) * cell;
        const y = (r + margin) * cell;
        ctx.fillRect(x, y, Math.ceil(cell), Math.ceil(cell));
      }
    }
    return canvas;
  }

  return { render, makeMatrix };
})();
