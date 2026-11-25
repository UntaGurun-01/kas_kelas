// ── SIDEBAR TOGGLE ────────────────────────────────────────
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');

if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

// ── THEME MANAGEMENT ─────────────────────────────────────────
function applyTheme(theme, saveBackend = true) {
  if (theme !== 'light' && theme !== 'dark') theme = 'dark';

  const html = document.documentElement;
  const body = document.body;

  // Set attribute & classes on html and body
  html.setAttribute('data-theme', theme);
  html.classList.remove('dark', 'light');
  html.classList.add(theme);

  if (body) {
    body.setAttribute('data-theme', theme);
    body.classList.remove('dark', 'light');
    body.classList.add(theme);
  }

  // Save to localStorage for instant local persistence
  localStorage.setItem('theme', theme);

  // Update Topbar Icon
  const icon = document.getElementById('themeIcon');
  const btn = document.getElementById('themeToggleBtn');
  if (icon) {
    if (theme === 'dark') {
      icon.className = 'bi bi-sun';
      if (btn) btn.setAttribute('title', 'Beralih ke Mode Terang');
    } else {
      icon.className = 'bi bi-moon-stars';
      if (btn) btn.setAttribute('title', 'Beralih ke Mode Gelap');
    }
  }

  // Update Pengaturan Page Theme Cards if user is on /pengaturan
  updatePengaturanThemeCards(theme);

  // Emit event for dynamic charts or other components
  window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));

  // Synchronize to Flask Session in background
  if (saveBackend) {
    fetch('/pengaturan/tema', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: 'tema=' + encodeURIComponent(theme)
    }).catch(err => console.log('Theme sync notice:', err));
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') ||
                  localStorage.getItem('theme') ||
                  (document.documentElement.classList.contains('light') ? 'light' : 'dark');
  const target = current === 'dark' ? 'light' : 'dark';
  applyTheme(target, true);
}

function updatePengaturanThemeCards(theme) {
  const darkCard = document.getElementById('themeCardDark');
  const lightCard = document.getElementById('themeCardLight');
  const badgeDark = document.getElementById('badgeDark');
  const badgeLight = document.getElementById('badgeLight');

  if (!darkCard || !lightCard) return;

  if (theme === 'dark') {
    darkCard.style.borderColor = '#10b981';
    darkCard.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.35)';
    lightCard.style.borderColor = 'rgba(255, 255, 255, 0.12)';
    lightCard.style.boxShadow = 'none';
    if (badgeDark) badgeDark.classList.remove('d-none');
    if (badgeLight) badgeLight.classList.add('d-none');
  } else {
    lightCard.style.borderColor = '#10b981';
    lightCard.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.35)';
    darkCard.style.borderColor = 'rgba(0, 0, 0, 0.1)';
    darkCard.style.boxShadow = 'none';
    if (badgeLight) {
      badgeLight.classList.remove('d-none', 'bg-secondary');
      badgeLight.classList.add('bg-success');
    }
    if (badgeDark) badgeDark.classList.add('d-none');
  }
}

// Initial run on script execution & DOM ready
(function initTheme() {
  const saved = localStorage.getItem('theme') ||
                document.documentElement.getAttribute('data-theme') ||
                'dark';
  applyTheme(saved, false);
})();

document.addEventListener('DOMContentLoaded', () => {
  const saved = localStorage.getItem('theme') ||
                document.documentElement.getAttribute('data-theme') ||
                'dark';
  applyTheme(saved, false);
});

// ── GLOBAL SEARCH ─────────────────────────────────────────
const globalSearch = document.getElementById('globalSearch');
if (globalSearch) {
  const menuMap = {
    'beranda': '/beranda',
    'iuran': '/iuran-saya',
    'transaksi': '/transaksi',
    'riwayat': '/riwayat',
    'pengumuman': '/pengumuman',
    'profil': '/profil',
    'anggota': '/anggota',
    'pengaturan': '/pengaturan',
    'tentang': '/tentang',
  };

  globalSearch.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const val = globalSearch.value.toLowerCase().trim();
      for (const [key, path] of Object.entries(menuMap)) {
        if (val.includes(key)) {
          window.location.href = path;
          return;
        }
      }
    }
  });
}

// ── AUTO-DISMISS ALERTS ───────────────────────────────────
document.querySelectorAll('.alert').forEach(alert => {
  setTimeout(() => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
    if (bsAlert) bsAlert.close();
  }, 4000);
});

// ── NUMBER COUNTER ANIMATION ──────────────────────────────
function animateCounter(el) {
  const target = parseFloat(el.dataset.target || el.textContent.replace(/[^0-9]/g, ''));
  if (isNaN(target)) return;
  let current = 0;
  const step = target / 40;
  const interval = setInterval(() => {
    current += step;
    if (current >= target) { current = target; clearInterval(interval); }
    el.textContent = Math.floor(current).toLocaleString('id-ID');
  }, 20);
}

document.querySelectorAll('[data-counter]').forEach(el => {
  animateCounter(el);
});

// ── TOOLTIP INIT ──────────────────────────────────────────
const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
tooltipEls.forEach(el => new bootstrap.Tooltip(el));

// ── FADE IN ON SCROLL ─────────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      observer.unobserve(e.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
