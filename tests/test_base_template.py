"""共通レイアウトテンプレート(base.html)の構造テスト。"""
from pathlib import Path

BASE_HTML = Path("app/templates/base.html").read_text(encoding="utf-8")


def test_base_template_has_viewport_meta_for_responsiveness():
    """スマホ対応のviewportメタタグがある。"""
    assert 'name="viewport"' in BASE_HTML


def test_base_template_has_bootstrap_css():
    """Bootstrap 5のCSSが読み込まれている。"""
    assert "bootstrap@5" in BASE_HTML
    assert ".min.css" in BASE_HTML


def test_base_template_has_bootstrap_js():
    """Bootstrap 5のJS(トグルメニュー動作用)が読み込まれている。"""
    assert "bootstrap.bundle.min.js" in BASE_HTML


def test_base_template_has_responsive_nav_toggler():
    """スマホ用のハンバーガーメニュー(トグラー)がある。"""
    assert "navbar-toggler" in BASE_HTML
    assert "navbar-expand-lg" in BASE_HTML


def test_base_template_has_navigation_links():
    """主要なナビゲーションリンクが含まれる。"""
    assert "ダッシュボード" in BASE_HTML
    assert "タスク一覧" in BASE_HTML
    assert "新規タスク登録" in BASE_HTML


def test_base_template_has_content_block():
    """子テンプレートがコンテンツを差し込むブロックがある。"""
    assert "{% block content %}" in BASE_HTML