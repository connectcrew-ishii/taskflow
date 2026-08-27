"""GET /tasksのsortクエリパラメータのテスト。"""
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


def test_sort_by_priority_asc_query_param():
    """sort=priority_ascで優先度順に並ぶ。"""
    client = _make_client()
    client.post("/tasks", json={"title": "低", "priority": "低"})
    client.post("/tasks", json={"title": "重要", "priority": "重要"})

    response = client.get("/tasks?sort=priority_asc")

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()["items"]]
    assert titles == ["重要", "低"]

    app.dependency_overrides.clear()


def test_sort_by_due_date_asc_query_param():
    """sort=due_date_ascで期限が近い順に並ぶ。"""
    client = _make_client()
    client.post("/tasks", json={"title": "遠い", "due_date": "2026-12-31"})
    client.post("/tasks", json={"title": "近い", "due_date": "2026-09-01"})

    response = client.get("/tasks?sort=due_date_asc")

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()["items"]]
    assert titles == ["近い", "遠い"]

    app.dependency_overrides.clear()


def test_sort_returns_422_for_invalid_value():
    """許可されていないsort値は422になる。"""
    client = _make_client()

    response = client.get("/tasks?sort=invalid_value")

    assert response.status_code == 422

    app.dependency_overrides.clear()