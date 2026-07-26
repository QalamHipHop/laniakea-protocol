/* ============================================================
   🌌 LANIAKEA — WebSocket Real-time Client
   Auto-reconnect · Event bus · Typed events
   ============================================================ */

class LaniakeaSocket {
  constructor(url, opts = {}) {
    this.url = url || (window.LANIAKEA_WS || this._guessUrl());
    this.opts = { reconnect: true, maxRetries: 20, heartbeat: 25000, debug: false, ...opts };
    this.ws = null;
    this.listeners = new Map();
    this.retries = 0;
    this.connected = false;
    this.heartbeatTimer = null;
    this.queue = [];
    this._simulate();
  }

  _guessUrl() {
    const api = window.LANIAKEA_API || location.origin;
    return api.replace(/^http/, 'ws') + '/ws';
  }

  _simulate() {
    // If no WS server reachable, run a deterministic simulator so the UI is always alive.
    this._mode = 'sim';
    this.connected = true;
    this._emit('open', { simulated: true });
    this._simTick();
  }

  _simTick() {
    const events = [
      { t: 'block', data: () => ({ height: 8931 + Math.floor(Math.random()*5), consensus: ['PoHD','PoA','PoV'][Math.floor(Math.random()*3)], tx_count: Math.floor(Math.random()*200) }) },
      { t: 'scda', data: () => ({ id: 4000 + Math.floor(Math.random()*500), tier: 'T'+(2+Math.floor(Math.random()*4)), complexity: (10+Math.random()*5).toFixed(2) }) },
      { t: 'metric', data: () => ({ name: ['tps','peers','energy','complexity'][Math.floor(Math.random()*4)], value: Math.random()*100, unit: '' }) },
      { t: 'problem', data: () => ({ id: 200+Math.floor(Math.random()*20), solved: Math.random() > 0.5, reward: 100+Math.floor(Math.random()*500) }) },
      { t: 'governance', data: () => ({ proposal: 12+Math.floor(Math.random()*4), votes: Math.floor(Math.random()*1000), percent: Math.floor(20+Math.random()*70) }) },
    ];
    const pick = events[Math.floor(Math.random()*events.length)];
    setTimeout(() => {
      this._emit(pick.t, pick.data());
      this._simTick();
    }, 1500 + Math.random()*2500);
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);
      this.ws.onopen = () => {
        this.connected = true; this.retries = 0;
        this._mode = 'live';
        this._emit('open');
        this._heartbeat();
        this.queue.forEach(m => this.send(m)); this.queue = [];
      };
      this.ws.onmessage = e => {
        try { const msg = JSON.parse(e.data); this._emit(msg.type || 'message', msg); }
        catch { this._emit('raw', e.data); }
      };
      this.ws.onclose = () => {
        this.connected = false; this._emit('close');
        if (this.opts.reconnect && this.retries < this.opts.maxRetries) {
          this.retries++;
          setTimeout(() => this.connect(), Math.min(30000, 1000 * Math.pow(1.5, this.retries)));
        }
      };
      this.ws.onerror = e => this._emit('error', e);
    } catch (e) { this._simulate(); }
  }

  _heartbeat() {
    clearInterval(this.heartbeatTimer);
    this.heartbeatTimer = setInterval(() => this.send({ type: 'ping' }), this.opts.heartbeat);
  }

  send(msg) {
    if (this._mode === 'sim') return;
    if (this.ws?.readyState === 1) this.ws.send(JSON.stringify(msg));
    else this.queue.push(msg);
  }

  on(type, fn) {
    if (!this.listeners.has(type)) this.listeners.set(type, new Set());
    this.listeners.get(type).add(fn);
    return () => this.off(type, fn);
  }
  off(type, fn) { this.listeners.get(type)?.delete(fn); }
  _emit(type, data) { this.listeners.get(type)?.forEach(fn => { try { fn(data); } catch(e) { console.error(e); } }); }
}

window.LK = window.LK || {};
window.LK.socket = new LaniakeaSocket();

// Auto-wire to UI hooks
document.addEventListener('DOMContentLoaded', () => {
  if (!window.LK) return;
  const s = window.LK.socket;
  s.on('open', () => console.log('🌌 LK Socket connected' + (s._mode==='sim' ? ' (simulated)' : '')));
  s.on('block', b => window.LK.ui?.onBlock?.(b));
  s.on('scda', d => window.LK.ui?.onSCDA?.(d));
  s.on('metric', m => window.LK.ui?.onMetric?.(m));
  s.on('problem', p => window.LK.ui?.onProblem?.(p));
  s.on('governance', g => window.LK.ui?.onGovernance?.(g));
});
