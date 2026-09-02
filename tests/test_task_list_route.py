"""GET /tasks-list (タスク一覧画面)のテスト。"""
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


def test_task_list_returns_200():
    """一覧画面にアクセスすると200が返る。"""
    client = _make_client()

    response = client.get("/tasks-list")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    app.dependency_overrides.clear()


def test_task_list_shows_placeholder_when_empty():
    """タスクが0件の場合、案内文が表示される。"""
    client = _make_client()

    response = client.get("/tasks-list")

    assert "タスクがまだ登録されていません" in response.text

    app.dependency_overrides.clear()


def test_task_list_shows_main_fields():
    """タイトル・優先度・状態・期限が表示される。"""
    client = _make_client()
    client.post(
        "/tasks",
        json={
            "title": "設計書を書く",
            "priority": "高",
            "status": "対応中",
            "due_date": "2026-09-10",
        },
    )

    response = client.get("/tasks-list")

    assert response.status_code == 200
    body = response.text
    assert "設計書を書く" in body
    assert "高" in body
    assert "対応中" in body
    assert "2026-09-10" in body

    app.dependency_overrides.clear()


def test_task_list_shows_edit_and_delete_buttons():
    """編集・削除の操作ボタンが表示される。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "読書"}).json()

    response = client.get("/tasks-list")

    assert response.status_code == 200
    body = response.text
    assert f"/tasks-list/{created['id']}/edit" in body
    assert "編集" in body
    assert "削除" in body

    app.dependency_overrides.clear()


def test_task_list_shows_new_registration_link():
    """新規登録リンクが表示される。"""
    client = _make_client()

    response = client.get("/tasks-list")

    assert "/tasks-list/new" in response.text

    app.dependency_overrides.clear()