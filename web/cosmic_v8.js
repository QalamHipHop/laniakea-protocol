/* ════════════════════════════════════════════════════════════════════════════
   LaniakeA · 8D Cosmic Engine v8 · Frontend Logic
   Author: Qalam · Network: mainnet
   ════════════════════════════════════════════════════════════════════════════ */
import * as THREE from 'three';

const API = ''; // same origin
const $ = (s, p=document) => p.querySelector(s);
const $$ = (s, p=document) => Array.from(p.querySelectorAll(s));

/* ─── TAB SWITCHING ───────────────────────────────────────────────────────── */
$$('.lk-nav__item[data-tab]').forEach(it => {
  it.addEventListener('click', e => {
    e.preventDefault();
    const tab = it.dataset.tab;
    $$('.lk-nav__item').forEach(x => x.classList.remove('active'));
    it.classList.add('active');
    $$('.lk-tab').forEach(x => x.classList.remove('active'));
    const t = $('#tab-' + tab);
    if (t) t.classList.add('active');
    if (location.hash !== '#' + tab) history.replaceState(null, '', '#' + tab);
  });
});
// restore tab from hash
const initialTab = (location.hash || '#overview').slice(1);
const initialItem = $(`.lk-nav__item[data-tab="${initialTab}"]`);
if (initialItem) initialItem.click();

/* ─── MOBILE MENU ─────────────────────────────────────────────────────────── */
$('#lk-btn-menu')?.addEventListener('click', () => {
  $('#lk-sidebar')?.classList.toggle('open');
  $('#lk-backdrop')?.classList.toggle('open');
});
$('#lk-backdrop')?.addEventListener('click', () => {
  $('#lk-sidebar')?.classList.remove('open');
  $('#lk-backdrop')?.classList.remove('open');
});

/* ─── API HELPERS ─────────────────────────────────────────────────────────── */
async function api(path, opts={}) {
  try {
    const r = await fetch(API + path, { headers: { 'Content-Type': 'application/json' }, ...opts });
    if (!r.ok) throw new Error(r.statusText);
    return await r.json();
  } catch (e) { console.warn('API', path, e); return null; }
}
const safe = (v, d='—') => (v===null||v===undefined||v==='—') ? d : v;
const fmt = (n) => {
  if (n===null||n===undefined) return '—';
  if (typeof n !== 'number') return String(n);
  if (n >= 1e9) return (n/1e9).toFixed(2) + 'B';
  if (n >= 1e6) return (n/1e6).toFixed(2) + 'M';
  if (n >= 1e3) return (n/1e3).toFixed(2) + 'K';
  return n.toFixed(2);
};

/* ─── CONNECTION STATUS ───────────────────────────────────────────────────── */
function setStatus(state, text) {
  const dot = $('.lk-netbar__dot'); if (dot) dot.dataset.state = state;
  const t = $('#lk-nb-status-text'); if (t) t.textContent = text;
  const p = $('#lk-pill-conn'); if (p) { p.dataset.state = state; p.textContent = '● ' + text; }
}

/* ─── METRICS LOADER ──────────────────────────────────────────────────────── */
async function loadOverview() {
  const data = await api('/');
  if (!data) { setStatus('off', 'offline'); return; }
  setStatus('on', 'live');
  $('#m-subsys').textContent = safe(data.subsystems ? Object.values(data.subsystems).filter(Boolean).length : '—');
  $('#m-routes').textContent = '170+';
  $('#m-blocks').textContent = safe(data.block_height ?? data.blocks ?? '—', '0');
  $('#m-validators').textContent = safe(data.validators ?? '—');
  $('#m-aiperf').textContent = safe(data.ai_perf ?? '0.92');
  $('#m-uptime').textContent = safe(data.uptime ?? '—');
  $('#lk-nb-version').textContent = safe(data.version, 'v6.3.0-Qalam');
  $('#lk-pill-version').textContent = safe(data.version, 'v—');
  $('#lk-pill-env').textContent = safe(data.environment, 'env —');
  $('#lk-pill-routes').textContent = '170+ routes';
  // token
  if (data.token) {
    $('#lk-t-sym').textContent = safe(data.token.symbol, 'LANA');
    $('#lk-t-name').textContent = safe(data.token.name, 'Laniakea');
    $('#lk-t-dec').textContent = safe(data.token.decimals, '18');
    $('#lk-t-sup').textContent = fmt(data.token.total_supply);
  }
  // subsystems grid
  const sg = $('#lk-ss-grid');
  if (sg && data.subsystems) {
    sg.innerHTML = Object.entries(data.subsystems).map(([k, v]) =>
      `<div class="lk-ss"><span class="lk-ss__dot ${v?'':'lk-ss__dot--off'}"></span><span class="lk-ss__name">${k}</span></div>`
    ).join('');
  }
}
async function loadScda() {
  const [identities, leaderboard] = await Promise.all([api('/scda/identities'), api('/scda/leaderboard')]);
  const list = $('#lk-scda-list');
  if (list && identities) {
    const items = (Array.isArray(identities) ? identities : identities.items || identities.identities || []).slice(0, 30);
    list.innerHTML = items.length ? items.map(s => `
      <div class="lk-scda">
        <span class="lk-scda__id">${s.id || s.identity || s.name || JSON.stringify(s).slice(0,24)}</span>
        <span class="lk-scda__fit">${fmt(s.fitness ?? s.score ?? 0)}</span>
      </div>`).join('') : '<div style="color:var(--t-muted);font-size:12px;padding:8px">No SCDAs yet</div>';
    $('#lk-scda-sub').textContent = `${items.length} digital organisms`;
    $('#m-scda').textContent = items.length;
    $('#lk-nb-scda').textContent = items.length;
  }
  const lb = $('#lk-scda-leaderboard');
  if (lb && leaderboard) {
    const arr = (Array.isArray(leaderboard) ? leaderboard : leaderboard.items || []).slice(0, 10);
    lb.innerHTML = arr.length ? arr.map((s, i) => `
      <div class="lk-lb-row">
        <span class="lk-lb-row__rank ${i<3?'lk-lb-row__rank--top':''}">#${i+1}</span>
        <span class="lk-lb-row__id">${s.id || s.identity || '—'}</span>
        <span class="lk-lb-row__fit">${fmt(s.fitness ?? 0)}</span>
        <span class="lk-lb-row__gen">gen ${s.generation ?? '—'}</span>
      </div>`).join('') : '<div style="color:var(--t-muted);font-size:12px;padding:8px">No leaderboard data</div>';
  }
  // reputation tab
  const rep = $('#lk-rep-list');
  if (rep && leaderboard) {
    const arr = (Array.isArray(leaderboard) ? leaderboard : leaderboard.items || []).slice(0, 15);
    rep.innerHTML = arr.length ? arr.map((s, i) => `
      <div class="lk-lb-row">
        <span class="lk-lb-row__rank ${i<3?'lk-lb-row__rank--top':''}">#${i+1}</span>
        <span class="lk-lb-row__id">${s.id || s.identity || '—'}</span>
        <span class="lk-lb-row__fit">${fmt(s.reputation ?? s.fitness ?? 0)}</span>
        <span class="lk-lb-row__gen">gen ${s.generation ?? '—'}</span>
      </div>`).join('') : '<div style="color:var(--t-muted);font-size:12px;padding:8px">No reputation data</div>';
  }
}
async function loadProblems() {
  const data = await api('/llm/hard_problem');
  const list = (id) => {
    const el = $('#' + id); if (!el || !data) return;
    el.innerHTML = `
      <div class="lk-problem">
        <div class="lk-problem__eq">${data.equation || data.problem || JSON.stringify(data)}</div>
        <div class="lk-problem__meta">
          <span>id: ${data.id || '—'}</span>
          <span>difficulty: ${data.difficulty ?? '—'}</span>
          <span>domain: ${data.domain ?? '—'}</span>
        </div>
      </div>`;
  };
  list('lk-problems-list'); list('lk-problems-list-2');
}
async function loadChain() {
  const [info, cons, blocks] = await Promise.all([api('/blockchain/info'), api('/blockchain/consensus'), api('/blockchain/blocks')]);
  const fill = (elId, data) => {
    const el = $('#' + elId); if (!el || !data) return;
    el.innerHTML = Object.entries(data).slice(0, 8).map(([k, v]) =>
      `<div class="lk-kv"><span>${k}</span><strong>${typeof v === 'object' ? JSON.stringify(v).slice(0,30) : v}</strong></div>`
    ).join('');
  };
  fill('lk-chain-info', info); fill('lk-consensus-info', cons);
  const bl = $('#lk-blocks-list');
  if (bl && blocks) {
    const arr = (Array.isArray(blocks) ? blocks : blocks.items || []).slice(0, 15);
    bl.innerHTML = arr.length ? arr.map(b => `
      <div class="lk-block">
        <span class="lk-block__h">#${b.height ?? b.index ?? '—'}</span>
        <span class="lk-block__hash">${(b.hash || b.id || '').toString().slice(0, 32)}</span>
        <span class="lk-block__meta">${b.txs ?? b.tx_count ?? 0} txs</span>
        <span class="lk-block__meta">${b.validator ?? '—'}</span>
        <span class="lk-block__meta">${b.time ?? ''}</span>
      </div>`).join('') : '<div style="color:var(--t-muted);padding:8px">No blocks</div>';
  }
}
async function loadGov() {
  const data = await api('/governance/proposals');
  const el = $('#lk-gov-list'); if (!el || !data) return;
  const arr = (Array.isArray(data) ? data : data.items || []).slice(0, 20);
  el.innerHTML = arr.length ? arr.map(p => `
    <div class="lk-problem">
      <div class="lk-problem__eq">${p.title || p.id}</div>
      <div class="lk-problem__meta">
        <span>state: ${p.state ?? '—'}</span>
        <span>votes: ${fmt(p.votes ?? 0)}</span>
        <span>id: ${p.id ?? '—'}</span>
      </div>
    </div>`).join('') : '<div style="color:var(--t-muted);padding:8px">No proposals</div>';
}
async function loadDiplomacy() {
  const data = await api('/diplomacy/alliances');
  const el = $('#lk-dip-list'); if (!el || !data) return;
  const arr = (Array.isArray(data) ? data : data.items || []).slice(0, 20);
  el.innerHTML = arr.length ? arr.map(a => `
    <div class="lk-problem">
      <div class="lk-problem__eq">${a.name || a.id}</div>
      <div class="lk-problem__meta">
        <span>members: ${a.members?.length ?? a.size ?? '—'}</span>
        <span>rep: ${fmt(a.reputation ?? 0)}</span>
        <span>id: ${a.id ?? '—'}</span>
      </div>
    </div>`).join('') : '<div style="color:var(--t-muted);padding:8px">No alliances</div>';
}
async function loadKm() {
  const data = await api('/knowledge-market/listed');
  const el = $('#lk-km-list'); if (!el || !data) return;
  const arr = (Array.isArray(data) ? data : data.items || []).slice(0, 20);
  el.innerHTML = arr.length ? arr.map(k => `
    <div class="lk-problem">
      <div class="lk-problem__eq">${k.title || k.name || k.id}</div>
      <div class="lk-problem__meta">
        <span>type: ${k.type ?? '—'}</span>
        <span>price: ${fmt(k.price ?? 0)}</span>
        <span>id: ${k.id ?? '—'}</span>
      </div>
    </div>`).join('') : '<div style="color:var(--t-muted);padding:8px">No knowledge assets</div>';
}
async function loadDefi() {
  const [pools, stake] = await Promise.all([api('/defi/pools'), api('/defi/staking')]);
  const fill = (id, data) => {
    const el = $('#' + id); if (!el || !data) return;
    const arr = (Array.isArray(data) ? data : data.items || [data]).slice(0, 10);
    el.innerHTML = arr.map(p => `<div class="lk-kv"><span>${p.pair || p.name || p.id || JSON.stringify(p).slice(0,20)}</span><strong>${fmt(p.tvl ?? p.value ?? p.amount ?? 0)}</strong></div>`).join('');
  };
  fill('lk-defi-pools', pools); fill('lk-defi-staking', stake);
}
async function loadNft() {
  const data = await api('/marketplace/nfts');
  const el = $('#lk-nft-list'); if (!el || !data) return;
  const arr = (Array.isArray(data) ? data : data.items || []).slice(0, 20);
  el.innerHTML = arr.length ? arr.map(n => `
    <div class="lk-problem">
      <div class="lk-problem__eq">${n.name || n.title || n.id}</div>
      <div class="lk-problem__meta">
        <span>owner: ${(n.owner || '').toString().slice(0,16)}</span>
        <span>price: ${fmt(n.price ?? 0)}</span>
        <span>id: ${n.id ?? '—'}</span>
      </div>
    </div>`).join('') : '<div style="color:var(--t-muted);padding:8px">No NFTs</div>';
}
async function loadCrossChain() {
  const data = await api('/crosschain/networks');
  const el = $('#lk-cc-list'); if (!el || !data) return;
  const arr = (Array.isArray(data) ? data : data.items || []);
  el.innerHTML = arr.map(c => `
    <div class="lk-chain">
      <span class="lk-chain__dot lk-chain__dot--${(c.name||'eth').toLowerCase().slice(0,4)}"></span>
      <span class="lk-chain__name">${c.name || c.chain || c.id}</span>
      <span class="lk-chain__status">${c.status || c.state || 'live'}</span>
    </div>`).join('');
}
async function loadQuantum() {
  const data = await api('/quantum/queue');
  const el = $('#lk-q-queue'); if (!el || !data) return;
  const arr = (Array.isArray(data) ? data : data.items || []).slice(0, 20);
  el.innerHTML = arr.length ? arr.map(q => `
    <div class="lk-problem">
      <div class="lk-problem__eq">${q.circuit || q.id || 'job'}</div>
      <div class="lk-problem__meta">
        <span>state: ${q.state ?? '—'}</span>
        <span>shots: ${q.shots ?? '—'}</span>
      </div>
    </div>`).join('') : '<div style="color:var(--t-muted);padding:8px">Queue empty</div>';
}
async function loadAchievements() {
  const data = await api('/achievements');
  const el = $('#lk-ach-list'); if (!el || !data) return;
  const arr = (Array.isArray(data) ? data : data.items || []).slice(0, 20);
  el.innerHTML = arr.length ? arr.map(a => `
    <div class="lk-problem">
      <div class="lk-problem__eq">★ ${a.name || a.title || a.id}</div>
      <div class="lk-problem__meta">
        <span>rarity: ${a.rarity ?? '—'}</span>
        <span>unlocked: ${a.unlocked ?? '—'}</span>
      </div>
    </div>`).join('') : '<div style="color:var(--t-muted);padding:8px">No achievements</div>';
}
async function loadSocial() {
  const data = await api('/social/posts');
  const el = $('#lk-soc-list'); if (!el || !data) return;
  const arr = (Array.isArray(data) ? data : data.items || []).slice(0, 20);
  el.innerHTML = arr.length ? arr.map(p => `
    <div class="lk-problem">
      <div class="lk-problem__eq">${(p.text || p.content || '').toString().slice(0, 80)}</div>
      <div class="lk-problem__meta">
        <span>by: ${(p.author || p.user || '—').toString().slice(0,16)}</span>
        <span>♥ ${fmt(p.likes ?? 0)}</span>
      </div>
    </div>`).join('') : '<div style="color:var(--t-muted);padding:8px">No posts</div>';
}
async function loadMining() {
  const data = await api('/mining/status');
  const el = $('#lk-mine-list'); if (!el || !data) return;
  el.innerHTML = Object.entries(data).slice(0, 12).map(([k, v]) =>
    `<div class="lk-kv"><span>${k}</span><strong>${typeof v === 'object' ? JSON.stringify(v).slice(0,30) : v}</strong></div>`
  ).join('');
}
async function loadSimState() {
  const data = await api('/simulation/state');
  const el = $('#lk-sim-state'); if (!el || !data) return;
  el.innerHTML = Object.entries(data).slice(0, 14).map(([k, v]) =>
    `<div class="lk-kv"><span>${k}</span><strong>${typeof v === 'object' ? JSON.stringify(v).slice(0,30) : v}</strong></div>`
  ).join('');
}

/* ─── ACTIONS ─────────────────────────────────────────────────────────────── */
async function runAction(name) {
  const map = {
    solve: { method: 'POST', path: '/llm/hard_problem', body: {} },
    evaluate: { method: 'POST', path: '/llm/evaluate', body: { expression: 'sin(x)^2 + cos(x)^2' } },
    predict: { method: 'POST', path: '/scda/predict', body: {} },
    breed: { method: 'POST', path: '/scda/breed', body: {} },
    quantum: { method: 'POST', path: '/quantum/submit', body: { circuit: 'bell', shots: 100 } },
    tokenize: { method: 'POST', path: '/knowledge-market/tokenize', body: { title: 'Sample', type: 'doc' } },
    alliance: { method: 'POST', path: '/diplomacy/alliances', body: { name: 'New Alliance' } },
    propose: { method: 'POST', path: '/governance/proposals', body: { title: 'New proposal' } },
    mint: { method: 'POST', path: '/marketplace/mint', body: { name: 'Cosmic NFT' } },
    simulate: { method: 'POST', path: '/simulation/step', body: { steps: 1 } },
  };
  const cfg = map[name]; if (!cfg) return;
  const out = $('#lk-action-output'); out.hidden = false;
  $('#lk-action-out-title').textContent = '⚡ ' + name;
  $('#lk-action-out-time').textContent = new Date().toLocaleTimeString();
  $('#lk-action-out-body').textContent = '… working …';
  const res = await api(cfg.path, { method: cfg.method, body: JSON.stringify(cfg.body) });
  $('#lk-action-out-body').textContent = res ? JSON.stringify(res, null, 2) : '⚠ request failed';
}
$$('.lk-action').forEach(b => b.addEventListener('click', () => runAction(b.dataset.action)));
$('#lk-btn-actions-clear')?.addEventListener('click', () => $('#lk-action-output').hidden = true);
$('#lk-action-out-close')?.addEventListener('click', () => $('#lk-action-output').hidden = true);

/* ─── FORM ACTIONS ────────────────────────────────────────────────────────── */
$('#lk-btn-ai-query')?.addEventListener('click', async () => {
  const prompt = $('#lk-ai-prompt').value;
  const max_tokens = parseInt($('#lk-ai-tokens').value, 10);
  const r = $('#lk-ai-result'); r.hidden = false;
  $('#lk-ai-result-body').textContent = '… generating …';
  const res = await api('/llm/generate', { method: 'POST', body: JSON.stringify({ prompt, max_tokens }) });
  $('#lk-ai-result-body').textContent = res?.text || res?.output || res?.response || JSON.stringify(res, null, 2);
});
$('#lk-btn-mine')?.addEventListener('click', async () => {
  const out = $('#lk-mine-result'); out.hidden = false; out.textContent = '… mining …';
  const res = await api('/blockchain/mine', { method: 'POST', body: '{}' });
  out.textContent = JSON.stringify(res, null, 2);
});
$('#lk-btn-cc-init')?.addEventListener('click', async () => {
  const r = $('#lk-cc-result'); r.hidden = false;
  $('#lk-cc-result-body').textContent = '… initiating …';
  const res = await api('/crosschain/transfer', { method: 'POST', body: JSON.stringify({
    from: $('#lk-cc-from').value, to: $('#lk-cc-to').value,
    amount: parseFloat($('#lk-cc-amount').value)
  })});
  $('#lk-cc-result-body').textContent = JSON.stringify(res, null, 2);
});
$('#lk-btn-q-submit')?.addEventListener('click', async () => {
  const r = $('#lk-q-result'); r.hidden = false;
  $('#lk-q-result-body').textContent = '… submitting …';
  const res = await api('/quantum/submit', { method: 'POST', body: JSON.stringify({
    circuit: $('#lk-q-circuit').value, shots: parseInt($('#lk-q-shots').value, 10)
  })});
  $('#lk-q-result-body').textContent = JSON.stringify(res, null, 2);
});
$('#lk-btn-defi-swap')?.addEventListener('click', async () => {
  const r = $('#lk-defi-result'); r.hidden = false;
  $('#lk-defi-result-body').textContent = '… quoting …';
  const res = await api('/defi/swap', { method: 'POST', body: JSON.stringify({
    from: $('#lk-defi-from').value, to: $('#lk-defi-to').value, amount: parseFloat($('#lk-defi-amount').value)
  })});
  $('#lk-defi-result-body').textContent = JSON.stringify(res, null, 2);
});
$('#lk-btn-km-tokenize')?.addEventListener('click', async () => {
  const r = $('#lk-km-result'); r.hidden = false;
  $('#lk-km-result-body').textContent = '… tokenizing …';
  const res = await api('/knowledge-market/tokenize', { method: 'POST', body: JSON.stringify({
    title: $('#lk-km-title').value, type: $('#lk-km-type').value, description: $('#lk-km-desc').value
  })});
  $('#lk-km-result-body').textContent = JSON.stringify(res, null, 2);
});
$('#lk-btn-gov-propose')?.addEventListener('click', async () => {
  const r = $('#lk-gov-result'); r.hidden = false;
  $('#lk-gov-result-body').textContent = '… submitting …';
  const res = await api('/governance/proposals', { method: 'POST', body: JSON.stringify({
    title: $('#lk-gov-title').value, description: $('#lk-gov-desc').value
  })});
  $('#lk-gov-result-body').textContent = JSON.stringify(res, null, 2);
});
$('#lk-btn-dip-form')?.addEventListener('click', async () => {
  const r = $('#lk-dip-result'); r.hidden = false;
  $('#lk-dip-result-body').textContent = '… forming …';
  const members = $('#lk-dip-members').value.split(',').map(s => s.trim()).filter(Boolean);
  const res = await api('/diplomacy/alliances', { method: 'POST', body: JSON.stringify({
    name: $('#lk-dip-name').value, members
  })});
  $('#lk-dip-result-body').textContent = JSON.stringify(res, null, 2);
});
$('#lk-btn-sim-run')?.addEventListener('click', async () => {
  const r = $('#lk-sim-result'); r.hidden = false;
  $('#lk-sim-result-body').textContent = '… simulating …';
  const res = await api('/simulation/step', { method: 'POST', body: JSON.stringify({ steps: parseInt($('#lk-sim-steps').value, 10) })});
  $('#lk-sim-result-body').textContent = JSON.stringify(res, null, 2);
});
$('#lk-btn-reload-blocks')?.addEventListener('click', loadChain);
$('#lk-btn-refresh')?.addEventListener('click', () => location.reload());

/* ─── 8D HYPERCUBE WEBGL ──────────────────────────────────────────────────── */
function buildHypercube(canvas, opts={}) {
  if (!canvas) return null;
  const scene = new THREE.Scene();
  const cam = opts.orthographic
    ? new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 100)
    : new THREE.PerspectiveCamera(60, 1, 0.1, 100);
  cam.position.set(0, 0, 3.2);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  // hypercube vertices: 2^8 = 256
  const verts = [];
  for (let i = 0; i < 256; i++) {
    const v = [];
    for (let b = 0; b < 8; b++) v.push(((i >> b) & 1) ? 1 : -1);
    verts.push(v);
  }
  // edges connect vertices differing in 1 bit
  const lines = [];
  for (let i = 0; i < 256; i++) {
    for (let b = 0; b < 8; b++) {
      const j = i ^ (1 << b);
      if (j > i) {
        const colors = [
          new THREE.Color(0x00ffe0), new THREE.Color(0x00c4ff),
          new THREE.Color(0x7c3aed), new THREE.Color(0xb14bff),
          new THREE.Color(0xff3d8a), new THREE.Color(0xffb547)
        ];
        const col = colors[b % colors.length];
        lines.push({ a: verts[i], b: verts[j], c: col });
      }
    }
  }
  // project: 8D → 3D via rotation in 8D then drop dims
  const rot = Array.from({length: 8}, () => Array(8).fill(0).map((_,j) => j===Array.from({length:8}).indexOf(0) ? 1 : 0));
  // simpler: 4 plane rotations
  const angles = [0.4, 0.6, 0.5, 0.3, 0.7, 0.2, 0.5, 0.6].map(a => a * 0.01);
  function project(p8, t) {
    const r = p8.slice();
    for (let k = 0; k < 4; k++) {
      const i = k * 2, j = i + 1;
      const c = Math.cos(t * angles[k]), s = Math.sin(t * angles[k]);
      const ri = r[i], rj = r[j];
      r[i] = ri * c - rj * s; r[j] = ri * s + rj * c;
    }
    return [r[0] + r[4]*0.4, r[1] + r[5]*0.4, r[2] + r[6]*0.4 + r[3]*0.2 + r[7]*0.1];
  }
  // geometry
  const positions = new Float32Array(lines.length * 2 * 3);
  const colors = new Float32Array(lines.length * 2 * 3);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const mat = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.9 });
  const mesh = new THREE.LineSegments(geo, mat);
  scene.add(mesh);
  // vertex points
  const ptGeo = new THREE.BufferGeometry();
  const ptPos = new Float32Array(256 * 3);
  ptGeo.setAttribute('position', new THREE.BufferAttribute(ptPos, 3));
  const ptMat = new THREE.PointsMaterial({ color: 0x00ffe0, size: 0.025, transparent: true, opacity: 0.9 });
  const pts = new THREE.Points(ptGeo, ptMat);
  scene.add(pts);
  let autoRotate = true, speed = 0.4, t = 0, fps = 0, last = performance.now(), frames = 0;
  function resize() {
    const r = canvas.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    renderer.setSize(r.width, r.height, false);
    if (cam.isPerspectiveCamera) cam.aspect = r.width / r.height, cam.updateProjectionMatrix();
  }
  resize(); window.addEventListener('resize', resize);
  function loop() {
    requestAnimationFrame(loop);
    const now = performance.now();
    if (autoRotate) t += 0.016 * speed;
    const pos = geo.attributes.position.array;
    const col = geo.attributes.color.array;
    for (let i = 0; i < lines.length; i++) {
      const a = project(lines[i].a, t);
      const b = project(lines[i].b, t);
      pos[i*6+0]=a[0]*0.8; pos[i*6+1]=a[1]*0.8; pos[i*6+2]=a[2]*0.5;
      pos[i*6+3]=b[0]*0.8; pos[i*6+4]=b[1]*0.8; pos[i*6+5]=b[2]*0.5;
      const c = lines[i].c;
      for (let k = 0; k < 6; k += 3) { col[i*6+k]=c.r; col[i*6+k+1]=c.g; col[i*6+k+2]=c.b; }
    }
    geo.attributes.position.needsUpdate = true;
    const pp = ptGeo.attributes.position.array;
    for (let i = 0; i < 256; i++) {
      const p = project(verts[i], t);
      pp[i*3]=p[0]*0.8; pp[i*3+1]=p[1]*0.8; pp[i*3+2]=p[2]*0.5;
    }
    ptGeo.attributes.position.needsUpdate = true;
    renderer.render(scene, cam);
    frames++;
    if (now - last > 1000) { fps = frames; frames = 0; last = now; }
  }
  loop();
  return { setAutoRotate: v => autoRotate = v, setSpeed: v => speed = v / 25, getFps: () => fps };
}
const cube = buildHypercube($('#lk-cube-canvas'));
if (cube) {
  const fpsEl = $('#lk-cube-fps');
  setInterval(() => { if (fpsEl) fpsEl.textContent = cube.getFps(); }, 500);
}
const full = buildHypercube($('#lk-hc-full-canvas'));
if (full) {
  $('#lk-hc-autorotate')?.addEventListener('change', e => full.setAutoRotate(e.target.checked));
  $('#lk-hc-speed')?.addEventListener('input', e => full.setSpeed(parseInt(e.target.value, 10)));
  const fpsEl = $('#lk-hc-fps');
  setInterval(() => { if (fpsEl) fpsEl.textContent = full.getFps(); }, 500);
}
const mv = buildHypercube($('#lk-mv-canvas'));

/* ─── SCDA TREE CANVAS ────────────────────────────────────────────────────── */
function drawTree() {
  const c = $('#lk-tree-canvas'); if (!c) return;
  const r = c.getBoundingClientRect();
  if (r.width < 1) return;
  c.width = r.width; c.height = r.height;
  const ctx = c.getContext('2d');
  ctx.clearRect(0, 0, c.width, c.height);
  // simple branching tree
  const cx = c.width / 2, cy = c.height - 20;
  function branch(x, y, len, angle, depth) {
    if (depth > 7 || len < 2) return;
    const x2 = x + Math.cos(angle) * len;
    const y2 = y + Math.sin(angle) * len;
    ctx.strokeStyle = `hsla(${260 + depth * 12}, 80%, ${50 + depth*4}%, ${0.85 - depth*0.08})`;
    ctx.lineWidth = Math.max(0.5, 2 - depth * 0.25);
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x2, y2); ctx.stroke();
    if (depth < 3) {
      ctx.fillStyle = `hsla(${260 + depth * 12}, 90%, 70%, .9)`;
      ctx.beginPath(); ctx.arc(x2, y2, 3 - depth*0.3, 0, Math.PI*2); ctx.fill();
    }
    branch(x2, y2, len * 0.72, angle - 0.45, depth + 1);
    branch(x2, y2, len * 0.72, angle + 0.45, depth + 1);
  }
  branch(cx, cy, c.height * 0.28, -Math.PI / 2, 0);
  branch(cx * 0.4, cy, c.height * 0.18, -Math.PI / 2.2, 1);
  branch(cx * 1.6, cy, c.height * 0.18, -Math.PI / 1.8, 1);
}
setTimeout(drawTree, 100);
window.addEventListener('resize', drawTree);

/* ─── STARS BG CANVAS ─────────────────────────────────────────────────────── */
(function stars() {
  const c = $('#lk-bg-canvas'); if (!c) return;
  const ctx = c.getContext('2d');
  function resize() { c.width = innerWidth; c.height = innerHeight; }
  resize(); addEventListener('resize', resize);
  const S = Array.from({length: 180}, () => ({
    x: Math.random()*c.width, y: Math.random()*c.height,
    r: Math.random()*1.4 + 0.2,
    vx: (Math.random()-0.5)*0.04, vy: (Math.random()-0.5)*0.04,
    a: Math.random()*0.7 + 0.3
  }));
  (function loop() {
    requestAnimationFrame(loop);
    ctx.clearRect(0, 0, c.width, c.height);
    for (const s of S) {
      s.x += s.vx; s.y += s.vy;
      if (s.x < 0) s.x = c.width; if (s.x > c.width) s.x = 0;
      if (s.y < 0) s.y = c.height; if (s.y > c.height) s.y = 0;
      ctx.fillStyle = `rgba(${180+Math.random()*70}, ${200+Math.random()*55}, 255, ${s.a})`;
      ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI*2); ctx.fill();
    }
  })();
})();

/* ─── BOOT ────────────────────────────────────────────────────────────────── */
async function boot() {
  setStatus('off', 'connecting');
  await Promise.allSettled([
    loadOverview(), loadScda(), loadProblems(), loadChain(),
    loadGov(), loadDiplomacy(), loadKm(), loadDefi(), loadNft(),
    loadCrossChain(), loadQuantum(), loadAchievements(),
    loadSocial(), loadMining(), loadSimState()
  ]);
}
boot();
setInterval(loadOverview, 30000);
setInterval(loadScda, 60000);
