"""GET /tasksのフィルタ機能テスト。"""
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


def test_filter_by_status_query_param():
    """statusクエリパラメータで絞り込める。"""
    client = _make_client()
    client.post("/tasks", json={"title": "タスク1", "status": "対応中"})
    client.post("/tasks", json={"title": "タスク2", "status": "完了"})

    response = client.get("/tasks?status=対応中")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "対応中"

    app.dependency_overrides.clear()


def test_filter_by_priority_query_param():
    """priorityクエリパラメータで絞り込める。"""
    client = _make_client()
    client.post("/tasks", json={"title": "タスク1", "priority": "高"})
    client.post("/tasks", json={"title": "タスク2", "priority": "低"})

    response = client.get("/tasks?priority=高")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["priority"] == "高"

    app.dependency_overrides.clear()


def test_filter_by_overdue_query_param():
    """overdueクエリパラメータで絞り込める。"""
    client = _make_client()
    client.post(
        "/tasks",
        json={"title": "期限切れ", "due_date": "2020-01-01", "status": "対応中"},
    )
    client.post("/tasks", json={"title": "期限なし"})

    response = client.get("/tasks?overdue=true")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "期限切れ"

    app.dependency_overrides.clear()


def test_no_filter_returns_all_tasks():
    """フィルタ未指定の場合は全件返る。"""
    client = _make_client()
    client.post("/tasks", json={"title": "タスク1"})
    client.post("/tasks", json={"title": "タスク2"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json()["total"] == 2

    app.dependency_overrides.clear()