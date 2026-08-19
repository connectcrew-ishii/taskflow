"""priority/status列挙型の検証テスト。"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Task, TaskPriority, TaskStatus


def _make_session() -> Session:
    """テスト用のインメモリSQLiteセッションを作成する。"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_valid_priority_and_status_are_accepted():
    """許可された値であれば登録できる。"""
    session = _make_session()
    task = Task(
        title="設計書を書く",
        priority=TaskPriority.HIGH.value,
        status=TaskStatus.IN_PROGRESS.value,
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.priority == "高"
    assert task.status == "対応中"


def test_invalid_priority_is_rejected():
    """許可値以外のpriorityはValueErrorになる。"""
    with pytest.raises(ValueError, match="不正なpriorityです"):
        Task(title="テスト", priority="不明")


def test_invalid_status_is_rejected():
    """許可値以外のstatusはValueErrorになる。"""
    with pytest.raises(ValueError, match="不正なstatusです"):
        Task(title="テスト", status="不明")


def test_default_priority_and_status_use_enum_values():
    """既定値がEnumの値と一致する。"""
    session = _make_session()
    task = Task(title="読書")

    session.add(task)
    session.commit()
    session.refresh(task)

    assert task.priority == TaskPriority.MEDIUM.value
    assert task.status == TaskStatus.NOT_STARTED.value