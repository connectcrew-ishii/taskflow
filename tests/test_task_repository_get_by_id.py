"""TaskRepository.get_by_idのテスト。"""
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


def test_get_by_id_returns_task_when_exists():
    """存在するIDを指定した場合、該当タスクを返す。"""
    session = _make_session()
    task = Task(title="設計書を書く")
    session.add(task)
    session.commit()
    session.refresh(task)
    repo = TaskRepository(session)

    result = repo.get_by_id(task.id)

    assert result is not None
    assert result.id == task.id
    assert result.title == "設計書を書く"


def test_get_by_id_returns_none_when_not_exists():
    """存在しないIDを指定した場合、Noneを返す。"""
    session = _make_session()
    repo = TaskRepository(session)

    result = repo.get_by_id("11111111-1111-1111-1111-111111111111")

    assert result is None
