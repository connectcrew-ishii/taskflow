"""GET /tasks/search APIのテスト。"""
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


def test_search_returns_200_with_matching_tasks():
    """検索語に一致するタスクだけ返る。"""
    client = _make_client()
    client.post("/tasks", json={"title": "API設計書を作成する"})
    client.post("/tasks", json={"title": "読書"})

    response = client.get("/tasks/search?q=API")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "API設計書を作成する"

    app.dependency_overrides.clear()


def test_search_returns_422_when_q_missing():
    """qが未指定の場合は422になる。"""
    client = _make_client()

    response = client.get("/tasks/search")

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_search_returns_422_when_q_empty():
    """qが空文字の場合は422になる。"""
    client = _make_client()

    response = client.get("/tasks/search?q=")

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_search_does_not_conflict_with_get_by_id_route():
    """/tasks/searchが/tasks/{task_id}と誤って衝突しない。"""
    client = _make_client()
    client.post("/tasks", json={"title": "テスト"})

    response = client.get("/tasks/search?q=テスト")

    assert response.status_code == 200
    assert response.json()["total"] == 1

    app.dependency_overrides.clear()