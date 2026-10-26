/* =========================================================
   Điều khiển chung: Chuyển trang theo Tab (Menu), Sáng/Tối, Âm thanh
   ========================================================= */
function showToast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => t.classList.remove('show'), 2600);
}

(function () {
  const root = document.documentElement;

  // ---------- Sáng / tối ----------
  const btnTheme = document.getElementById('btn-theme');
  if (btnTheme) {
    btnTheme.addEventListener('click', () => {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem('natural-theme', next);
      Sound.play('toggle');
      showToast(next === 'dark' ? '🌙 Đã bật chế độ tối' : '☀️ Đã bật chế độ sáng');
      requestAnimationFrame(() => document.dispatchEvent(new Event('themechange')));
    });
  }

  // ---------- Âm thanh ----------
  const btnSfx = document.getElementById('btn-sfx');
  const btnMusic = document.getElementById('btn-music');
  if (btnSfx) {
    const syncSfx = () => btnSfx.classList.toggle('muted', !Sound.sfx);
    syncSfx();
    btnSfx.addEventListener('click', () => {
      Sound.setSfx(!Sound.sfx);
      syncSfx();
      Sound.play('toggle');
      showToast(Sound.sfx ? '🔊 Đã bật hiệu ứng âm thanh' : '🔇 Đã tắt hiệu ứng âm thanh');
    });
  }
  if (btnMusic) {
    btnMusic.addEventListener('click', () => {
      Sound.setMusic(!Sound.music);
      btnMusic.classList.toggle('on', Sound.music);
      showToast(Sound.music ? '🎵 Đã bật nhạc nền' : '🎵 Đã tắt nhạc nền');
    });
  }

  // Âm thanh nhấp & đóng hộp thoại
  document.addEventListener('click', (e) => {
    const closeBtn = e.target.closest('[data-close]');
    if (closeBtn) {
      const m = document.getElementById(closeBtn.dataset.close);
      if (m) m.classList.add('hidden');
      Sound.play('click');
      return;
    }
    if (e.target.classList && e.target.classList.contains('modal-backdrop')) {
      e.target.classList.add('hidden');
      Sound.play('click');
      return;
    }
    const el = e.target.closest('.btn, .seg-btn, .nav-link, .btn-tiny');
    if (el && (!el.id || (!el.id.startsWith('ws-') && !el.id.startsWith('r-'))) && !el.closest('#classify')) {
      Sound.play('click');
    }
  });

  // ---------- Menu di động ----------
  const nav = document.getElementById('main-nav');
  const btnMenu = document.getElementById('btn-menu');
  if (nav && btnMenu) {
    btnMenu.addEventListener('click', () => nav.classList.toggle('open'));
  }

  // ---------- Hệ thống chuyển trang độc lập theo Menu (SPA Tabs) ----------
  const TABS = [
    { id: 'trang-chu', title: 'Trang chủ' },
    { id: 'ly-thuyet', title: 'Lý thuyết' },
    { id: 'tn1', title: 'TN1: Tia sáng' },
    { id: 'tn2', title: 'TN2: Vẽ ảnh' },
    { id: 'phieu', title: 'Phiếu học tập' },
    { id: 'nhom', title: 'Nhóm Natural' },
  ];

  const tabEls = TABS.map((t) => document.getElementById(t.id)).filter(Boolean);
  const navLinks = [...document.querySelectorAll('.nav-link')];

  if (tabEls.length === TABS.length) {
    document.body.classList.add('tabbed-mode');

    // Gắn class page-tab và tạo thanh điều hướng Bước trước / Bước tiếp theo ở cuối mỗi trang
    TABS.forEach((t, idx) => {
      const sec = document.getElementById(t.id);
      sec.classList.add('page-tab');
      const wrap = sec.querySelector('.container');
      if (!wrap) return;

      const prev = idx > 0 ? TABS[idx - 1] : null;
      const next = idx < TABS.length - 1 ? TABS[idx + 1] : null;
      const pager = document.createElement('div');
      pager.className = 'tab-pager no-print';
      pager.innerHTML = `
        <div>
          ${prev ? `<a href="#${prev.id}" class="btn btn-ghost btn-small">← ${prev.title}</a>` : ''}
        </div>
        <div class="tab-step-indicator">Trang ${idx + 1} / ${TABS.length} · <b>${t.title}</b></div>
        <div>
          ${next ? `<a href="#${next.id}" class="btn btn-primary btn-small">${next.title} →</a>` : ''}
        </div>
      `;
      wrap.appendChild(pager);
    });

    function switchTab(targetId, updateHash = true) {
      const valid = TABS.some((t) => t.id === targetId) ? targetId : 'trang-chu';
      TABS.forEach((t) => {
        const sec = document.getElementById(t.id);
        const active = t.id === valid;
        sec.classList.toggle('active-tab', active);
        if (active) {
          sec.querySelectorAll('.reveal').forEach((el) => el.classList.add('in'));
        }
      });

      navLinks.forEach((l) => {
        l.classList.toggle('active', l.getAttribute('href') === '#' + valid);
      });

      if (nav) nav.classList.remove('open');
      if (updateHash && history.replaceState) {
        history.replaceState(null, '', '#' + valid);
      }
      window.scrollTo({ top: 0, behavior: 'instant' });

      requestAnimationFrame(() => {
        document.dispatchEvent(new CustomEvent('tabshown', { detail: valid }));
      });
    }

    // Bắt mọi cú nhấp vào liên kết nội bộ #...
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (!a) return;
      const id = a.getAttribute('href').slice(1);
      if (TABS.some((t) => t.id === id)) {
        e.preventDefault();
        switchTab(id, true);
      }
    });

    window.addEventListener('hashchange', () => {
      const h = (location.hash || '#trang-chu').slice(1);
      switchTab(h, false);
    });

    const initialHash = (location.hash || '#trang-chu').slice(1);
    switchTab(initialHash, false);
  } else {
    // Trang đơn (phieu-hoc-tap.html)
    document.querySelectorAll('.reveal').forEach((el) => el.classList.add('in'));
  }
})();
