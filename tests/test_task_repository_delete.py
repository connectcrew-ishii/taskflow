"""TaskRepository.deleteのテスト。"""
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


def test_delete_removes_task():
    """削除後、get_by_idで取得できなくなる。"""
    session = _make_session()
    repo = TaskRepository(session)
    task = repo.create(Task(title="設計書を書く"))

    repo.delete(task)

    assert repo.get_by_id(task.id) is None


def test_delete_decreases_total_count():
    """削除後、一覧のtotalが減る。"""
    session = _make_session()
    repo = TaskRepository(session)
    task1 = repo.create(Task(title="タスク1"))
    repo.create(Task(title="タスク2"))

    repo.delete(task1)
    _, total = repo.list(limit=10, offset=0)

    assert total == 1


def test_delete_does_not_affect_other_tasks():
    """削除しても他のタスクは残る。"""
    session = _make_session()
    repo = TaskRepository(session)
    task1 = repo.create(Task(title="タスク1"))
    task2 = repo.create(Task(title="タスク2"))

    repo.delete(task1)

    assert repo.get_by_id(task2.id) is not None
