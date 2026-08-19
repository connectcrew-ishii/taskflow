"""PUT /tasks/{task_id} APIのテスト。"""
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


def test_update_task_returns_200_and_saves_changes():
    """更新内容が保存され200を返す。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "ジムに行く"}).json()

    response = client.put(
        f"/tasks/{created['id']}",
        json={"title": "ジムで筋トレ", "priority": "高", "status": "対応中"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "ジムで筋トレ"
    assert body["priority"] == "高"
    assert body["status"] == "対応中"

    app.dependency_overrides.clear()


def test_update_task_changes_are_persisted():
    """更新後、GETで取得しても変更が反映されている。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "読書"}).json()
    client.put(f"/tasks/{created['id']}", json={"title": "読書する", "status": "完了"})

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "読書する"
    assert response.json()["status"] == "完了"

    app.dependency_overrides.clear()


def test_update_task_returns_404_when_not_exists():
    """存在しないIDの更新は404になる。"""
    client = _make_client()

    response = client.put(
        "/tasks/11111111-1111-1111-1111-111111111111",
        json={"title": "タスク"},
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_update_task_returns_422_for_missing_title():
    """titleが未指定の場合は422になる。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "タスク"}).json()

    response = client.put(f"/tasks/{created['id']}", json={})

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_update_task_returns_422_for_invalid_status():
    """statusが許可値以外の場合は422になる。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "タスク"}).json()

    response = client.put(
        f"/tasks/{created['id']}", json={"title": "タスク", "status": "不明"}
    )

    assert response.status_code == 422

    app.dependency_overrides.clear()
