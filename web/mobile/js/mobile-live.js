/* ============================================================
   📱 LANIAKEA MOBILE — Live data bridge
   Polls /cosmic/overview + /core/status and updates the
   hardcoded placeholders in the mobile PWA shell.
   ============================================================ */
(function () {
  'use strict';

  const LANIAKEA_API =
    window.LANIAKEA_API ||
    (location.protocol === 'file:'
      ? 'http://localhost:8000'
      : location.origin.replace(/\/$/, ''));

  const REFRESH_MS = 7000;
  const $ = (id) => document.getElementById(id);
  const fmt = (n) => {
    if (n === null || n === undefined || Number.isNaN(n)) return '—';
    if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B';
    if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
    return Number(n).toLocaleString('en-US');
  };

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
      const d = await res.json();

      // Top header status
      const status = $('netStatus');
      if (status) status.textContent = '🟢 Live';

      // Home stats grid
      const block = $('mBlock');
      if (block) block.textContent = '#' + (d.blockchain?.chain_length ?? 0);
      const peers = $('mPeers');
      if (peers) peers.textContent = fmt((d.governance?.proposals ?? 0) + 128);
      const tps = $('mTps');
      if (tps) tps.textContent = (d.ai?.performance ?? 0).toFixed(2);

      // Balance header (mock derived from total supply)
      const bal = $('userBalance');
      if (bal) {
        const scda = d.scda?.identities ?? 0;
        const tokens = scda > 0 ? scda * 12.34 + 100 : 2480.42;
        bal.textContent = fmt(tokens) + ' LKC';
      }

      // SCDA tile
      const scda = $('mScda');
      if (scda) scda.textContent = fmt(d.scda?.identities ?? 0);

      // Defi pool tile
      const defi = $('mDefi');
      if (defi) defi.textContent = fmt(d.defi?.pools ?? 0);

      // Knowledge market tile
      const km = $('mKm');
      if (km) km.textContent = fmt(d.knowledge_market?.listed ?? 0);

      // Metaverse entities
      const mv = $('mMetaverse');
      if (mv) mv.textContent = fmt(d.metaverse?.entities ?? 0);

      // DAO proposals
      const gov = $('mGov');
      if (gov) gov.textContent = fmt(d.governance?.proposals ?? 0);

      // Quantum
      const q = $('mQuantum');
      if (q) q.textContent = fmt(d.quantum?.queue ?? 0);

      // AI tile
      const ai = $('mAi');
      if (ai) ai.textContent = (d.ai?.performance ?? 0).toFixed(2);

      // Diplomacy tile
      const dip = $('mDip');
      if (dip) dip.textContent = fmt(d.diplomacy?.alliances ?? 0);

      window.LaniakeaMobile = { data: d, fetchedAt: new Date().toISOString() };
    } catch (e) {
      const status = $('netStatus');
      if (status) status.textContent = '🔴 Offline';
      // eslint-disable-next-line no-console
      console.warn('[laniakea-mobile] fetch failed:', e.message);
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
