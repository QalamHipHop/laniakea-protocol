/* ============================================================
   🌌 LANIAKEA PROTOCOL — COSMIC APP
   SPA Router · Live data · 3D Metaverse · Charts · i18n
   ============================================================ */

// ---------- CONFIG ----------
const API = window.LANIAKEA_API || 'http://localhost:8000';
const REFRESH = 5000;

// ---------- I18N ----------
const I18N = {
  fa: {
    'loading': 'در حال اتصال به ابرپروتکل کیهانی...',
    'connect': 'اتصال',
    'nav.dashboard': 'دشبورد', 'nav.evolution': 'تکامل', 'nav.metaverse': 'متاورس',
    'nav.blockchain': 'بلاکچین ۸D', 'nav.governance': 'حاکمیت',
    'nav.economy': 'اقتصاد', 'nav.network': 'شبکه',
    'hero.title1': 'ابرپروتکل تکامل', 'hero.title2': 'هوش جمعی کیهانی',
    'hero.sub': 'یک اکوسیستم غیرمتمرکز که با الهام از ساختار جهان هستی، از سلول تک‌یاخته تا هوش کیهانی را شبیه‌سازی می‌کند.',
    'hero.cta1': 'آغاز تکامل', 'hero.cta2': 'ورود به متاورس',
    'stats.scda': 'SCDA فعال', 'stats.blocks': 'بلاک ۸D', 'stats.uptime': 'آپتایم', 'stats.peers': 'همتایان P2P',
    'kpi.tier': 'Tier متوسط', 'kpi.energy': 'انرژی شبکه', 'kpi.complexity': 'پیچیدگی', 'kpi.treasury': 'خزانه DAO',
    'chart.evolution': 'منحنی تکامل', 'chart.network': 'نقشه شبکه P2P',
    'feed.title': 'جریان زنده شبکه', 'console.title': 'کنسول فرمان',
    'evo.title': 'موتور تکامل SCDA',
    'evo.sub': 'DNA دیجیتال + Breeding + Hard Problems — هر سلول یک شخصیت تکامل‌یافته',
    'evo.dist': 'توزیع Tier', 'evo.hard': 'Hard Problems', 'evo.evolve': 'تکامل بعدی',
    'dna.tier': 'Tier', 'dna.gen': 'نسل', 'dna.energy': 'انرژی', 'dna.complexity': 'پیچیدگی',
    'mv.title': 'متاورس هایپرکیوب ۸D',
    'mv.sub': '256 رأس · 1024 یال · چند نمایش · بُعد هشتم: آگاهی',
    'bc.title': 'بلاکچین هایپرکیوب ۸D',
    'bc.sub': 'اجماع PoHD (Proof of Human Development) + PoA + PoV',
    'bc.chain': 'زنجیره زنده', 'bc.cube': 'بردار ۸ بعدی',
    'gov.title': 'DAO — حاکمیت غیرمتمرکز',
    'gov.sub': 'پیشنهادها · رأی‌گیری · خزانه · تفویض',
    'gov.props': 'پیشنهادهای فعال', 'gov.treasury': 'خزانه',
    'eco.title': 'اقتصاد دانش', 'eco.sub': 'بازار Hard Problems · NFT دانش · Staking',
    'eco.price': 'قیمت LKC', 'eco.stake': 'استیکینگ', 'eco.deposit': 'سپرده‌گذاری', 'eco.nft': 'NFT دانش',
    'net.title': 'شبکه P2P', 'net.sub': 'Kademlia DHT · WebSocket Transport · K-بازویی ۲۰',
    'net.peers': 'همتایان', 'net.health': 'سلامت شبکه',
  },
  en: {
    'loading': 'Connecting to the cosmic superprotocol...',
    'connect': 'Connect',
    'nav.dashboard': 'Dashboard', 'nav.evolution': 'Evolution', 'nav.metaverse': 'Metaverse',
    'nav.blockchain': '8D Blockchain', 'nav.governance': 'Governance',
    'nav.economy': 'Economy', 'nav.network': 'Network',
    'hero.title1': 'Superprotocol for', 'hero.title2': 'Cosmic Collective Intelligence',
    'hero.sub': 'A decentralized ecosystem inspired by the structure of the universe, simulating evolution from a single cell to cosmic intelligence.',
    'hero.cta1': 'Begin Evolution', 'hero.cta2': 'Enter Metaverse',
    'stats.scda': 'Active SCDAs', 'stats.blocks': '8D Blocks', 'stats.uptime': 'Uptime', 'stats.peers': 'P2P Peers',
    'kpi.tier': 'Avg Tier', 'kpi.energy': 'Network Energy', 'kpi.complexity': 'Complexity', 'kpi.treasury': 'DAO Treasury',
    'chart.evolution': 'Evolution Curve', 'chart.network': 'P2P Network Map',
    'feed.title': 'Live Network Stream', 'console.title': 'Command Console',
    'evo.title': 'SCDA Evolution Engine',
    'evo.sub': 'Digital DNA + Breeding + Hard Problems — every cell is an evolved entity',
    'evo.dist': 'Tier Distribution', 'evo.hard': 'Hard Problems', 'evo.evolve': 'Next Evolution',
    'dna.tier': 'Tier', 'dna.gen': 'Generation', 'dna.energy': 'Energy', 'dna.complexity': 'Complexity',
    'mv.title': '8D Hypercube Metaverse',
    'mv.sub': '256 vertices · 1024 edges · multi-projection · 8th dim: awareness',
    'bc.title': '8D Hypercube Blockchain',
    'bc.sub': 'PoHD (Proof of Human Development) + PoA + PoV consensus',
    'bc.chain': 'Live Chain', 'bc.cube': '8D Vector',
    'gov.title': 'DAO — Decentralized Governance',
    'gov.sub': 'Proposals · Voting · Treasury · Delegation',
    'gov.props': 'Active Proposals', 'gov.treasury': 'Treasury',
    'eco.title': 'Knowledge Economy', 'eco.sub': 'Hard Problems market · Knowledge NFTs · Staking',
    'eco.price': 'LKC Price', 'eco.stake': 'Staking', 'eco.deposit': 'Deposit', 'eco.nft': 'Knowledge NFTs',
    'net.title': 'P2P Network', 'net.sub': 'Kademlia DHT · WebSocket transport · k-bucket 20',
    'net.peers': 'Peers', 'net.health': 'Network Health',
  }
};

const state = { lang: 'fa', theme: 'cosmic', paused: false, charts: {}, rotating: true };

// ---------- BOOT ----------
window.addEventListener('DOMContentLoaded', () => {
  initLoader();
  initStarfield();
  initRouter();
  initI18n();
  initTheme();
  initCounters();
  initKPIs();
  initCharts();
  initMetaverse();
  initVector8();
  initConsole();
  initLiveFeed();
  initActions();
  setInterval(refreshData, REFRESH);
});

// ---------- LOADER ----------
function initLoader() {
  const fill = document.getElementById('loaderFill');
  let p = 0;
  const t = setInterval(() => {
    p += Math.random() * 18;
    if (p >= 100) { p = 100; clearInterval(t); setTimeout(() => document.getElementById('loader').classList.add('hide'), 200); }
    fill.style.width = p + '%';
  }, 120);
}

// ---------- STARFIELD ----------
function initStarfield() {
  const c = document.getElementById('starfield');
  const ctx = c.getContext('2d');
  let stars = [];
  const resize = () => { c.width = innerWidth; c.height = innerHeight; stars = Array.from({length: 220}, () => ({
    x: Math.random()*c.width, y: Math.random()*c.height,
    z: Math.random()*1.5 + 0.2, r: Math.random()*1.4,
    a: Math.random(), s: Math.random()*0.02 + 0.005
  })); };
  resize(); addEventListener('resize', resize);
  const draw = () => {
    ctx.clearRect(0,0,c.width,c.height);
    stars.forEach(s => {
      s.a += s.s; if (s.a > 1 || s.a < 0.1) s.s *= -1;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r * s.z, 0, Math.PI*2);
      ctx.fillStyle = `rgba(${180+Math.random()*75}, ${180+Math.random()*75}, 255, ${s.a*0.8})`;
      ctx.fill();
    });
    requestAnimationFrame(draw);
  };
  draw();
}

// ---------- ROUTER ----------
function initRouter() {
  document.querySelectorAll('[data-route]').forEach(el => {
    el.addEventListener('click', e => {
      e.preventDefault();
      const r = el.dataset.route;
      location.hash = '#' + r;
      document.getElementById('navLinks')?.classList.remove('open');
    });
  });
  addEventListener('hashchange', navigate);
  navigate();
}
function navigate() {
  const r = (location.hash || '#dashboard').slice(1);
  document.querySelectorAll('.route').forEach(s => s.classList.toggle('active', s.id === 'route-'+r));
  document.querySelectorAll('.nav-link').forEach(n => n.classList.toggle('active', n.dataset.route === r));
  if (r === 'metaverse' && !state._mvInit) { state._mvInit = true; startMetaverse(); }
}

// ---------- I18N ----------
function initI18n() {
  document.getElementById('langToggle').addEventListener('click', () => {
    state.lang = state.lang === 'fa' ? 'en' : 'fa';
    document.documentElement.lang = state.lang;
    document.body.dir = state.lang === 'fa' ? 'rtl' : 'ltr';
    document.getElementById('langLabel').textContent = state.lang === 'fa' ? 'EN' : 'فا';
    applyI18n();
  });
  applyI18n();
}
function applyI18n() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const k = el.dataset.i18n;
    if (I18N[state.lang][k]) el.textContent = I18N[state.lang][k];
  });
}

// ---------- THEME ----------
function initTheme() {
  const btn = document.getElementById('themeToggle');
  btn.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'cosmic' ? 'light' : 'cosmic';
    document.documentElement.dataset.theme = next;
    btn.textContent = next === 'cosmic' ? '🌙' : '☀️';
    state.charts.ev && state.charts.ev.update();
    state.charts.net && state.charts.net.update();
  });
}

// ---------- COUNTERS ----------
function initCounters() {
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const el = e.target;
        const target = parseFloat(el.dataset.counter);
        const dur = 1500, start = performance.now();
        const step = t => {
          const p = Math.min((t-start)/dur, 1);
          const v = target * (1 - Math.pow(1-p, 3));
          el.textContent = target < 100 ? v.toFixed(2) : Math.floor(v).toLocaleString();
          if (p < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
        obs.unobserve(el);
      }
    });
  }, { threshold: 0.3 });
  document.querySelectorAll('[data-counter]').forEach(el => obs.observe(el));
}

// ---------- KPIs (simulated live values) ----------
function initKPIs() {
  document.getElementById('kpiTier').textContent = 'T3.24';
  document.getElementById('kpiEnergy').textContent = '87.4%';
  document.getElementById('kpiComplexity').textContent = 'C=12.8';
  document.getElementById('kpiTreasury').textContent = '1.28M LKC';
  refreshData();
}

function refreshData() {
  const tier = (3 + Math.random()*0.6).toFixed(2);
  const energy = (80 + Math.random()*15).toFixed(1) + '%';
  const complex = 'C=' + (10 + Math.random()*5).toFixed(1);
  const treas = (1.2 + Math.random()*0.1).toFixed(2) + 'M LKC';
  if (state._ready) {
    document.getElementById('kpiTier').textContent = 'T' + tier;
    document.getElementById('kpiEnergy').textContent = energy;
    document.getElementById('kpiComplexity').textContent = complex;
    document.getElementById('kpiTreasury').textContent = treas;
  }
  state._ready = true;
  // tick charts
  ['ev', 'price', 'tier', 'treasury'].forEach(k => state.charts[k]?.data?.datasets?.forEach((d,i) => {
    if (k === 'ev' && i === 0) { d.data.push(d.data[d.data.length-1] + (Math.random()-0.4)); d.data.shift(); }
    if (k === 'price' && i === 0) { d.data.push(d.data[d.data.length-1] + (Math.random()-0.5)*0.5); d.data.shift(); }
  }));
  state.charts.ev?.update('none');
  state.charts.price?.update('none');
}

// ---------- CHARTS ----------
function initCharts() {
  Chart.defaults.color = '#9b9bd0';
  Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
  Chart.defaults.font.family = "'Space Grotesk', sans-serif";

  // Evolution curve
  const ev = document.getElementById('chartEvolution').getContext('2d');
  const data = Array.from({length: 30}, (_, i) => 1 + Math.log(i+1) * 2.5 + Math.sin(i/3) * 0.4);
  state.charts.ev = new Chart(ev, {
    type: 'line',
    data: { labels: data.map((_,i)=>i), datasets: [{
      label: 'C(t)', data, borderColor: '#7c3aed',
      backgroundColor: (ctx) => {
        const g = ctx.chart.ctx.createLinearGradient(0,0,0,220);
        g.addColorStop(0, 'rgba(124,58,237,0.5)'); g.addColorStop(1, 'rgba(124,58,237,0)');
        return g;
      },
      fill: true, tension: 0.4, borderWidth: 2.5, pointRadius: 0
    },{
      label: 'E(t)', data: data.map(v => 100 - v*3), borderColor: '#06b6d4',
      backgroundColor: 'rgba(6,182,212,0.05)', fill: true, tension: 0.4, borderWidth: 2, pointRadius: 0
    }]},
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#d6d6f5' } } }, scales: { x: { display: false }, y: { grid: { color: 'rgba(255,255,255,0.04)' } } } }
  });

  // Network scatter
  const net = document.getElementById('chartNetwork').getContext('2d');
  const nodes = Array.from({length: 60}, () => ({ x: Math.random()*100, y: Math.random()*100 }));
  state.charts.net = new Chart(net, {
    type: 'scatter',
    data: { datasets: [{
      label: 'Nodes', data: nodes, pointRadius: 4,
      pointBackgroundColor: (ctx) => {
        const colors = ['#7c3aed','#06b6d4','#ec4899','#f59e0b'];
        return colors[ctx.dataIndex % 4];
      },
      pointBorderColor: 'rgba(255,255,255,0.6)', pointBorderWidth: 1
    }]},
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
      scales: { x: { display: false }, y: { display: false } } }
  });

  // Tier distribution
  const tier = document.getElementById('chartTier').getContext('2d');
  state.charts.tier = new Chart(tier, {
    type: 'doughnut',
    data: { labels: ['T1','T2','T3','T4','T5','T6'], datasets: [{
      data: [120, 340, 480, 220, 75, 12],
      backgroundColor: ['#06b6d4','#7c3aed','#ec4899','#f59e0b','#10b981','#ef4444'],
      borderWidth: 0
    }]},
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { padding: 12, font: { size: 11 } } } }, cutout: '60%' }
  });

  // Treasury
  const tr = document.getElementById('chartTreasury').getContext('2d');
  state.charts.treasury = new Chart(tr, {
    type: 'bar',
    data: { labels: ['Jan','Feb','Mar','Apr','May','Jun'], datasets: [{
      label: 'LKC', data: [820, 905, 1050, 1180, 1210, 1284],
      backgroundColor: (ctx) => {
        const g = ctx.chart.ctx.createLinearGradient(0,0,0,200);
        g.addColorStop(0,'#7c3aed'); g.addColorStop(1,'#06b6d4'); return g;
      }, borderRadius: 8
    }]},
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
  });

  // Price
  const pr = document.getElementById('chartPrice').getContext('2d');
  const priceData = Array.from({length:40},(_,i)=> 12 + Math.sin(i/4)*2 + Math.random()*0.8);
  state.charts.price = new Chart(pr, {
    type: 'line',
    data: { labels: priceData.map((_,i)=>i), datasets: [{
      label: 'LKC/USD', data: priceData, borderColor: '#f59e0b', backgroundColor: 'rgba(245,158,11,0.1)',
      fill: true, tension: 0.3, borderWidth: 2, pointRadius: 0
    }]},
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false } } }
  });

  // Geo (peers) — radar
  const geo = document.getElementById('chartGeo').getContext('2d');
  state.charts.geo = new Chart(geo, {
    type: 'polarArea',
    data: { labels: ['NA','EU','AS','SA','AF','OC'], datasets: [{
      data: [1200, 980, 1500, 280, 158, 100],
      backgroundColor: ['rgba(124,58,237,0.6)','rgba(6,182,212,0.6)','rgba(236,72,153,0.6)','rgba(245,158,11,0.6)','rgba(16,185,129,0.6)','rgba(239,68,68,0.6)'],
      borderColor: 'rgba(255,255,255,0.2)', borderWidth: 1
    }]},
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } }, scales: { r: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { display: false } } } }
  });
}

// ---------- VECTOR 8D ----------
function initVector8() {
  const v = document.getElementById('vector8');
  if (!v) return;
  v.innerHTML = '';
  for (let i = 0; i < 8; i++) {
    const c = document.createElement('div');
    c.className = 'v8-cell';
    c.textContent = 'D'+i;
    c.style.background = `linear-gradient(135deg, ${['#7c3aed','#06b6d4','#ec4899','#f59e0b'][i%4]}30, transparent)`;
    c.style.borderColor = ['#7c3aed','#06b6d4','#ec4899','#f59e0b'][i%4] + '50';
    c.title = `Dimension ${i}: ${['Knowledge','Energy','Complexity','Time','Space','Consciousness','Network','Entropy'][i]}`;
    v.appendChild(c);
  }
}

// ---------- METAVERSE (8D Hypercube 3D projection) ----------
let mvState = { rot: { x: 0, y: 0, z: 0 } };
function initMetaverse() { /* startMetaverse called on route */ }
function startMetaverse() {
  const c = document.getElementById('mvCanvas');
  if (!c) return;
  const ctx = c.getContext('2d');
  c.width = c.offsetWidth; c.height = 460;

  // 8 vertices of a hypercube projected to 3D
  const V = [
    [-1,-1,-1,-1, 1, 1, 1, 1],[ 1,-1,-1,-1,-1, 1, 1, 1],[ 1, 1,-1,-1,-1,-1, 1, 1],[-1, 1,-1,-1, 1,-1, 1, 1],
    [-1,-1, 1,-1, 1, 1,-1, 1],[ 1,-1, 1,-1,-1, 1,-1, 1],[ 1, 1, 1,-1,-1,-1,-1, 1],[-1, 1, 1,-1, 1,-1,-1, 1],
    [-1,-1,-1, 1, 1, 1, 1,-1],[ 1,-1,-1, 1,-1, 1, 1,-1],[ 1, 1,-1, 1,-1,-1, 1,-1],[-1, 1,-1, 1, 1,-1, 1,-1],
    [-1,-1, 1, 1, 1, 1,-1,-1],[ 1,-1, 1, 1,-1, 1,-1,-1],[ 1, 1, 1, 1,-1,-1,-1,-1],[-1, 1, 1, 1, 1,-1,-1,-1]
  ];
  const E = [];
  for (let i=0;i<16;i++) for (let j=i+1;j<16;j++) {
    let diff=0; for (let k=0;k<8;k++) if (V[i][k]!==V[j][k]) diff++;
    if (diff===1) E.push([i,j]);
  }

  const project = (p8, t) => {
    // rotate in 8D then project to 3D
    const r = (a, i, j) => { const c=Math.cos(a),s=Math.sin(a); const x=p8[i]*c-p8[j]*s; const y=p8[i]*s+p8[j]*c; p8[i]=x; p8[j]=y; };
    const p = p8.slice();
    r(t.x, 0, 4); r(t.y, 1, 5); r(t.z, 2, 6);
    // 8D -> 3D: just take 3 coords after rotation
    return { x: p[0]*80 + p[4]*40, y: p[1]*80 + p[5]*40, z: p[2]*80 + p[6]*40 };
  };

  const colors = ['#7c3aed','#06b6d4','#ec4899','#f59e0b'];

  const draw = () => {
    if (!document.getElementById('route-metaverse')?.classList.contains('active')) { requestAnimationFrame(draw); return; }
    if (state.rotating) { mvState.rot.x += 0.004; mvState.rot.y += 0.006; mvState.rot.z += 0.002; }
    const w = c.width, h = c.height;
    ctx.fillStyle = 'rgba(5,5,20,0.25)'; ctx.fillRect(0,0,w,h);
    const cx = w/2, cy = h/2;
    const pts = V.map(p => project(p.slice(), { ...mvState.rot }));

    // edges
    E.forEach(([a,b], i) => {
      const pa = pts[a], pb = pts[b];
      const depth = (pa.z + pb.z) / 2;
      const alpha = Math.max(0.1, 0.6 - depth*0.05);
      ctx.beginPath();
      ctx.moveTo(cx+pa.x, cy+pa.y); ctx.lineTo(cx+pb.x, cy+pb.y);
      ctx.strokeStyle = `rgba(124,58,237,${alpha})`;
      ctx.lineWidth = 1.2;
      ctx.stroke();
    });

    // vertices
    pts.forEach((p, i) => {
      const depth = p.z;
      const size = Math.max(2, 6 - depth*0.4);
      const alpha = Math.max(0.4, 1 - depth*0.05);
      ctx.beginPath();
      ctx.arc(cx+p.x, cy+p.y, size, 0, Math.PI*2);
      ctx.fillStyle = colors[i%4] + Math.floor(alpha*255).toString(16).padStart(2,'0');
      ctx.shadowBlur = 15; ctx.shadowColor = colors[i%4];
      ctx.fill();
      ctx.shadowBlur = 0;
    });
    requestAnimationFrame(draw);
  };
  draw();

  document.querySelectorAll('.mv-controls [data-rotate]').forEach(b => {
    b.addEventListener('click', () => {
      const r = b.dataset.rotate;
      if (r === 'x') mvState.rot.x += Math.PI/4;
      else if (r === 'y') mvState.rot.y += Math.PI/4;
      else if (r === 'z') mvState.rot.z += Math.PI/4;
      else { mvState.rot = { x:0, y:0, z:0 }; }
    });
  });

  // v3 enhancement: also init WebGL hypercube overlay if available
  if (window.Cosmic && window.Cosmic.Hypercube3D) {
    try {
      // store a flag so we can re-init on route change
      window.__cosmicMv3D = { canvas: c, V, E, project, draw, mvState, colors };
    } catch (e) {
      console.warn('Cosmic v3 hypercube init failed:', e);
    }
  }
}

// ---------- CONSOLE ----------
function initConsole() {
  const form = document.getElementById('consoleForm');
  const input = document.getElementById('consoleInput');
  const out = document.getElementById('consoleOut');
  if (!form) return;

  const commands = {
    help: '▸ status, evolve, mine, peers, blocks, balance, dna, hard, whoami, clear',
    status: '▸ Network: ONLINE · 4218 peers · Block #8931 · SCDA Tier avg: T3.24',
    evolve: '▸ ΔC computed: C(t+1) = 13.4 · Energy consumed: 12.7 · Tier: T3 → T3',
    mine: '▸ Mining started · Nonce: 0x4f2a... · Hashrate: 1.2 MH/s · Block #8932 candidate',
    peers: '▸ Active peers: 4218 · DHT buckets: 20/20 · avg latency: 32ms',
    blocks: '▸ Latest: #8931 (PoHD) · #8930 (PoHD) · #8929 (PoV) · ...',
    balance: '▸ Wallet: 0x4F2A…b8E1 · LKC: 2,480.42 · Staked: 1,200.00',
    dna: '▸ DNA: ATGC-GCAT-TTAA · Generation: 42 · Mutations: 7 · Fitness: 0.87',
    hard: '▸ Active Hard Problems: 14 · Open reward pool: 48,200 LKC',
    whoami: '▸ SCDA #4218 · Tier: T3 · Born: 2024-Q3 · Reputation: 4.7σ',
    clear: '__CLEAR__'
  };

  form.addEventListener('submit', e => {
    e.preventDefault();
    const cmd = input.value.trim().toLowerCase();
    if (!cmd) return;
    const ln = document.createElement('div');
    ln.className = 'ln';
    ln.innerHTML = `<span class="prompt">laniakea@v1.0.0 ~ $</span> <span class="cmd">${cmd}</span>`;
    out.appendChild(ln);
    const res = commands[cmd] || `▸ command not found: ${cmd}. try 'help'`;
    if (res === '__CLEAR__') { out.innerHTML = ''; input.value=''; return; }
    const r = document.createElement('div');
    r.className = 'ln out';
    r.textContent = res;
    out.appendChild(r);
    out.scrollTop = out.scrollHeight;
    input.value = '';
  });

  document.querySelectorAll('.console-tabs .tab').forEach(t => {
    t.addEventListener('click', () => {
      document.querySelectorAll('.console-tabs .tab').forEach(x => x.classList.remove('active'));
      t.classList.add('active');
      input.value = t.dataset.cmd;
    });
  });
}

// ---------- LIVE FEED ----------
function initLiveFeed() {
  const events = [
    { i:'🧬', t:'SCDA #{n} → Tier {t}', get: () => ({ n: 4000+Math.floor(Math.random()*500), t: 'T'+(2+Math.floor(Math.random()*4)) }) },
    { i:'🔷', t:'Block #{b} confirmed (PoHD)', get: () => ({ b: 8900+Math.floor(Math.random()*50) }) },
    { i:'🧠', t:'Hard Problem #{n} solved · reward {r} LKC', get: () => ({ n: 200+Math.floor(Math.random()*20), r: 100+Math.floor(Math.random()*500) }) },
    { i:'🏛️', t:'DAO proposal #{n} vote update · {p}%', get: () => ({ n: 10+Math.floor(Math.random()*5), p: 30+Math.floor(Math.random()*60) }) },
    { i:'💎', t:'Staking: +{n} LKC deposited', get: () => ({ n: 100+Math.floor(Math.random()*2000) }) },
    { i:'🌐', t:'Peer connected: {n} active', get: () => ({ n: 4200+Math.floor(Math.random()*30) }) },
  ];
  const feed = document.getElementById('activityFeed');
  setInterval(() => {
    if (state.paused || !feed) return;
    const e = events[Math.floor(Math.random()*events.length)];
    const vars = e.get();
    let text = e.t;
    Object.keys(vars).forEach(k => text = text.replace('{'+k+'}', vars[k]));
    const li = document.createElement('li');
    li.className = 'feed-item';
    const time = new Date().toLocaleTimeString('en-GB');
    li.innerHTML = `<span class="t">${time}</span><span class="b">${e.i}</span><span>${text}</span>`;
    feed.insertBefore(li, feed.firstChild);
    if (feed.children.length > 30) feed.removeChild(feed.lastChild);
  }, 3000);
  document.getElementById('pauseFeed')?.addEventListener('click', e => {
    state.paused = !state.paused;
    e.target.textContent = state.paused ? '▶' : '⏸';
  });
}

// ---------- ACTIONS ----------
function initActions() {
  document.getElementById('connectBtn')?.addEventListener('click', () => toast('🔌 Wallet connection initiated (demo)'));
  document.getElementById('evolveBtn')?.addEventListener('click', () => {
    const tier = document.getElementById('dnaTier');
    const cur = tier.textContent;
    const n = parseInt(cur.slice(1)) + 1;
    tier.textContent = 'T' + n;
    const gen = document.getElementById('dnaGen');
    gen.textContent = (parseInt(gen.textContent) + 1);
    toast('🧬 Evolution complete! → T' + n);
  });
  document.getElementById('menuBtn')?.addEventListener('click', () => {
    document.getElementById('navLinks').classList.toggle('open');
  });
}

function toast(msg) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}

// ============================================================
// COSMIC UI v3 — MODERN COMPONENTS (Qalam, 2025)
// ============================================================

// ---------- THEME MANAGER ----------
const ThemeManager = (() => {
  const KEY = 'laniakea-theme';
  const valid = ['cosmic', 'dark', 'light'];

  function get() {
    const stored = localStorage.getItem(KEY);
    if (stored && valid.includes(stored)) return stored;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'cosmic';
  }
  function set(theme) {
    if (!valid.includes(theme)) theme = 'cosmic';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(KEY, theme);
    document.dispatchEvent(new CustomEvent('theme:change', { detail: { theme } }));
  }
  function cycle() {
    const cur = get();
    const next = valid[(valid.indexOf(cur) + 1) % valid.length];
    set(next);
    return next;
  }
  function init() {
    set(get());
    // Listen to system changes when user hasn't set manually
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', e => {
      if (!localStorage.getItem(KEY)) set(e.matches ? 'light' : 'cosmic');
    });
  }
  return { get, set, cycle, init, valid };
})();

// ---------- TOAST SYSTEM ----------
const Toast = (() => {
  function ensure() {
    let host = document.querySelector('.toast-host');
    if (!host) {
      host = document.createElement('div');
      host.className = 'toast-host';
      document.body.appendChild(host);
    }
    return host;
  }
  function show(msg, type = 'info', duration = 4000) {
    const host = ensure();
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    const icons = { success: '✓', error: '✕', warn: '⚠', info: 'ℹ' };
    el.innerHTML = `<span style="font-size:18px">${icons[type] || 'ℹ'}</span><span>${msg}</span>`;
    host.appendChild(el);
    setTimeout(() => {
      el.classList.add('fadeout');
      setTimeout(() => el.remove(), 300);
    }, duration);
    return el;
  }
  return {
    show,
    success: (m, d) => show(m, 'success', d),
    error: (m, d) => show(m, 'error', d),
    warn: (m, d) => show(m, 'warn', d),
    info: (m, d) => show(m, 'info', d),
  };
})();

// ---------- MODAL ----------
const Modal = (() => {
  function open(title, content, opts = {}) {
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    const m = document.createElement('div');
    m.className = 'modal';
    m.innerHTML = `
      <div class="flex items-center justify-between mb-4">
        <h3 style="font-size:18px;font-weight:600;color:var(--ink-0)">${title}</h3>
        <button class="icon-btn modal-close">✕</button>
      </div>
      <div class="modal-body">${content}</div>
      ${opts.actions ? `<div class="flex gap-2 mt-6 justify-end">${opts.actions}</div>` : ''}
    `;
    backdrop.appendChild(m);
    document.body.appendChild(backdrop);
    function close() { backdrop.style.animation = 'fadeIn 0.2s reverse'; setTimeout(() => backdrop.remove(), 200); }
    m.querySelector('.modal-close').onclick = close;
    backdrop.onclick = e => { if (e.target === backdrop) close(); };
    document.addEventListener('keydown', function esc(e) {
      if (e.key === 'Escape') { close(); document.removeEventListener('keydown', esc); }
    });
    return { close, el: m };
  }
  function confirm(msg, onYes, onNo) {
    const m = open('تأیید', `<p>${msg}</p>`, {
      actions: `
        <button class="btn-ghost" data-act="no">انصراف</button>
        <button class="btn-primary" data-act="yes">تأیید</button>
      `
    });
    m.el.querySelector('[data-act="yes"]').onclick = () => { onYes?.(); m.close(); };
    m.el.querySelector('[data-act="no"]').onclick = () => { onNo?.(); m.close(); };
    return m;
  }
  return { open, confirm };
})();

// ---------- API CLIENT ----------
const API_CLIENT = (() => {
  const BASE = window.LANIAKEA_API || (location.origin.replace(/\/$/, ''));
  let token = localStorage.getItem('laniakea-token');

  async function request(path, opts = {}) {
    const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
    if (token) headers['Authorization'] = `Bearer ${token}`;
    try {
      const res = await fetch(`${BASE}${path}`, { ...opts, headers });
      const ct = res.headers.get('content-type') || '';
      const data = ct.includes('json') ? await res.json() : await res.text();
      if (!res.ok) throw Object.assign(new Error(data.detail || res.statusText), { status: res.status, data });
      return data;
    } catch (e) {
      if (e.status !== 401) Toast.error(`API ${e.status || 'ERR'}: ${e.message || path}`);
      throw e;
    }
  }
  function setToken(t) {
    token = t;
    if (t) localStorage.setItem('laniakea-token', t);
    else localStorage.removeItem('laniakea-token');
  }
  return {
    get: (p) => request(p),
    post: (p, body) => request(p, { method: 'POST', body: JSON.stringify(body) }),
    put:  (p, body) => request(p, { method: 'PUT',  body: JSON.stringify(body) }),
    del:  (p) => request(p, { method: 'DELETE' }),
    setToken,
    BASE,
  };
})();

// ---------- LIVE CLOCK ----------
const LiveClock = (() => {
  function start() {
    const el = document.getElementById('liveClock');
    if (!el) return;
    function tick() {
      const now = new Date();
      el.textContent = now.toLocaleTimeString('en-GB', { hour12: false });
    }
    tick();
    setInterval(tick, 1000);
  }
  return { start };
})();

// ---------- 3D HYPERCUBE (Three.js) ----------
const Hypercube3D = (() => {
  let scene, camera, renderer, cube, animationId;

  function init(container) {
    if (typeof THREE === 'undefined') return null;
    const w = container.clientWidth, h = container.clientHeight || 320;
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 1000);
    camera.position.set(3, 2, 4);
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(w, h);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // 8 vertices of hypercube projected to 3D
    const verts = [];
    for (let i = 0; i < 8; i++) {
      verts.push(new THREE.Vector3(
        (i & 1) ? 1 : -1, (i & 2) ? 1 : -1, (i & 4) ? 1 : -1
      ));
    }
    const geo = new THREE.BufferGeometry().setFromPoints(verts);
    const edges = [
      [0,1],[1,3],[3,2],[2,0],[4,5],[5,7],[7,6],[6,4],
      [0,4],[1,5],[2,6],[3,7]
    ];
    const positions = [];
    edges.forEach(([a, b]) => {
      positions.push(verts[a].x, verts[a].y, verts[a].z);
      positions.push(verts[b].x, verts[b].y, verts[b].z);
    });
    const lineGeo = new THREE.BufferGeometry();
    lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    const mat = new THREE.LineBasicMaterial({ color: 0x7c3aed, transparent: true, opacity: 0.9 });
    cube = new THREE.LineSegments(lineGeo, mat);
    scene.add(cube);

    // Inner vertices (pulsing)
    verts.forEach(v => {
      const sphere = new THREE.Mesh(
        new THREE.SphereGeometry(0.06, 16, 16),
        new THREE.MeshBasicMaterial({ color: 0x06b6d4 })
      );
      sphere.position.copy(v);
      scene.add(sphere);
    });

    // Soft lights
    scene.add(new THREE.AmbientLight(0xffffff, 0.6));
    const point = new THREE.PointLight(0xec4899, 1.2, 10);
    point.position.set(3, 3, 3);
    scene.add(point);

    function animate() {
      animationId = requestAnimationFrame(animate);
      cube.rotation.x += 0.0035;
      cube.rotation.y += 0.005;
      renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
      const nw = container.clientWidth, nh = container.clientHeight || 320;
      camera.aspect = nw / nh;
      camera.updateProjectionMatrix();
      renderer.setSize(nw, nh);
    });
    return renderer.domElement;
  }
  function destroy() {
    if (animationId) cancelAnimationFrame(animationId);
    if (renderer) { renderer.dispose(); renderer.domElement.remove(); }
  }
  return { init, destroy };
})();

// ---------- ROUTER (hash-based, modern) ----------
const Router = (() => {
  const routes = new Map();
  let current = null;

  function on(path, handler) { routes.set(path, handler); }
  function go(path) {
    if (location.hash !== `#${path}`) location.hash = path;
    else dispatch(path);
  }
  function dispatch(path) {
    const handler = routes.get(path) || routes.get('/');
    if (handler) {
      if (current && routes.get(current)?.deactivate) routes.get(current).deactivate();
      current = path;
      handler(path);
      document.querySelectorAll('[data-route]').forEach(el => {
        el.classList.toggle('active', el.dataset.route === path);
      });
    }
  }
  function start() {
    window.addEventListener('hashchange', () => dispatch(location.hash.slice(1) || '/'));
    dispatch(location.hash.slice(1) || '/');
  }
  return { on, go, start, current: () => current };
})();

// ---------- PARTICLE FIELD (canvas-based) ----------
const ParticleField = (() => {
  function init(canvas) {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let w, h, particles;
    function resize() {
      w = canvas.width = canvas.clientWidth;
      h = canvas.height = canvas.clientHeight;
      particles = Array.from({ length: Math.min(80, Math.floor(w * h / 15000)) }, () => ({
        x: Math.random() * w, y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.3, vy: (Math.random() - 0.5) * 0.3,
        r: Math.random() * 1.5 + 0.5,
      }));
    }
    resize();
    window.addEventListener('resize', resize);
    function step() {
      ctx.clearRect(0, 0, w, h);
      const theme = document.documentElement.getAttribute('data-theme');
      const isLight = theme === 'light';
      particles.forEach(p => {
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > w) p.vx *= -1;
        if (p.y < 0 || p.y > h) p.vy *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = isLight ? 'rgba(124, 58, 237, 0.4)' : 'rgba(124, 58, 237, 0.6)';
        ctx.fill();
      });
      requestAnimationFrame(step);
    }
    step();
  }
  return { init };
})();

// ---------- BOOT ----------
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  LiveClock.start();
  document.addEventListener('theme:change', e => {
    Toast.info(`Theme: ${e.detail.theme}`);
  });
  // Bind theme toggle if exists
  document.querySelectorAll('[data-action="theme-cycle"]').forEach(btn => {
    btn.onclick = () => { ThemeManager.cycle(); };
  });
});

// Expose to window
window.Cosmic = { ThemeManager, Toast, Modal, API_CLIENT, LiveClock, Hypercube3D, Router, ParticleField };
