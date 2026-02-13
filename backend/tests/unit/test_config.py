"""Tests for multi-LLM provider configuration."""
import os

import pytest


class TestLLMEnabled:

    def test_azure_enabled_with_endpoint_env_reload(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "azure")
        monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://my.openai.azure.com")
        # Reload settings to pick up monkeypatched env
        import importlib
        import app.config as cfg_module
        importlib.reload(cfg_module)
        assert cfg_module.Settings().llm_enabled() is True

    def test_azure_disabled_without_endpoint_env(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "azure")
        monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
        from app.config import Settings
        s = Settings()
        s.AZURE_OPENAI_ENDPOINT = None
        assert s.llm_enabled() is False

    def test_azure_enabled_with_endpoint(self):
        from app.config import Settings
        s = Settings()
        s.LLM_PROVIDER = "azure"
        s.AZURE_OPENAI_ENDPOINT = "https://my.openai.azure.com"
        assert s.llm_enabled() is True

    def test_azure_disabled_without_endpoint(self):
        from app.config import Settings
        s = Settings()
        s.LLM_PROVIDER = "azure"
        s.AZURE_OPENAI_ENDPOINT = None
        assert s.llm_enabled() is False

    def test_github_enabled_with_token(self):
        from app.config import Settings
        s = Settings()
        s.LLM_PROVIDER = "github"
        s.GITHUB_TOKEN = "ghp_test"
        assert s.llm_enabled() is True

    def test_github_disabled_without_token(self):
        from app.config import Settings
        s = Settings()
        s.LLM_PROVIDER = "github"
        s.GITHUB_TOKEN = None
        assert s.llm_enabled() is False
    
