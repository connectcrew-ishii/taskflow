"""GET / (ダッシュボード画面)のテスト。"""
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


def test_dashboard_returns_200():
    """ダッシュボードにアクセスすると200が返る。"""
    client = _make_client()

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    app.dependency_overrides.clear()


def test_dashboard_shows_all_four_status_counts():
    """4状態すべての件数が表示される。"""
    client = _make_client()
    client.post("/tasks", json={"title": "タスク1", "status": "未着手"})
    client.post("/tasks", json={"title": "タスク2", "status": "完了"})

    response = client.get("/")

    assert response.status_code == 200
    body = response.text
    assert "未着手" in body
    assert "対応中" in body
    assert "保留" in body
    assert "完了" in body

    app.dependency_overrides.clear()


def test_dashboard_shows_upcoming_task_title():
    """期限が近いタスクのタイトルが表示される。"""
    client = _make_client()
    client.post(
        "/tasks", json={"title": "重要な会議準備", "due_date": "2026-12-31"}
    )

    response = client.get("/")

    assert response.status_code == 200
    assert "重要な会議準備" in response.text

    app.dependency_overrides.clear()


def test_dashboard_shows_placeholder_when_no_upcoming_tasks():
    """期限が近いタスクがない場合、案内文が表示される。"""
    client = _make_client()

    response = client.get("/")

    assert response.status_code == 200
    assert "期限が近いタスクはありません" in response.text

    app.dependency_overrides.clear()