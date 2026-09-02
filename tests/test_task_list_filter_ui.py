"""タスク一覧画面の検索・フィルタUIのテスト。"""
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


def test_search_query_filters_task_list():
    """キーワード検索(q)が一覧に反映される。"""
    client = _make_client()
    client.post("/tasks", json={"title": "API設計書を作成する"})
    client.post("/tasks", json={"title": "読書"})

    response = client.get("/tasks-list?q=API")

    assert response.status_code == 200
    assert "API設計書を作成する" in response.text
    assert "読書" not in response.text

    app.dependency_overrides.clear()


def test_status_filter_reflects_in_task_list():
    """statusフィルタが一覧に反映される。"""
    client = _make_client()
    client.post("/tasks", json={"title": "対応中タスク", "status": "対応中"})
    client.post("/tasks", json={"title": "完了タスク", "status": "完了"})

    response = client.get("/tasks-list?status=対応中")

    assert response.status_code == 200
    assert "対応中タスク" in response.text
    assert "完了タスク" not in response.text

    app.dependency_overrides.clear()


def test_priority_filter_reflects_in_task_list():
    """priorityフィルタが一覧に反映される。"""
    client = _make_client()
    client.post("/tasks", json={"title": "高優先度タスク", "priority": "高"})
    client.post("/tasks", json={"title": "低優先度タスク", "priority": "低"})

    response = client.get("/tasks-list?priority=高")

    assert response.status_code == 200
    assert "高優先度タスク" in response.text
    assert "低優先度タスク" not in response.text

    app.dependency_overrides.clear()


def test_overdue_filter_reflects_in_task_list():
    """overdueフィルタが一覧に反映される。"""
    client = _make_client()
    client.post(
        "/tasks",
        json={"title": "期限切れ", "due_date": "2020-01-01", "status": "対応中"},
    )
    client.post("/tasks", json={"title": "期限なし"})

    response = client.get("/tasks-list?overdue=true")

    assert response.status_code == 200
    assert "期限切れ" in response.text
    assert "期限なし" not in response.text

    app.dependency_overrides.clear()


def test_search_form_retains_entered_keyword():
    """検索後、入力欄に入力したキーワードが保持される。"""
    client = _make_client()

    response = client.get("/tasks-list?q=テスト")

    assert 'value="テスト"' in response.text

    app.dependency_overrides.clear()


def test_no_match_shows_placeholder_message():
    """条件に一致しない場合、案内文が表示される。"""
    client = _make_client()
    client.post("/tasks", json={"title": "読書"})

    response = client.get("/tasks-list?q=存在しない語")

    assert "条件に一致するタスクがありません" in response.text

    app.dependency_overrides.clear()