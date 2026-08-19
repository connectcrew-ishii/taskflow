"""GET /tasks APIのテスト。"""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Task


def _make_client() -> tuple[TestClient, sessionmaker]:
    """インメモリDBを使うテスト用クライアントを作成する。

    StaticPoolを使い、テーブル作成時とリクエスト処理時（別スレッド）で
    同一のSQLite接続を共有することで、インメモリDBが失われないようにする。
    """
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
    return TestClient(app), testing_session_local


def test_list_tasks_returns_200_and_empty_list_when_no_tasks():
    """タスクが0件の場合、200と空のitemsを返す。"""
    client, _ = _make_client()

    response = client.get("/tasks")

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["limit"] == 50
    assert body["offset"] == 0

    app.dependency_overrides.clear()


def test_list_tasks_returns_created_tasks():
    """登録済みタスクが一覧に含まれる。"""
    client, session_local = _make_client()
    session = session_local()
    session.add(Task(title="設計書を書く"))
    session.add(Task(title="読書"))
    session.commit()
    session.close()

    response = client.get("/tasks")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2

    app.dependency_overrides.clear()


def test_list_tasks_respects_limit_and_offset():
    """limit/offsetパラメータが反映される。"""
    client, session_local = _make_client()
    session = session_local()
    for i in range(5):
        session.add(Task(title=f"タスク{i + 1}"))
    session.commit()
    session.close()

    response = client.get("/tasks?limit=2&offset=1")

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["limit"] == 2
    assert body["offset"] == 1
    assert body["total"] == 5

    app.dependency_overrides.clear()


def test_list_tasks_rejects_limit_over_100():
    """limitが100を超える場合は422になる。"""
    client, _ = _make_client()

    response = client.get("/tasks?limit=101")

    assert response.status_code == 422

    app.dependency_overrides.clear()


def test_list_tasks_rejects_negative_offset():
    """offsetが負数の場合は422になる。"""
    client, _ = _make_client()

    response = client.get("/tasks?offset=-1")

    assert response.status_code == 422

    app.dependency_overrides.clear()
