"""登録・編集フォームの項目別エラー表示のテスト。"""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.error_messages import build_field_errors
from app.main import app


def _make_client() -> TestClient:
    """インメモリDBを使うテスト用クライアントを作成する。"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    testing_session_local = sessionmaker(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_build_field_errors_maps_missing_title():
    """titleが未入力の場合、日本語メッセージに変換される。"""
    errors = [{"loc": ("title",), "type": "string_too_short", "msg": "..."}]

    result = build_field_errors(errors)

    assert result["title"] == "タイトルを入力してください。"


def test_build_field_errors_maps_title_too_long():
    """titleが長すぎる場合、日本語メッセージに変換される。"""
    errors = [{"loc": ("title",), "type": "string_too_long", "msg": "..."}]

    result = build_field_errors(errors)

    assert "タイトル" in result["title"]
    assert "上限" in result["title"]


def test_build_field_errors_maps_invalid_enum():
    """priorityが不正な値の場合、日本語メッセージに変換される。"""
    errors = [{"loc": ("priority",), "type": "enum", "msg": "..."}]

    result = build_field_errors(errors)

    assert result["priority"] == "優先度の値が正しくありません。"


def test_create_form_shows_japanese_error_next_to_title_field():
    """登録フォームで、タイトル欄の直下に日本語エラーが表示される。"""
    client = _make_client()

    response = client.post("/tasks-list/new", data={"title": ""})

    assert response.status_code == 422
    body = response.text
    assert "タイトルを入力してください" in body
    assert 'id="title"' in body
    assert "is-invalid" in body

    app.dependency_overrides.clear()


def test_create_form_retains_values_alongside_field_errors():
    """エラー時、他の入力値も保持されたまま項目別エラーが表示される。"""
    client = _make_client()

    response = client.post(
        "/tasks-list/new",
        data={"title": "", "priority": "高", "description": "詳細説明"},
    )

    assert response.status_code == 422
    body = response.text
    assert "タイトルを入力してください" in body
    assert "詳細説明" in body

    app.dependency_overrides.clear()


def test_edit_form_shows_japanese_error_next_to_title_field():
    """編集フォームで、タイトル欄の直下に日本語エラーが表示される。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "タスク"}).json()

    response = client.post(f"/tasks-list/{created['id']}/edit", data={"title": ""})

    assert response.status_code == 422
    body = response.text
    assert "タイトルを入力してください" in body
    assert "is-invalid" in body

    app.dependency_overrides.clear()


def test_create_form_shows_title_too_long_error():
    """タイトルが101文字の場合、文字数超過の日本語エラーが表示される。"""
    client = _make_client()

    response = client.post("/tasks-list/new", data={"title": "あ" * 101})

    assert response.status_code == 422
    assert "上限" in response.text

    app.dependency_overrides.clear()
