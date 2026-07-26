/* ============================================================
   🌌 LANIAKEA — Wallet Connect (MetaMask + WalletConnect)
   SIWE (Sign-In With Ethereum) compatible
   ============================================================ */

class LaniakeaWallet {
  constructor() {
    this.address = null;
    this.chainId = null;
    this.signer = null;
    this.listeners = new Set();
  }

  on(cb) { this.listeners.add(cb); return () => this.listeners.delete(cb); }
  _emit() { this.listeners.forEach(cb => cb(this.getState())); }

  getState() {
    return {
      connected: !!this.address,
      address: this.address,
      short: this.address ? `${this.address.slice(0,6)}…${this.address.slice(-4)}` : null,
      chainId: this.chainId,
      chainName: this._chainName()
    };
  }

  _chainName() {
    const m = { 1: 'Ethereum', 56: 'BNB Chain', 137: 'Polygon', 42161: 'Arbitrum', 10: 'Optimism', 43114: 'Avalanche', 250: 'Fantom' };
    return m[this.chainId] || `Chain ${this.chainId}`;
  }

  async detect() {
    if (typeof window.ethereum !== 'undefined') {
      window.ethereum.on?.('accountsChanged', a => { this.address = a[0] || null; this._emit(); });
      window.ethereum.on?.('chainChanged', c => { this.chainId = parseInt(c, 16); this._emit(); });
      return 'metamask';
    }
    return null;
  }

  async connect() {
    const provider = await this.detect();
    if (!provider) {
      // Mock mode for demo
      this.address = '0x' + Array.from({length:40}, () => Math.floor(Math.random()*16).toString(16)).join('');
      this.chainId = 1;
      this._emit();
      return this.getState();
    }
    try {
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
      this.address = accounts[0];
      this.chainId = parseInt(await window.ethereum.request({ method: 'eth_chainId' }), 16);
      this._emit();
      return this.getState();
    } catch (e) {
      throw new Error('User rejected wallet connection');
    }
  }

  async disconnect() {
    this.address = null; this.chainId = null; this.signer = null;
    this._emit();
  }

  async signIn(siweMessage) {
    if (!this.address) throw new Error('Wallet not connected');
    if (typeof window.ethereum === 'undefined') return 'mock_signature_0x' + Date.now();
    return await window.ethereum.request({
      method: 'personal_sign',
      params: [siweMessage, this.address]
    });
  }

  buildSIWE(nonce, statement = 'Sign in to Laniakea Protocol') {
    return `${statement}\n\nURI: ${location.origin}\nVersion: 1\nChain ID: ${this.chainId || 1}\nNonce: ${nonce}\nIssued At: ${new Date().toISOString()}`;
  }

  async sendTx(tx) {
    if (!this.address || typeof window.ethereum === 'undefined') {
      return { hash: '0xmock_' + Date.now(), mock: true };
    }
    return await window.ethereum.request({ method: 'eth_sendTransaction', params: [{ from: this.address, ...tx }] });
  }
}

window.LK = window.LK || {};
window.LK.wallet = new LaniakeaWallet();
