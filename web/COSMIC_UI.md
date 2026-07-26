# 🌌 Laniakea Protocol — Cosmic UI v2

A complete **modern, glassmorphism, cyber-cosmic** frontend for the Laniakea Protocol — built with vanilla JS (no build step), Tailwind CDN, Chart.js, GSAP, and Three.js.

## ✨ Features

- 🎨 **Glassmorphism + Neon** design system with cosmic gradients
- 🌟 **Animated starfield** background (canvas, 220 stars)
- 🧭 **SPA routing** via hash (dashboard / evolution / metaverse / blockchain / governance / economy / network)
- 🌍 **Bilingual** (FA + EN) with live toggle
- 🌓 **Light/Dark** theme switcher
- 📊 **Live charts** (Chart.js) — Evolution curve, P2P map, Tier doughnut, Treasury bars, Price line, Geo polar
- 🌐 **3D Hypercube Metaverse** — 16 vertices / 32 edges 8D→3D projection, rotatable on X/Y/Z
- 🖥️ **Command console** with 10+ commands (`status`, `evolve`, `mine`, `peers`, `blocks`, `balance`, `dna`, `hard`, `whoami`, `clear`)
- 📡 **Live activity feed** with auto-scroll + pause
- 🔢 **Animated counters** on hero stats (IntersectionObserver)
- 🧬 **DNA helix** visualization
- 💎 **NFT grid, staking, governance proposals** with progress bars
- ⌨️ **Responsive** (mobile menu, adaptive grids)

## 📁 Files

| File | Purpose |
|---|---|
| `cosmic.html` | Single-page app entry (RTL/LTR aware) |
| `cosmic.css`  | Design system, animations, components |
| `cosmic.js`   | SPA router, charts, metaverse, i18n, console, live feed |

## 🚀 Usage

Just open `cosmic.html` in a browser, or serve the `web/` directory:

```bash
cd web && python3 -m http.server 8080
# open http://localhost:8080/cosmic.html
```

To integrate with the live API, set `window.LANIAKEA_API = 'https://your-api.onrender.com'` before loading `cosmic.js`.

## 🎯 Design Principles

1. **Cosmic-first** — color palette inspired by nebulae: violet (#7c3aed), cyan (#06b6d4), pink (#ec4899), amber (#f59e0b)
2. **Performance** — all animations GPU-friendly (transform/opacity), 60fps
3. **Accessibility** — keyboard-friendly, ARIA labels, RTL support
4. **No build step** — drop in and serve, perfect for static hosts (Render, GitHub Pages, Vercel)
5. **Bilingual first** — designed for Persian + English, with proper RTL/LTR switching

---

*Built for the cosmic web 🌌*
