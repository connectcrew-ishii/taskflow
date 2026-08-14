"""環境設定モジュールのテスト。"""
from app.config import DEFAULT_DATABASE_URL, get_settings


def test_default_database_url(monkeypatch):
    """環境変数未設定の場合、開発用既定値が使われる。"""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.database_url == DEFAULT_DATABASE_URL


def test_database_url_overridden_by_env(monkeypatch):
    """環境変数が設定されている場合、その値が優先される。"""
    monkeypatch.setenv("DATABASE_URL", "postgresql://example/db")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.database_url == "postgresql://example/db"
