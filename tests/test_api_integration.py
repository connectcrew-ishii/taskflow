"""複数エンドポイントを横断するAPI統合テスト。"""
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


def test_full_task_lifecycle_across_all_endpoints():
    """登録→一覧確認→詳細取得→更新→更新確認→削除→削除確認の一連の流れを検証する。"""
    client = _make_client()

    # 1. 登録: 201
    create_response = client.post(
        "/tasks",
        json={
            "title": "設計書を作成する",
            "priority": "高",
            "status": "未着手",
            "due_date": "2026-12-31",
        },
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # 2. 一覧に反映されているか: 200
    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    # 3. 詳細取得: 200
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "設計書を作成する"

    # 4. 更新: 200
    update_response = client.put(
        f"/tasks/{task_id}",
        json={
            "title": "設計書を完成させる",
            "priority": "高",
            "status": "完了",
            "due_date": "2026-12-31",
        },
    )
    assert update_response.status_code == 200

    # 5. 更新内容が詳細取得に反映されているか: 200
    get_after_update = client.get(f"/tasks/{task_id}")
    assert get_after_update.status_code == 200
    assert get_after_update.json()["title"] == "設計書を完成させる"
    assert get_after_update.json()["status"] == "完了"

    # 6. 削除: 204
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # 7. 削除後の詳細取得: 404
    get_after_delete = client.get(f"/tasks/{task_id}")
    assert get_after_delete.status_code == 404

    # 8. 一覧からも消えているか: 200
    list_after_delete = client.get("/tasks")
    assert list_after_delete.status_code == 200
    assert list_after_delete.json()["total"] == 0


def test_search_and_filter_endpoints_work_together():
    """検索・一覧・フィルタの各エンドポイントが組み合わせても正しく動作する。"""
    client = _make_client()
    client.post(
        "/tasks", json={"title": "API設計書", "priority": "高", "status": "対応中"}
    )
    client.post(
        "/tasks", json={"title": "読書", "priority": "低", "status": "完了"}
    )

    search_response = client.get("/tasks/search?q=API")
    assert search_response.status_code == 200
    assert search_response.json()["total"] == 1

    filter_response = client.get("/tasks?priority=高&status=対応中")
    assert filter_response.status_code == 200
    assert filter_response.json()["total"] == 1

    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 2


def test_all_primary_status_codes_are_confirmed_across_api():
    """API全体で200/201/204/404/422の各ステータスが確認できることをまとめて検証する。"""
    client = _make_client()

    # 201: 登録成功
    created = client.post("/tasks", json={"title": "タスク"})
    assert created.status_code == 201
    task_id = created.json()["id"]

    # 200: 一覧・詳細・更新
    assert client.get("/tasks").status_code == 200
    assert client.get(f"/tasks/{task_id}").status_code == 200
    assert (
        client.put(f"/tasks/{task_id}", json={"title": "更新後"}).status_code == 200
    )

    # 422: 不正な登録
    assert client.post("/tasks", json={"title": ""}).status_code == 422

    # 404: 存在しないIDへの操作
    missing_id = "11111111-1111-1111-1111-111111111111"
    assert client.get(f"/tasks/{missing_id}").status_code == 404

    # 204: 削除成功
    assert client.delete(f"/tasks/{task_id}").status_code == 204

    # 404: 削除後の再アクセス
    assert client.get(f"/tasks/{task_id}").status_code == 404