"""タスク登録画面(GET/POST /tasks-list/new)のテスト。"""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
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


def test_new_task_form_returns_200():
    """登録フォーム画面にアクセスすると200が返る。"""
    client = _make_client()

    response = client.get("/tasks-list/new")

    assert response.status_code == 200
    assert "新規タスク登録" in response.text

    app.dependency_overrides.clear()


def test_submitting_form_creates_task_and_redirects_to_list():
    """フォーム送信でタスクが登録され、一覧画面へリダイレクトされる。"""
    client = _make_client()

    response = client.post(
        "/tasks-list/new",
        data={
            "title": "設計書を書く",
            "priority": "高",
            "status": "対応中",
            "due_date": "2026-09-10",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/tasks-list"

    list_response = client.get("/tasks-list")
    assert "設計書を書く" in list_response.text

    app.dependency_overrides.clear()


def test_submitting_form_with_minimal_fields_uses_defaults():
    """タイトルのみ入力した場合、既定値で登録される。"""
    client = _make_client()

    response = client.post(
        "/tasks-list/new",
        data={"title": "読書"},
        follow_redirects=False,
    )

    assert response.status_code == 303

    list_response = client.get("/tasks-list")
    assert "読書" in list_response.text
    assert "中" in list_response.text
    assert "未着手" in list_response.text

    app.dependency_overrides.clear()


def test_submitting_form_with_empty_title_shows_error():
    """タイトル未入力の場合、フォームにエラーが表示される。"""
    client = _make_client()

    response = client.post(
        "/tasks-list/new",
        data={"title": ""},
    )

    assert response.status_code == 422
    assert "alert-danger" in response.text


def test_submitting_form_with_empty_title_retains_other_values():
    """タイトル未入力エラー時、他の入力値が保持される。"""
    client = _make_client()

    response = client.post(
        "/tasks-list/new",
        data={"title": "", "priority": "高", "description": "詳細説明"},
    )

    assert response.status_code == 422
    assert 'value="高"' in response.text or "高" in response.text
    assert "詳細説明" in response.text