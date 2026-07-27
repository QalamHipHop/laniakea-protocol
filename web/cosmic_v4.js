// ============================================================
// 🌌 Laniakea v4 — Cosmic Dashboard JS
// Author: Qalam
// ============================================================

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

// --- Configuration ---------------------------------------------------
const API_BASE = window.location.origin;
const REFRESH_INTERVAL = 5000;
const MAX_FEED_ITEMS = 20;

// --- State ------------------------------------------------------------
const state = {
  online: false,
  hypercube: null,
  feedItems: [],
  scda: new Map(),
  projection: 'perspective',
};

// --- Helpers ----------------------------------------------------------
const $ = (id) => document.getElementById(id);
const fmt = (n) => {
  if (n === null || n === undefined) return '—';
  if (typeof n === 'number') {
    if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(2) + 'K';
    if (Number.isInteger(n)) return n.toString();
    return n.toFixed(3);
  }
  return String(n);
};
const short = (s, n = 12) => (s ? s.slice(0, n) + (s.length > n ? '…' : '') : '—');
const ago = (ts) => {
  const s = Math.floor((Date.now() - ts * 1000) / 1000);
  if (s < 60) return s + 's ago';
  if (s < 3600) return Math.floor(s / 60) + 'm ago';
  if (s < 86400) return Math.floor(s / 3600) + 'h ago';
  return Math.floor(s / 86400) + 'd ago';
};

// --- API client -------------------------------------------------------
async function api(path, opts = {}) {
  const r = await fetch(API_BASE + path, { cache: 'no-store', ...opts });
  if (!r.ok) throw new Error(`API ${path} → ${r.status}`);
  return r.json();
}

// --- Cosmic WebGL background ----------------------------------------
function initCosmicBackground() {
  const canvas = $('cosmic-canvas');
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.z = 60;

  // Star field
  const starCount = 2000;
  const positions = new Float32Array(starCount * 3);
  const colors = new Float32Array(starCount * 3);
  for (let i = 0; i < starCount; i++) {
    const r = 80 + Math.random() * 60;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos((Math.random() * 2) - 1);
    positions[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = r * Math.cos(phi);
    const hue = 0.55 + Math.random() * 0.25; // blue → purple
    const c = new THREE.Color().setHSL(hue, 0.7, 0.5 + Math.random() * 0.5);
    colors[i * 3]     = c.r;
    colors[i * 3 + 1] = c.g;
    colors[i * 3 + 2] = c.b;
  }
  const starGeo = new THREE.BufferGeometry();
  starGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  starGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const starMat = new THREE.PointsMaterial({ size: 0.4, vertexColors: true, transparent: true, opacity: 0.9 });
  const stars = new THREE.Points(starGeo, starMat);
  scene.add(stars);

  // Nebula clouds (additive)
  for (let i = 0; i < 4; i++) {
    const cloudGeo = new THREE.SphereGeometry(20 + Math.random() * 25, 16, 16);
    const cloudMat = new THREE.MeshBasicMaterial({
      color: new THREE.Color().setHSL(0.7 + Math.random() * 0.2, 0.6, 0.5),
      transparent: true,
      opacity: 0.04 + Math.random() * 0.05,
      depthWrite: false,
    });
    const cloud = new THREE.Mesh(cloudGeo, cloudMat);
    cloud.position.set((Math.random() - 0.5) * 80, (Math.random() - 0.5) * 60, -30 - Math.random() * 30);
    scene.add(cloud);
  }

  let mouseX = 0, mouseY = 0;
  document.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX / window.innerWidth) * 2 - 1;
    mouseY = (e.clientY / window.innerHeight) * 2 - 1;
  });

  function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }
  window.addEventListener('resize', onResize);

  function tick() {
    stars.rotation.y += 0.0002;
    stars.rotation.x += 0.0001;
    camera.position.x += (mouseX * 5 - camera.position.x) * 0.05;
    camera.position.y += (-mouseY * 5 - camera.position.y) * 0.05;
    camera.lookAt(scene.position);
    renderer.render(scene, camera);
    requestAnimationFrame(tick);
  }
  tick();
}

// --- Hypercube 3D projection -----------------------------------------
function initHypercube() {
  const canvas = $('hypercube-canvas');
  if (!canvas) return;
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100);
  camera.position.set(0, 0, 5);

  // Build 8D hypercube vertices and project to 3D
  const D = 8;
  const N = 2 ** D; // 256
  const verts8 = [];
  for (let i = 0; i < N; i++) {
    const v = [];
    for (let d = 0; d < D; d++) v.push(((i >> d) & 1) ? 0.5 : -0.5);
    verts8.push(v);
  }
  // 8D rotation matrix for animation
  function rot8D(a) {
    const m = Array.from({ length: D }, () => new Float32Array(D));
    for (let i = 0; i < D; i++) { m[i][i] = 1; }
    // rotate in planes (0,1), (2,3), (4,5), (6,7)
    const planes = [[0,1], [2,3], [4,5], [6,7]];
    for (const [i, j] of planes) {
      m[i][i] = Math.cos(a);  m[i][j] = -Math.sin(a);
      m[j][i] = Math.sin(a);  m[j][j] = Math.cos(a);
    }
    return m;
  }
  function project(verts8, m8, scale = 2) {
    return verts8.map((v) => {
      const r = new Array(D).fill(0);
      for (let i = 0; i < D; i++) for (let j = 0; j < D; j++) r[i] += m8[i][j] * v[j];
      // project 8D → 3D by averaging pairs
      const x = (r[0] + r[1]) * 0.7 + (r[2] - r[3]) * 0.3;
      const y = (r[4] + r[5]) * 0.7 + (r[6] - r[7]) * 0.3;
      const z = (r[0] - r[1]) * 0.5 + (r[2] + r[3]) * 0.2;
      return new THREE.Vector3(x * scale, y * scale, z * scale);
    });
  }
  // Edges: connect vertices differing in exactly one dimension
  const edges = [];
  for (let i = 0; i < N; i++) {
    for (let j = i + 1; j < N; j++) {
      let diff = 0;
      for (let d = 0; d < D; d++) if (verts8[i][d] !== verts8[j][d]) diff++;
      if (diff === 1) edges.push([i, j]);
    }
  }

  const group = new THREE.Group();
  scene.add(group);

  let t = 0;
  function rebuild(projMode) {
    while (group.children.length) group.remove(group.children[0]);
    const m8 = rot8D(t);
    const scale = projMode === 'stereo' ? 2.6 : projMode === 'orthographic' ? 1.8 : 2.2;
    const verts3 = project(verts8, m8, scale);

    // Edges
    const lineMat = new THREE.LineBasicMaterial({ color: 0x7c3aed, transparent: true, opacity: 0.4 });
    for (const [a, b] of edges) {
      const geo = new THREE.BufferGeometry().setFromPoints([verts3[a], verts3[b]]);
      group.add(new THREE.Line(geo, lineMat));
    }
    // Vertices
    const dotGeo = new THREE.SphereGeometry(0.05, 8, 8);
    verts3.forEach((p, i) => {
      const mat = new THREE.MeshBasicMaterial({ color: 0x06b6d4, transparent: true, opacity: 0.95 });
      const dot = new THREE.Mesh(dotGeo, mat);
      dot.position.copy(p);
      group.add(dot);
    });
    if (projMode === 'perspective') {
      // Add an outer "shell" of larger semi-transparent dots for depth
      const shellGeo = new THREE.SphereGeometry(0.08, 8, 8);
      verts3.forEach((p) => {
        const mat = new THREE.MeshBasicMaterial({ color: 0xec4899, transparent: true, opacity: 0.25 });
        const dot = new THREE.Mesh(shellGeo, mat);
        dot.position.copy(p);
        group.add(dot);
      });
    }
  }
  rebuild(state.projection);

  function fit() {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight || 320;
    if (canvas.width !== w || canvas.height !== h) {
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
  }
  window.addEventListener('resize', fit);

  // Chip controls
  document.querySelectorAll('.v4-chip[data-proj]').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.v4-chip[data-proj]').forEach((b) => b.classList.remove('is-active'));
      btn.classList.add('is-active');
      state.projection = btn.dataset.proj;
      rebuild(state.projection);
    });
  });

  function tick() {
    t += 0.005;
    fit();
    rebuild(state.projection);
    group.rotation.y += 0.002;
    group.rotation.x = Math.sin(t * 0.4) * 0.3;
    renderer.render(scene, camera);
    requestAnimationFrame(tick);
  }
  tick();
}

// --- DNA spectrum (8D knowledge vector radar) ------------------------
function initDNASpectrum() {
  const canvas = $('dna-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function fit() {
    const w = canvas.clientWidth;
    const h = canvas.clientHeight || 240;
    if (canvas.width !== w * 2 || canvas.height !== h * 2) {
      canvas.width = w * 2;
      canvas.height = h * 2;
      ctx.scale(2, 2);
    }
  }

  function draw(values) {
    fit();
    const w = canvas.clientWidth;
    const h = canvas.clientHeight || 240;
    ctx.clearRect(0, 0, w, h);

    const cx = w / 2;
    const cy = h / 2;
    const r = Math.min(w, h) * 0.35;
    const N = values.length;
    const labels = ['K', 'C', 'O', 'A', 'E', 'H', 'S', 'T'];

    // background rings
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    for (let i = 1; i <= 4; i++) {
      ctx.beginPath();
      ctx.arc(cx, cy, (r * i) / 4, 0, Math.PI * 2);
      ctx.stroke();
    }
    // axes
    for (let i = 0; i < N; i++) {
      const a = (i / N) * Math.PI * 2 - Math.PI / 2;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r);
      ctx.stroke();
    }
    // labels
    ctx.fillStyle = 'rgba(168,168,212,0.9)';
    ctx.font = '10px JetBrains Mono';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    for (let i = 0; i < N; i++) {
      const a = (i / N) * Math.PI * 2 - Math.PI / 2;
      const lx = cx + Math.cos(a) * (r + 14);
      const ly = cy + Math.sin(a) * (r + 14);
      ctx.fillText(labels[i], lx, ly);
    }
    // data polygon
    ctx.beginPath();
    for (let i = 0; i < N; i++) {
      const a = (i / N) * Math.PI * 2 - Math.PI / 2;
      const v = Math.max(0, Math.min(1, values[i]));
      const rr = r * v;
      const x = cx + Math.cos(a) * rr;
      const y = cy + Math.sin(a) * rr;
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.closePath();
    const grad = ctx.createLinearGradient(0, 0, w, h);
    grad.addColorStop(0, 'rgba(124, 58, 237, 0.55)');
    grad.addColorStop(0.5, 'rgba(6, 182, 212, 0.4)');
    grad.addColorStop(1, 'rgba(236, 72, 153, 0.5)');
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.strokeStyle = '#06b6d4';
    ctx.lineWidth = 2;
    ctx.stroke();
    // dots
    for (let i = 0; i < N; i++) {
      const a = (i / N) * Math.PI * 2 - Math.PI / 2;
      const v = Math.max(0, Math.min(1, values[i]));
      const rr = r * v;
      const x = cx + Math.cos(a) * rr;
      const y = cy + Math.sin(a) * rr;
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fillStyle = '#ec4899';
      ctx.fill();
    }
  }
  return { draw };
}

// --- Feed ------------------------------------------------------------
function addFeed(item) {
  state.feedItems.unshift({ ...item, ts: Date.now() / 1000 });
  if (state.feedItems.length > MAX_FEED_ITEMS) state.feedItems.pop();
  renderFeed();
}
function renderFeed() {
  const list = $('v4-feed');
  if (state.feedItems.length === 0) {
    list.innerHTML = '<li class="v4-feed-empty">awaiting the first signal from the void…</li>';
    $('v4-feed-count').textContent = '0 events';
    return;
  }
  list.innerHTML = state.feedItems.map((it) => `
    <li>
      <span class="v4-feed-icon ${it.kind}">${it.icon || '◆'}</span>
      <span class="v4-feed-text">${it.text}</span>
      <span class="v4-feed-time">${ago(it.ts)}</span>
    </li>
  `).join('');
  $('v4-feed-count').textContent = `${state.feedItems.length} event${state.feedItems.length > 1 ? 's' : ''}`;
}

// --- Leaderboard -----------------------------------------------------
function renderLeaderboard(scdas) {
  const ol = $('v4-leaderboard');
  if (!scdas || scdas.length === 0) {
    ol.innerHTML = '<li class="v4-leaderboard-empty">awaiting genesis SCDAs…</li>';
    return;
  }
  const maxC = Math.max(...scdas.map((s) => s.complexity_index || 0), 1);
  ol.innerHTML = scdas.slice(0, 10).map((s) => `
    <li>
      <div>
        <div class="v4-lb-name">${s.identity}</div>
        <div class="v4-lb-bar"><div class="v4-lb-bar-fill" style="width: ${((s.complexity_index || 0) / maxC * 100).toFixed(1)}%"></div></div>
      </div>
      <span class="v4-lb-c">C=${fmt(s.complexity_index || 0)}</span>
    </li>
  `).join('');
  if (scdas.length > 0) {
    $('v4-dna-target').textContent = scdas[0].identity;
    drawDNA(dnaVectorFor(scdas[0]));
  }
}

// --- Compute an 8D DNA vector for a SCDA (best-effort) ---------------
function dnaVectorFor(scda) {
  // Default: equal distribution so a new SCDA shows a regular octagon.
  const v = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5];
  if (scda.knowledge_vector_8d && Array.isArray(scda.knowledge_vector_8d)) {
    return scda.knowledge_vector_8d.map((x) => Math.max(0, Math.min(1, x)));
  }
  return v;
}

// --- Stats updater ---------------------------------------------------
function setStat(key, value, trend) {
  const el = document.querySelector(`.v4-stat[data-key="${key}"]`);
  if (!el) return;
  const v = el.querySelector('[data-value]');
  const t = el.querySelector('[data-trend]');
  v.textContent = value;
  if (trend) {
    t.textContent = trend.text;
    t.className = 'v4-stat-trend is-' + trend.dir;
  } else {
    t.textContent = '';
  }
}

let dna;
async function refresh() {
  try {
    const [status, leaderboard, version, overview] = await Promise.allSettled([
      api('/blockchain/info'),
      api('/scda/leaderboard'),
      api('/version'),
      api('/cosmic/overview'),
    ]);

    if (status.status === 'fulfilled') {
      const s = status.value;
      setStat('chain_length', fmt(s.chain_length || s.length || 1));
      setStat('total_transactions', fmt(s.total_transactions || 0));
      setStat('difficulty', fmt(s.difficulty || 1));
      setStat('consensus', s.consensus || 'PoHD', { text: '8D hypercube', dir: 'up' });
      $('v4-tel-last').textContent = ago(s.last_block_timestamp || Date.now() / 1000);
      $('v4-tel-hash').textContent = short(s.last_block_hash || '—', 16);
    } else {
      // fallback to /core/status
      try {
        const cs = await api('/core/status');
        setStat('chain_length', fmt(cs.chain_length || 1));
        setStat('total_transactions', fmt(cs.total_transactions || 0));
        setStat('difficulty', fmt(cs.difficulty || 1));
        setStat('consensus', cs.consensus || 'PoHD', { text: '8D hypercube', dir: 'up' });
      } catch (_) { /* swallow */ }
    }
    if (leaderboard.status === 'fulfilled') {
      const scdas = leaderboard.value || [];
      setStat('scda_count', fmt(scdas.length), { text: 'live', dir: 'up' });
      renderLeaderboard(scdas);
    }
    if (overview.status === 'fulfilled') {
      const o = overview.value;
      if (o.tps !== undefined) setStat('tps', fmt(o.tps), { text: 'real-time', dir: 'up' });
      if (o.dimensions) $('v4-tel-dim').textContent = o.dimensions;
      if (o.environment) $('v4-tel-env').textContent = o.environment;
    }
    if (version.status === 'fulfilled') {
      const v = version.value;
      if (v.protocol_version) $('v4-tel-reward').textContent = v.protocol_version;
      if (v.environment) $('v4-tel-env').textContent = v.environment;
    }

    setStatus(true);
    addFeed({ kind: 'scda', icon: '✦', text: 'data refreshed' });
  } catch (err) {
    setStatus(false, err.message);
  }
}

function setStatus(online, msg) {
  state.online = online;
  const el = $('v4-status');
  el.classList.toggle('is-online', online);
  el.classList.toggle('is-offline', !online);
  el.querySelector('.v4-status-label').textContent = online
    ? `online · ${new Date().toLocaleTimeString()}`
    : `offline · ${msg || 'connection lost'}`;
}

function drawDNA(vec) {
  if (dna) dna.draw(vec);
}

// --- Boot ------------------------------------------------------------
function boot() {
  initCosmicBackground();
  initHypercube();
  dna = initDNASpectrum();
  dna.draw([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]);
  refresh();
  setInterval(refresh, REFRESH_INTERVAL);
  $('v4-refresh').addEventListener('click', () => {
    addFeed({ kind: 'scda', icon: '↻', text: 'manual refresh' });
    refresh();
  });
  $('v4-theme').addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur === 'cosmic-v4' ? 'light' : 'cosmic-v4';
    document.documentElement.setAttribute('data-theme', next);
    addFeed({ kind: 'scda', icon: '◐', text: 'theme → ' + next });
  });
  // Boot feed events
  addFeed({ kind: 'genesis', icon: '🌌', text: 'cosmic dashboard booted' });
  setInterval(() => {
    const up = Math.floor(performance.now() / 1000);
    const h = Math.floor(up / 3600);
    const m = Math.floor((up % 3600) / 60);
    const s = up % 60;
    $('v4-uptime').textContent = `uptime ${h}h ${m}m ${s}s`;
  }, 1000);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}
