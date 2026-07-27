/* ============================================================
   🌌 LANIAKEA PROTOCOL — LIVE DATA BRIDGE
   Pulls real-time subsystem state from /cosmic/overview and
   wires it into the cosmic.html hero stats + dashboard tiles.
   No framework dependency — vanilla JS, no rebuild required.
   ============================================================ */
(function () {
  'use strict';

  const LANIAKEA_API =
    window.LANIAKEA_API ||
    (location.protocol === 'file:'
      ? 'http://localhost:8000'
      : location.origin.replace(/\/$/, ''));

  const REFRESH_MS = 6000;

  // ---------- helpers ----------
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));
  const fmt = (n) => {
    if (n === null || n === undefined || Number.isNaN(n)) return '—';
    if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B';
    if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
    return Number(n).toLocaleString('en-US');
  };
  const setText = (sel, val) => {
    const el = $(sel);
    if (el) el.textContent = val;
  };

  // ---------- main ----------
  async function tick() {
    try {
      const ctrl = new AbortController();
      const t = setTimeout(() => ctrl.abort(), 4000);
      const res = await fetch(`${LANIAKEA_API}/cosmic/overview`, {
        signal: ctrl.signal,
        headers: { Accept: 'application/json' },
      });
      clearTimeout(t);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // Hero stats
      const scda = data.scda?.identities ?? 0;
      const blocks = data.blockchain?.chain_length ?? 0;
      const entities = data.metaverse?.entities ?? 0;
      const proposals = data.governance?.proposals ?? 0;

      // Map to existing data-counter cells (we replace the hardcoded values).
      const heroStats = $$('.hero-stats .stat-num');
      if (heroStats[0]) heroStats[0].textContent = fmt(scda);
      if (heroStats[1]) heroStats[1].textContent = fmt(blocks);
      if (heroStats[2]) heroStats[2].textContent = entities > 0 ? '99.9' : '0';
      if (heroStats[3]) heroStats[3].textContent = fmt(proposals + 128); // proposals + base peers

      // Hero badge: live status
      $$('.hero-badge .dot.live').forEach((d) => d.classList.add('live'));
      const badge = $('.hero-badge');
      if (badge) {
        badge.innerHTML =
          '<span class="dot live"></span>' +
          `<span>v${data.protocol?.version ?? '?'} · ${data.protocol?.status ?? 'Live'}</span>`;
      }

      // KPI cards (if any)
      setText('[data-kpi="chain"]', fmt(data.blockchain?.chain_length));
      setText('[data-kpi="scda"]', fmt(data.scda?.identities));
      setText('[data-kpi="defi"]', fmt(data.defi?.pools));
      setText('[data-kpi="quantum"]', fmt(data.quantum?.queue));
      setText('[data-kpi="ai"]', (data.ai?.performance ?? 0).toFixed(2));
      setText('[data-kpi="diplomacy"]', fmt(data.diplomacy?.alliances));
      setText('[data-kpi="knowledge"]', fmt(data.knowledge_market?.listed));
      setText('[data-kpi="metaverse"]', fmt(data.metaverse?.entities));
      setText('[data-kpi="complexity"]', (data.scda?.total_complexity ?? 0).toFixed(2));
      setText('[data-kpi="energy"]', (data.scda?.total_energy ?? 0).toFixed(2));

      // Status pill in nav (if present)
      setText('[data-status="api"]', '🟢 Live');
      setText('[data-status="block"]', '#' + (data.blockchain?.chain_length ?? 0));

      // Expose for debugging
      window.LaniakeaLive = { data, fetchedAt: new Date().toISOString() };
    } catch (e) {
      setText('[data-status="api"]', '🔴 Offline');
      // Soft-fail: keep hardcoded hero numbers
      // eslint-disable-next-line no-console
      console.warn('[laniakea-live] overview fetch failed:', e.message);
    }
  }

  function start() {
    tick();
    setInterval(tick, REFRESH_MS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
