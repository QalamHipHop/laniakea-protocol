"""
Tests for rate limiting middleware & API safety.
"""
import os
import time
import pytest
from unittest.mock import MagicMock, patch


class TestRateLimitConfig:
    """Validate rate limit configuration."""

    def test_env_has_rate_limit_vars(self):
        env = Path(__file__).parent.parent / ".env.example"
        if not env.exists():
            pytest.skip(".env.example not present")
        content = env.read_text()
        assert "RATE_LIMIT" in content or "rate" in content.lower()

    def test_nginx_rate_limit_configured(self):
        nginx = Path(__file__).parent.parent / "nginx" / "nginx.cosmic.conf"
        if not nginx.exists():
            pytest.skip("nginx.cosmic.conf not present")
        content = nginx.read_text()
        assert "limit_req_zone" in content
        assert "rate=" in content


class TestAPIProtection:
    """Validate API middleware exists and is wired."""

    def test_middleware_module_exists(self):
        mw = Path(__file__).parent.parent / "laniakea" / "api" / "middleware.py"
        assert mw.exists(), "API middleware module missing"

    def test_middleware_has_rate_limiter(self):
        mw = Path(__file__).parent.parent / "laniakea" / "api" / "middleware.py"
        content = mw.read_text().lower()
        assert "rate" in content or "limit" in content

    def test_security_headers_in_nginx(self):
        nginx = Path(__file__).parent.parent / "nginx" / "nginx.cosmic.conf"
        if not nginx.exists():
            pytest.skip("nginx.cosmic.conf not present")
        content = nginx.read_text()
        assert "X-Frame-Options" in content
        assert "X-Content-Type-Options" in content


class TestAuthFlow:
    """Validate JWT auth integration."""

    def test_security_module_exists(self):
        sec = Path(__file__).parent.parent / "laniakea" / "security"
        assert sec.exists()
        assert (sec / "__init__.py").exists()

    def test_jwt_config_in_env(self):
        env = Path(__file__).parent.parent / ".env.example"
        if not env.exists():
            pytest.skip(".env.example missing")
        content = env.read_text()
        assert "JWT" in content or "jwt" in content

    def test_api_has_auth_endpoints(self):
        api = Path(__file__).parent.parent / "laniakea" / "api"
        if not api.exists():
            pytest.skip("api module missing")
        # Check for some auth pattern
        found = False
        for f in api.glob("*.py"):
            if "auth" in f.read_text(errors="ignore").lower() or "jwt" in f.read_text(errors="ignore").lower():
                found = True
                break
        assert found, "No auth/JWT code found in API"


class TestErrorPages:
    """Validate error pages exist."""

    def test_404_exists(self):
        assert (Path(__file__).parent.parent / "web" / "404.html").exists()

    def test_500_exists(self):
        assert (Path(__file__).parent.parent / "web" / "500.html").exists()

    def test_404_has_back_link(self):
        html = (Path(__file__).parent.parent / "web" / "404.html").read_text()
        assert "cosmic.html" in html or "landing.html" in html


class TestDockerfile:
    """Validate production deployment config."""

    def test_dockerfile_exists(self):
        assert (Path(__file__).parent.parent / "Dockerfile").exists()

    def test_dockerfile_uses_multi_stage(self):
        df = (Path(__file__).parent.parent / "Dockerfile").read_text()
        assert "FROM" in df
        # Should build UI
        assert "npm" in df.lower() or "node" in df.lower() or "vite" in df.lower()

    def test_dockerfile_exposes_port(self):
        df = (Path(__file__).parent.parent / "Dockerfile").read_text()
        assert "EXPOSE" in df

    def test_dockerfile_has_healthcheck(self):
        df = (Path(__file__).parent.parent / "Dockerfile").read_text()
        assert "HEALTHCHECK" in df

    def test_nginx_cosmic_config_exists(self):
        assert (Path(__file__).parent.parent / "nginx" / "nginx.cosmic.conf").exists()


class TestSecurityAudit:
    """Validate security audit tool."""

    def test_audit_script_exists(self):
        assert (Path(__file__).parent.parent / "scripts" / "security_audit.py").exists()

    def test_audit_runs_bandit(self):
        script = (Path(__file__).parent.parent / "scripts" / "security_audit.py").read_text()
        assert "bandit" in script.lower()

    def test_audit_runs_safety(self):
        script = (Path(__file__).parent.parent / "scripts" / "security_audit.py").read_text()
        assert "safety" in script.lower()

    def test_audit_checks_secrets(self):
        script = (Path(__file__).parent.parent / "scripts" / "security_audit.py").read_text()
        assert "github_token" in script or "private_key" in script


class TestI18n:
    """Validate i18n JSON files."""

    def test_fa_exists(self):
        p = Path(__file__).parent.parent / "web" / "i18n" / "fa.json"
        assert p.exists()
        import json
        data = json.loads(p.read_text())
        assert data["lang"] == "fa"
        assert data["dir"] == "rtl"
        assert len(data["strings"]) > 30

    def test_en_exists(self):
        p = Path(__file__).parent.parent / "web" / "i18n" / "en.json"
        assert p.exists()
        import json
        data = json.loads(p.read_text())
        assert data["lang"] == "en"
        assert data["dir"] == "ltr"
        assert len(data["strings"]) > 30

    def test_keys_match(self):
        import json
        fa = json.loads((Path(__file__).parent.parent / "web" / "i18n" / "fa.json").read_text())
        en = json.loads((Path(__file__).parent.parent / "web" / "i18n" / "en.json").read_text())
        assert set(fa["strings"].keys()) == set(en["strings"].keys()), "i18n keys mismatch"


class TestE2E:
    """Validate e2e test setup."""

    def test_playwright_config_exists(self):
        assert (Path(__file__).parent.parent / "tests" / "e2e" / "playwright.config.js").exists()

    def test_spec_file_exists(self):
        specs = list((Path(__file__).parent.parent / "tests" / "e2e" / "tests").glob("*.spec.js"))
        assert len(specs) > 0

    def test_spec_has_test_blocks(self):
        spec = next((Path(__file__).parent.parent / "tests" / "e2e" / "tests").glob("*.spec.js"))
        content = spec.read_text()
        assert content.count("test(") >= 10


from pathlib import Path
