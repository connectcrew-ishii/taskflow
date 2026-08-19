"""エラー応答形式（ErrorResponse）の統一テスト。"""
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


def test_404_response_matches_error_response_format():
    """404応答がcode/message/details形式になっている。"""
    client = _make_client()

    response = client.get("/tasks/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "TASK_NOT_FOUND"
    assert "message" in body
    assert body["details"] is None

    app.dependency_overrides.clear()


def test_422_response_matches_error_response_format():
    """422応答がcode/message/details形式になっている。"""
    client = _make_client()

    response = client.post("/tasks", json={"title": ""})

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"] == "入力内容を確認してください。"
    assert isinstance(body["details"], list)
    assert len(body["details"]) > 0

    app.dependency_overrides.clear()


def test_delete_404_response_matches_error_response_format():
    """DELETE時の404応答も同じ形式になっている。"""
    client = _make_client()

    response = client.delete("/tasks/11111111-1111-1111-1111-111111111111")

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "TASK_NOT_FOUND"

    app.dependency_overrides.clear()