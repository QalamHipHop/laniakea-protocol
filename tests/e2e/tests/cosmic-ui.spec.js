/**
 * E2E: Cosmic UI v2 — full user journey
 */
const { test, expect } = require('@playwright/test');

test.describe('Cosmic UI — Dashboard', () => {
  test('loads cosmic.html and shows hero', async ({ page }) => {
    await page.goto('/cosmic.html');
    await expect(page.locator('.hero-title')).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('.hero-title')).toContainText('تکامل');
  });

  test('displays KPI cards with live values', async ({ page }) => {
    await page.goto('/cosmic.html');
    await expect(page.locator('.kpi-card').first()).toBeVisible();
    const kpiValue = page.locator('#kpiTier');
    await expect(kpiValue).toHaveText(/T\d/);
  });

  test('navigates between all 7 routes', async ({ page }) => {
    await page.goto('/cosmic.html');
    const routes = ['evolution', 'metaverse', 'blockchain', 'governance', 'economy', 'network', 'dashboard'];
    for (const r of routes) {
      await page.click(`[data-route="${r}"]`);
      await expect(page.locator(`#route-${r}`)).toHaveClass(/active/);
    }
  });

  test('toggles language FA ↔ EN', async ({ page }) => {
    await page.goto('/cosmic.html');
    await page.click('#langToggle');
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
    await expect(page.locator('body')).toHaveAttribute('dir', 'ltr');
    await page.click('#langToggle');
    await expect(page.locator('html')).toHaveAttribute('lang', 'fa');
  });

  test('toggles theme cosmic ↔ light', async ({ page }) => {
    await page.goto('/cosmic.html');
    await page.click('#themeToggle');
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'light');
    await page.click('#themeToggle');
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'cosmic');
  });

  test('animated counters reach final values', async ({ page }) => {
    await page.goto('/cosmic.html');
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(2000);
    const counters = await page.locator('[data-counter]').allTextContents();
    counters.forEach(c => {
      expect(c).not.toBe('0');
      expect(parseFloat(c.replace(/,/g, ''))).toBeGreaterThan(0);
    });
  });
});

test.describe('Cosmic UI — Console', () => {
  test('executes status command', async ({ page }) => {
    await page.goto('/cosmic.html');
    await page.fill('#consoleInput', 'status');
    await page.press('#consoleInput', 'Enter');
    await expect(page.locator('#consoleOut')).toContainText('Network: ONLINE');
  });

  test('executes evolve command', async ({ page }) => {
    await page.goto('/cosmic.html');
    await page.fill('#consoleInput', 'evolve');
    await page.press('#consoleInput', 'Enter');
    await expect(page.locator('#consoleOut')).toContainText('ΔC computed');
  });

  test('handles unknown command gracefully', async ({ page }) => {
    await page.goto('/cosmic.html');
    await page.fill('#consoleInput', 'foobar');
    await page.press('#consoleInput', 'Enter');
    await expect(page.locator('#consoleOut')).toContainText('command not found');
  });
});

test.describe('Cosmic UI — Evolution', () => {
  test('evolve button increases tier', async ({ page }) => {
    await page.goto('/cosmic.html#/evolution');
    await page.waitForTimeout(500);
    const before = await page.locator('#dnaTier').textContent();
    await page.click('#evolveBtn');
    await page.waitForTimeout(300);
    const after = await page.locator('#dnaTier').textContent();
    expect(parseInt(after.slice(1))).toBeGreaterThan(parseInt(before.slice(1)));
  });
});

test.describe('Cosmic UI — Metaverse', () => {
  test('canvas renders on route activation', async ({ page }) => {
    await page.goto('/cosmic.html#/metaverse');
    await page.waitForTimeout(1500);
    const canvas = page.locator('#mvCanvas');
    await expect(canvas).toBeVisible();
    const box = await canvas.boundingBox();
    expect(box.width).toBeGreaterThan(0);
    expect(box.height).toBeGreaterThan(0);
  });

  test('rotation controls work', async ({ page }) => {
    await page.goto('/cosmic.html#/metaverse');
    await page.waitForTimeout(800);
    await page.click('[data-rotate="x"]');
    await page.click('[data-rotate="y"]');
    await page.click('[data-rotate="reset"]');
  });
});

test.describe('Cosmic UI — WebSocket', () => {
  test('connects (simulated or real)', async ({ page }) => {
    await page.goto('/cosmic.html');
    const connected = await page.evaluate(() => {
      return new Promise(resolve => {
        const start = Date.now();
        const check = () => {
          if (window.LK?.socket?.connected) resolve(true);
          else if (Date.now() - start > 3000) resolve(false);
          else setTimeout(check, 100);
        };
        check();
      });
    });
    expect(connected).toBe(true);
  });

  test('emits block events', async ({ page }) => {
    await page.goto('/cosmic.html');
    const received = await page.evaluate(() => {
      return new Promise(resolve => {
        const events = [];
        window.LK.socket.on('block', d => events.push(d));
        setTimeout(() => resolve(events.length > 0), 5000);
      });
    });
    expect(received).toBe(true);
  });
});

test.describe('Cosmic UI — Wallet', () => {
  test('wallet module loads', async ({ page }) => {
    await page.goto('/cosmic.html');
    const loaded = await page.evaluate(() => !!window.LK?.wallet);
    expect(loaded).toBe(true);
  });

  test('connectBtn triggers flow', async ({ page }) => {
    await page.goto('/cosmic.html');
    await page.click('#connectBtn');
    await expect(page.locator('#toast')).toBeVisible({ timeout: 3000 });
  });
});

test.describe('Landing Page', () => {
  test('renders hero', async ({ page }) => {
    await page.goto('/landing.html');
    await expect(page.locator('.lhero-title')).toBeVisible();
  });

  test('has 6 pillars', async ({ page }) => {
    await page.goto('/landing.html');
    const pillars = page.locator('.lpillar');
    await expect(pillars).toHaveCount(6);
  });

  test('CTA links to cosmic UI', async ({ page }) => {
    await page.goto('/landing.html');
    const cta = page.locator('a[href="cosmic.html"]').first();
    await expect(cta).toBeVisible();
  });
});

test.describe('Mobile PWA', () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test('mobile UI loads', async ({ page }) => {
    await page.goto('/mobile/index.html');
    await expect(page.locator('.app-header')).toBeVisible();
    await expect(page.locator('.bottom-nav')).toBeVisible();
  });

  test('switches between tabs', async ({ page }) => {
    await page.goto('/mobile/index.html');
    await page.click('[data-page="evo"]');
    await expect(page.locator('#p-evo')).toHaveClass(/active/);
    await page.click('[data-page="wallet"]');
    await expect(page.locator('#p-wallet')).toHaveClass(/active/);
  });

  test('manifest.json is valid', async ({ request }) => {
    const r = await request.get('/mobile/manifest.json');
    expect(r.ok()).toBe(true);
    const data = await r.json();
    expect(data.name).toBeTruthy();
    expect(data.icons.length).toBeGreaterThan(0);
  });
});
