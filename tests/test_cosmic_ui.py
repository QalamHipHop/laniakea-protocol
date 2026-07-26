"""
Test suite for the Cosmic UI v2 — static assets validation.
Validates HTML/CSS/JS files exist, are well-formed, and reference each other correctly.
"""
import os
import re
import json
from pathlib import Path

import pytest

WEB_DIR = Path(__file__).parent.parent / "web"


class TestCosmicUI:
    """Tests for the Cosmic UI v2 frontend."""

    def test_cosmic_html_exists(self):
        assert (WEB_DIR / "cosmic.html").exists()

    def test_cosmic_css_exists(self):
        assert (WEB_DIR / "cosmic.css").exists()

    def test_cosmic_js_exists(self):
        assert (WEB_DIR / "cosmic.js").exists()

    def test_cosmic_ws_js_exists(self):
        assert (WEB_DIR / "cosmic-ws.js").exists()

    def test_cosmic_wallet_js_exists(self):
        assert (WEB_DIR / "cosmic-wallet.js").exists()

    def test_landing_page_exists(self):
        assert (WEB_DIR / "landing.html").exists()
        assert (WEB_DIR / "landing.css").exists()
        assert (WEB_DIR / "landing.js").exists()

    def test_html_includes_required_libraries(self):
        html = (WEB_DIR / "cosmic.html").read_text()
        assert "tailwindcss" in html or "tailwind" in html
        assert "chart.js" in html or "Chart" in html
        assert "cosmic.css" in html
        assert "cosmic.js" in html

    def test_html_has_7_routes(self):
        html = (WEB_DIR / "cosmic.html").read_text()
        routes = ["dashboard", "evolution", "metaverse", "blockchain", "governance", "economy", "network"]
        for route in routes:
            assert f'id="route-{route}"' in html, f"Missing route: {route}"

    def test_html_is_rtl_aware(self):
        html = (WEB_DIR / "cosmic.html").read_text()
        assert 'dir="rtl"' in html
        assert 'lang="fa"' in html

    def test_js_has_spa_router(self):
        js = (WEB_DIR / "cosmic.js").read_text()
        assert "initRouter" in js
        assert "hashchange" in js or "hash" in js

    def test_js_has_i18n(self):
        js = (WEB_DIR / "cosmic.js").read_text()
        assert "I18N" in js
        assert "'fa'" in js and "'en'" in js

    def test_js_has_console(self):
        js = (WEB_DIR / "cosmic.js").read_text()
        assert "consoleForm" in js
        assert "consoleInput" in js

    def test_js_has_live_feed(self):
        js = (WEB_DIR / "cosmic.js").read_text()
        assert "activityFeed" in js
        assert "setInterval" in js

    def test_css_has_glassmorphism(self):
        css = (WEB_DIR / "cosmic.css").read_text()
        assert "backdrop-filter" in css
        assert "blur(" in css

    def test_css_has_dark_and_light_themes(self):
        css = (WEB_DIR / "cosmic.css").read_text()
        assert "[data-theme=\"cosmic\"]" in css
        assert "[data-theme=\"light\"]" in css

    def test_css_is_responsive(self):
        css = (WEB_DIR / "cosmic.css").read_text()
        assert "@media" in css
        assert "max-width" in css


class TestMobilePWA:
    """Tests for the mobile PWA."""

    def test_mobile_html_exists(self):
        assert (WEB_DIR / "mobile" / "index.html").exists()

    def test_mobile_manifest_exists(self):
        manifest = WEB_DIR / "mobile" / "manifest.json"
        assert manifest.exists()
        data = json.loads(manifest.read_text())
        assert data["name"]
        assert data["start_url"]
        assert data["display"] == "standalone"
        assert len(data["icons"]) >= 1

    def test_mobile_service_worker_exists(self):
        assert (WEB_DIR / "mobile" / "sw.js").exists()
        sw = (WEB_DIR / "mobile" / "sw.js").read_text()
        assert "caches.open" in sw
        assert "install" in sw
        assert "fetch" in sw

    def test_mobile_has_bottom_nav(self):
        html = (WEB_DIR / "mobile" / "index.html").read_text()
        assert "bottom-nav" in html
        assert "nav-item" in html

    def test_mobile_has_wallet_integration(self):
        html = (WEB_DIR / "mobile" / "index.html").read_text()
        assert "mConnect" in html or "walletBtn" in html

    def test_mobile_js_exists(self):
        assert (WEB_DIR / "mobile" / "js" / "mobile.js").exists()
        js = (WEB_DIR / "mobile" / "js" / "mobile.js").read_text()
        assert "ethereum" in js
        assert "eth_requestAccounts" in js


class TestLanding:
    """Tests for the landing page."""

    def test_landing_has_hero(self):
        html = (WEB_DIR / "landing.html").read_text()
        assert "lhero" in html
        assert "ابرپروکل" in html or "تکامل" in html

    def test_landing_has_features_section(self):
        html = (WEB_DIR / "landing.html").read_text()
        assert "id=\"features\"" in html
        assert "lpillar" in html

    def test_landing_has_cta(self):
        html = (WEB_DIR / "landing.html").read_text()
        assert "lcta" in html

    def test_landing_links_to_cosmic_ui(self):
        html = (WEB_DIR / "landing.html").read_text()
        assert "cosmic.html" in html


class TestWebSocket:
    """Tests for the WebSocket client."""

    def test_has_reconnect(self):
        js = (WEB_DIR / "cosmic-ws.js").read_text()
        assert "reconnect" in js.lower()
        assert "onclose" in js

    def test_has_event_emitter(self):
        js = (WEB_DIR / "cosmic-ws.js").read_text()
        assert "listeners" in js
        assert "_emit" in js
        assert "on(" in js

    def test_has_simulation_fallback(self):
        js = (WEB_DIR / "cosmic-ws.js").read_text()
        assert "_simulate" in js
        assert "sim" in js


class TestWallet:
    """Tests for the wallet connector."""

    def test_supports_metamask(self):
        js = (WEB_DIR / "cosmic-wallet.js").read_text()
        assert "ethereum" in js
        assert "eth_requestAccounts" in js

    def test_supports_siwe(self):
        js = (WEB_DIR / "cosmic-wallet.js").read_text()
        assert "siwe" in js.lower() or "Sign-In" in js or "personal_sign" in js

    def test_handles_chain_changes(self):
        js = (WEB_DIR / "cosmic-wallet.js").read_text()
        assert "chainChanged" in js or "chainId" in js


class TestCI:
    """Tests for CI/CD configuration."""

    def test_ci_workflow_exists(self):
        ci = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"
        assert ci.exists()
        content = ci.read_text()
        assert "pytest" in content or "test" in content.lower()

    def test_release_workflow_exists(self):
        rel = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"
        assert rel.exists()


class TestMonitoring:
    """Tests for monitoring config."""

    def test_grafana_dashboard_exists(self):
        dash = Path(__file__).parent.parent / "monitoring" / "grafana" / "laniakea-dashboard.json"
        assert dash.exists()
        data = json.loads(dash.read_text())
        assert data["title"]
        assert len(data["panels"]) >= 5

    def test_dashboard_has_key_metrics(self):
        dash = Path(__file__).parent.parent / "monitoring" / "grafana" / "laniakea-dashboard.json"
        data = json.loads(dash.read_text())
        titles = [p["title"] for p in data["panels"]]
        assert any("SCDA" in t or "scda" in t for t in titles)
        assert any("Block" in t for t in titles)
        assert any("Peer" in t for t in titles)


class TestOpenAPI:
    """Tests for OpenAPI documentation."""

    def test_openapi_exists(self):
        spec = Path(__file__).parent.parent / "docs" / "api" / "openapi.yaml"
        assert spec.exists()

    def test_openapi_is_valid(self):
        spec = Path(__file__).parent.parent / "docs" / "api" / "openapi.yaml"
        content = spec.read_text()
        assert content.startswith("openapi:")
        assert "3.0" in content
        assert "paths:" in content
        assert "/api/v1/scda" in content
        assert "/api/v1/blockchain" in content

    def test_openapi_has_schemas(self):
        spec = Path(__file__).parent.parent / "docs" / "api" / "openapi.yaml"
        content = spec.read_text()
        assert "components:" in content
        assert "SCDA:" in content
        assert "Block:" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
