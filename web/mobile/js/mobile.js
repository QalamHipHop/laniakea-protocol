/* ============================================================
   🌌 Laniakea Mobile — PWA Logic
   ============================================================ */

const state = { page: 'home', wallet: null };

// Starfield
(function initStars() {
  const c = document.getElementById('starfield');
  const ctx = c.getContext('2d');
  function resize() { c.width = innerWidth; c.height = innerHeight; }
  resize(); addEventListener('resize', resize);
  const stars = Array.from({length: 80}, () => ({
    x: Math.random()*innerWidth, y: Math.random()*innerHeight,
    r: Math.random()*1.2 + 0.3, a: Math.random(), s: Math.random()*0.02 + 0.005
  }));
  (function draw() {
    ctx.clearRect(0, 0, c.width, c.height);
    stars.forEach(s => {
      s.a += s.s; if (s.a > 1 || s.a < 0.1) s.s *= -1;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
      ctx.fillStyle = `rgba(200,200,255,${s.a*0.7})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  })();
})();

// Navigation
document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById('p-' + btn.dataset.page).classList.add('active');
    state.page = btn.dataset.page;
    if (state.page === 'evo') buildDNA();
    if (state.page === 'gov') buildProposals();
    if (state.page === 'wallet') updateWalletUI();
  });
});

// DNA helix
function buildDNA() {
  const el = document.getElementById('dnaViz');
  if (!el || el.children.length) return;
  for (let i = 0; i < 40; i++) {
    const d = document.createElement('div');
    d.className = 'dna-rung';
    el.appendChild(d);
  }
}

// Proposals
function buildProposals() {
  const el = document.getElementById('mProposals');
  if (!el || el.children.length) return;
  const props = [
    { t: 'افزایش پاداش Breeding', p: 67 },
    { t: 'راه‌اندازی زنجیره جانبی', p: 42 },
    { t: 'بهبود اجماع PoHD', p: 89 },
  ];
  props.forEach(p => {
    const div = document.createElement('div');
    div.className = 'prop-mob';
    div.innerHTML = `
      <div class="prop-t-mob">${p.t}</div>
      <div class="prop-bar-mob"><div style="width:${p}%"></div></div>
      <div class="prop-meta-mob">${p}% · در حال رأی‌گیری</div>
    `;
    el.appendChild(div);
  });
}

// Chart
(function initChart() {
  const ctx = document.getElementById('mChart')?.getContext('2d');
  if (!ctx) return;
  const data = Array.from({length: 24}, (_, i) => 8 + Math.sin(i/3) * 3 + Math.random()*2);
  new Chart(ctx, {
    type: 'line',
    data: { labels: data.map((_,i) => i+'h'), datasets: [{
      label: 'C(t)', data, borderColor: '#7c3aed',
      backgroundColor: (c) => { const g = c.chart.ctx.createLinearGradient(0,0,0,160); g.addColorStop(0,'rgba(124,58,237,0.4)'); g.addColorStop(1,'transparent'); return g; },
      fill: true, tension: 0.4, borderWidth: 2, pointRadius: 0
    }]},
    options: { responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { display: false }, y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9b9bd0', font: { size: 10 } } } }
    }
  });
})();

// Activity
(function initActivity() {
  const list = document.getElementById('mActivity');
  const items = [
    { i: '🧬', t: 'SCDA #4218 → T4', time: '12:04' },
    { i: '🔷', t: 'بلاک #8931 تأیید شد', time: '12:04' },
    { i: '🧠', t: 'Hard Problem حل شد +480', time: '12:02' },
    { i: '🏛️', t: 'رأی DAO ثبت شد', time: '11:58' },
    { i: '💎', t: 'استیک +1200 LKC', time: '11:45' },
  ];
  items.forEach(it => {
    const li = document.createElement('li');
    li.className = 'activity-item';
    li.innerHTML = `<span class="ico">${it.i}</span><span>${it.t}</span><span class="time">${it.time}</span>`;
    list.appendChild(li);
  });
})();

// Hard problems
(function initProblems() {
  const el = document.getElementById('mProblems');
  const list = [
    { q: '∇²ψ + (8π/c⁴)T = 0', h: '9.2', r: '480' },
    { q: 'P vs NP — SAT reduction', h: '8.7', r: '420' },
    { q: 'Riemann ζ(s) zeros', h: '8.1', r: '380' },
  ];
  list.forEach(p => {
    const d = document.createElement('div');
    d.className = 'hp-item-mob';
    d.innerHTML = `<div class="hp-q-mob">${p.q}</div><div class="hp-d-mob">Hardness: ${p.h} · Reward: ${p.r}</div>`;
    el.appendChild(d);
  });
})();

// Wallet
const walletBtn = document.getElementById('mConnect');
const disconnectBtn = document.getElementById('mDisconnect');
const headerWalletBtn = document.getElementById('walletBtn');

async function connectWallet() {
  try {
    if (typeof window.ethereum !== 'undefined') {
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      const chainId = parseInt(await window.ethereum.request({ method: 'eth_chainId' }), 16);
      state.wallet = { address: accounts[0], chainId };
    } else {
      // Mock for demo
      state.wallet = {
        address: '0x' + Array.from({length:40}, () => Math.floor(Math.random()*16).toString(16)).join(''),
        chainId: 1
      };
      toast('⚠️ MetaMask یافت نشد — حالت نمایشی');
    }
    updateWalletUI();
    toast('✅ کیف پول متصل شد');
  } catch (e) {
    toast('❌ اتصال لغو شد');
  }
}

function disconnectWallet() {
  state.wallet = null;
  updateWalletUI();
  toast('کیف پول قطع شد');
}

function updateWalletUI() {
  const title = document.getElementById('walletStateTitle');
  const sub = document.getElementById('walletStateSub');
  const info = document.getElementById('walletInfo');
  const addr = document.getElementById('walletAddr');
  const chain = document.getElementById('walletChain');
  const bal = document.getElementById('walletBal');
  const header = document.getElementById('walletBtn');
  const chains = { 1: 'Ethereum', 56: 'BNB', 137: 'Polygon', 42161: 'Arbitrum' };

  if (state.wallet) {
    title.textContent = 'کیف پول متصل است';
    sub.textContent = 'دسترسی کامل فعال';
    info.classList.remove('hidden');
    walletBtn.classList.add('hidden');
    disconnectBtn.classList.remove('hidden');
    addr.textContent = state.wallet.address.slice(0,6) + '…' + state.wallet.address.slice(-4);
    chain.textContent = chains[state.wallet.chainId] || `Chain ${state.wallet.chainId}`;
    bal.textContent = '2,480.42 LKC';
    header.textContent = state.wallet.address.slice(0,4) + '…' + state.wallet.address.slice(-2);
  } else {
    title.textContent = 'کیف پول متصل نیست';
    sub.textContent = 'برای دسترسی کامل، کیف پول خود را وصل کنید';
    info.classList.add('hidden');
    walletBtn.classList.remove('hidden');
    disconnectBtn.classList.add('hidden');
    header.textContent = 'اتصال';
  }
}

walletBtn.addEventListener('click', connectWallet);
disconnectBtn.addEventListener('click', disconnectWallet);
headerWalletBtn.addEventListener('click', () => {
  if (state.wallet) {
    document.querySelector('[data-page="wallet"]').click();
  } else {
    connectWallet();
  }
});

// Actions
document.querySelectorAll('[data-act]').forEach(b => {
  b.addEventListener('click', () => toast('🚀 ' + b.dataset.act + ' (دمو)'));
});

document.getElementById('mEvolve')?.addEventListener('click', () => toast('🧬 تکامل انجام شد!'));

// Toast
function toast(msg) {
  const t = document.getElementById('mToast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}

// Live updates
setInterval(() => {
  const bal = document.getElementById('userBalance');
  if (bal) {
    const cur = parseFloat(bal.textContent.replace(/,/g, ''));
    const next = (cur + (Math.random() - 0.4) * 5).toFixed(2);
    bal.textContent = parseFloat(next).toLocaleString() + ' LKC';
  }
  const block = document.getElementById('mBlock');
  if (block) {
    const n = parseInt(block.textContent.replace(/[^0-9]/g, '')) + 1;
    block.textContent = '#' + n;
  }
}, 8000);

// Register service worker for PWA
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(() => {});
}

// ============================================================
// MOBILE v3 — Theme + Haptics (Qalam, 2025)
// ============================================================

const MTheme = (() => {
  const KEY = 'laniakea-mob-theme';
  const valid = ['cosmic', 'dark', 'light'];
  function get() {
    const stored = localStorage.getItem(KEY);
    if (stored && valid.includes(stored)) return stored;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'cosmic';
  }
  function set(t) {
    if (!valid.includes(t)) t = 'cosmic';
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem(KEY, t);
  }
  function cycle() {
    const cur = get();
    const next = valid[(valid.indexOf(cur) + 1) % valid.length];
    set(next);
    mToast(`Theme: ${next}`);
    return next;
  }
  function init() {
    set(get());
    const btn = document.getElementById('themeCycle');
    if (btn) btn.onclick = cycle;
  }
  return { get, set, cycle, init, valid };
})();

// Haptic feedback (where supported)
function haptic(pattern = 10) {
  if (navigator.vibrate) navigator.vibrate(pattern);
}

// Ripple effect
function attachRipple(el) {
  el.classList.add('m-ripple');
  el.addEventListener('pointerdown', e => {
    const r = el.getBoundingClientRect();
    el.style.setProperty('--rx', `${e.clientX - r.left}px`);
    el.style.setProperty('--ry', `${e.clientY - r.top}px`);
    haptic(8);
  });
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  MTheme.init();
  // Auto-attach ripple to all .m-card-v3
  document.querySelectorAll('.m-card-v3, .nav-item, .m-btn').forEach(attachRipple);
  // Pull-to-refresh hint
  const shell = document.querySelector('.app-shell');
  const hint = document.querySelector('.ptr-hint');
  if (shell && hint) {
    let startY = 0;
    shell.addEventListener('touchstart', e => { startY = e.touches[0].clientY; }, { passive: true });
    shell.addEventListener('touchmove', e => {
      const dy = e.touches[0].clientY - startY;
      if (dy > 80) hint.classList.add('active');
    }, { passive: true });
    shell.addEventListener('touchend', () => {
      hint.classList.remove('active');
      if (startY) location.reload();
    });
  }
});

// Expose
window.MobileV3 = { MTheme, haptic, attachRipple };
