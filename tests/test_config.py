"""Tests for the unified configuration layer.

These tests pin the *contract* of both the new
``laniakea.core.config.settings`` singleton (pydantic-settings) and the
legacy ``laniakea.utils.config.get_config()`` dataclass shim.

The goal is to make sure the two stay in lock-step as the project evolves.
"""

from __future__ import annotations

import os

import pytest


def test_settings_loads_defaults():
    from laniakea.core.config import settings

    assert settings.PROJECT_NAME == "Laniakea Protocol"
    assert settings.API_PORT == 8000
    assert settings.TOTAL_TOKEN_SUPPLY == 1_000_000_000
    assert settings.AUTHORITIES, "AUTHORITIES must default to a non-empty list"
    assert "Validator_A" in settings.AUTHORITIES


def test_settings_overrides_via_env(monkeypatch):
    monkeypatch.setenv("API_PORT", "9123")
    monkeypatch.setenv("TOKEN_SYMBOL", "TEST")
    # Pydantic-settings reads env at instantiation, so re-import.
    import importlib
    from laniakea.core import config as cfg_mod

    importlib.reload(cfg_mod)
    assert cfg_mod.settings.API_PORT == 9123
    assert cfg_mod.settings.TOKEN_SYMBOL == "TEST"
    # Restore defaults
    monkeypatch.delenv("API_PORT", raising=False)
    monkeypatch.delenv("TOKEN_SYMBOL", raising=False)
    importlib.reload(cfg_mod)


def test_config_compat_class_proxies():
    from laniakea.core.config import Config, settings

    # The compat class must mirror the singleton.
    assert Config.PROJECT_NAME == settings.PROJECT_NAME
    assert Config.API_PORT == settings.API_PORT
    Config.PROJECT_NAME = "Renamed"
    assert settings.PROJECT_NAME == "Renamed"
    # Reset
    settings.PROJECT_NAME = "Laniakea Protocol"


def test_legacy_get_config_returns_dataclass():
    from laniakea.utils.config import get_config

    cfg = get_config()
    # Legacy dataclass attributes must still be reachable.
    assert cfg.blockchain.difficulty == 4
    assert cfg.network.host == "0.0.0.0"
    assert cfg.ai.enabled is True


def test_legacy_config_get_set_classmethods():
    from laniakea.utils.config import Config

    # .get() must read from env (backward compat with old call-sites).
    assert Config.get("__LANIAKEA_NONEXISTENT__", "fallback") == "fallback"
    # .set() must persist back to os.environ.
    Config.set("__LANIAKEA_TEST_KEY__", "hello")
    assert os.getenv("__LANIAKEA_TEST_KEY__") == "hello"
    del os.environ["__LANIAKEA_TEST_KEY__"]


def test_legacy_import_path_does_not_break():
    """network/api.py and external_apis/integrations.py import from here.

    We don't load those modules here (they have heavy deps), but we do
    import the symbol they reach for at import time.
    """
    from laniakea.utils.config import Config  # noqa: F401

    assert hasattr(Config, "get")
    assert hasattr(Config, "set")


def test_to_public_dict_redacts_secrets():
    from laniakea.core.config import settings

    out = settings.to_public_dict()
    assert "SECRET_KEY" in out
    assert out["SECRET_KEY"] == "***"
    assert out["OPENAI_API_KEY"] == "***"
    assert "POSTGRES_PASSWORD" in out and out["POSTGRES_PASSWORD"] == "***"
    # Public values stay readable.
    assert out["PROJECT_NAME"] == settings.PROJECT_NAME
