"""POST /tasks APIのテスト。"""
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


def test_create_task_returns_201_with_required_fields_only():
    """titleのみ指定した場合、201と既定値が設定されたタスクを返す。"""
    client = _make_client()

    response = client.post("/tasks", json={"title": "設計書を書く"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "設計書を書く"
    assert body["priority"] == "中"
    assert body["status"] == "未着手"
    assert body["id"] is not None
    assert body["created_at"] is not None

    app.dependency_overrides.clear()


def test_create_task_returns_201_with_all_fields():
    """全項目を指定して登録できる。"""
    client = _make_client()

    response = client.post(
        "/tasks",
        json={
            "title": "API設計書を作成する",
            "description": "OpenAPI仕様を整備する",
            "priority": "高",
            "status": "対応中",
            "due_date": "2026-09-10",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["priority"] == "高"
    assert body["status"] == "対応中"
    assert body["due_date"] == "2026-09-10"

    app.dependency_overrides.clear()


def test_create_task_returns_422_for_empty_title():
    """titleが空文字の場合は422になる。"""
    client = _make_client()

    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_create_task_returns_422_for_title_over_100_chars():
    """titleが101文字の場合は422になる。"""
    client = _make_client()

    response = client.post("/tasks", json={"title": "あ" * 101})

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_create_task_returns_422_for_invalid_priority():
    """priorityが許可値以外の場合は422になる。"""
    client = _make_client()

    response = client.post("/tasks", json={"title": "タスク", "priority": "不明"})

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_create_task_returns_422_for_missing_title():
    """titleが未指定の場合は422になる。"""
    client = _make_client()

    response = client.post("/tasks", json={})

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_created_task_is_retrievable_via_list():
    """登録したタスクが一覧取得にも反映される。"""
    client = _make_client()
    client.post("/tasks", json={"title": "読書"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json()["total"] == 1

    app.dependency_overrides.clear()
