"""削除確認ダイアログのUI構造テスト。

実際のクリック操作(キャンセル/削除)の動作確認は、JSテストツールが
技術スタックに含まれていないため、ブラウザでの目視確認で行う。
このテストではモーダルの構造とJSファイルの内容を確認する。
"""
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

JS_CONTENT = Path("app/static/js/task_delete.js").read_text(encoding="utf-8")


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


def test_task_list_renders_delete_confirmation_modal():
    """一覧画面に削除確認モーダルが存在する。"""
    client = _make_client()

    response = client.get("/tasks-list")

    assert response.status_code == 200
    body = response.text
    assert 'id="deleteConfirmModal"' in body
    assert "タスクを削除しますか" in body
    assert "キャンセル" in body
    assert "削除する" in body

    app.dependency_overrides.clear()


def test_task_list_delete_buttons_have_task_id_and_title():
    """削除ボタンにタスクIDとタイトルがdata属性として埋め込まれる。"""
    client = _make_client()
    created = client.post("/tasks", json={"title": "設計書を書く"}).json()

    response = client.get("/tasks-list")

    body = response.text
    assert f'data-task-id="{created["id"]}"' in body
    assert 'data-task-title="設計書を書く"' in body

    app.dependency_overrides.clear()


def test_task_list_loads_delete_confirmation_script():
    """一覧画面が削除確認用JSファイルを読み込んでいる。"""
    client = _make_client()

    response = client.get("/tasks-list")

    assert '/static/js/task_delete.js' in response.text

    app.dependency_overrides.clear()


def test_delete_script_is_served_and_accessible():
    """削除確認用JSファイルが静的ファイルとして配信される。"""
    client = _make_client()

    response = client.get("/static/js/task_delete.js")

    assert response.status_code == 200

    app.dependency_overrides.clear()


def test_delete_script_calls_delete_api_with_correct_pattern():
    """JSがDELETE /tasks/{id}を正しいパターンで呼び出す。"""
    assert 'fetch("/tasks/" + targetTaskId' in JS_CONTENT
    assert 'method: "DELETE"' in JS_CONTENT


def test_delete_script_references_modal_and_confirm_button_ids():
    """JSがモーダル・確認ボタンのIDを正しく参照している。"""
    assert 'getElementById("deleteConfirmModal")' in JS_CONTENT
    assert 'getElementById("deleteConfirmButton")' in JS_CONTENT
    assert 'getElementById("deleteConfirmTaskTitle")' in JS_CONTENT