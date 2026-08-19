"""DELETE /tasks/{task_id} APIのテスト。"""
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


def test_delete_task_returns_204_when_exists():
    """存在するタスクを削除すると204を返す。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "英語学習"}).json()

    response = client.delete(f"/tasks/{created['id']}")

    assert response.status_code == 204
    assert response.content == b""

    app.dependency_overrides.clear()


def test_delete_task_removes_it_from_list():
    """削除後、一覧からも消える。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "英語学習"}).json()
    client.delete(f"/tasks/{created['id']}")

    response = client.get("/tasks")

    assert response.json()["total"] == 0

    app.dependency_overrides.clear()


def test_delete_task_makes_get_return_404():
    """削除後、GETで取得しようとすると404になる。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "英語学習"}).json()
    client.delete(f"/tasks/{created['id']}")

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_delete_task_returns_404_when_not_exists():
    """存在しないIDの削除は404になる。"""
    client = _make_client()

    response = client.delete("/tasks/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404

    app.dependency_overrides.clear()