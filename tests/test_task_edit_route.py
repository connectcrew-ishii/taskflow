"""タスク編集画面(GET/POST /tasks-list/{task_id}/edit)のテスト。"""
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


def test_edit_form_returns_200_with_existing_values():
    """編集フォームに既存値が表示される。"""
    client = _make_client()
    created = client.post(
        "/tasks", json={"title": "設計書を書く", "priority": "高"}
    ).json()

    response = client.get(f"/tasks-list/{created['id']}/edit")

    assert response.status_code == 200
    assert 'value="設計書を書く"' in response.text
    assert 'selected' in response.text

    app.dependency_overrides.clear()


def test_edit_form_returns_404_for_missing_task():
    """存在しないタスクIDの場合は404になる。"""
    client = _make_client()

    response = client.get("/tasks-list/11111111-1111-1111-1111-111111111111/edit")

    assert response.status_code == 404

    app.dependency_overrides.clear()


def test_submitting_edit_form_updates_task_and_redirects():
    """編集フォーム送信で更新され、一覧画面へリダイレクトされる。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "ジムに行く"}).json()

    response = client.post(
        f"/tasks-list/{created['id']}/edit",
        data={"title": "ジムで筋トレ", "priority": "高", "status": "対応中"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/tasks-list"

    app.dependency_overrides.clear()


def test_update_is_reflected_in_list_screen():
    """更新後の値が一覧画面に反映される。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "読書"}).json()
    client.post(
        f"/tasks-list/{created['id']}/edit",
        data={"title": "読書する", "status": "完了"},
    )

    response = client.get("/tasks-list")

    assert "読書する" in response.text
    assert "完了" in response.text

    app.dependency_overrides.clear()


def test_update_is_reflected_via_api_detail():
    """更新後の値がJSON API(詳細取得)にも反映される。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "英語学習"}).json()
    client.post(
        f"/tasks-list/{created['id']}/edit",
        data={"title": "英語学習を続ける", "priority": "重要"},
    )

    response = client.get(f"/tasks/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "英語学習を続ける"
    assert body["priority"] == "重要"

    app.dependency_overrides.clear()


def test_submitting_edit_form_with_empty_title_shows_error():
    """タイトル未入力の場合、編集フォームにエラーが表示される。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "タスク"}).json()

    response = client.post(
        f"/tasks-list/{created['id']}/edit",
        data={"title": ""},
    )

    assert response.status_code == 422
    assert "alert-danger" in response.text

    app.dependency_overrides.clear()


def test_submitting_edit_form_for_missing_task_returns_404():
    """存在しないタスクIDへの更新は404になる。"""
    client = _make_client()

    response = client.post(
        "/tasks-list/11111111-1111-1111-1111-111111111111/edit",
        data={"title": "タスク"},
    )

    assert response.status_code == 404

    app.dependency_overrides.clear()