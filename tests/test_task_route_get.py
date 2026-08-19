"""GET /tasks/{task_id} APIのテスト。"""
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


def test_get_task_returns_200_when_exists():
    """存在するタスクを取得すると200で内容が返る。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "設計書を書く"}).json()

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "設計書を書く"

    app.dependency_overrides.clear()


def test_get_task_returns_404_when_not_exists():
    """存在しないIDの場合は404になる。"""
    client = _make_client()

    response = client.get("/tasks/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404

    app.dependency_overrides.clear()
