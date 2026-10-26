/* =========================================================
   Âm thanh – tạo bằng Web Audio API (không cần file âm thanh)
   ========================================================= */
const Sound = (() => {
  let ctx = null;
  let sfx = localStorage.getItem('natural-sfx') !== 'off';
  let music = false;
  let musicTimer = null;
  let musicBus = null;
  let lastDrag = 0;

  function ac() {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }

  function tone(freq, dur, opt = {}) {
    const { type = 'sine', vol = 0.12, when = 0, slideTo = null, dest = null } = opt;
    const c = ac();
    const t = c.currentTime + when;
    const o = c.createOscillator();
    const g = c.createGain();
    o.type = type;
    o.frequency.setValueAtTime(freq, t);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t + dur);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol, t + 0.015);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g).connect(dest || c.destination);
    o.start(t);
    o.stop(t + dur + 0.05);
  }

  const fx = {
    click() { tone(660, 0.07, { type: 'triangle', vol: 0.07 }); },
    toggle() { tone(520, 0.06, { vol: 0.07 }); tone(780, 0.08, { vol: 0.07, when: 0.05 }); },
    ray() { tone(320, 0.6, { vol: 0.06, slideTo: 1300 }); tone(640, 0.6, { type: 'triangle', vol: 0.03, slideTo: 2000, when: 0.05 }); },
    correct() { [523.25, 659.25, 783.99, 1046.5].forEach((f, i) => tone(f, 0.22, { type: 'triangle', vol: 0.09, when: i * 0.08 })); },
    wrong() { tone(240, 0.28, { type: 'sawtooth', vol: 0.05, slideTo: 140 }); },
    drag() {
      const now = performance.now();
      if (now - lastDrag < 70) return;
      lastDrag = now;
      tone(880 + Math.random() * 200, 0.03, { vol: 0.02 });
    },
    pop() { tone(400, 0.1, { vol: 0.06, slideTo: 800 }); },
  };

  function play(name) {
    if (!sfx || !unlocked || !fx[name]) return;
    try { fx[name](); } catch (e) { /* bỏ qua */ }
  }

  // Trình duyệt chỉ cho phát âm thanh sau thao tác đầu tiên của người dùng
  let unlocked = false;
  const unlock = () => { unlocked = true; };
  ['pointerdown', 'keydown', 'touchstart'].forEach((ev) => window.addEventListener(ev, unlock, { once: true, capture: true }));

  function startMusic() {
    const c = ac();
    musicBus = c.createGain();
    musicBus.gain.value = 0.55;
    musicBus.connect(c.destination);
    // Vòng hợp âm nhẹ nhàng: C – Am – F – G
    const chords = [
      [261.63, 329.63, 392.0],
      [220.0, 261.63, 329.63],
      [174.61, 220.0, 261.63],
      [196.0, 246.94, 293.66],
    ];
    const pattern = [0, 1, 2, 1, 0, 2, 1, 2];
    let step = 0;
    const tick = () => {
      const ch = chords[Math.floor(step / 8) % chords.length];
      const n = ch[pattern[step % 8]] * (step % 8 >= 4 ? 2 : 1);
      tone(n, 1.0, { vol: 0.03, dest: musicBus });
      if (step % 8 === 0) ch.forEach((f) => tone(f / 2, 3.4, { vol: 0.018, dest: musicBus }));
      step++;
    };
    tick();
    musicTimer = setInterval(tick, 420);
  }

  function stopMusic() {
    clearInterval(musicTimer);
    musicTimer = null;
    if (musicBus && ctx) {
      const bus = musicBus;
      bus.gain.setTargetAtTime(0, ctx.currentTime, 0.12);
      setTimeout(() => bus.disconnect(), 800);
      musicBus = null;
    }
  }

  return {
    play,
    get sfx() { return sfx; },
    setSfx(v) { sfx = v; localStorage.setItem('natural-sfx', v ? 'on' : 'off'); },
    get music() { return music; },
    setMusic(v) { music = v; if (v) startMusic(); else stopMusic(); },
  };
})();
