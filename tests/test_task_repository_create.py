"""TaskRepository.createのテスト。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Task
from app.repositories import TaskRepository


def _make_session() -> Session:
    """テスト用のインメモリSQLiteセッションを作成する。"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_create_sets_id_and_timestamps():
    """登録後にidとcreated_at/updated_atが設定される。"""
    session = _make_session()
    repo = TaskRepository(session)
    task = Task(title="設計書を書く")

    created = repo.create(task)

    assert created.id is not None
    assert len(created.id) == 36
    assert created.created_at is not None
    assert created.updated_at is not None


def test_create_persists_task_to_db():
    """登録したタスクをget_by_idで再取得できる。"""
    session = _make_session()
    repo = TaskRepository(session)
    task = Task(title="API設計書を作成する", priority="高")

    created = repo.create(task)
    fetched = repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.title == "API設計書を作成する"
    assert fetched.priority == "高"


def test_create_increases_total_count():
    """登録後、一覧のtotalが増える。"""
    session = _make_session()
    repo = TaskRepository(session)

    repo.create(Task(title="タスク1"))
    repo.create(Task(title="タスク2"))
    _, total = repo.list(limit=10, offset=0)

    assert total == 2
