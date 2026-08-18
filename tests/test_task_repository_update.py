"""TaskRepository.updateのテスト。"""
import time

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


def test_update_persists_changed_fields():
    """変更した属性がDBに反映される。"""
    session = _make_session()
    repo = TaskRepository(session)
    task = repo.create(Task(title="設計書を書く"))

    task.title = "設計書を完成させる"
    task.status = "完了"
    updated = repo.update(task)

    fetched = repo.get_by_id(updated.id)
    assert fetched is not None
    assert fetched.title == "設計書を完成させる"
    assert fetched.status == "完了"


def test_update_changes_updated_at():
    """更新するとupdated_atが変わる。"""
    session = _make_session()
    repo = TaskRepository(session)
    task = repo.create(Task(title="読書"))
    original_updated_at = task.updated_at

    time.sleep(0.01)
    task.title = "読書する"
    updated = repo.update(task)

    assert updated.updated_at > original_updated_at


def test_update_does_not_change_created_at():
    """更新してもcreated_atは変わらない。"""
    session = _make_session()
    repo = TaskRepository(session)
    task = repo.create(Task(title="ジムに行く"))
    original_created_at = task.created_at

    task.status = "対応中"
    updated = repo.update(task)

    assert updated.created_at == original_created_at
