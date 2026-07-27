/* ════════════════════════════════════════════════════════════════
   LANIAKEA PROTOCOL · 8D COSMIC UI v8 · JS CONTROLLER
   Author: Qalam · Build v6.3.0-Qalam
   ──────────────────────────────────────────────────────────────
   Real-time binding to 154+ API routes · 18 subsystems · mainnet
   ════════════════════════════════════════════════════════════════ */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ─── Configuration ─────────────────────────────────────────
const API = window.location.origin;
const REFRESH_FAST = 4000;   // 4s
const REFRESH_SLOW = 12000;  // 12s
const REFRESH_FEED = 6000;   // 6s
const TOAST_TTL = 2800;
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

// ─── State ────────────────────────────────────────────────
const state = {
  theme: localStorage.getItem('lk_theme') || 'cosmic-dark',
  feedOpen: localStorage.getItem('lk_feed_open') === '1',
  feedOn: true,
  online: false,
  startTime: Date.now(),
  cache: {},
  routes: 0,
  feedItems: [],
  subsystems: [],
  blocks: [],
  scdas: [],
  metrics: {},
  // Hypercube state
  hypercube: { enabled: true, autoRotate: true, wireframe: false, trail: true, projection: 'perspective', speed: 40 },
};

// ─── Apply theme ──────────────────────────────────────────
document.documentElement.dataset.theme = state.theme;

// ─── Utilities ────────────────────────────────────────────
const fmt = {
  num: n => (typeof n === 'number' && isFinite(n)) ? n.toLocaleString('en-US') : '—',
  short: n => {
    if (typeof n !== 'number' || !isFinite(n)) return '—';
    const abs = Math.abs(n);
    if (abs >= 1e9) return (n / 1e9).toFixed(2) + 'B';
    if (abs >= 1e6) return (n / 1e6).toFixed(2) + 'M';
    if (abs >= 1e3) return (n / 1e3).toFixed(2) + 'K';
    return n.toString();
  },
  hash: h => (h && typeof h === 'string') ? (h.slice(0, 6) + '…' + h.slice(-4)) : '—',
  ts: () => new Date().toLocaleTimeString('en-GB'),
  duration: sec => {
    if (typeof sec !== 'number' || !isFinite(sec)) return '—';
    const d = Math.floor(sec / 86400);
    const h = Math.floor((sec % 86400) / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = Math.floor(sec % 60);
    if (d > 0) return `${d}d ${h}h`;
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
  },
  pct: n => (typeof n === 'number' && isFinite(n)) ? (n * 100).toFixed(1) + '%' : '—',
};

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') node.className = v;
    else if (k === 'style' && typeof v === 'object') Object.assign(node.style, v);
    else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2).toLowerCase(), v);
    else if (k === 'html') node.innerHTML = v;
    else if (v !== null && v !== undefined) node.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c == null || c === false) continue;
    node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  }
  return node;
}

function toast(msg, type = '') {
  const t = el('div', { class: 'lk-toast lk-toast--' + type }, msg);
  $('#lk-toast-wrap').appendChild(t);
  setTimeout(() => t.remove(), TOAST_TTL);
}

// ─── API ──────────────────────────────────────────────────
async function api(path, opts = {}) {
  const start = performance.now();
  try {
    const res = await fetch(API + path, {
      headers: { 'Accept': 'application/json' },
      cache: 'no-store',
      ...opts,
    });
    const ms = performance.now() - start;
    if (!res.ok) {
      console.warn(`[api] ${path} HTTP ${res.status} (${ms.toFixed(0)}ms)`);
      return { __error: true, status: res.status, path, ms };
    }
    const ct = res.headers.get('content-type') || '';
    const data = ct.includes('json') ? await res.json() : await res.text();
    return data;
  } catch (e) {
    console.warn(`[api] ${path} failed:`, e.message);
    return { __error: true, message: e.message, path };
  }
}

async function apiPost(path, body) {
  return api(path, {
    method: 'POST',
    headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {}),
  });
}

// ─── Tabs ─────────────────────────────────────────────────
function setupTabs() {
  $$('.lk-nav__item').forEach(item => {
    item.addEventListener('click', e => {
      e.preventDefault();
      const tab = item.dataset.tab;
      switchTab(tab);
      if (window.innerWidth < 768) {
        $('#lk-sidebar').classList.remove('open');
        $('#lk-backdrop').classList.remove('show');
        $('#lk-btn-menu').setAttribute('aria-expanded', 'false');
      }
    });
  });
  const initial = (location.hash || '#overview').slice(1);
  if (document.getElementById('tab-' + initial)) switchTab(initial);
}

function switchTab(tab) {
  $$('.lk-nav__item').forEach(n => n.classList.toggle('active', n.dataset.tab === tab));
  $$('.lk-tab').forEach(t => t.classList.toggle('active', t.id === 'tab-' + tab));
  history.replaceState(null, '', '#' + tab);
  // Resize hypercube on switch
  if (tab === 'hypercube') setTimeout(() => fullHypercube && fullHypercube.resize(), 100);
  if (tab === 'overview') setTimeout(() => previewHypercube && previewHypercube.resize(), 100);
  // Trigger lazy data load for this tab
  loadTabData(tab);
}

// ─── Mobile menu ──────────────────────────────────────────
function setupMobileMenu() {
  const btn = $('#lk-btn-menu');
  const sb = $('#lk-sidebar');
  const bd = $('#lk-backdrop');
  const toggle = () => {
    const open = sb.classList.toggle('open');
    bd.classList.toggle('show', open);
    btn.setAttribute('aria-expanded', String(open));
  };
  btn.addEventListener('click', toggle);
  bd.addEventListener('click', () => {
    sb.classList.remove('open');
    bd.classList.remove('show');
    btn.setAttribute('aria-expanded', 'false');
  });
}

// ─── Theme ────────────────────────────────────────────────
function setupTheme() {
  const btn = $('#lk-btn-theme');
  btn.addEventListener('click', () => {
    const cur = document.documentElement.dataset.theme;
    const next = cur === 'cosmic-dark' ? 'light' : 'cosmic-dark';
    document.documentElement.dataset.theme = next;
    state.theme = next;
    localStorage.setItem('lk_theme', next);
    toast('Theme: ' + next, 'ok');
    // Re-render canvas colors if open
    if (fullHypercube) fullHypercube.applyTheme();
    if (previewHypercube) previewHypercube.applyTheme();
  });
}

// ─── Feed toggle ──────────────────────────────────────────
function setupFeedToggle() {
  const layout = document.querySelector('.lk-layout');
  if (state.feedOpen) layout.classList.add('feed-open');
  $('#lk-btn-feed').addEventListener('click', () => {
    state.feedOpen = !state.feedOpen;
    layout.classList.toggle('feed-open', state.feedOpen);
    localStorage.setItem('lk_feed_open', state.feedOpen ? '1' : '0');
    toast('Feed: ' + (state.feedOpen ? 'on' : 'off'), 'ok');
  });
  $('#lk-btn-feed-close').addEventListener('click', () => {
    state.feedOpen = false;
    layout.classList.remove('feed-open');
    localStorage.setItem('lk_feed_open', '0');
  });
  $('#lk-btn-feed-clear').addEventListener('click', () => {
    state.feedItems = [];
    renderFeed();
  });
}

// ─── Refresh button ───────────────────────────────────────
function setupRefresh() {
  $('#lk-btn-refresh').addEventListener('click', async () => {
    toast('Refreshing…', '');
    await loadAll(true);
    toast('Refreshed', 'ok');
  });
}

// ─── Cosmic background canvas ─────────────────────────────
function setupBgCanvas() {
  const cvs = $('#lk-bg-canvas');
  if (!cvs) return;
  const ctx = cvs.getContext('2d');
  let stars = [];
  const STAR_COUNT = 180;

  function resize() {
    cvs.width = window.innerWidth * window.devicePixelRatio;
    cvs.height = window.innerHeight * window.devicePixelRatio;
    cvs.style.width = window.innerWidth + 'px';
    cvs.style.height = window.innerHeight + 'px';
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    initStars();
  }
  function initStars() {
    stars = [];
    for (let i = 0; i < STAR_COUNT; i++) {
      stars.push({
        x: Math.random() * window.innerWidth,
        y: Math.random() * window.innerHeight,
        z: Math.random() * 1 + 0.2,
        r: Math.random() * 1.2 + 0.2,
        vx: (Math.random() - 0.5) * 0.08,
        vy: (Math.random() - 0.5) * 0.08,
        tw: Math.random() * Math.PI * 2,
        tws: 0.02 + Math.random() * 0.04,
        hue: Math.random() < 0.7 ? '180-200' : (Math.random() < 0.5 ? '280-320' : '150-180'),
      });
    }
  }
  function draw() {
    const W = window.innerWidth, H = window.innerHeight;
    ctx.clearRect(0, 0, W, H);
    const isLight = document.documentElement.dataset.theme === 'light';
    for (const s of stars) {
      s.x += s.vx; s.y += s.vy;
      s.tw += s.tws;
      if (s.x < 0) s.x = W; else if (s.x > W) s.x = 0;
      if (s.y < 0) s.y = H; else if (s.y > H) s.y = 0;
      const a = (Math.sin(s.tw) + 1) * 0.4 + 0.2;
      const r = s.r * s.z;
      let color;
      if (isLight) {
        if (s.hue === '180-200') color = `rgba(80, 60, 200, ${a * 0.4})`;
        else if (s.hue === '280-320') color = `rgba(140, 60, 180, ${a * 0.4})`;
        else color = `rgba(40, 140, 180, ${a * 0.4})`;
      } else {
        if (s.hue === '180-200') color = `rgba(0, 255, 220, ${a})`;
        else if (s.hue === '280-320') color = `rgba(180, 100, 255, ${a})`;
        else color = `rgba(100, 200, 255, ${a})`;
      }
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(s.x, s.y, r, 0, Math.PI * 2);
      ctx.fill();
    }
    requestAnimationFrame(draw);
  }
  window.addEventListener('resize', resize);
  resize();
  draw();
}

// ─── 8D Hypercube (Three.js) ──────────────────────────────
class Hypercube3D {
  constructor(canvas, opts = {}) {
    this.canvas = canvas;
    this.opts = opts;
    this.W = 0; this.H = 0;
    this.fps = 0; this.fpsCounter = 0; this.fpsTime = performance.now();
    this.init();
  }
  init() {
    this.scene = new THREE.Scene();
    this.isLight = document.documentElement.dataset.theme === 'light';
    this.scene.fog = new THREE.FogExp2(this.isLight ? 0xf4f6fb : 0x02030a, 0.04);

    this.camera = new THREE.PerspectiveCamera(60, 1, 0.1, 1000);
    this.camera.position.set(0, 0, 16);

    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setClearColor(0x000000, 0);

    this.controls = new OrbitControls(this.camera, this.canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.autoRotate = true;
    this.controls.autoRotateSpeed = 0.8;
    this.controls.minDistance = 6;
    this.controls.maxDistance = 60;

    this.buildCube();
    this.applyTheme();
    this.resize();
    this.animate = this.animate.bind(this);
    this.animate();
  }
  buildCube() {
    // 8D hypercube: project to 3D with 4 layers of 8 vertices
    const N = 8; // bits
    const size = 4;
    const verts = [];
    const layers = [];
    for (let i = 0; i < N; i++) {
      const layerVerts = [];
      for (let j = 0; j < N; j++) {
        const x = (j & 1) ? size : -size;
        const y = (j & 2) ? size : -size;
        const z = (j & 4) ? size : -size;
        const w = (i / (N - 1) - 0.5) * size * 2; // 4th dimension
        // Project 4D -> 3D
        const w_factor = 1 / (3 - w * 0.4);
        layerVerts.push(new THREE.Vector3(x * w_factor, y * w_factor, z * w_factor));
      }
      layers.push(layerVerts);
    }
    // Flatten
    for (const layer of layers) verts.push(...layer);
    // Connect edges within each layer (cube) and between layers
    const indices = [];
    // Within each cube
    for (let i = 0; i < N; i++) {
      for (let e = 0; e < 12; e++) {
        const pairs = [[0,1],[0,2],[0,4],[1,3],[1,5],[2,3],[2,6],[3,7],[4,5],[4,6],[5,7],[6,7]];
        indices.push(i * 8 + pairs[e][0], i * 8 + pairs[e][1]);
      }
    }
    // Between consecutive layers (w-axis)
    for (let i = 0; i < N - 1; i++) {
      for (let j = 0; j < 8; j++) {
        indices.push(i * 8 + j, (i + 1) * 8 + j);
      }
    }
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(verts.length * 3);
    verts.forEach((v, i) => { positions[i * 3] = v.x; positions[i * 3 + 1] = v.y; positions[i * 3 + 2] = v.z; });
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setIndex(indices);
    // Edges
    const edges = new THREE.EdgesGeometry(geometry);
    const mat = new THREE.LineBasicMaterial({ color: 0x00ffd0, transparent: true, opacity: 0.8 });
    this.lines = new THREE.LineSegments(edges, mat);
    this.scene.add(this.lines);
    // Vertices
    const vGeo = new THREE.BufferGeometry();
    vGeo.setAttribute('position', geometry.getAttribute('position'));
    const vMat = new THREE.PointsMaterial({ color: 0xff3d8a, size: 0.18, transparent: true, opacity: 0.95 });
    this.points = new THREE.Points(vGeo, vMat);
    this.scene.add(this.points);
    // Inner glow
    const glow = new THREE.PointLight(0x7c3aed, 2, 30);
    this.scene.add(glow);
    this.cubeGroup = new THREE.Group();
    this.cubeGroup.add(this.lines, this.points, glow);
    this.scene.add(this.cubeGroup);
  }
  applyTheme() {
    if (!this.lines) return;
    this.isLight = document.documentElement.dataset.theme === 'light';
    this.scene.fog = new THREE.FogExp2(this.isLight ? 0xf4f6fb : 0x02030a, 0.04);
    this.lines.material.color.set(this.isLight ? 0x7c3aed : 0x00ffd0);
    this.points.material.color.set(this.isLight ? 0xff3d8a : 0xff3d8a);
  }
  resize() {
    const r = this.canvas.getBoundingClientRect();
    this.W = r.width; this.H = r.height;
    if (this.W === 0 || this.H === 0) return;
    this.camera.aspect = this.W / this.H;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(this.W, this.H, false);
  }
  animate() {
    requestAnimationFrame(this.animate);
    this.controls.update();
    this.cubeGroup.rotation.y += 0.001 * (state.hypercube.speed / 40);
    this.cubeGroup.rotation.x = Math.sin(Date.now() * 0.0003) * 0.1;
    this.renderer.render(this.scene, this.camera);
    // FPS
    this.fpsCounter++;
    const now = performance.now();
    if (now - this.fpsTime > 500) {
      this.fps = Math.round(this.fpsCounter / ((now - this.fpsTime) / 1000));
      this.fpsCounter = 0; this.fpsTime = now;
      const fpsEl = this.canvas.id === 'lk-cube-canvas' ? $('#lk-cube-fps') : $('#lk-hc-fps');
      if (fpsEl) fpsEl.textContent = this.fps;
    }
  }
  dispose() {
    if (this.lines) this.lines.geometry.dispose(), this.lines.material.dispose();
    if (this.points) this.points.geometry.dispose(), this.points.material.dispose();
    this.renderer.dispose();
  }
}

let previewHypercube = null;
let fullHypercube = null;

function setupHypercube() {
  // Preview canvas in overview
  const c1 = $('#lk-cube-canvas');
  if (c1) previewHypercube = new Hypercube3D(c1);
  // Full canvas in hypercube tab
  const c2 = $('#lk-hc-full-canvas');
  if (c2) {
    fullHypercube = new Hypercube3D(c2, { full: true });
    // Controls
    const autorotate = $('#lk-hc-autorotate');
    const wireframe = $('#lk-hc-wireframe');
    const trail = $('#lk-hc-trail');
    const proj = $('#lk-hc-proj');
    const speed = $('#lk-hc-speed');
    if (autorotate) autorotate.addEventListener('change', e => { fullHypercube.controls.autoRotate = e.target.checked; });
    if (wireframe) wireframe.addEventListener('change', e => {
      fullHypercube.lines.material.wireframe = e.target.checked;
      fullHypercube.lines.material.opacity = e.target.checked ? 0.4 : 0.8;
    });
    if (trail) trail.addEventListener('change', e => { fullHypercube.points.material.opacity = e.target.checked ? 0.95 : 0.5; });
    if (proj) proj.addEventListener('change', e => {
      state.hypercube.projection = e.target.value;
      if (e.target.value === 'orthographic') {
        fullHypercube.camera = new THREE.OrthographicCamera(-10, 10, 10, -10, 0.1, 1000);
      } else if (e.target.value === 'stereographic') {
        fullHypercube.camera = new THREE.PerspectiveCamera(90, fullHypercube.W / fullHypercube.H, 0.1, 1000);
      } else {
        fullHypercube.camera = new THREE.PerspectiveCamera(60, fullHypercube.W / fullHypercube.H, 0.1, 1000);
      }
    });
    if (speed) speed.addEventListener('input', e => { state.hypercube.speed = +e.target.value; });
  }
  window.addEventListener('resize', () => {
    if (previewHypercube) previewHypercube.resize();
    if (fullHypercube) fullHypercube.resize();
  });
}

// ─── Tree canvas (SCDA lineage) ──────────────────────────
function setupTreeCanvas() {
  const cvs = $('#lk-tree-canvas');
  if (!cvs) return;
  const ctx = cvs.getContext('2d');

  function draw() {
    const r = cvs.getBoundingClientRect();
    cvs.width = r.width * window.devicePixelRatio;
    cvs.height = r.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    const W = r.width, H = r.height;
    ctx.clearRect(0, 0, W, H);
    const isLight = document.documentElement.dataset.theme === 'light';
    const nodes = state.scdas && state.scdas.length ? state.scdas : [];
    if (nodes.length === 0) {
      ctx.fillStyle = isLight ? '#5a6589' : '#5a6589';
      ctx.font = '13px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No SCDAs yet — the evolutionary tree is empty', W / 2, H / 2);
      return;
    }
    // Simple radial tree
    const cx = W / 2, cy = H / 2;
    const radius = Math.min(W, H) * 0.4;
    nodes.slice(0, 32).forEach((n, i) => {
      const a = (i / Math.max(nodes.length, 1)) * Math.PI * 2;
      const x = cx + Math.cos(a) * radius;
      const y = cy + Math.sin(a) * radius;
      // Line to center
      ctx.strokeStyle = isLight ? 'rgba(124, 58, 237, 0.3)' : 'rgba(0, 255, 208, 0.3)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(x, y);
      ctx.stroke();
      // Node
      const fitness = n.fitness || n.complexity || 0.5;
      const r = 4 + Math.min(fitness * 8, 12);
      const grad = ctx.createRadialGradient(x, y, 0, x, y, r);
      grad.addColorStop(0, 'rgba(0, 255, 208, 0.9)');
      grad.addColorStop(1, 'rgba(124, 58, 237, 0)');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(x, y, r * 1.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = isLight ? '#0d1424' : '#00ffd0';
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
      // Label
      ctx.fillStyle = isLight ? '#2a3554' : '#c8d0ee';
      ctx.font = '10px JetBrains Mono';
      ctx.textAlign = 'center';
      ctx.fillText((n.id || n.did || 'scda-' + i).slice(-6), x, y + r + 12);
    });
    // Center node
    const grad2 = ctx.createRadialGradient(cx, cy, 0, cx, cy, 16);
    grad2.addColorStop(0, 'rgba(255, 61, 138, 0.9)');
    grad2.addColorStop(1, 'rgba(255, 61, 138, 0)');
    ctx.fillStyle = grad2;
    ctx.beginPath();
    ctx.arc(cx, cy, 24, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#ff3d8a';
    ctx.beginPath();
    ctx.arc(cx, cy, 8, 0, Math.PI * 2);
    ctx.fill();
  }
  // Redraw on data change
  state._treeRedraw = draw;
  draw();
  window.addEventListener('resize', draw);
}

// ─── Live Activity Feed ───────────────────────────────────
async function loadFeed() {
  if (!state.feedOn || !state.feedOpen) return;
  const list = $('#lk-feed-list');
  const data = await api('/v6/feed');
  const status = $('#lk-feed-status');
  if (data && !data.__error && Array.isArray(data.events || data.items || data)) {
    const events = data.events || data.items || data;
    events.slice(0, 20).forEach(ev => {
      state.feedItems.unshift({
        type: ev.type || ev.kind || 'system',
        msg: ev.message || ev.msg || ev.text || JSON.stringify(ev).slice(0, 120),
        time: ev.timestamp || ev.time || new Date().toISOString(),
      });
    });
    if (state.feedItems.length > 80) state.feedItems = state.feedItems.slice(0, 80);
    renderFeed();
    if (status) status.textContent = 'on · ' + state.feedItems.length;
    state.online = true;
    updateNetbar();
  } else {
    if (status) status.textContent = 'offline';
  }
}

function renderFeed() {
  const list = $('#lk-feed-list');
  if (!list) return;
  list.innerHTML = '';
  for (const item of state.feedItems) {
    const t = new Date(item.time);
    list.appendChild(el('div', { class: 'lk-feed-item' },
      el('div', { class: 'lk-feed-item__head' },
        el('span', { class: 'lk-feed-item__type lk-feed-item__type--' + item.type }, item.type),
        el('span', { class: 'lk-feed-item__time' }, t.toLocaleTimeString())
      ),
      el('div', { class: 'lk-feed-item__msg' }, item.msg)
    ));
  }
}

// ─── Update functions for each section ────────────────────
async function loadOverview() {
  const [health, status, core, cosmic, dashboard, achv, dex, props, nft, quantum, market, know, scda] = await Promise.all([
    api('/health'),
    api('/core/status'),
    api('/'),
    api('/cosmic/overview'),
    api('/dashboard/metrics'),
    api('/achievements/all'),
    api('/defi/pools'),
    api('/governance/proposals'),
    api('/marketplace/nft/all'),
    api('/quantum/queue'),
    api('/marketplace/all'),
    api('/knowledge_market/listed'),
    api('/v6/scda/leaderboard'),
  ]);

  // Health
  if (health && !health.__error) {
    $('#lk-nb-version').textContent = 'v' + (health.version || '—');
    state.online = true;
    updateNetbar();
  }

  // Subsystems from root
  if (core && !core.__error) {
    state.subsystems = Object.entries(core.subsystems || {}).map(([k, v]) => ({
      name: k, status: v ? 'on' : 'off'
    }));
    state.routes = (core.routes || core.api_routes || 0);
    // Net bar
    if (core.chain_length !== undefined) $('#lk-nb-block').textContent = fmt.num(core.chain_length);
    if (core.scda_identities !== undefined) $('#lk-nb-scda').textContent = fmt.num(core.scda_identities);
    if (core.validators) $('#lk-nb-val').textContent = fmt.num(core.validators);
    if (core.uptime_seconds) $('#lk-nb-up').textContent = fmt.duration(core.uptime_seconds);
    if (core.tps !== undefined) $('#lk-nb-tps').textContent = fmt.num(core.tps);
  }
  if (status && !status.__error) {
    $('#lk-pill-version').textContent = 'v' + (status.protocol_version || '—');
    $('#lk-pill-env').textContent = 'env ' + (status.environment || '—');
  }

  // Metrics
  if (dashboard && !dashboard.__error) {
    state.metrics = dashboard;
  }

  // Render top metric grid
  const subs = state.subsystems.filter(s => s.status === 'on').length;
  $('#m-subsys').textContent = subs;
  $('#m-routes').textContent = state.routes || '—';
  $('#m-scda').textContent = (core && core.scda_identities) || '—';
  $('#m-blocks').textContent = (core && core.chain_length) || '—';
  $('#m-validators').textContent = (core && core.validators) || '—';
  $('#m-treasury').textContent = (core && core.treasury) ? fmt.short(core.treasury) : '—';
  $('#m-aiperf').textContent = (core && core.ai_performance !== undefined) ? fmt.pct(core.ai_performance) : (core && core.ai_performance) || '—';
  $('#m-dex').textContent = (core && core.dex_pools) || '—';
  $('#m-dao').textContent = (core && core.dao_proposals) || '0';
  $('#m-quantum').textContent = (core && core.quantum_queue) || '0';
  $('#m-alliances').textContent = (core && core.diplomacy_alliances) || '0';
  $('#m-knowledge').textContent = (know && know.assets ? know.assets.length : (core && core.knowledge_market_listed)) || '0';
  $('#m-nft').textContent = (nft && nft.tokens ? nft.tokens.length : (core && core.nft_count)) || '0';
  $('#m-achv').textContent = (achv && achv.unlocked ? achv.unlocked : (achv && achv.achievements ? achv.achievements.length : '—'));
  $('#m-social').textContent = (core && core.social_posts) || '—';
  $('#m-uptime').textContent = (core && core.uptime_seconds) ? fmt.num(core.uptime_seconds) : '—';

  $('#lk-ov-sub').textContent = `Last sync: ${fmt.ts()} · ${state.routes || '—'} routes · mainnet live`;

  // Subsystems grid
  renderSubsystems();

  // Token info
  const token = await api('/token/info');
  if (token && !token.__error) {
    $('#lk-t-sym').textContent = token.symbol || 'LANA';
    $('#lk-t-name').textContent = token.name || 'Laniakea';
    $('#lk-t-dec').textContent = token.decimals || '18';
    $('#lk-t-sup').textContent = token.total_supply ? fmt.short(token.total_supply) : '—';
    $('#lk-t-net').textContent = token.network || 'mainnet';
    if (token.chain_id) $('#lk-t-chain').textContent = token.chain_id;
  }

  // Cross-chain status
  const cc = await api('/crosschain/supported');
  if (cc && !cc.__error) {
    const networks = cc.networks || cc.supported || cc.chains || cc || [];
    if (Array.isArray(networks)) {
      const map = {
        ethereum: 'eth', polygon: 'poly', arbitrum: 'arb', optimism: 'op',
        base: 'base', bnb: 'bsc', bsc: 'bsc', avalanche: 'avax', fantom: 'ftm',
      };
      networks.forEach(n => {
        const key = (n.name || n.chain || n).toLowerCase().replace(/\s/g, '');
        const cssKey = map[key];
        const el = cssKey && $('#lk-chain-' + cssKey);
        if (el) el.textContent = (n.status || 'live').toUpperCase();
      });
    }
  }
}

function renderSubsystems() {
  const grid = $('#lk-ss-grid');
  if (!grid) return;
  const ico = {
    blockchain: '⛓', consensus: '⚖', crosschain: '⌖', quantum: '⚛',
    governance: '⚖', marketplace: '◇', simulation: '∿', dashboard: '◉',
    achievements: '★', ai: '⌬', defi: '◈', diplomacy: '⚐',
    knowledge_market: '✎', scda: '✦', ai_engine: '⌬', metaverse: '⌘',
    social: '✉', reputation: '♛',
  };
  grid.innerHTML = '';
  for (const s of state.subsystems) {
    grid.appendChild(el('div', { class: 'lk-ss' },
      el('span', { class: 'lk-ss__ico' }, ico[s.name] || '◆'),
      el('div', { class: 'lk-ss__name' }, s.name.replace(/_/g, ' ')),
      el('div', { class: 'lk-ss__status lk-ss__status--' + s.status }, s.status)
    ));
  }
  $('#lk-ss-sub').textContent = `${state.subsystems.filter(s => s.status === 'on').length} / ${state.subsystems.length} online`;
}

function updateNetbar() {
  const el = $('#lk-nb-status-text');
  const dot = $('#lk-nb-status .lk-netbar__dot');
  if (state.online) {
    el.textContent = 'connected';
    dot.dataset.state = 'on';
  } else {
    el.textContent = 'offline';
    dot.dataset.state = 'off';
  }
  const pill = $('#lk-pill-conn');
  if (pill) {
    pill.dataset.state = state.online ? 'on' : 'off';
    pill.textContent = state.online ? '● online' : '● offline';
  }
}

// ─── SCDA tab ─────────────────────────────────────────────
async function loadSCDA() {
  const [list, lb] = await Promise.all([
    api('/scda/identities'),
    api('/v6/scda/leaderboard'),
  ]);
  const listEl = $('#lk-scda-list');
  const lbEl = $('#lk-scda-leaderboard');
  listEl.innerHTML = '';
  lbEl.innerHTML = '';
  let scdas = [];
  if (list && !list.__error) scdas = list.identities || list.scdas || list.items || list || [];
  if (!Array.isArray(scdas)) scdas = [];
  state.scdas = scdas;
  if (scdas.length === 0) {
    listEl.appendChild(el('div', { class: 'lk-empty' }, 'No SCDAs yet — the universe is ready to evolve.'));
  } else {
    scdas.forEach((s, i) => {
      const fitness = s.fitness || s.complexity || s.c || 1.0;
      listEl.appendChild(el('div', { class: 'lk-scda-item' },
        el('div', { class: 'lk-scda-item__rank' }, '#' + (i + 1)),
        el('div', { class: 'lk-scda-item__main' },
          el('div', { class: 'lk-scda-item__name' }, '✦ ' + (s.name || s.id || 'scda-' + i)),
          el('div', { class: 'lk-scda-item__id' }, (s.did || s.id || '').slice(0, 24) + '…'),
          el('div', { class: 'lk-scda-item__meta' }, 'Tier ' + (s.tier || 'I') + ' · ' + (s.generation || 0) + ' gens')
        ),
        el('div', { class: 'lk-scda-item__stat' },
          el('strong', {}, fmt.num(parseFloat(fitness.toFixed(2)))),
          el('div', { style: { fontSize: '10px', color: 'var(--t-3)' } }, 'fitness')
        )
      ));
    });
  }
  $('#lk-scda-sub').textContent = scdas.length + ' digital organisms';

  // Leaderboard
  let leaders = [];
  if (lb && !lb.__error) leaders = lb.leaderboard || lb.top || lb.scdas || lb.items || [];
  if (!Array.isArray(leaders)) leaders = [];
  if (leaders.length === 0) {
    lbEl.appendChild(el('div', { class: 'lk-empty' }, 'No leaderboard data yet.'));
  } else {
    leaders.forEach((s, i) => {
      const fitness = s.fitness || s.complexity || s.score || 0;
      const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '';
      lbEl.appendChild(el('div', { class: 'lk-lb-item' },
        el('div', { class: 'lk-lb-item__rank' }, medal || '#' + (i + 1)),
        el('div', { class: 'lk-lb-item__main' },
          el('div', { class: 'lk-lb-item__name' }, (s.name || s.id || 'scda-' + i)),
          el('div', { class: 'lk-lb-item__id' }, (s.did || s.id || '').slice(0, 24))
        ),
        el('div', { class: 'lk-lb-item__stat' },
          el('strong', {}, fmt.num(parseFloat(fitness.toFixed(2)))),
          el('div', { style: { fontSize: '10px', color: 'var(--t-3)' } }, 'fitness')
        )
      ));
    });
  }
  if (state._treeRedraw) state._treeRedraw();
}

// ─── Blockchain tab ───────────────────────────────────────
async function loadBlockchain() {
  const [info, chain, cons] = await Promise.all([
    api('/blockchain/info'),
    api('/blockchain/chain'),
    api('/consensus/info').catch(() => null),
  ]);
  const infoEl = $('#lk-chain-info');
  if (info && !info.__error) {
    infoEl.innerHTML = '';
    Object.entries(info).slice(0, 8).forEach(([k, v]) => {
      infoEl.appendChild(el('div', { class: 'lk-kv' },
        el('span', {}, k.replace(/_/g, ' ')),
        el('strong', {}, typeof v === 'object' ? JSON.stringify(v).slice(0, 24) : String(v).slice(0, 24))
      ));
    });
  }
  if (cons && !cons.__error) {
    const cEl = $('#lk-consensus-info');
    cEl.innerHTML = '';
    Object.entries(cons).slice(0, 8).forEach(([k, v]) => {
      cEl.appendChild(el('div', { class: 'lk-kv' },
        el('span', {}, k.replace(/_/g, ' ')),
        el('strong', {}, String(v).slice(0, 24))
      ));
    });
  }
  const blocks = Array.isArray(chain) ? chain : (chain && chain.blocks) || [];
  state.blocks = blocks;
  const listEl = $('#lk-blocks-list');
  listEl.innerHTML = '';
  if (blocks.length === 0) {
    listEl.appendChild(el('div', { class: 'lk-empty' }, 'No blocks yet — be the first to mine.'));
  } else {
    blocks.slice().reverse().slice(0, 30).forEach((b, i) => {
      listEl.appendChild(el('div', { class: 'lk-block-item' },
        el('div', { class: 'lk-scda-item__rank' }, '#' + (b.index !== undefined ? b.index : (blocks.length - i))),
        el('div', { class: 'lk-scda-item__main' },
          el('div', { class: 'lk-scda-item__name' }, '⛓ Block ' + (b.index || i)),
          el('div', { class: 'lk-scda-item__id' }, fmt.hash(b.hash || '0x' + i)),
          el('div', { class: 'lk-scda-item__meta' }, (b.transactions || []).length + ' tx · ' + (b.timestamp || ''))
        )
      ));
    });
  }
}

// ─── AI Engine tab ────────────────────────────────────────
async function loadAI() {
  const problems = await api('/ai/problems');
  renderProblems('#lk-problems-list', problems);
  renderProblems('#lk-problems-list-2', problems);
  const info = await api('/ai/info');
  if (info && !info.__error) {
    $('#lk-ai-model').textContent = info.model || info.model_version || 'cognitive engine';
  }
}

function renderProblems(sel, data) {
  const list = $(sel);
  if (!list) return;
  list.innerHTML = '';
  if (!data || data.__error) {
    list.appendChild(el('div', { class: 'lk-empty' }, 'No hard problems available.'));
    return;
  }
  const problems = data.problems || data.items || data || [];
  if (!Array.isArray(problems) || problems.length === 0) {
    list.appendChild(el('div', { class: 'lk-empty' }, 'No hard problems yet.'));
    return;
  }
  problems.slice(0, 20).forEach((p, i) => {
    list.appendChild(el('div', { class: 'lk-prob-item' },
      el('div', { class: 'lk-scda-item__rank' }, '⚡'),
      el('div', { class: 'lk-scda-item__main' },
        el('div', { class: 'lk-scda-item__name' }, p.equation || p.text || p.problem || ('Problem ' + i)),
        el('div', { class: 'lk-scda-item__meta' }, 'difficulty ' + (p.difficulty || '—') + ' · ' + (p.domain || 'math'))
      )
    ));
  });
}

// ─── Quantum tab ──────────────────────────────────────────
async function loadQuantum() {
  const q = await api('/quantum/queue');
  const list = $('#lk-q-queue');
  list.innerHTML = '';
  if (q && !q.__error) {
    const jobs = q.jobs || q.queue || q.items || q || [];
    if (Array.isArray(jobs) && jobs.length > 0) {
      jobs.forEach(j => {
        list.appendChild(el('div', { class: 'lk-prob-item' },
          el('div', { class: 'lk-scda-item__rank' }, '⚛'),
          el('div', { class: 'lk-scda-item__main' },
            el('div', { class: 'lk-scda-item__name' }, j.circuit || j.id || 'job'),
            el('div', { class: 'lk-scda-item__meta' }, (j.shots || 0) + ' shots · ' + (j.status || 'queued'))
          )
        ));
      });
    } else {
      list.appendChild(el('div', { class: 'lk-empty' }, 'Quantum queue empty.'));
    }
  }
}

// ─── Cross-chain tab ──────────────────────────────────────
async function loadCrossChain() {
  const cc = await api('/crosschain/supported');
  const list = $('#lk-cc-list');
  list.innerHTML = '';
  if (cc && !cc.__error) {
    const networks = cc.networks || cc.supported || cc.chains || cc || [];
    if (Array.isArray(networks) && networks.length > 0) {
      networks.forEach(n => {
        const name = (n.name || n.chain || n).toString();
        const cssMap = { ethereum: 'eth', polygon: 'poly', arbitrum: 'arb', optimism: 'op', base: 'base', bnb: 'bsc', bsc: 'bsc', avalanche: 'avax', fantom: 'ftm' };
        const key = name.toLowerCase().replace(/\s/g, '');
        const dotClass = 'lk-chain__dot--' + (cssMap[key] || 'eth');
        list.appendChild(el('div', { class: 'lk-chain' },
          el('span', { class: 'lk-chain__dot ' + dotClass }),
          el('span', { class: 'lk-chain__name' }, name),
          el('span', { class: 'lk-chain__status' }, (n.status || 'live').toUpperCase())
        ));
      });
    } else {
      list.appendChild(el('div', { class: 'lk-empty' }, 'No networks data.'));
    }
  }
}

// ─── Governance tab ───────────────────────────────────────
async function loadGovernance() {
  const props = await api('/governance/proposals');
  const list = $('#lk-prop-list');
  list.innerHTML = '';
  if (props && !props.__error) {
    const items = props.proposals || props.items || props || [];
    if (Array.isArray(items) && items.length > 0) {
      items.forEach(p => {
        list.appendChild(el('div', { class: 'lk-prop-item' },
          el('div', { class: 'lk-scda-item__rank' }, '⚖'),
          el('div', { class: 'lk-scda-item__main' },
            el('div', { class: 'lk-scda-item__name' }, p.title || p.name || p.id || 'Proposal'),
            el('div', { class: 'lk-scda-item__meta' }, (p.status || 'active') + ' · votes: ' + (p.votes || 0))
          )
        ));
      });
    } else {
      list.appendChild(el('div', { class: 'lk-empty' }, 'No active proposals.'));
    }
  }
}

// ─── DeFi tab ─────────────────────────────────────────────
async function loadDeFi() {
  const pools = await api('/defi/pools');
  const list = $('#lk-pools');
  list.innerHTML = '';
  if (pools && !pools.__error) {
    const items = pools.pools || pools.items || pools || [];
    if (Array.isArray(items) && items.length > 0) {
      items.forEach(p => {
        list.appendChild(el('div', { class: 'lk-pool-item' },
          el('div', { class: 'lk-scda-item__rank' }, '◈'),
          el('div', { class: 'lk-scda-item__main' },
            el('div', { class: 'lk-scda-item__name' }, (p.pair || p.name || p.id || 'pool')),
            el('div', { class: 'lk-scda-item__meta' }, 'TVL ' + (p.tvl ? fmt.short(p.tvl) : '—') + ' · APR ' + (p.apr || '—') + '%')
          )
        ));
      });
    } else {
      list.appendChild(el('div', { class: 'lk-empty' }, 'No liquidity pools yet.'));
    }
  }
}

// ─── NFT Marketplace tab ──────────────────────────────────
async function loadMarketplace() {
  const nfts = await api('/marketplace/nft/all');
  const list = $('#lk-nft-list');
  list.innerHTML = '';
  if (nfts && !nfts.__error) {
    const items = nfts.tokens || nfts.items || nfts.nfts || nfts || [];
    if (Array.isArray(items) && items.length > 0) {
      items.forEach(n => {
        list.appendChild(el('div', { class: 'lk-nft-item' },
          el('div', { class: 'lk-scda-item__rank' }, '◇'),
          el('div', { class: 'lk-scda-item__main' },
            el('div', { class: 'lk-scda-item__name' }, n.name || n.title || ('NFT #' + (n.token_id || n.id || ''))),
            el('div', { class: 'lk-scda-item__meta' }, (n.price || '—') + ' LANA · ' + (n.status || 'listed'))
          )
        ));
      });
    } else {
      list.appendChild(el('div', { class: 'lk-empty' }, 'No NFTs minted yet.'));
    }
  }
}

// ─── Knowledge Market tab ─────────────────────────────────
async function loadKnowledge() {
  const km = await api('/knowledge_market/listed');
  const list = $('#lk-knowledge-list');
  list.innerHTML = '';
  if (km && !km.__error) {
    const items = km.assets || km.items || km.knowledge || km || [];
    if (Array.isArray(items) && items.length > 0) {
      items.forEach(k => {
        list.appendChild(el('div', { class: 'lk-know-item' },
          el('div', { class: 'lk-scda-item__rank' }, '✎'),
          el('div', { class: 'lk-scda-item__main' },
            el('div', { class: 'lk-scda-item__name' }, k.title || k.name || k.id || 'Knowledge asset'),
            el('div', { class: 'lk-scda-item__meta' }, (k.price || '—') + ' LANA · ' + (k.domain || 'general'))
          )
        ));
      });
    } else {
      list.appendChild(el('div', { class: 'lk-empty' }, 'No knowledge assets listed yet.'));
    }
  }
}

// ─── Diplomacy tab ────────────────────────────────────────
async function loadDiplomacy() {
  const d = await api('/diplomacy/alliances');
  const list = $('#lk-diplomacy-list');
  list.innerHTML = '';
  if (d && !d.__error) {
    const items = d.alliances || d.items || d.relations || d || [];
    if (Array.isArray(items) && items.length > 0) {
      items.forEach(a => {
        list.appendChild(el('div', { class: 'lk-dip-item' },
          el('div', { class: 'lk-scda-item__rank' }, '⚐'),
          el('div', { class: 'lk-scda-item__main' },
            el('div', { class: 'lk-scda-item__name' }, a.name || a.civ_a + ' ⇄ ' + a.civ_b || 'Alliance'),
            el('div', { class: 'lk-scda-item__meta' }, (a.status || 'active') + ' · strength ' + (a.strength || '—'))
          )
        ));
      });
    } else {
      list.appendChild(el('div', { class: 'lk-empty' }, 'No diplomatic relations yet.'));
    }
  }
}

// ─── Achievements tab ─────────────────────────────────────
async function loadAchievements() {
  const a = await api('/achievements/catalog');
  const list = $('#lk-achv-list');
  list.innerHTML = '';
  if (a && !a.__error) {
    const items = a.achievements || a.items || a.catalog || a || [];
    if (Array.isArray(items) && items.length > 0) {
      items.forEach(ach => {
        list.appendChild(el('div', { class: 'lk-achv-item' },
          el('div', { class: 'lk-scda-item__rank' }, '★'),
          el('div', { class: 'lk-scda-item__main' },
            el('div', { class: 'lk-scda-item__name' }, ach.name || ach.title || ach.id || 'Achievement'),
            el('div', { class: 'lk-scda-item__meta' }, ach.description || ach.desc || '—')
          )
        ));
      });
    } else {
      list.appendChild(el('div', { class: 'lk-empty' }, 'No achievements available.'));
    }
  }
}

// ─── Social Hub tab ───────────────────────────────────────
async function loadSocial() {
  const s = await api('/social/posts');
  const list = $('#lk-social-list');
  list.innerHTML = '';
  if (s && !s.__error) {
    const items = s.posts || s.items || s.feed || s || [];
    if (Array.isArray(items) && items.length > 0) {
      items.forEach(p => {
        list.appendChild(el('div', { class: 'lk-soc-item' },
          el('div', { class: 'lk-scda-item__rank' }, '✉'),
          el('div', { class: 'lk-scda-item__main' },
            el('div', { class: 'lk-scda-item__name' }, p.author || p.user || 'anonymous'),
            el('div', { class: 'lk-scda-item__meta' }, (p.content || p.text || '').slice(0, 100))
          )
        ));
      });
    } else {
      list.appendChild(el('div', { class: 'lk-empty' }, 'No social posts yet.'));
    }
  }
}

// ─── Mining tab ───────────────────────────────────────────
async function loadMining() {
  const m = await api('/mining/info');
  const list = $('#lk-mining-info');
  if (m && !m.__error) {
    list.innerHTML = '';
    Object.entries(m).slice(0, 10).forEach(([k, v]) => {
      list.appendChild(el('div', { class: 'lk-kv' },
        el('span', {}, k.replace(/_/g, ' ')),
        el('strong', {}, String(v).slice(0, 32))
      ));
    });
  }
  const r = await api('/mining/rewards');
  const rew = $('#lk-mining-rewards');
  if (r && !r.__error) {
    rew.innerHTML = '';
    Object.entries(r).slice(0, 8).forEach(([k, v]) => {
      rew.appendChild(el('div', { class: 'lk-kv' },
        el('span', {}, k.replace(/_/g, ' ')),
        el('strong', {}, String(v).slice(0, 32))
      ));
    });
  }
}

// ─── Reputation tab ───────────────────────────────────────
async function loadReputation() {
  const r = await api('/reputation/leaderboard');
  const list = $('#lk-rep-list');
  list.innerHTML = '';
  if (r && !r.__error) {
    const items = r.leaderboard || r.items || r.users || r || [];
    if (Array.isArray(items) && items.length > 0) {
      items.forEach((u, i) => {
        list.appendChild(el('div', { class: 'lk-rep-item' },
          el('div', { class: 'lk-scda-item__rank' }, '♛'),
          el('div', { class: 'lk-scda-item__main' },
            el('div', { class: 'lk-scda-item__name' }, u.name || u.id || ('user-' + i)),
            el('div', { class: 'lk-scda-item__meta' }, 'rep ' + (u.reputation || u.score || 0))
          )
        ));
      });
    } else {
      list.appendChild(el('div', { class: 'lk-empty' }, 'No reputation data yet.'));
    }
  }
}

// ─── Metaverse tab ────────────────────────────────────────
async function loadMetaverse() {
  const m = await api('/metaverse/world');
  const list = $('#lk-metaverse-view');
  if (m && !m.__error) {
    list.innerHTML = '';
    Object.entries(m).slice(0, 12).forEach(([k, v]) => {
      list.appendChild(el('div', { class: 'lk-sim-item' },
        el('div', { class: 'lk-scda-item__rank' }, '⌘'),
        el('div', { class: 'lk-scda-item__main' },
          el('div', { class: 'lk-scda-item__name' }, k.replace(/_/g, ' ')),
          el('div', { class: 'lk-scda-item__meta' }, typeof v === 'object' ? JSON.stringify(v).slice(0, 80) : String(v).slice(0, 80))
        )
      ));
    });
  } else {
    list.innerHTML = '<div class="lk-empty">Metaverse world initializing…</div>';
  }
}

// ─── Simulation tab ───────────────────────────────────────
async function loadSimulation() {
  const ents = await api('/simulation/entities');
  const list = $('#lk-sim-list');
  list.innerHTML = '';
  if (ents && !ents.__error) {
    const items = ents.entities || ents.items || ents || [];
    if (Array.isArray(items) && items.length > 0) {
      items.forEach(e => {
        list.appendChild(el('div', { class: 'lk-sim-item' },
          el('div', { class: 'lk-scda-item__rank' }, '∿'),
          el('div', { class: 'lk-scda-item__main' },
            el('div', { class: 'lk-scda-item__name' }, e.name || e.id || 'Entity'),
            el('div', { class: 'lk-scda-item__meta' }, 'energy ' + (e.energy || '—') + ' · complexity ' + (e.complexity || '—'))
          )
        ));
      });
    } else {
      list.appendChild(el('div', { class: 'lk-empty' }, 'No entities in simulation.'));
    }
  }
}

// ─── Quick actions ────────────────────────────────────────
function setupActions() {
  $$('.lk-action').forEach(btn => {
    btn.addEventListener('click', async () => {
      const action = btn.dataset.action;
      await runAction(action);
    });
  });
  $('#lk-action-out-close').addEventListener('click', () => {
    $('#lk-action-output').hidden = true;
  });
  $('#lk-btn-actions-clear').addEventListener('click', () => {
    $('#lk-action-output').hidden = true;
  });
  $('#lk-btn-mine').addEventListener('click', async () => {
    const result = await apiPost('/blockchain/mine', {});
    const out = $('#lk-mine-result');
    if (result && !result.__error) {
      out.textContent = JSON.stringify(result, null, 2);
      out.hidden = false;
      toast('Block mined!', 'ok');
      loadBlockchain();
    } else {
      out.textContent = 'Error: ' + (result.message || 'unknown');
      out.hidden = false;
      toast('Mining failed', 'err');
    }
  });
  $('#lk-btn-reload-blocks').addEventListener('click', loadBlockchain);
  $('#lk-btn-reload-props').addEventListener('click', loadGovernance);
  $('#lk-btn-reload-nft').addEventListener('click', loadMarketplace);

  // AI query
  $('#lk-btn-ai-query').addEventListener('click', async () => {
    const prompt = $('#lk-ai-prompt').value;
    const tokens = +$('#lk-ai-tokens').value || 512;
    const out = $('#lk-ai-result');
    const body = $('#lk-ai-result-body');
    out.hidden = false;
    body.textContent = 'Thinking…';
    const r = await apiPost('/ai/query', { prompt, max_tokens: tokens });
    if (r && !r.__error) {
      body.textContent = (r.response || r.answer || r.text || r.message || JSON.stringify(r, null, 2));
    } else {
      body.textContent = 'Error: ' + (r.message || r.status || 'unknown');
    }
  });

  // Quantum submit
  $('#lk-btn-q-submit').addEventListener('click', async () => {
    const circuit = $('#lk-q-circuit').value;
    const shots = +$('#lk-q-shots').value || 100;
    const out = $('#lk-q-result');
    const body = $('#lk-q-result-body');
    out.hidden = false;
    body.textContent = 'Submitting…';
    const r = await apiPost('/quantum/job/submit', { circuit, shots });
    if (r && !r.__error) {
      body.textContent = JSON.stringify(r, null, 2);
      loadQuantum();
      toast('Quantum job submitted', 'ok');
    } else {
      body.textContent = 'Error: ' + (r.message || 'unknown');
    }
  });

  // Cross-chain initiate
  $('#lk-btn-cc-init').addEventListener('click', async () => {
    const from = $('#lk-cc-from').value;
    const to = $('#lk-cc-to').value;
    const amount = +$('#lk-cc-amount').value;
    const out = $('#lk-cc-result');
    const body = $('#lk-cc-result-body');
    out.hidden = false;
    body.textContent = 'Initiating…';
    const r = await apiPost('/crosschain/transfer/initiate', { from, to, amount });
    if (r && !r.__error) {
      body.textContent = JSON.stringify(r, null, 2);
      toast('Bridge transfer initiated', 'ok');
    } else {
      body.textContent = 'Error: ' + (r.message || 'unknown');
    }
  });

  // Swap
  $('#lk-btn-swap').addEventListener('click', async () => {
    const from = $('#lk-swap-from').value;
    const to = $('#lk-swap-to').value;
    const amount = +$('#lk-swap-amount').value;
    const out = $('#lk-swap-result');
    const body = $('#lk-swap-result-body');
    out.hidden = false;
    body.textContent = 'Swapping…';
    const r = await apiPost('/defi/swap', { from, to, amount });
    if (r && !r.__error) {
      body.textContent = JSON.stringify(r, null, 2);
      toast('Swap executed', 'ok');
      loadDeFi();
    } else {
      body.textContent = 'Error: ' + (r.message || 'unknown');
    }
  });
}

async function runAction(action) {
  const out = $('#lk-action-output');
  const title = $('#lk-action-out-title');
  const body = $('#lk-action-out-body');
  const time = $('#lk-action-out-time');
  out.hidden = false;
  time.textContent = fmt.ts();
  let result = null;
  let titleText = 'Result';

  switch (action) {
    case 'solve': {
      titleText = '⚡ Hard Problem Solver';
      body.textContent = 'Solving with LLM cognitive engine…';
      result = await apiPost('/ai/solve', { problem: 'ΔC = D(P) / C(t)^α' });
      break;
    }
    case 'evaluate': {
      titleText = '∫ Expression Evaluator';
      body.textContent = 'Evaluating via LLM…';
      result = await apiPost('/ai/evaluate', { expression: '∫ x^2 dx' });
      break;
    }
    case 'predict': {
      titleText = '◐ SCDA Predict';
      body.textContent = 'Predicting SCDA evolution…';
      result = await apiPost('/scda/predict', { steps: 10 });
      break;
    }
    case 'breed': {
      titleText = '✥ SCDA Breed';
      body.textContent = 'Breeding lineage…';
      result = await apiPost('/scda/breed', { count: 2 });
      break;
    }
    case 'quantum': {
      titleText = '⚛ Quantum Job';
      body.textContent = 'Submitting quantum job…';
      result = await apiPost('/quantum/job/submit', { circuit: 'bell', shots: 100 });
      break;
    }
    case 'tokenize': {
      titleText = '◊ Tokenize Knowledge';
      body.textContent = 'Tokenizing knowledge asset…';
      result = await apiPost('/knowledge_market/tokenize', { title: 'LaniakeA insight', content: 'SCDA evolution ΔC = D(P)/C(t)^α', price: 10 });
      break;
    }
    case 'alliance': {
      titleText = '⚐ Form Alliance';
      body.textContent = 'Forming diplomatic alliance…';
      result = await apiPost('/diplomacy/ally', { civ_a: 'Qalam', civ_b: 'Laniakea' });
      break;
    }
    case 'propose': {
      titleText = '⚖ DAO Proposal';
      body.textContent = 'Creating proposal…';
      result = await apiPost('/governance/proposals/new', { title: 'Qalam proposal', description: 'Sample proposal' });
      break;
    }
    case 'mint': {
      titleText = '◇ Mint NFT';
      body.textContent = 'Minting NFT…';
      result = await apiPost('/marketplace/nft/mint', { name: 'Qalam Genesis NFT', uri: 'ipfs://laniakea/qalam' });
      break;
    }
    case 'simulate': {
      titleText = '∿ Cosmic Step';
      body.textContent = 'Running cosmic step…';
      result = await apiPost('/simulation/step', {});
      break;
    }
  }
  if (result && !result.__error) {
    body.textContent = JSON.stringify(result, null, 2);
    toast(titleText + ' ✓', 'ok');
  } else {
    body.textContent = 'Error: ' + (result?.message || result?.status || 'API returned an error');
    toast(titleText + ' ✗', 'err');
  }
  title.textContent = titleText;
}

// ─── Tab data loader ──────────────────────────────────────
const tabLoaders = {
  overview: loadOverview,
  hypercube: () => {},
  scda: loadSCDA,
  blockchain: loadBlockchain,
  ai: loadAI,
  problems: loadAI,
  quantum: loadQuantum,
  crosschain: loadCrossChain,
  governance: loadGovernance,
  defi: loadDeFi,
  marketplace: loadMarketplace,
  knowledge: loadKnowledge,
  diplomacy: loadDiplomacy,
  achievements: loadAchievements,
  social: loadSocial,
  mining: loadMining,
  reputation: loadReputation,
  metaverse: loadMetaverse,
  simulation: loadSimulation,
};
const tabLoaded = new Set();
function loadTabData(tab) {
  const loader = tabLoaders[tab];
  if (loader) loader();
}

// ─── Main loop ────────────────────────────────────────────
async function loadAll(force = false) {
  if (force) tabLoaded.clear();
  // Always load overview first
  if (force || !tabLoaded.has('overview')) {
    await loadOverview();
    tabLoaded.add('overview');
  }
  // Load current tab
  const current = (location.hash || '#overview').slice(1);
  if (current !== 'overview' && tabLoaders[current]) {
    await tabLoaders[current]();
    tabLoaded.add(current);
  }
}

async function main() {
  setupTheme();
  setupMobileMenu();
  setupFeedToggle();
  setupRefresh();
  setupBgCanvas();
  setupTabs();
  setupHypercube();
  setupTreeCanvas();
  setupActions();

  // Initial load
  await loadAll(true);
  loadFeed();

  // Periodic refresh
  setInterval(() => {
    const cur = (location.hash || '#overview').slice(1);
    if (cur === 'overview') loadOverview();
    else if (tabLoaders[cur]) tabLoaders[cur]();
  }, REFRESH_FAST);
  setInterval(loadFeed, REFRESH_FEED);

  // Welcome
  setTimeout(() => toast('LaniakeA mainnet connected · v6.2.0-Qalam', 'ok'), 600);
}

// ─── Boot ─────────────────────────────────────────────────
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', main);
} else {
  main();
}

// Expose for debugging
window.LK = { state, api, switchTab, loadAll };
